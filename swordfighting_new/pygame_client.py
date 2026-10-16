"""pygame_client.py - Basic Pygame rendering window for Blade Fighters

Implements:
 - Spawn column at position 3 (0-indexed)
 - Up arrow = rotate counter-clockwise, Down arrow = rotate clockwise
 - Space = accelerated gravity while held (NOT instant hard drop)
 - Game over only if newly spawned piece overlaps occupied cells

Usage: python3 -m swordfighting_new.pygame_client
python -m swordfighting_new.pygame_client
python run_bladefighters.py
#C:/BladeFighters_1.5/bladefighters2/BladeFighters-bf1.5/swordfighting_new6/.venv/Scripts/python.exe run_bladefighters.py
Windows venv example:
.venv\\Scripts\\python.exe run_bladefighters.py
Env knobs:
- BF_ENEMY_STYLE: passive|mirror|boss|rubix1|rubix2|rubix3|rubix4|... (default: passive)
- BF_BOSS_LEVEL: integer tier passed into MatchSession (optional)
"""
import os
import sys
from typing import Any
import pygame
from pytweening import easeOutQuad
from swordfighting_new.mechanics.timing import DEFAULT_TIMING
from swordfighting_new.session import MatchSession, BotBattleSession
from swordfighting_new.attacks.garbage_pattern import SwordType, SWORD_PATTERNS, get_sword_asset_filename
from swordfighting_new.util.resources import assets_dir
from swordfighting_new.audio_manager import AudioManager
from swordfighting_new.asset_manager import AssetManager
from swordfighting_new.controllers.settings_controller import SettingsController
from swordfighting_new.controllers.menu_controller import MenuController
from swordfighting_new.controllers.display_controller import DisplayController, get_desktop_size, set_windows_dpi_awareness
from swordfighting_new.controllers.ui_scale_controller import UIScaleController
from swordfighting_new.controllers.input_controller import InputController
from swordfighting_new.rendering.text_render_controller import TextRenderController
from swordfighting_new.rendering.explosion_fx_controller import ExplosionFXController
from swordfighting_new.controllers.training_controller import TrainingController
from swordfighting_new.controllers.story_controller import StoryController
from swordfighting_new.rendering.menu_render_controller import MenuRenderController
from swordfighting_new.controllers.strike_test_controller import StrikeTestController
from swordfighting_new.controllers.event_controller import EventController
from swordfighting_new.rendering.sword_panels_render_controller import SwordPanelsRenderController
from swordfighting_new.rendering.preview_render_controller import PreviewRenderController
from swordfighting_new.controllers.puzzle_sfx_controller import PuzzleSFXController
from swordfighting_new.controllers.fx_events_controller import FXEventsController
from swordfighting_new.rendering.ui_labels_render_controller import UILabelsRenderController
from swordfighting_new.rendering.enemy_hp_panel_render_controller import EnemyHPPanelRenderController
from swordfighting_new.rendering.strike_art_controller import StrikeArtController
from swordfighting_new.rendering.block_render_controller import BlockRenderController
from swordfighting_new.rendering.sword_render_controller import SwordRenderController
from swordfighting_new.rendering.score_render_controller import ScoreRenderController
from swordfighting_new.controllers.board_view_controller import BoardViewController
from swordfighting_new.controllers.smooth_fall_controller import SmoothFallController
from swordfighting_new.controllers.session_reset_controller import SessionResetController
from swordfighting_new.controllers.story_intro_controller import StoryIntroController
from swordfighting_new.ui_config import UIConfig

# Reuse the existing save file format in saves/save.json.
from swordfighting_new.save_system import SaveManager, GameSettings


# Display constants (base; will be scaled at runtime based on display size)
BASE_CELL_W = 40
BASE_CELL_H = 75
BASE_MARGIN = 4
BASE_BOARD_GAP = 72  # pixels between player & enemy boards

CELL_W = BASE_CELL_W
CELL_H = BASE_CELL_H
MARGIN = BASE_MARGIN
BOARD_GAP = BASE_BOARD_GAP

# Preview constants (now side panels)
BASE_PREVIEW_SCALE = 0.8
BASE_PREVIEW_LABEL_OFFSET_Y = 10
BASE_PREVIEW_PIECE_OFFSET_Y = 40
BASE_PREVIEW_PANEL_WIDTH = 120  # width reserved on each side for previews
BASE_PREVIEW_STATS_OFFSET_Y = 140  # y offset for scoring text under previews

PREVIEW_SCALE = BASE_PREVIEW_SCALE
PREVIEW_LABEL_OFFSET_Y = BASE_PREVIEW_LABEL_OFFSET_Y
PREVIEW_PIECE_OFFSET_Y = BASE_PREVIEW_PIECE_OFFSET_Y
PREVIEW_PANEL_WIDTH = BASE_PREVIEW_PANEL_WIDTH
PREVIEW_STATS_OFFSET_Y = BASE_PREVIEW_STATS_OFFSET_Y

# Pull timing numbers from centralized timing config
TIMING = DEFAULT_TIMING
# Cascade/breaker pacing (visual): ~2.5x faster than the prior 5-frame delay.
# Override with BF_CHAIN_FRAME_DELAY if you want explicit control.
if os.getenv('BF_CHAIN_FRAME_DELAY') is None:
    TIMING.chain_frame_delay = 2
FPS = TIMING.target_fps

# Attack pacing configuration (tune to slow down attacks)
ATTACK_DELAY_FRAMES = 24  # frames to wait before delivering outbound or inbound garbage
BULK_GARBAGE_DELIVERY = True  # deliver inbound garbage all at once (evenly distributed stacks)

COLOR_MAP = {
    'red': (220, 50, 50),
    'blue': (50, 90, 200),
    'yellow': (230, 200, 40),
    'green': (40, 180, 80),
    'white': (255, 255, 255),
}

# UI Colors
BG = (18, 18, 28)
GRID_LINE = (40, 40, 60)
BREAKER_OUTLINE = (255, 255, 255)
GARBAGE_COLOR = (120, 120, 120)
STRIKE_OUTLINE = (250, 180, 40)
SPRINKLE_COLOR = (170, 80, 220)
CGARBAGE_COLOR = (170, 170, 170)
DEFAULT_BLOCK_COLOR = (200, 200, 200)


class PygameClient:
    def __init__(self):
        set_windows_dpi_awareness()
        pygame.init()

        # Display controller owns fullscreen/window mode switching.
        self._display = DisplayController(pygame=pygame)

        # UI scale controller owns layout scaling + size-dependent cache rebuilds.
        self._ui_scale_controller = UIScaleController(pygame=pygame)

        # Input controller owns keybind defaults + action resolution.
        self._input = InputController(pygame=pygame)

        # Text render controller owns fitted-text rendering + font caching helpers.
        self._text = TextRenderController(pygame=pygame)

        # Explosion FX controller owns per-color block-break explosion bookkeeping.
        self._explode_fx = ExplosionFXController(pygame=pygame)
        try:
            self._explode_fx.init_explosion_fx_state(self)
        except Exception:
            pass

        # Training controller owns Tutorial + Practice event flows and overlays.
        self._training = TrainingController(pygame=pygame)

        # Story controller owns story/menu scene rendering helpers.
        self._story = StoryController(pygame=pygame)

        # Menu rendering controller owns menu draw functions.
        self._menu_render = MenuRenderController(pygame=pygame)

        # Strike test controller owns Strike Test UI/event/render helpers.
        self._strike_test_controller = StrikeTestController(pygame=pygame)

        # Event controller owns the main pygame event loop dispatch.
        self._events = EventController(pygame=pygame)

        # Sword panels rendering (quickplay/bot battle) controller.
        self._sword_panels_render = SwordPanelsRenderController(pygame=pygame)

        # Side previews rendering (next piece + next sword) controller.
        self._preview_render = PreviewRenderController(pygame=pygame)

        # Puzzle SFX helpers (legacy pygame client SFX; kept as wrappers for compatibility).
        self._puzzle_sfx_controller = PuzzleSFXController(pygame=pygame, assets_dir_fn=assets_dir)

        # Transient FX events (spark outlines, etc.) extracted from client.
        self._fx_events_controller = FXEventsController(pygame=pygame)

        # Top-of-board labels (player/enemy name + style + KO marker).
        self._ui_labels_render = UILabelsRenderController()

        # Enemy HP-mode panel renderer (used when enemy_has_board=False).
        self._enemy_hp_panel_render = EnemyHPPanelRenderController(pygame=pygame)

        # Strike per-cell artwork cache controller.
        self._strike_art = StrikeArtController(pygame=pygame, assets_dir_fn=assets_dir)

        # Block render helper (draw a single cell/block).
        self._block_render = BlockRenderController(pygame=pygame)

        # Horizontal sword render helper (legacy piece variant).
        self._sword_render = SwordRenderController()

        # Preview side-score render helpers.
        self._score_render = ScoreRenderController()

        # Board view/snapshot helpers (render-support; no pygame calls).
        self._board_view_controller = BoardViewController()

        # Smooth-fall interpolation (compute y pixel offsets between rows).
        self._smooth_fall = SmoothFallController()

        # Session reset helper (match/bot battle session recreation + runtime resets).
        self._session_reset = SessionResetController()

        # Story intro helpers (character tiles, name entry, dialogue advance).
        self._story_intro = StoryIntroController(pygame=pygame)

        # Save manager must exist before we attempt to read any persisted settings.
        try:
            self._save_manager = SaveManager()
        except Exception:
            self._save_manager = None

        # Settings controller owns persistence logic (SaveManager interactions).
        self._settings = SettingsController()

        # Menu controller owns menu UI state transitions/draw helpers.
        self._menu = MenuController()

        seed_val = None
        seed_env = os.getenv("BF_SEED")
        if seed_env:
            try:
                seed_val = int(seed_env)
            except ValueError:
                seed_val = None

        # Used by MatchSession/BotBattleSession so resets are deterministic.
        try:
            self._seed_val = seed_val
        except Exception:
            self._seed_val = None
        self._sfx_enabled = str(os.getenv('BF_SFX', '1') or '1').strip().lower() not in ('0', 'false', 'no', 'off')
        env_sfx_volume = os.getenv('BF_SFX_VOLUME')

        # Prefer an existing saved preference; fall back to BF_SFX_VOLUME; else default.
        saved = {}
        try:
            saved = self._settings.load_saved_preferences(self)
        except Exception:
            saved = {}
        saved_volume = saved.get('saved_volume', None)
        saved_hmove_repeat_ms = saved.get('saved_hmove_repeat_ms', None)
        saved_fullscreen = saved.get('saved_fullscreen', None)
        saved_gold = saved.get('saved_gold', None)
        saved_story_tutorial_complete = saved.get('saved_story_tutorial_complete', None)
        saved_story_player_name = saved.get('saved_story_player_name', None)
        saved_keybinds = saved.get('saved_keybinds', None)
        saved_equipped_sword = saved.get('saved_equipped_sword', None)
        saved_enemy_sword = saved.get('saved_enemy_sword', None)
        saved_preview_sword_scale = saved.get('saved_preview_sword_scale', None)
        saved_preview_sword_scale_by_weapon = saved.get('saved_preview_sword_scale_by_weapon', None)
        saved_preview_sword_offset_px = saved.get('saved_preview_sword_offset_px', None)
        saved_preview_piece_offset_px = saved.get('saved_preview_piece_offset_px', None)
        saved_coin_panel_pad_mult = saved.get('saved_coin_panel_pad_mult', None)
        saved_coin_panel_icon_layout_cap_mult = saved.get('saved_coin_panel_icon_layout_cap_mult', None)
        saved_coin_panel_size_override = saved.get('saved_coin_panel_size_override', None)
        saved_coin_panel_size_override_frac = saved.get('saved_coin_panel_size_override_frac', None)

        if saved_volume is not None:
            try:
                self._sfx_volume = float(saved_volume)
            except Exception:
                self._sfx_volume = 0.65
        elif env_sfx_volume is not None and (str(env_sfx_volume).strip() != ''):
            try:
                self._sfx_volume = float(env_sfx_volume)
            except Exception:
                self._sfx_volume = 0.65
        else:
            self._sfx_volume = 0.65
        self._sfx_volume = max(0.0, min(1.0, float(self._sfx_volume)))

        # Audio manager (SFX). Keep PygameClient as orchestrator; manager owns SFX state/caches.
        self._audio = AudioManager(
            pygame=pygame,
            assets_dir_fn=assets_dir,
            enabled=bool(getattr(self, '_sfx_enabled', True)),
            volume=float(getattr(self, '_sfx_volume', 0.65) or 0.65),
        )

        # Assets manager (images/surfaces). Keep PygameClient as orchestrator.
        self._assets = AssetManager()

        # --- Player meta (Story UI uses this for HUD) ---------------
        try:
            self._player_gold = int(saved_gold) if saved_gold is not None else 0
        except Exception:
            self._player_gold = 0

        # --- Story progress (persisted) ----------------------------
        try:
            self._story_swift_tutorial_complete = bool(saved_story_tutorial_complete) if saved_story_tutorial_complete is not None else False
        except Exception:
            self._story_swift_tutorial_complete = False

        try:
            if saved_story_player_name:
                self._story_player_name = str(saved_story_player_name)
                self._story_name_confirmed = True
        except Exception:
            pass

        # --- Horizontal key-hold auto-move (DAS/ARR-lite) ------------
        # Repeat interval in milliseconds. Lower = faster movement.
        try:
            self._horizontal_move_repeat_ms = int(saved_hmove_repeat_ms) if saved_hmove_repeat_ms is not None else int(getattr(GameSettings, 'horizontal_move_repeat_ms', 70))
        except Exception:
            self._horizontal_move_repeat_ms = 70
        self._horizontal_move_repeat_ms = max(30, min(250, int(self._horizontal_move_repeat_ms)))
        # Fixed initial delay before repeats start (ms).
        self._horizontal_move_initial_delay_ms = 160
        # Runtime hold state
        self._horiz_hold_dir = 0  # -1 left, +1 right
        self._horiz_next_repeat_ms = 0
        self._horiz_piece_id = None
        # Track held keycodes so key-hold behavior works reliably across pygame versions.
        # (pygame.key.get_pressed() is scancode-indexed, while keybinds are keycode-based.)
        self._held_keycodes: set[int] = set()

        # --- Strike per-cell (solid.png) cache ------------------------
        try:
            self._strike_art.init_state(self)
        except Exception:
            self._strike_solid_src = None
            self._strike_solid_scaled_cache = {}

        # --- Explosion sprite FX (per-color) ---------------------------
        # Initialized via ExplosionFXController to keep this constructor smaller.

        # --- Display / DPI / Scaling ---------------------------------
        # Defaults:
        # - Windowed by default (dev-friendly; avoids hijacking the display).
        # - Fullscreen can be enabled via saved setting, or by env overrides.
        env_fs = os.getenv('BF_FULLSCREEN')
        if env_fs is not None:
            fullscreen_pref = str(env_fs or '').strip().lower() not in ('0', 'false', 'no', 'off', '')
        else:
            fullscreen_pref = bool(saved_fullscreen) if saved_fullscreen is not None else False

        self._fullscreen_enabled = bool(fullscreen_pref)

        try:
            default_mode = 'fullscreen' if bool(fullscreen_pref) else 'windowed'
            window_mode = (os.getenv('BF_WINDOW_MODE', default_mode) or '').strip().lower()
        except Exception:
            window_mode = 'fullscreen' if bool(fullscreen_pref) else 'windowed'

        # Supported BF_WINDOW_MODE values:
        # - fullscreen: exclusive fullscreen
        # - borderless/fullscreen_windowed: borderless fullscreen window (NOFRAME)
        # - windowed_fullscreen/decorated_fullscreen/maximized: decorated window sized to desktop
        # - windowed: resizable window (BF_WINDOW_W/H)
        borderless = window_mode in ('borderless', 'fullscreen_windowed', 'borderless_fullscreen')
        decorated_fullscreen = window_mode in ('windowed_fullscreen', 'decorated_fullscreen', 'maximized')
        fullscreen = (window_mode == 'fullscreen')

        flags = 0
        # pygame.SCALED can be surprising in normal windowed mode on Windows (it may
        # report a "logical" surface size that causes UI to scale way up). Keep it
        # enabled by default for fullscreen-ish modes, but default it off for normal
        # windowed/resizable windows.
        try:
            default_scaled = '1' if (fullscreen or decorated_fullscreen) else '0'
        except Exception:
            default_scaled = '0'
        want_scaled = False
        try:
            want_scaled = str(os.getenv('BF_SCALED', default_scaled) or default_scaled).strip().lower() not in ('0', 'false', 'no', 'off')
        except Exception:
            want_scaled = (default_scaled == '1')
        # SCALED can be problematic with borderless NOFRAME modes; keep it opt-in there.
        if want_scaled and (not borderless):
            try:
                flags |= pygame.SCALED
            except Exception:
                pass
        if fullscreen:
            flags |= pygame.FULLSCREEN
        elif borderless:
            try:
                flags |= pygame.NOFRAME
            except Exception:
                # If NOFRAME isn't available, fall back to normal window.
                pass
        else:
            flags |= pygame.RESIZABLE

        if fullscreen or borderless or decorated_fullscreen:
            req_w, req_h = get_desktop_size(pygame)
        else:
            try:
                req_w = int(os.getenv('BF_WINDOW_W', '1920') or '1920')
            except Exception:
                req_w = 1920
            try:
                req_h = int(os.getenv('BF_WINDOW_H', '1080') or '1080')
            except Exception:
                req_h = 1080

        # Some SDL/pygame combos reject certain flag combos; allow fallback retries.
        size = (int(req_w), int(req_h))
        try:
            self.screen = pygame.display.set_mode(size, flags)
        except Exception:
            # Retry without SCALED.
            try:
                self.screen = pygame.display.set_mode(size, (flags & ~getattr(pygame, 'SCALED', 0)))
            except Exception:
                # Retry without NOFRAME.
                try:
                    self.screen = pygame.display.set_mode(size, (flags & ~getattr(pygame, 'NOFRAME', 0)))
                except Exception:
                    # Last resort: basic fullscreen/windowed without extras.
                    fallback_flags = pygame.FULLSCREEN if fullscreen else 0
                    self.screen = pygame.display.set_mode(size, fallback_flags)
        pygame.display.set_caption("Blade Fighters Modular")
        self.clock = pygame.time.Clock()
        self.running = True

        # UI state must exist before entering the main loop.
        self.state = 'menu'
        try:
            self._menu_view = str(getattr(self, '_menu_view', 'main') or 'main')
        except Exception:
            self._menu_view = 'main'

        # Track the actual exclusive fullscreen state for toggles/persistence.
        try:
            self._fullscreen_enabled = bool(fullscreen)
        except Exception:
            self._fullscreen_enabled = False

        # Ensure a session exists before any layout sizing uses it.
        # (Some UI computations depend on board dimensions.)
        try:
            mode = str(getattr(self, '_session_mode', 'match') or 'match').strip().lower()
        except Exception:
            mode = 'match'
        if not mode:
            mode = 'match'
        try:
            self._session_mode = str(mode)
        except Exception:
            pass

        try:
            enemy_style = str(getattr(self, '_enemy_style', '') or '').strip().lower()
        except Exception:
            enemy_style = ''
        if not enemy_style:
            try:
                enemy_style = str(os.getenv('BF_ENEMY_STYLE', 'passive') or 'passive').strip().lower()
            except Exception:
                enemy_style = 'passive'
            try:
                self._enemy_style = str(enemy_style)
            except Exception:
                pass

        try:
            boss_level = getattr(self, '_boss_level', None)
        except Exception:
            boss_level = None
        if boss_level is None:
            env_bl = os.getenv('BF_BOSS_LEVEL')
            if env_bl is not None and str(env_bl).strip() != '':
                try:
                    boss_level = int(str(env_bl).strip())
                except Exception:
                    boss_level = None
            try:
                self._boss_level = boss_level
            except Exception:
                pass

        if getattr(self, 'session', None) is None:
            if str(mode) == 'bot_battle':
                try:
                    bot_a = str(getattr(self, '_bot_battle_a_style', 'rubix3') or 'rubix3').strip().lower()
                except Exception:
                    bot_a = 'rubix3'
                try:
                    bot_b = str(getattr(self, '_bot_battle_b_style', 'rubix4') or 'rubix4').strip().lower()
                except Exception:
                    bot_b = 'rubix4'
                self.session = BotBattleSession(
                    timing=TIMING,
                    attack_delay_frames=ATTACK_DELAY_FRAMES,
                    bulk_delivery=BULK_GARBAGE_DELIVERY,
                    seed=getattr(self, '_seed_val', None),
                    bot_a_style=str(bot_a),
                    bot_b_style=str(bot_b),
                )
            else:
                self.session = MatchSession(
                    timing=TIMING,
                    attack_delay_frames=ATTACK_DELAY_FRAMES,
                    bulk_delivery=BULK_GARBAGE_DELIVERY,
                    seed=getattr(self, '_seed_val', None),
                    enemy_style=str(getattr(self, '_enemy_style', 'passive') or 'passive').strip().lower(),
                    boss_level=getattr(self, '_boss_level', None),
                )

            # Apply any already-known sword selections to the fresh session.
            try:
                self._apply_equipped_sword_to_session()
            except Exception:
                pass
            try:
                self._apply_enemy_sword_to_session()
            except Exception:
                pass

        # Compute a UI scale that makes the whole 2-board layout fit nicely.
        board = self.session.player.get_board()
        try:
            screen_w, screen_h = self.screen.get_size()
        except Exception:
            screen_w, screen_h = (3840, 2160)

        base_board_px_w = board.WIDTH * BASE_CELL_W + BASE_MARGIN * 2
        try:
            base_h_cells = int(getattr(board, 'VISIBLE_HEIGHT', board.HEIGHT) or board.HEIGHT)
        except Exception:
            base_h_cells = int(getattr(board, 'HEIGHT', 12) or 12)
        base_board_px_h = base_h_cells * BASE_CELL_H + BASE_MARGIN * 2
        # IMPORTANT: include spawn headroom rows in the sizing model, otherwise the
        # auto UI-scale can overshoot and the bottom of the board gets clipped.
        try:
            base_hr = int(os.getenv('BF_SPAWN_HEADROOM_ROWS', '3') or '3')
        except Exception:
            base_hr = 3
        base_hr = max(0, min(6, int(base_hr)))
        # Layout sizing model:
        # - Normal mode: 2 boards + left/right preview panels.
        # - HP-mode (enemy_has_board=False): 1 board + left preview panel + compact HP panel.
        has_ai = bool(getattr(getattr(self, 'session', None), 'ai', None) is not None)
        has_enemy_board = bool(getattr(getattr(self, 'session', None), 'enemy_has_board', True))
        if has_ai and has_enemy_board:
            base_total_w = base_board_px_w * 2 + BASE_BOARD_GAP + BASE_PREVIEW_PANEL_WIDTH * 2
        elif has_ai and (not has_enemy_board):
            base_enemy_panel_w = max(220, int(round(float(base_board_px_w) * 0.62)))
            base_total_w = BASE_PREVIEW_PANEL_WIDTH + base_board_px_w + BASE_BOARD_GAP + base_enemy_panel_w
        else:
            base_total_w = base_board_px_w + BASE_PREVIEW_PANEL_WIDTH * 2

        base_total_h = base_board_px_h + (base_hr * BASE_CELL_H)

        ui_scale_env = str(os.getenv('BF_UI_SCALE', 'auto') or 'auto').strip().lower()
        if ui_scale_env not in ('', 'auto'):
            try:
                ui_scale = float(ui_scale_env)
            except Exception:
                ui_scale = 1.0
        else:
            # Leave a little breathing room so we don't touch screen edges.
            ui_scale = min(float(screen_w) / float(max(1, base_total_w)), float(screen_h) / float(max(1, base_total_h))) * 0.94

        # Allow small windows to still show the full board by scaling down.
        ui_scale = max(0.45, float(ui_scale))

        # Apply scaled constants (module-level globals used throughout renderer).
        global CELL_W, CELL_H, MARGIN, BOARD_GAP
        global PREVIEW_PANEL_WIDTH, PREVIEW_LABEL_OFFSET_Y, PREVIEW_PIECE_OFFSET_Y, PREVIEW_STATS_OFFSET_Y

        CELL_W = max(10, int(round(BASE_CELL_W * ui_scale)))
        CELL_H = max(10, int(round(BASE_CELL_H * ui_scale)))
        MARGIN = max(2, int(round(BASE_MARGIN * ui_scale)))
        BOARD_GAP = max(12, int(round(BASE_BOARD_GAP * ui_scale)))
        PREVIEW_PANEL_WIDTH = max(80, int(round(BASE_PREVIEW_PANEL_WIDTH * ui_scale)))
        PREVIEW_LABEL_OFFSET_Y = max(6, int(round(BASE_PREVIEW_LABEL_OFFSET_Y * ui_scale)))
        PREVIEW_PIECE_OFFSET_Y = max(18, int(round(BASE_PREVIEW_PIECE_OFFSET_Y * ui_scale)))
        PREVIEW_STATS_OFFSET_Y = max(60, int(round(BASE_PREVIEW_STATS_OFFSET_Y * ui_scale)))

        self.ui_scale = float(ui_scale)

        # Instance-owned snapshot of UI sizing (for modularization / extraction).
        try:
            self._ui = UIConfig.from_scaled_values(
                scale=self.ui_scale,
                cell_w=CELL_W,
                cell_h=CELL_H,
                margin=MARGIN,
                board_gap=BOARD_GAP,
                preview_panel_width=PREVIEW_PANEL_WIDTH,
                preview_label_offset_y=PREVIEW_LABEL_OFFSET_Y,
                preview_piece_offset_y=PREVIEW_PIECE_OFFSET_Y,
                preview_stats_offset_y=PREVIEW_STATS_OFFSET_Y,
            )
        except Exception:
            self._ui = UIConfig.from_scaled_values(
                scale=float(getattr(self, 'ui_scale', 1.0) or 1.0),
                cell_w=int(CELL_W),
                cell_h=int(CELL_H),
                margin=int(MARGIN),
                board_gap=int(BOARD_GAP),
                preview_panel_width=int(PREVIEW_PANEL_WIDTH),
                preview_label_offset_y=int(PREVIEW_LABEL_OFFSET_Y),
                preview_piece_offset_y=int(PREVIEW_PIECE_OFFSET_Y),
                preview_stats_offset_y=int(PREVIEW_STATS_OFFSET_Y),
            )

        # Recompute content sizing/offsets using scaled constants.
        self.board_px_w = board.WIDTH * CELL_W + MARGIN * 2
        try:
            h_cells = int(getattr(board, 'VISIBLE_HEIGHT', board.HEIGHT) or board.HEIGHT)
        except Exception:
            h_cells = int(getattr(board, 'HEIGHT', 12) or 12)
        self.board_px_h = h_cells * CELL_H + MARGIN * 2
        has_ai = bool(getattr(getattr(self, 'session', None), 'ai', None) is not None)
        has_enemy_board = bool(getattr(getattr(self, 'session', None), 'enemy_has_board', True))
        if has_ai and has_enemy_board:
            self.enemy_panel_px_w = int(self.board_px_w)
            content_w = self.board_px_w * 2 + BOARD_GAP + PREVIEW_PANEL_WIDTH * 2
        elif has_ai and (not has_enemy_board):
            # Compact right-side panel for enemy HP so the player board can scale up.
            self.enemy_panel_px_w = max(220, int(round(float(self.board_px_w) * 0.62)))
            content_w = PREVIEW_PANEL_WIDTH + self.board_px_w + BOARD_GAP + int(self.enemy_panel_px_w)
        else:
            self.enemy_panel_px_w = 0
            content_w = self.board_px_w + PREVIEW_PANEL_WIDTH * 2
        # Add some headroom above the boards so the spawn rows are visible.
        # Only the active falling piece is rendered in this headroom area.
        try:
            hr = int(os.getenv('BF_SPAWN_HEADROOM_ROWS', '3') or '3')
        except Exception:
            hr = 3
        self._spawn_headroom_rows = max(0, min(6, int(hr)))
        headroom_px = int(self._spawn_headroom_rows) * int(CELL_H)

        content_h = self.board_px_h + headroom_px
        x_pad = max(0, (int(screen_w) - int(content_w)) // 2)
        y_pad = max(0, (int(screen_h) - int(content_h)) // 2)

        if has_ai and has_enemy_board:
            self.player_offset_x = x_pad + PREVIEW_PANEL_WIDTH
            self.enemy_offset_x = x_pad + PREVIEW_PANEL_WIDTH + self.board_px_w + BOARD_GAP
            self.left_preview_center_x = x_pad + (PREVIEW_PANEL_WIDTH // 2)
            self.right_preview_center_x = x_pad + PREVIEW_PANEL_WIDTH + self.board_px_w + BOARD_GAP + self.board_px_w + (PREVIEW_PANEL_WIDTH // 2)
        elif has_ai and (not has_enemy_board):
            self.player_offset_x = x_pad + PREVIEW_PANEL_WIDTH
            self.enemy_offset_x = self.player_offset_x + self.board_px_w + BOARD_GAP
            self.left_preview_center_x = x_pad + (PREVIEW_PANEL_WIDTH // 2)
            self.right_preview_center_x = int(self.enemy_offset_x - (PREVIEW_PANEL_WIDTH // 2))
        else:
            self.player_offset_x = x_pad + PREVIEW_PANEL_WIDTH
            self.enemy_offset_x = self.player_offset_x + self.board_px_w + BOARD_GAP
            self.left_preview_center_x = x_pad + (PREVIEW_PANEL_WIDTH // 2)
            self.right_preview_center_x = x_pad + PREVIEW_PANEL_WIDTH + self.board_px_w + (PREVIEW_PANEL_WIDTH // 2)
        # Board top starts below the headroom.
        self._content_offset_y = int(y_pad) + int(headroom_px)

        # Scaled fonts for 4K readability.
        self.ui_font = pygame.font.SysFont(None, max(14, int(round(20 * ui_scale))))
        self.preview_font = pygame.font.SysFont(None, max(12, int(round(16 * ui_scale))))

        # Font caching: creating fonts repeatedly (especially via SysFont) can be
        # extremely slow on Windows and can make the app appear frozen.
        self._font_cache: dict[int, pygame.font.Font] = {}
        # Visual smoothing state: remember last per-piece offset to add 1-frame boundary grace
        self._last_offsets = {}
        # Cascade tween state (per board id)
        self.cascade_tween_ms = 100
        self._cascade_tween = {}  # board_id -> {'prev': snapshot, 'start': ms}
        self._last_board_grid = {}  # board_id -> snapshot
        # Preload block/breaker images
        self._load_images()
        # Preload per-color explosion sprites
        self._load_explosion_sprites()
        # Preload board background
        self._load_board_background()

        # Main menu art (background + button)
        self._load_menu_assets()

        # Cache for on-the-fly menu button scaling (used when window is small).
        self._menu_button_state_scaled_cache: dict[tuple[str, int, int], pygame.Surface] = {}

        # Cache for expensive fitted-text rendering (menu labels, etc.).
        self._fitted_text_cache: dict[tuple, pygame.Surface] = {}

        # Initialize audio after pygame init (best-effort; allow headless/no-device).
        try:
            self._audio.init_puzzle_sfx()
        except Exception:
            pass

        # Cache the latest snapshot once per frame (used for SFX + draw).
        self._last_snapshot = None

        # Menu UI state
        self._menu_buttons: list[dict] = []
        self._menu_status_text: str = ''
        self._menu_last_size: tuple[int, int] | None = None
        self._menu_title_font_px = max(24, int(round(54 * ui_scale)))
        self._menu_button_font_px = max(18, int(round(40 * ui_scale)))
        self._menu_title_font = pygame.font.SysFont(None, int(self._menu_title_font_px))
        self._menu_button_font = pygame.font.SysFont(None, int(self._menu_button_font_px))

        # Rendering toggles
        try:
            self._show_grid = str(os.getenv('BF_SHOW_GRID', '0') or '0').strip().lower() in ('1', 'true', 'yes', 'on')
        except Exception:
            self._show_grid = False

        # Controls (Keybinds)
        self._default_keybinds = self._build_default_keybinds()
        self._keybinds = self._normalize_keybinds(saved_keybinds, self._default_keybinds)
        self._rebind_action: str | None = None
        self._menu_selected: int = 0

        # Bot Battle menu UI state
        self._bot_battle_dropdown_open: str | None = None  # None | 'a' | 'b'
        self._bot_battle_sword_scroll_y: dict[str, int] = {'a': 0, 'b': 0}

        # Quickplay (enemy_select) menu UI state
        self._quickplay_sword_scroll_y: dict[str, int] = {'a': 0, 'b': 0}

        # Inventory / Equipped sword
        try:
            self._equipped_sword_value = str(saved_equipped_sword or 'rusty_sword').strip().lower()
        except Exception:
            self._equipped_sword_value = 'rusty_sword'

        # Enemy sword (quickplay): controls the pattern you RECEIVE
        try:
            self._enemy_sword_value = str(saved_enemy_sword or 'rusty_sword').strip().lower()
        except Exception:
            self._enemy_sword_value = 'rusty_sword'

        # Weapon art caches (loaded on-demand by inventory view)
        self._weapon_img_raw: dict[str, pygame.Surface] = {}
        self._weapon_img_raw_trimmed: set[str] = set()
        self._weapon_img_scaled: dict[tuple[str, int], pygame.Surface] = {}
        # Preview-sized weapon art cache (keyed by sword id + target box)
        self._weapon_img_preview_scaled: dict[tuple[str, int, int], pygame.Surface] = {}
        # Preview sword tuning cache: (sword id, target_w, target_h, _) -> scaled surface
        # NOTE: We intentionally scale from the original trimmed PNG each time (cached),
        # rather than scaling an already-scaled surface, to avoid pixelation.
        self._weapon_img_preview_scaled_tuned: dict[tuple[str, int, int, int], pygame.Surface] = {}

        # Gameplay preview sword positioning (draggable during gameplay for layout tuning)
        self._preview_sword_offset_px: dict[str, tuple[int, int]] = {'left': (0, 0), 'right': (0, 0)}
        self._preview_sword_drag_active: bool = False
        self._preview_sword_drag_side: str | None = None
        self._preview_sword_drag_start_pos: tuple[int, int] = (0, 0)
        self._preview_sword_drag_start_offset: tuple[int, int] = (0, 0)
        self._last_preview_sword_rect: dict[str, pygame.Rect | None] = {'left': None, 'right': None}

        # Gameplay preview sword sizing (tune with '-' and '=' during gameplay; later we can lock this value).
        self._preview_sword_scale: float = 1.35
        # Per-sword tuning (because different sword art has different aspect/weight).
        self._preview_sword_scale_by_weapon: dict[str, float] = {}
        # Which side's sword is currently being tuned (set by clicking the sword).
        self._preview_sword_tune_side: str | None = None

        # --- HUD coin panel tuning (persisted via saves/save.json -> ui) ---
        # These affect the background panel sizing for gold/coin HUD widgets.
        # Defaults preserve current look.
        try:
            v = float(saved_coin_panel_pad_mult) if saved_coin_panel_pad_mult is not None else 1.0
        except Exception:
            v = 1.0
        self._coin_panel_pad_mult = max(0.50, min(2.00, float(v)))

        try:
            v2 = float(saved_coin_panel_icon_layout_cap_mult) if saved_coin_panel_icon_layout_cap_mult is not None else 1.25
        except Exception:
            v2 = 1.25
        self._coin_panel_icon_layout_cap_mult = max(1.00, min(3.50, float(v2)))

        # Manual panel size overrides (drag-resize). Stored as pixel sizes.
        self._coin_panel_size_override: dict[str, tuple[int, int]] = {}
        if isinstance(saved_coin_panel_size_override, dict):
            try:
                cleaned: dict[str, tuple[int, int]] = {}
                for k, v in saved_coin_panel_size_override.items():
                    try:
                        kk = str(k or '').strip().lower()
                    except Exception:
                        kk = ''
                    if kk not in ('hud', 'menu', 'story'):
                        continue
                    try:
                        if isinstance(v, (list, tuple)) and len(v) >= 2:
                            w = int(v[0])
                            h = int(v[1])
                        else:
                            continue
                    except Exception:
                        continue
                    w = max(40, min(4096, int(w)))
                    h = max(24, min(4096, int(h)))
                    cleaned[kk] = (int(w), int(h))
                self._coin_panel_size_override = dict(cleaned)
            except Exception:
                pass

        # Manual panel size overrides (drag-resize). Stored as screen-relative fractions.
        # Preferred when present so resizing stays proportional across window/fullscreen changes.
        self._coin_panel_size_override_frac: dict[str, tuple[float, float]] = {}
        if isinstance(saved_coin_panel_size_override_frac, dict):
            try:
                cleaned_f: dict[str, tuple[float, float]] = {}
                for k, v in saved_coin_panel_size_override_frac.items():
                    try:
                        kk = str(k or '').strip().lower()
                    except Exception:
                        kk = ''
                    if kk not in ('hud', 'menu', 'story'):
                        continue
                    try:
                        if isinstance(v, (list, tuple)) and len(v) >= 2:
                            fw = float(v[0])
                            fh = float(v[1])
                        else:
                            continue
                    except Exception:
                        continue
                    fw = max(0.02, min(0.98, float(fw)))
                    fh = max(0.02, min(0.98, float(fh)))
                    cleaned_f[kk] = (float(fw), float(fh))
                self._coin_panel_size_override_frac = dict(cleaned_f)
            except Exception:
                pass

        # Drag state for resizing coin panels.
        self._coin_panel_drag_active: bool = False
        self._coin_panel_drag_kind: str | None = None
        self._coin_panel_drag_corner: str | None = None  # 'bl' | 'br'
        self._coin_panel_drag_start_pos: tuple[int, int] = (0, 0)
        self._coin_panel_drag_start_size: tuple[int, int] = (0, 0)
        self._last_coin_panel_rects: dict[str, pygame.Rect | None] = {'hud': None, 'menu': None, 'story': None}

        # Apply persisted preview sword sizing (if present).
        if saved_preview_sword_scale is not None:
            try:
                v = float(saved_preview_sword_scale)
                self._preview_sword_scale = max(0.30, min(2.50, float(v)))
            except Exception:
                pass
        if isinstance(saved_preview_sword_scale_by_weapon, dict):
            try:
                cleaned: dict[str, float] = {}
                for k, v in saved_preview_sword_scale_by_weapon.items():
                    try:
                        kk = str(k or '').strip().lower()
                    except Exception:
                        kk = ''
                    if not kk:
                        continue
                    try:
                        vv = float(v)
                    except Exception:
                        continue
                    vv = max(0.30, min(2.50, float(vv)))
                    cleaned[kk] = float(vv)
                self._preview_sword_scale_by_weapon = dict(cleaned)
            except Exception:
                pass

        def _apply_offsets(saved_off: Any, target: dict[str, tuple[int, int]]) -> None:
            if not isinstance(saved_off, dict):
                return
            for side in ('left', 'right'):
                try:
                    v = saved_off.get(side, None)
                except Exception:
                    v = None
                if not (isinstance(v, (list, tuple)) and len(v) >= 2):
                    continue
                try:
                    ox = int(v[0])
                    oy = int(v[1])
                except Exception:
                    continue
                ox = max(-800, min(800, int(ox)))
                oy = max(-800, min(800, int(oy)))
                target[str(side)] = (int(ox), int(oy))

        try:
            _apply_offsets(saved_preview_sword_offset_px, self._preview_sword_offset_px)
        except Exception:
            pass

        # Gameplay preview piece positioning (draggable during gameplay for layout tuning)
        self._preview_piece_offset_px: dict[str, tuple[int, int]] = {'left': (0, 0), 'right': (0, 0)}
        self._preview_piece_drag_active: bool = False
        self._preview_piece_drag_side: str | None = None
        self._preview_piece_drag_start_pos: tuple[int, int] = (0, 0)
        self._preview_piece_drag_start_offset: tuple[int, int] = (0, 0)
        self._last_preview_piece_rect: dict[str, pygame.Rect | None] = {'left': None, 'right': None}

        try:
            _apply_offsets(saved_preview_piece_offset_px, self._preview_piece_offset_px)
        except Exception:
            pass

        # Story placeholder UI state
        self._story_char_buttons: list[dict] = []

        # Story intro UI state (academy/menu1)
        self._story_selected_character: str | None = None
        self._story_player_name: str = str(getattr(self, '_story_player_name', '') or '')
        self._story_name_confirmed: bool = bool(getattr(self, '_story_name_confirmed', False))
        self._story_dialogue_step: int = 0
        # Post-tutorial mini-cutscene progression (menu1 -> menu2 -> quarters)
        self._story_post_tutorial_step: int = 0
        # Story scene state
        self._story_inside_cabin_slept: bool = False

        # Tutorial state (guided overlay while playing)
        self._tutorial_active: bool = False
        self._tutorial_step: int = 0
        self._tutorial_done: bool = False
        self._tutorial_progress: dict[str, bool] = {}
        self._tutorial_hint_text: str = ''
        # Tutorial scripted stages (deterministic cluster/combo + inbound demo)
        self._tutorial_cluster_setup_done: bool = False
        self._tutorial_controls_locked: bool = False
        self._tutorial_combo_chain_started: bool = False
        self._tutorial_inbound_injected: bool = False
        # Tutorial input tracking
        self._tutorial_fast_hold_start_ms: int | None = None

        # Story practice events (exams submenu)
        self._practice_active: bool = False
        self._practice_kind: str | None = None  # 'speed_test' | 'boss_1v1'
        self._practice_start_ms: int = 0
        self._practice_duration_ms: int = 0
        self._practice_return_view: str = 'story_practice_exams'
        self._practice_best_chain: int = 0
        self._practice_last_elapsed_ms: int | None = None

        # Menu transition (fade) state
        self._menu_transition_active: bool = False
        self._menu_transition_from: str = 'main'
        self._menu_transition_to: str = 'main'
        self._menu_transition_start_ms: int = 0
        self._menu_transition_duration_ms: int = 650

        # Menu pause overlay (used by placeholder menus to avoid accidental exits)
        self._menu_pause_active: bool = False
        self._menu_pause_buttons: list[dict] = []
        self._menu_pause_selected: int = 0

        # Pause UI state
        self._pause_buttons: list[dict] = []
        self._pause_selected: int = 0
        self._pause_view: str = 'main'  # 'main' | 'options'
        self._pause_status_text: str = ''

    def _reset_session(self) -> None:
        try:
            self._session_reset.reset_session(
                self,
                match_session_cls=MatchSession,
                bot_battle_session_cls=BotBattleSession,
                timing=TIMING,
                attack_delay_frames=int(ATTACK_DELAY_FRAMES),
                bulk_delivery=bool(BULK_GARBAGE_DELIVERY),
            )
        except Exception:
            pass

    def _load_menu_assets(self) -> None:
        try:
            self._assets.load_menu_assets(self)
        except Exception:
            pass

    def _rebuild_menu_scaled_assets(self) -> None:
        try:
            self._assets.rebuild_menu_scaled_assets(self)
        except Exception:
            pass

    def _get_scaled_menu_button_surface(self, state: str, src: pygame.Surface | None, size: tuple[int, int]) -> pygame.Surface | None:
        try:
            return self._assets.get_scaled_menu_button_surface(self, state, src, size)
        except Exception:
            return src

    def _ui_flash_button(self, group: str, button_id: str, duration_ms: int = 130) -> None:
        try:
            now = int(pygame.time.get_ticks())
        except Exception:
            now = 0
        try:
            self._ui_button_flash_group = str(group or '')
            self._ui_button_flash_id = str(button_id or '')
            self._ui_button_flash_until_ms = int(now + max(40, int(duration_ms)))
        except Exception:
            pass

    def _ui_is_button_flashed(self, group: str, button_id: str) -> bool:
        try:
            now = int(pygame.time.get_ticks())
        except Exception:
            now = 0
        try:
            return (
                int(now) < int(getattr(self, '_ui_button_flash_until_ms', 0) or 0)
                and str(getattr(self, '_ui_button_flash_group', '') or '') == str(group or '')
                and str(getattr(self, '_ui_button_flash_id', '') or '') == str(button_id or '')
            )
        except Exception:
            return False

    def _menu_button_at(self, pos) -> str | None:
        try:
            return self._menu.menu_button_at(self, pos)
        except Exception:
            return None

    def _story_char_button_at(self, pos) -> str | None:
        try:
            return self._menu.story_char_button_at(self, pos)
        except Exception:
            return None

    def _get_menu_safe_bounds(self, view: str) -> tuple[int, int]:
        """Return (safe_top, safe_bottom_y) for menu content under the title/header."""
        try:
            return self._menu.get_menu_safe_bounds(self, view)
        except Exception:
            try:
                h = int(self.screen.get_height())
            except Exception:
                h = 1080
            return (0, int(h))

    def _get_two_panel_rects(self, *, view: str) -> tuple['pygame.Rect', 'pygame.Rect', 'pygame.Rect']:
        """Shared 2-side-panel + middle-column menu layout.

        Returns (left_panel, right_panel, mid_rect) sized to fit within the view's safe bounds.
        """
        try:
            return self._menu.get_two_panel_rects(self, view=str(view))
        except Exception:
            w = int(self.screen.get_width())
            h = int(self.screen.get_height())
            z = pygame.Rect(0, 0, max(1, w // 3), max(1, h // 2))
            return (z, z, z)

    def _friendly_sword_name(self, value: str) -> str:
        vv = str(value or '').strip().lower()
        if not vv:
            return ''
        try:
            st = self._resolve_sword_type(vv)
            patt = SWORD_PATTERNS.get(st)
            nm = str(getattr(patt, 'name', vv) or vv)
            return nm
        except Exception:
            return vv

    def _get_bot_battle_sword_panel_rects(self) -> tuple['pygame.Rect', 'pygame.Rect', 'pygame.Rect']:
        """Return (left_panel, right_panel, mid_rect) for Bot Battle menu layout."""
        try:
            return self._menu.get_bot_battle_sword_panel_rects(self)
        except Exception:
            return self._get_two_panel_rects(view='bot_battle')

    def _get_quickplay_sword_panel_rects(self) -> tuple['pygame.Rect', 'pygame.Rect', 'pygame.Rect']:
        """Return (left_panel, right_panel, mid_rect) for Quickplay enemy_select layout."""
        try:
            return self._menu.get_quickplay_sword_panel_rects(self)
        except Exception:
            return self._get_two_panel_rects(view='enemy_select')

    def _get_quickplay_panel_inner_rects(self, side: str) -> tuple['pygame.Rect', 'pygame.Rect', 'pygame.Rect']:
        """Return (panel_rect, header_rect, swords_rect) for a Quickplay side."""
        try:
            return self._menu.get_quickplay_panel_inner_rects(self, side)
        except Exception:
            z = pygame.Rect(0, 0, 1, 1)
            return (z, z, z)

    def _quickplay_sword_layout(self, side: str) -> dict:
        """Compute sword tile layout for Quickplay enemy_select side, including scrolling bounds."""
        try:
            return self._menu.quickplay_sword_layout(self, side)
        except Exception:
            return {
                'panel': pygame.Rect(0, 0, 1, 1),
                'header_rect': pygame.Rect(0, 0, 1, 1),
                'swords_rect': pygame.Rect(0, 0, 1, 1),
                'tiles': [],
                'max_scroll': 0,
                'gap': 0,
            }

    def _quickplay_sword_tile_at(self, pos) -> tuple[str, str] | None:
        """Return ('a'|'b', sword_value) if a Quickplay sword tile was clicked."""
        try:
            return self._menu.quickplay_sword_tile_at(self, pos)
        except Exception:
            return None

    def _draw_quickplay_sword_panels(self, *, mouse_pos: tuple[int, int]) -> None:
        try:
            self._sword_panels_render.draw_quickplay_sword_panels(self, mouse_pos=mouse_pos, color_map=COLOR_MAP)
        except Exception:
            pass

    def _bot_battle_bot_styles(self) -> list[str]:
        try:
            return list(self._menu.bot_battle_bot_styles() or [])
        except Exception:
            return ['rubix1', 'rubix2', 'rubix3', 'rubix4', 'rubix5', 'rubix6']

    def _fmt_bot_battle_style(self, style: str) -> str:
        try:
            return str(self._menu.fmt_bot_battle_style(style))
        except Exception:
            s = str(style or '').strip().lower()
            if s in self._bot_battle_bot_styles():
                return 'Rubix ' + s.replace('rubix', '')
            return s or 'Rubix 1'

    def _get_bot_battle_panel_inner_rects(self, side: str) -> tuple['pygame.Rect', 'pygame.Rect', 'pygame.Rect']:
        """Return (panel_rect, dropdown_rect, swords_rect) for a side."""
        try:
            return self._menu.get_bot_battle_panel_inner_rects(self, side)
        except Exception:
            z = pygame.Rect(0, 0, 1, 1)
            return (z, z, z)

    def _get_bot_battle_dropdown_option_rects(self, side: str) -> list[tuple[str, 'pygame.Rect']]:
        """If dropdown is open for this side, return list of (style, rect)."""
        try:
            return list(self._menu.get_bot_battle_dropdown_option_rects(self, side) or [])
        except Exception:
            return []

    def _bot_battle_dropdown_header_at(self, pos) -> str | None:
        """Return 'a' or 'b' if pos hits a dropdown header."""
        try:
            return self._menu.bot_battle_dropdown_header_at(self, pos)
        except Exception:
            return None

    def _bot_battle_dropdown_option_at(self, pos) -> tuple[str, str] | None:
        """Return (side, style) if pos hits an open dropdown option."""
        try:
            return self._menu.bot_battle_dropdown_option_at(self, pos)
        except Exception:
            return None

    def _bot_battle_sword_layout(self, side: str) -> dict:
        """Compute sword tile layout for a side, including scrolling bounds."""
        try:
            return self._menu.bot_battle_sword_layout(self, side)
        except Exception:
            return {
                'panel': pygame.Rect(0, 0, 1, 1),
                'dropdown_rect': pygame.Rect(0, 0, 1, 1),
                'swords_rect': pygame.Rect(0, 0, 1, 1),
                'tiles': [],
                'max_scroll': 0,
                'gap': 0,
            }

    def _bot_battle_sword_tile_at(self, pos) -> tuple[str, str] | None:
        """Return ('a'|'b', sword_value) if a Bot Battle sword tile was clicked."""
        try:
            return self._menu.bot_battle_sword_tile_at(self, pos)
        except Exception:
            return None

    def _draw_bot_battle_hover_pattern(self, *, sword_type: 'SwordType', anchor_rect: 'pygame.Rect') -> None:
        try:
            self._sword_panels_render.draw_bot_battle_hover_pattern(self, sword_type=sword_type, anchor_rect=anchor_rect, color_map=COLOR_MAP)
        except Exception:
            pass

    def _draw_bot_battle_sword_panels(self, *, mouse_pos: tuple[int, int]) -> None:
        try:
            self._sword_panels_render.draw_bot_battle_sword_panels(self, mouse_pos=mouse_pos, color_map=COLOR_MAP)
        except Exception:
            pass

    def _enter_menu_pause(self) -> None:
        try:
            self._menu.enter_menu_pause(self)
        except Exception:
            pass

    def _exit_menu_pause(self) -> None:
        try:
            self._menu.exit_menu_pause(self)
        except Exception:
            pass

    def _build_menu_pause_buttons(self) -> list[dict]:
        try:
            return self._menu.build_menu_pause_buttons(self)
        except Exception:
            return []

    def _menu_pause_button_at(self, pos) -> int | None:
        try:
            return self._menu.menu_pause_button_at(self, pos)
        except Exception:
            return None

    def _menu_pause_action(self, action_id: str) -> None:
        try:
            self._menu.menu_pause_action(self, action_id)
        except Exception:
            pass

    def _draw_menu_pause_overlay(self) -> None:
        try:
            self._menu.draw_menu_pause_overlay(self)
        except Exception:
            pass

    def _set_menu_status(self, msg: str) -> None:
        try:
            self._menu.set_menu_status(self, msg)
        except Exception:
            self._menu_status_text = ''

    def _set_sfx_volume(self, v: float) -> None:
        try:
            self._settings.set_sfx_volume(self, v)
        except Exception:
            pass

    def _set_horizontal_move_repeat_ms(self, ms: int) -> None:
        try:
            self._settings.set_horizontal_move_repeat_ms(self, ms)
        except Exception:
            pass

    def _recompute_ui_scale_and_assets(self) -> None:
        """Recompute UI scaling and reload any size-dependent assets."""
        try:
            self._ui_scale_controller.recompute_ui_scale_and_assets(self, pygame_client_module=sys.modules[__name__])
        except Exception:
            pass

    def _apply_display_mode(self, fullscreen_enabled: bool) -> None:
        try:
            self._display.apply_display_mode(self, bool(fullscreen_enabled))
        except Exception:
            pass

    def _set_fullscreen_enabled(self, enabled: bool, *, persist: bool = True) -> None:
        enabled = bool(enabled)
        if bool(getattr(self, '_fullscreen_enabled', False)) == enabled:
            return
        self._fullscreen_enabled = bool(enabled)
        if persist:
            try:
                self._persist_volume_preference()
            except Exception:
                pass
        self._apply_display_mode(bool(enabled))

    def _persist_volume_preference(self) -> None:
        try:
            self._settings.persist_volume_preference(self)
        except Exception:
            pass

    def _persist_controls_preference(self) -> None:
        try:
            self._settings.persist_controls_preference(self)
        except Exception:
            pass

    def _persist_equipped_sword_preference(self) -> None:
        try:
            self._settings.persist_equipped_sword_preference(self)
        except Exception:
            pass

    def _persist_enemy_sword_preference(self) -> None:
        try:
            self._settings.persist_enemy_sword_preference(self)
        except Exception:
            pass

    def _persist_preview_sword_tuning(self) -> None:
        try:
            self._settings.persist_preview_sword_tuning(self)
        except Exception:
            pass

    def _persist_coin_panel_size_override(self) -> None:
        try:
            self._settings.persist_coin_panel_size_override(self)
        except Exception:
            pass

    def _resolve_sword_type(self, raw: str | None) -> SwordType:
        val = str(raw or '').strip().lower()
        if val:
            try:
                for st in SwordType:
                    if str(st.value).strip().lower() == val:
                        return st
            except Exception:
                pass

        # Default: prefer rusty_sword if present.
        try:
            return SwordType.RUSTY_SWORD
        except Exception:
            return SwordType.CUTLASS

    def _apply_equipped_sword_to_session(self) -> None:
        try:
            st = self._resolve_sword_type(getattr(self, '_equipped_sword_value', None))
        except Exception:
            return
        try:
            if getattr(self, 'session', None) is not None and getattr(self.session, 'player', None) is not None:
                self.session.player.set_weapon_sword(st)
        except Exception:
            pass

    def _apply_enemy_sword_to_session(self) -> None:
        try:
            st = self._resolve_sword_type(getattr(self, '_enemy_sword_value', None))
        except Exception:
            return
        try:
            if getattr(self, 'session', None) is not None and getattr(self.session, 'ai', None) is not None:
                self.session.ai.set_weapon_sword(st)
        except Exception:
            pass

    def _weapon_asset_path(self, sword_type: SwordType) -> str | None:
        try:
            return self._assets.weapon_asset_path(self, sword_type)
        except Exception:
            return None

    def _weapon_inventory_target_h_px(self) -> int:
        try:
            return int(self._assets.weapon_inventory_target_h_px(self))
        except Exception:
            return 180

    def _trim_alpha_surface(self, surf: 'pygame.Surface') -> 'pygame.Surface':
        try:
            return self._assets.trim_alpha_surface(surf)
        except Exception:
            return surf

    def _invalidate_weapon_scaled_caches_for_key(self, key: str) -> None:
        try:
            self._assets.invalidate_weapon_scaled_caches_for_key(self, key)
        except Exception:
            pass

    def _ensure_weapon_raw_trimmed(self, key: str, raw: 'pygame.Surface') -> 'pygame.Surface':
        try:
            return self._assets.ensure_weapon_raw_trimmed(self, key, raw)
        except Exception:
            return raw

    def _get_weapon_art_scaled(self, sword_type: SwordType) -> pygame.Surface | None:
        try:
            return self._assets.get_weapon_art_scaled(self, sword_type)
        except Exception:
            return None

    def _get_weapon_art_scaled_preview(self, sword_type: SwordType, *, max_w: int, max_h: int) -> pygame.Surface | None:
        try:
            return self._assets.get_weapon_art_scaled_preview(self, sword_type, max_w=max_w, max_h=max_h)
        except Exception:
            return None

    def _get_weapon_art_raw_trimmed(self, sword_type: SwordType) -> pygame.Surface | None:
        try:
            return self._assets.get_weapon_art_raw_trimmed(self, sword_type)
        except Exception:
            return None

    def _get_weapon_art_scaled_preview_exact(self, sword_type: SwordType, *, target_w: int, target_h: int) -> pygame.Surface | None:
        try:
            return self._assets.get_weapon_art_scaled_preview_exact(self, sword_type, target_w=target_w, target_h=target_h)
        except Exception:
            return None

    def _build_default_keybinds(self) -> dict[str, list[int]]:
        try:
            return self._input.build_default_keybinds()
        except Exception:
            return {}

    def _normalize_keybinds(self, raw: dict | None, defaults: dict[str, list[int]]) -> dict[str, list[int]]:
        try:
            return self._input.normalize_keybinds(raw, defaults)
        except Exception:
            try:
                return {k: list(v) for k, v in (defaults or {}).items()}
            except Exception:
                return {}

    def _action_keys(self, action: str) -> list[int]:
        try:
            return self._input.action_keys(self, action)
        except Exception:
            return []

    def _event_is_action(self, event_key: int, action: str) -> bool:
        try:
            return self._input.event_is_action(self, event_key, action)
        except Exception:
            return False

    def _keys_pressed_action(self, keys_pressed, action: str) -> bool:
        try:
            return self._input.keys_pressed_action(self, keys_pressed, action)
        except Exception:
            return False

    def _format_action_keys(self, action: str) -> str:
        try:
            return self._input.format_action_keys(self, action)
        except Exception:
            return 'Unbound'

    def _set_single_binding(self, action: str, keycode: int) -> None:
        try:
            self._input.set_single_binding(self, action, keycode)
        except Exception:
            pass

    def _toggle_sfx(self) -> None:
        try:
            self._settings.toggle_sfx(self)
        except Exception:
            pass

    def _start_quickplay(self) -> None:
        # Quick Play now goes to enemy selection.
        self._menu_view = 'enemy_select'
        self._set_menu_status('')

    def _start_match(self, enemy_style: str, boss_level: int | None = None) -> None:
        # Ensure we are in standard player-vs-enemy mode.
        try:
            self._session_mode = 'match'
        except Exception:
            self._session_mode = 'match'
        try:
            self._enemy_style = str(enemy_style or 'passive').strip().lower()
        except Exception:
            self._enemy_style = 'passive'
        self._boss_level = boss_level

        self._reset_session()
        self.state = 'game'
        self._menu_view = 'main'

        # Clear any lingering postgame state.
        try:
            self._postgame_result = None
            self._postgame_buttons = []
            self._postgame_selected = 0
            self._postgame_breakdown = None
        except Exception:
            pass

    def _start_bot_battle(self) -> None:
        try:
            self._session_mode = 'bot_battle'
        except Exception:
            self._session_mode = 'bot_battle'

        self._reset_session()
        self.state = 'game'
        self._menu_view = 'main'
        self._set_menu_status('')

        # Clear any lingering postgame state.
        try:
            self._postgame_result = None
            self._postgame_buttons = []
            self._postgame_selected = 0
            self._postgame_breakdown = None
        except Exception:
            pass

    def _start_practice_event(self, kind: str) -> None:
        try:
            self._training.start_practice_event(self, kind)
        except Exception:
            pass

    def _end_practice_to_story(self, message: str) -> None:
        try:
            self._training.end_practice_to_story(self, message)
        except Exception:
            pass

    def _practice_tick(self) -> None:
        try:
            self._training.practice_tick(self)
        except Exception:
            pass

    def _draw_practice_overlay(self, snap: dict) -> None:
        try:
            self._training.draw_practice_overlay(self, snap)
        except Exception:
            pass

    def _start_tutorial(self) -> None:
        try:
            self._training.start_tutorial(self)
        except Exception:
            pass

    def _tutorial_step_text(self) -> str:
        try:
            return str(self._training.tutorial_step_text(self))
        except Exception:
            return 'Press Enter to continue.'

    def _advance_tutorial(self) -> None:
        try:
            self._training.advance_tutorial(self)
        except Exception:
            pass

    def _tutorial_configure_combo_stage(self) -> None:
        try:
            self._training.tutorial_configure_combo_stage(self)
        except Exception:
            pass

    def _tutorial_tick(self) -> None:
        try:
            self._training.tutorial_tick(self)
        except Exception:
            pass

    def _award_gold(self, amount: int) -> None:
        try:
            self._settings.award_gold(self, amount)
        except Exception:
            pass

    def _persist_story_progress(self, tutorial_complete: bool | None = None, player_name: str | None = None) -> None:
        try:
            self._settings.persist_story_progress(self, tutorial_complete=tutorial_complete, player_name=player_name)
        except Exception:
            return

    def _complete_tutorial_and_return(self) -> None:
        try:
            self._training.complete_tutorial_and_return(self)
        except Exception:
            pass

    def _draw_tutorial_overlay(self) -> None:
        try:
            self._training.draw_tutorial_overlay(self, preview_panel_width=int(PREVIEW_PANEL_WIDTH), margin=int(MARGIN))
        except Exception:
            pass

    def _enter_postgame(self, result: str) -> None:
        # result: 'win' | 'lose'
        try:
            self._postgame_result = str(result or 'win').strip().lower()
        except Exception:
            self._postgame_result = 'win'
        self.state = 'postgame'
        try:
            self._postgame_selected = int(getattr(self, '_postgame_selected', 0) or 0)
        except Exception:
            self._postgame_selected = 0
        self._postgame_buttons = []

        # Compute final score + gold payout once.
        try:
            snap = self._last_snapshot if self._last_snapshot is not None else self.session.snapshot()
        except Exception:
            snap = {}

        try:
            p_score = ((snap.get('scoring', {}) or {}).get('player', {}) or {})
        except Exception:
            p_score = {}
        try:
            points = int(p_score.get('points_total', 0) or 0)
        except Exception:
            points = 0
        try:
            clears_total = int(p_score.get('clears_total', 0) or 0)
        except Exception:
            clears_total = 0
        try:
            max_chain = int(p_score.get('max_chain', 0) or 0)
        except Exception:
            max_chain = 0

        gold_earned = max(0, int(points))
        try:
            self._postgame_breakdown = {
                'points': int(points),
                'gold_earned': int(gold_earned),
                'clears_total': int(clears_total),
                'max_chain': int(max_chain),
            }
        except Exception:
            self._postgame_breakdown = None

        try:
            if gold_earned > 0:
                self._award_gold(int(gold_earned))
        except Exception:
            pass

        # Freeze the snapshot so the last frame stays visible behind the prompt.
        try:
            if self._last_snapshot is None:
                self._last_snapshot = self.session.snapshot()
        except Exception:
            pass

        # Optional debug log for defeat reasons (helps reproduce "unfair defeat").
        try:
            if str(os.getenv('BF_DEFEAT_REASON_LOG', '0') or '0').strip().lower() in ('1', 'true', 'yes', 'on'):
                snap = self._last_snapshot or {}
                p = (snap.get('player', {}) or {})
                a = (snap.get('ai', {}) or {})
                try:
                    pr = p.get('defeat_reason', None)
                    ar = a.get('defeat_reason', None)
                except Exception:
                    pr, ar = None, None
                print(f"[POSTGAME] result={str(getattr(self, '_postgame_result', 'win'))} player_reason={pr} enemy_reason={ar}")
        except Exception:
            pass

    def _enter_pause(self) -> None:
        try:
            self._menu.enter_pause(self)
        except Exception:
            pass

    def _pause_action(self, action_id: str) -> None:
        try:
            self._menu.pause_action(self, action_id)
        except Exception:
            pass

    def _postgame_action(self, action_id: str) -> None:
        try:
            self._menu.postgame_action(self, action_id)
        except Exception:
            pass

    def _build_postgame_buttons(self) -> list[dict]:
        try:
            return self._menu.build_postgame_buttons(self)
        except Exception:
            return []

    def _build_pause_buttons(self) -> list[dict]:
        try:
            return self._menu.build_pause_buttons(self)
        except Exception:
            return []

    def _postgame_button_at(self, pos) -> int | None:
        try:
            return self._menu.postgame_button_at(self, pos)
        except Exception:
            return None

    def _pause_button_at(self, pos) -> int | None:
        try:
            return self._menu.pause_button_at(self, pos)
        except Exception:
            return None

    def _draw_postgame_prompt(self) -> None:
        try:
            self._menu.draw_postgame_prompt(self)
        except Exception:
            pass

    def _draw_pause_prompt(self) -> None:
        try:
            self._menu.draw_pause_prompt(self)
        except Exception:
            pass

    def _draw_enemy_hp_panel(self, snap: dict) -> None:
        try:
            self._enemy_hp_panel_render.draw_enemy_hp_panel(self, snap, margin=int(MARGIN))
        except Exception:
            pass

    def _make_cell_rect(self, x, y, offset_x=0, offset_y=0):
        return pygame.Rect(offset_x + MARGIN + x * CELL_W, offset_y + MARGIN + y * CELL_H, CELL_W, CELL_H)

    def _get_fighter_for_board(self, board):
        # Map a board instance back to its owning fighter
        return self.session.player if board is self.session.player.get_board() else self.session.ai

    def _load_images(self):
        try:
            self._assets.load_images(self, cell_w=int(CELL_W), cell_h=int(CELL_H))
        except Exception:
            try:
                self.block_images = {}
                self.breaker_images = {}
                self.garbage_images = {}
            except Exception:
                pass

    def _load_explosion_sprites(self) -> None:
        try:
            self._explode_fx.load_explosion_sprites(self, cell_w=int(CELL_W), cell_h=int(CELL_H))
        except Exception:
            try:
                self._assets.load_explosion_sprites(self, cell_w=int(CELL_W), cell_h=int(CELL_H))
            except Exception:
                pass

    def _spawn_explosions_for_delta(self, *, board_id: int, last_snap: dict | None, curr_snap: dict, offset_x: int, offset_y: int) -> None:
        try:
            self._explode_fx.spawn_explosions_for_delta(self, board_id=int(board_id), last_snap=last_snap, curr_snap=curr_snap, offset_x=int(offset_x), offset_y=int(offset_y))
        except Exception:
            pass

    def _draw_active_explosions(self, *, board_id: int) -> None:
        try:
            self._explode_fx.draw_active_explosions(self, board_id=int(board_id))
        except Exception:
            pass

    # --- Puzzle SFX (pygame) ------------------------------------------
    def _init_puzzle_sfx(self) -> None:
        self._puzzle_sfx_controller.init_puzzle_sfx(self)

    def _play_puzzle_sfx(self, key: str, *, stop_first: bool = True) -> None:
        self._puzzle_sfx_controller.play_puzzle_sfx(self, key, stop_first=stop_first)

    def _compute_piece_avg_row_index(self, piece, board, max_rows: int = 12):
        return self._puzzle_sfx_controller.compute_piece_avg_row_index(self, piece, board, max_rows=max_rows)

    def _play_gem_place1_row_sfx_for_piece(self, piece, board) -> None:
        self._puzzle_sfx_controller.play_gem_place1_row_sfx_for_piece(self, piece, board)

    def _count_2x2_clusters(self, board) -> int:
        return self._puzzle_sfx_controller.count_2x2_clusters(self, board)

    def _is_board_stable(self, board) -> bool:
        return bool(self._puzzle_sfx_controller.is_board_stable(self, board))

    def _tick_puzzle_sfx(self, snap: dict, *, pre_player_piece, session_frame: int) -> None:
        self._puzzle_sfx_controller.tick_puzzle_sfx(self, snap, pre_player_piece=pre_player_piece, session_frame=session_frame)

    # --- Strike (per-cell artwork) -----------------------------------
    def _get_strike_solid_block(self):
        try:
            return self._strike_art.get_strike_solid_block(self)
        except Exception:
            return None

    def _get_strike_solid_scaled(self, size: tuple[int, int]):
        try:
            return self._strike_art.get_strike_solid_scaled(self, size)
        except Exception:
            return None

    def _load_board_background(self):
        try:
            self._assets.load_board_background(self, margin=int(MARGIN))
        except Exception:
            self.board_bg = None

    def _get_board_view(self, board) -> tuple[int, int]:
        """Return (view_y0, view_h) for rendering."""
        try:
            return self._board_view_controller.get_board_view(board)
        except Exception:
            try:
                total_h = int(getattr(board, 'HEIGHT', 12) or 12)
            except Exception:
                total_h = 12
            return 0, int(total_h)

    def _snapshot_board(self, board, *, view_y0: int = 0, view_h: int | None = None):
        try:
            return self._board_view_controller.snapshot_board(board, view_y0=int(view_y0), view_h=view_h)
        except Exception:
            return {'cells': {}, 'id_map': {}, 'blocks': {}, 'view_y0': int(view_y0), 'view_h': int(view_h or 0)}

    def _compute_y_offset_pixels(self, board, piece, is_current_piece: bool, faller_occupied: set | None = None, ignore_piece=None) -> int:
        try:
            return int(
                self._smooth_fall.compute_y_offset_pixels(
                    self,
                    board,
                    piece,
                    bool(is_current_piece),
                    faller_occupied=faller_occupied,
                    ignore_piece=ignore_piece,
                    cell_h=int(CELL_H),
                )
            )
        except Exception:
            return 0

    def run(self):
        while self.running:
            self.handle_events()
            self.update_logic()
            self.draw()
            self.clock.tick(FPS)

    def handle_events(self):
        try:
            self._events.handle_events(self)
        except Exception:
            pass

    def update_logic(self):
        if self.state == 'strike_test':
            try:
                if self._strike_test is not None:
                    self._strike_test.update()
            except Exception:
                pass
            self._last_snapshot = None
            return
        if self.state == 'menu':
            # Keep things idle on the menu (no gameplay ticking).
            self._last_snapshot = None
            return
        if self.state == 'pause':
            # Freeze gameplay while paused.
            return
        if self.state == 'postgame':
            # Freeze gameplay while the prompt is up.
            return

        try:
            accepts_input = bool(getattr(self.session, 'accepts_player_input', True))
        except Exception:
            accepts_input = True

        # If the match has ended, we run a limited "settle" simulation so
        # in-flight attacks can finish without continuing normal turns.
        try:
            pending_postgame = bool(getattr(self, '_pending_postgame', False))
        except Exception:
            pending_postgame = False

        # Apply per-frame horizontal auto-repeat when holding left/right.
        if accepts_input:
            try:
                self._input.apply_horizontal_auto_repeat(self, session=self.session, accepts_input=True)
            except Exception:
                pass

        intents = {'move': 0, 'rotate_cw': False, 'rotate_ccw': False, 'fast': (self.fast if accepts_input else False)}
        pre_piece = self.session.player.get_piece() if self.session.player.get_piece() else None
        old_piece_id = id(pre_piece) if pre_piece else None
        if pending_postgame and hasattr(self.session, 'settle_update'):
            try:
                self.session.settle_update()
            except Exception:
                # Fallback: do not crash; keep deterministic no-input update.
                self.session.update({'move': 0, 'rotate_cw': False, 'rotate_ccw': False, 'fast': False})
        else:
            self.session.update(intents)
        new_piece_id = id(self.session.player.get_piece()) if self.session.player.get_piece() else None
        if old_piece_id != new_piece_id and new_piece_id is not None:
            try:
                self._input.reset_fast_fall_state(self)
            except Exception:
                self.fast = False
                self._space_consumed = False
            # Also reset horizontal repeat timers when a new controllable piece spawns.
            try:
                self._input.reset_horizontal_repeat_state(self, piece_id=new_piece_id)
            except Exception:
                pass

        # Snapshot once per frame so SFX + draw read the same data.
        try:
            self._last_snapshot = self.session.snapshot()
        except Exception:
            self._last_snapshot = None

        # Tutorial runtime (scripted stages + inbound demo).
        try:
            self._tutorial_tick()
        except Exception:
            pass

        # Practice events runtime.
        try:
            self._practice_tick()
        except Exception:
            pass

        # Ingest transient FX events (drained from fx_bus during snapshot).
        try:
            snap = self._last_snapshot or {}
            self._ingest_fx_events(snap)
        except Exception:
            pass

        # SFX tick (lock/settle/cluster/break).
        try:
            snap = self._last_snapshot or {}
            session_frame = int(getattr(self.session, 'frame', 0) or 0)
            self._audio.tick_puzzle_sfx(snap, pre_player_piece=pre_piece, session_frame=session_frame, session=self.session)
        except Exception:
            pass

        ai_defeated = bool(getattr(getattr(self.session, 'ai', None), 'defeated', False))
        player_defeated = bool(getattr(self.session, 'player', None).defeated)

        # Practice mode: intercept endings and return to story instead of postgame.
        if bool(getattr(self, '_practice_active', False)) and (player_defeated or ai_defeated):
            kind = str(getattr(self, '_practice_kind', '') or '').strip().lower()
            try:
                elapsed_ms = int(getattr(self, '_practice_last_elapsed_ms', None) or 0)
            except Exception:
                elapsed_ms = 0
            try:
                sec = int(elapsed_ms // 1000)
                mm = int(sec // 60)
                ss = int(sec % 60)
                t = f"{mm}:{ss:02d}"
            except Exception:
                t = '0:00'

            if kind == 'speed_test':
                if player_defeated and (not ai_defeated):
                    self._end_practice_to_story(f"Speed test: {t} (you lost)")
                elif ai_defeated and (not player_defeated):
                    self._end_practice_to_story(f"Speed test: you WON in {t} — try to lose faster")
                else:
                    self._end_practice_to_story(f"Speed test: ended in {t}")
                return

            if kind == 'boss_1v1':
                if ai_defeated and (not player_defeated):
                    self._end_practice_to_story(f"1v1 (Boss): WIN — {t}")
                elif player_defeated and (not ai_defeated):
                    self._end_practice_to_story(f"1v1 (Boss): LOSE — {t}")
                else:
                    self._end_practice_to_story(f"1v1 (Boss): ended — {t}")
                return

            # Unknown practice kind -> fall through to postgame.

        # Postgame settle window: if the match ends, keep ticking briefly so
        # inbound attacks / chains / swords can finish landing before we freeze
        # the game under the replay/menu prompt.
        if player_defeated or ai_defeated:
            try:
                pending = bool(getattr(self, '_pending_postgame', False))
            except Exception:
                pending = False

            if not pending:
                try:
                    self._pending_postgame = True
                    self._pending_postgame_result = 'win' if ai_defeated else 'lose'
                    try:
                        self._pending_postgame_start_ms = int(pygame.time.get_ticks())
                    except Exception:
                        self._pending_postgame_start_ms = 0
                except Exception:
                    pass
                # Freeze player input during the settle window.
                try:
                    if hasattr(self.session, 'accepts_player_input'):
                        self.session.accepts_player_input = False
                except Exception:
                    pass
                try:
                    self.fast = False
                except Exception:
                    pass

            try:
                if self._postgame_settle_complete() or self._postgame_settle_timed_out():
                    res = str(getattr(self, '_pending_postgame_result', 'win') or 'win')
                    self._pending_postgame = False
                    self._enter_postgame(res)
                return
            except Exception:
                # If anything goes wrong, do not trap the user.
                self._enter_postgame('win' if ai_defeated else 'lose')
                return

        # If the game continues, clear any stale pending state.
        try:
            self._pending_postgame = False
        except Exception:
            pass

    def _postgame_settle_timed_out(self) -> bool:
        """Fail-safe timeout for the settle window."""
        try:
            start = int(getattr(self, '_pending_postgame_start_ms', 0) or 0)
        except Exception:
            start = 0
        try:
            now = int(pygame.time.get_ticks())
        except Exception:
            return True

        try:
            timeout_ms = int(os.getenv('BF_POSTGAME_SETTLE_TIMEOUT_MS', '8000') or '8000')
        except Exception:
            timeout_ms = 8000
        timeout_ms = max(250, int(timeout_ms))
        return int(now - start) >= int(timeout_ms)

    def _postgame_settle_complete(self) -> bool:
        """True once the session has no active attack/chain/inbound activity."""
        s = getattr(self, 'session', None)
        if s is None:
            return True

        fighters = []
        try:
            fighters.append(getattr(s, 'player', None))
        except Exception:
            pass
        try:
            fighters.append(getattr(s, 'ai', None))
        except Exception:
            pass

        for f in fighters:
            if f is None:
                continue

            # Chain / breaker activity
            try:
                cr = getattr(f, 'chain_runner', None)
                if cr is not None and bool(getattr(cr, 'active', False)):
                    return False
            except Exception:
                return False

            try:
                bm = getattr(f, 'breaker', None)
                if bm is not None and (bool(getattr(bm, 'cascade_in_progress', False)) or bool(bm.has_pending_breakers())):
                    return False
            except Exception:
                pass

            # Inbound (pending + in-flight)
            try:
                ih = getattr(f, 'inbound_handler', None)
                if ih is not None:
                    if int(getattr(ih, 'pending_in_sprinkle', 0) or 0) > 0:
                        return False
                    if int(getattr(ih, 'pending_in_strike', 0) or 0) > 0:
                        return False
                    if int(getattr(ih, 'spawn_queue', 0) or 0) > 0:
                        return False
                    if len(getattr(ih, 'garbage_fallers', []) or []) > 0:
                        return False
                    if len(getattr(ih, '_delayed_clusters', []) or []) > 0:
                        return False
            except Exception:
                return False

            # Horizontal swords still in-flight
            try:
                hs = getattr(f, 'horizontal_swords', None)
                if hs is not None and len(getattr(hs, 'active_swords', []) or []) > 0:
                    return False
            except Exception:
                pass

        return True

    def draw(self):
        if self.state == 'menu':
            self._draw_main_menu()
            pygame.display.flip()
            return

        if self.state == 'strike_test':
            self._draw_strike_test()
            pygame.display.flip()
            return

        if self.state == 'postgame':
            # Draw the last game frame, then overlay the prompt.
            self.screen.fill(BG)
            snap = self._last_snapshot if self._last_snapshot is not None else self.session.snapshot()
            self._now_ms = pygame.time.get_ticks()
            self._draw_board(snap['player']['board'], snap['player']['piece'], snap['player']['garbage_fallers'], offset_x=self.player_offset_x, offset_y=getattr(self, '_content_offset_y', 0))
            if snap.get('ai') is not None:
                if bool(snap.get('enemy_has_board', True)):
                    self._draw_board(snap['ai']['board'], snap['ai']['piece'], snap['ai']['garbage_fallers'], offset_x=self.enemy_offset_x, offset_y=getattr(self, '_content_offset_y', 0))
                else:
                    self._draw_enemy_hp_panel(snap)
            try:
                if bool(getattr(self, '_fx_enabled', False)):
                    self._draw_active_fx(snap)
            except Exception:
                pass
            self._draw_side_previews(snap)
            self._draw_ui_labels(snap)
            try:
                self._draw_score_hud_under_previews(snap)
            except Exception:
                pass
            try:
                self._draw_score_and_gold_hud(snap)
            except Exception:
                pass
            try:
                self._draw_practice_overlay(snap)
            except Exception:
                pass
            self._draw_postgame_prompt()
            pygame.display.flip()
            return

        if self.state == 'pause':
            # Draw the last game frame, then overlay pause prompt.
            self.screen.fill(BG)
            snap = self._last_snapshot if self._last_snapshot is not None else self.session.snapshot()
            self._now_ms = pygame.time.get_ticks()
            self._draw_board(snap['player']['board'], snap['player']['piece'], snap['player']['garbage_fallers'], offset_x=self.player_offset_x, offset_y=getattr(self, '_content_offset_y', 0))
            if snap.get('ai') is not None:
                if bool(snap.get('enemy_has_board', True)):
                    self._draw_board(snap['ai']['board'], snap['ai']['piece'], snap['ai']['garbage_fallers'], offset_x=self.enemy_offset_x, offset_y=getattr(self, '_content_offset_y', 0))
                else:
                    self._draw_enemy_hp_panel(snap)
            try:
                if bool(getattr(self, '_fx_enabled', False)):
                    self._draw_active_fx(snap)
            except Exception:
                pass
            self._draw_side_previews(snap)
            self._draw_ui_labels(snap)
            try:
                self._draw_score_hud_under_previews(snap)
            except Exception:
                pass
            try:
                self._draw_score_and_gold_hud(snap)
            except Exception:
                pass
            try:
                self._draw_practice_overlay(snap)
            except Exception:
                pass
            self._draw_pause_prompt()
            try:
                # Don't draw tutorial overlay while paused (pause prompt takes over).
                pass
            except Exception:
                pass
            pygame.display.flip()
            return

        self.screen.fill(BG)
        snap = self._last_snapshot if self._last_snapshot is not None else self.session.snapshot()
        self._now_ms = pygame.time.get_ticks()
        self._draw_board(snap['player']['board'], snap['player']['piece'], snap['player']['garbage_fallers'], offset_x=self.player_offset_x, offset_y=getattr(self, '_content_offset_y', 0))
        if snap.get('ai') is not None:
            if bool(snap.get('enemy_has_board', True)):
                self._draw_board(snap['ai']['board'], snap['ai']['piece'], snap['ai']['garbage_fallers'], offset_x=self.enemy_offset_x, offset_y=getattr(self, '_content_offset_y', 0))
            else:
                self._draw_enemy_hp_panel(snap)
        try:
            if bool(getattr(self, '_fx_enabled', False)):
                self._draw_active_fx(snap)
        except Exception:
            pass
        self._draw_side_previews(snap)
        self._draw_ui_labels(snap)
        try:
            self._draw_score_hud_under_previews(snap)
        except Exception:
            pass
        try:
            self._draw_score_and_gold_hud(snap)
        except Exception:
            pass
        try:
            self._draw_practice_overlay(snap)
        except Exception:
            pass
        try:
            self._draw_tutorial_overlay()
        except Exception:
            pass
        pygame.display.flip()

    def _ingest_fx_events(self, snap: dict) -> None:
        self._fx_events_controller.ingest_fx_events(self, snap)

    def _draw_active_fx(self, snap: dict) -> None:
        self._fx_events_controller.draw_active_fx(self, snap)

    def _build_menu_buttons(self, view: str) -> list[dict]:
        try:
            return self._menu.build_menu_buttons(self, view)
        except Exception:
            return []

    def _build_story_character_buttons(self) -> list[dict]:
        try:
            return list(self._story_intro.build_story_character_buttons(self) or [])
        except Exception:
            return []

    def _on_menu_button(self, bid: str) -> None:
        try:
            self._menu.on_menu_button(self, bid)
        except Exception:
            pass

    def _enter_strike_test(self) -> None:
        try:
            self._strike_test_controller.enter_strike_test(
                self,
                timing=TIMING,
                attack_delay_frames=ATTACK_DELAY_FRAMES,
                bulk_delivery=BULK_GARBAGE_DELIVERY,
            )
        except Exception:
            pass

    def _exit_strike_test(self) -> None:
        try:
            self._strike_test_controller.exit_strike_test(self)
        except Exception:
            pass

    def _strike_test_run(self) -> None:
        try:
            self._strike_test_controller.strike_test_run(self)
        except Exception:
            pass

    def _strike_test_rebuild_ui(self) -> None:
        try:
            self._strike_test_controller.strike_test_rebuild_ui(
                self,
                margin=MARGIN,
                cell_w=CELL_W,
                cell_h=CELL_H,
                preview_panel_width=PREVIEW_PANEL_WIDTH,
                board_gap=BOARD_GAP,
            )
        except Exception:
            self._strike_ui = {}

    def _handle_strike_test_event(self, event) -> None:
        try:
            self._strike_test_controller.handle_strike_test_event(
                self,
                event,
                margin=MARGIN,
                cell_w=CELL_W,
                cell_h=CELL_H,
                preview_panel_width=PREVIEW_PANEL_WIDTH,
                board_gap=BOARD_GAP,
            )
        except Exception:
            pass

    def _draw_strike_test(self) -> None:
        try:
            self._strike_test_controller.draw_strike_test(
                self,
                bg=BG,
                margin=MARGIN,
                cell_w=CELL_W,
                cell_h=CELL_H,
                preview_panel_width=PREVIEW_PANEL_WIDTH,
                board_gap=BOARD_GAP,
            )
        except Exception:
            pass


    def _begin_menu_transition(self, to_view: str, duration_ms: int | None = None) -> None:
        try:
            self._menu.begin_menu_transition(self, to_view, duration_ms)
        except Exception:
            self._menu_transition_active = False

    def _start_story_intro_from_character(self, cid: str) -> None:
        try:
            self._story_intro.start_story_intro_from_character(self, cid)
        except Exception:
            pass

    def _handle_story_name_input(self, event) -> None:
        try:
            self._story_intro.handle_story_name_input(self, event)
        except Exception:
            pass

    def _advance_story_intro(self) -> None:
        try:
            self._story_intro.advance_story_intro(self)
        except Exception:
            pass

    def _wrap_text(self, text: str, font, max_width: int) -> list[str]:
        try:
            return self._text.wrap_text(text, font, int(max_width))
        except Exception:
            return [str(text or '')]

    def _ellipsize_text(self, text: str, font, max_width: int) -> str:
        try:
            return self._text.ellipsize_text(text, font, int(max_width))
        except Exception:
            return '...'

    def _render_fitted_text(self, text: str, *, max_width: int, max_height: int, color=(255, 255, 255), base_px: int | None = None, min_px: int | None = None, max_lines: int = 2) -> pygame.Surface | None:
        try:
            return self._text.render_fitted_text(
                self,
                text,
                max_width=int(max_width),
                max_height=int(max_height),
                color=color,
                base_px=base_px,
                min_px=min_px,
                max_lines=int(max_lines),
            )
        except Exception:
            return None

    def _blit_fitted_text(self, text: str, rect: pygame.Rect, *, color=(255, 255, 255), pad: int | None = None, x: int | None = None, align: str = 'center', base_px: int | None = None, max_lines: int = 2) -> None:
        try:
            self._text.blit_fitted_text(
                self,
                text,
                rect,
                color=color,
                pad=pad,
                x=x,
                align=str(align),
                base_px=base_px,
                max_lines=int(max_lines),
            )
        except Exception:
            pass

    def _get_story_dialogue_text(self) -> str:
        try:
            return str(self._story.get_story_dialogue_text(self))
        except Exception:
            return ""

    def _draw_story_intro(self) -> None:
        try:
            self._story.draw_story_intro(self)
        except Exception:
            pass

    def _story_message_for_academy(self) -> str:
        try:
            return str(self._story.story_message_for_academy(self))
        except Exception:
            return ''

    def _draw_story_academy(self) -> None:
        try:
            self._story.draw_story_academy(self)
        except Exception:
            pass

    def _draw_story_quarters(self) -> None:
        try:
            self._story.draw_story_quarters(self)
        except Exception:
            pass

    def _draw_story_inside_cabin(self) -> None:
        try:
            self._story.draw_story_inside_cabin(self)
        except Exception:
            pass

    def _draw_story_practice_exams(self) -> None:
        try:
            self._story.draw_story_practice_exams(self)
        except Exception:
            pass

    def _draw_story_examinations(self) -> None:
        try:
            self._story.draw_story_examinations(self)
        except Exception:
            pass

    def _draw_menu_view(self, view) -> None:
        try:
            self._menu_render.draw_menu_view(self, view, color_map=COLOR_MAP)
        except Exception:
            pass

    def _draw_main_menu(self) -> None:
        try:
            self._menu_render.draw_main_menu(self)
        except Exception:
            pass

    def _draw_ui_labels(self, snap):
        # Hide top-of-board label text (Player/Enemy/etc.) per UX request.
        return

    def _draw_score_hud_under_previews(self, snap: dict) -> None:
        """Draw the player's total score under the left side preview panel.

        This avoids overlap with the top-right currency HUD.
        """
        try:
            scoring = (snap or {}).get('scoring', {}) or {}
            p_score = scoring.get('player', {}) or {}
            points = int(p_score.get('points_total', 0) or 0)
        except Exception:
            points = 0

        try:
            enemy_has_board = bool((snap or {}).get('enemy_has_board', True))
        except Exception:
            enemy_has_board = True
        try:
            ai_score = ((scoring or {}).get('ai', {}) or {}) if enemy_has_board else {}
            ai_points = int(ai_score.get('points_total', 0) or 0) if enemy_has_board else 0
        except Exception:
            ai_points = 0

        try:
            left_center_x = int(getattr(self, 'left_preview_center_x', 0) or 0)
        except Exception:
            left_center_x = 0
        try:
            right_center_x = int(getattr(self, 'right_preview_center_x', 0) or 0)
        except Exception:
            right_center_x = 0
        if left_center_x <= 0 and (not (enemy_has_board and right_center_x > 0)):
            return

        try:
            w = int(self.screen.get_width())
            h = int(self.screen.get_height())
        except Exception:
            w, h = (0, 0)

        try:
            ui_scale = float(getattr(self, 'ui_scale', 1.0) or 1.0)
        except Exception:
            ui_scale = 1.0
        base_gap_y = int(max(6, round(10 * float(ui_scale))))

        try:
            y0 = int(getattr(self, '_content_offset_y', 0) or 0)
        except Exception:
            y0 = 0

        # Default fallback (legacy placement).
        try:
            fallback_y = int(y0 + int(MARGIN) + int(PREVIEW_STATS_OFFSET_Y))
        except Exception:
            fallback_y = int(y0 + 8 + 120)

        def _y_under_preview(side: str) -> int:
            yy = int(fallback_y)
            try:
                pr = (getattr(self, '_last_preview_piece_rect', None) or {}).get(side, None)
            except Exception:
                pr = None
            try:
                sr = (getattr(self, '_last_preview_sword_rect', None) or {}).get(side, None)
            except Exception:
                sr = None
            bottoms: list[int] = []
            try:
                if pr is not None:
                    bottoms.append(int(pr.bottom))
            except Exception:
                pass
            try:
                if sr is not None:
                    bottoms.append(int(sr.bottom))
            except Exception:
                pass
            if bottoms:
                yy = max(int(yy), int(max(bottoms) + int(base_gap_y)))
            return int(yy)

        try:
            font = getattr(self, 'preview_font', None) or getattr(self, 'ui_font', None)
            if font is None:
                return
            surf_left = font.render(f"P: {points}", True, (220, 220, 232))
            surf_right = font.render(f"E: {ai_points}", True, (220, 220, 232)) if enemy_has_board else None
        except Exception:
            return

        y_left = int(_y_under_preview('left'))
        y_right = int(_y_under_preview('right'))
        try:
            if int(h) > 0:
                y_left = max(0, min(int(h - surf_left.get_height() - 2), int(y_left)))
                if surf_right is not None:
                    y_right = max(0, min(int(h - surf_right.get_height() - 2), int(y_right)))
        except Exception:
            pass

        try:
            if left_center_x > 0:
                x = int(left_center_x - int(surf_left.get_width()) // 2)
                self.screen.blit(surf_left, (int(x), int(y_left)))
            if enemy_has_board and surf_right is not None and right_center_x > 0:
                xr = int(right_center_x - int(surf_right.get_width()) // 2)
                self.screen.blit(surf_right, (int(xr), int(y_right)))
        except Exception:
            pass

    def _draw_score_and_gold_hud(self, snap: dict) -> None:
        try:
            w = int(self.screen.get_width())
            h = int(self.screen.get_height())
        except Exception:
            return

        try:
            gold = int(getattr(self, '_player_gold', 0) or 0)
        except Exception:
            gold = 0

        try:
            pad = int(max(8, round(12 * float(getattr(self, 'ui_scale', 1.0) or 1.0))))
            gap = int(max(2, round(4 * float(getattr(self, 'ui_scale', 1.0) or 1.0))))
        except Exception:
            pad, gap = 10, 4

        try:
            pad_mult = float(getattr(self, '_coin_panel_pad_mult', 1.0) or 1.0)
        except Exception:
            pad_mult = 1.0
        pad_mult = max(0.50, min(2.00, float(pad_mult)))
        pad = int(max(4, int(round(float(pad) * float(pad_mult)))))

        try:
            fh = int(self.ui_font.get_height())
        except Exception:
            fh = int(round(20 * float(getattr(self, 'ui_scale', 1.0) or 1.0)))
        # Scale icon off font height so it stays readable at 4K.
        try:
            # Oversized on purpose for readability.
            coin = self._assets.get_coin_icon_scaled(self, target_h=max(84, int(round(fh * 12.0))))
        except Exception:
            coin = None

        items: list[tuple[pygame.Surface, pygame.Surface | None]] = []
        try:
            items.append((self.ui_font.render(f"{gold}", True, (245, 245, 245)), coin))
        except Exception:
            return
        if not items:
            return

        icon_gap = int(max(4, round(6 * float(getattr(self, 'ui_scale', 1.0) or 1.0))))
        try:
            if coin is not None:
                # Don't let an oversized coin inflate spacing too much.
                eff_h = min(int(coin.get_height()), int(round(float(fh) * 3.0)))
                icon_gap = int(max(int(icon_gap), int(round(float(eff_h) * 0.22))))
        except Exception:
            pass

        try:
            icon_cap_mult = float(getattr(self, '_coin_panel_icon_layout_cap_mult', 1.25) or 1.25)
        except Exception:
            icon_cap_mult = 1.25
        icon_cap_mult = max(1.00, min(3.50, float(icon_cap_mult)))
        try:
            content_w = 0
            content_h = 0
            for (txt, ico) in items:
                row_w = int(txt.get_width())
                row_h = int(txt.get_height())
                if ico is not None:
                    row_w += int(ico.get_width()) + int(icon_gap)
                    # Keep the background panel compact by capping how much the icon
                    # contributes to layout height. The icon itself is still drawn full-size.
                    try:
                        ico_layout_h = min(int(ico.get_height()), int(round(float(row_h) * float(icon_cap_mult))))
                    except Exception:
                        ico_layout_h = int(row_h)
                    row_h = max(row_h, int(ico_layout_h))
                content_w = max(content_w, row_w)
                content_h += int(row_h)
            content_h += max(0, len(items) - 1) * int(gap)

            panel_w = int(content_w + 2 * pad)
            panel_h = int(content_h + 2 * pad)

            # Manual resize override (drag corner). Allows the panel to be sized independent
            # of content-driven auto sizing.
            try:
                ov_f = (getattr(self, '_coin_panel_size_override_frac', {}) or {}).get('hud', None)
            except Exception:
                ov_f = None
            if isinstance(ov_f, (list, tuple)) and len(ov_f) >= 2:
                try:
                    ow = int(round(float(ov_f[0]) * float(w)))
                    oh = int(round(float(ov_f[1]) * float(h)))
                    panel_w = int(max(40, min(int(w - 6), int(ow))))
                    panel_h = int(max(24, min(int(h - 6), int(oh))))
                except Exception:
                    pass
            else:
                try:
                    ov = (getattr(self, '_coin_panel_size_override', {}) or {}).get('hud', None)
                except Exception:
                    ov = None
                if isinstance(ov, (list, tuple)) and len(ov) >= 2:
                    try:
                        ow = int(ov[0])
                        oh = int(ov[1])
                        panel_w = int(max(40, min(int(w - 6), int(ow))))
                        panel_h = int(max(24, min(int(h - 6), int(oh))))
                    except Exception:
                        pass

            panel_x = int(w - panel_w - int(w * 0.03))
            panel_y = int(h * 0.02)

            try:
                self._last_coin_panel_rects['hud'] = pygame.Rect(int(panel_x), int(panel_y), int(panel_w), int(panel_h))
            except Exception:
                pass
        except Exception:
            return

        try:
            panel = pygame.Surface((int(panel_w), int(panel_h)), flags=pygame.SRCALPHA)
            panel.fill((0, 0, 0, 150))
            self.screen.blit(panel, (panel_x, panel_y))
            pygame.draw.rect(self.screen, (255, 255, 255), pygame.Rect(panel_x, panel_y, panel_w, panel_h), width=2, border_radius=10)
        except Exception:
            pass

        try:
            yy = int(panel_y + pad)
            for (txt, ico) in items:
                row_h = int(txt.get_height())
                x = int(panel_x + pad)
                if ico is not None:
                    # Layout row height stays text-driven; icon may extend beyond panel.
                    try:
                        ico_h = int(ico.get_height())
                    except Exception:
                        ico_h = 0
                    try:
                        ico_layout_h = min(int(ico_h), int(round(float(row_h) * float(icon_cap_mult))))
                    except Exception:
                        ico_layout_h = int(row_h)
                    row_h = max(row_h, int(ico_layout_h))
                    iy = int(yy + (int(txt.get_height()) - int(ico_h)) // 2)
                    iy = max(0, int(iy))
                    self.screen.blit(ico, (int(x), int(iy)))
                    x = int(x + int(ico.get_width()) + int(icon_gap))
                ty = int(yy + (row_h - int(txt.get_height())) // 2)
                self.screen.blit(txt, (int(x), int(ty)))
                yy += int(row_h + gap)
        except Exception:
            pass

    def _draw_board(self, board, falling_piece, extra_fallers, offset_x=0, offset_y=0, *, draw_fallers_headroom: bool = False):
        # Board cascade tween detection (time-based prev->curr interpolation)
        board_id = id(board)
        is_player_board = (board is self.session.player.get_board())
        runner = self.session.player.chain_runner if is_player_board else (self.session.ai.chain_runner if getattr(self.session, 'ai', None) is not None else None)
        if runner is None:
            step_mode = False
        else:
            step_mode = getattr(runner, 'cascade_mode', 'step') == 'step'

        view_y0, view_h = self._get_board_view(board)
        curr_snap = self._snapshot_board(board, view_y0=view_y0, view_h=view_h)
        last_snap = self._last_board_grid.get(board_id)
        tween = self._cascade_tween.get(board_id)

        # If the view window changed (scroll), disable tweening for this frame.
        try:
            if last_snap is not None and (int(last_snap.get('view_y0', view_y0)) != int(view_y0) or int(last_snap.get('view_h', view_h)) != int(view_h)):
                last_snap = None
                self._cascade_tween.pop(board_id, None)
                tween = None
        except Exception:
            pass

        # Spawn colored explosion sprites for blocks that were cleared/removed.
        try:
            self._spawn_explosions_for_delta(board_id=board_id, last_snap=last_snap, curr_snap=curr_snap, offset_x=int(offset_x), offset_y=int(offset_y))
        except Exception:
            pass

        # Start a new tween when board changes during cascade step mode
        if step_mode and last_snap is not None and curr_snap['cells'] != last_snap['cells']:
            self._cascade_tween[board_id] = {'prev': last_snap, 'start': self._now_ms}
            tween = self._cascade_tween[board_id]
        # Update last snapshot
        self._last_board_grid[board_id] = curr_snap

        # Determine tween phase if active
        phase = 0.0
        if tween is not None:
            elapsed = self._now_ms - tween['start']
            if self.cascade_tween_ms > 0:
                phase = max(0.0, min(1.0, elapsed / float(self.cascade_tween_ms)))
            if phase >= 1.0:
                # Tween complete
                self._cascade_tween.pop(board_id, None)
                tween = None
                phase = 0.0

        moving_ids = set()
        prev_by_id = {}
        if tween is not None:
            prev_by_id = tween['prev']['id_map']
            curr_by_id = curr_snap['id_map']
            for bid, ppos in prev_by_id.items():
                cpos = curr_by_id.get(bid)
                if cpos is not None and cpos != ppos:
                    moving_ids.add(bid)

        # Draw board background under grid
        if self.board_bg is not None:
            self.screen.blit(self.board_bg, (offset_x + MARGIN, offset_y + MARGIN))

        # Pixel-space visible board rect (used for clip + intersection checks).
        # This prevents drawing anything outside the puzzle board, while still
        # allowing smooth-fall offsets to reveal blocks *as they cross* the top edge.
        try:
            board_visible_rect = pygame.Rect(
                int(offset_x + MARGIN),
                int(offset_y + MARGIN),
                int(board.WIDTH) * int(CELL_W),
                int(view_h) * int(CELL_H),
            )
        except Exception:
            board_visible_rect = None

        # Draw grid and cells
        if bool(getattr(self, '_show_grid', False)):
            for y in range(view_h):
                for x in range(board.WIDTH):
                    rect = self._make_cell_rect(x, y, offset_x, offset_y)
                    pygame.draw.rect(self.screen, GRID_LINE, rect, 1)

        # Draw static cells at current positions (exclude moving ids during tween)
        for (x, y), cell in curr_snap['cells'].items():
            bid = id(cell)
            if tween is not None and bid in moving_ids:
                continue
            rect = self._make_cell_rect(x, y, offset_x, offset_y)
            self._draw_block(
                rect,
                cell,
            )

        # Draw moving cells interpolated from previous positions to current
        if tween is not None and moving_ids:
            import math
            # Cosine ease for cascade motion
            eased = (1 - math.cos(phase * math.pi)) * 0.5
            curr_by_id = curr_snap['id_map']
            blocks_map = curr_snap['blocks'] | tween['prev']['blocks']
            for bid in moving_ids:
                (x0, y0) = prev_by_id[bid]
                (x1, y1) = curr_by_id.get(bid, (x0, y0))
                dx = (x1 - x0)
                dy = (y1 - y0)
                rect = self._make_cell_rect(x0, y0, offset_x, offset_y)
                if dx != 0 or dy != 0:
                    rect = rect.move(int(round(dx * CELL_W * eased)), int(round(dy * CELL_H * eased)))
                block = blocks_map.get(bid)
                if block is None:
                    # Fallback if block mapping missing
                    try:
                        block = board.get_piece(int(x1), int(view_y0 + int(y1)))
                    except Exception:
                        block = board.get_piece(int(x0), int(view_y0 + int(y0)))
                self._draw_block(
                    rect,
                    block,
                )
        # Pre-collect occupied integer cells of fallers (non-sword) for visual collision clamp
        faller_occupied = set()
        for g in extra_fallers:
            if hasattr(g, 'horizontal_sword') and g.horizontal_sword:
                continue
            for fx, fy, _ in g.get_block_positions():
                faller_occupied.add((fx, fy))

        # During breaker chains, don't overlay any falling piece on top of board clears
        if board is self.session.player.get_board():
            chain_active = bool(getattr(self.session.player.chain_runner, 'active', False))
        else:
            chain_active = bool(getattr(getattr(self.session, 'ai', None), 'chain_runner', None).active) if getattr(self.session, 'ai', None) is not None else False
        if falling_piece is not None and not chain_active:
            y_off = self._compute_y_offset_pixels(board, falling_piece, is_current_piece=True, faller_occupied=faller_occupied)
            prev_clip = None
            if board_visible_rect is not None:
                try:
                    prev_clip = self.screen.get_clip()
                    self.screen.set_clip(board_visible_rect)
                except Exception:
                    prev_clip = None

            for x, y, block in falling_piece.get_block_positions():
                try:
                    yi = int(y)
                except Exception:
                    continue
                sy = int(yi - int(view_y0))
                rect = self._make_cell_rect(x, sy, offset_x, offset_y)
                if y_off:
                    rect.move_ip(0, int(y_off))
                if board_visible_rect is not None and (not rect.colliderect(board_visible_rect)):
                    continue
                self._draw_block(rect, block)

            if prev_clip is not None:
                try:
                    self.screen.set_clip(prev_clip)
                except Exception:
                    pass

        for g in extra_fallers:
            if hasattr(g, 'horizontal_sword') and g.horizontal_sword:
                self._draw_horizontal_sword(
                    g,
                    offset_x,
                    offset_y,
                    board,
                )
            else:
                y_off = self._compute_y_offset_pixels(board, g, is_current_piece=False, faller_occupied=None, ignore_piece=g)
                prev_clip = None
                if board_visible_rect is not None:
                    try:
                        prev_clip = self.screen.get_clip()
                        self.screen.set_clip(board_visible_rect)
                    except Exception:
                        prev_clip = None
                for x, y, block in g.get_block_positions():
                    try:
                        yi = int(y)
                    except Exception:
                        continue
                    sy = int(yi - int(view_y0))
                    rect = self._make_cell_rect(x, sy, offset_x, offset_y)
                    if y_off:
                        rect.move_ip(0, int(y_off))
                    if board_visible_rect is not None and (not rect.colliderect(board_visible_rect)):
                        continue
                    self._draw_block(rect, block)

                if prev_clip is not None:
                    try:
                        self.screen.set_clip(prev_clip)
                    except Exception:
                        pass

        # Draw any active per-color break explosions on top of the board.
        # (Spawned earlier from snapshot delta; drawn last so it overlays blocks.)
        try:
            self._draw_active_explosions(board_id=int(board_id))
        except Exception:
            pass

    def _draw_block(self, rect, block):
        return self._block_render.draw_block(
            self,
            rect,
            block,
            color_map=COLOR_MAP,
            sprinkle_color=SPRINKLE_COLOR,
            cgarbage_color=CGARBAGE_COLOR,
            garbage_color=GARBAGE_COLOR,
            default_block_color=DEFAULT_BLOCK_COLOR,
        )

    def _draw_breaker_effects(self, base_rect, base_color):
        return self._block_render.draw_breaker_effects(self, base_rect, base_color)

    def _draw_horizontal_sword(self, sword_piece, offset_x, offset_y, board):
        try:
            return self._sword_render.draw_horizontal_sword(self, sword_piece, int(offset_x), int(offset_y), board)
        except Exception:
            return

    def _draw_piece_fallback(self, piece, offset_x, offset_y, board):
        try:
            return self._sword_render.draw_piece_fallback(self, piece, int(offset_x), int(offset_y), board)
        except Exception:
            return

    def _calculate_sword_blocks(self, sword_piece):
        try:
            return self._sword_render.calculate_sword_blocks(sword_piece)
        except Exception:
            return []

    def _draw_sword_blocks(self, sword_blocks, sword_piece, offset_x, offset_y, board):
        try:
            return self._sword_render.draw_sword_blocks(
                self,
                list(sword_blocks or []),
                sword_piece,
                int(offset_x),
                int(offset_y),
                board,
            )
        except Exception:
            return

    def _draw_side_previews(self, snap):
        try:
            self._preview_render.draw_side_previews(
                self,
                snap,
                preview_panel_width=PREVIEW_PANEL_WIDTH,
                preview_scale=PREVIEW_SCALE,
                cell_w=CELL_W,
                cell_h=CELL_H,
                margin=MARGIN,
                preview_label_offset_y=PREVIEW_LABEL_OFFSET_Y,
                preview_piece_offset_y=PREVIEW_PIECE_OFFSET_Y,
            )
        except Exception:
            pass

    def _clamp_preview_piece_center_x(self, piece, desired_center_x: int, panel_rect: pygame.Rect) -> int:
        try:
            return self._preview_render.clamp_preview_piece_center_x(
                self,
                piece,
                int(desired_center_x),
                panel_rect,
                preview_scale=PREVIEW_SCALE,
                cell_w=CELL_W,
                cell_h=CELL_H,
            )
        except Exception:
            return int(panel_rect.centerx)

    def _draw_preview_label(self, center_x, text):
        try:
            self._preview_render.draw_preview_label(
                self,
                int(center_x),
                str(text),
                margin=MARGIN,
                preview_label_offset_y=PREVIEW_LABEL_OFFSET_Y,
            )
        except Exception:
            pass

    def _draw_preview_piece(self, piece, center_x, *, offset: tuple[int, int] = (0, 0)) -> pygame.Rect | None:
        try:
            return self._preview_render.draw_preview_piece(
                self,
                piece,
                int(center_x),
                offset=offset,
                preview_scale=PREVIEW_SCALE,
                cell_w=CELL_W,
                cell_h=CELL_H,
                margin=MARGIN,
                preview_piece_offset_y=PREVIEW_PIECE_OFFSET_Y,
            )
        except Exception:
            return None

    def _draw_preview_sword_next_to_piece(
        self,
        sword_value: str | None,
        piece_rect: pygame.Rect | None,
        panel_rect: pygame.Rect,
        *,
        side: str,
        sword_slot_rect: pygame.Rect | None = None,
    ) -> None:
        try:
            self._preview_render.draw_preview_sword_next_to_piece(
                self,
                sword_value,
                piece_rect,
                panel_rect,
                side=str(side),
                sword_slot_rect=sword_slot_rect,
            )
        except Exception:
            return

    def _get_preview_positions(self, piece):
        try:
            return self._preview_render.get_preview_positions(self, piece)
        except Exception:
            return [(0, 0, piece.blocks[0])]

    def _draw_side_scores(self, snap):
        try:
            return self._score_render.draw_side_scores(self, snap, margin=MARGIN, preview_stats_offset_y=PREVIEW_STATS_OFFSET_Y)
        except Exception:
            return

    def _format_score_lines(self, sdict):
        try:
            return self._score_render.format_score_lines(sdict)
        except Exception:
            return []

    def _blit_score_block(self, lines, center_x):
        try:
            return self._score_render.blit_score_block(
                self,
                list(lines or []),
                int(center_x),
                margin=MARGIN,
                preview_stats_offset_y=PREVIEW_STATS_OFFSET_Y,
            )
        except Exception:
            return


if __name__ == "__main__":
    client = PygameClient()
    try:
        client.run()
    finally:
        try:
            client._persist_volume_preference()
        except Exception:
            pass
        try:
            pygame.quit()
        except Exception:
            pass
