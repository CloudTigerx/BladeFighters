"""
Core package initializer to allow imports like `core.puzzle_module` during tests.
"""

from .cluster_detection import ClusterDetector

__all__ = ['ClusterDetector']
