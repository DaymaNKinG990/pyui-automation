import time
from typing import Union
import platform

if platform.system() == 'Windows':
    import win32api
    import win32con
elif platform.system() == 'Linux':
    from Xlib import X, display
    from Xlib.ext.xtest import fake_input
else:  # macOS
    from Quartz import *


class Keyboard:
    """Cross-platform keyboard input handling"""

    def __init__(self):
        self.platform = platform.system().lower()
        if self.platform == 'linux':
            self.display = display.Display()

    def type_text(self, text: str, interval: float = 0.0):
        """Type text with optional interval between keystrokes"""
        for char in text:
            self.press_key(char)
            self.release_key(char)
            if interval > 0:
                time.sleep(interval)

    def press_key(self, key: Union[str, int]):
        """Press a key"""
        if self.platform == 'windows':
            win32api.keybd_event(self._get_vk_code(key), 0, 0, 0)
        elif self.platform == 'linux':
            keycode = self.display.keysym_to_keycode(ord(key))
            fake_input(self.display, X.KeyPress, keycode)
            self.display.sync()
        else:  # macOS
            event = CGEventCreateKeyboardEvent(None, ord(key), True)
            CGEventPost(kCGHIDEventTap, event)

    def release_key(self, key: Union[str, int]):
        """Release a key"""
        if self.platform == 'windows':
            win32api.keybd_event(self._get_vk_code(key), 0, win32con.KEYEVENTF_KEYUP, 0)
        elif self.platform == 'linux':
            keycode = self.display.keysym_to_keycode(ord(key))
            fake_input(self.display, X.KeyRelease, keycode)
            self.display.sync()
        else:  # macOS
            event = CGEventCreateKeyboardEvent(None, ord(key), False)
            CGEventPost(kCGHIDEventTap, event)

    def _get_vk_code(self, key: Union[str, int]) -> int:
        """Convert character to virtual key code (Windows-specific)"""
        if isinstance(key, int):
            return key
        return ord(key.upper())


class Mouse:
    """Cross-platform mouse input handling"""

    def __init__(self):
        self.platform = platform.system().lower()
        if self.platform == 'linux':
            self.display = display.Display()

    def move(self, x: int, y: int):
        """Move mouse to specific coordinates"""
        if self.platform == 'windows':
            win32api.SetCursorPos((x, y))
        elif self.platform == 'linux':
            fake_input(self.display, X.MotionNotify, x=x, y=y)
            self.display.sync()
        else:  # macOS
            move = CGEventCreateMouseEvent(
                None, kCGEventMouseMoved, CGPoint(x, y), kCGMouseButtonLeft
            )
            CGEventPost(kCGHIDEventTap, move)

    def click(self, button: str = "left"):
        """Perform mouse click"""
        if self.platform == 'windows':
            if button == "left":
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0)
            else:
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0)
                win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0)
        elif self.platform == 'linux':
            button_num = 1 if button == "left" else 3
            fake_input(self.display, X.ButtonPress, button_num)
            self.display.sync()
            fake_input(self.display, X.ButtonRelease, button_num)
            self.display.sync()
        else:  # macOS
            button_type = kCGMouseButtonLeft if button == "left" else kCGMouseButtonRight
            pos = CGEventGetLocation(CGEventCreate(None))
            click_down = CGEventCreateMouseEvent(
                None, kCGEventLeftMouseDown if button == "left" else kCGEventRightMouseDown,
                pos, button_type
            )
            click_up = CGEventCreateMouseEvent(
                None, kCGEventLeftMouseUp if button == "left" else kCGEventRightMouseUp,
                pos, button_type
            )
            CGEventPost(kCGHIDEventTap, click_down)
            CGEventPost(kCGHIDEventTap, click_up)
