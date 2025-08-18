#!/usr/bin/env python3
"""
QA Attack Delivery Repro Script
Tests the attack delivery monitoring system to catch "on-grid then fall" issues.
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
        logging.FileHandler('qa_attack_delivery_verbose.log'),
        logging.StreamHandler()
    ]
)

# Enable verbose logging for specific modules
logging.getLogger('modules.testmode_module.test_mode').setLevel(logging.DEBUG)
logging.getLogger('modules.testmode_module.attack_delivery_committer').setLevel(logging.DEBUG)

def run_attack_delivery_test():
    """Run the attack delivery test to reproduce and monitor issues."""
    logger = logging.getLogger(__name__)
    
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
        
        logger.info("Starting attack delivery test...")
        
        # Initialize test
        test_mode.initialize_test()
        
        # Start PvP mode
        logger.info("Starting PvP mode...")
        
        # Trigger attacks quickly
        logger.info("Triggering attacks...")
        
        # Queue multiple attacks per side
        for i in range(3):
            # Player attacks enemy
            test_mode.queue_attack_spawn('enemy', 'garbage', count=5)
            test_mode.queue_attack_spawn('enemy', 'strike', count=1, strike_details=[{'width': 2, 'height': 4}])
            
            # Enemy attacks player
            test_mode.queue_attack_spawn('player', 'garbage', count=3)
            test_mode.queue_attack_spawn('player', 'strike', count=1, strike_details=[{'width': 1, 'height': 3}])
            
            logger.info(f"Queued attack batch {i+1}")
        
        # Run the game for 10 seconds
        start_time = time.time()
        frame_count = 0
        
        logger.info("Running game for 10 seconds to capture attack delivery...")
        
        while time.time() - start_time < 10:
            # Process events
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.QUIT:
                    return
            
            # Update game state
            test_mode.update()
            
            # Draw
            screen.fill((0, 0, 0))
            test_mode.draw()
            pygame.display.flip()
            
            frame_count += 1
            
            # Log every 60 frames (1 second at 60fps)
            if frame_count % 60 == 0:
                elapsed = time.time() - start_time
                logger.info(f"Frame {frame_count}, elapsed: {elapsed:.1f}s")
                
                # Log current state
                player_pending = len(test_mode.pending_attacks.get('player', []))
                enemy_pending = len(test_mode.pending_attacks.get('enemy', []))
                player_landings = len(test_mode.pending_landings.get('player', []))
                enemy_landings = len(test_mode.pending_landings.get('enemy', []))
                
                logger.info(f"  Pending attacks: P={player_pending}, E={enemy_pending}")
                logger.info(f"  Pending landings: P={player_landings}, E={enemy_landings}")
                
                # Log detailed landing information
                for board_name, landings in [("Player", test_mode.pending_landings.get('player', [])), 
                                           ("Enemy", test_mode.pending_landings.get('enemy', []))]:
                    if landings:
                        logger.info(f"  {board_name} pending landings:")
                        for col, row, block_type, end_ms in landings:
                            time_remaining = end_ms - test_mode.clock.now_ms()
                            logger.info(f"    ({col},{row}) {block_type} ends in {time_remaining}ms")
        
        # Get violations report
        violations_report = test_mode.get_attack_delivery_violations_report()
        logger.info("=== ATTACK DELIVERY VIOLATIONS REPORT ===")
        logger.info(violations_report)
        
        # Check for specific issues
        if "pre-commit grid write violations" in violations_report:
            logger.error("❌ PRE-COMMIT GRID WRITE VIOLATIONS DETECTED!")
            logger.error("This indicates attacks are appearing on grid before falling.")
        else:
            logger.info("✅ No pre-commit grid write violations detected.")
        
        # Check for gray garbage transformation
        logger.info("=== GARBAGE TRANSFORMATION CHECK ===")
        player_garbage = sum(1 for row in test_mode.player_engine.puzzle_grid 
                           for cell in row if cell == 'garbage_block')
        enemy_garbage = sum(1 for row in test_mode.enemy_engine.puzzle_grid 
                          for cell in row if cell == 'garbage_block')
        
        logger.info(f"Neutral garbage blocks: P={player_garbage}, E={enemy_garbage}")
        
        # Check for colored garbage blocks
        player_colored_garbage = sum(1 for row in test_mode.player_engine.puzzle_grid 
                                   for cell in row if '_garbage' in str(cell) and cell != 'garbage_block')
        enemy_colored_garbage = sum(1 for row in test_mode.enemy_engine.puzzle_grid 
                                  for cell in row if '_garbage' in str(cell) and cell != 'garbage_block')
        
        logger.info(f"Colored garbage blocks: P={player_colored_garbage}, E={enemy_colored_garbage}")
        
        # Check for normal blocks from transformations
        player_normal_blocks = sum(1 for row in test_mode.player_engine.puzzle_grid 
                                 for cell in row if '_block' in str(cell) and '_garbage' not in str(cell))
        enemy_normal_blocks = sum(1 for row in test_mode.enemy_engine.puzzle_grid 
                                for cell in row if '_block' in str(cell) and '_garbage' not in str(cell))
        
        logger.info(f"Normal blocks from transformations: P={player_normal_blocks}, E={enemy_normal_blocks}")
        
        if player_garbage > 0 or enemy_garbage > 0:
            logger.warning("⚠️  Neutral garbage blocks detected - may not be transforming properly")
        else:
            logger.info("✅ No neutral garbage blocks detected - transformation working")
            
        # Log detailed grid state for debugging
        logger.info("=== DETAILED GRID STATE ===")
        for board_name, engine in [("Player", test_mode.player_engine), ("Enemy", test_mode.enemy_engine)]:
            logger.info(f"{board_name} grid state:")
            for row_idx, row in enumerate(engine.puzzle_grid):
                row_content = []
                for col_idx, cell in enumerate(row):
                    if cell and cell not in ['empty', None]:
                        row_content.append(f"({col_idx},{row_idx})={cell}")
                if row_content:
                    logger.info(f"  Row {row_idx}: {', '.join(row_content)}")
        
        logger.info("Test completed successfully.")
        
    except Exception as e:
        logger.error(f"Test failed with error: {e}")
        import traceback
        logger.error(traceback.format_exc())
    
    finally:
        pygame.quit()

if __name__ == "__main__":
    run_attack_delivery_test()
