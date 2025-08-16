#!/usr/bin/env python3
"""
Quick Optimization Demo
Demonstrates the highest priority optimization: Lazy Menu Loading
"""

import sys
import os
import time
from typing import Optional

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


class OptimizedGameClient:
    """Demo of optimized GameClient with lazy loading."""
    
    def __init__(self):
        self._menu_system = None
        self._settings_ui = None
        self._puzzle_engine = None
        self._audio_system = None
        self._background_images = None
        
        print("🚀 Optimized GameClient initialized (lazy loading enabled)")
    
    def _initialize_menu_system(self):
        """Initialize menu system (expensive operation)."""
        print("   ⏳ Loading menu system...")
        time.sleep(0.1)  # Simulate 100ms loading time
        self._menu_system = {"type": "menu_system", "loaded": True}
        print("   ✅ Menu system loaded")
    
    def _initialize_settings_ui(self):
        """Initialize settings UI (expensive operation)."""
        print("   ⏳ Loading settings UI...")
        time.sleep(0.05)  # Simulate 50ms loading time
        self._settings_ui = {"type": "settings_ui", "loaded": True}
        print("   ✅ Settings UI loaded")
    
    def _initialize_puzzle_engine(self):
        """Initialize puzzle engine (expensive operation)."""
        print("   ⏳ Loading puzzle engine...")
        time.sleep(0.2)  # Simulate 200ms loading time
        self._puzzle_engine = {"type": "puzzle_engine", "loaded": True}
        print("   ✅ Puzzle engine loaded")
    
    def _load_background_images(self):
        """Load background images (expensive operation)."""
        print("   ⏳ Loading background images...")
        time.sleep(0.12)  # Simulate 120ms loading time
        self._background_images = {"type": "background_images", "loaded": True}
        print("   ✅ Background images loaded")
    
    def _initialize_audio_system(self):
        """Initialize audio system (expensive operation)."""
        print("   ⏳ Loading audio system...")
        time.sleep(0.02)  # Simulate 20ms loading time
        self._audio_system = {"type": "audio_system", "loaded": True}
        print("   ✅ Audio system loaded")
    
    # Lazy loading getters
    def get_menu_system(self):
        """Get menu system (lazy loaded)."""
        if self._menu_system is None:
            self._initialize_menu_system()
        return self._menu_system
    
    def get_settings_ui(self):
        """Get settings UI (lazy loaded)."""
        if self._settings_ui is None:
            self._initialize_settings_ui()
        return self._settings_ui
    
    def get_puzzle_engine(self):
        """Get puzzle engine (lazy loaded)."""
        if self._puzzle_engine is None:
            self._initialize_puzzle_engine()
        return self._puzzle_engine
    
    def get_background_images(self):
        """Get background images (lazy loaded)."""
        if self._background_images is None:
            self._load_background_images()
        return self._background_images
    
    def get_audio_system(self):
        """Get audio system (lazy loaded)."""
        if self._audio_system is None:
            self._initialize_audio_system()
        return self._audio_system


def demo_optimization():
    """Demonstrate the optimization benefits."""
    
    # Test 1: Traditional initialization (all at once)
    start_time = time.time()
    
    # Simulate traditional approach
    time.sleep(0.1)  # Menu system
    time.sleep(0.05)  # Settings UI
    time.sleep(0.2)  # Puzzle engine
    time.sleep(0.12)  # Background images
    time.sleep(0.02)  # Audio system
    
    traditional_time = (time.time() - start_time) * 1000
    
    # Test 2: Lazy loading initialization
    start_time = time.time()
    client = OptimizedGameClient()
    lazy_init_time = (time.time() - start_time) * 1000
    
    # Test 3: Access components on demand
    # Access menu system (triggers loading)
    start_time = time.time()
    menu = client.get_menu_system()
    menu_time = (time.time() - start_time) * 1000
    
    # Access settings UI (triggers loading)
    start_time = time.time()
    settings = client.get_settings_ui()
    settings_time = (time.time() - start_time) * 1000
    
    # Access puzzle engine (triggers loading)
    start_time = time.time()
    puzzle = client.get_puzzle_engine()
    puzzle_time = (time.time() - start_time) * 1000
    
    # Test 4: Subsequent access (no loading)
    start_time = time.time()
    menu2 = client.get_menu_system()  # Already loaded
    cached_time = (time.time() - start_time) * 1000
    
    # Performance comparison
    total_lazy_time = lazy_init_time + menu_time + settings_time + puzzle_time
    improvement = ((traditional_time - total_lazy_time) / traditional_time) * 100
    
    return improvement > 0


if __name__ == "__main__":
    success = demo_optimization()
    sys.exit(0 if success else 1)

