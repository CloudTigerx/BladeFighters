#!/usr/bin/env python3
"""
Debug script to test weapon color generation and identify the source of invalid color argument error.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def test_weapon_color_generation():
    """Test weapon color generation to identify the source of invalid color argument error."""
    print("🔍 DEBUGGING WEAPON COLOR GENERATION")
    print("=" * 50)
    
    try:
        from modules.items_module.item_system import create_weapon_by_name, ItemSystem
        
        # Test weapon creation
        print("1. Testing weapon creation...")
        weapon = create_weapon_by_name("Rusted Sword")
        if weapon:
            print(f"   ✅ Weapon created: {weapon.name}")
            print(f"   Pattern: {weapon.pattern}")
        else:
            print("   ❌ Failed to create weapon")
            return
        
        # Test pattern color generation
        print("\n2. Testing pattern color generation...")
        for column in range(6):
            try:
                color = weapon.pattern.color_for_column(column)
                print(f"   Column {column}: {color} (type: {type(color)})")
                
                # Test if color is valid
                if not isinstance(color, str):
                    print(f"   ⚠️ Invalid color type for column {column}: {type(color)}")
                elif color not in ['red', 'blue', 'green', 'yellow']:
                    print(f"   ⚠️ Invalid color value for column {column}: {color}")
                    
            except Exception as e:
                print(f"   ❌ Error getting color for column {column}: {e}")
        
        # Test cell color generation
        print("\n3. Testing cell color generation...")
        for column in range(6):
            for row in range(12):
                try:
                    color = weapon.pattern.color_for_cell(column, row, 12)
                    if row == 0:  # Only print first row to avoid spam
                        print(f"   Column {column}, Row {row}: {color} (type: {type(color)})")
                    
                    # Test if color is valid
                    if not isinstance(color, str):
                        print(f"   ⚠️ Invalid color type for cell ({column},{row}): {type(color)}")
                    elif color not in ['red', 'blue', 'green', 'yellow']:
                        print(f"   ⚠️ Invalid color value for cell ({column},{row}): {color}")
                        
                except Exception as e:
                    print(f"   ❌ Error getting color for cell ({column},{row}): {e}")
        
        # Test item system integration
        print("\n4. Testing item system integration...")
        item_system = ItemSystem()
        item_system.equip_weapon(weapon)
        
        for column in range(6):
            try:
                color = item_system.get_garbage_color_for_column(column)
                print(f"   Column {column} garbage color: {color} (type: {type(color)})")
                
                # Test if color is valid
                if not isinstance(color, str):
                    print(f"   ⚠️ Invalid color type for column {column}: {type(color)}")
                elif color not in ['red', 'blue', 'green', 'yellow']:
                    print(f"   ⚠️ Invalid color value for column {column}: {color}")
                    
            except Exception as e:
                print(f"   ❌ Error getting garbage color for column {column}: {e}")
        
        # Test attack color generation
        print("\n5. Testing attack color generation...")
        for column in range(6):
            try:
                color = item_system.get_attack_color_for_column(column)
                print(f"   Column {column} attack color: {color} (type: {type(color)})")
                
                # Test if color is valid
                if not isinstance(color, str):
                    print(f"   ⚠️ Invalid color type for column {column}: {type(color)}")
                elif color not in ['red', 'blue', 'green', 'yellow']:
                    print(f"   ⚠️ Invalid color value for column {column}: {color}")
                    
            except Exception as e:
                print(f"   ❌ Error getting attack color for column {column}: {e}")
        
        print("\n✅ Weapon color generation test completed successfully!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_weapon_color_generation()
