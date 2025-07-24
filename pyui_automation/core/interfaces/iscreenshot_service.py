"""
IScreenshotService interface - defines contract for screenshot service.

Responsible for:
- Taking screenshots
- Capturing element screenshots
- Saving screenshots
- Image processing
"""

from abc import ABC, abstractmethod
from typing import Optional, Union, TYPE_CHECKING
from pathlib import Path
import numpy as np

if TYPE_CHECKING:
    from ...elements.base_element import BaseElement


class IScreenshotService(ABC):
    """Interface for screenshot service"""
    
    @abstractmethod
    def take_screenshot(self, save_path: Optional[Path] = None) -> np.ndarray:
        """Take screenshot of entire screen"""
        pass
    
    @abstractmethod
    def capture_screenshot(self) -> np.ndarray:
        """Capture screenshot (alias for take_screenshot)"""
        pass
    
    @abstractmethod
    def capture_element_screenshot(self, element: "BaseElement") -> np.ndarray:
        """Capture screenshot of specific element"""
        pass
    
    @abstractmethod
    def capture_screen_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Capture screenshot of specific screen region"""
        pass
    
    @abstractmethod
    def save_screenshot(self, image: np.ndarray, path: Union[str, Path]) -> None:
        """Save screenshot to file"""
        pass
    
    @abstractmethod
    def get_screen_size(self) -> tuple[int, int]:
        """Get screen dimensions"""
        pass 