import sys
from typing import Optional, List, Tuple, Any, Dict
import numpy as np
from PIL import Image
import time
import platform

if platform.system() == 'Darwin':
    import objc  # type: ignore
    import Quartz  # type: ignore
    from AppKit import NSWorkspace, NSScreen  # type: ignore
    from Cocoa import *  # type: ignore
else:
    objc = None
    Quartz = None
    NSWorkspace = None
    NSScreen = None

from .base import BaseBackend


class MacOSBackend(BaseBackend):
    """macOS-specific implementation using Apple Accessibility API"""

    def __init__(self) -> None:
        """
        Initialize the MacOSBackend.

        Raises:
            RuntimeError: If platform is not macOS
        """
        if platform.system() != 'Darwin':
            raise RuntimeError("MacOSBackend can only be used on macOS systems")
        self.ax = objc.ObjCClass('AXUIElement')
        self.system = self.ax.systemWide()

    def find_element(self, by: str, value: str, timeout: float = 0) -> Optional[Any]:
        """
        Find a UI element using Apple Accessibility API
        
        Args:
            by: Strategy to find element ('id', 'name', 'class', 'xpath', etc.)
            value: Value to search for
            timeout: Time to wait for element (0 for no wait)
        
        Returns:
            AXUIElement if found, None otherwise
        """
        if timeout > 0:
            start_time = time.time()
            while time.time() - start_time < timeout:
                app = self._get_frontmost_application()
                if not app:
                    time.sleep(0.1)
                    continue
                element = self._find_element_recursive(app, by, value)
                if element:
                    return element
                time.sleep(0.1)
            return None
            
        app = self._get_frontmost_application()
        if not app:
            return None
        return self._find_element_recursive(app, by, value)

    def find_elements(self, by: str, value: str) -> List[Any]:
        """
        Find all matching UI elements

        Args:
            by: Strategy to find elements ('id', 'name', 'class', 'xpath', etc.)
            value: Value to search for

        Returns:
            A list of all matching elements. If no elements are found, an empty list is returned.
        """
        app = self._get_frontmost_application()
        if not app:
            return []
        elements = []
        self._find_elements_recursive(app, by, value, elements)
        return elements

    def get_active_window(self) -> Optional[Any]:
        """
        Get the currently active window

        Returns:
            The currently active window, or None if no window is active
        """
        app = self._get_frontmost_application()
        if app:
            windows = self._get_attribute(app, "AXWindows")
            if windows and len(windows) > 0:
                return windows[0]
        return None

    def take_screenshot(self, filepath: str) -> bool:
        """
        Take a screenshot using Quartz

        Args:
            filepath: Path to save screenshot to file

        Returns:
            True if successful, False otherwise
        """
        try:
            # Get the main screen
            screen = NSScreen.mainScreen()
            rect = screen.frame()
            
            # Create CGImage
            image = Quartz.CGWindowListCreateImage(
                rect,
                Quartz.kCGWindowListOptionOnScreenOnly,
                Quartz.kCGNullWindowID,
                Quartz.kCGWindowImageDefault
            )
            
            # Convert to PIL Image
            width = Quartz.CGImageGetWidth(image)
            height = Quartz.CGImageGetHeight(image)
            bytesperrow = Quartz.CGImageGetBytesPerRow(image)
            
            # Create PIL Image
            pil_image = Image.frombytes(
                'RGBA',
                (width, height),
                Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(image)),
                'raw',
                'BGRA'
            )
            
            # Save image
            pil_image.save(filepath)
            return True
        except Exception:
            return False

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen dimensions

        Returns:
            tuple: A tuple containing the width and height of the screen in pixels.
        """
        screen = NSScreen.mainScreen()
        rect = screen.frame()
        return (int(rect.size.width), int(rect.size.height))

    def capture_screenshot(self) -> Optional[np.ndarray]:
        """
        Capture a screenshot of the main screen and return it as a numpy array.

        Returns:
            np.ndarray: A numpy array representation of the screenshot in RGBA format.
                        Returns None if capturing the screenshot fails.
        """
        try:
            # Get the main screen
            screen = NSScreen.mainScreen()
            rect = screen.frame()
            
            # Create CGImage
            image = Quartz.CGWindowListCreateImage(
                rect,
                Quartz.kCGWindowListOptionOnScreenOnly,
                Quartz.kCGNullWindowID,
                Quartz.kCGWindowImageDefault
            )
            
            # Convert to numpy array
            width = Quartz.CGImageGetWidth(image)
            height = Quartz.CGImageGetHeight(image)
            
            # Create PIL Image first
            pil_image = Image.frombytes(
                'RGBA',
                (width, height),
                Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(image)),
                'raw',
                'BGRA'
            )
            
            # Convert PIL image to numpy array
            return np.array(pil_image)
        except Exception:
            return None

    def get_window_handle(self, pid: Optional[int] = None) -> Optional[int]:
        """
        Get the window handle for a specific process ID.

        Args:
            pid (Optional[int]): The process ID to search for. If None, returns the first visible window handle found.

        Returns:
            Optional[int]: The window handle if found, otherwise None.
        """
        try:
            if pid is None:
                # Get frontmost application's main window
                app = NSWorkspace.sharedWorkspace().frontmostApplication()
                if app:
                    window_list = Quartz.CGWindowListCopyWindowInfo(
                        Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
                        Quartz.kCGNullWindowID
                    )
                    for window in window_list:
                        if window.get(Quartz.kCGWindowOwnerName, '') == app.localizedName():
                            return window.get(Quartz.kCGWindowNumber, 0)
            else:
                # Find window for specific process ID
                window_list = Quartz.CGWindowListCopyWindowInfo(
                    Quartz.kCGWindowListOptionAll,
                    Quartz.kCGNullWindowID
                )
                for window in window_list:
                    if window.get(Quartz.kCGWindowOwnerPID, 0) == pid:
                        return window.get(Quartz.kCGWindowNumber, 0)
            return None
        except Exception as e:
            print(f"Error getting window handle: {str(e)}")
            return None

    def find_window(self, title: str) -> Optional[Any]:
        """
        Find a window by its title
        
        Args:
            title: Window title to search for
            
        Returns:
            Window element if found, None otherwise
        """
        return self.find_element('name', title)

    def get_window_handles(self) -> List[Any]:
        """
        Get a list of all window handles in the system.
        
        Returns:
            List of window handles (AXUIElements) for all visible windows
        """
        windows = []
        workspace = NSWorkspace.sharedWorkspace()
        running_apps = workspace.runningApplications()
        
        for app in running_apps:
            if app.isActive():
                ax_app = self.ax.applicationWithPID_(app.processIdentifier())
                if ax_app:
                    window_list = ax_app.attributeValue_('AXWindows')
                    if window_list:
                        windows.extend(window_list)
        
        return windows

    def _get_frontmost_application(self) -> Optional[Any]:
        """
        Get the frontmost application.

        Returns:
            Optional[Any]: The frontmost application, or None if no application is found.
        """
        workspace = NSWorkspace.sharedWorkspace()
        frontmost_app = workspace.frontmostApplication()
        if frontmost_app:
            pid = frontmost_app.processIdentifier()
            return self.ax.applicationElementForPID_(pid)
        return None

    def _find_element_recursive(self, element: Any, by: str, value: str) -> Optional[Any]:
        """
        Recursively search for an element.

        Args:
            element: The element to start searching from.
            by: The strategy to find the element by (e.g. 'name', 'role', etc.).
            value: The value to search for using the specified strategy.

        Returns:
            The first matching element, or None if no matching element is found.
        """
        if self._matches_criteria(element, by, value):
            return element

        children = self._get_attribute(element, "AXChildren")
        if children:
            for child in children:
                result = self._find_element_recursive(child, by, value)
                if result:
                    return result
        return None

    def _find_elements_recursive(self, element: Any, by: str, value: str, results: List[Any]):
        """
        Recursively search for all matching elements

        Args:
            element: The element to start searching from.
            by: The strategy to find the element by (e.g. 'name', 'role', etc.).
            value: The value to search for using the specified strategy.
            results: List of elements that match the specified criteria.

        Returns:
            None
        """
        if self._matches_criteria(element, by, value):
            results.append(element)

        children = self._get_attribute(element, "AXChildren")
        if children:
            for child in children:
                self._find_elements_recursive(child, by, value, results)

    def _matches_criteria(self, element: Any, by: str, value: str) -> bool:
        """Check if element matches search criteria"""
        try:
            if by == "role":
                return self._get_attribute(element, "AXRole") == value
            elif by == "title":
                return self._get_attribute(element, "AXTitle") == value
            elif by == "description":
                return self._get_attribute(element, "AXDescription") == value
            elif by == "identifier":
                return self._get_attribute(element, "AXIdentifier") == value
        except Exception:
            pass
        return False

    def _get_attribute(self, element: Any, attribute: str) -> Any:
        """Get an accessibility attribute from an element"""
        try:
            return element.attributeValue_(attribute)
        except Exception:
            return None

    def check_accessibility(self, element: Optional[Any] = None) -> Dict[str, Any]:
        """
        Check accessibility of an element or the entire UI using macOS Accessibility API.

        Args:
            element: Optional element to check. If None, checks entire UI.

        Returns:
            Dictionary containing accessibility issues and their details
        """
        issues = {}
        try:
            if not objc:
                return {"error": "Objective-C bridge not available"}

            # Get the element to check
            target = element if element else self.system
            if not target:
                return {"error": "No target element available"}

            # Check role
            try:
                role = target.AXRole()
                if not role or role == "AXUnknown":
                    issues["role"] = "Element has unknown role"
            except:
                issues["role_error"] = "Could not check element role"

            # Check title/description
            try:
                title = target.AXTitle()
                if not title or title.isspace():
                    issues["missing_title"] = "Element lacks a title"
            except:
                issues["title_error"] = "Could not check element title"

            # Check help text
            try:
                help_text = target.AXHelp()
                if not help_text or help_text.isspace():
                    issues["missing_help"] = "Element lacks help text"
            except:
                issues["help_error"] = "Could not check element help text"

            # Check enabled state
            try:
                if not target.AXEnabled():
                    issues["disabled"] = "Element is disabled"
            except:
                issues["enabled_error"] = "Could not check if element is enabled"

            # Check focused state
            try:
                if not target.AXFocused():
                    issues["focus"] = "Element is not focused"
            except:
                issues["focus_error"] = "Could not check element focus"

            # Check position
            try:
                position = target.AXPosition()
                size = target.AXSize()
                if not position or not size:
                    issues["bounds"] = "Element lacks proper bounds"
            except:
                issues["bounds_error"] = "Could not check element bounds"

            return issues
        except Exception as e:
            return {"error": f"Accessibility check failed: {str(e)}"}

    def cleanup(self) -> None:
        """Clean up resources"""
        if hasattr(self, 'ax'):
            self.ax = None
        if hasattr(self, 'system'):
            self.system = None

    def set_ocr_languages(self, languages: List[str]) -> None:
        """
        Set OCR languages for text recognition.

        Args:
            languages: List of language codes (e.g., ['eng', 'fra'])
        """
        # macOS Accessibility API does not directly handle OCR
        # This is handled by the OCREngine class
        pass
