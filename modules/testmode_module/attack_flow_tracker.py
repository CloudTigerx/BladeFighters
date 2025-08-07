#!/usr/bin/env python3
"""
Attack Flow Tracker

Provides clean, comprehensive tracking of attack flow between players.
Replaces scattered debug messages with organized summaries.
"""

import time
from typing import Dict, List, Any

class AttackFlowTracker:
    """Tracks attack flow between players with clean summary output."""
    
    def __init__(self):
        """Initialize the attack flow tracker."""
        self.reset()
    
    def reset(self):
        """Reset all tracking data."""
        self.data = {
            'player_to_enemy': {
                'sent': {'strikes': 0, 'garbage': 0},
                'queued': {'strikes': 0, 'garbage': 0},
                'placed': {'strikes': 0, 'garbage': 0},
                'pending_attacks': []
            },
            'enemy_to_player': {
                'sent': {'strikes': 0, 'garbage': 0},
                'queued': {'strikes': 0, 'garbage': 0}, 
                'placed': {'strikes': 0, 'garbage': 0},
                'pending_attacks': []
            }
        }
        self.last_summary_time = 0
    
    def track_sent(self, sender: str, attack_type: str, count: int):
        """Track when attacks are sent."""
        direction = f"{sender}_to_{'enemy' if sender == 'player' else 'player'}"
        self.data[direction]['sent'][attack_type] += count
        
        # Add to pending
        self.data[direction]['pending_attacks'].append({
            'type': attack_type,
            'count': count,
            'remaining': count,
            'timestamp': time.time()
        })
    
    def track_queued(self, receiver: str, attack_type: str, count: int):
        """Track when attacks are queued for placement."""
        direction = f"{'enemy' if receiver == 'player' else 'player'}_to_{receiver}"
        self.data[direction]['queued'][attack_type] += count
    
    def track_placed(self, receiver: str, attack_type: str, blocks_placed: int):
        """Track when attack blocks are placed on board."""
        direction = f"{'enemy' if receiver == 'player' else 'player'}_to_{receiver}"
        self.data[direction]['placed'][attack_type] += blocks_placed
        
        # Update pending attacks
        for attack in self.data[direction]['pending_attacks']:
            if attack['type'] == attack_type and attack['remaining'] > 0:
                placed = min(blocks_placed, attack['remaining'])
                attack['remaining'] -= placed
                blocks_placed -= placed
                if blocks_placed <= 0:
                    break
    
    def get_summary(self) -> str:
        """Get a clean summary of current attack flow."""
        lines = []
        lines.append("🎯 ATTACK FLOW SUMMARY")
        lines.append("=" * 50)
        
        for direction, data in self.data.items():
            sender, receiver = direction.split('_to_')
            
            # Calculate totals
            sent_total = data['sent']['strikes'] + data['sent']['garbage']
            placed_total = data['placed']['strikes'] + data['placed']['garbage']
            
            if sent_total > 0:
                lines.append(f"\n📊 {sender.upper()} → {receiver.upper()}:")
                lines.append(f"   Sent:   {data['sent']['strikes']} strikes, {data['sent']['garbage']} garbage")
                lines.append(f"   Placed: {data['placed']['strikes']} strikes, {data['placed']['garbage']} garbage")
                
                # Calculate accuracy
                accuracy = (placed_total / sent_total) * 100 if sent_total > 0 else 0
                lines.append(f"   Success: {accuracy:.1f}%")
                
                # Show pending
                pending_total = sum(a['remaining'] for a in data['pending_attacks'] if a['remaining'] > 0)
                if pending_total > 0:
                    lines.append(f"   Pending: {pending_total} blocks waiting")
        
        return "\n".join(lines)
    
    def print_summary(self):
        """Print the attack flow summary."""
        print(self.get_summary())
    
    def should_print_summary(self) -> bool:
        """Check if enough time has passed to print another summary."""
        current_time = time.time()
        if current_time - self.last_summary_time > 5.0:  # Every 5 seconds max
            self.last_summary_time = current_time
            return True
        return False
    
    def track_combo_result(self, player: str, combo_info: Dict[str, Any]):
        """Track combo results with clean output."""
        if combo_info.get('strikes', 0) > 0 or combo_info.get('garbage', 0) > 0:
            print(f"🎯 {player.upper()} COMBO: {combo_info.get('chain_pos', 1)}x chain")
            if combo_info.get('strikes', 0) > 0:
                print(f"   → {combo_info['strikes']} strikes")
            if combo_info.get('garbage', 0) > 0:
                print(f"   → {combo_info['garbage']} garbage")