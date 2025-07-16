from typing import Dict, Any
from .performance import PerformanceService
import time

class PerformanceServiceImpl(PerformanceService):
    """Implementation of PerformanceService for collecting, aggregating and pushing performance metrics."""
    def __init__(self):
        """Initialize performance service implementation."""
        self._metrics = {}
        self._monitoring = False
        self._interval = 1.0
        self._last_time = None
        self._external_sources = {}

    def start_monitoring(self, interval: float = 1.0) -> None:
        self._monitoring = True
        self._interval = interval
        self._last_time = time.time()
        self._metrics = {"cpu": [], "memory": [], "response_time": []}

    def add_metric(self, name: str, initial_value: float = 0.0) -> None:
        self._metrics[name] = [initial_value]

    def record_metric(self, name: str, value: float) -> None:
        if name not in self._metrics:
            self._metrics[name] = []
        self._metrics[name].append(value)

    def get_metric(self, name: str) -> float:
        values = self._metrics.get(name, [])
        return sum(values) / len(values) if values else 0.0

    def add_external_source(self, name: str, fetch_fn: Any) -> None:
        self._external_sources[name] = fetch_fn

    def get_external_metrics(self) -> dict:
        return {name: fn() for name, fn in self._external_sources.items()}

    def get_metrics(self) -> Dict[str, float]:
        return {k: sum(v)/len(v) if v else 0.0 for k, v in self._metrics.items()}

    def generate_report(self, output_dir: str) -> None:
        path = f"{output_dir}/performance_report.txt"
        with open(path, "w") as f:
            for k, v in self._metrics.items():
                f.write(f"{k}: {v}\n")

    def push_metrics(self, push_fn: Any) -> None:
        """Push all collected metrics to an external system using push_fn(dict)"""
        data = {k: self.get_metric(k) for k in self._metrics}
        data.update(self.get_external_metrics())
        push_fn(data) 