from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class UIConfig:
    """Snapshot of runtime UI scaling values.

    This exists to decouple UI/layout helpers from module-level globals that are
    mutated at runtime (e.g., when switching modes or resizing).
    """

    scale: float

    cell_w: int
    cell_h: int
    margin: int
    board_gap: int

    preview_panel_width: int
    preview_label_offset_y: int
    preview_piece_offset_y: int
    preview_stats_offset_y: int

    @staticmethod
    def clamp_scale(scale: float) -> float:
        try:
            s = float(scale)
        except Exception:
            s = 1.0
        return max(0.45, s)

    @classmethod
    def from_scaled_values(
        cls,
        *,
        scale: float,
        cell_w: int,
        cell_h: int,
        margin: int,
        board_gap: int,
        preview_panel_width: int,
        preview_label_offset_y: int,
        preview_piece_offset_y: int,
        preview_stats_offset_y: int,
    ) -> "UIConfig":
        return cls(
            scale=cls.clamp_scale(scale),
            cell_w=int(cell_w),
            cell_h=int(cell_h),
            margin=int(margin),
            board_gap=int(board_gap),
            preview_panel_width=int(preview_panel_width),
            preview_label_offset_y=int(preview_label_offset_y),
            preview_piece_offset_y=int(preview_piece_offset_y),
            preview_stats_offset_y=int(preview_stats_offset_y),
        )
