import pygame
import sys
import os
import time
import json
from pathlib import Path

# Import resolution enhancer
from resolution_enhancer import resolution_enhancer

# Import loading screen first
from modules.loading_module.loading_screen import LoadingScreen

# Import all extracted modules - all are working properly
from modules.audio_module import AudioSystem
from modules.menu_module.draggable_menu_system import DraggableMenuSystem  # Use draggable menu system

from modules.testmode_module import TestMode
from modules.screen_module import ScreenManager
from modules.story_module import StorySystem
from modules.items_module import ItemSystem
# Settings system (reintroduced)
from modules.settings_module.config_service import ConfigService
from modules.settings_module.settings_ui import SettingsUI
from modules.settings_module.controls_service import ControlsService
from modules.logging_module.logger import configure_logging, get_logger
from modules.asset_module.preflight import AssetPreflight
from modules.replay_module.record import InputRecorder
from modules.replay_module.replay import InputReplayer

# All extracted modules loaded successfully

from core.puzzle_module import PuzzleEngine
from core.puzzle_renderer import PuzzleRenderer
from utils.clock import PygameClock, Clock
from core.ui.input_tuner_overlay import InputTunerOverlay

# Constants
ASSET_PATH = "puzzleassets"
ROOT_PATH = os.path.dirname(os.path.abspath(__file__))

class GameClient:
    def __init__(self, clock: Clock = None):
        """Initialize the game client."""
        pygame.init()
        self.clock: Clock = clock or PygameClock()
        
        os.environ['SDL_VIDEO_VSYNC'] = '1'  # Default to V-Sync enabled
        self.asset_path = ASSET_PATH
        
        # Use enhanced resolution system
        self.resolutions = resolution_enhancer.get_resolution_list()
        
        # Get desktop info for default resolution
        desktop_info = pygame.display.Info()
        desktop_width, desktop_height = desktop_info.current_w, desktop_info.current_h
        
        # Load config first to get user's preferred resolution
        self.config = ConfigService(os.path.join(ROOT_PATH, "game_settings.json"))
        self.config.load()
        
        # Get resolution from settings, fallback to optimal resolution
        resolution_setting = self.config.get("resolution", "2560x1440")
        try:
            # Parse resolution string (e.g., "2560x1440")
            width_str, height_str = resolution_setting.split("x")
            self.width, self.height = int(width_str), int(height_str)
        except (ValueError, AttributeError):
            # Fallback to optimal resolution if settings parsing fails
            self.width, self.height = resolution_enhancer.get_optimal_resolution(desktop_width, desktop_height)
        
        # Create window with default resolution
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        pygame.display.set_caption("Blade Fighters")
        
        self.font = None
        self.audio = None
        self.menu_system = None
        self.settings_ui = None  # Settings UI overlay
        self.test_mode = None
        self.screen_manager = None
        self.story_system = None
        self.puzzle_engine = None
        self.puzzle_renderer = None
        self.item_system = None
        self.input_tuner = None
        
        # Notification system
        self.notifications = []
        self.notification_duration = 3000  # 3 seconds
        
        # Logging first to capture early diagnostics
        try:
            log_level = os.environ.get("BLADE_LOG_LEVEL", "INFO")
            log_file = os.environ.get("BLADE_LOG_FILE")
            configure_logging(level=log_level, file_path=log_file)
        except Exception:
            pass
        self.logger = get_logger("GameClient")

        # Config service (already loaded above)
        # Controls
        self.controls = ControlsService(os.path.join(ROOT_PATH, "game_controls.json"))
        self.controls.load()

        # Game state
        self.game_running = True
        self.version = "1.0.0"
        self._preflight_report = None
        self._preflight_toast_until_ms = None
        # Record/Replay
        self._recorder: InputRecorder = None
        self._replayer: InputReplayer = None
        self._replay_active: bool = False
        self._replay_started: bool = False
        self._seed_for_run: int = None
        
        # Colors
        self.BLACK = (0, 0, 0)
        self.WHITE = (255, 255, 255)
        self.GRAY = (100, 100, 100)
        self.LIGHT_GRAY = (200, 200, 200)
        self.BLUE = (0, 100, 255)
        self.LIGHT_BLUE = (100, 150, 255)
        
        # Story content view variables
        self.story_scroll_position = 0
        self.current_story = {"title": "No Story Selected", "content": []}
        
        # Background images (will be loaded during initialization)
        self.main_background = None
        self.puzzle_background = None
        self.story_background = None
        
        # Current screen (will be set after loading)
        self.current_screen = "loading"
        
        self.brightness = 1.0  # Default brightness

        # Seed RNG if CLI arg provided
        try:
            cli_seed = None
            if '--seed' in sys.argv:
                idx = sys.argv.index('--seed')
                if idx + 1 < len(sys.argv):
                    cli_seed = int(sys.argv[idx + 1])
            if cli_seed is not None:
                import random
                random.seed(cli_seed)
                try:
                    import numpy as np  # optional
                    np.random.seed(cli_seed)
                except Exception:
                    pass
                self._seed_for_run = cli_seed
                self.logger.info(f"Run RNG seed: {cli_seed}")
        except Exception:
            pass

        # Optional asset preflight (runs once at startup)
        try:
            run_preflight = bool(self.config.get('run_asset_preflight', True))
        except Exception:
            run_preflight = True
        if run_preflight:
            try:
                preflight = AssetPreflight(asset_root=Path(self.asset_path), logger=self.logger)
                report = preflight.run_checks()
                self._preflight_report = report
                summary = (
                    f"Asset Preflight: ok={report['ok']} "
                    f"images={report['counts'].get('images_checked', 0)} "
                    f"sounds={report['counts'].get('sounds_checked', 0)} "
                    f"configs={report['counts'].get('configs_checked', 0)} "
                    f"fonts={report['counts'].get('fonts_checked', 0)}"
                )
                self.logger.info(summary)
                if not report['ok']:
                    for err in report['errors']:
                        self.logger.error(err)
                    for warn in report['warnings']:
                        self.logger.warning(warn)
                    try:
                        self._preflight_toast_until_ms = self.clock.now_ms() + 8000
                    except Exception:
                        self._preflight_toast_until_ms = None
            except Exception as e:
                # Never block startup on preflight
                try:
                    self.logger.error(f"Asset preflight failed: {e}")
                except Exception:
                    pass

        # Window mode will be set based on user preferences in the settings application

        # Record/Replay CLI wiring
        try:
            if '--record' in sys.argv:
                i = sys.argv.index('--record')
                if i + 1 < len(sys.argv):
                    self._recorder = InputRecorder()
                    self._rec_path = sys.argv[i + 1]
                    self._recorder.start(seed=self._seed_for_run or 0, settings=self.config.settings)
            if '--replay' in sys.argv:
                i = sys.argv.index('--replay')
                if i + 1 < len(sys.argv):
                    path_or_token = sys.argv[i + 1]
                    session = None
                    try:
                        # Try token first
                        from tools.repro_token import unpack as unpack_token
                        session = unpack_token(path_or_token)
                    except Exception:
                        # Fallback to file path
                        import json
                        with open(path_or_token, 'r', encoding='utf-8') as f:
                            session = json.load(f)
                    self._replayer = InputReplayer(session, self.clock)
                    self._replay_active = True
        except Exception as e:
            try:
                self.logger.error(f"Record/Replay wiring failed: {e}")
            except Exception:
                pass
    
    def _initialize_font(self):
        """Initialize the font system."""
        try:
            # Calculate appropriate font size for current resolution
            base_font_size = 36
            font_size = resolution_enhancer.get_font_size_for_resolution(base_font_size, self.width, self.height)
            
            font_path = os.path.join(ASSET_PATH, "fonts", "PermanentMarker-Regular.ttf")
            if os.path.exists(font_path):
                self.font = pygame.font.Font(font_path, font_size)
            else:
                self.font = pygame.font.SysFont('Arial', font_size)
        except Exception as e:
            fallback_size = resolution_enhancer.get_font_size_for_resolution(36, self.width, self.height)
            self.font = pygame.font.SysFont('Arial', fallback_size)
    
    def _initialize_audio_system(self):
        """Initialize the audio system."""
        self.audio = AudioSystem(".", ASSET_PATH)
    
    def _initialize_menu_system(self):
        """Initialize the menu system."""
        # Use quickplay mode for the menu system to get the correct background
        self.menu_system = DraggableMenuSystem(self.screen, self.font, self.audio, self.asset_path, game_mode="quickplay")
        # Apply initial UI scale
        try:
            self.menu_system.ui_scale = float(self.config.get('ui_scale', 1.0))
        except Exception:
            pass
    
    def _initialize_settings_ui(self):
        """Initialize the modern settings UI overlay."""
        # Import the modern settings UI
        from modules.settings_module.modern_settings_ui import ModernSettingsUI
        
        callbacks = {
            'master_volume': (lambda v: self.audio.set_volume(v) if hasattr(self, 'audio') and self.audio else None),
            'music_volume': (lambda v: self.audio.set_music_volume(v) if hasattr(self, 'audio') and self.audio else None),
            'ui_scale': self.set_ui_scale,
            'vsync': self.set_vsync,
            'fullscreen': self.set_fullscreen,
            'native_fullscreen': self.set_native_fullscreen,
            'borderless': self.set_borderless,
            'particle_effects': self.set_particle_effects,
            'show_fps': self.set_show_fps,
            'resolution': self._change_resolution_from_settings,
        }
        
        self.settings_ui = ModernSettingsUI(
            self.screen,
            self.config,
            callbacks
        )
        
        # Create input tuner overlay (depends on settings/config and input handler later)
        # DISABLED: Input tuner overlay completely disabled
        self.input_tuner = None
    
    def _change_resolution_from_settings(self, resolution_str: str):
        """Change resolution from settings dropdown."""
        try:
            # Parse resolution string (e.g., "1920x1080")
            if 'x' in resolution_str:
                width, height = map(int, resolution_str.split('x'))
                print(f"🖥️ Changing resolution to {width}x{height} from settings")
                self.change_resolution(width, height)
            else:
                print(f"⚠️ Invalid resolution format: {resolution_str}")
        except Exception as e:
            print(f"⚠️ Error changing resolution: {e}")
    
    def _initialize_test_mode(self):
        """Initialize the test mode."""
        try:
            self.test_mode = TestMode(self.screen, self.font, self.audio, self.asset_path, self.settings_ui, clock=self.clock)
            
            # Add equip notification callback to test mode player items
            if hasattr(self.test_mode, 'player_items') and self.test_mode.player_items:
                def equip_notification_callback(weapon):
                    self.add_notification(f"⚔️ Equipped: {weapon.name}", (120, 255, 120))
                self.test_mode.player_items.add_equip_callback(equip_notification_callback)
            
            pass
        except Exception as e:
            self.test_mode = None
    
    def _initialize_screen_manager(self):
        """Initialize the screen manager."""
        self.screen_manager = ScreenManager(self.screen, self.font, self.width, self.height)
        print("✅ Screen manager initialized")
    
    def _initialize_story_system(self):
        """Initialize the story system."""
        self.story_system = StorySystem(self.screen, self.font, self.width, self.height, self.menu_system)
        print("✅ Story system initialized")
    
    def _initialize_puzzle_engine(self):
        """Initialize the puzzle engine."""
        try:
            self.puzzle_engine = PuzzleEngine(self.screen, self.font, self.audio, self.asset_path, self.settings_ui, game_mode="default")
            
            # Provide unified clock to the engine for subsystems (e.g., input handler)
            try:
                setattr(self.puzzle_engine, 'clock', self.clock)
            except Exception:
                pass
            # Ensure input tuner overlay is wired with the actual input handler
            # DISABLED: Input tuner overlay completely disabled
            pass
            print("✅ Puzzle engine initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize puzzle engine: {e}")
            import traceback
            traceback.print_exc()
            self.puzzle_engine = None
            raise
    
    def _initialize_puzzle_renderer(self):
        """Initialize the puzzle renderer."""
        try:
            # Always create a puzzle renderer for quickplay mode
            # TestMode can create its own renderers separately if needed
            
            # Check if puzzle engine was initialized successfully
            if not hasattr(self, 'puzzle_engine') or self.puzzle_engine is None:
                raise RuntimeError("Puzzle engine must be initialized before renderer")
            
            self.puzzle_renderer = PuzzleRenderer(self.puzzle_engine, clock=self.clock)
            print("✅ Puzzle renderer initialized successfully")
            
        except Exception as e:
            print(f"❌ Failed to initialize puzzle renderer: {e}")
            import traceback
            traceback.print_exc()
            self.puzzle_renderer = None
            raise
    
    def _load_background_images(self):
        """Load background images using simple direct loading."""
        try:
            # Simple direct loading like the working Dev2 system
            self.main_background = pygame.image.load(os.path.join(ASSET_PATH, "menus", "Official_mainmenu_background.png"))
            if self.main_background:
                print("✅ Loaded main menu background")
            else:
                print("⚠️ Failed to load main menu background")
        except Exception as e:
            self.main_background = None
            print(f"⚠️ Failed to load main menu background: {e}")
        
        try:
            self.puzzle_background = pygame.image.load(os.path.join(ASSET_PATH, "puzzlebackground.png"))
            print("✅ Loaded puzzle background")
        except pygame.error:
            self.puzzle_background = None
            print("⚠️ Failed to load puzzle background")
        
        try:
            self.story_background = pygame.image.load(os.path.join(ASSET_PATH, "storybackground.png"))
            print("✅ Loaded story background")
        except pygame.error:
            self.story_background = None
            print("⚠️ Failed to load story background")
    
    def _complete_initialization(self):
        """Complete the initialization process."""
        try:
            from modules.items_module.item_system import create_rusted_sword
            self.item_system = ItemSystem()
            self.item_system.equip_weapon(create_rusted_sword())
            print("✅ Item system initialized and Rusted Sword equipped")
        except Exception as e:
            print(f"⚠️ Item system init failed: {e}")
        # Apply initial settings (audio, vsync/fullscreen, particles)
        try:
            if hasattr(self, 'audio') and self.audio and hasattr(self, 'config') and self.config:
                self.audio.set_volume(self.config.get('master_volume', 0.6))
                self.audio.set_music_volume(self.config.get('music_volume', 0.5))
            # VSync and fullscreen
            self.set_vsync(bool(self.config.get('vsync', True)))
            if bool(self.config.get('native_fullscreen', False)):
                self.set_native_fullscreen(True)
            elif bool(self.config.get('borderless', False)):
                self.set_borderless(True)
            elif bool(self.config.get('fullscreen', False)):
                self.set_fullscreen(True)
            # Particles
            self.set_particle_effects(bool(self.config.get('particle_effects', True)))
        except Exception:
            pass
        # Ensure menu system is initialized
        if not self.menu_system:
            self._initialize_menu_system()
        
        self.current_screen = "main_menu"
        print("✅ Game initialization complete!")

    
    def set_screen(self, screen_name):
        """Set the current screen."""
        # Use screen manager if available
        if hasattr(self, 'screen_manager') and self.screen_manager:
            self.screen_manager.set_screen(screen_name)
            self.current_screen = self.screen_manager.get_current_screen()
        else:
            # Legacy screen management
            print(f"Game Client: Setting screen to {screen_name}")
            self.current_screen = screen_name
        
        # Screen-specific initialization
        if screen_name == "settings":
            # Open settings overlay on top of main menu
            if hasattr(self, 'settings_ui') and self.settings_ui:
                self.settings_ui.open()
            self.current_screen = "main_menu"
        elif screen_name == "ui_editor":
            print("Game Client: Switching to UI editor")
        elif screen_name == "test":
            if hasattr(self, 'test_mode') and self.test_mode:
                self.test_mode.initialize_test()
                # Reload UI positions to ensure the latest positions are used
                self.test_mode.setup_board_positions()
        elif screen_name == "main_menu" and hasattr(self, 'test_mode') and self.test_mode:
            # Make sure the test mode has the latest UI positions when going back to main menu
            self.test_mode.setup_board_positions()
        elif screen_name == "game":
            # Ensure next-piece preview is shown in Quickplay (single-player)
            try:
                if hasattr(self, 'puzzle_renderer') and self.puzzle_renderer:
                    self.puzzle_renderer.preview_side = 'left'
            except Exception:
                pass
            self.puzzle_engine.start_game()
    


    
    def draw_placeholder_settings(self):
        """Draw a placeholder 'Coming Soon' settings screen."""
        # Fill with dark gradient background
        self.screen.fill((20, 20, 50))
        
        # Draw "Settings Coming Soon" message
        title_font = pygame.font.SysFont('Arial', 64, bold=True)
        title_text = title_font.render("Settings Coming Soon", True, (255, 255, 255))
        title_rect = title_text.get_rect(center=(self.width//2, self.height//2 - 100))
        self.screen.blit(title_text, title_rect)
        
        # Draw subtitle
        subtitle_font = pygame.font.SysFont('Arial', 32)
        subtitle_text = subtitle_font.render("The settings system is being redesigned", True, (200, 200, 200))
        subtitle_rect = subtitle_text.get_rect(center=(self.width//2, self.height//2 - 40))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Draw instructions
        instruction_font = pygame.font.SysFont('Arial', 28)
        instruction_text = instruction_font.render("Press ESC or click anywhere to return to main menu", True, (150, 150, 150))
        instruction_rect = instruction_text.get_rect(center=(self.width//2, self.height//2 + 50))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Draw a nice border around the whole message
        border_rect = pygame.Rect(self.width//2 - 400, self.height//2 - 150, 800, 250)
        pygame.draw.rect(self.screen, (100, 100, 255), border_rect, 3, border_radius=10)
        
        # Add some visual flair with a subtle glow effect
        glow_rect = pygame.Rect(self.width//2 - 405, self.height//2 - 155, 810, 260)
        pygame.draw.rect(self.screen, (50, 50, 150), glow_rect, 2, border_radius=12)
    
    def change_resolution(self, width, height):
        """Change the game's resolution."""
        print(f"🖥️ Changing resolution from {self.width}x{self.height} to {width}x{height}")
        
        # Update the screen dimensions
        self.width = width
        self.height = height
        
        # Update the display mode
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
        
        # Update resolution enhancer with new resolution
        if hasattr(self, 'resolutions') and self.resolutions:
            # Update the current resolution in the enhancer
            resolution_enhancer.current_resolution = (width, height)
            print(f"📏 Updated resolution in enhancer: {width}x{height}")
        
        # Update UI scaler with new scale factor (if it exists)
        if hasattr(self, 'ui_scaler') and self.ui_scaler:
            # Calculate new scale factor based on resolution
            base_width, base_height = 1920, 1080
            scale_x = width / base_width
            scale_y = height / base_height
            new_scale_factor = min(scale_x, scale_y)
            
            # Apply Retina adjustments if needed
            if resolution_enhancer.is_retina:
                new_scale_factor *= 0.6
            
            # Clamp to reasonable range
            new_scale_factor = max(0.6, min(1.2, new_scale_factor))
            
            self.ui_scaler.scale_factor = new_scale_factor
            print(f"🎨 Updated UI scaler scale factor: {new_scale_factor}")
        
        # Update menu system with new screen and scaling
        if hasattr(self, 'menu_system') and self.menu_system:
            self.menu_system.screen = self.screen
            self.menu_system.width = self.width
            self.menu_system.height = self.height
            # Force menu system to recalculate scaling
            if hasattr(self.menu_system, 'ui_scaler') and self.menu_system.ui_scaler:
                self.menu_system.ui_scaler.scale_factor = new_scale_factor if 'new_scale_factor' in locals() else 1.0
        
        # Update settings system with new screen
        if hasattr(self, 'settings_ui') and self.settings_ui:
            self.settings_ui.screen = self.screen
            self.settings_ui.width = self.width
            self.settings_ui.height = self.height
            # Force settings UI to recalculate positions
            self.settings_ui._create_ui_components()
        
        # Update screen manager with new resolution
        if hasattr(self, 'screen_manager') and self.screen_manager:
            self.screen_manager.handle_resolution_change(width, height)
        
        # Update story system with new resolution
        if hasattr(self, 'story_system') and self.story_system:
            self.story_system.update_resolution(width, height)
        
        # If we're in test mode, update the board positions
        if hasattr(self, 'test_mode'):
            self.test_mode.setup_board_positions()
        
        # Play click sound if available
        if hasattr(self.audio, 'sounds') and 'click' in self.audio.sounds:
            self.audio.sounds['click'].play()
        
        print(f"✅ Resolution change completed: {width}x{height}")
    
    def start_quickplay(self):
        """Start the game in quickplay mode."""
        print("🎮 Starting quickplay mode")
        
        # Ensure components are initialized - create them if missing
        try:
            # Always create a new puzzle engine for quickplay mode (replace any existing one)
            print("🔧 Creating puzzle engine for quickplay...")
            from core.puzzle_module import PuzzleEngine
            
            # Create a basic font if missing
            if not hasattr(self, 'font') or self.font is None:
                import pygame
                self.font = pygame.font.Font(None, 36)
            
            self.puzzle_engine = PuzzleEngine(self.screen, self.font, self.audio, self.asset_path, self.settings_ui, game_mode="quickplay")
            if hasattr(self, 'clock'):
                setattr(self.puzzle_engine, 'clock', self.clock)
            print("✅ Puzzle engine created for quickplay")
            
            # Always create a new puzzle renderer for quickplay mode (replace any existing one)
            print("🔧 Creating puzzle renderer for quickplay...")
            from core.puzzle_renderer import PuzzleRenderer
            self.puzzle_renderer = PuzzleRenderer(self.puzzle_engine, clock=getattr(self, 'clock', None))
            print("✅ Puzzle renderer created for quickplay")
            
            # Configure and start
            print("🎮 Configuring quickplay mode...")
            self.set_screen("game")
            self.puzzle_renderer.preview_side = 'left'  # Configure for single player
            self.puzzle_engine.start_game()
            print("✅ Quickplay mode started successfully")
            
        except Exception as e:
            print(f"❌ Failed to start quickplay: {e}")
            import traceback
            traceback.print_exc()

    def _apply_intents(self, intents):
        try:
            ih = getattr(self.puzzle_engine, 'input_handler', None)
            for ev in intents:
                intent = ev.get('intent')
                data = ev.get('data') or {}
                if intent == 'move_l':
                    self.puzzle_engine.move_piece(-1, 0)
                elif intent == 'move_r':
                    self.puzzle_engine.move_piece(1, 0)
                elif intent == 'rotate':
                    self.puzzle_engine.rotate_attached_piece(int(data.get('dir', 1)) or 1)
                elif intent == 'drop':
                    # Treat as hold: accelerate
                    self.puzzle_engine.current_fall_speed = self.puzzle_engine.accelerated_fall_speed
                    self.puzzle_engine.micro_fall_time = self.puzzle_engine._calculate_micro_fall_time(self.puzzle_engine.current_fall_speed)
                elif intent == 'pause':
                    self.set_screen('main_menu')
        except Exception:
            pass
    

    

    
    def display_custom_mp3_player(self):
        """Display only the custom MP3 player image with functional buttons."""
        if not hasattr(self.audio, 'mp3_player') or not self.audio.mp3_player:
            return
        
        # Simply use the MP3 player's own draw method
        # This will draw the MP3 player with consistent button positioning
        self.mp3_player_buttons = self.audio.mp3_player.draw(self.screen, self.width, self.height)
        
        return self.mp3_player_buttons
    
    def get_brightness(self) -> float:
        """Get the current brightness setting."""
        if hasattr(self, 'settings_ui') and self.settings_ui:
            # Prefer config service
            return self.settings_ui.config.get('brightness', 1.0)
        return 1.0  # Default brightness
    
    def add_notification(self, message: str, color: tuple = (255, 255, 255)):
        """Add a notification message to display."""
        current_time = self.clock.now_ms()
        self.notifications.append({
            'message': message,
            'color': color,
            'start_time': current_time,
            'duration': self.notification_duration
        })
    
    def update_notifications(self):
        """Update notification timers and remove expired ones."""
        current_time = self.clock.now_ms()
        self.notifications = [
            notif for notif in self.notifications 
            if (current_time - notif['start_time']) < notif['duration']
        ]
    
    def draw_notifications(self):
        """Draw all active notifications."""
        if not self.notifications:
            return
        
        notification_font = pygame.font.SysFont(None, 24)
        y_offset = 100
        
        for i, notif in enumerate(self.notifications):
            # Calculate alpha based on time remaining
            current_time = self.clock.now_ms()
            time_elapsed = current_time - notif['start_time']
            time_remaining = notif['duration'] - time_elapsed
            
            # Fade out in last 500ms
            if time_remaining < 500:
                alpha = int(255 * (time_remaining / 500))
            else:
                alpha = 255
            
            # Create notification surface
            text_surface = notification_font.render(notif['message'], True, notif['color'])
            text_rect = text_surface.get_rect()
            
            # Create background
            padding = 20
            bg_rect = pygame.Rect(
                self.width // 2 - text_rect.width // 2 - padding,
                y_offset + i * 40,
                text_rect.width + padding * 2,
                text_rect.height + padding * 2
            )
            
            # Draw background with alpha
            bg_surface = pygame.Surface((bg_rect.width, bg_rect.height), pygame.SRCALPHA)
            bg_surface.fill((0, 0, 0, min(180, alpha)))
            self.screen.blit(bg_surface, bg_rect)
            
            # Draw border (without alpha - pygame.draw.rect doesn't support alpha)
            pygame.draw.rect(self.screen, (100, 100, 100), bg_rect, 2, border_radius=8)
            
            # Draw text
            text_rect.center = bg_rect.center
            self.screen.blit(text_surface, text_rect)
    
    def apply_brightness_to_surface(self, surface: pygame.Surface) -> pygame.Surface:
        """Apply brightness adjustment to a surface."""
        brightness = self.get_brightness()
        if brightness == 1.0:
            return surface  # No adjustment needed
        
        # Create a copy of the surface to avoid modifying the original
        adjusted_surface = surface.copy()
        
        # Create a brightness overlay
        brightness_overlay = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # Calculate the darkness level (1.0 = no change, 0.0 = completely black)
        darkness = 1.0 - brightness
        alpha = int(255 * darkness)
        
        # Fill with black with appropriate alpha for darkening
        brightness_overlay.fill((0, 0, 0, alpha))
        
        # Apply the overlay using BLEND_MULT for darkening effect
        adjusted_surface.blit(brightness_overlay, (0, 0), special_flags=pygame.BLEND_MULT)
        
        return adjusted_surface
    
    def toggle_fullscreen(self):
        """Toggle fullscreen mode."""
        try:
            # Get current display info
            info = pygame.display.Info()
            
            # Toggle fullscreen flag
            if pygame.display.get_surface().get_flags() & pygame.FULLSCREEN:
                # Currently fullscreen, switch to windowed
                self.screen = pygame.display.set_mode((self.width, self.height))
                print("🖥️ Switched to windowed mode")
            else:
                # Currently windowed, switch to fullscreen
                # Use native resolution for Retina displays
                if resolution_enhancer.is_retina:
                    fullscreen_width = 3456
                    fullscreen_height = 2234
                    print(f"🍎 Switching to native Retina fullscreen: {fullscreen_width} x {fullscreen_height}")
                else:
                    fullscreen_width = info.current_w
                    fullscreen_height = info.current_h
                    print(f"🖥️ Switching to fullscreen: {fullscreen_width} x {fullscreen_height}")
                
                self.screen = pygame.display.set_mode((fullscreen_width, fullscreen_height), pygame.FULLSCREEN)
                print("🖥️ Switched to fullscreen mode")
            
            # Update internal width/height from the new display surface
            try:
                self.width = self.screen.get_width()
                self.height = self.screen.get_height()
            except Exception:
                pass

            # Update screen references in other systems
            if hasattr(self, 'settings_ui') and self.settings_ui:
                self.settings_ui.update_screen(self.screen)
            if hasattr(self, 'menu_system') and self.menu_system:
                self.menu_system.screen = self.screen
                # Refresh menu system dimensions
                try:
                    self.menu_system.width = self.screen.get_width()
                    self.menu_system.height = self.screen.get_height()
                except Exception:
                    pass
            if hasattr(self, 'puzzle_engine') and self.puzzle_engine:
                self.puzzle_engine.screen = self.screen
            if hasattr(self, 'puzzle_renderer') and self.puzzle_renderer:
                self.puzzle_renderer.screen = self.screen
            
        except Exception as e:
            print(f"❌ Error toggling fullscreen: {e}")
    
    def set_fullscreen(self, enabled: bool):
        """Set fullscreen to a specific state."""
        try:
            is_full = pygame.display.get_surface().get_flags() & pygame.FULLSCREEN
            if bool(is_full) == bool(enabled):
                return
            # If enabling fullscreen, disable borderless
            if enabled and hasattr(self, 'config'):
                self.config.update({'borderless': False})
            self.toggle_fullscreen()
            # Persist setting
            try:
                if hasattr(self, 'config') and self.config:
                    self.config.update({'fullscreen': bool(enabled), 'native_fullscreen': False})
            except Exception:
                pass
        except Exception as e:
            print(f"❌ Error setting fullscreen: {e}")

    def set_native_fullscreen(self, enabled: bool):
        """Force native display resolution fullscreen (best clarity on macOS)."""
        try:
            if enabled:
                # Turn off borderless and normal fullscreen flags in config
                if hasattr(self, 'config') and self.config:
                    self.config.update({'borderless': False, 'fullscreen': True, 'native_fullscreen': True})
                info = pygame.display.Info()
                target_w, target_h = info.current_w, info.current_h
                # Retina specific upscale path
                if hasattr(resolution_enhancer, 'is_retina') and resolution_enhancer.is_retina:
                    target_w, target_h = 3456, 2234
                self.screen = pygame.display.set_mode((target_w, target_h), pygame.FULLSCREEN)
            else:
                # Disable native fullscreen -> fall back to windowed
                if hasattr(self, 'config') and self.config:
                    self.config.update({'native_fullscreen': False, 'fullscreen': False})
                self.screen = pygame.display.set_mode((self.width, self.height))
            # Update internals and references
            self.width = self.screen.get_width()
            self.height = self.screen.get_height()
            if hasattr(self, 'settings_ui') and self.settings_ui:
                self.settings_ui.update_screen(self.screen)
            if hasattr(self, 'menu_system') and self.menu_system:
                self.menu_system.screen = self.screen
                self.menu_system.width = self.width
                self.menu_system.height = self.height
            if hasattr(self, 'puzzle_engine') and self.puzzle_engine:
                self.puzzle_engine.screen = self.screen
            if hasattr(self, 'puzzle_renderer') and self.puzzle_renderer:
                self.puzzle_renderer.screen = self.screen
        except Exception as e:
            print(f"❌ Error setting native fullscreen: {e}")

    def set_borderless(self, enabled: bool):
        """Set borderless windowed mode (mutually exclusive with fullscreen)."""
        try:
            # Update config
            if hasattr(self, 'config') and self.config:
                self.config.update({'borderless': bool(enabled)})
                if enabled:
                    self.config.update({'fullscreen': False})
            # Recreate display flags
            flags = pygame.RESIZABLE | pygame.NOFRAME if enabled else 0
            # Fit to current display when enabling borderless
            target_w, target_h = self.width, self.height
            if enabled:
                info = pygame.display.Info()
                target_w, target_h = info.current_w, info.current_h
            self.screen = pygame.display.set_mode((int(target_w), int(target_h)), flags)
            # Update internals
            self.width = self.screen.get_width()
            self.height = self.screen.get_height()
            if hasattr(self, 'menu_system') and self.menu_system:
                self.menu_system.screen = self.screen
                self.menu_system.width = self.width
                self.menu_system.height = self.height
            if hasattr(self, 'settings_ui') and self.settings_ui:
                self.settings_ui.update_screen(self.screen)
        except Exception as e:
            print(f"❌ Error setting borderless: {e}")
    
    def get_mouse_sensitivity(self) -> float:
        """Get the current mouse sensitivity setting."""
        if hasattr(self, 'settings_ui') and self.settings_ui:
            return self.settings_ui.config.get('sensitivity', 1.0)
        return 1.0  # Default sensitivity
    
    def toggle_vsync(self):
        """Working V-Sync toggle that actually changes the display mode."""
        try:
            # Get current V-Sync state (fallback to True when settings are absent)
            current_vsync = (self.settings_ui.config.get('vsync', True) if getattr(self, 'settings_ui', None) else True)
            
            # Toggle the setting
            new_vsync = not current_vsync
            if getattr(self, 'settings_ui', None):
                self.settings_ui.config.update({'vsync': new_vsync})
            
            # Actually recreate the display with proper flags
            if new_vsync:
                # Enable V-Sync
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE | pygame.DOUBLEBUF)
                print("🔄 V-Sync ENABLED - Display recreated with V-Sync")
            else:
                # Disable V-Sync  
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE)
                print("🔄 V-Sync DISABLED - Display recreated without V-Sync")
            
            # Update all screen references
            self._update_screen_references()
            
        except Exception as e:
            print(f"❌ Error toggling V-Sync: {e}")

    def set_vsync(self, enabled: bool):
        """Set V-Sync to a specific state by recreating display appropriately."""
        try:
            current_vsync = (self.settings_ui.config.get('vsync', True) if getattr(self, 'settings_ui', None) else self.config.get('vsync', True))
            if current_vsync == enabled:
                return
            # Update stored setting if settings_ui exists, else update config directly
            if getattr(self, 'settings_ui', None):
                self.settings_ui.config.update({'vsync': enabled})
            else:
                self.config.update({'vsync': enabled})
            # Recreate display to apply
            if enabled:
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE | pygame.DOUBLEBUF)
            else:
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.HWSURFACE)
            self._update_screen_references()
            print(f"🔄 V-Sync set to {'ENABLED' if enabled else 'DISABLED'}")
        except Exception as e:
            print(f"❌ Error setting V-Sync: {e}")

    def set_show_fps(self, enabled: bool):
        try:
            if hasattr(self, 'config') and self.config:
                self.config.update({'show_fps': bool(enabled)})
        except Exception:
            pass

    def set_ui_scale(self, scale: float):
        """Apply a uniform UI scale and persist it."""
        try:
            scale = max(0.8, min(1.5, float(scale)))
            if hasattr(self, 'config') and self.config:
                self.config.update({'ui_scale': scale})
            # Apply to menu
            if hasattr(self, 'menu_system') and self.menu_system:
                self.menu_system.ui_scale = scale
            # Optionally adjust puzzle block size to match visual scale
            if hasattr(self, 'puzzle_engine') and self.puzzle_engine and hasattr(self.puzzle_engine, 'asset_loader'):
                try:
                    base_width = self.puzzle_engine.block_width
                    new_width = int(round(base_width * scale))
                    new_width = max(32, min(96, new_width))
                    new_height = int(new_width * 1.25)  # Maintain 4:5 aspect ratio
                    self.puzzle_engine.asset_loader.update_block_size(new_width, new_height)
                    # Recompute backgrounds and offsets
                    self.puzzle_engine.block_width = new_width
                    self.puzzle_engine.block_height = new_height
                    if hasattr(self, 'puzzle_renderer') and self.puzzle_renderer:
                        self.puzzle_renderer.block_width = new_width
                        self.puzzle_renderer.block_height = new_height
                        self.puzzle_renderer.update_coordinate_offsets()
                except Exception:
                    pass
        except Exception:
            pass

    def _get_display_recommendation(self):
        """Return a recommendation dict: {text, action_key} based on current screen/mode."""
        try:
            info = pygame.display.Info()
            is_full = bool(pygame.display.get_surface().get_flags() & pygame.FULLSCREEN)
            borderless = bool(self.config.get('borderless', False))
            current_screen = getattr(self, 'current_screen', 'main_menu')
            # Recommend borderless in menus; native fullscreen in game
            if current_screen == 'main_menu':
                if not borderless and not is_full:
                    return { 'text': 'Recommended: Borderless Windowed for crisp UI on your display', 'action_key': 'borderless_on' }
            if current_screen == 'game':
                # If fullscreen is toggling odd sizes, recommend borderless or native fullscreen
                if not is_full and not borderless:
                    return { 'text': 'Recommended: Native Fullscreen or Borderless for smooth gameplay', 'action_key': 'native_full_or_borderless' }
                if is_full and (info.current_w < self.width or info.current_h < self.height):
                    return { 'text': 'Recommended: Native Fullscreen to match display resolution', 'action_key': 'native_full' }
            return None
        except Exception:
            return None

    def _apply_display_recommendation(self, action_key: str):
        try:
            if action_key == 'borderless_on':
                self.set_borderless(True)
            elif action_key == 'native_full':
                # Force native fullscreen size
                info = pygame.display.Info()
                self.width, self.height = info.current_w, info.current_h
                self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
                # Update and persist
                self.config.update({'fullscreen': True, 'borderless': False})
                self._update_screen_references()
            elif action_key == 'native_full_or_borderless':
                # Prefer borderless first (macOS)
                self.set_borderless(True)
        except Exception:
            pass

    def _update_screen_references(self):
        """Update screen references in all systems."""
        systems = ['settings_ui', 'menu_system', 'puzzle_engine', 'puzzle_renderer']
        for system_name in systems:
            if hasattr(self, system_name) and getattr(self, system_name):
                system = getattr(self, system_name)
                if hasattr(system, 'screen'):
                    system.screen = self.screen
                    print(f"✅ Updated {system_name} screen reference")
    
    def check_vsync_status(self) -> bool:
        """Check if V-Sync is currently enabled."""
        try:
            # Check environment variable
            vsync_env = os.environ.get('SDL_VIDEO_VSYNC', '0')
            return vsync_env == '1'
        except:
            return False
    
    def set_particle_effects(self, enabled: bool):
        """Enable or disable particle effects."""
        try:
            # Set particle effects in the puzzle renderer if available
            if hasattr(self, 'puzzle_renderer') and self.puzzle_renderer:
                if hasattr(self.puzzle_renderer, 'animation_renderer'):
                    # Store the setting for the renderer to use
                    self.puzzle_renderer.animation_renderer.particle_effects_enabled = enabled
                    print(f"✨ Particle effects {'enabled' if enabled else 'disabled'}")
        except Exception as e:
            print(f"❌ Error setting particle effects: {e}")
    
    def handle_mp3_player_click(self, pos):
        """Handle clicks on the custom MP3 player buttons."""
        if not hasattr(self, 'mp3_player_buttons') or not self.mp3_player_buttons:
            return False
        
        # Check if any button was clicked
        for btn_name, btn_rect in self.mp3_player_buttons.items():
            if btn_rect.collidepoint(pos):
                # Play click sound if available
                if hasattr(self.audio, 'sounds') and 'click' in self.audio.sounds:
                    self.audio.sounds['click'].play()
                
                # Handle button actions using the audio system's MP3 player
                if hasattr(self.audio, 'mp3_player'):
                    if btn_name == 'play':
                        self.audio.mp3_player.pause_song()  # Toggle play/pause
                    elif btn_name == 'prev':
                        self.audio.mp3_player.prev_song()
                    elif btn_name == 'next':
                        self.audio.mp3_player.next_song()
                        
                return True  # Click was handled
                
        return False  # Click was not on any MP3 player button
    
    def show_game_over_screen(self):
        """Display a dramatic game over screen."""
        # Create a semi-transparent black overlay
        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))  # Black with 180/255 alpha
        self.screen.blit(overlay, (0, 0))
        
        # Create a dramatic "GAME OVER" text with red glow effect
        game_over_font = pygame.font.SysFont(None, 72)
        game_over_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
        game_over_rect = game_over_text.get_rect(center=(self.width // 2, self.height // 2))
        
        # Draw glow effect
        glow_surface = pygame.Surface((game_over_text.get_width() + 20, game_over_text.get_height() + 20), pygame.SRCALPHA)
        for i in range(10):
            alpha = 100 - (i * 10)
            glow_text = game_over_font.render("GAME OVER", True, (255, 0, 0))
            glow_rect = glow_text.get_rect(center=(glow_surface.get_width() // 2, glow_surface.get_height() // 2))
            glow_surface.blit(glow_text, glow_rect)
        self.screen.blit(glow_surface, (game_over_rect.x - 10, game_over_rect.y - 10))
        
        # Draw the main text
        self.screen.blit(game_over_text, game_over_rect)
        
        # Draw instruction text
        instruction_font = pygame.font.SysFont(None, 36)
        instruction_text = instruction_font.render("Press ESC to return to main menu", True, self.WHITE)
        instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height // 2 + 60))
        self.screen.blit(instruction_text, instruction_rect)
        
        # Update the display
        pygame.display.flip()
        
        # Wait for 2 seconds before returning to main menu
        pygame.time.wait(2000)
        
        # Return to main menu
        self.set_screen("main_menu")

    def run(self):
        """Main loop for the application."""
        # Set up the frame limiter clock (separate from unified time source)
        frame_clock = pygame.time.Clock()
        
        # Create loading screen
        loading_screen = LoadingScreen(self.screen, self.asset_path)
        
        # Define loading tasks
        loading_tasks = [
            ("Loading Font System", self._initialize_font),
            ("Initializing Audio System", self._initialize_audio_system),
            ("Loading Background Images", self._load_background_images),
            ("Initializing Menu System", self._initialize_menu_system),
            ("Initializing Settings UI", self._initialize_settings_ui),
            ("Initializing Test Mode", self._initialize_test_mode),
            ("Initializing Screen Manager", self._initialize_screen_manager),
            ("Initializing Story System", self._initialize_story_system),
            ("Initializing Puzzle Engine", self._initialize_puzzle_engine),
            ("Initializing Puzzle Renderer", self._initialize_puzzle_renderer),
            ("Finalizing Setup", self._complete_initialization)
        ]
        
        # Start loading process
        loading_screen.start_loading(loading_tasks, on_complete=lambda: None)
        
        try:
            # Main game loop
            while self.game_running:
                # Calculate delta time
                dt = frame_clock.tick(60) / 1000.0  # Convert to seconds
                
                # Get all events
                events = pygame.event.get()
                
                # Process window close events
                for event in events:
                    if event.type == pygame.QUIT:
                        # Save UI positions before closing
                        self.game_running = False
                    elif event.type == pygame.VIDEORESIZE:
                        # Update resolution if the window is resized
                        self.change_resolution(event.w, event.h)
                    # Handle mouse clicks for MP3 player buttons
                    elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:  # Left click
                        # Check if click was on MP3 player buttons
                        if hasattr(self, 'mp3_player_buttons') and self.mp3_player_buttons:
                            if self.handle_mp3_player_click(event.pos):
                                # Click was handled by MP3 player, no need to process it further
                                continue
                    # Global hotkey to open Settings overlay
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_F1, pygame.K_F10):
                            if hasattr(self, 'settings_ui') and self.settings_ui:
                                self.settings_ui.open()
                                # Skip further menu processing this frame
                                continue
                        # Toggle input tuner overlay
                        if event.key == pygame.K_F9:
                            if self.input_tuner is None:
                                # Late create if puzzle engine just became available
                                try:
                                    ih = getattr(self, 'puzzle_engine', None)
                                    ih = getattr(ih, 'input_handler', None)
                                    self.input_tuner = InputTunerOverlay(self.clock, self.config, ih, self.font, logger=print)
                                except Exception:
                                    self.input_tuner = None
                            if self.input_tuner:
                                self.input_tuner.toggle()
                    elif event.type == pygame.VIDEORESIZE:
                        # Keep windowed mode resizable and persist size
                        self.width, self.height = max(800, event.w), max(600, event.h)
                        self.screen = pygame.display.set_mode((self.width, self.height), pygame.RESIZABLE)
                        # Update systems
                        if hasattr(self, 'menu_system') and self.menu_system:
                            self.menu_system.screen = self.screen
                            self.menu_system.width = self.width
                            self.menu_system.height = self.height
                        if hasattr(self, 'settings_ui') and self.settings_ui:
                            self.settings_ui.update_screen(self.screen)
                    # Prevent escape from closing the game in main menu, except when settings overlay is open
                    elif (
                        event.type == pygame.KEYDOWN
                        and event.key == pygame.K_ESCAPE
                        and self.current_screen == "main_menu"
                        and not (hasattr(self, 'settings_ui') and self.settings_ui and self.settings_ui.is_open())
                    ):
                        continue
                    
                    # Let the audio system handle any audio-related events
                    if hasattr(self, 'audio') and self.audio:
                        try:
                            self.audio.handle_audio_events(event)
                        except Exception as e:
                            # Silently ignore audio event handling errors
                            pass
                
                # Process events and update/draw the current screen
                if self.current_screen == "main_menu":
                    # Filter out escape key events in main menu BEFORE processing any events
                    filtered_events = []
                    for event in events:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            # Allow ESC to pass through if settings overlay is open
                            if hasattr(self, 'settings_ui') and self.settings_ui and self.settings_ui.is_open():
                                filtered_events.append(event)
                            else:
                                continue
                        filtered_events.append(event)
                    events = filtered_events
                    
                    # Process menu events with filtered event list
                    if hasattr(self, 'menu_system') and self.menu_system:
                        # If settings overlay is open, let it consume inputs first and block menu
                        if hasattr(self, 'settings_ui') and self.settings_ui and self.settings_ui.is_open():
                            result = self.settings_ui.handle_events(events)
                            # While open, do not process underlying menu clicks
                            menu_action = None
                        else:
                            menu_action = self.menu_system.process_main_menu_events(events)
                        # Let tuner overlay consume events when visible
                        # DISABLED: Input tuner completely disabled
                        pass
                        
                        # Handle menu actions
                        if menu_action == "quickplay":
                            self.start_quickplay()
                        elif menu_action == "story":
                            self.set_screen("story")
                        elif menu_action == "test":
                            self.set_screen("test")
                        elif menu_action == "smithing":
                            self.set_screen("smithing")
                        elif menu_action == "inventory":
                            self.set_screen("inventory")
                        elif menu_action == "quit":
                            self.game_running = False
                        elif menu_action == "settings":
                            if hasattr(self, 'settings_ui') and self.settings_ui:
                                self.settings_ui.open()
                        
                        # Draw the main menu
                        self.main_menu_buttons = self.menu_system.draw_main_menu(
                            on_start_action=self.start_quickplay,
                            on_story_action=lambda: self.set_screen("story"),
                            on_test_action=lambda: self.set_screen("test"),
                            version=self.version
                        )
                        # Draw settings overlay (on top of menu) AFTER MP3 so it isn't obscured
                        if hasattr(self, 'settings_ui') and self.settings_ui and self.settings_ui.is_open():
                            # Temporarily skip drawing MP3 while settings are open to avoid overlap
                            # The global MP3 draw occurs later; we will guard it there too
                            self.settings_ui.draw(self.screen)
                    else:
                        # Fallback if menu system is not available
                        self.screen.fill(self.BLACK)
                        error_text = self.font.render("Menu system not available", True, self.WHITE)
                        error_rect = error_text.get_rect(center=(self.width // 2, self.height // 2))
                        self.screen.blit(error_text, error_rect)
                        
                        # Handle escape key to quit
                        for event in events:
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                                self.game_running = False
                    

                
                elif self.current_screen == "test":
                    # Handle settings UI events first if open
                    if hasattr(self, 'settings_ui') and self.settings_ui and self.settings_ui.is_open():
                        settings_result = self.settings_ui.handle_events(events)
                        if settings_result in ['apply', 'cancel', 'close']:
                            # Settings closed, continue with normal event processing
                            pass
                        else:
                            # Settings consumed the events, skip further processing
                            continue
                    
                    if hasattr(self, 'test_mode') and self.test_mode:
                        # Process test mode events
                        test_action = self.test_mode.process_events(events)
                        
                        # Handle test mode actions
                        if test_action == "back_to_menu":
                            self.set_screen("main_menu")
                        
                        # Update the test mode
                        test_update_result = self.test_mode.update()
                        
                        # Handle game over state
                        if test_update_result == "game_over":
                            self.show_game_over_screen()
                            continue
                        
                        # Draw the test mode screen
                        self.test_mode.draw()
                        
                        # Draw settings overlay if open
                        if hasattr(self, 'settings_ui') and self.settings_ui and self.settings_ui.is_open():
                            self.settings_ui.draw(self.screen)

                    else:
                        # Fallback if test mode is not available
                        self.screen.fill(self.BLACK)
                        error_text = self.font.render("Test mode not available", True, self.WHITE)
                        error_rect = error_text.get_rect(center=(self.width // 2, self.height // 2))
                        self.screen.blit(error_text, error_rect)
                        
                        # Handle escape key to go back
                        for event in events:
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                                self.set_screen("main_menu")
                
                elif self.current_screen == "story":
                    # Handle settings UI events first if open
                    if hasattr(self, 'settings_ui') and self.settings_ui and self.settings_ui.is_open():
                        settings_result = self.settings_ui.handle_events(events)
                        if settings_result in ['apply', 'cancel', 'close']:
                            # Settings closed, continue with normal event processing
                            pass
                        else:
                            # Settings consumed the events, skip further processing
                            continue
                    
                    # Process story menu events
                    if hasattr(self, 'menu_system') and self.menu_system:
                        story_action = self.menu_system.process_story_menu_events(events)
                        
                        # Handle story menu actions
                        if story_action == "back" or story_action == "back_to_main":
                            self.set_screen("main_menu")
                        elif isinstance(story_action, str) and (story_action.startswith("story:") or story_action == "saga1"):
                            # Extract story ID from action string
                            if story_action.startswith("story:"):
                                story_id = int(story_action.split(":")[1])
                            else:
                                # Handle direct action like "saga1"
                                story_id = 1  # Default to saga 1
                            print(f"Selected story {story_id}")
                            # Load and display the selected story
                            if hasattr(self, 'story_system') and self.story_system:
                                self.current_story = self.story_system.load_story(story_id)
                            else:
                                self.load_story(story_id)
                            self.set_screen("story_content")
                        
                        # Draw the story menu
                        self.menu_system.draw_story_menu(
                            on_back_action=lambda: self.set_screen("main_menu")
                        )
                        
                        # Draw settings overlay if open
                        if hasattr(self, 'settings_ui') and self.settings_ui and self.settings_ui.is_open():
                            self.settings_ui.draw(self.screen)
                    else:
                        # Fallback if menu system is not available
                        self.screen.fill(self.BLACK)
                        error_text = self.font.render("Story menu not available", True, self.WHITE)
                        error_rect = error_text.get_rect(center=(self.width // 2, self.height // 2))
                        self.screen.blit(error_text, error_rect)
                        
                        # Handle escape key to go back
                        for event in events:
                            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                                self.set_screen("main_menu")
                    

                
                elif self.current_screen == "story_content":
                    # Use extracted story system if available
                    if hasattr(self, 'story_system') and self.story_system:
                        # Handle story events using the story system
                        story_action, new_scroll_position = self.story_system.handle_story_events(events, self.story_scroll_position)
                        self.story_scroll_position = new_scroll_position
                        
                        # Handle story actions
                        if story_action == "back_to_story":
                            self.set_screen("story")
                        
                        # Display the story content using the story system
                        self.story_scroll_position = self.story_system.display_story_content(self.current_story, self.story_scroll_position)
                    else:
                        # Legacy story content handling
                        for event in events:
                            if event.type == pygame.KEYDOWN:
                                if event.key == pygame.K_ESCAPE:
                                    self.set_screen("story")
                                elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                                    # Scroll down
                                    self.story_scroll_position += 20
                                elif event.key == pygame.K_UP or event.key == pygame.K_w:
                                    # Scroll up (with limit to prevent scrolling above the top)
                                    self.story_scroll_position = max(0, self.story_scroll_position - 20)
                            elif event.type == pygame.MOUSEBUTTONDOWN:
                                if event.button == 4:  # Mouse wheel up
                                    self.story_scroll_position = max(0, self.story_scroll_position - 40)
                                elif event.button == 5:  # Mouse wheel down
                                    self.story_scroll_position += 40
                        
                        # Display the story content using legacy method
                        self.display_story_content()
                    

                
                elif self.current_screen == "settings":
                    # Settings screen removed – redirect to main menu
                    self.set_screen("main_menu")
                

                
                elif self.current_screen == "smithing":
                    # Simple placeholder smithing scene
                    for event in events:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            self.set_screen("main_menu")

                    # Draw placeholder screen
                    self.screen.fill((20, 20, 20))
                    title_font = pygame.font.SysFont(None, 64)
                    subtitle_font = pygame.font.SysFont(None, 32)
                    title_text = title_font.render("Smithing", True, self.WHITE)
                    subtitle_text = subtitle_font.render("Coming Soon", True, self.LIGHT_GRAY)
                    instruction_text = subtitle_font.render("Press ESC to return to main menu", True, self.LIGHT_GRAY)
                    title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 40))
                    subtitle_rect = subtitle_text.get_rect(center=(self.width // 2, self.height // 2 + 10))
                    instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height // 2 + 60))
                    self.screen.blit(title_text, title_rect)
                    self.screen.blit(subtitle_text, subtitle_rect)
                    self.screen.blit(instruction_text, instruction_rect)

                elif self.current_screen == "inventory":
                    # Simple placeholder inventory scene
                    for event in events:
                        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                            self.set_screen("main_menu")
                        elif event.type == pygame.MOUSEWHEEL:
                            # Scroll wheel for inventory
                            if not hasattr(self, 'inventory_scroll'):
                                self.inventory_scroll = 0
                            self.inventory_scroll = max(0, self.inventory_scroll - event.y * 30)
                        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            # Left-click to equip a clicked item
                            if hasattr(self, 'inventory_card_entries'):
                                mx, my = event.pos
                                # Top-bar button: populate all curated items
                                if hasattr(self, 'inventory_add_all_btn') and self.inventory_add_all_btn and self.inventory_add_all_btn.collidepoint(mx, my):
                                    try:
                                        from modules.items_module.catalog import CURATED_WEAPONS
                                        curated_names = [w['name'] for w in CURATED_WEAPONS][:60]
                                        if hasattr(self, 'test_mode') and self.test_mode and hasattr(self.test_mode, 'player_items'):
                                            self.test_mode.player_items.set_owned_weapons(curated_names)
                                            if hasattr(self.test_mode, 'save_equipment'):
                                                self.test_mode.save_equipment()
                                            if hasattr(self, 'audio') and self.audio:
                                                self.audio.play_sound('click')
                                            # Add notification
                                            self.add_notification(f"🗡️ Added {len(curated_names)} weapons to inventory", (120, 200, 255))
                                    except Exception:
                                        pass
                                for rect, item_name in self.inventory_card_entries:
                                    if rect.collidepoint(mx, my):
                                        # Rate limiting: prevent rapid clicking
                                        current_time = self.clock.now_ms()
                                        if hasattr(self, '_last_equip_time') and current_time - self._last_equip_time < 200:  # 200ms cooldown
                                            continue
                                        self._last_equip_time = current_time
                                        
                                        try:
                                            from modules.items_module.item_system import create_weapon_by_name
                                            if hasattr(self, 'test_mode') and self.test_mode and hasattr(self.test_mode, 'player_items'):
                                                weapon = create_weapon_by_name(item_name)
                                                if weapon:
                                                    self.test_mode.player_items.equip_weapon(weapon)
                                                    # persist immediately
                                                    if hasattr(self.test_mode, 'save_equipment'):
                                                        self.test_mode.save_equipment()
                                                    if hasattr(self, 'audio') and self.audio:
                                                        self.audio.play_sound('click')
                                        except Exception as e:
                                            # Log the error but don't crash
                                            print(f"Error equipping weapon {item_name}: {e}")
                                            pass

                    self.screen.fill((30, 20, 20))
                    title_font = pygame.font.SysFont(None, 64)
                    subtitle_font = pygame.font.SysFont(None, 28)
                    title_text = title_font.render("Inventory", True, self.WHITE)
                    # Show both player and enemy current weapons
                    p_name = None
                    e_name = None
                    try:
                        if hasattr(self, 'test_mode') and self.test_mode:
                            p_weapon = getattr(self.test_mode.player_items, 'get_equipped_weapon', lambda: None)()
                            e_weapon = getattr(self.test_mode.enemy_items, 'get_equipped_weapon', lambda: None)()
                            p_name = p_weapon.name if p_weapon else None
                            e_name = e_weapon.name if e_weapon else None
                    except Exception:
                        pass
                    eq_text = subtitle_font.render(f"Player Equipped: {p_name or 'None'}", True, self.LIGHT_GRAY)
                    eq2_text = subtitle_font.render(f"Enemy Equipped: {e_name or 'None'}", True, self.LIGHT_GRAY)
                    instruction_text = subtitle_font.render("Mouse wheel to scroll • ESC to return", True, self.LIGHT_GRAY)
                    title_rect = title_text.get_rect(center=(self.width // 2, self.height // 2 - 40))
                    eq_rect = eq_text.get_rect(center=(self.width // 2, self.height // 2 + 10))
                    eq2_rect = eq2_text.get_rect(center=(self.width // 2, self.height // 2 + 40))
                    instruction_rect = instruction_text.get_rect(center=(self.width // 2, self.height // 2 + 90))
                    self.screen.blit(title_text, title_rect)
                    self.screen.blit(eq_text, eq_rect)
                    self.screen.blit(eq2_text, eq2_rect)
                    self.screen.blit(instruction_text, instruction_rect)

                    # Reserve top bar space for future sorting/filters
                    top_bar_rect = pygame.Rect(60, 120, self.width - 120, 60)
                    pygame.draw.rect(self.screen, (45, 35, 35), top_bar_rect, border_radius=8)
                    pygame.draw.rect(self.screen, (80, 70, 70), top_bar_rect, 2, border_radius=8)
                    sort_hint = subtitle_font.render("Sorting/Filters (coming soon)", True, self.LIGHT_GRAY)
                    self.screen.blit(sort_hint, sort_hint.get_rect(midleft=(top_bar_rect.x + 16, top_bar_rect.centery)))

                    # Scrollable area for items list
                    list_top = top_bar_rect.bottom + 20
                    list_margin = 60
                    list_rect = pygame.Rect(list_margin, list_top, self.width - 2 * list_margin, self.height - list_top - 120)
                    pygame.draw.rect(self.screen, (40, 30, 30), list_rect, border_radius=10)
                    pygame.draw.rect(self.screen, (85, 75, 75), list_rect, 2, border_radius=10)

                    # Add an action button in top bar: Add All Curated
                    btn_w, btn_h = 180, 32
                    add_btn_rect = pygame.Rect(top_bar_rect.right - btn_w - 16, top_bar_rect.centery - btn_h // 2, btn_w, btn_h)
                    pygame.draw.rect(self.screen, (70, 60, 60), add_btn_rect, border_radius=8)
                    pygame.draw.rect(self.screen, (130, 120, 120), add_btn_rect, 2, border_radius=8)
                    btn_label = pygame.font.SysFont(None, 22).render("Add All Curated", True, self.WHITE)
                    self.screen.blit(btn_label, btn_label.get_rect(center=add_btn_rect.center))
                    # Store for click detection
                    self.inventory_add_all_btn = add_btn_rect

                    # Fetch owned items (player side for UI); fallback to curated list if empty
                    owned = []
                    if hasattr(self, 'test_mode') and self.test_mode and hasattr(self.test_mode, 'player_items'):
                        try:
                            owned = self.test_mode.player_items.get_owned_weapons()
                        except Exception:
                            owned = []
                    if not owned:
                        try:
                            from modules.items_module.catalog import CURATED_WEAPONS
                            owned = [w['name'] for w in CURATED_WEAPONS][:60]
                        except Exception:
                            owned = []

                    # Build name->slug map for displaying and asset lookup
                    name_to_slug = {}
                    try:
                        from modules.items_module.catalog import CURATED_WEAPONS
                        name_to_slug = {w['name']: w['slug'] for w in CURATED_WEAPONS}
                    except Exception:
                        name_to_slug = {}

                    # Ensure image cache exists
                    if not hasattr(self, 'inventory_images'):
                        self.inventory_images = {}

                    # Layout item cards in a grid inside the scrollable area
                    cols = 4
                    card_w = (list_rect.width - (cols + 1) * 16) // cols
                    # Expanded card height to accommodate full 6x12 preview grid
                    card_h = 240
                    spacing = 16
                    y_offset = -(getattr(self, 'inventory_scroll', 0))
                    start_x = list_rect.x + spacing
                    start_y = list_rect.y + spacing + y_offset
                    card_font = pygame.font.SysFont(None, 24)

                    # Prepare entries list for clicking
                    self.inventory_card_entries = []

                    # Simple masking: only draw items that intersect list_rect
                    for idx, item_name in enumerate(owned):
                        row = idx // cols
                        col = idx % cols
                        x = start_x + col * (card_w + spacing)
                        y = start_y + row * (card_h + spacing)
                        card = pygame.Rect(x, y, card_w, card_h)
                        if card.bottom < list_rect.top or card.top > list_rect.bottom:
                            continue
                        self.inventory_card_entries.append((card.copy(), item_name))
                        # Background
                        pygame.draw.rect(self.screen, (55, 45, 45), card, border_radius=10)
                        pygame.draw.rect(self.screen, (100, 90, 90), card, 2, border_radius=10)
                        # Image area
                        img_rect = pygame.Rect(card.x + 10, card.y + 10, 80, 80)
                        # Try to load thumbnail once and cache
                        thumb = self.inventory_images.get(item_name, None)
                        if item_name not in self.inventory_images:
                            # Build candidate filenames from weapon name
                            base_slug = name_to_slug.get(item_name, item_name.lower().replace(' ', '_'))
                            exts = [".png", ".jpg", ".jpeg"]
                            subdirs = ["", "weapons/", "items/", "weapon_images/", "swords/"]
                            candidates = []
                            for sd in subdirs:
                                for ext in exts:
                                    candidates.append(f"{sd}{base_slug}{ext}")
                            # Special-case known alt name
                            if item_name == 'Rusted Sword':
                                for sd in subdirs:
                                    candidates.insert(0, f"{sd}rusty_sword.png")
                            loaded = None
                            for fname in candidates:
                                try:
                                    path = os.path.join(ASSET_PATH, fname)
                                    if os.path.exists(path):
                                        loaded = pygame.image.load(path)
                                        break
                                except Exception:
                                    loaded = None
                            if loaded:
                                try:
                                    thumb = pygame.transform.scale(loaded, (img_rect.width, img_rect.height))
                                except Exception:
                                    thumb = None
                            self.inventory_images[item_name] = thumb

                        if thumb is not None:
                            self.screen.blit(thumb, img_rect)
                            pygame.draw.rect(self.screen, (100, 90, 90), img_rect, 1, border_radius=6)
                        else:
                            # Placeholder box if no image
                            pygame.draw.rect(self.screen, (35, 25, 25), img_rect, border_radius=6)
                            pygame.draw.rect(self.screen, (100, 90, 90), img_rect, 1, border_radius=6)
                        # Title
                        name_surf = card_font.render(item_name, True, self.WHITE)
                        self.screen.blit(name_surf, (img_rect.right + 12, img_rect.y + 8))
                        # Slug under title (helps with asset filenames)
                        slug_here = name_to_slug.get(item_name, item_name.lower().replace(' ', '_'))
                        slug_surf = pygame.font.SysFont(None, 20).render(slug_here, True, self.LIGHT_GRAY)
                        self.screen.blit(slug_surf, (img_rect.right + 12, img_rect.y + 28))
                        
                        # Pattern hint and full 12-row preview on hover
                        mouse_pos = pygame.mouse.get_pos()
                        hovered = card.collidepoint(mouse_pos)
                        # Draw a mini 6x12 color preview (bottom row is garbage color)
                        preview_y = img_rect.y + 44
                        block_w = 14
                        block_h = 12
                        spacing_x = 3
                        spacing_y = 2
                        # pick a reference to the player's items for preview
                        preview_items = None
                        if hasattr(self, 'test_mode') and self.test_mode and hasattr(self.test_mode, 'player_items'):
                            preview_items = self.test_mode.player_items
                        # If the item name exists in registry, build a temporary weapon and preview its pattern
                        pattern_colors = None
                        pattern_grid = None
                        if preview_items:
                            try:
                                from modules.items_module.item_system import create_weapon_by_name, Weapon
                                w = create_weapon_by_name(item_name)
                                if w:
                                    # Build 6x12 grid: rows indexed from bottom for pattern
                                    grid_h = 12
                                    pattern_grid = [[None for _ in range(grid_h)] for _ in range(6)]
                                    for c in range(6):
                                        for r in range(grid_h):
                                            # Convert preview row (top=0) to engine row index assumption
                                            engine_row_idx = (grid_h - 1 - r)
                                            try:
                                                color = w.pattern.color_for_cell(c, engine_row_idx, grid_h)
                                                # Safety check: ensure color is valid
                                                if not color or not isinstance(color, str) or color not in ['red', 'blue', 'green', 'yellow']:
                                                    color = 'blue'
                                                pattern_grid[c][r] = color
                                            except Exception:
                                                pattern_grid[c][r] = 'blue'
                                    
                                    # Generate pattern colors with safety checks
                                    pattern_colors = []
                                    for c in range(6):
                                        try:
                                            color = w.pattern.color_for_column(c)
                                            # Safety check: ensure color is valid
                                            if not color or not isinstance(color, str) or color not in ['red', 'blue', 'green', 'yellow']:
                                                color = 'blue'
                                            pattern_colors.append(color)
                                        except Exception:
                                            pattern_colors.append('blue')
                            except Exception:
                                pattern_colors = None
                        
                        # Always show mini pattern preview (column colors)
                        if pattern_colors:
                            mini_preview_y = img_rect.y + 44
                            mini_block_w = 8
                            mini_block_h = 8
                            mini_spacing = 2
                            color_map = {
                                'red': (255, 80, 80),
                                'blue': (80, 80, 255),
                                'green': (80, 255, 120),
                                'yellow': (255, 255, 120)
                            }
                            # Draw mini pattern preview
                            for c in range(6):
                                color_name = pattern_colors[c] if c < len(pattern_colors) else 'blue'
                                # Safety check: ensure color_name is valid
                                if not color_name or not isinstance(color_name, str):
                                    color_name = 'blue'
                                px = img_rect.right + 12 + c * (mini_block_w + mini_spacing)
                                py = mini_preview_y
                                
                                # Enhanced safety check for color
                                try:
                                    color = color_map.get(color_name, (150, 150, 150))
                                    # Ensure color is a valid RGB tuple
                                    if not isinstance(color, tuple) or len(color) != 3:
                                        color = (150, 150, 150)
                                    elif not all(isinstance(x, int) and 0 <= x <= 255 for x in color):
                                        color = (150, 150, 150)
                                    
                                    pygame.draw.rect(self.screen, color, pygame.Rect(px, py, mini_block_w, mini_block_h), border_radius=1)
                                    pygame.draw.rect(self.screen, (40, 40, 40), pygame.Rect(px, py, mini_block_w, mini_block_h), 1, border_radius=1)
                                except Exception as e:
                                    # Fallback to safe color if any error occurs
                                    print(f"Color error in mini preview: {e}, using fallback color")
                                    pygame.draw.rect(self.screen, (150, 150, 150), pygame.Rect(px, py, mini_block_w, mini_block_h), border_radius=1)
                                    pygame.draw.rect(self.screen, (40, 40, 40), pygame.Rect(px, py, mini_block_w, mini_block_h), 1, border_radius=1)
                        # Only show pattern preview on hover
                        if hovered and pattern_grid:
                            color_map = {
                                'red': (255, 80, 80),
                                'blue': (80, 80, 255),
                                'green': (80, 255, 120),
                                'yellow': (255, 255, 120)
                            }
                            # Column labels
                            label = card_font.render("Pattern (12 rows)", True, self.LIGHT_GRAY)
                            self.screen.blit(label, (img_rect.right + 12, preview_y - 18))
                            # Draw from top to bottom
                            for r in range(12):
                                for c in range(6):
                                    color_name = pattern_grid[c][r] if c < len(pattern_grid) and r < len(pattern_grid[c]) else 'blue'
                                    # Safety check: ensure color_name is valid
                                    if not color_name or not isinstance(color_name, str):
                                        color_name = 'blue'
                                    px = img_rect.right + 12 + c * (block_w + spacing_x)
                                    py = preview_y + r * (block_h + spacing_y)
                                    
                                    # Enhanced safety check for color
                                    try:
                                        color = color_map.get(color_name, (150, 150, 150))
                                        # Ensure color is a valid RGB tuple
                                        if not isinstance(color, tuple) or len(color) != 3:
                                            color = (150, 150, 150)
                                        elif not all(isinstance(x, int) and 0 <= x <= 255 for x in color):
                                            color = (150, 150, 150)
                                        
                                        pygame.draw.rect(self.screen, color, pygame.Rect(px, py, block_w, block_h), border_radius=2)
                                        pygame.draw.rect(self.screen, (40, 40, 40), pygame.Rect(px, py, block_w, block_h), 1, border_radius=2)
                                    except Exception as e:
                                        # Fallback to safe color if any error occurs
                                        print(f"Color error in pattern grid: {e}, using fallback color")
                                        pygame.draw.rect(self.screen, (150, 150, 150), pygame.Rect(px, py, block_w, block_h), border_radius=2)
                                        pygame.draw.rect(self.screen, (40, 40, 40), pygame.Rect(px, py, block_w, block_h), 1, border_radius=2)

                        # Hover effect border
                        if hovered:
                            pygame.draw.rect(self.screen, (255, 200, 120), card, 2, border_radius=10)

                        # Equipped badge if this item is currently equipped by player
                        try:
                            equipped = None
                            if hasattr(self, 'test_mode') and self.test_mode and hasattr(self.test_mode, 'player_items'):
                                w = self.test_mode.player_items.get_equipped_weapon()
                                equipped = w.name if w else None
                            if equipped == item_name:
                                badge_rect = pygame.Rect(card.right - 90, card.top + 8, 80, 22)
                                pygame.draw.rect(self.screen, (40, 90, 40), badge_rect, border_radius=6)
                                pygame.draw.rect(self.screen, (120, 220, 120), badge_rect, 1, border_radius=6)
                                badge_text = pygame.font.SysFont(None, 20).render("Equipped", True, (220, 255, 220))
                                self.screen.blit(badge_text, badge_text.get_rect(center=badge_rect.center))
                        except Exception:
                            pass

                elif self.current_screen == "game":
                    # Handle settings UI events first if open
                    if hasattr(self, 'settings_ui') and self.settings_ui and self.settings_ui.is_open():
                        settings_result = self.settings_ui.handle_events(events)
                        if settings_result in ['apply', 'cancel', 'close']:
                            # Settings closed, continue with normal event processing
                            pass
                        else:
                            # Settings consumed the events, skip further processing
                            continue
                    
                    # Start replay session by switching to game once
                    if self._replay_active and not self._replay_started:
                        self._replay_started = True

                    # Process inputs: either replay or live input handler
                    if self._replay_active:
                        game_action = None
                        # Feed due intents based on replay timeline
                        now_ms = self.clock.now_ms()
                        try:
                            intents = self._replayer.step(now_ms)
                            self._apply_intents(intents)
                        except Exception:
                            pass
                    else:
                        # Live input path
                        game_action = self.puzzle_engine.process_events(events)
                        # Record any emitted intents
                        if self._recorder is not None:
                            try:
                                for intent in self.puzzle_engine.input_handler.pop_intents():
                                    self._recorder.record(intent)
                            except Exception:
                                pass
                    # Tuner overlay consumes events after game input handling
                    # DISABLED: Input tuner completely disabled
                    pass
                    
                    # Handle game actions
                    if game_action == "back_to_menu":
                        self.set_screen("main_menu")
                    
                    # Update game timing
                    current_time = self.clock.now_ms() / 1000.0
                    if not hasattr(self, 'last_frame_time'):
                        self.last_frame_time = current_time
                    self.last_frame_time = current_time
                    
                    # Update game state
                    self.puzzle_engine.update()
                    
                    # Update renderer animations
                    self.puzzle_renderer.update_visual_state()
                    self.puzzle_renderer.update_animations()
                    
                    # Draw the game content (avoid extra flip/tick inside renderer)
                    self.puzzle_renderer.draw_game_content()
                    
                    # Draw settings overlay if open
                    if hasattr(self, 'settings_ui') and self.settings_ui and self.settings_ui.is_open():
                        self.settings_ui.draw(self.screen)
                    
                    # Draw tuner overlay on top of game
                    # DISABLED: Input tuner completely disabled
                    pass
                    

                
                # Display MP3 player on all screens unless settings overlay is open
                if hasattr(self, 'audio') and self.audio and not (hasattr(self, 'settings_ui') and self.settings_ui and self.settings_ui.is_open()):
                    self.display_custom_mp3_player()
                    # Global hotkeys for music controls
                    try:
                        keys = pygame.key.get_pressed()
                        # Use bindings if set; otherwise fallbacks
                        def kc(name, default):
                            val = self.config.get(f"bind_{name}")
                            return int(val) if isinstance(val, (int, float)) else default
                        if keys[kc('music_pause', pygame.K_p)]:
                            self.audio.mp3_player.pause_song()
                        if keys[kc('music_next', pygame.K_RIGHTBRACKET)]:
                            self.audio.mp3_player.next_song()
                        if keys[kc('music_prev', pygame.K_LEFTBRACKET)]:
                            self.audio.mp3_player.prev_song()
                        if keys[kc('music_vol_up', pygame.K_EQUALS)]:
                            self.audio.mp3_player.volume_up()
                        if keys[kc('music_vol_down', pygame.K_MINUS)]:
                            self.audio.mp3_player.volume_down()
                    except Exception:
                        pass
                
                # Update settings UI if open
                if hasattr(self, 'settings_ui') and self.settings_ui and self.settings_ui.is_open():
                    self.settings_ui.update(dt)
                
                # Update notifications
                self.update_notifications()
                
                # Global brightness overlay (applies after everything else is drawn)
                try:
                    # Asset preflight toast (non-blocking)
                    if self._preflight_report and (self._preflight_toast_until_ms is None or self.clock.now_ms() <= self._preflight_toast_until_ms):
                        if not self._preflight_report.get('ok', True):
                            # Draw a small toast in the top-right with summary
                            toast_w, toast_h = 520, 140
                            margin = 16
                            x = self.width - toast_w - margin
                            y = margin
                            overlay = pygame.Surface((toast_w, toast_h), pygame.SRCALPHA)
                            overlay.fill((20, 20, 20, 200))
                            pygame.draw.rect(overlay, (120, 60, 60), overlay.get_rect(), 2, border_radius=10)
                            title_font = pygame.font.SysFont(None, 24)
                            body_font = pygame.font.SysFont(None, 20)
                            err_count = len(self._preflight_report.get('errors', []))
                            warn_count = len(self._preflight_report.get('warnings', []))
                            title = title_font.render(f"Asset issues detected: {err_count} errors, {warn_count} warnings", True, (255, 220, 220))
                            overlay.blit(title, (12, 10))
                            # Show up to first 2 errors
                            yy = 40
                            for line in self._preflight_report.get('errors', [])[:2]:
                                text = body_font.render(str(line)[:70], True, (255, 200, 200))
                                overlay.blit(text, (12, yy))
                                yy += 22
                            self.screen.blit(overlay, (x, y))

                    brightness = 1.0
                    if hasattr(self, 'settings_ui') and self.settings_ui:
                        brightness = float(self.settings_ui.config.get('brightness', 1.0))
                    elif hasattr(self, 'config') and self.config:
                        brightness = float(self.config.get('brightness', 1.0))
                    brightness = max(0.3, min(1.0, brightness))
                    if brightness < 0.999:
                        alpha = int(255 * (1.0 - brightness))
                        overlay = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
                        overlay.fill((0, 0, 0, alpha))
                        self.screen.blit(overlay, (0, 0))
                except Exception:
                    pass

                # Draw notifications
                self.draw_notifications()
                
                # FPS overlay
                try:
                    if hasattr(self, 'config') and self.config.get('show_fps', False):
                        fps_font = pygame.font.SysFont(None, 18)
                        fps = int(frame_clock.get_fps())
                        fps_surf = fps_font.render(f"FPS: {fps}", True, (255, 255, 255))
                        self.screen.blit(fps_surf, (10, 10))
                        # If tuner overlay is visible on non-game screens, draw it at very end
                        # DISABLED: Input tuner completely disabled
                        pass
                except Exception:
                    pass
                
                # Update the display
                pygame.display.flip()
        except KeyboardInterrupt:
            print("Game interrupted by user")
        except Exception as e:
            print(f"Error occurred: {e}")
        finally:
            # Persist recording if active
            try:
                if self._recorder is not None and hasattr(self, '_rec_path'):
                    import json as _json
                    sess = self._recorder.stop()
                    with open(self._rec_path, 'w', encoding='utf-8') as f:
                        _json.dump(sess, f, indent=2)
                    self.logger.info(f"Recorded session written to {self._rec_path}")
            except Exception:
                pass
            # Save equipment if test mode exists
            try:
                if hasattr(self, 'test_mode') and self.test_mode and hasattr(self.test_mode, 'save_equipment'):
                    self.test_mode.save_equipment()
            except Exception:
                pass
            # Clean up
            pygame.quit()
            sys.exit()
            
    def load_story(self, story_id):
        """Load story content from file based on story ID (legacy fallback method)."""
        # Use extracted story system if available
        if hasattr(self, 'story_system') and self.story_system:
            self.current_story = self.story_system.load_story(story_id)
            self.story_scroll_position = 0
        else:
            # Simple fallback
            self.current_story = {
                "title": f"Story {story_id}",
                "content": ["Story system not available.", "Please check system configuration."]
            }
            self.story_scroll_position = 0
        
    def display_story_content(self):
        """Display the current story content with scrolling (legacy fallback)."""
        # Simple fallback display
        self.screen.fill(self.BLACK)
        
        # Draw title
        title_font = pygame.font.SysFont(None, 56)
        title_surf = title_font.render(self.current_story["title"], True, self.WHITE)
        title_rect = title_surf.get_rect(midtop=(self.width // 2, 50))
        self.screen.blit(title_surf, title_rect)
        
        # Draw simple content
        text_font = pygame.font.SysFont(None, 24)
        y_offset = title_rect.bottom + 50
        for line in self.current_story["content"][:10]:  # Limit to first 10 lines
            if line:
                surf = text_font.render(line, True, self.WHITE)
                rect = surf.get_rect(topleft=(50, y_offset))
                self.screen.blit(surf, rect)
                y_offset += 30
        
        # Draw instruction
        instruction_font = pygame.font.SysFont(None, 20)
        instruction_surf = instruction_font.render("Press ESC to return to story menu.", True, self.LIGHT_GRAY)
        instruction_rect = instruction_surf.get_rect(midbottom=(self.width // 2, self.height - 10))
        self.screen.blit(instruction_surf, instruction_rect)

if __name__ == "__main__":
    client = GameClient()
    client.run() 