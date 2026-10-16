"""player.py - Player-controlled fighter logic (decoupled from pygame UI).

Handles player input and delegates to base fighter functionality.
The only difference from AI is that this receives intents from user input
instead of generating them automatically.
"""
from __future__ import annotations
from typing import Dict, Any
from swordfighting_new.mechanics.timing import TimingConfig
from swordfighting_new.fighters.base_fighter import BaseFighter


class PlayerFighter(BaseFighter):
    """Player-controlled fighter that receives intents from user input."""
    
    def __init__(self, timing: TimingConfig, **kwargs):
        # Initialize base fighter with player name
        super().__init__(timing, fighter_name="Player", **kwargs)

    def update(self, intents: Dict[str, Any]):
        """Update player fighter with user-provided intents.
        
        Intents contract (dict keys used by update()):
        {
          'move': -1|0|1,          # horizontal move this frame
          'rotate_cw': bool,
          'rotate_ccw': bool,
          'fast': bool             # fast-fall (soft drop)
        }
        """
        # Log a 'decide' event approximated from player's current controllable state for ML dataset
        try:
            from swordfighting_new.util.stats_recorder import get_recorder
            from swordfighting_new.util.board_hash import compute_board_hash
            rec = get_recorder()
            cur = self.movement.current_piece
            if rec.enabled and cur is not None and getattr(cur, 'controllable', True):
                # Map intents to action (rotation target and col approximation)
                # We approximate chosen action as: desired rotation (0/1) from current, and target x = current x after move intent
                rotation = 0 if getattr(cur, 'orientation', 0) in (0,2) else 1
                if intents.get('rotate_cw') or intents.get('rotate_ccw'):
                    rotation = 1 - rotation
                x = getattr(cur, 'x', 0) + int(intents.get('move', 0))
                x = max(0, min(self.board.WIDTH - 1, x))
                # Build minimal mask and features
                heights = self.board.get_column_heights()
                mask = [0] * (self.board.WIDTH * 2)
                for c in range(self.board.WIDTH):
                    if heights[c] + 2 <= self.board.HEIGHT:
                        mask[0 * self.board.WIDTH + c] = 1
                for c in range(self.board.WIDTH - 1):
                    if max(heights[c], heights[c + 1]) + 1 <= self.board.HEIGHT:
                        mask[1 * self.board.WIDTH + c] = 1
                holes = self._count_holes_simple()
                bump = sum(abs(heights[i] - heights[i + 1]) for i in range(len(heights) - 1)) if heights else 0
                chosen = {
                    'rotation': int(rotation),
                    'x': int(x),
                    'legal_mask': mask,
                    'features': {
                        'holes': float(holes),
                        'height_max': float(max(heights) if heights else 0),
                        'surface_bumpiness': float(bump),
                    },
                    'board_hash': int(compute_board_hash(self.board)),
                }
                decision = {'why': 'human_input'}
                self._last_decision_id = (getattr(self, '_last_decision_id', 0) or 0) + 1
                self._last_decision_heights = list(heights)
                self._last_decision_holes = holes
                rec.record_decision(self.frame, 'player', getattr(self, 'seed', None), self._last_decision_id, decision, None, chosen)
        except Exception:
            pass
        # Update using base fighter logic with user intents
        super().update(intents)
