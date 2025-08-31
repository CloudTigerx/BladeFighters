"""session.py - MatchSession orchestrates two fighters and attack exchange.

Responsibilities:
 - Own player + AI fighters
 - Apply player intents each frame
 - Tick both fighters
 - Collect ready outbound attacks and deliver to opponent with shared pacing
 - Provide a lightweight snapshot for rendering layer
"""
from __future__ import annotations
from typing import Dict, Any

from swordfighting_new.mechanics.timing import DEFAULT_TIMING
from swordfighting_new.fighters.player import PlayerFighter
import random


class MatchSession:
    def __init__(self, timing=DEFAULT_TIMING, attack_delay_frames: int = 24, bulk_delivery: bool = True):
        self.timing = timing
        # Disable puzzle microsecond speeds so gravity ticks are more frequent/visible during tuning.
        self.player = PlayerFighter(timing, attack_delay_frames=attack_delay_frames, bulk_delivery=bulk_delivery,
                                    enable_puzzle_speeds=False)
        # AI is now just a second PlayerFighter with identical mechanics
        self.ai = PlayerFighter(timing, spawn_x=6, attack_delay_frames=attack_delay_frames, bulk_delivery=bulk_delivery,
                               enable_puzzle_speeds=False)
        self.attack_delay_frames = attack_delay_frames
        self.bulk_delivery = bulk_delivery
        self.frame = 0
        # AI decision making parameters (moved from old AIFighter)
        self.ai_decision_interval = 10
        self.ai_h_move_prob = 0.55
        self.ai_rotate_prob = 0.25
        self.ai_fast_trigger_prob = 0.18
        self.ai_fast_burst_min = 18
        self.ai_fast_burst_max = 40
        self.ai_fast_remaining = 0

    def _generate_ai_intents(self):
        """Generate static intents for the AI player (no movement)"""
        return {'move': 0, 'rotate_cw': False, 'rotate_ccw': False, 'fast': False}

    def update(self, intents: Dict[str, Any]):
        self.frame += 1
        # Update fighters
        self.player.update(intents)
        ai_intents = self._generate_ai_intents()
        self.ai.update(ai_intents)

        # Exchange attacks (player -> AI)
        p_out = self.player.collect_ready_attacks()
        if p_out:
            # PlayerFighter uses receive_attacks instead of individual add_* methods
            self.ai.receive_attacks(p_out)

        # AI outbound -> player inbound
        ai_out = self.ai.collect_ready_attacks()
        if ai_out:
            self.player.receive_attacks(ai_out)

    def snapshot(self):
        return {
            'player': {
                'board': self.player.get_board(),
                'piece': self.player.get_piece(),
                'next_piece': self.player.get_next_piece(),
                'garbage_fallers': self.player.get_garbage_fallers(),
                'defeated': self.player.defeated,
            },
            'ai': {
                'board': self.ai.get_board(),
                'piece': self.ai.get_piece(),
                'next_piece': self.ai.get_next_piece(),
                'garbage_fallers': self.ai.get_garbage_fallers(),
                'defeated': self.ai.defeated,
            },
            'frame': self.frame
        }
