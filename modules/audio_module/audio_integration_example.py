"""
Audio Integration Example
Demonstrates how to integrate the audio system with state management
and coordinate with the settings module.
"""

import pygame
import sys
import os
from typing import Dict, Any

# Add the project root to the path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from modules.game_state_module.game_state_manager import GameStateManager
from modules.audio_module.audio_system import AudioSystem
from modules.audio_module.audio_integration import AudioStateIntegrator


class AudioSystemWithStateIntegration:
    """
    Example audio system with full state management integration.
    Demonstrates the complete integration pattern for audio state management.
    """
    
    def __init__(self, screen, font, asset_path="puzzleassets", state_manager=None):
        """Initialize the audio system with state integration."""
        self.screen = screen
        self.font = font
        self.asset_path = asset_path
        
        # Initialize state manager if not provided
        if state_manager is None:
            self.state_manager = GameStateManager()
        else:
            self.state_manager = state_manager
        
        # Initialize audio system
        self.audio_system = AudioSystem(
            root_path=".",
            asset_path=asset_path,
            state_manager=self.state_manager
        )
        
        # Initialize state integrator
        self.state_integrator = AudioStateIntegrator(self.state_manager, self.audio_system)
        
        # Start integration
        self.state_integrator.start_integration()
        self.state_integrator.register_state_callbacks()
        
        # Initialize UI state
        self.volume_sliders = {
            "master": {"value": 0.7, "rect": pygame.Rect(50, 100, 200, 20)},
            "music": {"value": 0.6, "rect": pygame.Rect(50, 150, 200, 20)},
            "sfx": {"value": 0.8, "rect": pygame.Rect(50, 200, 200, 20)}
        }
        
        # Initialize buttons
        self.buttons = {
            "play_sound": {"text": "Play Click", "rect": pygame.Rect(50, 250, 120, 30)},
            "play_music": {"text": "Toggle Music", "rect": pygame.Rect(180, 250, 120, 30)},
            "reset": {"text": "Reset Audio", "rect": pygame.Rect(50, 300, 120, 30)},
            "show_mp3": {"text": "Show MP3", "rect": pygame.Rect(180, 300, 120, 30)}
        }
        
        # Sync initial state
        self._sync_volume_sliders()
        
        print("Audio system with state integration initialized")
    
    def _sync_volume_sliders(self):
        """Sync volume sliders with current state."""
        self.volume_sliders["master"]["value"] = self.state_integrator.get_master_volume()
        self.volume_sliders["music"]["value"] = self.state_integrator.get_music_volume()
        self.volume_sliders["sfx"]["value"] = self.state_integrator.get_sfx_volume()
    
    def update(self):
        """Update the audio system and state integration."""
        # Sync state to state manager
        self.state_integrator.sync_to_state_manager()
        
        # Sync from state manager (for changes from other sources)
        self.state_integrator.sync_from_state_manager()
        
        # Update volume sliders
        self._sync_volume_sliders()
    
    def handle_events(self, events):
        """Handle pygame events for audio controls."""
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left click
                    self._handle_mouse_click(event.pos)
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left click release
                    self._handle_mouse_release()
            
            elif event.type == pygame.MOUSEMOTION:
                self._handle_mouse_motion(event.pos)
    
    def _handle_mouse_click(self, pos):
        """Handle mouse click events."""
        # Check volume sliders
        for slider_name, slider in self.volume_sliders.items():
            if slider["rect"].collidepoint(pos):
                self._update_slider_value(slider_name, pos[0])
                return
        
        # Check buttons
        for button_name, button in self.buttons.items():
            if button["rect"].collidepoint(pos):
                self._handle_button_click(button_name)
                return
    
    def _handle_mouse_release(self):
        """Handle mouse release events."""
        # Could add drag end logic here
        pass
    
    def _handle_mouse_motion(self, pos):
        """Handle mouse motion events."""
        # Check if dragging volume sliders
        for slider_name, slider in self.volume_sliders.items():
            if slider["rect"].collidepoint(pos):
                if pygame.mouse.get_pressed()[0]:  # Left mouse button pressed
                    self._update_slider_value(slider_name, pos[0])
                    return
    
    def _update_slider_value(self, slider_name, x_pos):
        """Update slider value based on mouse position."""
        slider = self.volume_sliders[slider_name]
        slider_rect = slider["rect"]
        
        # Calculate value based on mouse position
        relative_x = max(0, min(1, (x_pos - slider_rect.x) / slider_rect.width))
        new_value = round(relative_x, 2)
        
        # Update slider and state
        slider["value"] = new_value
        
        # Update state through integrator
        if slider_name == "master":
            self.state_integrator.set_master_volume(new_value)
        elif slider_name == "music":
            self.state_integrator.set_music_volume(new_value)
        elif slider_name == "sfx":
            self.state_integrator.set_sfx_volume(new_value)
    
    def _handle_button_click(self, button_name):
        """Handle button click events."""
        if button_name == "play_sound":
            self.state_integrator.play_sound("click")
            print("Playing click sound")
        
        elif button_name == "play_music":
            if self.state_integrator.is_music_playing():
                self.state_integrator.set_music_playing(False)
                print("Music stopped")
            else:
                self.state_integrator.play_music("music")
                print("Music started")
        
        elif button_name == "reset":
            self.state_integrator.reset_audio_state()
            self._sync_volume_sliders()
            print("Audio state reset")
        
        elif button_name == "show_mp3":
            current_visible = self.state_integrator.is_mp3_player_visible()
            self.state_integrator.set_mp3_player_visible(not current_visible)
            print(f"MP3 player {'shown' if not current_visible else 'hidden'}")
    
    def draw(self):
        """Draw the audio control interface."""
        # Draw title
        title_text = self.font.render("Audio State Integration Demo", True, (255, 255, 255))
        self.screen.blit(title_text, (50, 50))
        
        # Draw volume sliders
        for slider_name, slider in self.volume_sliders.items():
            # Draw slider background
            pygame.draw.rect(self.screen, (100, 100, 100), slider["rect"])
            
            # Draw slider value
            value_rect = pygame.Rect(
                slider["rect"].x,
                slider["rect"].y,
                int(slider["rect"].width * slider["value"]),
                slider["rect"].height
            )
            pygame.draw.rect(self.screen, (0, 255, 0), value_rect)
            
            # Draw slider border
            pygame.draw.rect(self.screen, (255, 255, 255), slider["rect"], 2)
            
            # Draw label
            label_text = self.font.render(f"{slider_name.title()}: {slider['value']:.2f}", True, (255, 255, 255))
            self.screen.blit(label_text, (slider["rect"].x, slider["rect"].y - 25))
        
        # Draw buttons
        for button_name, button in self.buttons.items():
            # Draw button background
            pygame.draw.rect(self.screen, (50, 50, 50), button["rect"])
            pygame.draw.rect(self.screen, (255, 255, 255), button["rect"], 2)
            
            # Draw button text
            text = self.font.render(button["text"], True, (255, 255, 255))
            text_rect = text.get_rect(center=button["rect"].center)
            self.screen.blit(text, text_rect)
        
        # Draw state information
        self._draw_state_info()
    
    def _draw_state_info(self):
        """Draw current state information."""
        y_offset = 350
        
        # Get state summary
        state_summary = self.state_integrator.get_audio_state_summary()
        
        # Draw state info
        info_lines = [
            f"Master Volume: {state_summary['master_volume']:.2f}",
            f"Music Volume: {state_summary['music_volume']:.2f}",
            f"SFX Volume: {state_summary['sfx_volume']:.2f}",
            f"Music Enabled: {state_summary['music_enabled']}",
            f"SFX Enabled: {state_summary['sfx_enabled']}",
            f"MP3 Player Visible: {state_summary['mp3_player_visible']}",
            f"Music Playing: {state_summary['music_playing']}",
            f"Current Music: {state_summary['current_music'] or 'None'}",
            f"Sounds Played: {state_summary['sounds_played']}",
            f"Music Tracks Played: {state_summary['music_tracks_played']}",
            f"Volume Changes: {state_summary['volume_changes']}"
        ]
        
        for i, line in enumerate(info_lines):
            text = self.font.render(line, True, (200, 200, 200))
            self.screen.blit(text, (50, y_offset + i * 20))
    
    def get_audio_state(self) -> Dict[str, Any]:
        """Get current audio state for external access."""
        return self.state_integrator.get_audio_state_summary()
    
    def set_audio_state(self, state_dict: Dict[str, Any]):
        """Set audio state from external source (e.g., settings module)."""
        if "master_volume" in state_dict:
            self.state_integrator.set_master_volume(state_dict["master_volume"])
        if "music_volume" in state_dict:
            self.state_integrator.set_music_volume(state_dict["music_volume"])
        if "sfx_volume" in state_dict:
            self.state_integrator.set_sfx_volume(state_dict["sfx_volume"])
        if "music_enabled" in state_dict:
            self.state_integrator.set_music_enabled(state_dict["music_enabled"])
        if "sfx_enabled" in state_dict:
            self.state_integrator.set_sfx_enabled(state_dict["sfx_enabled"])
    
    def sync_with_settings(self, settings_dict: Dict[str, Any]):
        """Sync with settings module configuration."""
        self.state_integrator.sync_with_settings_module(settings_dict)
    
    def get_settings_dict(self) -> Dict[str, Any]:
        """Get audio state as settings dictionary."""
        return self.state_integrator.get_settings_dict()


def main():
    """Main function to demonstrate audio integration."""
    # Initialize Pygame
    pygame.init()
    
    # Set up display
    screen_width, screen_height = 800, 600
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("Audio State Integration Demo")
    
    # Set up font
    font = pygame.font.SysFont(None, 24)
    
    # Initialize audio system with state integration
    audio_demo = AudioSystemWithStateIntegration(screen, font)
    
    # Game loop
    clock = pygame.time.Clock()
    running = True
    
    print("Audio State Integration Demo")
    print("Controls:")
    print("- Drag volume sliders to adjust volume")
    print("- Click 'Play Click' to play a sound effect")
    print("- Click 'Toggle Music' to start/stop music")
    print("- Click 'Reset Audio' to reset all settings")
    print("- Click 'Show MP3' to toggle MP3 player visibility")
    print("- Press ESC to exit")
    
    while running:
        # Handle events
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_SPACE:
                    # Play sound on spacebar
                    audio_demo.state_integrator.play_sound("click")
        
        # Handle audio events
        audio_demo.handle_events(events)
        
        # Update audio system
        audio_demo.update()
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw audio interface
        audio_demo.draw()
        
        # Update display
        pygame.display.flip()
        
        # Cap frame rate
        clock.tick(60)
    
    # Cleanup
    pygame.quit()
    print("Audio State Integration Demo completed")


if __name__ == "__main__":
    main()
