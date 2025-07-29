"""
Memory Leak Detector Service - follows SRP.

This service is responsible only for detecting memory leaks.
"""

import time
from typing import Dict, Any, Callable, Tuple, Optional
import numpy as np
from ..interfaces.iapplication import IApplication


class MemoryLeakDetector:
    """
    Detector for memory leaks.
    
    Single Responsibility: Detect memory leaks in applications.
    """

    def __init__(self, application: Optional[IApplication] = None):
        """Initialize memory leak detector"""
        self.application = application

    def check_memory_leaks(
        self, 
        action: Callable[[], None], 
        num_iterations: int = 100,
        threshold_mb: float = 10.0
    ) -> Tuple[bool, float]:
        """
        Check for memory leaks using iterative action execution

        Args:
            action: The callable to test for memory leaks
            num_iterations: Number of iterations to run the action
            threshold_mb: Memory growth threshold in MB to consider as leak

        Returns:
            Tuple of (has_leak, memory_growth_mb)
        """
        if action is None:
            raise ValueError("Action cannot be None")
        if num_iterations <= 0:
            raise ValueError("Iterations must be positive")
        if threshold_mb < 0:
            raise ValueError("Threshold must be non-negative")

        # Record initial memory usage
        initial_memory = self._get_memory_usage()
        
        for _ in range(num_iterations):
            action()
            
        final_memory = self._get_memory_usage()
        memory_diff_mb = (final_memory - initial_memory) / (1024 * 1024)
        
        leak_detected = memory_diff_mb > threshold_mb
        
        return leak_detected, memory_diff_mb

    def memory_leak_test(
        self,
        action: Callable[[], None],
        num_iterations: int = 100,
        threshold_mb: float = 10.0
    ) -> Dict[str, Any]:
        """
        Comprehensive memory leak test

        Args:
            action: The callable to test for memory leaks
            num_iterations: Number of iterations to run the action
            threshold_mb: Memory growth threshold in MB to consider as leak

        Returns:
            Dictionary containing detailed memory leak analysis
        """
        if action is None:
            raise ValueError("Action cannot be None")
        if num_iterations <= 0:
            raise ValueError("Iterations must be positive")
        if threshold_mb < 0:
            raise ValueError("Threshold must be non-negative")

        threshold_bytes = threshold_mb * 1024 * 1024
        
        try:
            initial_memory = float(self._get_memory_usage())
        except (TypeError, ValueError):
            initial_memory = 0.0
            
        memory_usage = []
        
        for _ in range(num_iterations):
            action()
            try:
                current_memory = float(self._get_memory_usage())
            except (TypeError, ValueError):
                current_memory = initial_memory
            memory_usage.append(current_memory)
            
        if not memory_usage:
            return {
                'has_leak': False,
                'memory_growth_mb': 0.0,
                'growth_rate_mb_per_iteration': 0.0,
                'initial_memory_mb': 0.0,
                'final_memory_mb': 0.0,
                'memory_usage_history': []
            }
            
        memory_usage_array = np.array(memory_usage)
        memory_growth = memory_usage_array[-1] - initial_memory
        
        # Calculate growth rate using simple linear calculation
        if len(memory_usage) > 1:
            try:
                # Simple linear regression: slope = (y2-y1)/(x2-x1)
                x1, y1 = 0, memory_usage[0]
                x2, y2 = len(memory_usage) - 1, memory_usage[-1]
                slope = (y2 - y1) / (x2 - x1) if x2 != x1 else 0.0
            except Exception:
                slope = 0.0
        else:
            slope = 0.0
        
        return {
            'has_leak': memory_growth > threshold_bytes and slope > 0,
            'memory_growth_mb': memory_growth / (1024 * 1024),
            'growth_rate_mb_per_iteration': slope / (1024 * 1024),
            'initial_memory_mb': initial_memory / (1024 * 1024),
            'final_memory_mb': memory_usage[-1] / (1024 * 1024),
            'memory_usage_history': memory_usage_array.tolist(),
            'threshold_mb': threshold_mb,
            'iterations': num_iterations
        }

    def monitor_memory_growth(
        self,
        action: Callable[[], None],
        duration: int = 60,
        interval: float = 1.0
    ) -> Dict[str, Any]:
        """
        Monitor memory growth over time

        Args:
            action: The callable to monitor
            duration: Duration of monitoring in seconds
            interval: Interval between measurements in seconds

        Returns:
            Dictionary containing memory growth analysis
        """
        if action is None:
            raise ValueError("Action cannot be None")
        if duration <= 0:
            raise ValueError("Duration must be positive")
        if interval <= 0:
            raise ValueError("Interval must be positive")

        end_time = time.time() + duration
        memory_readings = []
        timestamps = []
        
        while time.time() < end_time:
            try:
                memory = float(self._get_memory_usage())
                memory_readings.append(memory)
                timestamps.append(time.time())
            except (TypeError, ValueError):
                memory_readings.append(0.0)
                timestamps.append(time.time())
                
            action()
            time.sleep(interval)
            
        if not memory_readings:
            return {
                'has_growth': False,
                'total_growth_mb': 0.0,
                'growth_rate_mb_per_second': 0.0,
                'memory_readings': [],
                'timestamps': []
            }
            
        memory_readings_array = np.array(memory_readings)
        timestamps_array = np.array(timestamps)
        
        # Calculate growth
        initial_memory = memory_readings_array[0]
        final_memory = memory_readings_array[-1]
        total_growth = final_memory - initial_memory
        
        # Calculate growth rate
        if len(timestamps_array) > 1:
            duration_seconds = timestamps_array[-1] - timestamps_array[0]
            growth_rate = total_growth / duration_seconds if duration_seconds > 0 else 0.0
        else:
            growth_rate = 0.0
            
        return {
            'has_growth': total_growth > 0,
            'total_growth_mb': total_growth / (1024 * 1024),
            'growth_rate_mb_per_second': growth_rate / (1024 * 1024),
            'initial_memory_mb': initial_memory / (1024 * 1024),
            'final_memory_mb': final_memory / (1024 * 1024),
            'memory_readings': memory_readings_array.tolist(),
            'timestamps': timestamps_array.tolist(),
            'duration_seconds': timestamps[-1] - timestamps[0] if len(timestamps) > 1 else 0.0
        }

    def _get_memory_usage(self) -> int:
        """Get current memory usage in bytes"""
        try:
            if self.application is None:
                return 0
            if getattr(self.application, 'process', None) is not None and self.application.process is not None:
                memory_info = self.application.process.memory_info()
            elif hasattr(self.application, 'memory_info'):
                memory_info = self.application.memory_info()
            else:
                return 0

            if memory_info is None:
                return 0

            rss = getattr(memory_info, 'rss', 0)
            if callable(rss):
                val = rss()
                if isinstance(val, (int, float)):
                    return int(val)
                return 0
            if isinstance(rss, (int, float)):
                return int(rss)
            return 0
        except Exception:
            return 0 