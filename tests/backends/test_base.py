import pytest
from unittest.mock import MagicMock
from pyui_automation.backends.base import BaseBackend
from typing import Optional, List, Tuple, Any, Dict
import numpy as np


class ConcreteBackend(BaseBackend):
    """Concrete implementation of BaseBackend for testing"""

    def __init__(self) -> None:
        """
        Initialize ConcreteBackend with mock functions for testing

        Mock functions:
            - _mock_find_element: Mocked implementation of find_element
            - _mock_find_elements: Mocked implementation of find_elements
            - _mock_get_active_window: Mocked implementation of get_active_window
            - _mock_take_screenshot: Mocked implementation of take_screenshot
            - _mock_get_screen_size: Mocked implementation of get_screen_size
        """
        self._mock_find_element = MagicMock()
        self._mock_find_elements = MagicMock()
        self._mock_get_active_window = MagicMock()
        self._mock_take_screenshot = MagicMock()
        self._mock_get_screen_size = MagicMock()
        self._mock_ocr = MagicMock()

    def find_element(self, by: str, value: str, timeout: float = 0) -> Optional[Any]:
        """
        Find a single UI element using the specified strategy and value

        Args:
            by: Strategy to find element (e.g., 'id', 'name', 'class', 'xpath', etc.)
            value: Value to search for using the specified strategy
            timeout: Time to wait for element (0 for no wait)

        Returns:
            Found element or None if not found
        """
        return self._mock_find_element(by, value)

    def find_elements(self, by: str, value: str) -> List[Any]:
        """
        Find multiple UI elements using the specified strategy and value

        Args:
            by: Strategy to find elements (e.g., 'id', 'name', 'class', 'xpath', etc.)
            value: Value to search for using the specified strategy

        Returns:
            List of found elements or empty list if none found
        """
        return self._mock_find_elements(by, value)

    def get_active_window(self) -> Optional[Any]:
        """
        Get the currently active window

        Returns:
            The currently active window or None if no window is active
        """
        return self._mock_get_active_window()

    def take_screenshot(self, filepath: str) -> bool:
        """
        Take a screenshot and save it to file

        Args:
            filepath: Path to save the screenshot to

        Returns:
            True if the screenshot was saved successfully, False if not
        """
        return self._mock_take_screenshot(filepath)

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get the screen dimensions

        Returns:
            A tuple of two integers representing the width and height of the screen
        """
        return self._mock_get_screen_size()

    def capture_screenshot(self) -> Optional[np.ndarray]:
        """Capture screenshot as numpy array

        Returns:
            A numpy array representing the screenshot or None if capture failed
        """
        # Mock implementation for testing
        return np.zeros((100, 100, 3), dtype=np.uint8)

    def capture_element_screenshot(self, element: Any) -> Optional[np.ndarray]:
        """Mock implementation of capture_element_screenshot"""
        mock_image = np.zeros((50, 50, 3), dtype=np.uint8)
        return mock_image

    def get_window_handle(self, pid: Optional[int] = None) -> Optional[int]:
        """
        Get the window handle for a specific process ID

        Args:
            pid (Optional[int]): The process ID to search for. If None, returns the first visible window handle found.

        Returns:
            Optional[int]: The window handle if found, otherwise None.
        """
        return 0

    @property
    def application(self) -> Any:
        """Get the current application instance"""
        return MagicMock()

    @property
    def ocr(self) -> Any:
        """Get the OCR engine instance."""
        return self._mock_ocr

    def check_accessibility(self, element: Optional[Any] = None) -> Dict[str, Any]:
        """Check accessibility of an element or the entire UI"""
        return {}

    def set_ocr_languages(self, languages: List[str]) -> None:
        """Set OCR languages for text recognition"""
        pass

    def move_mouse(self, x: int, y: int) -> None:
        """Move mouse cursor to absolute coordinates"""
        pass

    def click_mouse(self) -> None:
        """Click at current mouse position"""
        pass

    def double_click_mouse(self) -> None:
        """Double click at current mouse position"""
        pass

    def right_click_mouse(self) -> None:
        """Right click at current mouse position"""
        pass

    def mouse_down(self) -> None:
        """Press and hold primary mouse button"""
        pass

    def mouse_up(self) -> None:
        """Release primary mouse button"""
        pass

    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse cursor position"""
        return (0, 0)  # Return a default position for this incomplete implementation


class IncompleteBackend(BaseBackend):
    """Incomplete backend that doesn't implement all abstract methods"""

    def find_element(self, by: str, value: str, timeout: float = 0) -> Optional[Any]:
        """Find a single UI element"""
        pass

    def find_elements(self, by: str, value: str) -> List[Any]:
        """Find multiple UI elements"""
        return []

    def get_active_window(self) -> Optional[Any]:
        """Get the currently active window"""
        pass

    def take_screenshot(self, filepath: str) -> bool:
        """Take a screenshot and save to file"""
        return False  # Return False to indicate screenshot was not taken

    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions"""
        return (0, 0)  # Return a default tuple of integers

    def capture_screenshot(self) -> Optional[np.ndarray]:
        """Capture screenshot as numpy array"""
        pass

    def capture_element_screenshot(self, element: Any) -> Optional[np.ndarray]:
        """Capture a screenshot of a specific element"""
        pass

    def get_window_handle(self, pid: Optional[int] = None) -> Optional[int]:
        """Get window handle for process ID"""
        pass

    def check_accessibility(self, element: Optional[Any] = None) -> Dict[str, Any]:
        """Check accessibility of element or UI"""
        return {}

    @property
    def application(self) -> Any:
        """Get current application instance"""
        pass

    @property
    def ocr(self) -> Any:
        """Get OCR engine instance"""
        pass

    def set_ocr_languages(self, languages: List[str]) -> None:
        """Set OCR languages for text recognition"""
        pass

    def move_mouse(self, x: int, y: int) -> None:
        """Move mouse cursor to absolute coordinates"""
        pass

    def click_mouse(self) -> None:
        """Click at current mouse position"""
        pass

    def double_click_mouse(self) -> None:
        """Double click at current mouse position"""
        pass

    def right_click_mouse(self) -> None:
        """Right click at current mouse position"""
        pass

    def mouse_down(self) -> None:
        """Press and hold primary mouse button"""
        pass

    def mouse_up(self) -> None:
        """Release primary mouse button"""
        pass

    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse cursor position"""
        return (0, 0)  # Return a default position for this incomplete implementation


@pytest.fixture
def backend():
    return ConcreteBackend()


@pytest.fixture
def incomplete_backend():
    return IncompleteBackend()

def test_find_element_by_id(backend):
    backend._mock_find_element.return_value = "test_element"
    element = backend.find_element_by_id("test_id")
    assert element == "test_element"
    backend._mock_find_element.assert_called_once_with("id", "test_id")

def test_find_element_by_name(backend):
    backend._mock_find_element.return_value = "test_element"
    element = backend.find_element_by_name("test_name")
    assert element == "test_element"
    backend._mock_find_element.assert_called_once_with("name", "test_name")

def test_find_element_by_class(backend):
    backend._mock_find_element.return_value = "test_element"
    element = backend.find_element_by_class("test_class")
    assert element == "test_element"
    backend._mock_find_element.assert_called_once_with("class", "test_class")

def test_find_element_by_role(backend):
    backend._mock_find_element.return_value = "test_element"
    element = backend.find_element_by_role("button")
    assert element == "test_element"
    backend._mock_find_element.assert_called_once_with("role", "button")

def test_find_element_by_xpath(backend):
    backend._mock_find_element.return_value = "test_element"
    element = backend.find_element_by_xpath("//button[@name='test']")
    assert element == "test_element"
    backend._mock_find_element.assert_called_once_with("xpath", "//button[@name='test']")

def test_find_element_by_css(backend):
    backend._mock_find_element.return_value = "test_element"
    element = backend.find_element_by_css("#test-button")
    assert element == "test_element"
    backend._mock_find_element.assert_called_once_with("css", "#test-button")

def test_find_element_by_text(backend):
    backend._mock_find_element.return_value = "test_element"
    element = backend.find_element_by_text("Click me")
    assert element == "test_element"
    backend._mock_find_element.assert_called_once_with("text", "Click me")

def test_find_element_by_partial_text(backend):
    backend._mock_find_element.return_value = "test_element"
    element = backend.find_element_by_partial_text("Click")
    assert element == "test_element"
    backend._mock_find_element.assert_called_once_with("partial_text", "Click")

def test_find_element_by_ocr(backend):
    backend._mock_find_element.return_value = "test_element"
    element = backend.find_element_by_ocr("Click me")
    assert element == "test_element"
    backend._mock_find_element.assert_called_once_with("ocr_text", "Click me")

def test_find_element_by_image(backend):
    backend._mock_find_element.return_value = "test_element"
    element = backend.find_element_by_image("button.png")
    assert element == "test_element"
    backend._mock_find_element.assert_called_once_with("image", "button.png")

def test_find_element_returns_none(backend):
    backend._mock_find_element.return_value = None
    element = backend.find_element_by_id("non_existent")
    assert element is None
    backend._mock_find_element.assert_called_once_with("id", "non_existent")

def test_get_active_window(backend):
    backend._mock_get_active_window.return_value = "active_window"
    window = backend.get_active_window()
    assert window == "active_window"
    backend._mock_get_active_window.assert_called_once()

def test_take_screenshot(backend):
    backend._mock_take_screenshot.return_value = True
    result = backend.take_screenshot("test.png")
    assert result is True
    backend._mock_take_screenshot.assert_called_once_with("test.png")

def test_get_screen_size(backend):
    backend._mock_get_screen_size.return_value = (1920, 1080)
    size = backend.get_screen_size()
    assert size == (1920, 1080)
    backend._mock_get_screen_size.assert_called_once()

def test_find_elements(backend):
    backend._mock_find_elements.return_value = ["element1", "element2"]
    elements = backend.find_elements("class", "test-class")
    assert elements == ["element1", "element2"]
    backend._mock_find_elements.assert_called_once_with("class", "test-class")

def test_find_elements_empty(backend):
    backend._mock_find_elements.return_value = []
    elements = backend.find_elements("id", "non-existent")
    assert elements == []
    backend._mock_find_elements.assert_called_once_with("id", "non-existent")

def test_abstract_find_element(incomplete_backend):
    """Test that find_element is properly defined as abstract"""
    with pytest.raises(NotImplementedError):
        incomplete_backend.find_element("id", "test")

def test_abstract_find_elements(incomplete_backend):
    """Test that find_elements is properly defined as abstract"""
    with pytest.raises(NotImplementedError):
        incomplete_backend.find_elements("id", "test")

def test_abstract_get_active_window(incomplete_backend):
    """Test that get_active_window is properly defined as abstract"""
    with pytest.raises(NotImplementedError):
        incomplete_backend.get_active_window()

def test_abstract_take_screenshot(incomplete_backend):
    """Test that take_screenshot is properly defined as abstract"""
    with pytest.raises(NotImplementedError):
        incomplete_backend.take_screenshot("test.png")

def test_abstract_get_screen_size(incomplete_backend):
    """Test that get_screen_size is properly defined as abstract"""
    with pytest.raises(NotImplementedError):
        incomplete_backend.get_screen_size()
