from __future__ import annotations

from typing import Any, Dict, List


class _NoopRecorder:
    enabled: bool = False

    def record_attack(self, *args: Any, **kwargs: Any) -> None:
        pass

    def record_chain(self, *args: Any, **kwargs: Any) -> None:
        pass

    def record_piece(self, *args: Any, **kwargs: Any) -> None:
        pass

    def record_decision(self, *args: Any, **kwargs: Any) -> None:
        pass


_rec = _NoopRecorder()


def get_recorder() -> _NoopRecorder:
    return _rec


