import time
from typing import Dict, List, Optional, Tuple, Callable, Any, Union
import psutil
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np  # Импортируем numpy глобально
from dataclasses import dataclass
from .application import Application

@dataclass
class PerformanceMetric:
    timestamp: float
    cpu_usage: float
    memory_usage: float
    response_time: float


class PerformanceMonitor:
    """
    Monitor and analyze application performance.

    Сбор и анализ метрик производительности приложения: CPU, память, время отклика, пользовательские метрики.
    Используется сервисным слоем PerformanceService.

    Example usage:
        monitor = PerformanceMonitor(app)
        monitor.start_monitoring(interval=1.0)
        # ... действия ...
        metrics = monitor.stop_monitoring()
        monitor.generate_report("reports/perf.html")

    Назначение:
        - Сбор и анализ производительности
        - Генерация HTML-отчёта
        - Интеграция с сервисным слоем
    """

    def __init__(self, application) -> None:
        """
        Initialize PerformanceMonitor object

        Args:
            application: The application to monitor
        """
        self.application = application
        self.metrics: List[PerformanceMetric] = []
        self.start_time = time.time()
        self.is_monitoring = False

    def start_monitoring(self, interval: float = 1.0) -> None:
        """
        Start collecting performance metrics

        This method starts collecting performance metrics for the application.
        The metrics are collected at the specified interval until the stop_monitoring
        method is called.

        Args:
            interval: Time between metric collections in seconds
        """
        self.metrics = []  # Clear any existing metrics
        self.start_time = time.time()
        self.is_monitoring = True
        # Не вызываем self.record_metric() здесь
        # Schedule next metric collection if interval is specified
        if interval > 0:
            def collect_metrics():
                while self.is_monitoring:
                    time.sleep(interval)
                    self.record_metric()
            
            import threading
            self.monitor_thread = threading.Thread(target=collect_metrics)
            self.monitor_thread.daemon = True
            self.monitor_thread.start()

    def record_metric(self, response_time: float = 0.0) -> None:
        """
        Record current performance metrics

        This method records the current performance metrics of the application.
        The metrics include CPU usage, memory usage, and response time. The
        response time is an optional argument and defaults to 0.0 if not
        provided.

        Args:
            response_time: The response time to record
        """
        # Разрешаем ручной вызов для тестов, даже если is_monitoring == False
        if not hasattr(self, 'metrics'):
            self.metrics = []
        # Get CPU usage
        try:
            cpu_usage = float(self.get_cpu_usage())
        except (TypeError, ValueError, Exception):
            cpu_usage = 0.0
        # Get memory usage
        try:
            memory_usage = int(self.get_memory_usage())
        except (TypeError, ValueError, Exception):
            memory_usage = 0
        metric = PerformanceMetric(
            timestamp=time.time() - self.start_time,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            response_time=float(response_time)
        )
        self.metrics.append(metric)

    def get_average_metrics(self) -> Dict[str, float]:
        """
        Get average performance metrics

        This method returns the average performance metrics of the application
        during the monitoring session. The metrics include CPU usage, memory
        usage, response time, and duration. The duration is calculated from the
        start of the monitoring session to the current time.

        If the monitoring session is not running, the returned metrics are all
        0.0.
        """
        if not self.metrics:
            return {
                'cpu_usage': 0.0,
                'memory_usage': 0.0,
                'response_time': 0.0,
                'duration': time.time() - self.start_time
            }

        # Convert all metrics to proper numeric types
        cpu_values = []
        memory_values = []
        response_values = []

        for metric in self.metrics:
            try:
                cpu_values.append(float(metric.cpu_usage))
            except (TypeError, ValueError):
                cpu_values.append(0.0)

            try:
                memory_values.append(int(metric.memory_usage))
            except (TypeError, ValueError):
                memory_values.append(0)

            try:
                response_values.append(float(metric.response_time))
            except (TypeError, ValueError):
                response_values.append(0.0)

        return {
            'cpu_usage': sum(cpu_values) / len(cpu_values) if cpu_values else 0.0,
            'memory_usage': sum(memory_values) / len(memory_values) if memory_values else 0.0,
            'response_time': sum(response_values) / len(response_values) if response_values else 0.0,
            'duration': time.time() - self.start_time
        }

    def get_metrics_history(self) -> Dict[str, List[float]]:
        """
        Get history of all recorded metrics

        This method returns a dictionary containing the history of all recorded
        metrics. The dictionary contains the following keys:

        - cpu_usage_history: A list of CPU usage metrics recorded during the
          monitoring session.
        - memory_usage_history: A list of memory usage metrics recorded during
          the monitoring session.
        - response_time_history: A list of response time metrics recorded during
          the monitoring session.
        - timestamps: A list of timestamps at which the metrics were recorded.

        If no metrics have been recorded, an empty dictionary is returned.
        """
        if not self.metrics:
            return {
                'cpu_usage_history': [],
                'memory_usage_history': [],
                'response_time_history': [],
                'timestamps': []
            }
            
        return {
            'cpu_usage_history': [m.cpu_usage for m in self.metrics],
            'memory_usage_history': [m.memory_usage for m in self.metrics],
            'response_time_history': [m.response_time for m in self.metrics],
            'timestamps': [m.timestamp for m in self.metrics]
        }

    def stop_monitoring(self) -> Dict[str, Any]:
        """Stop monitoring and return metrics
        
        Returns:
            Dictionary containing:
            - Average metrics (cpu_usage, memory_usage, response_time)
            - Duration of monitoring session
            - History metrics (cpu_usage_history, memory_usage_history, etc.)
        """
        self.is_monitoring = False
        metrics = self.get_average_metrics()
        history = self.get_metrics_history()
        return {**metrics, **history}

    def get_cpu_usage(self) -> float:
        """Get current CPU usage percentage

        Returns:
            float: CPU usage percentage, or 0.0 if not available.
        """
        try:
            # Access the process directly since it's a mock in tests
            if hasattr(self.application, 'cpu_percent'):
                return self.application.cpu_percent()
            else:
                return self.application.process.cpu_percent()
        except (psutil.NoSuchProcess, AttributeError, Exception):
            return 0.0

    def get_memory_usage(self) -> int:
        """
        Get current memory usage in bytes

        Returns:
            int: Memory usage in bytes, or 0 if not available.
        """
        try:
            # Get memory info from the appropriate source
            if getattr(self.application, 'process', None) is not None:
                memory_info = self.application.process.memory_info()
            else:
                memory_info = self.application.memory_info()

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

    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect all performance metrics

        Returns:
            Dict[str, Any]: Current performance metrics
        """
        try:
            cpu_usage = self.get_cpu_usage()
        except Exception:
            cpu_usage = 0.0

        try:
            memory_usage = self.get_memory_usage()
        except Exception:
            memory_usage = 0

        return {
            'cpu_usage': cpu_usage,
            'memory_usage': memory_usage,
            'timestamp': time.time()
        }

    def check_thresholds(self) -> Dict[str, bool]:
        """
        Check if any metrics exceed their thresholds

        Returns:
            Dictionary mapping metric names to boolean indicating if threshold was exceeded
        """
        if not hasattr(self, 'thresholds') or not self.metrics:
            return {}

        latest = self.metrics[-1]
        result = {}

        if 'cpu_usage' in self.thresholds:
            try:
                cpu_usage = float(latest.cpu_usage)
                result['cpu_usage'] = cpu_usage > self.thresholds['cpu_usage']
            except (TypeError, ValueError):
                result['cpu_usage'] = False

        if 'memory_usage' in self.thresholds:
            try:
                memory_usage = float(latest.memory_usage)
                result['memory_usage'] = memory_usage > self.thresholds['memory_usage']
            except (TypeError, ValueError):
                result['memory_usage'] = False

        if 'response_time' in self.thresholds:
            try:
                response_time = float(latest.response_time)
                result['response_time'] = response_time > self.thresholds['response_time']
            except (TypeError, ValueError):
                result['response_time'] = False

        return result

    def analyze_metrics(self) -> Dict[str, Dict[str, float]]:
        """
        Analyze collected metrics and return statistics

        Returns:
            Dictionary containing metric statistics
        """
        if not self.metrics:
            return {
                'cpu_usage': {'min': 0, 'max': 0, 'avg': 0, 'std': 0},
                'memory_usage': {'min': 0, 'max': 0, 'avg': 0, 'std': 0},
                'response_time': {'min': 0, 'max': 0, 'avg': 0, 'std': 0}
            }

        cpu_metrics = [m.cpu_usage for m in self.metrics]
        memory_metrics = [m.memory_usage for m in self.metrics]
        response_metrics = [m.response_time for m in self.metrics]

        result = {}
        for name, values in [
            ('cpu_usage', cpu_metrics),
            ('memory_usage', memory_metrics),
            ('response_time', response_metrics)
        ]:
            result[name] = {
                'min': min(values),
                'max': max(values),
                'avg': sum(values) / len(values),
                'std': np.std(values) if len(values) > 1 else 0
            }

        return result

    def export_metrics(self, file_path: Union[str, Path]) -> None:
        """
        Export metrics to JSON file

        Args:
            file_path: Path to save metrics JSON file
        """
        metrics_data = {
            'metrics': [
                {
                    'timestamp': m.timestamp,
                    'cpu_usage': m.cpu_usage,
                    'memory_usage': m.memory_usage,
                    'response_time': m.response_time
                }
                for m in self.metrics
            ],
            'analysis': self.analyze_metrics()
        }

        with open(file_path, 'w') as f:
            json.dump(metrics_data, f, indent=2)

    def measure_response_time(self, action: Callable) -> float:
        """
        Measure response time of an action

        This method measures the time it takes for the given action to execute.
        It returns the time taken in seconds as a float.

        Args:
            action: The callable to measure the response time of.

        Returns:
            float: The time taken to execute the action in seconds.
        """
        start_time = time.time()
        action()
        return time.time() - start_time

    def measure_operation_time(self, operation: Callable) -> Tuple[Any, float]:
        """
        Measure execution time of an operation

        This method measures the time it takes to execute the given operation.
        It returns a tuple containing the result of the operation and the time taken
        to execute the operation in seconds as a float.

        Args:
            operation: The callable to measure the execution time of.

        Returns:
            Tuple[Any, float]: A tuple containing the result of the operation and the
                time taken to execute the operation in seconds.
        """
        start_time = time.time()
        result = operation()
        duration = time.time() - start_time
        return result, duration

    def generate_report(self, output_path: str) -> None:
        """
        Generate HTML performance report

        This method generates an HTML performance report based on the metrics
        collected by the PerformanceMonitor. The report includes:

        - A summary of the performance metrics, including duration, average and
          peak CPU and memory usage.
        - Two line graphs showing CPU and memory usage over time.

        Args:
            output_path: The path where the report should be saved.
        """
        if not self.metrics:
            return
            
        # Extract metrics for plotting
        timestamps = [m.timestamp - self.start_time for m in self.metrics]
        cpu_usage = [m.cpu_usage for m in self.metrics]
        memory_usage = [m.memory_usage / (1024 * 1024) for m in self.metrics]  # Convert to MB
        
        # Create plots
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8))
        
        # CPU Usage plot
        ax1.plot(timestamps, cpu_usage, 'b-')
        ax1.set_title('CPU Usage Over Time')
        ax1.set_xlabel('Time (s)')
        ax1.set_ylabel('CPU Usage (%)')
        
        # Memory Usage plot
        ax2.plot(timestamps, memory_usage, 'r-')
        ax2.set_title('Memory Usage Over Time')
        ax2.set_xlabel('Time (s)')
        ax2.set_ylabel('Memory Usage (MB)')
        
        plt.tight_layout()
        
        # Save plots
        plot_path = str(Path(output_path).with_suffix('.png'))
        plt.savefig(plot_path)
        plt.close()
        
        # Generate HTML report
        html_content = f"""
        <html>
        <head>
            <title>Performance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                h1 {{ color: #333; }}
                .metrics {{ margin: 20px 0; }}
                img {{ max-width: 100%; }}
            </style>
        </head>
        <body>
            <h1>Performance Report</h1>
            <div class="metrics">
                <h2>Summary</h2>
                <p>Duration: {timestamps[-1]:.2f} seconds</p>
                <p>Average CPU Usage: {np.mean(cpu_usage):.1f}%</p>
                <p>Average Memory Usage: {np.mean(memory_usage):.1f} MB</p>
                <p>Peak CPU Usage: {max(cpu_usage):.1f}%</p>
                <p>Peak Memory Usage: {max(memory_usage):.1f} MB</p>
            </div>
            <div class="plots">
                <h2>Performance Graphs</h2>
                <img src="{plot_path}" alt="Performance Graphs">
            </div>
        </body>
        </html>
        """
        
        with open(output_path, 'w') as f:
            f.write(html_content)

    def plot_metrics(self, file_path: Union[str, Path]) -> None:
        """
        Generate performance metrics plot

        Args:
            file_path: Path to save plot image
        """
        import matplotlib
        matplotlib.use('Agg')  # Use non-interactive backend
        import matplotlib.pyplot as plt
        
        if not self.metrics:
            return
            
        timestamps = [m.timestamp for m in self.metrics]
        cpu_usage = [m.cpu_usage for m in self.metrics]
        memory_usage = [m.memory_usage for m in self.metrics]
        response_times = [m.response_time for m in self.metrics]
        
        fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(10, 12))
        
        # Plot CPU usage
        ax1.plot(timestamps, cpu_usage, 'b-')
        ax1.set_title('CPU Usage Over Time')
        ax1.set_ylabel('CPU Usage (%)')
        ax1.grid(True)
        
        # Plot memory usage
        ax2.plot(timestamps, memory_usage, 'g-')
        ax2.set_title('Memory Usage Over Time')
        ax2.set_ylabel('Memory Usage (bytes)')
        ax2.grid(True)
        
        # Plot response times
        ax3.plot(timestamps, response_times, 'r-')
        ax3.set_title('Response Time Over Time')
        ax3.set_ylabel('Response Time (s)')
        ax3.set_xlabel('Time (s)')
        ax3.grid(True)
        
        plt.tight_layout()
        plt.savefig(file_path)
        plt.close()

    def cleanup(self) -> None:
        """
        Clean up resources and stop monitoring
        """
        self.stop_monitoring()
        self.metrics.clear()

    def set_threshold(self, metric: str, value: float) -> None:
        """
        Set threshold for a specific metric

        Args:
            metric: Name of the metric (cpu_usage, memory_usage, response_time)
            value: Threshold value
        """
        if not hasattr(self, 'thresholds'):
            self.thresholds = {}
        self.thresholds[metric] = value

    def check_memory_leaks(self, *args, **kwargs):
        action = None
        num_iterations = 100
        if len(args) == 2:
            if callable(args[0]):
                action = args[0]
                num_iterations = args[1]
            else:
                num_iterations = args[0]
                action = args[1]
        elif len(args) == 1:
            if callable(args[0]):
                action = args[0]
            elif isinstance(args[0], int):
                num_iterations = args[0]
        if 'action' in kwargs:
            action = kwargs['action']
        if 'iterations' in kwargs:
            num_iterations = kwargs['iterations']
        if 'num_iterations' in kwargs:
            num_iterations = kwargs['num_iterations']
        if action is None:
            raise ValueError('Action must be provided')
        if num_iterations <= 0:
            raise ValueError('Iterations must be positive')
        # Record initial memory usage
        initial_memory = self.get_memory_usage()
        for _ in range(num_iterations):
            action()
        final_memory = self.get_memory_usage()
        memory_diff_mb = (final_memory - initial_memory) / (1024 * 1024)
        leak_threshold = num_iterations  # 1MB per iteration
        leak_detected = memory_diff_mb > leak_threshold
        return leak_detected, memory_diff_mb

    def memory_leak_test(self, *args, **kwargs):
        action = None
        num_iterations = 100
        threshold_mb = 10.0
        if len(args) >= 1:
            action = args[0]
        if len(args) >= 2:
            num_iterations = args[1]
        if len(args) >= 3:
            threshold_mb = args[2]
        if 'action' in kwargs:
            action = kwargs['action']
        if 'iterations' in kwargs:
            num_iterations = kwargs['iterations']
        if 'num_iterations' in kwargs:
            num_iterations = kwargs['num_iterations']
        if 'threshold_mb' in kwargs:
            threshold_mb = kwargs['threshold_mb']
        if action is None:
            raise ValueError('Action must be provided')
        if num_iterations <= 0:
            raise ValueError('Iterations must be positive')
        import numpy as np
        threshold_bytes = threshold_mb * 1024 * 1024
        try:
            initial_memory = float(self.application.get_memory_usage())
        except (TypeError, ValueError):
            initial_memory = 0.0
        memory_usage = []
        for _ in range(num_iterations):
            action()
            try:
                current_memory = float(self.application.get_memory_usage())
            except (TypeError, ValueError):
                current_memory = initial_memory
            memory_usage.append(current_memory)
            self.record_metric()
        if not memory_usage:
            return {
                'has_leak': False,
                'memory_growth_mb': 0.0,
                'growth_rate_mb_per_iteration': 0.0,
                'initial_memory_mb': 0.0,
                'final_memory_mb': 0.0
            }
        memory_usage = np.array(memory_usage)
        memory_growth = memory_usage[-1] - initial_memory
        x = np.arange(len(memory_usage))
        slope = np.polyfit(x, memory_usage, 1)[0] if len(memory_usage) > 1 else 0.0
        return {
            'has_leak': memory_growth > threshold_bytes and slope > 0,
            'memory_growth_mb': memory_growth / (1024 * 1024),
            'growth_rate_mb_per_iteration': slope / (1024 * 1024),
            'initial_memory_mb': initial_memory / (1024 * 1024),
            'final_memory_mb': memory_usage[-1] / (1024 * 1024)
        }


class PerformanceTest:
    """
    Class for running performance tests.

    Позволяет запускать тесты производительности: измерение времени выполнения, стресс-тесты, тесты на утечки памяти, сравнение с эталоном.
    Используется сервисным слоем PerformanceService.

    Example usage:
        test = PerformanceTest(app)
        result = test.measure_action(lambda: do_something())
        stress = test.stress_test(lambda: do_something(), duration=30)
        leak = test.memory_leak_test(lambda: do_something())

    Назначение:
        - Автоматизация тестирования производительности
        - Интеграция с сервисным слоем
    """

    def __init__(self, application: Application) -> None:
        """
        Initialize performance test object
        
        Args:
            application: The application to monitor
        """
        self.application = application
        self.monitor = PerformanceMonitor(application)
        
    def start_monitoring(self, interval: float = 1.0) -> None:
        """
        Start monitoring performance metrics
        
        Args:
            interval: Time between metric collections in seconds
        """
        self.monitor.start_monitoring(interval)
        
    def stop_monitoring(self) -> List[PerformanceMetric]:
        """
        Stop monitoring and return collected metrics
        
        Returns:
            List of collected performance metrics
        """
        return self.monitor.stop_monitoring()

    def measure_action(
        self,
        action: Callable,
        name: Optional[str] = None,
        warmup_runs: int = 1,
        test_runs: int = 5
    ) -> Dict[str, Union[str, float]]:
        """
        Measure performance of a specific action

        This method measures the performance of a specific action by executing
        it multiple times and recording the time taken for each execution. The
        action is executed first for a specified number of warmup runs, which
        are not recorded. Then, the action is executed for a specified number
        of test runs, and the time taken for each execution is recorded.

        Args:
            action: The callable to measure the performance of.
            name: Optional name to use for the action in the results.
            warmup_runs: The number of warmup runs to perform before measuring
                performance. Defaults to 1.
            test_runs: The number of test runs to perform to measure performance.
                Defaults to 5.

        Returns:
            A dictionary containing the results of the performance measurement:
                - name: The name of the action, or the name provided if given.
                - min_time: The minimum time taken to execute the action.
                - max_time: The maximum time taken to execute the action.
                - avg_time: The average time taken to execute the action.
                - std_dev: The standard deviation of the execution times.
        """
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
            self.monitor.record_metric(response_time=times[-1])

        return {
            'name': name or action.__name__,
            'min_time': min(times),
            'max_time': max(times),
            'avg_time': sum(times) / len(times),
            'std_dev': float(np.std(times))
        }

    def stress_test(
        self,
        action: Callable,
        duration: int = 60,
        interval: float = 0.1
    ) -> Dict[str, Union[float, bool]]:
        """
        Run stress test for specified duration

        This method executes a stress test on the given action for a specified
        duration. It continuously performs the action, pausing for the specified
        interval between each execution, and collects performance metrics.

        Args:
            action: The callable to stress test.
            duration: Total time in seconds to run the stress test. Defaults to 60.
            interval: Time in seconds to wait between each action execution. Defaults to 0.1.
        
        Returns:
            A dictionary containing performance metrics:
                - duration: The total duration of the test.
                - actions_performed: Number of times the action was executed.
                - errors: The number of errors encountered during the test.
                - actions_per_second: Average number of actions performed per second.
                - error_rate: Proportion of actions that resulted in an error.
                - Additional average metrics collected during the test.
        """
        self.monitor.start_monitoring()
        end_time = time.time() + duration
        action_count = 0
        errors = 0

        while time.time() < end_time:
            try:
                start_time = time.time()
                action()
                self.monitor.record_metric(response_time=time.time() - start_time)
                action_count += 1
            except Exception:
                errors += 1
            time.sleep(interval)

        return {
            'duration': duration,
            'actions_performed': action_count,
            'errors': errors,
            'actions_per_second': action_count / duration,
            'error_rate': errors / action_count if action_count > 0 else 0,
            **self.monitor.get_average_metrics()
        }

    def detect_regression(
        self,
        action: Callable,
        baseline_metrics: Dict[str, Dict[str, float]],
        test_runs: int = 5,
        threshold_std: float = 2.0
    ) -> Dict[str, Any]:
        """
        Detect performance regression against baseline metrics

        Args:
            action: The callable to test for regression
            baseline_metrics: Dictionary containing baseline metrics with averages and standard deviations
            test_runs: Number of test runs to perform
            threshold_std: Number of standard deviations to consider as regression

        Returns:
            Dictionary containing regression analysis results:
            - has_regression: Whether performance regression was detected
            - metrics: Current performance metrics
            - deviations: Standard deviations from baseline for each metric
        """
        current_metrics = {'response_time': [], 'memory_usage': [], 'cpu_usage': []}
        
        # Run the action multiple times and collect metrics
        for _ in range(test_runs):
            start_time = time.time()
            action()
            response_time = time.time() - start_time
            
            current_metrics['response_time'].append(response_time)
            current_metrics['memory_usage'].append(self.application.get_memory_usage())
            current_metrics['cpu_usage'].append(self.application.get_cpu_usage())
        
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
                
                # Calculate how many standard deviations away from baseline
                if baseline_std > 0:
                    deviation = (current_avg - baseline_avg) / baseline_std
                    deviations[metric] = deviation
                    
                    # Check if deviation exceeds threshold
                    if deviation > threshold_std:
                        has_regression = True
        
        return {
            'has_regression': has_regression,
            'metrics': avg_metrics,
            'deviations': deviations
        }

    def check_memory_leaks(self, action: Callable, num_iterations: int = 100) -> Tuple[bool, float]:
        """Check for memory leaks using the monitor's check_memory_leaks method."""
        return self.monitor.check_memory_leaks(action, num_iterations)

    def memory_leak_test(self, *args, **kwargs):
        """Proxy for memory_leak_test to underlying monitor for compatibility with tests."""
        return self.monitor.memory_leak_test(*args, **kwargs)
