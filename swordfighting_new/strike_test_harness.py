from __future__ import annotations

from dataclasses import dataclass

from swordfighting_new.attacks import Attack, AttackManager, HorizontalSwordManager
from swordfighting_new.core.board import Board
from swordfighting_new.fighters.inbound_attack_handler import InboundAttackHandler
from swordfighting_new.mechanics.breaker import BreakerManager
from swordfighting_new.mechanics.chain_runner import BreakerChainRunner
from swordfighting_new.mechanics.gravity import GravityManager
from swordfighting_new.mechanics.movement import PieceMover
from swordfighting_new.mechanics.timing import TimingConfig


@dataclass(frozen=True, slots=True)
class StrikeTestPassStats:
    sprinkles: int
    rectangles: list[dict]

    def as_dict(self) -> dict:
        return {
            'sprinkles': int(self.sprinkles),
            'rectangles': list(self.rectangles),
            # Compatibility keys used by some debug tooling.
            'breaker_cleared': 0,
            'normal_cleared': int(self.sprinkles) + sum(int(r.get('size', 0) or 0) for r in (self.rectangles or [])),
            'total_cleared': int(self.sprinkles) + sum(int(r.get('size', 0) or 0) for r in (self.rectangles or [])),
        }


class StrikeTestHarness:
    """Minimal attack-accuracy harness for the pygame Strike Test mode.

    Goals:
    - Reuse the real rectangle detection from BreakerManager
    - Reuse the real outbound attack generation (AttackManager)
    - Reuse the real inbound delivery/spawn logic (InboundAttackHandler), including waves

    This intentionally does NOT spawn controllable pieces or run full chain logic.
    """

    def __init__(
        self,
        timing: TimingConfig,
        attack_delay_frames: int = 24,
        bulk_delivery: bool = True,
        garbage_spawn_interval: int = 3,
    ) -> None:
        self.timing = timing
        self.attack_delay_frames = int(attack_delay_frames)
        self.bulk_delivery = bool(bulk_delivery)
        self.garbage_spawn_interval = int(garbage_spawn_interval)

        self.input_board = Board()
        self._breaker = BreakerManager(self.input_board)
        self._attack_mgr = AttackManager()

        # Last live-run (real chain) capture for UI/debug.
        self.last_live_pass_stats: list[dict] = []
        self.last_live_chain_passes: int = 0
        self.last_live_sim_frames: int = 0

        self.frame = 0
        self._build_output_pipeline()

    def _build_output_pipeline(self) -> None:
        self.output_board = Board()

        self._output_mover = PieceMover(self.output_board)
        self._output_gravity = GravityManager(self.output_board, self._output_mover, self.timing)

        self.output_horizontal_swords = HorizontalSwordManager(self.output_board, self.timing)
        self.output_inbound = InboundAttackHandler(
            board=self.output_board,
            timing=self.timing,
            piece_mover=self._output_mover,
            gravity_manager=self._output_gravity,
            attack_delay_frames=self.attack_delay_frames,
            bulk_delivery=self.bulk_delivery,
            garbage_spawn_interval=self.garbage_spawn_interval,
        )

    def reset_output(self) -> None:
        self._build_output_pipeline()

    def compute_pass_stats_from_input(self) -> StrikeTestPassStats:
        non_breaker_positions: set[tuple[int, int]] = set()
        for x in range(int(self.input_board.WIDTH)):
            for y in range(int(self.input_board.HEIGHT)):
                cell = self.input_board.get_piece(x, y)
                if cell in (None, self.input_board.EMPTY):
                    continue
                if bool(getattr(cell, 'is_breaker', False)):
                    continue
                # Inbound lifecycle blocks are intentionally ignored by breaker logic; mimic that.
                if getattr(cell, 'attack_state', None) is not None:
                    continue
                non_breaker_positions.add((int(x), int(y)))

        rectangles = self._breaker._find_rectangles_in_region(non_breaker_positions)
        rectangle_positions: set[tuple[int, int]] = set()
        for rect in rectangles:
            try:
                minx = int(rect.get('minx', 0) or 0)
                miny = int(rect.get('miny', 0) or 0)
                w = int(rect.get('width', 0) or 0)
                h = int(rect.get('height', 0) or 0)
            except Exception:
                continue
            for xx in range(minx, minx + w):
                for yy in range(miny, miny + h):
                    rectangle_positions.add((int(xx), int(yy)))

        sprinkle_positions = non_breaker_positions - rectangle_positions
        sprinkles = len(sprinkle_positions)
        return StrikeTestPassStats(sprinkles=sprinkles, rectangles=rectangles)

    def run_once(self, *, chain_len: int = 1) -> list[Attack]:
        """Generate outbound attacks from current input board and deliver to output.

        Note: in the real game, a combo/chain is a history of multiple passes.
        AttackManager scales some outputs based on the pass index (1..N).

        In Strike Test, `chain_len` represents the *combo step* you want to
        simulate for the current board stats. So `chain_len=2` means: pass 1 is
        empty, pass 2 contains the current rectangles/sprinkles.
        """
        self.reset_output()

        try:
            chain_len = int(chain_len)
        except Exception:
            chain_len = 1
        chain_len = max(1, min(9, chain_len))

        stats = self.compute_pass_stats_from_input().as_dict()
        empty = {
            'sprinkles': 0,
            'rectangles': [],
            'breaker_cleared': 0,
            'normal_cleared': 0,
            'total_cleared': 0,
        }
        history = [empty for _ in range(int(chain_len) - 1)] + [stats]
        self._attack_mgr.generate_from_chain(
            history,
            board_width=int(self.input_board.WIDTH),
            board_height=int(self.input_board.HEIGHT),
        )

        # Deliver immediately (outbound delay is a separate system in MatchSession).
        delivered: list[Attack] = []
        for a in (self._attack_mgr.generated_last_chain or []):
            try:
                delivered.append(Attack(a.kind, int(a.amount), 0, meta=dict(a.meta or {})))
            except Exception:
                continue

        self.output_inbound.receive_attacks(delivered)
        return delivered

    def run_live(self, *, max_chain_frames: int = 2400) -> list[Attack]:
        """Run a real breaker chain on the input board and generate attacks from it.

        This matches the live-game behavior:
        - Breaker passes are discovered by actually running breaker/cascade logic.
        - Per-pass stats come from BreakerChainRunner.get_pass_stats().
        - Attacks are generated by AttackManager.generate_from_chain(history).

        The input board itself is not mutated; we run the chain on a copy.
        """
        self.reset_output()

        try:
            max_chain_frames = int(max_chain_frames)
        except Exception:
            max_chain_frames = 2400
        max_chain_frames = max(60, min(20000, int(max_chain_frames)))

        # Run chain on a copy so the user can iterate without rebuilding the setup.
        try:
            sim_board = self.input_board.copy()
        except Exception:
            sim_board = Board()
            for x in range(int(self.input_board.WIDTH)):
                for y in range(int(self.input_board.HEIGHT)):
                    try:
                        sim_board.set_piece(x, y, self.input_board.get_piece(x, y))
                    except Exception:
                        pass

        breakers = BreakerManager(sim_board)
        runner = BreakerChainRunner(sim_board, breakers, frame_delay=0, cascade_mode='fast')
        runner.start()

        frames = 0
        for _ in range(max_chain_frames):
            if getattr(runner, 'finished', False):
                break
            runner.update()
            frames += 1

        try:
            history = list(runner.get_pass_stats() or [])
        except Exception:
            history = []

        self.last_live_pass_stats = list(history)
        self.last_live_chain_passes = int(len(history))
        self.last_live_sim_frames = int(frames)

        if not history:
            self._attack_mgr.generate_from_chain(
                [],
                board_width=int(sim_board.WIDTH),
                board_height=int(sim_board.HEIGHT),
            )
            self.output_inbound.receive_attacks([])
            return []

        self._attack_mgr.generate_from_chain(
            history,
            board_width=int(sim_board.WIDTH),
            board_height=int(sim_board.HEIGHT),
        )

        delivered: list[Attack] = []
        for a in (self._attack_mgr.generated_last_chain or []):
            try:
                delivered.append(Attack(a.kind, int(a.amount), 0, meta=dict(a.meta or {})))
            except Exception:
                continue

        self.output_inbound.receive_attacks(delivered)
        return delivered

    def is_settled(self) -> bool:
        """True when there are no pending/spawning inbound systems.

        Strike Test is intended to show the *result* of inbound attacks; this
        helper allows the UI to fast-forward until everything has landed.
        """
        try:
            pending = int(getattr(self.output_inbound, 'pending_in_sprinkle', 0) or 0) + int(getattr(self.output_inbound, 'pending_in_strike', 0) or 0)
        except Exception:
            pending = 0
        try:
            spawn_q = int(getattr(self.output_inbound, 'spawn_queue', 0) or 0)
        except Exception:
            spawn_q = 0
        try:
            delay = int(getattr(self.output_inbound, 'inbound_delay', 0) or 0)
        except Exception:
            delay = 0

        try:
            fallers = list(getattr(self.output_inbound, 'garbage_fallers', None) or [])
        except Exception:
            fallers = []
        try:
            delayed = list(getattr(self.output_inbound, '_delayed_clusters', None) or [])
        except Exception:
            delayed = []
        try:
            hs_active = list(getattr(self.output_horizontal_swords, 'active_swords', None) or [])
        except Exception:
            hs_active = []

        return (pending + spawn_q) == 0 and delay == 0 and (not fallers) and (not delayed) and (not hs_active)

    def settle(self, *, max_frames: int = 600) -> int:
        """Advance the output simulation until all inbound actions have landed.

        Returns the number of frames simulated.
        """
        try:
            max_frames = int(max_frames)
        except Exception:
            max_frames = 600
        max_frames = max(1, min(5000, max_frames))

        frames = 0
        for _ in range(max_frames):
            if self.is_settled():
                break
            self.update()
            frames += 1
        return frames

    def update(self) -> None:
        """Tick the output board inbound systems one frame."""
        self.frame += 1

        self.output_inbound.set_frame(self.frame)
        self.output_inbound.process_inbound(self.output_horizontal_swords)
        self.output_inbound.update_inbound_garbage()

        # Occupied cells from transient fallers so global gravity doesn't pull blocks through them.
        occupied: set[tuple[int, int]] = set()
        try:
            for g in (getattr(self.output_inbound, 'garbage_fallers', None) or []):
                for x, y, _b in g.get_block_positions():
                    if self.output_board.is_in_bounds(x, y):
                        xi, yi = int(x), int(y)
                        try:
                            if self.output_board.get_piece(xi, yi) == self.output_board.EMPTY:
                                occupied.add((xi, yi))
                        except Exception:
                            continue
        except Exception:
            occupied = set()

        self._output_gravity.apply_global_gravity(occupied_cells=occupied)

        new_falling_pieces, new_locked_blocks = self.output_horizontal_swords.update(self.frame)
        self.output_inbound.add_garbage_fallers(new_falling_pieces)

        # Register locked horizontal sword blocks with the lifecycle (mirrors BaseFighter behavior).
        if new_locked_blocks:
            for piece in new_locked_blocks:
                for x, y, block in piece.get_block_positions():
                    if getattr(block, 'attack_state', None):
                        try:
                            setattr(block, 'x', x)
                            setattr(block, 'y', y)
                        except Exception:
                            pass
                        self.output_inbound.register_new_attack_block(block)
