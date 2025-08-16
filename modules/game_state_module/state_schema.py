"""
Game State Schema Definitions
Defines the structure and types for all game state data.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Set, Optional, Any, Tuple
from enum import Enum
import time


class ScreenType(Enum):
    """Available screen types in the game."""
    LOADING = "loading"
    MAIN_MENU = "main_menu"
    STORY = "story"
    STORY_CONTENT = "story_content"
    TEST = "test"
    GAME = "game"
    SETTINGS = "settings"
    SMITHING = "smithing"
    INVENTORY = "inventory"
    UI_EDITOR = "ui_editor"


class GameMode(Enum):
    """Available game modes."""
    MENU = "menu"
    QUICKPLAY = "quickplay"
    STORY = "story"
    TEST = "test"
    MULTIPLAYER = "multiplayer"


class PuzzleState(Enum):
    """Puzzle game states."""
    IDLE = "idle"
    ACTIVE = "active"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    CHAIN_REACTION = "chain_reaction"
    BREAKING = "breaking"
    FALLING = "falling"


@dataclass
class ScreenState:
    """Screen-related state."""
    current_screen: ScreenType = ScreenType.LOADING
    previous_screen: Optional[ScreenType] = None
    screen_transition_time: float = field(default_factory=time.time)
    screen_cleanup_required: bool = False
    
    # Screen-specific state
    story_scroll_position: int = 0
    current_story: Dict[str, Any] = field(default_factory=lambda: {
        "title": "No Story Selected", 
        "content": []
    })


@dataclass
class PuzzleState:
    """Puzzle game state."""
    game_active: bool = False
    game_mode: GameMode = GameMode.MENU
    puzzle_state: PuzzleState = PuzzleState.IDLE
    
    # Grid state
    grid_width: int = 6
    grid_height: int = 15
    total_grid_height: int = 16
    block_size: int = 40
    
    # Piece state
    current_piece: Optional[Dict[str, Any]] = None
    next_piece: Optional[Dict[str, Any]] = None
    attached_piece: Optional[Dict[str, Any]] = None
    next_attached_piece: Optional[Dict[str, Any]] = None
    
    # Game mechanics state
    clusters: Set[Tuple[int, int]] = field(default_factory=set)
    breaking_blocks: List[Tuple[int, int, str]] = field(default_factory=list)
    chain_reaction_in_progress: bool = False
    chain_count: int = 0
    combo_multiplier: int = 1
    
    # Timing state
    last_fall_time: float = 0.0
    current_fall_speed: int = 640000
    normal_fall_speed: int = 640000
    accelerated_fall_speed: int = 2400
    
    # Animation state
    breaking_animation_start: float = 0.0
    breaking_animation_duration: float = 0.16
    
    # Statistics
    score: int = 0
    lines_cleared: int = 0
    level: int = 1
    
    # Debug state
    debug_mode: bool = False
    debug_breaks: bool = True
    enable_debug_logs: bool = False


@dataclass
class AudioState:
    """Audio system state."""
    master_volume: float = 0.6
    music_volume: float = 0.5
    sfx_volume: float = 0.7
    music_enabled: bool = True
    sfx_enabled: bool = True
    current_music: Optional[str] = None
    music_playing: bool = False
    mp3_player_visible: bool = False


@dataclass
class InputState:
    """Input system state."""
    # Key states
    keys_pressed: Set[int] = field(default_factory=set)
    keys_held: Set[int] = field(default_factory=set)
    
    # Mouse state
    mouse_position: Tuple[int, int] = (0, 0)
    mouse_buttons: Set[int] = field(default_factory=set)
    
    # Input timing
    last_input_time: float = 0.0
    input_cooldown: float = 0.05
    
    # DAS/ARR state
    das_time: float = 0.0
    arr_time: float = 0.0
    das_delay: float = 0.17
    arr_delay: float = 0.05
    
    # Input locking
    input_locked: bool = False
    input_lock_reason: Optional[str] = None
    input_lock_time: float = 0.0


@dataclass
class UIState:
    """UI system state."""
    ui_scale: float = 1.0
    brightness: float = 1.0
    vsync_enabled: bool = True
    fullscreen: bool = False
    borderless: bool = False
    native_fullscreen: bool = False
    particle_effects: bool = True
    show_fps: bool = False
    
    # UI element states
    settings_ui_open: bool = False
    input_tuner_visible: bool = False
    hovered_buttons: Set[str] = field(default_factory=set)


@dataclass
class GameState:
    """Complete game state container."""
    # Core state
    game_running: bool = True
    version: str = "1.0.0"
    start_time: float = field(default_factory=time.time)
    
    # Subsystem states
    screen: ScreenState = field(default_factory=ScreenState)
    puzzle: PuzzleState = field(default_factory=PuzzleState)
    audio: AudioState = field(default_factory=AudioState)
    input: InputState = field(default_factory=InputState)
    ui: UIState = field(default_factory=UIState)
    
    # System state
    initialized: bool = False
    loading_complete: bool = False
    error_state: Optional[str] = None
    
    # Performance state
    fps: float = 60.0
    frame_count: int = 0
    last_fps_update: float = 0.0
    
    # Debug state
    debug_mode: bool = False
    debug_info: Dict[str, Any] = field(default_factory=dict) 