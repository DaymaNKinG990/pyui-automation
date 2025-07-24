"""
Performance Monitor Service - follows SRP.

This service is responsible only for collecting and storing performance metrics.
Uses utils.metrics.MetricsCollector as the underlying metrics storage.
Other responsibilities are delegated to specialized services.
"""

import time
import threading
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from ..interfaces.iapplication import IApplication
from ...utils.core import retry
from ...utils.validation import validate_number_range
from ...utils.metrics import MetricsCollector


@dataclass
class PerformanceMetric:
    """Performance metric data point - specialized for performance monitoring"""
    timestamp: float
    cpu_usage: float
    memory_usage: float
    response_time: float
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'timestamp': self.timestamp,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'response_time': self.response_time
        }


class PerformanceMonitor:
    """
    Monitor for collecting performance metrics.
    
    Single Responsibility: Collect and store performance metrics.
    Uses MetricsCollector for underlying storage and delegates analysis to specialized services.
    """

    def __init__(self, application: Optional[IApplication] = None) -> None:
        """Initialize performance monitor"""
        self.application = application
        self._metrics_collector = MetricsCollector()
        self.start_time = time.time()
        self.is_monitoring = False
        self.monitor_thread: Optional[threading.Thread] = None

    def start_monitoring(self, interval: float = 1.0) -> None:
        """Start collecting performance metrics"""
        if interval <= 0:
            raise ValueError("Interval must be positive")
            
        self._metrics_collector.clear()
        self.start_time = time.time()
        self.is_monitoring = True
        
        if interval > 0:
            def collect_metrics():
                while self.is_monitoring:
                    time.sleep(interval)
                    self.record_metric()
            
            self.monitor_thread = threading.Thread(target=collect_metrics)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

    @retry(attempts=3, delay=0.1)
    def record_metric(self, response_time: float = 0.0) -> None:
        """Record current performance metrics using MetricsCollector"""
        if not validate_number_range(response_time, min_value=0.0):
            response_time = 0.0
            
        try:
            cpu_usage = float(self._get_cpu_usage())
        except (TypeError, ValueError, Exception):
            cpu_usage = 0.0
            
        try:
            memory_usage = int(self._get_memory_usage())
        except (TypeError, ValueError, Exception):
            memory_usage = 0
            
        # Record metrics using MetricsCollector
        self._metrics_collector.record_value("cpu_usage", cpu_usage)
        self._metrics_collector.record_value("memory_usage", memory_usage)
        self._metrics_collector.record_value("response_time", float(response_time))
        self._metrics_collector.record_value("timestamp", time.time() - self.start_time)

    def stop_monitoring(self) -> List[PerformanceMetric]:
        """Stop monitoring and return collected metrics"""
        self.is_monitoring = False
        
        if self.monitor_thread and self.monitor_thread.is_alive():
            self.monitor_thread.join(timeout=1.0)
        
        return self.get_metrics()

    def stop_performance_monitoring(self) -> Dict[str, Any]:
        """Stop performance monitoring and return metrics as dictionary (for interface compatibility)"""
        metrics = self.stop_monitoring()
        
        # Convert metrics to dictionary format
        result: Dict[str, Any] = {
            'metrics': [metric.to_dict() for metric in metrics],
            'total_samples': len(metrics),
            'monitoring_duration': time.time() - self.start_time if self.start_time else 0.0
        }
        
        # Add statistics if available
        if metrics:
            cpu_values = [m.cpu_usage for m in metrics]
            memory_values = [m.memory_usage for m in metrics]
            response_values = [m.response_time for m in metrics]
            
            result['statistics'] = {
                'cpu_usage': {
                    'min': min(cpu_values),
                    'max': max(cpu_values),
                    'avg': sum(cpu_values) / len(cpu_values)
                },
                'memory_usage': {
                    'min': min(memory_values),
                    'max': max(memory_values),
                    'avg': sum(memory_values) / len(memory_values)
                },
                'response_time': {
                    'min': min(response_values),
                    'max': max(response_values),
                    'avg': sum(response_values) / len(response_values)
                }
            }
        
        return result

    def get_metrics(self) -> List[PerformanceMetric]:
        """Get all collected metrics"""
        # Convert MetricsCollector data to PerformanceMetric objects
        cpu_values = [point.value for point in self._metrics_collector._metrics.get("cpu_usage", [])]
        memory_values = [point.value for point in self._metrics_collector._metrics.get("memory_usage", [])]
        response_values = [point.value for point in self._metrics_collector._metrics.get("response_time", [])]
        timestamp_values = [point.value for point in self._metrics_collector._metrics.get("timestamp", [])]
        
        # Create PerformanceMetric objects
        metrics = []
        for i in range(len(cpu_values)):
            metric = PerformanceMetric(
                timestamp=timestamp_values[i] if i < len(timestamp_values) else 0.0,
                cpu_usage=cpu_values[i] if i < len(cpu_values) else 0.0,
                memory_usage=memory_values[i] if i < len(memory_values) else 0,
                response_time=response_values[i] if i < len(response_values) else 0.0
            )
            metrics.append(metric)
        
        return metrics

    def clear_metrics(self) -> None:
        """Clear all collected metrics"""
        self._metrics_collector.clear()

    def get_metrics_collector(self) -> MetricsCollector:
        """Get underlying MetricsCollector for advanced operations"""
        return self._metrics_collector

    def get_performance_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics using MetricsCollector"""
        return {
            "cpu_usage": self._metrics_collector.get_stats("cpu_usage"),
            "memory_usage": self._metrics_collector.get_stats("memory_usage"),
            "response_time": self._metrics_collector.get_stats("response_time")
        }

    def start_performance_timer(self, name: str) -> None:
        """Start a performance timer"""
        self._metrics_collector.start_timer(name)

    def stop_performance_timer(self, name: str) -> Optional[float]:
        """Stop a performance timer and return duration"""
        return self._metrics_collector.stop_timer(name)

    def record_custom_metric(self, name: str, value: float) -> None:
        """Record a custom performance metric"""
        self._metrics_collector.record_value(name, value)

    def _get_cpu_usage(self) -> float:
        """Get current CPU usage percentage"""
        try:
            if self.application is None:
                return 0.0
            if hasattr(self.application, 'cpu_percent'):
                return self.application.cpu_percent()
            elif hasattr(self.application, 'process') and self.application.process is not None:
                return self.application.process.cpu_percent()
            else:
                return 0.0
        except Exception:
            return 0.0

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