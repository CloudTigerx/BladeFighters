"""
Test for the new attack delivery services.
Verifies that planner, animator, and committer work together correctly.
"""

import pytest
from unittest.mock import Mock, MagicMock
from .attack_delivery_planner import AttackDeliveryPlanner, DeliveryConfig, DeliveryPlan
from .attack_delivery_animator import AttackDeliveryAnimator, AnimationState
from .attack_delivery_committer import AttackDeliveryCommitter, CommitResult


class TestAttackDeliveryServices:
    """Test the attack delivery service integration."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.config = DeliveryConfig(
            attacks_fall_enabled=True,
            fall_garbage_enabled=True,
            fall_strikes_enabled=True,
            fall_speed_scale=0.75
        )
        self.planner = AttackDeliveryPlanner(self.config)
        self.animator = AttackDeliveryAnimator(self.config)
        self.committer = AttackDeliveryCommitter(self.config)
        
        # Mock engine
        self.engine = Mock()
        self.engine.grid_width = 6
        self.engine.grid_height = 12
        self.engine.puzzle_grid = [[None for _ in range(6)] for _ in range(12)]
        
        # Mock renderer and animation state manager
        self.mock_asm = Mock()
        self.mock_asm.fall_animation_duration = 0.085
        self.mock_asm.visual_falling_blocks = {}
        self.mock_renderer = Mock()
        self.mock_renderer.animation_state_manager = self.mock_asm
        self.engine.renderer = self.mock_renderer
        
        # Mock test_mode and garbage_block_brightness
        self.engine.test_mode = Mock()
        self.engine.test_mode.garbage_block_brightness = {}
        
        # Mock item system
        self.item_system = Mock()
        self.item_system.get_garbage_color_for_column.return_value = 'red'
        self.item_system.get_strike_color_for_cell.return_value = 'yellow'
        
        # Mock column rotator
        self.column_rotator = Mock()
    
    def test_garbage_delivery_workflow(self):
        """Test complete garbage delivery workflow."""
        # Create attack data
        attack_data = {
            'blocks_remaining': 3,
            'sprinkle_side': 'R',
            'handedness': 'R'
        }
        
        # Plan delivery
        plan = self.planner.plan_garbage_delivery(
            self.engine, attack_data, 'player', self.item_system)
        
        assert plan.attack_type == 'garbage'
        assert plan.target_player == 'player'
        assert len(plan.garbage_blocks) == 3
        
        # Start animation
        animation_state = self.animator.start_garbage_animation(
            self.engine, plan, 0.0)
        
        assert animation_state.is_active
        assert len(animation_state.animation_keys) == 3
        
        # Commit to grid
        result = self.committer.commit_garbage(self.engine, plan, 'player')
        
        assert result.blocks_placed == 3
        assert result.blocks_pierced == 0
        assert len(result.written_positions) == 3
    
    def test_strike_delivery_workflow(self):
        """Test complete strike delivery workflow."""
        # Create attack data
        attack_data = {
            'strike_details': ['2x3'],
            'pierce_budgets': [2],
            'handedness': 'R',
            'sprinkle_side': 'R'
        }
        
        # Plan delivery
        plan = self.planner.plan_strike_delivery(
            self.engine, attack_data, 'player', self.item_system, self.column_rotator)
        
        assert plan.attack_type == 'strike'
        assert plan.target_player == 'player'
        assert len(plan.strike_patterns) == 1
        
        # Start animation
        animation_state = self.animator.start_strike_animation(
            self.engine, plan, 0.0)
        
        assert animation_state.is_active
        # Should animate top and bottom cells per column
        assert len(animation_state.animation_keys) == 4  # 2 columns * 2 cells
        
        # Commit to grid
        result = self.committer.commit_strikes(self.engine, plan, 'player')
        
        assert result.blocks_placed == 6  # 2x3 pattern
        assert result.blocks_pierced == 0  # No existing blocks to pierce
        assert len(result.written_positions) == 6
    
    def test_piercing_logic(self):
        """Test that piercing logic works correctly."""
        # Set up grid with existing blocks
        self.engine.puzzle_grid[10][0] = 'red_block'
        self.engine.puzzle_grid[10][1] = 'blue_block'
        
        attack_data = {
            'strike_details': ['2x2'],
            'pierce_budgets': [3],  # Enough budget to pierce both blocks
            'handedness': 'R',
            'sprinkle_side': 'R'
        }
        
        plan = self.planner.plan_strike_delivery(
            self.engine, attack_data, 'player', self.item_system, self.column_rotator)
        
        result = self.committer.commit_strikes(self.engine, plan, 'player')
        
        assert result.blocks_placed == 4  # 2x2 pattern
        assert result.blocks_pierced == 2  # Should pierce both existing blocks
        assert len(result.written_positions) == 4
    
    def test_animation_completion_check(self):
        """Test animation completion detection."""
        # Create animation state
        animation_state = AnimationState(
            is_active=True,
            start_time=0.0,
            end_time=1.0,
            animation_keys=[(0, 0)]
        )
        
        # Should not be complete while animation is active
        self.mock_asm.visual_falling_blocks = {(0, 0): {'start_time': 0.0, 'duration': 0.1}}
        assert not self.animator.is_animation_complete(self.engine, animation_state, 0.05)
        
        # Should be complete after timeout
        assert self.animator.is_animation_complete(self.engine, animation_state, 1.1)
        
        # Should be complete when no animations are active
        self.mock_asm.visual_falling_blocks = {}
        assert self.animator.is_animation_complete(self.engine, animation_state, 0.05) 