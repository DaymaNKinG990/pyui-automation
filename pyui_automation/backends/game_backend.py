import platform
from typing import Optional, Tuple
import numpy as np
from PIL import Image
import cv2
import pyautogui
from .base import BaseBackend

class GameBackend(BaseBackend):
    """Backend for interacting with game windows across different platforms."""
    
    def __init__(self):
        super().__init__()
        self.window_title = None
        self.region = None
        pyautogui.FAILSAFE = True
        
    def connect(self, window_title: str) -> bool:
        """Connect to a game window by its title."""
        self.window_title = window_title
        try:
            if platform.system() == "Windows":
                import win32gui
                hwnd = win32gui.FindWindow(None, window_title)
                if hwnd:
                    self.region = win32gui.GetWindowRect(hwnd)
                    return True
            elif platform.system() == "Darwin":  # macOS
                # On macOS, we'll work with the active window
                self.region = None
                return True
            else:  # Linux
                # On Linux, we'll need to use X11 to find the window
                from Xlib import display, X
                d = display.Display()
                root = d.screen().root
                window_list = root.get_full_property(
                    d.intern_atom('_NET_CLIENT_LIST'),
                    X.AnyPropertyType
                ).value
                for window_id in window_list:
                    window = d.create_resource_object('window', window_id)
                    name = window.get_wm_name()
                    if name and window_title in name:
                        geometry = window.get_geometry()
                        self.region = (geometry.x, geometry.y, 
                                     geometry.x + geometry.width,
                                     geometry.y + geometry.height)
                        return True
        except Exception as e:
            print(f"Failed to connect to window: {e}")
        return False
        
    def capture_screen(self) -> Optional[Image.Image]:
        """Capture the game window content."""
        try:
            if self.region:
                screenshot = pyautogui.screenshot(region=self.region)
            else:
                screenshot = pyautogui.screenshot()
            return screenshot
        except Exception as e:
            print(f"Failed to capture screen: {e}")
            return None
            
    def find_element(self, template: Image.Image, threshold: float = 0.8, region=None) -> Optional[Tuple[int, int]]:
        """Find an element in the game window using template matching."""
        try:
            screen = self.capture_screen() if region is None else pyautogui.screenshot(region=region)
        except Exception:
            return None
        if screen is None:
            return None
        screen_np = np.array(screen)
        template_np = np.array(template)
        screen_gray = cv2.cvtColor(screen_np, cv2.COLOR_RGB2GRAY)
        template_gray = cv2.cvtColor(template_np, cv2.COLOR_RGB2GRAY)
        result = cv2.matchTemplate(screen_gray, template_gray, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        if max_val >= threshold:
            x, y = max_loc
            if region:
                x += region[0]
                y += region[1]
            elif self.region:
                x += self.region[0]
                y += self.region[1]
            return (x, y)
        return None
