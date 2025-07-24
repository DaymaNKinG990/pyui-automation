"""
IElementScreenshot interface - defines contract for element screenshots.

Responsible for:
- Element screenshot capture
- Element image processing
"""

from abc import ABC, abstractmethod
from typing import Optional
import numpy as np


class IElementScreenshot(ABC):
    """Interface for element screenshots"""
    
    @abstractmethod
    def capture_screenshot(self) -> Optional[np.ndarray]:
        """Capture screenshot of element"""
        pass
    
    @abstractmethod
    def take_screenshot(self) -> Optional[np.ndarray]:
        """Take screenshot of element (alias for capture_screenshot)"""
        pass 