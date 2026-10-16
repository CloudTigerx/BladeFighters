from __future__ import annotations

import os

from swordfighting_new.pygame_client import PygameClient


def main() -> None:
    # "Try B": make spawn-column-full the authoritative defeat rule.
    # If you want legacy behavior, set BF_DEFEAT_MODE to something else before launching.
    try:
        if os.getenv('BF_DEFEAT_MODE', None) is None:
            os.environ['BF_DEFEAT_MODE'] = 'b'
    except Exception:
        pass
    client = PygameClient()
    client.run()


if __name__ == "__main__":
    main()
