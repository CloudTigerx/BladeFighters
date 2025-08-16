"""
Modules Package for BladeFighters
================================

This package contains all the modular components of the BladeFighters game.
Each module is designed to be independent and testable.
"""

__version__ = "1.0.0"
__author__ = "BladeFighters Development Team"

# Back-compat export so tests can import `from modules.testmode_module import TestMode`
try:
	from .testmode_module.test_mode import TestModeRefactored as TestMode
except Exception:
	# Leave undefined if import fails; tests that need it will import directly
	pass

# Path shim: ensure repo root is importable so absolute imports like `core.puzzle_module` work in pytest
try:
	import os, sys
	repo_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
	if repo_root not in sys.path:
		sys.path.insert(0, repo_root)
except Exception:
	pass
