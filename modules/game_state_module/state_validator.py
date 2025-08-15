"""
State Validator
Validates state changes and ensures data integrity.
"""

from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
from .state_schema import GameState, ScreenType, GameMode, PuzzleState


@dataclass
class ValidationError:
    """Represents a validation error."""
    field: str
    message: str
    value: Any
    expected_type: Optional[type] = None


class StateValidator:
    """Validates game state changes and ensures data integrity."""
    
    def __init__(self):
        self.validation_rules = self._setup_validation_rules()
    
    def _setup_validation_rules(self) -> Dict[str, Dict[str, Any]]:
        """Setup validation rules for different state fields."""
        return {
            'screen.current_screen': {
                'type': ScreenType,
                'required': True,
                'validator': self._validate_screen_transition
            },
            'puzzle.game_active': {
                'type': bool,
                'required': True
            },
            'puzzle.score': {
                'type': int,
                'min_value': 0,
                'required': True
            },
            'puzzle.level': {
                'type': int,
                'min_value': 1,
                'max_value': 999,
                'required': True
            },
            'audio.master_volume': {
                'type': float,
                'min_value': 0.0,
                'max_value': 1.0,
                'required': True
            },
            'audio.music_volume': {
                'type': float,
                'min_value': 0.0,
                'max_value': 1.0,
                'required': True
            },
            'ui.ui_scale': {
                'type': float,
                'min_value': 0.1,
                'max_value': 3.0,
                'required': True
            },
            'game_running': {
                'type': bool,
                'required': True
            }
        }
    
    def validate_state_change(self, state: GameState, field_path: str, new_value: Any) -> List[ValidationError]:
        """Validate a state change for a specific field."""
        errors = []
        
        # Get validation rule for this field
        rule = self.validation_rules.get(field_path)
        if not rule:
            # No validation rule exists, allow the change
            return errors
        
        # Type validation
        if 'type' in rule:
            if not isinstance(new_value, rule['type']):
                errors.append(ValidationError(
                    field=field_path,
                    message=f"Expected type {rule['type'].__name__}, got {type(new_value).__name__}",
                    value=new_value,
                    expected_type=rule['type']
                ))
                return errors  # Stop validation if type is wrong
        
        # Range validation
        if 'min_value' in rule and new_value < rule['min_value']:
            errors.append(ValidationError(
                field=field_path,
                message=f"Value {new_value} is below minimum {rule['min_value']}",
                value=new_value
            ))
        
        if 'max_value' in rule and new_value > rule['max_value']:
            errors.append(ValidationError(
                field=field_path,
                message=f"Value {new_value} is above maximum {rule['max_value']}",
                value=new_value
            ))
        
        # Custom validation
        if 'validator' in rule:
            custom_errors = rule['validator'](state, field_path, new_value)
            errors.extend(custom_errors)
        
        return errors
    
    def _validate_screen_transition(self, state: GameState, field_path: str, new_value: ScreenType) -> List[ValidationError]:
        """Validate screen transitions."""
        errors = []
        current_screen = state.screen.current_screen
        
        # Check for invalid transitions
        invalid_transitions = {
            ScreenType.GAME: [ScreenType.LOADING],  # Can't go directly from loading to game
            ScreenType.TEST: [ScreenType.LOADING],  # Can't go directly from loading to test
        }
        
        if new_value in invalid_transitions and current_screen in invalid_transitions[new_value]:
            errors.append(ValidationError(
                field=field_path,
                message=f"Invalid transition from {current_screen.value} to {new_value.value}",
                value=new_value
            ))
        
        return errors
    
    def validate_full_state(self, state: GameState) -> List[ValidationError]:
        """Validate the entire game state."""
        errors = []
        
        # Validate all required fields
        for field_path, rule in self.validation_rules.items():
            if rule.get('required', False):
                value = self._get_nested_value(state, field_path)
                if value is None:
                    errors.append(ValidationError(
                        field=field_path,
                        message="Required field is None",
                        value=None
                    ))
        
        # Validate state consistency
        consistency_errors = self._validate_state_consistency(state)
        errors.extend(consistency_errors)
        
        return errors
    
    def _validate_state_consistency(self, state: GameState) -> List[ValidationError]:
        """Validate that the state is internally consistent."""
        errors = []
        
        # Game can't be active if not running
        if state.puzzle.game_active and not state.game_running:
            errors.append(ValidationError(
                field="puzzle.game_active",
                message="Game cannot be active when game is not running",
                value=state.puzzle.game_active
            ))
        
        # Can't be in game mode if not on game screen
        if state.puzzle.game_mode == GameMode.QUICKPLAY and state.screen.current_screen != ScreenType.GAME:
            errors.append(ValidationError(
                field="puzzle.game_mode",
                message="Quickplay mode requires game screen",
                value=state.puzzle.game_mode
            ))
        
        # Music volume can't exceed master volume
        if state.audio.music_volume > state.audio.master_volume:
            errors.append(ValidationError(
                field="audio.music_volume",
                message="Music volume cannot exceed master volume",
                value=state.audio.music_volume
            ))
        
        return errors
    
    def _get_nested_value(self, obj: Any, field_path: str) -> Any:
        """Get a nested value from an object using dot notation."""
        parts = field_path.split('.')
        current = obj
        
        for part in parts:
            if hasattr(current, part):
                current = getattr(current, part)
            else:
                return None
        
        return current
    
    def is_valid_state(self, state: GameState) -> bool:
        """Check if the entire state is valid."""
        return len(self.validate_full_state(state)) == 0 