"""
Performance Tester Service - follows SRP.

This service is responsible only for performance testing.
"""

import time
from typing import Dict, Any, Callable, Union, Optional
import numpy as np


class PerformanceTester:
    """
    Tester for performance testing.
    
    Single Responsibility: Run performance tests and collect results.
    """

    def __init__(self) -> None:
        """Initialize performance tester"""
        pass

    def measure_action(
        self,
        action: Callable[[], None],
        name: Optional[str] = None,
        warmup_runs: int = 1,
        test_runs: int = 5
    ) -> Dict[str, Union[str, float]]:
        """
        Measure performance of a specific action

        Args:
            action: The callable to measure the performance of
            name: Optional name to use for the action in the results
            warmup_runs: The number of warmup runs to perform before measuring
            test_runs: The number of test runs to perform to measure performance

        Returns:
            Dictionary containing performance measurement results
        """
        if action is None:
            raise ValueError("Action cannot be None")
        if warmup_runs < 0:
            raise ValueError("Warmup runs must be non-negative")
        if test_runs <= 0:
            raise ValueError("Test runs must be positive")

        # Warmup runs
        for _ in range(warmup_runs):
            action()

        # Test runs
        times = []
        for _ in range(test_runs):
            start_time = time.time()
            action()
            end_time = time.time()
            times.append(end_time - start_time)

        return {
            'name': name or str(getattr(action, '__name__', 'unknown')),
            'min_time': min(times),
            'max_time': max(times),
            'avg_time': sum(times) / len(times),
            'std_dev': float(np.std(times)),
            'test_runs': test_runs,
            'warmup_runs': warmup_runs
        }

    def stress_test(
        self,
        action: Callable[[], None],
        duration: int = 60,
        interval: float = 0.1
    ) -> Dict[str, Union[float, bool]]:
        """
        Run stress test for specified duration

        Args:
            action: The callable to stress test
            duration: Total time in seconds to run the stress test
            interval: Time in seconds to wait between each action execution

        Returns:
            Dictionary containing stress test results
        """
        if action is None:
            raise ValueError("Action cannot be None")
        if duration <= 0:
            raise ValueError("Duration must be positive")
        if interval < 0:
            raise ValueError("Interval must be non-negative")

        end_time = time.time() + duration
        action_count = 0
        errors = 0
        times = []

        while time.time() < end_time:
            try:
                start_time = time.time()
                action()
                end_action_time = time.time()
                times.append(end_action_time - start_time)
                action_count += 1
            except Exception:
                errors += 1
            
            time.sleep(interval)

        return {
            'total_actions': action_count,
            'errors': errors,
            'success_rate': (action_count - errors) / max(action_count, 1),
            'avg_time': sum(times) / len(times) if times else 0,
            'min_time': min(times) if times else 0,
            'max_time': max(times) if times else 0,
            'duration': duration
        }

    def run_stress_test(
        self,
        action: Callable[[], None],
        duration: float
    ) -> Dict[str, Any]:
        """
        Run stress test for specified duration (interface compatibility method)

        Args:
            action: The callable to stress test
            duration: Total time in seconds to run the stress test

        Returns:
            Dictionary containing stress test results
        """
        return self.stress_test(action, int(duration), 0.1)

    def benchmark_actions(
        self,
        actions: Dict[str, Callable[[], None]],
        test_runs: int = 5
    ) -> Dict[str, Dict[str, Union[str, float]]]:
        """
        Benchmark multiple actions

        Args:
            actions: Dictionary mapping action names to callables
            test_runs: Number of test runs for each action

        Returns:
            Dictionary containing benchmark results for each action
        """
        if not actions:
            raise ValueError("Actions dictionary cannot be empty")
        if test_runs <= 0:
            raise ValueError("Test runs must be positive")

        results = {}
        for name, action in actions.items():
            results[name] = self.measure_action(action, name, warmup_runs=1, test_runs=test_runs)

        return results

    def compare_actions(
        self,
        actions: Dict[str, Callable[[], None]],
        test_runs: int = 5
    ) -> Dict[str, Any]:
        """
        Compare performance of multiple actions

        Args:
            actions: Dictionary mapping action names to callables
            test_runs: Number of test runs for each action

        Returns:
            Dictionary containing comparison results
        """
        benchmark_results = self.benchmark_actions(actions, test_runs)
        
        if not benchmark_results:
            return {}

        # Find fastest and slowest actions
        avg_times = {name: float(result['avg_time']) for name, result in benchmark_results.items()}
        if avg_times:
            fastest_action = min(avg_times.keys(), key=lambda k: avg_times[k])
            slowest_action = max(avg_times.keys(), key=lambda k: avg_times[k])
        else:
            fastest_action = None
            slowest_action = None

        # Calculate relative performance
        relative_performance = {}
        if fastest_action is not None and fastest_action in avg_times:
            fastest_time = avg_times[fastest_action]
            for name, avg_time in avg_times.items():
                if fastest_time > 0:
                    relative_performance[name] = avg_time / fastest_time
                else:
                    relative_performance[name] = 1.0
        else:
            # Если нет данных, устанавливаем все в 1.0
            for name in avg_times.keys():
                relative_performance[name] = 1.0

        return {
            'benchmark_results': benchmark_results,
            'fastest_action': fastest_action,
            'slowest_action': slowest_action,
            'relative_performance': relative_performance,
            'performance_ranking': sorted(avg_times.items(), key=lambda x: x[1])
        } 