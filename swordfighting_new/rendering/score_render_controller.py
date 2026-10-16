from __future__ import annotations


class ScoreRenderController:
    def draw_side_scores(self, client, snap: dict, *, margin: int, preview_stats_offset_y: int) -> None:
        scoring = snap.get('scoring')
        if not scoring:
            return
        enemy_has_board = bool(snap.get('enemy_has_board', True))
        p_score = scoring.get('player', {})
        ai_score = scoring.get('ai', {})
        lines_player = self.format_score_lines(p_score)
        lines_ai = self.format_score_lines(ai_score)
        self.blit_score_block(client, lines_player, client.left_preview_center_x, margin=margin, preview_stats_offset_y=preview_stats_offset_y)
        if enemy_has_board:
            self.blit_score_block(client, lines_ai, client.right_preview_center_x, margin=margin, preview_stats_offset_y=preview_stats_offset_y)

    def format_score_lines(self, sdict: dict) -> list[str]:
        last_chain = sdict.get('last_chain', {}) or {}
        passes = last_chain.get('passes', 0)
        total_cleared = last_chain.get('total_cleared', 0)
        return [
            f"Clr {sdict.get('clears_total',0)}",
            f"Ch {sdict.get('chains',0)} M{sdict.get('max_chain',0)}",
            f"Last {passes}p/{total_cleared}",
            f"Atk S{sdict.get('sprinkles_sent',0)} T{sdict.get('strikes_sent',0)}",
            f"In  S{sdict.get('sprinkles_received',0)} T{sdict.get('strikes_received',0)}",
            f"Locks {sdict.get('piece_locks',0)}",
        ]

    def blit_score_block(self, client, lines: list[str], center_x: int, *, margin: int, preview_stats_offset_y: int) -> None:
        y0 = int(getattr(client, '_content_offset_y', 0) or 0)
        y = y0 + int(margin) + int(preview_stats_offset_y)
        line_h = max(12, int(round(16 * float(getattr(client, 'ui_scale', 1.0) or 1.0))))
        for text in lines:
            surf = client.preview_font.render(text, True, (190, 190, 200))
            x = int(center_x) - surf.get_width() // 2
            client.screen.blit(surf, (x, y))
            y += int(line_h)
