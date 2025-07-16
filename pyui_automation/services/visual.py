from abc import ABC, abstractmethod
from typing import Any, Optional
import numpy as np

class VisualTestingService(ABC):
    """Abstract visual testing service interface."""

    @abstractmethod
    def init_baseline(self, baseline_dir: Optional[str] = None) -> None:
        pass

    @abstractmethod
    def capture_baseline(self, name: str, element: Optional[Any] = None) -> None:
        pass

    @abstractmethod
    def compare_visual(self, name: str, element: Optional[Any] = None, threshold: float = 0.01, ignore_mask: Optional[np.ndarray] = None, ignore_regions: Optional[list] = None) -> dict:
        """Compare screenshot with baseline, игнорируя указанные области/маски"""
        pass

    @abstractmethod
    def generate_report(self, name: str, differences: list, output_dir: str) -> None:
        pass 