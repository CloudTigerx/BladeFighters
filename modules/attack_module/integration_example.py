"""
Integration Example

Shows how to integrate the simple attack system with existing code.
"""

from .simple_attack_system import SimpleAttackSystem


class AttackIntegrationExample:
    """
    Example of how to integrate the simple attack system.
    
    This shows how to add the attack system to your existing PuzzleEngine
    without major changes to your codebase.
    """
    
    def __init__(self):
        """Initialize the attack integration."""
        self.attack_system = SimpleAttackSystem(grid_width=6)
        self.current_chain_position = 0
        self.chain_window_active = False
        self.chain_window_duration = 2000  # 2 seconds to continue chain
    
    def on_blocks_broken(self, broken_blocks, is_cluster, combo_multiplier):
        """
        Called when blocks are broken in the puzzle engine.
        
        This is the main integration point with your existing code.
        
        Args:
            broken_blocks: List of (x, y, block_type) tuples
            is_cluster: Whether this was a cluster break
            combo_multiplier: Current combo multiplier
        """
        # Detect clusters in the broken blocks
        clusters = self.attack_system.detect_clusters(broken_blocks)
        
        # Determine chain position
        if not self.chain_window_active:
            # Start new chain
            self.current_chain_position = 1
            self.chain_window_active = True
        else:
            # Continue existing chain
            self.current_chain_position += 1
        
        # Process the combo and generate attacks
        new_attacks = self.attack_system.process_combo(
            broken_blocks, clusters, self.current_chain_position
        )
        
        # Get attack summary for display
        attack_summary = self.attack_system.get_attack_summary()
        
        # Log the attack generation
        print(f"Chain {self.current_chain_position}x: {attack_summary}")
        
        # Return attacks for further processing
        return new_attacks
    
    def on_chain_end(self):
        """
        Called when the chain window expires.
        
        This should be called after a delay when no more combos occur.
        """
        self.chain_window_active = False
        self.current_chain_position = 0
        
        # Get final attack summary
        final_attacks = self.attack_system.get_pending_attacks()
        if final_attacks:
            print(f"Final attack: {self.attack_system.get_attack_summary()}")
        
        return final_attacks
    
    def send_attacks_to_opponent(self, opponent_attack_system):
        """
        Send pending attacks to opponent.
        
        Args:
            opponent_attack_system: Attack system of the opponent
        """
        attacks = self.attack_system.get_pending_attacks()
        
        # Here you would apply the attacks to the opponent's grid
        # This is where you'd integrate with your existing attack system
        
        # Clear the attacks after sending
        self.attack_system.clear_attacks()
        
        return attacks


# Example usage in your existing code:
"""
# In your PuzzleEngine or TestMode:

# 1. Initialize the attack system
attack_integration = AttackIntegrationExample()

# 2. In your existing block breaking handler:
def handle_player_blocks_broken(self, broken_blocks, is_cluster, combo_multiplier):
    # Your existing logic...
    
    # Add attack system integration
    new_attacks = attack_integration.on_blocks_broken(
        broken_blocks, is_cluster, combo_multiplier
    )
    
    # Display attack information
    attack_summary = attack_integration.attack_system.get_attack_summary()
    print(f"Attack: {attack_summary}")

# 3. When chain ends (after delay):
def on_chain_timeout(self):
    final_attacks = attack_integration.on_chain_end()
    
    # Send attacks to opponent
    if final_attacks:
        self.send_attacks_to_opponent(opponent_attack_system)

# 4. Send attacks to opponent:
def send_attacks_to_opponent(self, opponent_attack_system):
    attacks = attack_integration.send_attacks_to_opponent(opponent_attack_system)
    
    # Apply attacks to opponent's grid
    for attack in attacks:
        self.apply_attack_to_grid(attack, opponent_grid)
""" 