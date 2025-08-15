import os
import hashlib
import yaml
import pygame
from typing import Dict, Any, List, Tuple

from utils.clock import FakeClock
from core.puzzle_module import PuzzleEngine
from modules.attack_module.attacks_service import AttacksService


PIECE_MAP = {
    'r': 'red_block',
    'b': 'blue_block',
    'g': 'green_block',
    'y': 'yellow_block',
    'R': 'red_breaker',
    'B': 'blue_breaker',
    'G': 'green_breaker',
    'Y': 'yellow_breaker',
    'X': None,
    '.': None,
}


def _grid_checksum(grid: List[List[Any]]) -> str:
    # Visible rows only: 0..grid_height-1
    rows: List[str] = []
    for y in range(len(grid) - 1):  # exclude invisible row if present
        row = grid[y]
        cells: List[str] = []
        for cell in row:
            if cell is None:
                cells.append('.')
            else:
                cells.append(str(cell))
        rows.append(''.join(cells))
    blob = '\n'.join(rows).encode('utf-8')
    return hashlib.sha1(blob).hexdigest()[:16]


def _apply_initial_layout(engine: PuzzleEngine, layout: List[List[str]]) -> None:
    pieces_to_place: List[Tuple[int, int, str]] = []
    # Layout provided as list of rows from bottom to top or top to bottom? We'll accept top-first.
    height = len(layout)
    for y, row in enumerate(layout):
        for x, token in enumerate(row):
            piece = PIECE_MAP.get(token, token)
            if piece is None:
                continue
            # Engine's grid y=0 is top visible row; assume layout is top-first
            pieces_to_place.append((x, y, piece))
    # Ensure no active falling piece interferes
    engine.main_piece = None
    engine.attached_piece = None
    engine.place_pieces(pieces_to_place)


def _install_combo_forwarding(engine: PuzzleEngine, svc: AttacksService, break_order: List[List[Tuple[int,int,str]]]):
    def on_broken(broken_blocks, is_cluster: bool, combo_multiplier: int):
        # Record break ordering
        break_order.append([(int(x), int(y), str(color)) for (x, y, color) in broken_blocks])
        # Forward to attacks
        svc.on_combo(broken_blocks, is_cluster=is_cluster, chain_multiplier=combo_multiplier, player_id=1)
    engine.blocks_broken_handler = on_broken


def load_fixture(path: str) -> Dict[str, Any]:
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    return data


def run_fixture(fixture: Dict[str, Any]) -> Dict[str, Any]:
    # Headless pygame
    os.environ.setdefault('SDL_VIDEODRIVER', 'dummy')
    pygame.init()
    try:
        screen = pygame.display.set_mode((800, 600))
        font = pygame.font.Font(None, 24)

        clock = FakeClock(0)

        # Monkeypatch pygame time to use FakeClock
        pygame.time.get_ticks = lambda: int(clock.now_ms())  # type: ignore

        # Build engine
        engine = PuzzleEngine(screen, font, audio=None, asset_path="puzzleassets", settings_system=None)
        # Attach clock where engine/input handler can see it
        setattr(engine, 'clock', clock)

        # Service to collect payloads
        attacks_mgr = None  # use default
        svc = AttacksService(clock=clock, attack_manager=attacks_mgr)

        # Seed initial board
        setup = fixture.get('setup', {})
        layout = setup.get('layout', [])
        # Start game to init state, then override pieces
        engine.start_game()
        _apply_initial_layout(engine, layout)

        # Install combo forwarding
        break_order: List[List[Tuple[int,int,str]]] = []
        _install_combo_forwarding(engine, svc, break_order)

        # Inputs
        inputs = fixture.get('inputs', [])
        # Normalize and sort by timestamp
        inputs = sorted(inputs, key=lambda i: int(i.get('t', 0)))

        action_map = {
            'left': lambda: engine.move_piece(-1, 0),
            'right': lambda: engine.move_piece(1, 0),
            'down': lambda: engine.move_piece(0, 1),
            'rotate_cw': lambda: engine.rotate_attached_piece(1),
            'rotate_ccw': lambda: engine.rotate_attached_piece(-1),
            'flip': lambda: engine.flip_pieces_vertically(),
            'drop': lambda: engine.place_piece_on_grid(),
            'tick': lambda: engine.update(),
            'noop': lambda: None,
        }

        current_ms = 0
        # Step to first input time
        for event in inputs:
            target_ms = int(event.get('t', current_ms))
            if target_ms < current_ms:
                target_ms = current_ms
            # Advance time in small steps calling update
            while current_ms < target_ms:
                clock.advance(10)
                current_ms += 10
                engine.update()

            action = event.get('action')
            fn = action_map.get(action)
            if fn:
                fn()
            # post-action update
            engine.update()

        # Drain chain reactions
        settle_steps = 0
        while settle_steps < 500:
            prev_checksum = _grid_checksum(engine.puzzle_grid)
            clock.advance(20)
            current_ms += 20
            engine.update()
            new_checksum = _grid_checksum(engine.puzzle_grid)
            settle_steps += 1
            if prev_checksum == new_checksum and not engine.chain_reaction_in_progress and not engine.breaking_blocks:
                break

        # Collect payloads for enemy board (2)
        payloads = svc.queue_payloads(board_id=2)
        payload_seq = [{'kind': p.kind, 'count': int(p.count), 'pattern': p.pattern} for p in payloads]

        result = {
            'final_checksum': _grid_checksum(engine.puzzle_grid),
            'break_order': break_order,
            'payloads': payload_seq,
        }
        return result
    finally:
        try:
            pygame.quit()
        except Exception:
            pass

