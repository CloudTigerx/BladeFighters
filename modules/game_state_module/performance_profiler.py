"""
Performance Profiler for State Management
Monitors and optimizes state change performance, memory usage, and frame rate impact.
"""

import time
import psutil
import threading
from typing import Dict, List, Any, Optional, Callable, Tuple
from dataclasses import dataclass, field
from collections import defaultdict, deque
import statistics
import gc
import weakref

from .state_schema import GameState
from modules.logging_module.logger import get_logger


@dataclass
class PerformanceMetrics:
    """Performance metrics for a specific operation."""
    operation_name: str
    total_calls: int = 0
    total_time: float = 0.0
    min_time: float = float('inf')
    max_time: float = 0.0
    avg_time: float = 0.0
    last_call_time: float = 0.0
    memory_before: int = 0
    memory_after: int = 0
    memory_delta: int = 0


@dataclass
class StateChangeMetrics:
    """Metrics for state change operations."""
    field_path: str
    change_count: int = 0
    total_time: float = 0.0
    avg_time: float = 0.0
    last_change_time: float = 0.0
    frequency_per_second: float = 0.0
    memory_impact: int = 0


@dataclass
class FrameMetrics:
    """Frame-by-frame performance metrics."""
    frame_number: int
    timestamp: float
    frame_time: float
    state_changes: int
    memory_usage: int
    cpu_usage: float
    gc_collections: int
    gc_time: float


class PerformanceProfiler:
    """
    Comprehensive performance profiler for state management optimization.
    """
    
    def __init__(self, enabled: bool = True, max_history: int = 1000):
        self.enabled = enabled
        self.logger = get_logger(__name__)
        
        # Performance tracking
        self.metrics: Dict[str, PerformanceMetrics] = {}
        self.state_change_metrics: Dict[str, StateChangeMetrics] = {}
        self.frame_metrics: deque = deque(maxlen=max_history)
        
        # Memory tracking
        self.memory_history: deque = deque(maxlen=max_history)
        self.gc_stats = {
            'collections': 0,
            'total_time': 0.0,
            'last_collection_time': 0.0
        }
        
        # Frame rate tracking
        self.frame_times: deque = deque(maxlen=60)  # Last 60 frames
        self.last_frame_time = time.time()
        self.frame_count = 0
        
        # State change frequency tracking
        self.state_changes_per_frame: deque = deque(maxlen=60)
        self.current_frame_changes = 0
        
        # Callbacks
        self.performance_callbacks: List[Callable[[Dict[str, Any]], None]] = []
        
        # Threading
        self._lock = threading.RLock()
        self._monitoring_thread = None
        self._monitoring_active = False
        
        # Optimization settings
        self.optimization_enabled = True
        self.memory_threshold_mb = 100  # Alert if memory usage increases by 100MB
        self.frame_time_threshold_ms = 16.67  # Alert if frame time exceeds 60 FPS threshold
        self.state_change_threshold = 50  # Alert if more than 50 state changes per frame
        
        # Initialize monitoring
        if self.enabled:
            self._start_monitoring()
    
    def start_operation(self, operation_name: str) -> None:
        """Start timing an operation."""
        if not self.enabled:
            return
        
        with self._lock:
            if operation_name not in self.metrics:
                self.metrics[operation_name] = PerformanceMetrics(operation_name)
            
            metric = self.metrics[operation_name]
            metric.memory_before = self._get_memory_usage()
            metric.last_call_time = time.time()
    
    def end_operation(self, operation_name: str) -> None:
        """End timing an operation."""
        if not self.enabled:
            return
        
        with self._lock:
            if operation_name not in self.metrics:
                return
            
            end_time = time.time()
            metric = self.metrics[operation_name]
            
            duration = end_time - metric.last_call_time
            metric.total_calls += 1
            metric.total_time += duration
            metric.min_time = min(metric.min_time, duration)
            metric.max_time = max(metric.max_time, duration)
            metric.avg_time = metric.total_time / metric.total_calls
            
            metric.memory_after = self._get_memory_usage()
            metric.memory_delta = metric.memory_after - metric.memory_before
    
    def record_state_change(self, field_path: str, duration: float, memory_impact: int = 0) -> None:
        """Record a state change operation."""
        if not self.enabled:
            return
        
        with self._lock:
            if field_path not in self.state_change_metrics:
                self.state_change_metrics[field_path] = StateChangeMetrics(field_path)
            
            metric = self.state_change_metrics[field_path]
            metric.change_count += 1
            metric.total_time += duration
            metric.avg_time = metric.total_time / metric.change_count
            metric.last_change_time = time.time()
            metric.memory_impact += memory_impact
            
            # Update frame-level tracking
            self.current_frame_changes += 1
    
    def record_frame(self) -> None:
        """Record frame-level metrics."""
        if not self.enabled:
            return
        
        current_time = time.time()
        frame_time = current_time - self.last_frame_time
        
        with self._lock:
            # Update frame tracking
            self.frame_count += 1
            self.frame_times.append(frame_time)
            self.state_changes_per_frame.append(self.current_frame_changes)
            
            # Record frame metrics
            frame_metric = FrameMetrics(
                frame_number=self.frame_count,
                timestamp=current_time,
                frame_time=frame_time,
                state_changes=self.current_frame_changes,
                memory_usage=self._get_memory_usage(),
                cpu_usage=self._get_cpu_usage(),
                gc_collections=self.gc_stats['collections'],
                gc_time=self.gc_stats['total_time']
            )
            self.frame_metrics.append(frame_metric)
            
            # Update memory history
            self.memory_history.append({
                'timestamp': current_time,
                'memory_mb': frame_metric.memory_usage / (1024 * 1024),
                'frame_number': self.frame_count
            })
            
            # Reset frame counters
            self.current_frame_changes = 0
            self.last_frame_time = current_time
            
            # Check for performance issues
            self._check_performance_alerts(frame_metric)
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get a comprehensive performance summary."""
        with self._lock:
            # Calculate frame rate metrics
            if self.frame_times:
                avg_frame_time = statistics.mean(self.frame_times)
                fps = 1.0 / avg_frame_time if avg_frame_time > 0 else 0
                min_fps = 1.0 / max(self.frame_times) if self.frame_times else 0
                max_fps = 1.0 / min(self.frame_times) if self.frame_times else 0
            else:
                fps = min_fps = max_fps = 0
            
            # Calculate state change frequency
            if self.state_changes_per_frame:
                avg_changes_per_frame = statistics.mean(self.state_changes_per_frame)
                max_changes_per_frame = max(self.state_changes_per_frame)
            else:
                avg_changes_per_frame = max_changes_per_frame = 0
            
            # Get memory usage
            current_memory = self._get_memory_usage()
            memory_mb = current_memory / (1024 * 1024)
            
            # Get most expensive operations
            expensive_operations = sorted(
                self.metrics.values(),
                key=lambda m: m.total_time,
                reverse=True
            )[:5]
            
            # Get most changed fields
            most_changed_fields = sorted(
                self.state_change_metrics.values(),
                key=lambda m: m.change_count,
                reverse=True
            )[:5]
            
            return {
                'frame_rate': {
                    'current_fps': fps,
                    'min_fps': min_fps,
                    'max_fps': max_fps,
                    'avg_frame_time_ms': avg_frame_time * 1000 if self.frame_times else 0,
                    'frame_count': self.frame_count
                },
                'state_changes': {
                    'avg_per_frame': avg_changes_per_frame,
                    'max_per_frame': max_changes_per_frame,
                    'total_fields_tracked': len(self.state_change_metrics)
                },
                'memory': {
                    'current_mb': memory_mb,
                    'peak_mb': max([h['memory_mb'] for h in self.memory_history]) if self.memory_history else 0,
                    'history_count': len(self.memory_history)
                },
                'expensive_operations': [
                    {
                        'name': op.operation_name,
                        'total_calls': op.total_calls,
                        'total_time': op.total_time,
                        'avg_time': op.avg_time,
                        'memory_delta': op.memory_delta
                    }
                    for op in expensive_operations
                ],
                'most_changed_fields': [
                    {
                        'field_path': field.field_path,
                        'change_count': field.change_count,
                        'avg_time': field.avg_time,
                        'frequency_per_second': field.frequency_per_second
                    }
                    for field in most_changed_fields
                ],
                'gc_stats': self.gc_stats.copy()
            }
    
    def get_optimization_recommendations(self) -> List[str]:
        """Get performance optimization recommendations."""
        recommendations = []
        summary = self.get_performance_summary()
        
        # Frame rate recommendations
        if summary['frame_rate']['current_fps'] < 55:
            recommendations.append(
                f"Low frame rate detected: {summary['frame_rate']['current_fps']:.1f} FPS. "
                "Consider reducing state change frequency or optimizing expensive operations."
            )
        
        # State change frequency recommendations
        if summary['state_changes']['avg_per_frame'] > 20:
            recommendations.append(
                f"High state change frequency: {summary['state_changes']['avg_per_frame']:.1f} per frame. "
                "Consider batching state changes or reducing update frequency."
            )
        
        # Memory recommendations
        if summary['memory']['current_mb'] > 500:
            recommendations.append(
                f"High memory usage: {summary['memory']['current_mb']:.1f} MB. "
                "Consider implementing state cleanup or reducing history size."
            )
        
        # Operation-specific recommendations
        for op in summary['expensive_operations']:
            if op['avg_time'] > 0.001:  # More than 1ms average
                recommendations.append(
                    f"Slow operation detected: {op['name']} takes {op['avg_time']*1000:.2f}ms average. "
                    "Consider optimization or caching."
                )
        
        return recommendations
    
    def optimize_state_management(self, state_manager) -> Dict[str, Any]:
        """Apply automatic optimizations to state management."""
        optimizations = {}
        summary = self.get_performance_summary()
        
        # Optimize snapshot frequency based on state change rate
        if summary['state_changes']['avg_per_frame'] > 10:
            # Reduce snapshot frequency for high-change scenarios
            if hasattr(state_manager, 'history') and hasattr(state_manager.history, 'max_snapshots'):
                old_max = state_manager.history.max_snapshots
                new_max = max(20, old_max // 2)
                state_manager.history.max_snapshots = new_max
                optimizations['reduced_snapshots'] = f"{old_max} -> {new_max}"
        
        # Optimize change history size
        if summary['memory']['current_mb'] > 300:
            if hasattr(state_manager, 'history') and hasattr(state_manager.history, 'max_changes'):
                old_max = state_manager.history.max_changes
                new_max = max(500, old_max // 2)
                state_manager.history.max_changes = new_max
                optimizations['reduced_changes'] = f"{old_max} -> {new_max}"
        
        # Force garbage collection if memory usage is high
        if summary['memory']['current_mb'] > 400:
            gc.collect()
            optimizations['forced_gc'] = "Memory cleanup performed"
        
        return optimizations
    
    def add_performance_callback(self, callback: Callable[[Dict[str, Any]], None]) -> None:
        """Add a callback for performance alerts."""
        self.performance_callbacks.append(callback)
    
    def _start_monitoring(self) -> None:
        """Start background monitoring thread."""
        if self._monitoring_thread is None or not self._monitoring_thread.is_alive():
            self._monitoring_active = True
            self._monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self._monitoring_thread.start()
    
    def _monitoring_loop(self) -> None:
        """Background monitoring loop."""
        while self._monitoring_active:
            try:
                time.sleep(1.0)  # Check every second
                
                # Update GC stats
                gc_stats = gc.get_stats()
                if gc_stats:
                    self.gc_stats['collections'] = sum(stat['collections'] for stat in gc_stats)
                    # Note: GC collection time is not available in all Python versions
                    # We'll keep the existing total_time value
                
                # Update state change frequencies
                current_time = time.time()
                for metric in self.state_change_metrics.values():
                    if metric.last_change_time > 0:
                        time_since_last = current_time - metric.last_change_time
                        if time_since_last > 0:
                            metric.frequency_per_second = 1.0 / time_since_last
                
            except Exception as e:
                self.logger.error(f"Error in monitoring loop: {e}")
    
    def _check_performance_alerts(self, frame_metric: FrameMetrics) -> None:
        """Check for performance issues and trigger alerts."""
        alerts = {}
        
        # Frame time alerts
        if frame_metric.frame_time * 1000 > self.frame_time_threshold_ms:
            alerts['frame_time'] = f"Frame time {frame_metric.frame_time*1000:.2f}ms exceeds threshold"
        
        # Memory alerts
        memory_mb = frame_metric.memory_usage / (1024 * 1024)
        if len(self.memory_history) > 1:
            recent_memory = [h['memory_mb'] for h in list(self.memory_history)[-10:]]
            if max(recent_memory) - min(recent_memory) > self.memory_threshold_mb:
                alerts['memory'] = f"Memory usage increased by {max(recent_memory) - min(recent_memory):.1f}MB"
        
        # State change alerts
        if frame_metric.state_changes > self.state_change_threshold:
            alerts['state_changes'] = f"{frame_metric.state_changes} state changes in one frame"
        
        # Trigger callbacks
        if alerts:
            for callback in self.performance_callbacks:
                try:
                    callback(alerts)
                except Exception as e:
                    self.logger.error(f"Error in performance callback: {e}")
    
    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes."""
        try:
            process = psutil.Process()
            return process.memory_info().rss
        except Exception:
            return 0
    
    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage."""
        try:
            return psutil.cpu_percent(interval=0.1)
        except Exception:
            return 0.0
    
    def cleanup(self) -> None:
        """Clean up resources."""
        self._monitoring_active = False
        if self._monitoring_thread and self._monitoring_thread.is_alive():
            self._monitoring_thread.join(timeout=1.0)


# Global profiler instance
_global_profiler: Optional[PerformanceProfiler] = None


def get_performance_profiler() -> PerformanceProfiler:
    """Get the global performance profiler instance."""
    global _global_profiler
    if _global_profiler is None:
        _global_profiler = PerformanceProfiler()
    return _global_profiler


def set_global_profiler(profiler: PerformanceProfiler) -> None:
    """Set the global performance profiler instance."""
    global _global_profiler
    _global_profiler = profiler 