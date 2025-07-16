from abc import ABC, abstractmethod
from typing import List, Dict

class AccessibilityService(ABC):
    """Abstract accessibility service interface."""

    @abstractmethod
    def check_accessibility(self) -> List[Dict[str, str]]:
        pass

    @abstractmethod
    def generate_report(self, output_dir: str) -> None:
        pass 