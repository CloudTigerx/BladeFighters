YAML schema for black-box reactor replays

Each fixture file under `tests/reactor_blackbox/fixtures/*.yaml` uses this minimal schema:

- setup:
  - layout: 2D list of tokens, top row first. Width must be 6, height can be ≤ 16. Tokens:
    - Normal blocks: `r`, `b`, `g`, `y`
    - Breakers: `R`, `B`, `G`, `Y`
    - Empty: `.` or `X`
- inputs: list of timed actions:
  - Each: { t: <ms>, action: one of `left|right|down|rotate_cw|rotate_ccw|flip|drop|tick|noop` }
  - Time is absolute milliseconds on a deterministic FakeClock timeline.
- expect:
  - final_checksum: short hex string (first 16 chars of SHA1 over visible grid rows)
  - payloads: list of objects with fields: kind, count, pattern (pattern is None for garbage)

Notes
- The harness uses public engine APIs only: `PuzzleEngine`, `place_pieces`, `update`, movement and rotation methods, and the `blocks_broken_handler` callback.
- Time is controlled by `FakeClock`; the harness monkeypatches `pygame.time.get_ticks()` so the reactor’s timing is deterministic.
- Payloads are produced by `AttacksService` from combo callbacks and translated to a minimal DTO for assertions.

