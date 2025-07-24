"""
Performance Analyzer Service - follows SRP.

This service is responsible only for analyzing performance metrics.
"""

import time
from typing import Dict, List, Any, Callable
import numpy as np
from dataclasses import dataclass
from .performance_monitor import PerformanceMetric


@dataclass
class PerformanceStats:
    """Performance statistics"""
    min_value: float
    max_value: float
    avg_value: float
    std_dev: float
    count: int


class PerformanceAnalyzer:
    """
    Analyzer for performance metrics.
    
    Single Responsibility: Analyze performance metrics and provide statistics.
    """

    def __init__(self):
        """Initialize performance analyzer"""
        pass

    def analyze_metrics(self, metrics: List[PerformanceMetric]) -> Dict[str, PerformanceStats]:
        """Analyze collected metrics and return statistics"""
        if not metrics:
            return {
                'cpu_usage': PerformanceStats(0, 0, 0, 0, 0),
                'memory_usage': PerformanceStats(0, 0, 0, 0, 0),
                'response_time': PerformanceStats(0, 0, 0, 0, 0)
            }

        cpu_metrics = [m.cpu_usage for m in metrics]
        memory_metrics = [m.memory_usage for m in metrics]
        response_metrics = [m.response_time for m in metrics]

        result = {}
        for name, values in [
            ('cpu_usage', cpu_metrics),
            ('memory_usage', memory_metrics),
            ('response_time', response_metrics)
        ]:
            result[name] = PerformanceStats(
                min_value=min(values),
                max_value=max(values),
                avg_value=sum(values) / len(values),
                std_dev=float(np.std(values)) if len(values) > 1 else 0.0,
                count=len(values)
            )

        return result

    def get_average_metrics(self, metrics: List[PerformanceMetric]) -> Dict[str, float]:
        """Get average performance metrics"""
        if not metrics:
            return {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'response_time': 0.0,
                'duration': 0.0
            }

        cpu_values = [float(m.cpu_usage) for m in metrics]
        memory_values = [int(m.memory_usage) for m in metrics]
        response_values = [float(m.response_time) for m in metrics]

        return {
            'cpu_usage': sum(cpu_values) / len(cpu_values) if cpu_values else 0.0,
            'memory_usage': sum(memory_values) / len(memory_values) if memory_values else 0.0,
            'response_time': sum(response_values) / len(response_values) if response_values else 0.0,
            'duration': metrics[-1].timestamp if metrics else 0.0
        }

    def get_metrics_history(self, metrics: List[PerformanceMetric]) -> Dict[str, List[float]]:
        """Get history of all recorded metrics"""
        if not metrics:
            return {
                'cpu_usage_history': [],
                'memory_usage_history': [],
                'response_time_history': [],
                'timestamps': []
            }
            
        return {
            'cpu_usage_history': [m.cpu_usage for m in metrics],
            'memory_usage_history': [m.memory_usage for m in metrics],
            'response_time_history': [m.response_time for m in metrics],
            'timestamps': [m.timestamp for m in metrics]
        }

    def detect_regression(
        self,
        action: Callable,
        baseline_metrics: Dict[str, Dict[str, float]],
        test_runs: int = 5,
        threshold_std: float = 2.0
    ) -> Dict[str, Any]:
        """Detect performance regression against baseline metrics"""
        current_metrics = {'response_time': [], 'memory_usage': [], 'cpu_usage': []}
        
        # Run the action multiple times and collect metrics
        for _ in range(test_runs):
            start_time = time.time()
            action()
            response_time = time.time() - start_time
            
            current_metrics['response_time'].append(response_time)
            # Note: This would need application reference for real implementation
            current_metrics['memory_usage'].append(0)
            current_metrics['cpu_usage'].append(0)
        
        # Calculate averages of current metrics
        avg_metrics = {
            metric: sum(values) / len(values)
            for metric, values in current_metrics.items()
        }
        
        # Calculate deviations from baseline
        deviations = {}
        has_regression = False
        
        for metric in baseline_metrics:
            if metric in avg_metrics:
                baseline_avg = baseline_metrics[metric]['avg']
                baseline_std = baseline_metrics[metric]['std']
                current_avg = avg_metrics[metric]
                
                if baseline_std > 0:
                    deviation = (current_avg - baseline_avg) / baseline_std
                    deviations[metric] = deviation
                    
                    if deviation > threshold_std:
                        has_regression = True
        
        return {
            'has_regression': has_regression,
            'metrics': avg_metrics,
            'deviations': deviations
        }

    def check_thresholds(
        self, 
        metrics: List[PerformanceMetric], 
        thresholds: Dict[str, float]
    ) -> Dict[str, bool]:
        """Check if any metrics exceed their thresholds"""
        if not thresholds or not metrics:
            return {}

        latest = metrics[-1]
        result = {}

        if 'cpu_usage' in thresholds:
            try:
                cpu_usage = float(latest.cpu_usage)
                result['cpu_usage'] = cpu_usage > thresholds['cpu_usage']
            except (TypeError, ValueError):
                result['cpu_usage'] = False

        if 'memory_usage' in thresholds:
            try:
                memory_usage = float(latest.memory_usage)
                result['memory_usage'] = memory_usage > thresholds['memory_usage']
            except (TypeError, ValueError):
                result['memory_usage'] = False

        if 'response_time' in thresholds:
            try:
                response_time = float(latest.response_time)
                result['response_time'] = response_time > thresholds['response_time']
            except (TypeError, ValueError):
                result['response_time'] = False

        return result 