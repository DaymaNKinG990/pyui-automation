from typing import Optional, List, Tuple, Any
import win32gui
import win32ui
import win32con
import win32api
from PIL import Image
import numpy as np
from comtypes.client import CreateObject
from comtypes.gen.UIAutomationClient import *

from .base import BaseBackend


class WindowsBackend(BaseBackend):
    """Windows-specific implementation using UI Automation"""

    def __init__(self):
        self.automation = CreateObject("UIAutomation.UIAutomation")
        self.root = self.automation.GetRootElement()

    def find_element(self, by: str, value: str) -> Optional[Any]:
        """Find a UI element using Windows UI Automation"""
        condition = self._create_condition(by, value)
        if condition:
            return self.root.FindFirst(TreeScope_Children | TreeScope_Descendants, condition)
        return None

    def find_elements(self, by: str, value: str) -> List[Any]:
        """Find all matching UI elements"""
        condition = self._create_condition(by, value)
        if condition:
            return list(self.root.FindAll(TreeScope_Children | TreeScope_Descendants, condition))
        return []

    def get_active_window(self) -> Optional[Any]:
        """Get the currently active window"""
        hwnd = win32gui.GetForegroundWindow()
        if hwnd:
            element = self.automation.ElementFromHandle(hwnd)
            return element
        return None

    def take_screenshot(self, filepath: str) -> bool:
        """Take a screenshot using Win32 API"""
        try:
            # Get handle to the main screen
            hwnd = win32gui.GetDesktopWindow()
            
            # Get screen dimensions
            width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            
            # Create device context
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()
            
            # Create bitmap
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)
            
            # Copy screen content
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (0, 0), win32con.SRCCOPY)
            
            # Convert to PIL Image and save
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            im = Image.frombuffer(
                'RGB',
                (bmpinfo['bmWidth'], bmpinfo['bmHeight']),
                bmpstr, 'raw', 'BGRX', 0, 1)
            
            im.save(filepath)
            
            # Cleanup
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)
            
            return True
        except Exception:
            return False

    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions"""
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
        return (width, height)

    def _create_condition(self, by: str, value: str) -> Optional[Any]:
        """Create a search condition based on the search strategy"""
        if by == "id":
            return self.automation.CreatePropertyCondition(
                UIA_AutomationIdPropertyId, value
            )
        elif by == "name":
            return self.automation.CreatePropertyCondition(
                UIA_NamePropertyId, value
            )
        elif by == "class":
            return self.automation.CreatePropertyCondition(
                UIA_ClassNamePropertyId, value
            )
        elif by == "control_type":
            control_type = getattr(self.automation, f"UIA_{value}ControlTypeId")
            return self.automation.CreatePropertyCondition(
                UIA_ControlTypePropertyId, control_type
            )
        return None
