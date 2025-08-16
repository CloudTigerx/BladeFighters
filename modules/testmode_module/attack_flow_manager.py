"""
Attack Flow Manager
Handles attack queuing, routing between players, and chain management.
Extracted from TestMode to separate attack flow logic from game state.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from modules.attack_module.attacks_service import AttacksService


@dataclass
class AttackFlowConfig:
    """Configuration for attack flow behavior."""
    chain_window_duration: int = 302  # ms to continue chain
    attack_receive_pause_ms: int = 400  # pause window for receiving attacks
    max_chain_length: int = 10


@dataclass
class ChainState:
    """State of a player's attack chain."""
    is_active: bool = False
    start_time: int = 0
    length: int = 0
    last_combo_time: int = 0


class AttackFlowManager:
    """Manages attack flow between players and chain state."""
    
    def __init__(self, config: AttackFlowConfig, attacks_service: AttacksService):
        self.config = config
        self.attacks_service = attacks_service
        
        # Attack queues for each player
        self.pending_attacks = {
            'player': [],  # Attacks waiting to spawn above player board
            'enemy': []    # Attacks waiting to spawn above enemy board
        }
        
        # Chain tracking for each player
        self.player_chain = ChainState()
        self.enemy_chain = ChainState()
        
        # Spawn pause tracking
        self.player_spawn_pause_until = 0
        self.enemy_spawn_pause_until = 0
    
    def queue_attack(self, target_player: str, attack_data: Dict[str, Any]):
        """Queue an attack for the specified player."""
        if target_player in self.pending_attacks:
            self.pending_attacks[target_player].append(attack_data)
    
    def get_pending_attacks(self, player: str) -> List[Dict[str, Any]]:
        """Get pending attacks for a player."""
        return self.pending_attacks.get(player, [])
    
    def clear_pending_attacks(self, player: str):
        """Clear all pending attacks for a player."""
        if player in self.pending_attacks:
            self.pending_attacks[player] = []
    
    def start_chain(self, player: str, current_time: int):
        """Start a new chain for the specified player."""
        chain = self.player_chain if player == 'player' else self.enemy_chain
        chain.is_active = True
        chain.start_time = current_time
        chain.length = 0
    
    def end_chain(self, player: str):
        """End the current chain for the specified player."""
        chain = self.player_chain if player == 'player' else self.enemy_chain
        chain.is_active = False
        chain.length = 0
    
    def is_chain_active(self, player: str, current_time: int) -> bool:
        """Check if a player's chain is still active."""
        chain = self.player_chain if player == 'player' else self.enemy_chain
        if not chain.is_active:
            return False
        
        # Check if chain window has expired
        return (current_time - chain.start_time) < self.config.chain_window_duration
    
    def increment_chain(self, player: str, current_time: int):
        """Increment the chain length for a player."""
        chain = self.player_chain if player == 'player' else self.enemy_chain
        if chain.is_active:
            chain.length += 1
            chain.last_combo_time = current_time
    
    def get_chain_length(self, player: str) -> int:
        """Get the current chain length for a player."""
        chain = self.player_chain if player == 'player' else self.enemy_chain
        return chain.length if chain.is_active else 0
    
    def should_pause_spawn(self, player: str, current_time: int) -> bool:
        """Check if spawn should be paused for attack receiving."""
        pause_field = 'player_spawn_pause_until' if player == 'player' else 'enemy_spawn_pause_until'
        pause_until = getattr(self, pause_field, 0)
        return current_time < pause_until
    
    def set_spawn_pause(self, player: str, pause_until: int):
        """Set spawn pause for a player."""
        pause_field = 'player_spawn_pause_until' if player == 'player' else 'enemy_spawn_pause_until'
        current_pause = getattr(self, pause_field, 0)
        setattr(self, pause_field, max(current_pause, pause_until))
    
    def route_attacks(self, from_player: str, to_player: str, attacks: List[Dict[str, Any]] = None):
        """Route attacks from one player to another."""
        if attacks is None:
            # Get all pending attacks from the source player
            attacks = self.pending_attacks.get(from_player, [])
            self.clear_pending_attacks(from_player)
        
        # Add attacks to target player's queue
        for attack in attacks:
            self.queue_attack(to_player, attack)
    
    def get_attack_summary(self) -> Dict[str, Any]:
        """Get a summary of current attack flow state."""
        return {
            'pending_attacks': {
                'player': len(self.pending_attacks['player']),
                'enemy': len(self.pending_attacks['enemy'])
            },
            'chains': {
                'player': {
                    'active': self.player_chain.is_active,
                    'length': self.player_chain.length
                },
                'enemy': {
                    'active': self.enemy_chain.is_active,
                    'length': self.enemy_chain.length
                }
            },
            'spawn_pauses': {
                'player': self.player_spawn_pause_until,
                'enemy': self.enemy_spawn_pause_until
            }
        } 