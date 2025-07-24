"""
IBackendScreen interface - defines contract for screen operations.

Responsible for:
- Screen capture
- Screen region capture
- Screen size information
"""

from abc import ABC, abstractmethod
from typing import Optional, Tuple
import numpy as np


class IBackendScreen(ABC):
    """Interface for screen operations"""
    
    @abstractmethod
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions"""
        pass
    
    @abstractmethod
    def capture_screenshot(self) -> Optional[np.ndarray]:
        """Capture screenshot of entire screen"""
        pass
    
    @abstractmethod
    def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        """Capture screenshot of specific screen region"""
        pass 