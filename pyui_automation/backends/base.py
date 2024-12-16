"""Base class for UI automation backends"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union, Tuple
import numpy as np
from pathlib import Path


class BaseBackend(ABC):
    """Abstract base class for UI automation backends"""

    @abstractmethod
    def attach_to_application(self, pid: int) -> None:
        """Attach to an existing application"""
        pass

    @abstractmethod
    def capture_element_screenshot(self, element: Any) -> np.ndarray:
        """Capture screenshot of an element"""
        pass

    @abstractmethod
    def capture_screenshot(self) -> np.ndarray:
        """Capture full screen screenshot"""
        pass

    @abstractmethod
    def check_accessibility(self, element: Any = None) -> Dict[str, Any]:
        """Check accessibility compliance"""
        pass

    @abstractmethod
    def click_mouse(self, x: int, y: int) -> None:
        """Click mouse at coordinates"""
        pass

    @abstractmethod
    def close_application(self) -> None:
        """Close current application"""
        pass

    @abstractmethod
    def close_window(self, window: Any) -> None:
        """Close window"""
        pass

    @abstractmethod
    def double_click_mouse(self, x: int, y: int) -> None:
        """Double click mouse at coordinates"""
        pass

    @abstractmethod
    def find_element(self, by: str, value: str) -> Optional[Any]:
        """Find UI element"""
        pass

    @abstractmethod
    def find_elements(self, by: str, value: str) -> List[Any]:
        """Find multiple UI elements"""
        pass

    @abstractmethod
    def get_active_window(self) -> Optional[Any]:
        """Get currently active window"""
        pass

    @abstractmethod
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions"""
        pass

    @abstractmethod
    def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
        """Get window position and size"""
        pass

    @abstractmethod
    def get_window_title(self, window: Any) -> str:
        """Get window title"""
        pass

    @abstractmethod
    def launch_application(self, path: str, args: List[str]) -> None:
        """Launch application"""
        pass

    @abstractmethod
    def maximize_window(self, window: Any) -> None:
        """Maximize window"""
        pass

    @abstractmethod
    def minimize_window(self, window: Any) -> None:
        """Minimize window"""
        pass

    @abstractmethod
    def move_mouse(self, x: int, y: int) -> None:
        """Move mouse to coordinates"""
        pass

    @abstractmethod
    def press_key(self, key: str) -> None:
        """Press keyboard key"""
        pass

    @abstractmethod
    def release_key(self, key: str) -> None:
        """Release keyboard key"""
        pass

    @abstractmethod
    def resize_window(self, window: Any, width: int, height: int) -> None:
        """Resize window"""
        pass

    @abstractmethod
    def right_click_mouse(self, x: int, y: int) -> None:
        """Right click mouse at coordinates"""
        pass

    @abstractmethod
    def send_keys(self, text: str) -> None:
        """Send keyboard input"""
        pass

    @abstractmethod
    def set_window_position(self, window: Any, x: int, y: int) -> None:
        """Set window position"""
        pass

    @abstractmethod
    def take_screenshot(self, save_path: str) -> None:
        """Save screenshot to file"""
        pass

    @abstractmethod
    def get_element_attributes(self, element: Any) -> Dict[str, Any]:
        """Get element attributes"""
        pass

    @abstractmethod
    def get_element_property(self, element: Any, property_name: str) -> Any:
        """Get element property"""
        pass

    @abstractmethod
    def set_element_property(self, element: Any, property_name: str, value: Any) -> None:
        """Set element property"""
        pass

    @abstractmethod
    def get_element_pattern(self, element: Any, pattern_name: str) -> Any:
        """Get element pattern"""
        pass

    @abstractmethod
    def invoke_element_pattern_method(self, pattern: Any, method_name: str, *args) -> Any:
        """Invoke pattern method"""
        pass

    @abstractmethod
    def get_element_rect(self, element: Any) -> tuple[int, int, int, int]:
        """Get element rectangle"""
        pass

    @abstractmethod
    def scroll_element(self, element: Any, direction: str, amount: float) -> None:
        """Scroll element"""
        pass

    @abstractmethod
    def get_element_text(self, element: Any) -> str:
        """Get element text"""
        pass

    @abstractmethod
    def set_element_text(self, element: Any, text: str) -> None:
        """Set element text"""
        pass

    @abstractmethod
    def get_element_value(self, element: Any) -> Any:
        """Get element value"""
        pass

    @abstractmethod
    def set_element_value(self, element: Any, value: Any) -> None:
        """Set element value"""
        pass

    @abstractmethod
    def get_element_state(self, element: Any) -> Dict[str, bool]:
        """Get element state"""
        pass

    @abstractmethod
    def wait_for_element(self, by: str, value: str, timeout: float = 10) -> Optional[Any]:
        """Wait for element"""
        pass

    @abstractmethod
    def wait_for_element_state(self, element: Any, state: str, timeout: float = 10) -> bool:
        """Wait for element state"""
        pass

    @abstractmethod
    def wait_for_element_property(self, element: Any, property_name: str, value: Any, timeout: float = 10) -> bool:
        """Wait for element property"""
        pass

    @abstractmethod
    def generate_accessibility_report(self, output_dir: Union[str, Path]) -> None:
        """Generate accessibility report"""
        pass

    @abstractmethod
    def get_application(self) -> Optional[Any]:
        """Get current application"""
        pass

    @abstractmethod
    def close_application(self, application: Any) -> None:
        """Close application"""
        pass

    @abstractmethod
    def attach_to_application(self, process_id: int) -> Any:
        """Attach to application"""
        pass
