import sys
import platform
from typing import Optional, List, Tuple, Any, Dict
import numpy as np
from PIL import Image

if platform.system() == 'Linux':
    import pyatspi  # type: ignore
    from Xlib import display, X  # type: ignore
else:
    pyatspi = None
    display = None
    X = None

from .base import BaseBackend


class LinuxBackend(BaseBackend):
    """Linux-specific implementation using AT-SPI2"""

    def __init__(self) -> None:
        """
        Initialize the Linux UI Automation backend.

        This method creates a connection to the X server, gets the screen
        dimensions, and starts the AT-SPI registry.

        Raises:
            RuntimeError: If initialization fails due to any reason.
        """
        if sys.platform != 'linux':
            raise RuntimeError("LinuxBackend can only be used on Linux systems")
        self.display = display.Display()
        self.screen = self.display.screen()
        self.registry = pyatspi.Registry
        self.registry.start()
        self._current_app = None
        self._ocr_languages = []

    @property
    def application(self) -> Any:
        """
        Get the current application instance.
        
        Returns:
            The Linux application object
        """
        return self._current_app

    # Удалены методы find_element и find_elements (универсальные by/value)

    def get_active_window(self) -> Optional[Any]:
        """
        Get the currently active window

        Returns:
            The currently active window, or None if no window is active
        """
        desktop = self.registry.getDesktop(0)
        for app in desktop:
            if app.getState().contains(pyatspi.STATE_ACTIVE):
                return app
        return None

    def take_screenshot(self, filepath: str) -> bool:
        """
        Take a screenshot using X11 and save it to a file.

        Args:
            filepath (str): The path to save the screenshot.

        Returns:
            bool: True if the screenshot was taken and saved successfully, False otherwise.
        """
        try:
            root = self.display.screen().root
            geom = root.get_geometry()
            raw = root.get_image(0, 0, geom.width, geom.height, X.ZPixmap, 0xffffffff)
            image = Image.frombytes("RGB", (geom.width, geom.height), raw.data, "raw", "BGRX")
            image.save(filepath)
            return True
        except Exception:
            return False

    def capture_screenshot(self) -> Optional[np.ndarray]:
        """
        Capture screenshot as numpy array

        Returns:
            Screenshot as numpy array if successful, None otherwise
        """
        try:
            root = self.display.screen().root
            geom = root.get_geometry()
            raw = root.get_image(0, 0, geom.width, geom.height, X.ZPixmap, 0xffffffff)
            image = Image.frombytes("RGB", (geom.width, geom.height), raw.data, "raw", "BGRX")
            return np.array(image)
        except Exception:
            return None

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen dimensions

        Returns:
            tuple: A tuple containing the width and height of the screen in pixels.
        """
        root = self.display.screen().root
        geom = root.get_geometry()
        return (geom.width, geom.height)

    def get_window_handle(self, pid: Optional[int] = None) -> Optional[int]:
        """
        Get the window handle for a specific process ID.

        Args:
            pid (Optional[int]): The process ID to search for. If None, returns the first visible window handle found.

        Returns:
            Optional[int]: The window handle if found, otherwise None.
        """
        try:
            root = self.display.screen().root
            window_list = root.query_tree().children
            for window in window_list:
                if window.get_wm_class() and window.get_attributes().map_state == X.IsViewable:
                    if pid is None:
                        return window.id
                    window_pid = window.get_full_property(self.display.intern_atom('_NET_WM_PID'), 0)
                    if window_pid and window_pid.value[0] == pid:
                        return window.id
            return None
        except Exception as e:
            print(f"Error getting window handle: {str(e)}")
            return None

    def get_window_handles(self) -> List[Any]:
        """
        Get handles for all top-level windows.
        
        Returns:
            List of window handles/references
        """
        root = self.display.screen().root
        window_ids = []
        
        # Get the list of all top-level windows
        window_list = root.query_tree().children
        for window in window_list:
            try:
                # Check if window is viewable (mapped) and not an override redirect
                attrs = window.get_attributes()
                if attrs is not None and hasattr(attrs, 'map_state') and attrs.map_state == X.IsViewable and not attrs.override_redirect:
                    window_ids.append(window)
            except:
                continue
                
        return window_ids

    def find_window(self, title: str) -> Optional[Any]:
        """
        Find a window using its title.

        Args:
            title: The title of the window to search for. If an integer is passed, it will be converted to string.

        Returns:
            The window object if found, None otherwise.
        """
        if sys.platform != 'linux':
            raise RuntimeError("LinuxBackend.find_window() can only be used on Linux systems")
            
        if not pyatspi:
            raise RuntimeError("AT-SPI2 (pyatspi) is not available")

        try:
            title_str = str(title)
            desktop = pyatspi.Registry.getDesktop(0)
            
            for app in desktop:
                if app is None:
                    continue
                    
                # Check all windows in the application
                for window in app:
                    if window is None:
                        continue
                        
                    # Check if this is a window and has the matching title
                    if (window.getRole() == pyatspi.ROLE_FRAME or 
                        window.getRole() == pyatspi.ROLE_WINDOW) and \
                       window.name == title_str:
                        return window
                        
            return None
        except Exception as e:
            print(f"Error finding window: {str(e)}")
            return None

    def _find_element_recursive(self, element: Any, by: str, value: str) -> Optional[Any]:
        """
        Recursively search for an element that matches the given criteria.
        
        Args:
            element: The root element to start the search from.
            by: The attribute used for matching (e.g., 'name', 'role').
            value: The expected value of the attribute to match.
        
        Returns:
            The first element that matches the criteria, or None if no match is found.
        """
        if self._matches_criteria(element, by, value):
            return element

        for i in range(element.childCount):
            child = element.getChildAtIndex(i)
            result = self._find_element_recursive(child, by, value)
            if result:
                return result
        return None

    def _find_elements_recursive(self, element: Any, by: str, value: str, results: List[Any]):
        """
        Recursively search for all matching elements

        Args:
            element: The root element to start the search from.
            by: The attribute used for matching (e.g., 'name', 'role').
            value: The expected value of the attribute to match.
            results: A list to store the matching elements.

        Returns:
            None
        """
        if self._matches_criteria(element, by, value):
            results.append(element)

        for i in range(element.childCount):
            child = element.getChildAtIndex(i)
            self._find_elements_recursive(child, by, value, results)

    def _matches_criteria(self, element: Any, by: str, value: str) -> bool:
        """
        Check if element matches search criteria.

        Args:
            element: The element to check.
            by: The attribute used for matching (e.g., 'name', 'role').
            value: The expected value of the attribute to match.

        Returns:
            True if the element matches the criteria, False otherwise.
        """
        try:
            if by == "name":
                return element.name == value
            elif by == "role":
                return element.getRole() == getattr(pyatspi, value.upper())
            elif by == "id":
                return str(element.id) == value
            elif by == "description":
                return element.description == value
        except Exception:
            pass
        return False

    def check_accessibility(self, element: Optional[Any] = None) -> Dict[str, Any]:
        """
        Check accessibility of an element or the entire UI using AT-SPI.

        Args:
            element: Optional element to check. If None, checks entire UI.

        Returns:
            Dictionary containing accessibility issues and their details
        """
        issues = {}
        
        if element is None:
            # Check entire UI
            root = self.display.screen().root
            window_list = root.query_tree().children
            for window in window_list:
                try:
                    attrs = window.get_attributes()
                    if attrs is not None and attrs.map_state == X.IsViewable:
                        # Basic accessibility checks for each window
                        if not hasattr(window, 'get_wm_name') or window.get_wm_name() is None:
                            issues[str(window)] = "Window missing title/name"
                except:
                    continue
        else:
            # Check specific element
            if not hasattr(element, 'get_role'):
                issues[str(element)] = "Element missing role information"
            if not hasattr(element, 'get_name') or element.get_name() is None:
                issues[str(element)] = "Element missing name/label"

        return issues

    def set_ocr_languages(self, languages: List[str]) -> None:
        """
        Set OCR languages for text recognition.

        Args:
            languages: List of language codes (e.g., ['eng', 'fra'])
        """
        # Store languages for OCR configuration
        self._ocr_languages = languages

    def move_mouse(self, x: int, y: int) -> None:
        """
        Move mouse cursor to absolute coordinates using X11.

        Args:
            x: X coordinate
            y: Y coordinate
        """
        self.display.warp_pointer(x, y)
        self.display.flush()

    def click_mouse(self) -> bool:
        """Click at current mouse position using X11"""
        try:
            root = self.display.screen().root
            root.button_press(1)  # Button 1 is left mouse button
            root.button_release(1)
            self.display.flush()
            return True
        except:
            return False

    def double_click_mouse(self) -> None:
        """Double click at current mouse position using X11"""
        self.click_mouse()
        self.click_mouse()

    def right_click_mouse(self) -> None:
        """Right click at current mouse position using X11"""
        root = self.display.screen().root
        root.button_press(3)  # Button 3 is right mouse button
        root.button_release(3)
        self.display.flush()

    def mouse_down(self) -> None:
        """Press and hold primary mouse button using X11"""
        root = self.display.screen().root
        root.button_press(1)
        self.display.flush()

    def mouse_up(self) -> None:
        """Release primary mouse button using X11"""
        root = self.display.screen().root
        root.button_release(1)
        self.display.flush()

    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse cursor position using X11.

        Returns:
            Tuple of (x, y) coordinates
        """
        root = self.display.screen().root
        pointer = root.query_pointer()
        return (pointer.root_x, pointer.root_y)

    def cleanup(self) -> None:
        """Clean up resources"""
        if hasattr(self, 'display'):
            self.display.close()
        self.registry.stop()

    def __del__(self):
        """Cleanup AT-SPI2 registry"""
        try:
            self.registry.stop()
        except Exception:
            pass
