import argparse
import os
import sys
from collections import deque
from pathlib import Path

# Allow running this script directly via `python tools/...py`.
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from swordfighting_new.mechanics.timing import DEFAULT_TIMING
from swordfighting_new.session import RubixOpponent, create_shared_piece_queue


def _piece_desc(p) -> str:
    try:
        blocks = list(getattr(p, "blocks", []) or [])
    except Exception:
        blocks = []
    parts = []
    for b in blocks:
        try:
            if b is None:
                parts.append("None")
                continue
            col = str(getattr(b, "color", "") or "").strip().lower()
            if not col:
                col = "?"
            tag = col[0]
            if bool(getattr(b, "is_breaker", False)):
                tag = f"{tag}*"
            if bool(getattr(b, "is_garbage", False)):
                tag = "#"
            parts.append(tag)
        except Exception:
            parts.append("?")
    return "[" + ",".join(parts) + "]"


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument(
        "--level",
        type=int,
        default=5,
        help="Rubix boss level/tier to simulate (default: 5).",
    )
    ap.add_argument("--max-frames", type=int, default=30_000)
    ap.add_argument("--budget-ms", type=float, default=6.0)
    ap.add_argument("--danger-height", type=int, default=10)
    ap.add_argument("--dump-last", type=int, default=8)
    ap.add_argument("--out", type=str, default="")
    args = ap.parse_args()

    try:
        os.environ["BF_RUBIX_PLAN_BUDGET_MS"] = str(float(args.budget_ms))
    except Exception:
        pass

    pq = create_shared_piece_queue(int(args.seed))
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

    last_piece_id = None
    last_piece_plan = {}

    # History of recent locks and plans (we print last N at end).
    locks = deque(maxlen=max(1, int(args.dump_last)))

    def record_lock(frame_i: int, label: str) -> None:
        hs = list(ai.board.get_column_heights())
        mh = max(hs) if hs else 0
        try:
            ascii_board = ai.board.render_ascii()
        except Exception:
            ascii_board = str(ai.board)
        locks.append(
            {
                "frame": int(frame_i),
                "label": str(label),
                "heights": hs,
                "max_h": int(mh),
                "ascii": ascii_board,
            }
        )

    ai_was_active = bool(getattr(getattr(ai, "chain_runner", None), "active", False))

    defeated_at = None
    for step in range(max(1, int(args.max_frames))):
        ai.update()

        # Track planning decisions at piece spawn.
        try:
            p = getattr(ai.movement, "current_piece", None)
        except Exception:
            p = None
        if p is not None and bool(getattr(p, "controllable", False)):
            pid = id(p)
            if pid != last_piece_id:
                last_piece_id = pid
                try:
                    tx = getattr(ai, "_plan_target_x", None)
                    to = getattr(ai, "_plan_target_o", None)
                except Exception:
                    tx = None
                    to = None

                last_piece_plan = {
                    "frame": int(getattr(ai, "frame", step) or step),
                    "piece": _piece_desc(p),
                    "cur_x": int(getattr(p, "x", 0) or 0),
                    "cur_o": int(getattr(p, "orientation", 0) or 0) % 4,
                    "tx": None if tx is None else int(tx),
                    "to": None if to is None else int(to) % 4,
                    "heights": list(ai.board.get_column_heights()),
                }

        # Detect new chain resolution start (proxy for piece lock).
        try:
            ai_is_active = bool(getattr(getattr(ai, "chain_runner", None), "active", False))
        except Exception:
            ai_is_active = False

        if (not ai_was_active) and ai_is_active:
            # lock moment
            f = int(getattr(ai, "frame", step) or step)
            hs = list(ai.board.get_column_heights())
            mh = max(hs) if hs else 0
            try:
                p_lock = getattr(ai.movement, "current_piece", None)
            except Exception:
                p_lock = None
            try:
                lock_x = int(getattr(p_lock, "x", -999)) if p_lock is not None else -999
            except Exception:
                lock_x = -999
            try:
                lock_o = int(getattr(p_lock, "orientation", -999)) % 4 if p_lock is not None else -999
            except Exception:
                lock_o = -999

            label = f"lock plan={last_piece_plan.get('piece')}"
            label += f" spawn=({last_piece_plan.get('cur_x')},{last_piece_plan.get('cur_o')})"
            label += f" lock=({lock_x},{lock_o})"
            label += f" -> tgt=({last_piece_plan.get('tx')},{last_piece_plan.get('to')})"
            label += f" pre_h={last_piece_plan.get('heights')} post_h={hs}"
            record_lock(f, label)

            if int(mh) >= int(args.danger_height):
                # Also emit a one-off immediate danger dump into stdout so you can see the turning point.
                print(f"[DANGER] seed={args.seed} frame={f} max_h={mh} heights={hs}")

        ai_was_active = ai_is_active

        if getattr(ai, "defeated", False):
            defeated_at = int(getattr(ai, "frame", step) or step)
            record_lock(defeated_at, "DEFEAT")
            break

    if defeated_at is None:
        defeated_at = int(args.max_frames)

    out_lines = []
    out_lines.append(f"seed={args.seed} budget_ms={args.budget_ms} defeated_at={defeated_at}")
    out_lines.append("")
    out_lines.append(f"last_{len(locks)}_locks:")
    out_lines.append("")
    for i, item in enumerate(list(locks), start=1):
        out_lines.append(f"--- {i}/{len(locks)} frame={item['frame']} {item['label']}")
        out_lines.append(f"heights={item['heights']} max_h={item['max_h']}")
        out_lines.append(item["ascii"])
        out_lines.append("")

    out_text = "\n".join(out_lines)

    out_path = (str(args.out or "").strip() or "").strip()
    if out_path:
        Path(out_path).write_text(out_text, encoding="utf-8")
    else:
        print(out_text)


if __name__ == "__main__":
    main()
