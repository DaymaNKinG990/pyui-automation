"""
Screenshot Service - handles all screenshot operations.

Responsible for:
- Taking screenshots of screen and elements
- Saving screenshots to files
- Screenshot utilities
"""

from typing import Optional, Union, Any
from pathlib import Path
import numpy as np
from logging import getLogger

# Local imports
from ...elements.base_element import BaseElement
from ...utils import save_image, ensure_dir
from ..interfaces.iscreenshot_service import IScreenshotService


class ScreenshotService(IScreenshotService):
    """Service for screenshot operations"""
    
    def __init__(self, backend: Any, session: Any):
        self._backend = backend
        self._session = session
        self._logger = getLogger(__name__)
    
    def take_screenshot(self, save_path: Optional[Path] = None) -> np.ndarray:
        """Take screenshot of entire screen"""
        try:
            screenshot = self._backend.capture_screenshot()
            if screenshot is None:
                raise RuntimeError("Failed to capture screenshot")
            
            if save_path:
                self._save_image(screenshot, save_path)
            
            self._logger.debug("Screenshot captured successfully")
            return screenshot
        except Exception as e:
            self._logger.error(f"Failed to take screenshot: {e}")
            raise
    
    def capture_screenshot(self) -> np.ndarray:
        """Capture screenshot (alias for take_screenshot)"""
        return self.take_screenshot()
    
    def capture_element_screenshot(self, element: BaseElement) -> np.ndarray:
        """Capture screenshot of specific element"""
        try:
            rect = element.rect
            screenshot = self._backend.capture_screen_region(
                rect['x'], rect['y'], rect['width'], rect['height']
            )
            if screenshot is None:
                raise RuntimeError("Failed to capture element screenshot")
            
            self._logger.debug(f"Element screenshot captured at {rect}")
            return screenshot
        except Exception as e:
            self._logger.error(f"Failed to capture element screenshot: {e}")
            raise
    
    def capture_screen_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Capture screenshot of specific screen region"""
        try:
            screenshot = self._backend.capture_screen_region(x, y, width, height)
            if screenshot is None:
                raise RuntimeError("Failed to capture screen region")
            
            self._logger.debug(f"Screen region captured at ({x}, {y}, {width}, {height})")
            return screenshot
        except Exception as e:
            self._logger.error(f"Failed to capture screen region: {e}")
            raise
    
    def save_screenshot(self, image: np.ndarray, path: Union[str, Path]) -> None:
        """Save screenshot to file"""
        try:
            self._save_image(image, path)
            self._logger.debug(f"Screenshot saved to {path}")
        except Exception as e:
            self._logger.error(f"Failed to save screenshot: {e}")
            raise
    
    def _save_image(self, image: np.ndarray, path: Union[str, Path]) -> None:
        """Save image to file"""
        try:
            path = Path(path)
            ensure_dir(path.parent)
            save_image(image, path)
        except Exception as e:
            self._logger.error(f"Failed to save image: {e}")
            raise
    
    def get_screen_size(self) -> tuple[int, int]:
        """Get screen dimensions"""
        try:
            return self._backend.get_screen_size()
        except Exception as e:
            self._logger.error(f"Failed to get screen size: {e}")
            raise 