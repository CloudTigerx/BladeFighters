#!/usr/bin/env python3
"""
Attack Database System

A comprehensive lookup table that maps all possible block combinations
to their attack outputs. This allows for predictable, balanced attacks
and easy pattern recognition.
"""

from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
import json
import os


@dataclass
class AttackCombo:
    """Represents a specific combination of broken blocks."""
    cluster_sizes: List[int]  # e.g., [4, 6] for 4-block and 6-block clusters
    individual_blocks: int    # Number of individual (non-cluster) blocks
    breaker_blocks: int       # Number of breaker blocks
    chain_multiplier: int     # Chain position (1x, 2x, 3x, etc.)
    
    def __str__(self):
        clusters_str = f"clusters:{self.cluster_sizes}" if self.cluster_sizes else "no_clusters"
        return f"{clusters_str}+{self.individual_blocks}ind+{self.breaker_blocks}breakers@{self.chain_multiplier}x"


@dataclass
class AttackOutput:
    """Represents the attack output for a specific combo."""
    strikes: int              # Number of strikes to send
    garbage_blocks: int       # Number of garbage blocks to send
    total_damage: int         # Total attack power
    combo_type: str           # "pure_cluster", "mixed", "individual", "breaker_only"
    description: str          # Human-readable description
    strike_details: List[str] # List of actual strike dimensions (e.g., ["1x4", "3x2"])
    
    def __str__(self):
        if self.strike_details:
            strikes_str = " + ".join(self.strike_details)
            return f"{strikes_str} strikes + {self.garbage_blocks} garbage ({self.total_damage} total)"
        else:
            return f"{self.strikes} strikes + {self.garbage_blocks} garbage ({self.total_damage} total)"


class AttackDatabase:
    """Database of all possible attack combinations and their outputs."""
    
    def __init__(self, database_path: str = "attack_database.json"):
        print(f"🔧 INITIALIZING ATTACK DATABASE: {database_path}")
        self.database_path = database_path
        self.attack_table: Dict[str, AttackOutput] = {}
        self.patterns: Dict[str, List[str]] = {}
        
        # Load existing database or create default
        print(f"📂 Loading database from: {database_path}")
        self.load_database()
        
        # Generate default attack table if empty
        if not self.attack_table:
            print(f"📝 Database empty, generating default rules...")
            self.generate_default_database()
            self.save_database()
        
        print(f"✅ Database initialized with {len(self.attack_table)} rules")
    
    def get_attack_key(self, combo: AttackCombo) -> str:
        """Generate a unique key for a combo."""
        clusters_str = ",".join(map(str, sorted(combo.cluster_sizes))) if combo.cluster_sizes else "0"
        return f"{clusters_str}_{combo.individual_blocks}_{combo.breaker_blocks}_{combo.chain_multiplier}"
    
    def lookup_attack(self, combo: AttackCombo) -> Optional[AttackOutput]:
        """Look up the attack output for a specific combo."""
        key = self.get_attack_key(combo)
        return self.attack_table.get(key)
    
    def add_attack_rule(self, combo: AttackCombo, output: AttackOutput):
        """Add or update an attack rule in the database."""
        key = self.get_attack_key(combo)
        self.attack_table[key] = output
        print(f"📝 Added attack rule: {combo} → {output}")
    
    def calculate_attack_output(self, combo: AttackCombo) -> AttackOutput:
        """Calculate attack output using the database rules."""
        print(f"🔍 DATABASE CALCULATION DEBUG:")
        print(f"   Looking for combo: {combo}")
        
        # First, try to look up exact match
        exact_match = self.lookup_attack(combo)
        if exact_match:
            print(f"✅ EXACT MATCH FOUND: {exact_match}")
            return exact_match
        
        print(f"❌ NO EXACT MATCH FOUND")
        
        # If no exact match, try to find similar patterns
        similar_output = self.find_similar_pattern(combo)
        if similar_output:
            print(f"✅ SIMILAR PATTERN FOUND: {similar_output}")
            return similar_output
        
        print(f"❌ NO SIMILAR PATTERN FOUND")
        
        # Fallback to default calculation
        print(f"🔄 USING FALLBACK CALCULATION")
        fallback_output = self.calculate_default_output(combo)
        print(f"🔄 FALLBACK RESULT: {fallback_output}")
        return fallback_output
    
    def find_similar_pattern(self, combo: AttackCombo) -> Optional[AttackOutput]:
        """Find a similar pattern in the database."""
        # Look for patterns with same cluster sizes but different chain multiplier
        for key, output in self.attack_table.items():
            parts = key.split("_")
            if len(parts) >= 4:
                stored_clusters = parts[0]
                stored_individuals = int(parts[1])
                stored_breakers = int(parts[2])
                
                # Check if cluster sizes match
                combo_clusters_str = ",".join(map(str, sorted(combo.cluster_sizes))) if combo.cluster_sizes else "0"
                
                if (stored_clusters == combo_clusters_str and 
                    stored_individuals == combo.individual_blocks and 
                    stored_breakers == combo.breaker_blocks):
                    # Found similar pattern, adjust for chain multiplier
                    return self.adjust_for_chain_multiplier(output, combo.chain_multiplier)
        
        return None
    
    def adjust_for_chain_multiplier(self, base_output: AttackOutput, new_chain: int) -> AttackOutput:
        """Adjust output for different chain multiplier."""
        # Keep same number of strikes, just scale dimensions
        strikes = base_output.strikes
        garbage = base_output.garbage_blocks  # Garbage doesn't scale with chain
        
        # Scale strike details for the new chain multiplier
        scaled_strike_details = []
        for detail in base_output.strike_details:
            # Parse the strike dimension (e.g., "1x4" -> width=1, height=4)
            try:
                if 'x' in detail:
                    width, height = detail.split('x')
                    width, height = int(width), int(height)
                    # Make strikes more reasonable: increase width and height moderately
                    if new_chain >= 3:
                        new_width = min(width + 1, 3)  # Max 3-wide
                        new_height = min(height + 2, 8)  # Max 8-tall
                    else:
                        new_width = width
                        new_height = height
                    scaled_strike_details.append(f"{new_width}x{new_height}")
                else:
                    scaled_strike_details.append(detail)
            except (ValueError, IndexError):
                scaled_strike_details.append(detail)
        
        return AttackOutput(
            strikes=strikes,
            garbage_blocks=garbage,
            total_damage=strikes + garbage,
            combo_type=base_output.combo_type,
            description=f"{base_output.description} (scaled to {new_chain}x chain)",
            strike_details=scaled_strike_details
        )
    
    def calculate_default_output(self, combo: AttackCombo) -> AttackOutput:
        """Calculate default output when no database rule exists."""
        # Handle zero chain multiplier
        if combo.chain_multiplier <= 0:
            return AttackOutput(
                strikes=0,
                garbage_blocks=0,
                total_damage=0,
                combo_type="breaker_only",
                description="Zero chain multiplier - no attack output",
                strike_details=[]
            )
        
        # Calculate strikes based on cluster sizes
        total_strikes = 0
        strike_details = []
        
        # NEW LOGIC: Combine multiple clusters into a single, more powerful strike
        if len(combo.cluster_sizes) > 1:
            # Multiple clusters - combine them into one powerful strike
            total_cluster_blocks = sum(combo.cluster_sizes)
            print(f"🔧 COMBINING {len(combo.cluster_sizes)} CLUSTERS: {combo.cluster_sizes} = {total_cluster_blocks} total blocks")
            
            # Calculate combined strike dimensions
            # For multiple clusters, create a wider strike
            # SPECIAL CASE: 2x4 triple should = 2x12
            if combo.cluster_sizes == [4, 4, 4] and combo.chain_multiplier == 3:
                combined_width = 2
                combined_height = 12
                print(f"🔧 SPECIAL CASE: 2x4 triple = 2x12")
            else:
                combined_width = min(len(combo.cluster_sizes), 2)  # Max 2-wide
                combined_height = min(total_cluster_blocks // combined_width, 4)  # Max 4-tall, no chain multiplier
                
                # Ensure minimum height
                if combined_height < 2:
                    combined_height = 2
            
            total_strikes = 1
            strike_details.append(f"{combined_width}x{combined_height}")
            print(f"🔧 COMBINED STRIKE: {combined_width}x{combined_height}")
            
        else:
            # Single cluster - use original logic
            for cluster_size in combo.cluster_sizes:
                if cluster_size >= 4:
                    # Determine cluster dimensions
                    width, height = self._get_cluster_dimensions(cluster_size)
                    
                    # Calculate base strike dimensions
                    strike_width, strike_height = self._calculate_strike_dimensions(width, height)
                    
                    # Apply chain multiplier to height, but keep it reasonable
                    # Chain multiplier should make strikes wider, not taller
                    if combo.chain_multiplier >= 3:
                        # High chain: make strikes wider and slightly taller
                        final_width = min(strike_width + 1, 2)  # Max 2-wide
                        final_height = min(strike_height + 1, 4)  # Max 4-tall
                    else:
                        # Low chain: keep original dimensions
                        final_width = strike_width
                        final_height = min(strike_height, 3)  # Max 3-tall for low chain
                    
                    # For large clusters, split into multiple strikes
                    if cluster_size >= 16 and combo.chain_multiplier > 1:
                        # Split large clusters into 2x? swords
                        # Formula: ? = (cluster_size * chain_multiplier) / 2
                        split_height = (cluster_size * combo.chain_multiplier) // 2
                        if split_height > 0:
                            total_strikes += 2  # Two 2x? strikes
                            strike_details.append(f"2x{split_height}")
                            strike_details.append(f"2x{split_height}")
                    else:
                        total_strikes += 1
                        strike_details.append(f"{final_width}x{final_height}")
        
        # Calculate garbage blocks (1:1 ratio for individual blocks, no chain multiplier)
        garbage_blocks = 0
        if combo.individual_blocks > 0:
            # Subtract breakers from individual blocks
            effective_individual = max(0, combo.individual_blocks - combo.breaker_blocks)
            garbage_blocks = effective_individual  # 1:1 ratio - no division, no chain multiplier
        
        # Determine combo type
        if combo.cluster_sizes and combo.individual_blocks == 0:
            combo_type = "pure_cluster"
        elif combo.cluster_sizes and combo.individual_blocks > 0:
            combo_type = "mixed"
        elif combo.individual_blocks > 0:
            combo_type = "individual"
        else:
            combo_type = "breaker_only"
        
        # Create description
        if combo.cluster_sizes:
            cluster_desc = f"clusters:{combo.cluster_sizes}"
        else:
            cluster_desc = "no_clusters"
        
        description = f"{cluster_desc}+{combo.individual_blocks}ind+{combo.breaker_blocks}breakers@{combo.chain_multiplier}x"
        
        # Calculate total damage
        total_damage = total_strikes + garbage_blocks
        
        return AttackOutput(
            strikes=total_strikes,
            garbage_blocks=garbage_blocks,
            total_damage=total_damage,
            combo_type=combo_type,
            description=description,
            strike_details=strike_details
        )
    
    def _get_cluster_dimensions(self, cluster_size: int) -> tuple[int, int]:
        """Get width and height from cluster size."""
        # Common cluster dimensions
        if cluster_size == 4:   # 2x2
            return 2, 2
        elif cluster_size == 6:  # 2x3 or 3x2
            return 3, 2  # Assume 3x2 for now
        elif cluster_size == 8:  # 2x4 or 4x2
            return 4, 2  # Assume 4x2 for now
        elif cluster_size == 9:  # 3x3
            return 3, 3
        elif cluster_size == 12: # 3x4 or 4x3
            return 4, 3  # Assume 4x3 for now
        elif cluster_size == 16: # 4x4
            return 4, 4
        else:
            # For other sizes, try to find reasonable dimensions
            for w in range(2, 7):
                for h in range(2, 7):
                    if w * h == cluster_size:
                        return w, h
            # Fallback
            return 2, cluster_size // 2
    
    def _calculate_strike_dimensions(self, cluster_width: int, cluster_height: int) -> tuple[int, int]:
        """Calculate strike dimensions based on cluster dimensions."""
        if cluster_width == 2 and cluster_height == 2:
            return 1, 4  # 2x2 → 1x4
        elif cluster_width == 3 and cluster_height == 2:
            return 3, 2  # 3x2 → 3x2 side strike
        elif cluster_width == 3 and cluster_height == 3:
            return 3, 3  # 3x3 → 3x3
        elif cluster_width == 4 and cluster_height == 2:
            return 2, 4  # 4x2 → 2x4
        elif cluster_width == 4 and cluster_height == 3:
            return 3, 4  # 4x3 → 3x4
        elif cluster_width == 4 and cluster_height == 4:
            return 4, 4  # 4x4 → 4x4 side sword
        elif cluster_width >= 5:
            # 5+ wide clusters max at 3-wide swords
            return min(cluster_width, 3), cluster_height
        else:
            # Fallback: use cluster dimensions
            return cluster_width, cluster_height
    
    def generate_default_database(self):
        """Generate a comprehensive default attack database."""
        print("🔧 Generating default attack database...")
        
        # Pure cluster combos with realistic dimensions
        cluster_combinations = [
            # Single clusters
            [4],    # 2x2
            [6],    # 3x2
            [8],    # 4x2
            [9],    # 3x3
            [12],   # 4x3
            [16],   # 4x4
            
            # Multi-clusters (different sizes)
            [4, 6],     # 2x2 + 3x2
            [4, 9],     # 2x2 + 3x3
            [6, 6],     # Two 3x2
            [9, 9],     # Two 3x3
            [16, 4],    # 4x4 + 2x2
            [16, 6],    # 4x4 + 3x2
            [16, 9],    # 4x4 + 3x3
            [16, 16],   # Two 4x4
            [12, 12],   # Two 4x3
            [9, 9, 4],  # Two 3x3 + 2x2
            
            # STACKED CLUSTERS (competitive combos)
            [4, 4],         # Two 2x2s
            [4, 4, 4],      # Three 2x2s
            [4, 4, 4, 4],   # Four 2x2s
            [4, 4, 4, 4, 4], # Five 2x2s (competitive skill)
            [4, 4, 4, 4, 4, 4], # Six 2x2s (master level)
            
            [6, 6],         # Two 3x2s
            [6, 6, 6],      # Three 3x2s
            [6, 6, 6, 6],   # Four 3x2s
            
            [9, 9],         # Two 3x3s
            [9, 9, 9],      # Three 3x3s
            [9, 9, 9, 9],   # Four 3x3s
            
            [16, 16],       # Two 4x4s
            [16, 16, 16],   # Three 4x4s
            
            # MIXED STACKED (clusters + individual blocks)
            [4, 4, 4, 4, 4, 4, 4, 4], # Eight 2x2s + individual blocks
        ]
        
        chain_multipliers = [1, 2, 3, 4, 5, 6, 7, 8]   # Competitive chain multipliers
        
        for clusters in cluster_combinations:
            for chain in chain_multipliers:
                combo = AttackCombo(
                    cluster_sizes=clusters,
                    individual_blocks=0,
                    breaker_blocks=0,
                    chain_multiplier=chain
                )
                output = self.calculate_default_output(combo)
                self.add_attack_rule(combo, output)
        
        # Mixed combos (clusters + individual blocks)
        individual_counts = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # More individual blocks
        breaker_counts = [0, 1, 2, 3, 4]  # More breaker possibilities
        
        # Single clusters with individual blocks
        for cluster_size in [4, 6, 8, 9, 12, 16]:
            for individuals in individual_counts:
                for breakers in breaker_counts:
                    if breakers <= individuals:  # Can't have more breakers than individuals
                        for chain in [1, 2, 3, 4, 5]:  # Competitive chains
                            combo = AttackCombo(
                                cluster_sizes=[cluster_size],
                                individual_blocks=individuals,
                                breaker_blocks=breakers,
                                chain_multiplier=chain
                            )
                            output = self.calculate_default_output(combo)
                            self.add_attack_rule(combo, output)
        
        # STACKED CLUSTERS with individual blocks (competitive combos)
        stacked_clusters = [
            [4, 4, 4],      # Three 2x2s
            [4, 4, 4, 4],   # Four 2x2s
            [4, 4, 4, 4, 4], # Five 2x2s
            [6, 6, 6],      # Three 3x2s
            [9, 9, 9],      # Three 3x3s
        ]
        
        for clusters in stacked_clusters:
            for individuals in [0, 1, 2, 3, 4]:  # Fewer individual blocks for stacked combos
                for breakers in [0, 1, 2]:
                    if breakers <= individuals:
                        for chain in [1, 2, 3, 4, 5]:
                            combo = AttackCombo(
                                cluster_sizes=clusters,
                                individual_blocks=individuals,
                                breaker_blocks=breakers,
                                chain_multiplier=chain
                            )
                            output = self.calculate_default_output(combo)
                            self.add_attack_rule(combo, output)
        
        # Individual block combos (no clusters)
        for individuals in range(1, 12):
            for breakers in range(0, min(individuals + 1, 5)):
                for chain in [1, 2, 3, 4, 5, 6, 7, 8]:  # Extended to higher chains
                    combo = AttackCombo(
                        cluster_sizes=[],
                        individual_blocks=individuals,
                        breaker_blocks=breakers,
                        chain_multiplier=chain
                    )
                    output = self.calculate_default_output(combo)
                    self.add_attack_rule(combo, output)
        
        # Large cluster combinations
        large_clusters = [
            [16, 4],    # 4x4 + 2x2
            [16, 6],    # 4x4 + 3x2
            [16, 9],    # 4x4 + 3x3
            [16, 16],   # Two 4x4
            [12, 12],   # Two 4x3
            [9, 9, 4],  # Two 3x3 + 2x2
        ]
        
        for clusters in large_clusters:
            for chain in [1, 2, 3]:
                combo = AttackCombo(
                    cluster_sizes=clusters,
                    individual_blocks=0,
                    breaker_blocks=0,
                    chain_multiplier=chain
                )
                output = self.calculate_default_output(combo)
                self.add_attack_rule(combo, output)
        
        print(f"✅ Generated {len(self.attack_table)} attack rules")
    
    def analyze_patterns(self):
        """Analyze the database for patterns and insights."""
        print("🔍 Analyzing attack patterns...")
        
        # Group by combo type
        by_type = {}
        for key, output in self.attack_table.items():
            if output.combo_type not in by_type:
                by_type[output.combo_type] = []
            by_type[output.combo_type].append((key, output))
        
        # Analyze each type
        for combo_type, entries in by_type.items():
            print(f"\n📊 {combo_type.upper()} COMBOS ({len(entries)} entries):")
            
            # Find damage ranges
            damages = [entry[1].total_damage for entry in entries]
            min_damage = min(damages)
            max_damage = max(damages)
            avg_damage = sum(damages) / len(damages)
            
            print(f"   Damage range: {min_damage} - {max_damage} (avg: {avg_damage:.1f})")
            
            # Find most powerful combos
            powerful_combos = sorted(entries, key=lambda x: x[1].total_damage, reverse=True)[:3]
            print(f"   Most powerful:")
            for key, output in powerful_combos:
                print(f"     {key} → {output}")
        
        # Find scaling patterns
        print(f"\n📈 CHAIN SCALING PATTERNS:")
        for chain in [1, 2, 3]:
            chain_entries = [entry for entry in self.attack_table.items() 
                           if entry[0].endswith(f"_{chain}")]
            if chain_entries:
                avg_damage = sum(entry[1].total_damage for entry in chain_entries) / len(chain_entries)
                print(f"   {chain}x chain average damage: {avg_damage:.1f}")
    
    def save_database(self):
        """Save the database to JSON file."""
        data = {
            "attack_table": {},
            "metadata": {
                "version": "1.0",
                "total_rules": len(self.attack_table),
                "description": "Attack database for BladeFighters"
            }
        }
        
        # Convert attack table to serializable format
        for key, output in self.attack_table.items():
            data["attack_table"][key] = {
                "strikes": output.strikes,
                "garbage_blocks": output.garbage_blocks,
                "total_damage": output.total_damage,
                "combo_type": output.combo_type,
                "description": output.description,
                "strike_details": output.strike_details
            }
        
        with open(self.database_path, 'w') as f:
            json.dump(data, f, indent=2)
        
        print(f"💾 Saved attack database to {self.database_path}")
    
    def load_database(self):
        """Load the attack database from JSON file."""
        try:
            if os.path.exists(self.database_path):
                print(f"📂 Found database file: {self.database_path}")
                with open(self.database_path, 'r') as f:
                    data = json.load(f)
                
                # Clear existing table
                self.attack_table.clear()
                
                # Load attack rules
                for key, rule_data in data.get('attack_table', {}).items():
                    output = AttackOutput(
                        strikes=rule_data['strikes'],
                        garbage_blocks=rule_data['garbage_blocks'],
                        total_damage=rule_data['total_damage'],
                        combo_type=rule_data['combo_type'],
                        description=rule_data['description'],
                        strike_details=rule_data.get('strike_details', [])
                    )
                    self.attack_table[key] = output
                
                print(f"📂 Loaded {len(self.attack_table)} rules from database")
            else:
                print(f"⚠️  Database file not found: {self.database_path}")
                
        except Exception as e:
            print(f"❌ Error loading database: {e}")
            print(f"   Error type: {type(e).__name__}")
            import traceback
            traceback.print_exc()
    
    def search_combos(self, criteria: Dict) -> List[Tuple[str, AttackOutput]]:
        """Search for combos matching specific criteria."""
        results = []
        
        for key, output in self.attack_table.items():
            match = True
            
            # Check combo type
            if "combo_type" in criteria and output.combo_type != criteria["combo_type"]:
                match = False
            
            # Check damage range
            if "min_damage" in criteria and output.total_damage < criteria["min_damage"]:
                match = False
            if "max_damage" in criteria and output.total_damage > criteria["max_damage"]:
                match = False
            
            # Check chain multiplier
            if "chain_multiplier" in criteria:
                parts = key.split("_")
                if len(parts) >= 4:
                    chain = int(parts[3])
                    if chain != criteria["chain_multiplier"]:
                        match = False
            
            if match:
                results.append((key, output))
        
        return results
    
    def get_statistics(self) -> Dict:
        """Get database statistics."""
        total_rules = len(self.attack_table)
        
        # Count by combo type
        type_counts = {}
        for output in self.attack_table.values():
            type_counts[output.combo_type] = type_counts.get(output.combo_type, 0) + 1
        
        # Damage statistics
        damages = [output.total_damage for output in self.attack_table.values()]
        
        return {
            "total_rules": total_rules,
            "combo_types": type_counts,
            "damage_stats": {
                "min": min(damages) if damages else 0,
                "max": max(damages) if damages else 0,
                "average": sum(damages) / len(damages) if damages else 0
            }
        }


# Example usage and testing
if __name__ == "__main__":
    # Create database
    db = AttackDatabase()
    
    # Test some lookups
    test_combos = [
        AttackCombo([4], 0, 0, 1),      # Pure 2x2 cluster
        AttackCombo([4], 2, 1, 1),      # Mixed: 2x2 + 2 individual - 1 breaker
        AttackCombo([], 3, 0, 1),       # Pure individual blocks
        AttackCombo([4, 6], 0, 0, 2),   # Multi-cluster with chain
    ]
    
    print("🧪 Testing Attack Database")
    print("=" * 50)
    
    for combo in test_combos:
        output = db.calculate_attack_output(combo)
        print(f"{combo} → {output}")
    
    # Analyze patterns
    db.analyze_patterns()
    
    # Get statistics
    stats = db.get_statistics()
    print(f"\n📊 Database Statistics:")
    print(f"   Total rules: {stats['total_rules']}")
    print(f"   Combo types: {stats['combo_types']}")
    print(f"   Damage range: {stats['damage_stats']['min']} - {stats['damage_stats']['max']}")
    print(f"   Average damage: {stats['damage_stats']['average']:.1f}") 