from __future__ import annotations


class SessionResetController:
    def reset_session(
        self,
        client,
        *,
        match_session_cls,
        bot_battle_session_cls,
        timing,
        attack_delay_frames: int,
        bulk_delivery: bool,
    ) -> None:
        mode = str(getattr(client, '_session_mode', 'match') or 'match').strip().lower()
        if mode == 'bot_battle':
            client.session = bot_battle_session_cls(
                timing=timing,
                attack_delay_frames=attack_delay_frames,
                bulk_delivery=bulk_delivery,
                seed=client._seed_val,
                bot_a_style=str(getattr(client, '_bot_battle_a_style', 'rubix3') or 'rubix3').strip().lower(),
                bot_b_style=str(getattr(client, '_bot_battle_b_style', 'rubix4') or 'rubix4').strip().lower(),
            )
        else:
            client.session = match_session_cls(
                timing=timing,
                attack_delay_frames=attack_delay_frames,
                bulk_delivery=bulk_delivery,
                seed=client._seed_val,
                enemy_style=client._enemy_style,
                boss_level=client._boss_level,
            )

        # Apply currently equipped sword (inventory) to the player.
        try:
            client._apply_equipped_sword_to_session()
        except Exception:
            pass

        # Apply selected enemy sword pattern (quickplay) to the AI.
        try:
            client._apply_enemy_sword_to_session()
        except Exception:
            pass

        # Allow Space to fast-fall immediately after resets.
        client._space_consumed = False
        client.fast = False
        client._last_offsets = {}
        client._cascade_tween = {}
        client._last_board_grid = {}
        client._last_snapshot = None
        try:
            client._audio.reset_runtime_state()
        except Exception:
            pass

        # Session resets can change layout-relevant mode (e.g., Rubix uses a full enemy board,
        # while other enemies use HP-mode). Recompute offsets and preview panel positions so
        # the enemy preview never overlaps the board after switching modes.
        try:
            client._recompute_ui_scale_and_assets()
        except Exception:
            pass
