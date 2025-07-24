# type: ignore
# Python libraries
import sys
import platform
from typing import Optional, List, Tuple, Any
import numpy as np
from PIL import Image
import subprocess

# Linux-specific libraries
try:
    if platform.system() == 'Linux':
        import pyatspi  # type: ignore
        from Xlib import display, X  # type: ignore
    else:
        pyatspi = None
        display = None
        X = None
except ImportError:
    pyatspi = None
    display = None
    X = None

# Local libraries
from .base_backend import BaseBackend


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
        super().__init__()  # Вызываем родительский конструктор
        if sys.platform != 'linux':
            raise RuntimeError("LinuxBackend can only be used on Linux systems")
        if display is None:
            raise RuntimeError("Xlib.display is not available")
        if pyatspi is None:
            raise RuntimeError("pyatspi is not available")
        self.display = None
        self.screen = None
        self.registry = None
        self._current_app = None
        self._ocr_languages = []
        # Инициализация будет выполнена в initialize()

    def initialize(self) -> None:
        """Initialize Linux UI Automation backend"""
        try:
            self.display = display.Display()
            self.screen = self.display.screen()
            self.registry = pyatspi.Registry
            self.registry.start()
            self._initialized = True
            self._logger.info("Linux UI Automation backend initialized successfully")
        except Exception as e:
            self._logger.error(f"Failed to initialize Linux UI Automation backend: {e}")
            raise

    def is_initialized(self) -> bool:
        """Check if Linux UI Automation backend is initialized"""
        return self._initialized and self.display is not None and self.registry is not None

    @property
    def application(self) -> Any:
        """
        Get the current application instance.
        
        Returns:
            The Linux application object
        """
        return self._current_app

    def get_active_window(self) -> Optional[Any]:
        """
        Get the currently active window

        Returns:
            Optional[Any]: The currently active window, or None if no window is active
        """
        if pyatspi is None:
            return None
        desktop = self.registry.getDesktop(0)
        for app in desktop:
            if app.getState().contains(pyatspi.STATE_ACTIVE):  # type: ignore
                return app.id
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
            if X is None:
                return None
                
            root = self.display.screen().root
            raw = root.get_image(x, y, width, height, X.ZPixmap, 0xffffffff)
            image = Image.frombytes("RGB", (width, height), raw.data, "raw", "BGRX")
            return np.array(image)
        except Exception:
            return None

    def capture_screenshot(self) -> Optional[np.ndarray]:
        """
        Capture full screenshot as numpy array

        Returns:
            Screenshot as numpy array if successful, None otherwise
        """
        try:
            width, height = self.get_screen_size()
            return self.capture_screen_region(0, 0, width, height)
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
                if window.get_wm_class() and window.get_attributes().map_state == X.IsViewable:  # type: ignore
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
                if attrs is not None and hasattr(attrs, 'map_state') and attrs.map_state == X.IsViewable and not attrs.override_redirect:  # type: ignore
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

    def get_window_title(self, window: Any) -> str:
        """
        Get window title
        
        Args:
            window: Window object
            
        Returns:
            Window title as string
        """
        try:
            if hasattr(window, 'name'):
                return window.name
            return ""
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
            if hasattr(window, 'getExtents'):
                extents = window.getExtents()
                return (extents.x, extents.y, extents.width, extents.height)
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
            if hasattr(window, 'setState'):
                window.setState(pyatspi.STATE_MAXIMIZED)  # type: ignore
        except Exception:
            pass

    def minimize_window(self, window: Any) -> None:
        """
        Minimize window
        
        Args:
            window: Window object
        """
        try:
            if hasattr(window, 'setState'):
                window.setState(pyatspi.STATE_MINIMIZED)  # type: ignore
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
            if hasattr(window, 'setExtents'):
                current_bounds = self.get_window_bounds(window)
                window.setExtents(current_bounds[0], current_bounds[1], width, height)
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
            if hasattr(window, 'setExtents'):
                current_bounds = self.get_window_bounds(window)
                window.setExtents(x, y, current_bounds[2], current_bounds[3])
        except Exception:
            pass

    def close_window(self, window: Any) -> None:
        """
        Close window
        
        Args:
            window: Window object
        """
        try:
            if hasattr(window, 'destroy'):
                window.destroy()
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
            desktop = self.registry.getDesktop(0)
            for app in desktop:
                if app.id == process_id:
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
            if hasattr(application, 'destroy'):
                application.destroy()
        except Exception:
            pass

    def get_application(self) -> Optional[Any]:
        """
        Get current application
        
        Returns:
            Current application object or None
        """
        return self._current_app

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
