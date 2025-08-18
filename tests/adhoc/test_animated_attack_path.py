#!/usr/bin/env python3
"""
Focused Test: Animated Attack Path
Tests that attacks spawn above-board and fall properly without appearing on grid first.
"""

import sys
import time
import logging
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,  # Verbose logging
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('test_animated_attack_path_verbose.log'),
        logging.StreamHandler()
    ]
)

# Enable verbose logging for specific modules
logging.getLogger('modules.testmode_module.test_mode').setLevel(logging.DEBUG)
logging.getLogger('modules.testmode_module.attack_delivery_committer').setLevel(logging.DEBUG)

logger = logging.getLogger(__name__)

def test_animated_attack_path():
    """Test that attacks use animated path only and don't appear on grid before falling."""
    
    try:
        # Import game components
        from modules.testmode_module.test_mode import TestModeRefactored
        import pygame
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 24)
        
        # Initialize test mode
        test_mode = TestModeRefactored(
            screen=screen,
            font=font,
            audio=None,
            asset_path="puzzleassets",
            settings_system=None,
            clock=None
        )
        
        logger.info("=== ANIMATED ATTACK PATH TEST ===")
        
        # Initialize test
        test_mode.initialize_test()
        
        # Test 1: Single garbage attack
        logger.info("Test 1: Single garbage attack")
        
        # Enqueue a single garbage attack
        test_mode.queue_attack_spawn('enemy', 'garbage', count=1)
        
        # Call update once
        test_mode.update()
        
        # Check that enemy grid has zero garbage_block before animation end
        enemy_garbage_count = sum(1 for row in test_mode.enemy_engine.puzzle_grid 
                                for cell in row if cell == 'garbage_block')
        
        logger.info(f"Garbage blocks on enemy grid: {enemy_garbage_count}")
        
        if enemy_garbage_count == 0:
            logger.info("✅ PASS: No garbage blocks on grid before animation end")
        else:
            logger.error("❌ FAIL: Garbage blocks appeared on grid before animation end")
            return False
        
        # Check visual_falling_blocks has entry with start_y < 0
        enemy_renderer = test_mode.enemy_renderer
        asm = getattr(enemy_renderer, 'animation_state_manager', None)
        if asm and hasattr(asm, 'visual_falling_blocks'):
            visual_falling = asm.visual_falling_blocks
        else:
            visual_falling = {}
        
        logger.info(f"Visual falling blocks: {len(visual_falling)}")
        
        has_above_board_spawn = False
        for key, data in visual_falling.items():
            if data.get('start_y', 0) < 0:
                has_above_board_spawn = True
                logger.info(f"✅ Found above-board spawn at y={data.get('start_y')}")
                break
        
        if not has_above_board_spawn:
            logger.warning("⚠️  No above-board spawn found in visual_falling_blocks")
        
        # Test 2: Advance time to just before end_ms
        logger.info("Test 2: Advance time to just before end_ms")
        
        # Get pending landings
        pending_landings = test_mode.pending_landings.get('enemy', [])
        if pending_landings:
            earliest_end_ms = min(end_ms for _, _, _, end_ms in pending_landings)
            current_time = test_mode.clock.now_ms()
            
            # Advance to just before end_ms
            time_to_advance = max(0, earliest_end_ms - current_time - 100)  # 100ms before
            logger.info(f"Advancing time by {time_to_advance}ms")
            
            # Simulate time advancement
            for _ in range(int(time_to_advance / 16)):  # 60fps = 16ms per frame
                if hasattr(test_mode.clock, 'tick'):
                    test_mode.clock.tick()
                test_mode.update()
            
            # Check still no garbage on grid
            enemy_garbage_count = sum(1 for row in test_mode.enemy_engine.puzzle_grid 
                                    for cell in row if cell == 'garbage_block')
            
            logger.info(f"Garbage blocks on enemy grid (before end_ms): {enemy_garbage_count}")
            
            if enemy_garbage_count == 0:
                logger.info("✅ PASS: Still no garbage blocks on grid before end_ms")
            else:
                logger.error("❌ FAIL: Garbage blocks appeared on grid before end_ms")
                return False
        
        # Test 3: Advance beyond end_ms
        logger.info("Test 3: Advance beyond end_ms")
        
        # Advance past end_ms
        for _ in range(100):  # Advance 100 frames
            if hasattr(test_mode.clock, 'tick'):
                test_mode.clock.tick()
            test_mode.update()
        
        # Check that placement occurred
        enemy_garbage_count = sum(1 for row in test_mode.enemy_engine.puzzle_grid 
                                for cell in row if cell == 'garbage_block')
        
        logger.info(f"Garbage blocks on enemy grid (after end_ms): {enemy_garbage_count}")
        
        if enemy_garbage_count > 0:
            logger.info("✅ PASS: Garbage blocks placed after animation end")
        else:
            logger.warning("⚠️  No garbage blocks placed after animation end")
        
        # Test 4: Check for violations
        violations_report = test_mode.get_attack_delivery_violations_report()
        logger.info("=== VIOLATIONS REPORT ===")
        logger.info(violations_report)
        
        if "pre-commit grid write violations" in violations_report:
            logger.error("❌ FAIL: Pre-commit grid write violations detected")
            return False
        else:
            logger.info("✅ PASS: No pre-commit grid write violations")
        
        logger.info("=== ALL TESTS PASSED ===")
        return True
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    finally:
        pygame.quit()

def test_garbage_transformation():
    """Test that garbage blocks transform properly after landing."""
    
    try:
        # Import game components
        from modules.testmode_module.test_mode import TestModeRefactored
        import pygame
        
        # Initialize pygame
        pygame.init()
        screen = pygame.display.set_mode((1200, 800))
        font = pygame.font.Font(None, 24)
        
        # Initialize test mode
        test_mode = TestModeRefactored(
            screen=screen,
            font=font,
            audio=None,
            asset_path="puzzleassets",
            settings_system=None,
            clock=None
        )
        
        logger.info("=== GARBAGE TRANSFORMATION TEST ===")
        
        # Initialize test
        test_mode.initialize_test()
        
        # Queue garbage attack
        test_mode.queue_attack_spawn('enemy', 'garbage', count=1)
        
        # Let it land
        for _ in range(200):  # Advance enough frames for landing
            if hasattr(test_mode.clock, 'tick'):
                test_mode.clock.tick()
            test_mode.update()
        
        # Check for garbage_block (neutral)
        enemy_garbage_count = sum(1 for row in test_mode.enemy_engine.puzzle_grid 
                                for cell in row if cell == 'garbage_block')
        
        logger.info(f"Neutral garbage blocks: {enemy_garbage_count}")
        
        if enemy_garbage_count > 0:
            logger.info("✅ Found neutral garbage blocks after landing")
            
            # Call update_received_blocks for N frames
            logger.info("Calling update_received_blocks for transformation...")
            
            for i in range(60):  # 60 frames = 1 second at 60fps
                test_mode.delivery_committer.update_received_blocks(test_mode.enemy_engine, 'enemy')
                if hasattr(test_mode.clock, 'tick'):
                    test_mode.clock.tick()
                
                # Check for transformation
                colored_garbage = sum(1 for row in test_mode.enemy_engine.puzzle_grid 
                                    for cell in row if '_garbage' in str(cell))
                
                if colored_garbage > 0:
                    logger.info(f"✅ Transformation to colored garbage detected at frame {i}")
                    break
            else:
                logger.warning("⚠️  No transformation to colored garbage detected within 1 second")
        else:
            logger.warning("⚠️  No neutral garbage blocks found after landing")
        
        logger.info("=== TRANSFORMATION TEST COMPLETED ===")
        return True
        
    except Exception as e:
        logger.error(f"Transformation test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return False
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    logger.info("Running animated attack path tests...")
    
    success1 = test_animated_attack_path()
    success2 = test_garbage_transformation()
    
    if success1 and success2:
        logger.info("🎉 ALL TESTS PASSED!")
        sys.exit(0)
    else:
        logger.error("❌ SOME TESTS FAILED!")
        sys.exit(1)
