"""
IPerformanceService interface - defines contract for performance service.

Responsible for:
- Performance monitoring
- Performance testing
- Memory leak detection
- Stress testing
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Callable


class IPerformanceService(ABC):
    """Interface for performance service"""
    
    @abstractmethod
    def start_performance_monitoring(self, interval: float = 1.0, metrics: Optional[List[str]] = None) -> None:
        """Start performance monitoring"""
        pass
    
    @abstractmethod
    def stop_performance_monitoring(self) -> Dict[str, Any]:
        """Stop performance monitoring and return results"""
        pass
    
    @abstractmethod
    def measure_action_performance(self, action: Callable, runs: int = 3) -> Dict[str, float]:
        """Measure performance of an action"""
        pass
    
    @abstractmethod
    def run_stress_test(self, action: Callable, duration: float) -> Dict[str, Any]:
        """Run stress test for specified duration"""
        pass
    
    @abstractmethod
    def check_memory_leaks(self, action: Optional[Callable] = None, iterations: int = 100) -> Dict[str, Any]:
        """Check for memory leaks"""
        pass
    
    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        pass
    
    @abstractmethod
    def get_system_performance(self) -> Dict[str, float]:
        """Get system-wide performance metrics"""
        pass 