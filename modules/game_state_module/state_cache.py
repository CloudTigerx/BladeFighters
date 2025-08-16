"""
State Caching System
Optimizes state access by caching frequently used values and computed properties.
"""

import time
import threading
from typing import Dict, Any, Optional, Callable, Tuple, Union, List
from dataclasses import dataclass, field
from collections import OrderedDict
import weakref

from .state_schema import GameState
from modules.logging_module.logger import get_logger


@dataclass
class CacheEntry:
    """Represents a cached value with metadata."""
    value: Any
    timestamp: float
    ttl: float  # Time to live in seconds
    access_count: int = 0
    last_access: float = field(default_factory=time.time)
    dependencies: set = field(default_factory=set)
    computed: bool = False  # Whether this is a computed value


@dataclass
class ComputedProperty:
    """Represents a computed property that depends on other state fields."""
    name: str
    compute_func: Callable[[GameState], Any]
    dependencies: set
    ttl: float = 5.0  # Default 5 second TTL
    cache_size: int = 100  # Maximum number of cached values


class StateCache:
    """
    Intelligent caching system for game state values.
    Provides automatic invalidation, TTL management, and computed properties.
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: float = 10.0):
        self.max_size = max_size
        self.default_ttl = default_ttl
        self.logger = get_logger(__name__)
        
        # Cache storage
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._computed_properties: Dict[str, ComputedProperty] = {}
        
        # Performance tracking
        self._hits = 0
        self._misses = 0
        self._evictions = 0
        
        # Threading
        self._lock = threading.RLock()
        self._cleanup_thread = None
        self._cleanup_active = False
        
        # State change tracking
        self._last_state_hash = None
        self._state_change_callbacks: List[Callable[[str], None]] = []
        
        # Start cleanup thread
        self._start_cleanup_thread()
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get a value from cache."""
        with self._lock:
            if key in self._cache:
                entry = self._cache[key]
                
                # Check if expired
                if time.time() - entry.timestamp > entry.ttl:
                    del self._cache[key]
                    self._misses += 1
                    return default
                
                # Update access stats
                entry.access_count += 1
                entry.last_access = time.time()
                
                # Move to end (LRU)
                self._cache.move_to_end(key)
                
                self._hits += 1
                return entry.value
            else:
                self._misses += 1
                return default
    
    def set(self, key: str, value: Any, ttl: Optional[float] = None, 
            dependencies: Optional[set] = None) -> None:
        """Set a value in cache."""
        with self._lock:
            # Remove existing entry if present
            if key in self._cache:
                del self._cache[key]
            
            # Create new entry
            entry = CacheEntry(
                value=value,
                timestamp=time.time(),
                ttl=ttl or self.default_ttl,
                dependencies=dependencies or set()
            )
            
            # Add to cache
            self._cache[key] = entry
            
            # Enforce size limit
            if len(self._cache) > self.max_size:
                self._evict_oldest()
    
    def compute(self, key: str, compute_func: Callable[[GameState], Any], 
                dependencies: set, ttl: Optional[float] = None) -> Any:
        """Get or compute a value based on state."""
        with self._lock:
            # Check if we have a valid cached value
            if key in self._cache:
                entry = self._cache[key]
                if time.time() - entry.timestamp <= entry.ttl:
                    entry.access_count += 1
                    entry.last_access = time.time()
                    self._cache.move_to_end(key)
                    self._hits += 1
                    return entry.value
            
            # Compute new value
            try:
                # We need the current state to compute - this should be passed in practice
                # For now, we'll return None and let the caller handle it
                self._misses += 1
                return None
            except Exception as e:
                self.logger.error(f"Error computing cached value {key}: {e}")
                return None
    
    def invalidate(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        with self._lock:
            invalidated = 0
            keys_to_remove = []
            
            for key in self._cache:
                if pattern in key:
                    keys_to_remove.append(key)
                    invalidated += 1
            
            for key in keys_to_remove:
                del self._cache[key]
            
            return invalidated
    
    def invalidate_dependencies(self, dependencies: set) -> int:
        """Invalidate cache entries that depend on specific fields."""
        with self._lock:
            invalidated = 0
            keys_to_remove = []
            
            for key, entry in self._cache.items():
                if entry.dependencies & dependencies:
                    keys_to_remove.append(key)
                    invalidated += 1
            
            for key in keys_to_remove:
                del self._cache[key]
            
            return invalidated
    
    def register_computed_property(self, name: str, compute_func: Callable[[GameState], Any], 
                                 dependencies: set, ttl: float = 5.0) -> None:
        """Register a computed property that depends on specific state fields."""
        with self._lock:
            self._computed_properties[name] = ComputedProperty(
                name=name,
                compute_func=compute_func,
                dependencies=dependencies,
                ttl=ttl
            )
    
    def get_computed(self, name: str, state: GameState) -> Any:
        """Get a computed property value."""
        with self._lock:
            if name not in self._computed_properties:
                return None
            
            prop = self._computed_properties[name]
            cache_key = f"computed:{name}"
            
            # Check cache first
            if cache_key in self._cache:
                entry = self._cache[cache_key]
                if time.time() - entry.timestamp <= entry.ttl:
                    entry.access_count += 1
                    entry.last_access = time.time()
                    self._cache.move_to_end(cache_key)
                    self._hits += 1
                    return entry.value
            
            # Compute new value
            try:
                value = prop.compute_func(state)
                
                # Cache the result
                entry = CacheEntry(
                    value=value,
                    timestamp=time.time(),
                    ttl=prop.ttl,
                    dependencies=prop.dependencies,
                    computed=True
                )
                
                self._cache[cache_key] = entry
                self._misses += 1
                
                # Enforce size limit
                if len(self._cache) > self.max_size:
                    self._evict_oldest()
                
                return value
                
            except Exception as e:
                self.logger.error(f"Error computing property {name}: {e}")
                return None
    
    def on_state_change(self, changed_fields: set) -> None:
        """Called when state changes to invalidate dependent cache entries."""
        with self._lock:
            invalidated = self.invalidate_dependencies(changed_fields)
            if invalidated > 0:
                self.logger.debug(f"Invalidated {invalidated} cache entries due to state changes")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        with self._lock:
            total_requests = self._hits + self._misses
            hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
            
            # Calculate memory usage estimate
            memory_estimate = sum(
                len(str(entry.value)) + len(key) 
                for key, entry in self._cache.items()
            )
            
            return {
                'total_entries': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hits,
                'misses': self._misses,
                'hit_rate_percent': hit_rate,
                'evictions': self._evictions,
                'memory_estimate_bytes': memory_estimate,
                'computed_properties': len(self._computed_properties)
            }
    
    def clear(self) -> None:
        """Clear all cache entries."""
        with self._lock:
            self._cache.clear()
            self._hits = 0
            self._misses = 0
            self._evictions = 0
    
    def _evict_oldest(self) -> None:
        """Evict the oldest cache entry."""
        if self._cache:
            oldest_key = next(iter(self._cache))
            del self._cache[oldest_key]
            self._evictions += 1
    
    def _cleanup_expired(self) -> None:
        """Remove expired cache entries."""
        with self._lock:
            current_time = time.time()
            keys_to_remove = []
            
            for key, entry in self._cache.items():
                if current_time - entry.timestamp > entry.ttl:
                    keys_to_remove.append(key)
            
            for key in keys_to_remove:
                del self._cache[key]
    
    def _start_cleanup_thread(self) -> None:
        """Start background cleanup thread."""
        if self._cleanup_thread is None or not self._cleanup_thread.is_alive():
            self._cleanup_active = True
            self._cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
            self._cleanup_thread.start()
    
    def _cleanup_loop(self) -> None:
        """Background cleanup loop."""
        while self._cleanup_active:
            try:
                time.sleep(30.0)  # Clean up every 30 seconds
                self._cleanup_expired()
            except Exception as e:
                self.logger.error(f"Error in cleanup loop: {e}")
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self._cleanup_active = False
        if self._cleanup_thread and self._cleanup_thread.is_alive():
            self._cleanup_thread.join(timeout=1.0)


class StateCacheManager:
    """
    High-level cache manager that integrates with the game state manager.
    """
    
    def __init__(self, state_manager):
        self.state_manager = state_manager
        self.cache = StateCache()
        self.logger = get_logger(__name__)
        
        # Register common computed properties
        self._register_common_properties()
        
        # Register state change callback
        self.state_manager.add_global_callback(self._on_state_change)
    
    def _register_common_properties(self) -> None:
        """Register commonly used computed properties."""
        
        # Game state summary
        self.cache.register_computed_property(
            "game_state_summary",
            lambda state: {
                'screen': state.screen.current_screen.value,
                'game_active': state.puzzle.game_active,
                'score': state.puzzle.score,
                'level': state.puzzle.level,
                'fps': state.fps
            },
            {'screen.current_screen', 'puzzle.game_active', 'puzzle.score', 'puzzle.level', 'fps'},
            ttl=1.0
        )
        
        # Puzzle state summary
        self.cache.register_computed_property(
            "puzzle_state_summary",
            lambda state: {
                'active': state.puzzle.game_active,
                'mode': state.puzzle.game_mode.value,
                'state': state.puzzle.puzzle_state.value,
                'score': state.puzzle.score,
                'level': state.puzzle.level,
                'chain_count': state.puzzle.chain_count
            },
            {'puzzle.game_active', 'puzzle.game_mode', 'puzzle.puzzle_state', 
             'puzzle.score', 'puzzle.level', 'puzzle.chain_count'},
            ttl=0.5
        )
        
        # Audio state summary
        self.cache.register_computed_property(
            "audio_state_summary",
            lambda state: {
                'master_volume': state.audio.master_volume,
                'music_volume': state.audio.music_volume,
                'sfx_volume': state.audio.sfx_volume,
                'music_enabled': state.audio.music_enabled,
                'sfx_enabled': state.audio.sfx_enabled,
                'music_playing': state.audio.music_playing
            },
            {'audio.master_volume', 'audio.music_volume', 'audio.sfx_volume',
             'audio.music_enabled', 'audio.sfx_enabled', 'audio.music_playing'},
            ttl=2.0
        )
    
    def get_cached(self, key: str, default: Any = None) -> Any:
        """Get a cached value."""
        return self.cache.get(key, default)
    
    def set_cached(self, key: str, value: Any, ttl: Optional[float] = None, 
                   dependencies: Optional[set] = None) -> None:
        """Set a cached value."""
        self.cache.set(key, value, ttl, dependencies)
    
    def get_computed(self, name: str) -> Any:
        """Get a computed property value."""
        return self.cache.get_computed(name, self.state_manager.state)
    
    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate cache entries matching a pattern."""
        return self.cache.invalidate(pattern)
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """Get cache performance statistics."""
        return self.cache.get_stats()
    
    def _on_state_change(self, old_state: GameState, new_state: GameState) -> None:
        """Handle state changes by invalidating dependent cache entries."""
        # This is a simplified version - in practice, you'd track which fields actually changed
        # For now, we'll invalidate all computed properties
        changed_fields = {
            'screen.current_screen', 'puzzle.game_active', 'puzzle.score', 
            'puzzle.level', 'audio.master_volume', 'fps'
        }
        self.cache.on_state_change(changed_fields)


# Global cache manager instance
_global_cache_manager: Optional[StateCacheManager] = None


def get_state_cache_manager() -> Optional[StateCacheManager]:
    """Get the global state cache manager instance."""
    return _global_cache_manager


def set_global_cache_manager(cache_manager: StateCacheManager) -> None:
    """Set the global state cache manager instance."""
    global _global_cache_manager
    _global_cache_manager = cache_manager 