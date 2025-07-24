# type: ignore
# Python libraries
from typing import Optional, List, Tuple, Any
import numpy as np
from PIL import Image
import platform
import subprocess

# macOS-specific libraries
try:
    if platform.system() == 'Darwin':
        import objc  # type: ignore
        import Quartz  # type: ignore
        from AppKit import NSWorkspace, NSScreen  # type: ignore
        from Cocoa import NSApplication, NSWindow, NSRunningApplication  # type: ignore
    else:
        objc = None
        Quartz = None
        NSWorkspace = None
        NSScreen = None
except ImportError:
    objc = None
    Quartz = None
    NSWorkspace = None
    NSScreen = None

# Local libraries
from .base_backend import BaseBackend


class MacOSBackend(BaseBackend):
    """macOS-specific implementation using Apple Accessibility API"""

    def __init__(self) -> None:
        """
        Initialize the MacOSBackend.

        Raises:
            RuntimeError: If platform is not macOS
        """
        super().__init__()  # Вызываем родительский конструктор
        if platform.system() != 'Darwin':
            raise RuntimeError("MacOSBackend can only be used on macOS systems")
        if objc is None:
            raise RuntimeError("objc is not available")
        self.ax = None
        self.system = None
        # Инициализация будет выполнена в initialize()

    def initialize(self) -> None:
        """Initialize macOS UI Automation backend"""
        try:
            self.ax = objc.ObjCClass('AXUIElement')
            self.system = self.ax.systemWide()
            self._initialized = True
            self._logger.info("macOS UI Automation backend initialized successfully")
        except Exception as e:
            self._logger.error(f"Failed to initialize macOS UI Automation backend: {e}")
            raise

    def is_initialized(self) -> bool:
        """Check if macOS UI Automation backend is initialized"""
        return self._initialized and self.ax is not None and self.system is not None

    def get_active_window(self) -> Optional[Any]:
        """
        Get the currently active window

        Returns:
            Optional[Any]: The currently active window, or None if no window is active
        """
        app = self._get_frontmost_application()
        if app:
            windows = self._get_attribute(app, "AXWindows")
            if windows and len(windows) > 0:
                return windows[0]
        return None

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen dimensions

        Returns:
            tuple: A tuple containing the width and height of the screen in pixels.
        """
        if NSScreen is None:
            return (0, 0)
        screen = NSScreen.mainScreen()  # type: ignore
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
            if NSScreen is None or Quartz is None:
                return None
            # Get the main screen
            screen = NSScreen.mainScreen()  # type: ignore
            rect = screen.frame()
            
            # Create CGImage
            image = Quartz.CGWindowListCreateImage(  # type: ignore
                rect,
                Quartz.kCGWindowListOptionOnScreenOnly,  # type: ignore
                Quartz.kCGNullWindowID,  # type: ignore
                Quartz.kCGWindowImageDefault  # type: ignore
            )
            
            # Convert to numpy array
            width = Quartz.CGImageGetWidth(image)  # type: ignore
            height = Quartz.CGImageGetHeight(image)  # type: ignore
            
            # Create PIL Image first
            pil_image = Image.frombytes(
                'RGBA',
                (width, height),
                Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(image)),  # type: ignore
                'raw',
                'BGRA'
            )
            
            # Convert PIL image to numpy array
            return np.array(pil_image)
        except Exception:
            return None

    def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        """
        Capture screenshot of specific screen region

        Args:
            x: X coordinate of the region
            y: Y coordinate of the region
            width: Width of the region
            height: Height of the region

        Returns:
            Screenshot of the region as numpy array if successful, None otherwise
        """
        try:
            if width <= 0 or height <= 0:
                return None
            if Quartz is None:
                return None
                
            # Create CGRect for the specific region
            rect = Quartz.CGRectMake(x, y, width, height)  # type: ignore
            
            # Create CGImage for the region
            image = Quartz.CGWindowListCreateImage(  # type: ignore
                rect,
                Quartz.kCGWindowListOptionOnScreenOnly,  # type: ignore
                Quartz.kCGNullWindowID,  # type: ignore
                Quartz.kCGWindowImageDefault  # type: ignore
            )
            
            # Convert to numpy array
            width = Quartz.CGImageGetWidth(image)  # type: ignore
            height = Quartz.CGImageGetHeight(image)  # type: ignore
            
            # Create PIL Image first
            pil_image = Image.frombytes(
                'RGBA',
                (width, height),
                Quartz.CGDataProviderCopyData(Quartz.CGImageGetDataProvider(image)),  # type: ignore
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
            if NSWorkspace is None or Quartz is None:
                return None
            if pid is None:
                # Get frontmost application's main window
                app = NSWorkspace.sharedWorkspace().frontmostApplication()  # type: ignore
                if app:
                    window_list = Quartz.CGWindowListCopyWindowInfo(  # type: ignore
                        Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,  # type: ignore
                        Quartz.kCGNullWindowID  # type: ignore
                    )
                    for window in window_list:
                        if window.get(Quartz.kCGWindowOwnerName, '') == app.localizedName():  # type: ignore
                            return window.get(Quartz.kCGWindowNumber, 0)  # type: ignore
            else:
                # Find window for specific process ID
                window_list = Quartz.CGWindowListCopyWindowInfo(  # type: ignore
                    Quartz.kCGWindowListOptionAll,  # type: ignore
                    Quartz.kCGNullWindowID  # type: ignore
                )
                for window in window_list:
                    if window.get(Quartz.kCGWindowOwnerPID, 0) == pid:  # type: ignore
                        return window.get(Quartz.kCGWindowNumber, 0)  # type: ignore
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
        try:
            window_list = Quartz.CGWindowListCopyWindowInfo(
                Quartz.kCGWindowListOptionOnScreenOnly | Quartz.kCGWindowListExcludeDesktopElements,
                Quartz.kCGNullWindowID
            )
            for window in window_list:
                window_title = window.get(Quartz.kCGWindowName, '')
                if window_title == title:
                    window_id = window.get(Quartz.kCGWindowNumber, 0)
                    return self.ax.windowWithID_(window_id)
            return None
        except Exception:
            return None

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

    def get_window_title(self, window: Any) -> str:
        """
        Get window title
        
        Args:
            window: Window object
            
        Returns:
            Window title as string
        """
        try:
            title = self._get_attribute(window, "AXTitle")
            return title if title else ""
        except Exception:
            return ""

    def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
        """
        Get window position and size
        
        Args:
            window: Window object
            
        Returns:
            Tuple of (x, y, width, height)
        """
        try:
            position = self._get_attribute(window, "AXPosition")
            size = self._get_attribute(window, "AXSize")
            if position and size:
                return (position.x, position.y, size.width, size.height)
            return (0, 0, 0, 0)
        except Exception:
            return (0, 0, 0, 0)

    def maximize_window(self, window: Any) -> None:
        """
        Maximize window
        
        Args:
            window: Window object
        """
        try:
            self._set_attribute(window, "AXFullScreen", True)
        except Exception:
            pass

    def minimize_window(self, window: Any) -> None:
        """
        Minimize window
        
        Args:
            window: Window object
        """
        try:
            self._set_attribute(window, "AXMinimized", True)
        except Exception:
            pass

    def resize_window(self, window: Any, width: int, height: int) -> None:
        """
        Resize window
        
        Args:
            window: Window object
            width: New width
            height: New height
        """
        try:
            from Foundation import NSMakeSize
            new_size = NSMakeSize(width, height)
            self._set_attribute(window, "AXSize", new_size)
        except Exception:
            pass

    def set_window_position(self, window: Any, x: int, y: int) -> None:
        """
        Set window position
        
        Args:
            window: Window object
            x: New x position
            y: New y position
        """
        try:
            from Foundation import NSMakePoint
            new_position = NSMakePoint(x, y)
            self._set_attribute(window, "AXPosition", new_position)
        except Exception:
            pass

    def close_window(self, window: Any) -> None:
        """
        Close window
        
        Args:
            window: Window object
        """
        try:
            # Try to close using AXCloseButton
            close_button = self._get_attribute(window, "AXCloseButton")
            if close_button:
                close_button.performAction_("AXPress")
        except Exception:
            pass

    def launch_application(self, path: str, args: List[str]) -> None:
        """
        Launch application
        
        Args:
            path: Path to application
            args: Command line arguments
        """
        try:
            cmd = [path] + args
            subprocess.Popen(cmd)
        except Exception as e:
            print(f"Error launching application: {str(e)}")

    def attach_to_application(self, process_id: int) -> Optional[Any]:
        """
        Attach to existing application
        
        Args:
            process_id: Process ID to attach to
            
        Returns:
            Application object if found, None otherwise
        """
        try:
            app = self.ax.applicationElementForPID_(process_id)
            if app:
                self._current_app = app
                return app
            return None
        except Exception:
            return None

    def close_application(self, application: Any) -> None:
        """
        Close application
        
        Args:
            application: Application object
        """
        try:
            # Try to quit the application
            quit_button = self._get_attribute(application, "AXQuitButton")
            if quit_button:
                quit_button.performAction_("AXPress")
        except Exception:
            pass

    def get_application(self) -> Optional[Any]:
        """
        Get current application
        
        Returns:
            Current application object or None
        """
        return self._current_app

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

    def _get_attribute(self, element: Any, attribute: str) -> Any:
        """
        Get attribute value from element
        
        Args:
            element: UI element
            attribute: Attribute name
            
        Returns:
            Attribute value or None
        """
        try:
            return element.attributeValue_(attribute)
        except Exception:
            return None

    def _set_attribute(self, element: Any, attribute: str, value: Any) -> bool:
        """
        Set attribute value on element
        
        Args:
            element: UI element
            attribute: Attribute name
            value: New value
            
        Returns:
            True if successful, False otherwise
        """
        try:
            element.setAttributeValue_forAttribute_(value, attribute)
            return True
        except Exception:
            return False

    def cleanup(self) -> None:
        """Clean up resources"""
        if hasattr(self, 'ax'):
            self.ax = None
        if hasattr(self, 'system'):
            self.system = None

