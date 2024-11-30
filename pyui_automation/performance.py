import time
from typing import Dict, List, Optional, Tuple, Callable
import psutil
import json
from pathlib import Path
import matplotlib.pyplot as plt
import numpy as np
from dataclasses import dataclass
from datetime import datetime


@dataclass
class PerformanceMetric:
    timestamp: float
    cpu_usage: float
    memory_usage: float
    response_time: float


class PerformanceMonitor:
    """Monitor and analyze application performance"""

    def __init__(self, application):
        self.application = application
        self.metrics: List[PerformanceMetric] = []
        self.start_time = time.time()

    def start_monitoring(self, interval: float = 1.0):
        """Start collecting performance metrics"""
        self.start_time = time.time()
        self.metrics.clear()

    def record_metric(self, response_time: float = 0.0):
        """Record current performance metrics"""
        if self.application.is_running():
            self.metrics.append(PerformanceMetric(
                timestamp=time.time() - self.start_time,
                cpu_usage=self.application.get_cpu_usage(),
                memory_usage=self.application.get_memory_usage(),
                response_time=response_time
            ))

    def get_average_metrics(self) -> Dict[str, float]:
        """Get average performance metrics"""
        if not self.metrics:
            return {'cpu_usage': 0, 'memory_usage': 0, 'response_time': 0}

        return {
            'cpu_usage': sum(m.cpu_usage for m in self.metrics) / len(self.metrics),
            'memory_usage': sum(m.memory_usage for m in self.metrics) / len(self.metrics),
            'response_time': sum(m.response_time for m in self.metrics) / len(self.metrics)
        }

    def generate_report(self, output_dir: str):
        """Generate performance report with graphs"""
        if not self.metrics:
            return

        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create performance graphs
        timestamps = [m.timestamp for m in self.metrics]
        
        # CPU Usage Graph
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, [m.cpu_usage for m in self.metrics])
        plt.title('CPU Usage Over Time')
        plt.xlabel('Time (seconds)')
        plt.ylabel('CPU Usage (%)')
        plt.grid(True)
        plt.savefig(output_path / 'cpu_usage.png')
        plt.close()

        # Memory Usage Graph
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, [m.memory_usage for m in self.metrics])
        plt.title('Memory Usage Over Time')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Memory Usage (MB)')
        plt.grid(True)
        plt.savefig(output_path / 'memory_usage.png')
        plt.close()

        # Response Time Graph
        plt.figure(figsize=(10, 6))
        plt.plot(timestamps, [m.response_time for m in self.metrics])
        plt.title('Response Time Over Time')
        plt.xlabel('Time (seconds)')
        plt.ylabel('Response Time (seconds)')
        plt.grid(True)
        plt.savefig(output_path / 'response_time.png')
        plt.close()

        # Generate HTML report
        avg_metrics = self.get_average_metrics()
        html_report = f"""
        <html>
        <head>
            <title>Performance Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .metric {{ margin: 20px 0; }}
                .graph {{ margin: 20px 0; }}
            </style>
        </head>
        <body>
            <h1>Performance Report</h1>
            <p>Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            
            <div class="metric">
                <h2>Average Metrics</h2>
                <ul>
                    <li>CPU Usage: {avg_metrics['cpu_usage']:.2f}%</li>
                    <li>Memory Usage: {avg_metrics['memory_usage']:.2f} MB</li>
                    <li>Response Time: {avg_metrics['response_time']:.3f} seconds</li>
                </ul>
            </div>

            <div class="graph">
                <h2>CPU Usage</h2>
                <img src="cpu_usage.png" alt="CPU Usage Graph">
            </div>

            <div class="graph">
                <h2>Memory Usage</h2>
                <img src="memory_usage.png" alt="Memory Usage Graph">
            </div>

            <div class="graph">
                <h2>Response Time</h2>
                <img src="response_time.png" alt="Response Time Graph">
            </div>
        </body>
        </html>
        """
        
        with open(output_path / 'report.html', 'w') as f:
            f.write(html_report)

        # Save raw metrics
        with open(output_path / 'metrics.json', 'w') as f:
            json.dump([{
                'timestamp': m.timestamp,
                'cpu_usage': m.cpu_usage,
                'memory_usage': m.memory_usage,
                'response_time': m.response_time
            } for m in self.metrics], f, indent=2)


class PerformanceTest:
    """Class for running performance tests"""

    def __init__(self, application):
        self.application = application
        self.monitor = PerformanceMonitor(application)

    def measure_action(self, action: Callable, name: str = None,
                      warmup_runs: int = 1, test_runs: int = 5) -> Dict[str, float]:
        """Measure performance of a specific action"""
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
            'std_dev': np.std(times)
        }

    def stress_test(self, action: Callable, duration: int = 60,
                   interval: float = 0.1) -> Dict[str, float]:
        """Run stress test for specified duration"""
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

    def memory_leak_test(self, action: Callable, iterations: int = 100,
                        threshold_mb: float = 10.0) -> Dict[str, bool]:
        """Test for memory leaks"""
        initial_memory = self.application.get_memory_usage()
        memory_usage = []

        for _ in range(iterations):
            action()
            current_memory = self.application.get_memory_usage()
            memory_usage.append(current_memory)
            self.monitor.record_metric()

        # Analyze memory growth
        memory_growth = memory_usage[-1] - initial_memory
        linear_growth = np.polyfit(range(len(memory_usage)), memory_usage, 1)[0]

        return {
            'has_leak': memory_growth > threshold_mb and linear_growth > 0,
            'memory_growth_mb': memory_growth,
            'growth_rate_mb_per_iteration': linear_growth,
            'initial_memory_mb': initial_memory,
            'final_memory_mb': memory_usage[-1]
        }
