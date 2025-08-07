"""
Attack Calculator

Simple mathematical formulas for calculating attack strength.
"""


class AttackCalculator:
    """Calculates attack strength based on simple formulas."""
    
    def __init__(self):
        self.min_strike_size = 4  # Minimum blocks for a strike
        self.strike_ratio = 4  # 4 blocks = 1 strike
    
    def calculate_garbage_attack(self, broken_blocks, chain_multiplier):
        """
        Calculate garbage blocks to send.
        
        Args:
            broken_blocks: Number of blocks broken
            chain_multiplier: Chain multiplier (1, 2, 3, etc.)
            
        Returns:
            Number of garbage blocks to send
        """
        # Justin's formula: (blocks × combo) ÷ 2
        return (broken_blocks * chain_multiplier) // 2
    
    def calculate_strike_attack(self, cluster_size, chain_multiplier):
        """
        Calculate strikes to send based on cluster size and combo multiplier.
        
        Justin's formula: strikes = cluster_size × combo
        
        Args:
            cluster_size: Size of cluster broken (e.g., 4 for 2x2, 9 for 3x3)
            chain_multiplier: Chain multiplier (1, 2, 3, etc.)
            
        Returns:
            Number of strikes to send
        """
        if cluster_size < self.min_strike_size:
            return 0
        
        # Justin's formula: strikes = cluster_size × combo
        total_strikes = cluster_size * chain_multiplier
        
        # Return the calculated strikes
        return total_strikes
    
    def calculate_total_damage(self, broken_blocks, clusters, chain_multiplier):
        """
        Calculate total damage from a combo.
        
        Args:
            broken_blocks: Number of blocks broken
            clusters: List of cluster sizes
            chain_multiplier: Chain multiplier
            
        Returns:
            Tuple of (garbage_blocks, strikes)
        """
        garbage = self.calculate_garbage_attack(broken_blocks, chain_multiplier)
        strikes = sum(self.calculate_strike_attack(size, chain_multiplier) for size in clusters)
        
        return garbage, strikes
    
    def get_attack_description(self, broken_blocks, clusters, chain_multiplier):
        """
        Get a human-readable description of the attack.
        
        Args:
            broken_blocks: Number of blocks broken
            clusters: List of cluster sizes
            chain_multiplier: Chain multiplier
            
        Returns:
            String description of the attack
        """
        garbage, strikes = self.calculate_total_damage(broken_blocks, clusters, chain_multiplier)
        
        parts = []
        if garbage > 0:
            parts.append(f"{garbage} garbage blocks")
        if strikes > 0:
            parts.append(f"{strikes} strikes")
        
        if not parts:
            return "No attack"
        
        return " + ".join(parts)
    
    def get_chain_multiplier_text(self, chain_multiplier):
        """
        Get text representation of chain multiplier.
        
        Args:
            chain_multiplier: Chain multiplier (1, 2, 3, etc.)
            
        Returns:
            String like "1x", "2x", "3x", etc.
        """
        return f"{chain_multiplier}x"
    
    def is_significant_attack(self, broken_blocks, clusters, chain_multiplier):
        """
        Determine if this is a significant attack worth highlighting.
        
        Args:
            broken_blocks: Number of blocks broken
            clusters: List of cluster sizes
            chain_multiplier: Chain multiplier
            
        Returns:
            True if attack is significant
        """
        garbage, strikes = self.calculate_total_damage(broken_blocks, clusters, chain_multiplier)
        
        # Significant if:
        # - High chain multiplier (3x or higher)
        # - Large attack (5+ total damage)
        # - Contains strikes
        return (chain_multiplier >= 3 or 
                (garbage + strikes) >= 5 or 
                strikes > 0) 