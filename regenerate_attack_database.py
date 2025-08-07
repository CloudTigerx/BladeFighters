#!/usr/bin/env python3
"""
Regenerate Attack Database

This script regenerates the attack database with the new cluster combination logic.
"""

import sys
import os

# Add the modules directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'modules'))

from attack_module.attack_database import AttackDatabase


def regenerate_database():
    """Regenerate the attack database with new logic."""
    print("🔧 REGENERATING ATTACK DATABASE...")
    
    # Create a new database instance
    db = AttackDatabase("attack_database_new.json")
    
    # Generate the database with new logic
    db.generate_default_database()
    
    # Save the new database
    db.save_database()
    
    print("✅ Attack database regenerated!")
    
    # Test the 2x4 triple scenario
    print("\n🧪 TESTING 2x4 TRIPLE SCENARIO...")
    
    from attack_module import AttackCombo
    
    combo = AttackCombo(
        cluster_sizes=[4, 4, 4],  # Three 4-block clusters
        individual_blocks=0,
        breaker_blocks=0,
        chain_multiplier=3
    )
    
    output = db.calculate_attack_output(combo)
    print(f"🎯 RESULT: {output}")
    
    if "2x" in str(output) and "12" in str(output):
        print("✅ SUCCESS: Got combined 2x12 strike!")
    else:
        print("❌ ISSUE: Still not getting combined strike")
        print(f"   Output: {output.strike_details}")


if __name__ == "__main__":
    regenerate_database() 