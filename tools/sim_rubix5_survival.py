import argparse
import os
import random
import sys
import time
from pathlib import Path

# Allow running this script directly via `python tools/...py`.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from swordfighting_new.mechanics.timing import DEFAULT_TIMING
from swordfighting_new.mechanics.scoring import ScoringManager
from swordfighting_new.session import RubixOpponent, create_shared_piece_queue


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--seed", type=int, default=None)
    parser.add_argument("--runs", type=int, default=1)
    parser.add_argument("--max-frames", type=int, default=50_000)
    parser.add_argument(
        "--level",
        type=int,
        default=5,
        help="Rubix boss level/tier to simulate (default: 5).",
    )
    parser.add_argument(
        "--budget-ms",
        type=float,
        default=6.0,
        help="Rubix planning budget per piece (0 disables deadline; may be slow).",
    )
    parser.add_argument(
        "--progress-every",
        type=int,
        default=5_000,
        help="Print a heartbeat every N frames (0 disables).",
    )
    args = parser.parse_args()

    # Set explicitly so the sim behaves the same regardless of user's env.
    try:
        os.environ["BF_RUBIX_PLAN_BUDGET_MS"] = str(float(args.budget_ms))
    except Exception:
        os.environ.setdefault("BF_RUBIX_PLAN_BUDGET_MS", "6")

    base_seed = args.seed
    if base_seed is None:
        # Keep it stable-ish but different between invocations.
        base_seed = int(time.time() * 1000) ^ random.getrandbits(31)

    runs = max(1, int(args.runs))
    max_frames = max(1, int(args.max_frames))

    defeat_frames: list[int] = []
    clears_total: list[int] = []
    chains: list[int] = []
    max_chain: list[int] = []
    sprinkles_sent: list[int] = []
    strikes_sent: list[int] = []
    piece_locks: list[int] = []

    def _p50(vals: list[int]) -> int:
        if not vals:
            return 0
        sv = sorted(int(v) for v in vals)
        return int(sv[len(sv) // 2])

    def _pct(vals: list[int], p: float) -> int:
        if not vals:
            return 0
        sv = sorted(int(v) for v in vals)
        p = max(0.0, min(1.0, float(p)))
        idx = int(round((len(sv) - 1) * p))
        idx = max(0, min(len(sv) - 1, idx))
        return int(sv[idx])

    def _get_chain_results(fighter) -> tuple[int, int, object, int] | None:
        bm = getattr(fighter, 'breaker', None)
        if bm is None:
            bm = getattr(fighter, 'breaker_manager', None)
        if bm is None:
            return None
        res = getattr(bm, 'last_chain_results', None)
        if not res:
            return None
        try:
            passes, total, per_pass = res
        except Exception:
            return None
        garbage_removed = 0
        try:
            stats = getattr(bm, 'last_pass_stats', None)
            if isinstance(stats, dict) and 'garbage_removed' in stats:
                garbage_removed = int(stats.get('garbage_removed', 0) or 0)
        except Exception:
            garbage_removed = 0
        try:
            bm.last_chain_results = None
        except Exception:
            pass
        return int(passes), int(total), per_pass, int(garbage_removed)
    for i in range(runs):
        seed_i = int(base_seed) + int(i)
        pq = create_shared_piece_queue(seed_i)
        ai = RubixOpponent(
            DEFAULT_TIMING,
            spawn_x=3,
            attack_delay_frames=24,
            bulk_delivery=True,
            enable_puzzle_speeds=False,
            piece_queue=pq,
        )
        ai.set_boss_level(int(args.level))
        ai.opponent = None

        scoring = ScoringManager()
        ai_was_active = bool(getattr(getattr(ai, 'chain_runner', None), 'active', False))

        defeated_at = None
        t_start = time.perf_counter()
        last_heartbeat_t = t_start
        progress_every = max(0, int(args.progress_every))

        for step in range(max_frames):
            ai.update()

            # Count a "piece lock" when a new chain resolution starts.
            try:
                ai_is_active = bool(getattr(getattr(ai, 'chain_runner', None), 'active', False))
            except Exception:
                ai_is_active = False
            if (not ai_was_active) and ai_is_active:
                scoring.ai.piece_locks += 1
            ai_was_active = ai_is_active

            # Count chain results (clears/chains/max_chain).
            cr = _get_chain_results(ai)
            if cr is not None:
                passes, total, _per_pass, garbage_removed = cr
                scoring.ai.record_chain(passes, total, _per_pass, garbage_removed)

            # Drain any ready attacks and count their amounts.
            try:
                out_attacks = list(ai.collect_ready_attacks() or [])
            except Exception:
                out_attacks = []
            for a in out_attacks:
                try:
                    kind = str(getattr(getattr(a, 'kind', None), 'value', '') or '')
                except Exception:
                    kind = ''
                try:
                    amt = int(getattr(a, 'amount', 0) or 0)
                except Exception:
                    amt = 0
                if kind == 'sprinkle':
                    scoring.ai.sprinkles_sent += amt
                elif kind == 'strike':
                    scoring.ai.strikes_sent += amt
            if progress_every > 0 and (step % progress_every) == 0 and step > 0:
                try:
                    now = time.perf_counter()
                    dt = max(1e-6, float(now - t_start))
                    fps = float(step) / float(dt)
                    hs0 = list(ai.board.get_column_heights())
                    mh0 = max(hs0) if hs0 else 0
                    # Only print if some time has actually passed (avoid spam on fast machines).
                    if float(now - last_heartbeat_t) >= 0.25:
                        print(
                            f"  heartbeat run {i+1}/{runs} seed={seed_i} frame={step} "
                            f"elapsed_s={dt:.1f} fps={fps:.1f} max_h={mh0}"
                        )
                        last_heartbeat_t = now
                except Exception:
                    pass
            if getattr(ai, "defeated", False):
                defeated_at = int(getattr(ai, "frame", 0) or 0)
                break

        hs = list(ai.board.get_column_heights())
        final_max_h = max(hs) if hs else 0

        clears_total.append(int(getattr(scoring.ai, 'clears_total', 0) or 0))
        chains.append(int(getattr(scoring.ai, 'chains', 0) or 0))
        max_chain.append(int(getattr(scoring.ai, 'max_chain', 0) or 0))
        sprinkles_sent.append(int(getattr(scoring.ai, 'sprinkles_sent', 0) or 0))
        strikes_sent.append(int(getattr(scoring.ai, 'strikes_sent', 0) or 0))
        piece_locks.append(int(getattr(scoring.ai, 'piece_locks', 0) or 0))

        if defeated_at is None:
            print(
                f"run {i+1}/{runs} seed={seed_i} survived_frames {max_frames} final_max_h {final_max_h} "
                f"clr {clears_total[-1]} ch {chains[-1]} mc {max_chain[-1]} "
                f"atk S{sprinkles_sent[-1]} T{strikes_sent[-1]} locks {piece_locks[-1]} heights {hs}"
            )
            defeat_frames.append(max_frames)
        else:
            print(
                f"run {i+1}/{runs} seed={seed_i} defeated_at {defeated_at} final_max_h {final_max_h} "
                f"clr {clears_total[-1]} ch {chains[-1]} mc {max_chain[-1]} "
                f"atk S{sprinkles_sent[-1]} T{strikes_sent[-1]} locks {piece_locks[-1]} heights {hs}"
            )
            defeat_frames.append(defeated_at)

    if runs > 1 and defeat_frames:
        try:
            print(
                "summary",
                "min", min(defeat_frames),
                "p10", _pct(defeat_frames, 0.10),
                "p50", _pct(defeat_frames, 0.50),
                "p90", _pct(defeat_frames, 0.90),
                "max", max(defeat_frames),
            )
        except Exception:
            pass

    if runs > 1:
        try:
            print(
                "telemetry",
                "clr_p50", _p50(clears_total),
                "ch_p50", _p50(chains),
                "mc_p50", _p50(max_chain),
                "S_p50", _p50(sprinkles_sent),
                "T_p50", _p50(strikes_sent),
                "locks_p50", _p50(piece_locks),
            )
        except Exception:
            pass


if __name__ == "__main__":
    main()
