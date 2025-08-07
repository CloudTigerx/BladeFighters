"""
Simple Attack System

A simplified attack system that rewards chaining attacks without complexity.
"""

from .attack_calculator import AttackCalculator
from .column_rotator import ColumnRotator
from .attack_database import AttackCombo, AttackDatabase


class AttackData:
    """Represents a single attack to be sent to an opponent."""
    
    def __init__(self, attack_type, count, chain_multiplier, target_column=None):
        self.attack_type = attack_type  # "garbage" or "strike"
        self.count = count
        self.chain_multiplier = chain_multiplier
        self.target_column = target_column  # Set by column rotator
        self.creation_time = None  # Set when attack is created
        self.strike_details = []  # List of strike dimensions (e.g., ["1x4", "3x2"])
        
    def __str__(self):
        if self.attack_type == "strike" and self.strike_details:
            strike_str = " + ".join(self.strike_details)
            return f"{strike_str} at {self.chain_multiplier}x"
        else:
            return f"{self.count} {self.attack_type}(s) at {self.chain_multiplier}x"


class ComboData:
    """Represents combo data for attack calculation."""
    
    def __init__(self, broken_blocks, clusters, chain_position):
        self.broken_blocks = broken_blocks
        self.clusters = clusters  # List of cluster sizes
        self.chain_position = chain_position  # 1, 2, 3, etc.


class SimpleAttackSystem:
    """Main attack system that handles attack generation and management."""
    
    def __init__(self, grid_width: int = 6, max_chain_multiplier: int = 10):
        """Initialize the simple attack system."""
        self.grid_width = grid_width
        self.max_chain_multiplier = max_chain_multiplier
        self.pending_attacks = []
        
        # Initialize components
        self.calculator = AttackCalculator()
        self.column_rotator = ColumnRotator(grid_width)
        
        # Initialize attack database (optional)
        self.attack_database = None
        self.use_database = False
    
    def enable_database(self, database_path: str = "attack_database.json"):
        """Enable the attack database for lookups."""
        print(f"🔧 ENABLING DATABASE: {database_path}")
        try:
            self.attack_database = AttackDatabase(database_path)
            self.use_database = True
            print(f"✅ Attack database enabled: {database_path}")
            
            # Show database statistics
            stats = self.attack_database.get_statistics()
            print(f"📊 Database loaded: {stats['total_rules']} rules")
            
        except Exception as e:
            print(f"❌ Failed to enable attack database: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
            self.use_database = False
    
    def disable_database(self):
        """Disable the attack database (use fallback calculations)."""
        self.use_database = False
        self.attack_database = None
        print("🔄 Attack database disabled - using fallback calculations")
    
    def process_combo(self, broken_blocks, clusters, chain_position):
        """
        Process a combo and generate attacks.
        
        NEW LOGIC:
        - Clusters generate strikes (not garbage blocks)
        - Individual blocks (non-cluster, non-breaker) generate garbage blocks
        - Breakers don't count towards attack output
        - Mixed combos generate both strikes AND garbage blocks
        
        Args:
            broken_blocks: List of (x, y, block_type) tuples
            clusters: List of cluster sizes (e.g., [4, 4, 6] for 2x2, 2x2, 2x3)
            chain_position: Position in chain (1, 2, 3, etc.)
        """
        # Cap chain multiplier
        chain_multiplier = min(chain_position, self.max_chain_multiplier)
        
        print(f"🔧 PROCESS_COMBO DEBUG:")
        print(f"   Input clusters: {clusters}")
        print(f"   Chain position: {chain_position}")
        print(f"   Chain multiplier (capped): {chain_multiplier}")
        
        # STEP 1: Separate blocks into categories
        cluster_blocks, individual_blocks, breaker_blocks = self._categorize_blocks(broken_blocks, clusters)
        
        print(f"🎯 BLOCK CATEGORIZATION:")
        print(f"   Cluster blocks: {len(cluster_blocks)} (generate strikes)")
        print(f"   Individual blocks: {len(individual_blocks)} (generate garbage)")
        print(f"   Breaker blocks: {len(breaker_blocks)} (no attack output)")
        
        # NEW: Use attack database for lookup
        combo = AttackCombo(
            cluster_sizes=clusters,
            individual_blocks=len(individual_blocks),
            breaker_blocks=len(breaker_blocks),
            chain_multiplier=chain_multiplier
        )
        
        print(f"🔍 ATTACK COMBO CREATED:")
        print(f"   Cluster sizes: {combo.cluster_sizes}")
        print(f"   Individual blocks: {combo.individual_blocks}")
        print(f"   Breaker blocks: {combo.breaker_blocks}")
        print(f"   Chain multiplier: {combo.chain_multiplier}")
        
        # Try to get attack output from database
        if self.use_database and self.attack_database:
            print(f"🔍 ATTEMPTING DATABASE LOOKUP...")
            
            # Generate the database key
            db_key = self.attack_database.get_attack_key(combo)
            print(f"🔍 DATABASE KEY: {db_key}")
            
            # Look up the attack output
            output = self.attack_database.calculate_attack_output(combo)
            print(f"🎯 DATABASE LOOKUP: {combo} → {output}")
            print(f"   Strikes: {output.strikes}")
            print(f"   Garbage blocks: {output.garbage_blocks}")
            print(f"   Strike details: {output.strike_details}")
            print(f"   Total damage: {output.total_damage}")
            
            # Generate attacks based on database output
            if output.strikes > 0:
                # Create strike details string
                strike_details_str = " + ".join(output.strike_details) if output.strike_details else f"{output.strikes} strikes"
                
                strike_attack = AttackData(
                    attack_type="strike",
                    count=output.strikes,
                    chain_multiplier=chain_multiplier,
                    target_column=self.column_rotator.get_next_column()
                )
                # Add strike details to the attack data
                strike_attack.strike_details = output.strike_details
                self.pending_attacks.append(strike_attack)
                print(f"   Generated {strike_details_str} from database")
            
            if output.garbage_blocks > 0:
                garbage_attack = AttackData(
                    attack_type="garbage",
                    count=output.garbage_blocks,
                    chain_multiplier=chain_multiplier,
                    target_column=self.column_rotator.get_next_column()
                )
                self.pending_attacks.append(garbage_attack)
                print(f"   Generated {output.garbage_blocks} garbage blocks from database")
            
            return self.pending_attacks[-len(broken_blocks):]  # Return new attacks
        
        # FALLBACK: Original calculation logic (if no database)
        print(f"🎯 FALLBACK CALCULATION (database disabled or not found):")
        print(f"   use_database={self.use_database}")
        print(f"   attack_database exists={self.attack_database is not None}")
        
        # STEP 2: Generate strikes from clusters using corrected calculator
        for cluster_size in clusters:
            strike_count = self.calculator.calculate_strike_attack(
                cluster_size, chain_multiplier
            )
            
            if strike_count > 0:
                strike_attack = AttackData(
                    attack_type="strike",
                    count=strike_count,
                    chain_multiplier=chain_multiplier,
                    target_column=self.column_rotator.get_next_column()
                )
                self.pending_attacks.append(strike_attack)
                print(f"   Generated {strike_count} strikes from {cluster_size}-block cluster")
        
        # STEP 3: Generate garbage blocks from individual blocks using corrected calculator
        if individual_blocks:
            # Calculate effective individual blocks (minus breakers)
            breaker_count = len(breaker_blocks)
            effective_individual = max(0, len(individual_blocks) - breaker_count)
            
            if effective_individual > 0:
                # Use corrected calculator: (blocks × combo) ÷ 2
                garbage_count = self.calculator.calculate_garbage_attack(
                    effective_individual, chain_multiplier
                )
                
                if garbage_count > 0:
                    garbage_attack = AttackData(
                        attack_type="garbage",
                        count=garbage_count,
                        chain_multiplier=chain_multiplier,
                        target_column=self.column_rotator.get_next_column()
                    )
                    self.pending_attacks.append(garbage_attack)
                    print(f"   Generated {garbage_count} garbage blocks using formula: ({effective_individual} × {chain_multiplier}) ÷ 2")
                else:
                    print(f"   No garbage blocks generated (formula result was 0)")
            else:
                print(f"   No garbage blocks generated (all individual blocks were breakers)")
        
        return self.pending_attacks[-len(broken_blocks):]  # Return new attacks
    
    def get_pending_attacks(self):
        """Get all pending attacks."""
        return self.pending_attacks.copy()
    
    def clear_attacks(self):
        """Clear all pending attacks (when they're sent to opponent)."""
        self.pending_attacks.clear()
    
    def get_attack_summary(self):
        """Get a summary of pending attacks for display."""
        if not self.pending_attacks:
            return "No attacks pending"
        
        summary_parts = []
        
        # Group strikes by their details
        strike_groups = {}
        for attack in self.pending_attacks:
            if attack.attack_type == "strike":
                if hasattr(attack, 'strike_details') and attack.strike_details:
                    strike_key = " + ".join(attack.strike_details)
                    strike_groups[strike_key] = strike_groups.get(strike_key, 0) + attack.count
                else:
                    strike_groups["strikes"] = strike_groups.get("strikes", 0) + attack.count
        
        # Add strikes to summary
        for strike_desc, count in strike_groups.items():
            if strike_desc == "strikes":
                summary_parts.append(f"{count} strikes")
            else:
                summary_parts.append(f"{count}x {strike_desc}")
        
        # Add garbage blocks
        garbage_count = sum(a.count for a in self.pending_attacks if a.attack_type == "garbage")
        if garbage_count > 0:
            summary_parts.append(f"{garbage_count} garbage blocks")
        
        return " + ".join(summary_parts)
    
    def detect_clusters(self, broken_blocks):
        """
        Strict cluster detection - only detects proper cluster formations.
        
        Args:
            broken_blocks: List of (x, y, block_type) tuples
            
        Returns:
            List of cluster sizes
        """
        if not broken_blocks:
            return []
        
        # Group blocks by color
        color_groups = {}
        for x, y, block_type in broken_blocks:
            if block_type not in color_groups:
                color_groups[block_type] = []
            color_groups[block_type].append((x, y))
        
        clusters = []
        
        # For each color group, find connected components
        for block_type, positions in color_groups.items():
            if len(positions) >= 4:  # Minimum cluster size
                # Find connected components
                connected_groups = self._find_connected_components(positions)
                
                for group in connected_groups:
                    if len(group) >= 4:  # Only count as cluster if 4+ blocks
                        # Check if this group forms a proper cluster shape
                        if self._is_proper_cluster_shape(group):
                            clusters.append(len(group))
        
        return clusters
    
    def _is_proper_cluster_shape(self, positions):
        """
        Check if a group of positions forms a proper cluster shape.
        A proper cluster must be a 2x2 or larger rectangular formation.
        
        Args:
            positions: List of (x, y) tuples
            
        Returns:
            True if it forms a proper cluster shape
        """
        if len(positions) < 4:
            return False
        
        # Get the bounding box
        x_coords = [x for x, y in positions]
        y_coords = [y for x, y in positions]
        min_x, max_x = min(x_coords), max(x_coords)
        min_y, max_y = min(y_coords), max(y_coords)
        
        width = max_x - min_x + 1
        height = max_y - min_y + 1
        
        # CLUSTER RULES:
        # 1. Must be at least 2x2 (width >= 2 AND height >= 2)
        # 2. Must not be just a line (both width and height must be >= 2)
        # 3. Must have reasonable density (at least 70% for small clusters, 60% for larger ones)
        
        if width < 2 or height < 2:
            return False  # Not a proper cluster - too narrow or short
        
        # Additional check: ensure it's not just a line
        if width == 1 or height == 1:
            return False  # This is just a line, not a cluster
        
        area = width * height
        block_count = len(positions)
        density = block_count / area
        
        # Adjust density requirements based on cluster size
        if area <= 6:  # Small clusters (2x2, 2x3, 3x2)
            min_density = 0.7  # 70% for small clusters
        else:  # Larger clusters
            min_density = 0.6  # 60% for larger clusters
        
        if density < min_density:
            return False
        
        return True
    
    def _find_connected_components(self, positions):
        """
        Find connected components in a set of positions.
        
        Args:
            positions: List of (x, y) tuples
            
        Returns:
            List of connected component lists
        """
        if not positions:
            return []
        
        visited = set()
        components = []
        
        for pos in positions:
            if pos not in visited:
                component = []
                self._dfs(pos, positions, visited, component)
                components.append(component)
        
        return components
    
    def _dfs(self, pos, all_positions, visited, component):
        """Depth-first search to find connected components."""
        if pos in visited:
            return
        
        visited.add(pos)
        component.append(pos)
        
        x, y = pos
        # Check 4 adjacent positions
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            neighbor = (x + dx, y + dy)
            if neighbor in all_positions:
                self._dfs(neighbor, all_positions, visited, component) 

    def _categorize_blocks(self, broken_blocks, clusters):
        """
        Categorize broken blocks into clusters, individual blocks, and breakers.
        
        Args:
            broken_blocks: List of (x, y, block_type) tuples
            clusters: List of cluster sizes
            
        Returns:
            Tuple of (cluster_blocks, individual_blocks, breaker_blocks)
        """
        if not broken_blocks:
            return [], [], []
        
        # If no clusters detected, all blocks are individual (except breakers)
        if not clusters:
            cluster_blocks = []
            individual_blocks = []
            breaker_blocks = []
            
            for x, y, block_type in broken_blocks:
                if '_breaker' in block_type:
                    breaker_blocks.append((x, y, block_type))
                else:
                    individual_blocks.append((x, y, block_type))
            
            return cluster_blocks, individual_blocks, breaker_blocks
        
        # If clusters were detected, we need to identify which blocks are part of clusters
        cluster_blocks = []
        individual_blocks = []
        breaker_blocks = []
        
        # Group blocks by color for cluster detection
        color_groups = {}
        for x, y, block_type in broken_blocks:
            if block_type not in color_groups:
                color_groups[block_type] = []
            color_groups[block_type].append((x, y))
        
        # Find connected components for each color group
        cluster_positions = set()
        for block_type, positions in color_groups.items():
            if len(positions) >= 4:  # Minimum cluster size
                connected_groups = self._find_connected_components(positions)
                
                for group in connected_groups:
                    if len(group) >= 4:  # Only count as cluster if 4+ blocks
                        # Add all blocks in this cluster to cluster_positions set
                        for pos in group:
                            cluster_positions.add(pos)
        
        # Now categorize each broken block
        for x, y, block_type in broken_blocks:
            pos = (x, y)
            
            # Check if it's a breaker (exclude from attack output)
            if '_breaker' in block_type:
                breaker_blocks.append((x, y, block_type))
            # Check if it's part of a cluster
            elif pos in cluster_positions:
                # This block is part of a cluster - add to cluster_blocks
                cluster_blocks.append((x, y, block_type))
            # Otherwise it's an individual block
            else:
                individual_blocks.append((x, y, block_type))
        
        return cluster_blocks, individual_blocks, breaker_blocks 