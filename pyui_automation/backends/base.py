from abc import ABC, abstractmethod
from typing import Optional, List, Tuple, Any, Dict
import numpy as np


class BaseBackend(ABC):
    """Base class for platform-specific backends"""

    @abstractmethod
    def find_element(self, by: str, value: str, timeout: float = 0) -> Optional[Any]:
        """
        Find a single UI element
        
        Supported strategies:
        - id: Element ID or automation ID
        - name: Element name or title
        - class: Element class name
        - role/control_type: Element role or control type
        - xpath: XPath expression
        - css: CSS selector
        - text: Element text content
        - partial_text: Partial text content
        - ocr_text: Text found using OCR
        - image: Image pattern matching
        
        Args:
            by: Strategy to find element
            value: Value to search for
            timeout: Time to wait for element (0 for no wait)
        """
        raise NotImplementedError("find_element must be implemented by subclass")

    @abstractmethod
    def find_elements(self, by: str, value: str) -> List[Any]:
        """Find multiple UI elements using the same strategies as find_element"""
        raise NotImplementedError("find_elements must be implemented by subclass")

    @abstractmethod
    def get_active_window(self) -> Optional[Any]:
        """Get the currently active window"""
        raise NotImplementedError("get_active_window must be implemented by subclass")

    @abstractmethod
    def take_screenshot(self, filepath: str) -> bool:
        """Take a screenshot and save to file"""
        raise NotImplementedError("take_screenshot must be implemented by subclass")

    @abstractmethod
    def capture_screenshot(self) -> Optional[np.ndarray]:
        """Capture screenshot as numpy array"""
        raise NotImplementedError("capture_screenshot must be implemented by subclass")

    @abstractmethod
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions"""
        raise NotImplementedError("get_screen_size must be implemented by subclass")

    @abstractmethod
    def get_window_handle(self, pid: Optional[int] = None) -> Optional[int]:
        """
        Get the window handle for a specific process ID.

        Args:
            pid (Optional[int]): The process ID to search for. If None, returns the first visible window handle found.

        Returns:
            Optional[int]: The window handle if found, otherwise None.
        """
        raise NotImplementedError("get_window_handle must be implemented by subclass")

    @abstractmethod
    def capture_element_screenshot(self, element: Any) -> Optional[np.ndarray]:
        """
        Capture a screenshot of a specific element.

        Args:
            element: The element to capture

        Returns:
            Screenshot as numpy array, or None if capture fails
        """
        raise NotImplementedError("capture_element_screenshot must be implemented by subclass")

    @abstractmethod
    def check_accessibility(self, element: Optional[Any] = None) -> Dict[str, Any]:
        """
        Check accessibility of an element or the entire UI.

        Args:
            element: Optional element to check. If None, checks entire UI.

        Returns:
            Dictionary containing accessibility issues and their details
        """
        raise NotImplementedError("check_accessibility must be implemented by subclass")

    @property
    @abstractmethod
    def application(self) -> Any:
        """
        Get the current application instance.
        
        Returns:
            The platform-specific application object
        """
        raise NotImplementedError("application must be implemented by subclass")

    @property
    @abstractmethod
    def ocr(self) -> Any:
        """
        Get the OCR engine instance.
        
        Returns:
            The OCR engine instance for text recognition
        """
        raise NotImplementedError("ocr must be implemented by subclass")

    def find_element_by_id(self, id: str) -> Optional[Any]:
        """
        Find element by ID
        
        Args:
            id: Element ID
        
        Returns:
            Element if found, None otherwise
        """
        return self.find_element("id", id)

    def find_element_by_name(self, name: str) -> Optional[Any]:
        """
        Find element by name

        Args:
            name: Element name

        Returns:
            Element if found, None otherwise
        """
        return self.find_element("name", name)

    def find_element_by_class(self, class_name: str) -> Optional[Any]:
        """
        Find element by class name

        Args:
            class_name: Class name to search for

        Returns:
            Element if found, None otherwise
        """
        return self.find_element("class", class_name)

    def find_element_by_role(self, role: str) -> Optional[Any]:
        """
        Find an element by its role or control type.
        
        Args:
            role: The role or control type of the element to search for.
        
        Returns:
            The element if found, or None if no element with the specified role is found.
        """
        return self.find_element("role", role)

    def find_element_by_xpath(self, xpath: str) -> Optional[Any]:
        """
        Find element by XPath

        Args:
            xpath: The XPath expression to locate the element.

        Returns:
            The element if found, or None if no element matches the XPath.
        """
        return self.find_element("xpath", xpath)

    def find_element_by_css(self, css: str) -> Optional[Any]:
        """
        Find an element using a CSS selector.

        Args:
            css: The CSS selector to locate the element.

        Returns:
            The element if found, or None if no element matches the CSS selector.
        """
        return self.find_element("css", css)

    def find_element_by_text(self, text: str) -> Optional[Any]:
        """
        Find element by exact text content.

        Args:
            text: The exact text content to search for.

        Returns:
            The element if found, or None if no element matches the exact text.
        """
        return self.find_element("text", text)

    def find_element_by_partial_text(self, text: str) -> Optional[Any]:
        """
        Find element by partial text content.

        Args:
            text: The partial text content to search for.

        Returns:
            The element if found, or None if no element matches the partial text.
        """
        return self.find_element("partial_text", text)

    def find_element_by_ocr(self, text: str) -> Optional[Any]:
        """
        Find element by OCR text recognition.

        Uses an OCR (Optical Character Recognition) engine to find an element
        containing the given text. The OCR engine is configured to recognize
        English text.
        """
        return self.find_element("ocr_text", text)

    def find_element_by_image(self, image_path: str) -> Optional[Any]:
        """
        Find element by image pattern matching.

        Args:
            image_path: Path to the image file to search for.

        Returns:
            The element if found, or None if no element matches the image.
        """
        return self.find_element("image", image_path)

    @abstractmethod
    def set_ocr_languages(self, languages: List[str]) -> None:
        """
        Set OCR languages for text recognition.

        Args:
            languages: List of language codes (e.g., ['eng', 'fra'])
        """
        raise NotImplementedError("set_ocr_languages must be implemented by subclass")

    @abstractmethod
    def move_mouse(self, x: int, y: int) -> None:
        """
        Move mouse cursor to absolute coordinates.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        raise NotImplementedError("move_mouse must be implemented by subclass")

    @abstractmethod
    def click_mouse(self) -> bool:
        """Click at current mouse position"""
        raise NotImplementedError("click_mouse must be implemented by subclass")

    @abstractmethod
    def double_click_mouse(self) -> None:
        """Double click at current mouse position"""
        raise NotImplementedError("double_click_mouse must be implemented by subclass")

    @abstractmethod
    def right_click_mouse(self) -> None:
        """Right click at current mouse position"""
        raise NotImplementedError("right_click_mouse must be implemented by subclass")

    @abstractmethod
    def mouse_down(self) -> None:
        """Press and hold primary mouse button"""
        raise NotImplementedError("mouse_down must be implemented by subclass")

    @abstractmethod
    def mouse_up(self) -> None:
        """Release primary mouse button"""
        raise NotImplementedError("mouse_up must be implemented by subclass")

    @abstractmethod
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse cursor position.

        Returns:
            Tuple of (x, y) coordinates
        """
        raise NotImplementedError("get_mouse_position must be implemented by subclass")
