from abc import ABC, abstractmethod
from typing import Any, Dict

class PerformanceService(ABC):
    """Abstract performance service interface."""

    @abstractmethod
    def start_monitoring(self, interval: float = 1.0) -> None:
        pass

    @abstractmethod
    def add_metric(self, name: str, initial_value: float = 0.0) -> None:
        """Add a custom metric"""
        pass

    @abstractmethod
    def record_metric(self, name: str, value: float) -> None:
        """Record a value for a custom metric"""
        pass

    @abstractmethod
    def get_metric(self, name: str) -> float:
        """Get the current value or average of a custom metric"""
        pass

    @abstractmethod
    def add_external_source(self, name: str, fetch_fn: Any) -> None:
        """Add an external metric source (e.g., NetData)"""
        pass

    @abstractmethod
    def get_metrics(self) -> Dict[str, float]:
        pass

    @abstractmethod
    def generate_report(self, output_dir: str) -> None:
        pass

    @abstractmethod
    def push_metrics(self, push_fn: Any) -> None:
        """Push all collected metrics to an external system using push_fn(dict)"""
        pass 