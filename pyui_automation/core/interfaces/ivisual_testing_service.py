"""
IVisualTestingService interface - defines contract for visual testing service.

Responsible for:
- Visual baseline management
- Visual comparison
- Visual difference detection
- Visual testing reports
"""

from abc import ABC, abstractmethod
from typing import Optional, Union, Tuple, TYPE_CHECKING
from pathlib import Path
import numpy as np

if TYPE_CHECKING:
    from ...elements.base_element import BaseElement


class IVisualTestingService(ABC):
    """Interface for visual testing service"""
    
    @abstractmethod
    def init_visual_testing(self, baseline_dir: Union[str, Path], threshold: float = 0.95) -> None:
        """Initialize visual testing"""
        pass
    
    @abstractmethod
    def configure_visual_testing(self, baseline_dir: Union[str, Path], threshold: float = 0.95) -> None:
        """Configure visual testing"""
        pass
    
    @abstractmethod
    def capture_baseline(self, name: str, element: Optional["BaseElement"] = None) -> bool:
        """Capture visual baseline"""
        pass
    
    @abstractmethod
    def verify_visual(self, name: str, element: Optional["BaseElement"] = None) -> Tuple[bool, float]:
        """Verify visual state against baseline"""
        pass
    
    @abstractmethod
    def compare_visual(self, name: str, element: Optional["BaseElement"] = None) -> Tuple[bool, float]:
        """Compare visual state"""
        pass
    
    @abstractmethod
    def verify_visual_state(self, name: str, element: Optional["BaseElement"] = None, threshold: Optional[float] = None) -> bool:
        """Verify visual state and return boolean result"""
        pass
    
    @abstractmethod
    def capture_visual_baseline(self, name: str, element: Optional["BaseElement"] = None) -> bool:
        """Capture visual baseline"""
        pass
    
    @abstractmethod
    def generate_visual_report(self, differences: list, name: str, output_dir: Optional[Union[str, Path]] = None) -> None:
        """Generate visual testing report"""
        pass
    
    @abstractmethod
    def generate_diff_report(self, img1: np.ndarray, img2: np.ndarray, output_path: Union[str, Path]) -> None:
        """Generate difference report between two images"""
        pass
    
    @abstractmethod
    def find_all_elements(self, template: np.ndarray, threshold: float = 0.8) -> list:
        """Find all elements matching template"""
        pass
    
    @abstractmethod
    def wait_for_image(self, template: np.ndarray, timeout: float = 10) -> bool:
        """Wait for image to appear"""
        pass
    
    @abstractmethod
    def highlight_differences(self, img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        """Highlight differences between two images"""
        pass
    
    @abstractmethod
    def compare_images(self, baseline_path: Union[str, Path], current_image: Union[np.ndarray, str, Path]) -> dict:
        """Compare two images and return comparison results"""
        pass 