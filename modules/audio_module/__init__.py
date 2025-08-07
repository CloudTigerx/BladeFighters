"""
Audio Module for Blade Fighters
===============================

Extracted audio system providing sound effects and music playback functionality.

This module was extracted from the monolithic architecture during Phase 1 refactoring
to create a clean, modular audio system with well-defined interfaces.

Author: Blade Fighters Refactoring Team
Version: 1.0.0
Extraction Date: Phase 1 Refactoring
"""

from .audio_system import AudioSystem
from .mp3_player import MP3Player

# Version information
__version__ = "1.0.0"
__author__ = "Blade Fighters Refactoring Team"
__status__ = "Extracted from Monolith"

# Public API exports
__all__ = [
    'AudioSystem',
    'MP3Player'
]

# Module metadata for dependency tracking
MODULE_INFO = {
    'name': 'audio_module',
    'version': __version__,
    'dependencies': [
        'pygame',
        'os', 
        'random',
        'time'
    ],
    'extracted_from': 'monolithic_architecture',
    'extraction_phase': 'phase_1',
    'test_coverage': '100%',
    'interface_contract': 'audio_interface_contract.py'
} 