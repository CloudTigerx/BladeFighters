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

    def calculate_cluster_strike(self, cluster_type: str, combo_level: int):
        """
        Compute sword dimensions per Vertical Swords spec.

        Rules implemented:
        - Vertical or square gems produce vertical swords.
          - 2x2 → 1x4
          - 3x3 → 2x4
          - For general vertical (height > width):
            width = min(width, 3); if width > 3 fold extras into length
            length starts as height, then multiply by combo.
          - For squares (N x N): width = min(N-1, 3); length = 4; then apply width folding if N-1 > 3; finally multiply length by combo.
        - Horizontal handling is deferred to the horizontal placement system; for now we
          keep horizontal as-is (no conversion here) so downstream placement can decide.
        Returns (pattern, width, height) where height is vertical length.
        Pattern suffixes: "_vertical" or "_horizontal" for clarity.
        """
        try:
            width_str, height_str = cluster_type.lower().split('x')
            base_width = int(width_str)
            base_height = int(height_str)
        except Exception:
            base_width, base_height = 2, 2

        combo = max(1, int(combo_level))

        # Square or vertical → vertical sword
        if base_height >= base_width:
            if base_height == base_width:
                # Square mapping special cases per spec
                # 2x2 → 1x4 (then multiply sword length by combo)
                n = base_width
                if n == 2:
                    # 2x2 mapping per requested table:
                    # 1x: 1x4
                    # 2x: 2x4
                    # 3x: 2x6
                    # 4x: 2x8
                    # 5x: 2x10
                    # 6x: 2x12
                    if combo <= 1:
                        width = 1
                        length = 4
                    else:
                        width = 2
                        length = min(12, 2 * combo)
                # 3x3 → 2x4 (then multiply sword length by combo)
                elif n == 3:
                    width = 2
                    length = max(1, 4 * combo)
                else:
                    # General square mapping: (min(N-1,3))×4, fold excess width into length, then multiply by combo
                    width = max(2, min(n - 1, 3))
                    length = 4
                    if (n - 1) > 3:
                        length += (n - 1) - 3
                    length = max(1, length * combo)
            else:
                # Proper vertical mapping
                width = max(2, min(base_width, 3))
                # Fold any excess width above 3 into length
                extra_width = max(0, base_width - 3)
                length = max(1, base_height + extra_width)
                # Multiply length by combo
                length = max(1, length * combo)

            # Do not cap length here; placement will truncate/waste as needed
            pattern = f"{width}x{length}_vertical"
            return pattern, width, length

        # Horizontal gem (wider than tall): retain as horizontal for downstream handling
        # Key rule: do NOT fold 4x2 into two 2x2s. Keep 4x2 horizontal (rows_tall=2, length=4).
        horiz_width_rows = max(2, min(base_height, 3))
        # Folding rule applies only when rows_tall would exceed 3. For base_height<=3 keep length as base_width.
        horizontal_length = base_width if base_height <= 3 else base_width + (base_height - 3)
        horizontal_length = max(1, horizontal_length * combo)

        pattern = f"{horiz_width_rows}x{horizontal_length}_horizontal"
        # Return width as rows (vertical thickness) and height as horizontal length for consistency
        return pattern, horiz_width_rows, horizontal_length
    
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