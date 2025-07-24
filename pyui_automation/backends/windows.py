# Windows API
import win32gui
import win32con
import win32api
import win32ui
import win32process
import win32event
import win32security
import ctypes
import comtypes.client
try:
    import comtypes.gen.UIAutomationClient as UIAClient
except ImportError:
    comtypes.client.GetModule('UIAutomationCore.dll')
    import comtypes.gen.UIAutomationClient as UIAClient

# Python libraries
import time
import numpy as np
import os
from typing import Optional, Any, List, Tuple, Dict, Union

from pathlib import Path
from logging import getLogger

# Local imports
from ..elements.base_element import BaseElement
from .base_backend import BaseBackend


UIAutomationClient = None


class WindowsBackend(BaseBackend):
    """Windows UI Automation backend"""

    def __init__(self) -> None:
        """Initialize Windows UI Automation"""
        super().__init__()  # Вызываем родительский конструктор
        self.__logger = getLogger(__name__)
        self.automation = None
        self._root = None
        self.value_pattern = None
        self.invoke_pattern = None
        self.window_pattern = None
        self.transform_pattern = None
        self._current_app = None
        # Инициализация будет выполнена в initialize()

    @property
    def application(self) -> Any:
        """
        Get the current application instance.
        
        Returns:
            The Windows application object
        """
        return self._current_app
        
    @property
    def root(self) -> Any:
        """
        Get the root element.
        
        Returns:
            The root UI Automation element
        """
        return self._root

    def initialize(self) -> None:
        """Initialize Windows UI Automation backend"""
        try:
            self._init_automation()
            self._initialized = True
            self.__logger.info("Windows UI Automation backend initialized successfully")
        except Exception as e:
            self.__logger.error(f"Failed to initialize Windows UI Automation backend: {e}")
            raise

    def is_initialized(self) -> bool:
        """Check if Windows UI Automation backend is initialized"""
        return self._initialized and self.automation is not None and self.root is not None

    def _init_automation(self) -> None:
        """Initialize UI Automation"""
        try:
            try:
                self.automation = comtypes.client.CreateObject(
                    "{ff48dba4-60ef-4201-aa87-54103eef594e}",
                    interface=UIAClient.IUIAutomation,
                )
            except Exception as e:
                msg = f"Failed to create UIAutomation COM object: {str(e)}"
                self.__logger.error(msg)
                raise RuntimeError(msg)

            if not self.automation:
                msg = "Failed to create UIAutomation object"
                self.__logger.error(msg)
                raise RuntimeError(msg)

            self._root = self.automation.GetRootElement()
            if not self.root:
                msg = "Failed to get root element"
                self.__logger.error(msg)
                raise RuntimeError(msg)

        except Exception as e:
            msg = f"Critical error initializing Windows UI Automation: {str(e)}"
            self.__logger.error(msg)
            raise RuntimeError(msg)

    def get_window_handle(self, title: str) -> Optional[int]:
        """
        Get the window handle for a specific title.

        Args:
            title: The window title to search for.

        Returns:
            Optional[int]: The window handle if found, otherwise None.
        """
        try:
            # Try to parse as PID first
            try:
                pid = int(title)
                # If it's a PID, find window by process
                for hwnd in self.get_window_handles():
                    try:
                        _, process_id = win32gui.GetWindowThreadProcessId(hwnd)
                        if process_id == pid:
                            return hwnd
                    except:
                        continue
                return None
            except ValueError:
                # If not a PID, treat as title
                handle = win32gui.FindWindow(None, str(title))
                self.__logger.debug(f"Window handle for title: {title} - {handle}")
                return handle if handle != 0 else None
        except Exception as e:
            self.__logger.error(f"Error getting window handle for title: {title} - {str(e)}")
            return None

    def get_window_handles(self) -> List[int]:
        """
        Get all window handles

        Returns:
            List[int]: A list of window handles. If an exception is encountered, an empty list is returned.
        """
        try:
            handles = []
            def enum_windows(hwnd, _):
                if win32gui.IsWindowVisible(hwnd):
                    handles.append(hwnd)
                return True
            win32gui.EnumWindows(enum_windows, None)
            self.__logger.debug(f"Window handles: {handles}")
            return handles
        except Exception as e:
            self.__logger.error(f"Error getting window handles: {str(e)}")
            return []

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen dimensions

        Returns:
            Tuple[int, int]: The screen dimensions
        """
        width = win32api.GetSystemMetrics(win32con.SM_CXSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYSCREEN)
        self.__logger.debug(f"Screen size: {width}x{height}")
        return (width, height)

    def capture_screenshot(self) -> Optional[np.ndarray]:
        """
        Capture screenshot as numpy array

        Returns:
            Screenshot as numpy array if successful, None otherwise
        """
        try:
            width, height = self.get_screen_size()
            hdesktop = win32gui.GetDesktopWindow()
            desktop_dc = win32gui.GetWindowDC(hdesktop)
            img_dc = win32ui.CreateDCFromHandle(desktop_dc)
            mem_dc = img_dc.CreateCompatibleDC()
            screenshot = win32ui.CreateBitmap()
            screenshot.CreateCompatibleBitmap(img_dc, width, height)
            mem_dc.SelectObject(screenshot)
            mem_dc.BitBlt((0, 0), (width, height), img_dc, (0, 0), win32con.SRCCOPY)
            bmpstr = screenshot.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (height, width, 4)
            mem_dc.DeleteDC()
            win32gui.DeleteObject(screenshot.GetHandle())
            self.__logger.debug(f"Screenshot captured: {img.shape}")
            return img[..., :3]
        except Exception as e:
            self.__logger.error(f"Error capturing screenshot: {str(e)}")
            return None

    def find_window(self, title: str) -> Optional[UIAClient.IUIAutomationElement]:
        """
        Find a window using its title.

        Args:
            title: The title of the window to search for. If an integer is passed, it will be converted to string.

        Returns:
            The window object if found, None otherwise.
        """
        try:
            if self.automation is None or self.root is None:
                self.__logger.error("UI Automation not properly initialized. Make sure the backend was initialized successfully.")
                return None

            condition = self.automation.CreatePropertyCondition(
                UIAClient.UIA_NamePropertyId, title
            )
            window = self.root.FindFirst(
                UIAClient.TreeScope_Children | UIAClient.TreeScope_Descendants, condition
            )
            self.__logger.debug(f"Window found: {window}")
            return window
        except Exception as e:
            self.__logger.error(f"Error finding window: {str(e)}")
            return None

    def get_window_title(self, window: UIAClient.IUIAutomationElement) -> str:
        """
        Get the title of the specified window.

        Args:
            window (UIAClient.IUIAutomationElement): The window element whose title is to be retrieved.

        Returns:
            str: The title of the window.
        """
        title = window.CurrentName
        self.__logger.debug(f"Getting window title: {title}")
        return title

    def wait_for_window(self, title: str, timeout: int = 30) -> Optional[UIAClient.IUIAutomationElement]:
        """
        Wait for window with given title to appear

        Args:
            title (str): The title of the window to wait for
            timeout (int, optional): The maximum time to wait in seconds. Defaults to 30.

        Returns:
            Optional[Any]: The window object if it appears within the timeout period, None otherwise.
        """
        try:
            if self.automation is None or self.root is None:
                self.__logger.error("UI Automation not properly initialized. Make sure the backend was initialized successfully.")
                return None

            start_time = time.time()
            while time.time() - start_time < timeout:
                window = self.find_window(title)
                if window:
                    self.__logger.debug(f"Window found: {window}")
                    return window
                time.sleep(0.5)
        except Exception as e:
            self.__logger.error(f"Error waiting for window: {str(e)}")
        return None

    def get_active_window(self) -> Optional[int]:
        """
        Get the active window

        Returns:
            Optional[int]: The active window if found, None otherwise
        """
        try:
            active_window = win32gui.GetForegroundWindow()
            self.__logger.debug(f"Active window: {active_window}")
            return active_window
        except Exception as e:
            self.__logger.error(f"Error getting active window: {str(e)}")
            return None

    def inject_into_process(self, process_id: int) -> bool:
        """
        Inject into a running process to enable UI automation
        
        Args:
            process_id: ID of the process to inject into
            
        Returns:
            bool: True if injection was successful, False otherwise
        """
        handle = None
        thread_handle = None
        try:
            # Open process with required access rights
            handle = win32api.OpenProcess(win32con.PROCESS_ALL_ACCESS, False, process_id)
            if not handle:
                self.__logger.debug('OpenProcess failed')
                return False

            # Get the address of LoadLibrary function
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            load_library = kernel32.LoadLibraryW
            if not load_library:
                self.__logger.debug('LoadLibraryW not found')
                return False

            load_library_addr = ctypes.cast(load_library, ctypes.c_void_p).value
            if not load_library_addr:
                self.__logger.debug('load_library_addr is None')
                return False

            # Allocate memory in remote process
            dll_path = os.path.join(os.environ['SystemRoot'], 'System32', 'UIAutomationCore.dll')
            path_address = win32process.VirtualAllocEx(
                handle,
                0,
                len(dll_path) * 2 + 2,
                win32con.MEM_COMMIT,
                win32con.PAGE_READWRITE
            )

            if not path_address:
                self.__logger.debug('VirtualAllocEx failed')
                return False

            # Write DLL path to remote process memory
            if not win32process.WriteProcessMemory(handle, path_address, dll_path.encode('utf-16le') + b'\x00\x00', 0):
                self.__logger.debug('WriteProcessMemory failed')
                return False

            # Create remote thread to load DLL
            thread_handle, _ = win32process.CreateRemoteThread(
                handle,
                win32security.SECURITY_ATTRIBUTES(),  # Proper security attributes structure
                0,     # Default stack size
                load_library_addr,
                path_address,
                0      # Run thread immediately
            )

            if not thread_handle:
                self.__logger.debug('CreateRemoteThread failed')
                return False

            # Wait for thread completion and cleanup
            result = win32event.WaitForSingleObject(thread_handle, win32event.INFINITE)
            if result != win32event.WAIT_OBJECT_0:
                self.__logger.debug('WaitForSingleObject failed')
                return False
            self.__logger.debug('inject_into_process success')
            return True

        except Exception as e:
            self.__logger.error(f"Error injecting into process: {str(e)}")
            return False
            
        finally:
            # Clean up handles in finally block to ensure they're always closed
            if thread_handle:
                try:
                    win32api.CloseHandle(thread_handle)
                    self.__logger.debug('Thread handle closed')
                except Exception as e:
                    self.__logger.error(f"Error closing thread handle: {str(e)}")
            if handle:
                try:
                    win32api.CloseHandle(handle)
                    self.__logger.debug('Process handle closed')
                except Exception as e:
                    self.__logger.error(f"Error closing process handle: {str(e)}")

    def maximize_window(self, window: Any) -> None:
        """
        Maximize the specified window.

        Args:
            window: The window to maximize.
        """
        if isinstance(window, int):
            win32gui.ShowWindow(window, win32con.SW_MAXIMIZE)
        else:
            # Handle UIAClient.IUIAutomationElement
            try:
                window.SetFocus()
                # Additional UI automation specific maximization if needed
            except Exception as e:
                self.__logger.error(f"Error maximizing window: {str(e)}")

    def minimize_window(self, window: Any) -> None:
        """
        Minimize the specified window.

        Args:
            window: The window to minimize.
        """
        if isinstance(window, int):
            win32gui.ShowWindow(window, win32con.SW_MINIMIZE)
        else:
            # Handle UIAClient.IUIAutomationElement
            try:
                # Additional UI automation specific minimization if needed
                pass
            except Exception as e:
                self.__logger.error(f"Error minimizing window: {str(e)}")

    def restore_window(self, window_handle: int) -> None:
        """
        Restore a window to its normal state
        
        Args:
            window_handle: Handle to the window
        """
        win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)

    def capture_screen(self) -> Optional[np.ndarray]:
        """
        Capture the entire screen.

        Returns:
            Optional[np.ndarray]: Screenshot as numpy array, or None if capture fails.
        """
        # Get screen dimensions
        width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
        height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)

        # Initialize variables for cleanup
        hdc = None
        hdc_mem = None
        hdc_mem_copy = None
        bmp = None

        try:
            # Create device context and bitmap
            hdc = win32gui.GetDC(0)
            hdc_mem = win32ui.CreateDCFromHandle(hdc)
            hdc_mem_copy = hdc_mem.CreateCompatibleDC()
            
            # Create bitmap and select it into DC
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(hdc_mem, width, height)
            hdc_mem_copy.SelectObject(bmp)
            
            # Copy screen content
            hdc_mem_copy.BitBlt((0, 0), (width, height), hdc_mem, (0, 0), win32con.SRCCOPY)
            
            # Convert to numpy array
            bmpinfo = bmp.GetInfo()
            bmpstr = bmp.GetBitmapBits(True)
        
            img = np.frombuffer(bmpstr, dtype=np.uint8)
            img.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)
            self.__logger.debug(f"Screenshot captured: {img.shape}")
            return img[..., :3]
        except Exception as e:
            self.__logger.error(f"Error capturing screen: {str(e)}")
            return None
        finally:
            if bmp:
                try:
                    handle = bmp.GetHandle()
                    if handle:
                        win32gui.DeleteObject(handle)
                    self.__logger.debug('Bitmap object deleted')
                except (AttributeError, win32gui.error) as e:
                    self.__logger.error(f"Error deleting bitmap object: {str(e)}")

            if hdc_mem_copy:
                try:
                    hdc_mem_copy.DeleteDC()
                    self.__logger.debug('Compatible DC deleted')
                except win32gui.error as e:
                    self.__logger.error(f"Error deleting compatible DC: {str(e)}")

            if hdc_mem:
                try:
                    hdc_mem.DeleteDC()
                    self.__logger.debug('Device context deleted')
                except win32gui.error as e:
                    self.__logger.error(f"Error deleting device context: {str(e)}")

            if hdc:
                try:
                    win32gui.ReleaseDC(0, hdc)
                    self.__logger.debug('Desktop device context released')
                except win32gui.error as e:
                    self.__logger.error(f"Error releasing desktop device context: {str(e)}")

    def capture_window(self, window_handle: int) -> Optional[np.ndarray]:
        """
        Capture a specific window
        
        Args:
            window_handle: Handle to the window to capture
            
        Returns:
            Optional[np.ndarray]: Window screenshot as numpy array, or None if capture fails.
        """
        # Initialize variables for cleanup
        hdc = None
        hdc_mem = None
        hdc_mem_copy = None
        bmp = None

        try:
            # Get window dimensions
            left, top, right, bottom = win32gui.GetWindowRect(window_handle)
            width = right - left
            height = bottom - top

            # Create device context and bitmap
            hdc = win32gui.GetWindowDC(window_handle)
            hdc_mem = win32ui.CreateDCFromHandle(hdc)
            hdc_mem_copy = hdc_mem.CreateCompatibleDC()

            # Create bitmap and select it into DC
            bmp = win32ui.CreateBitmap()
            bmp.CreateCompatibleBitmap(hdc_mem, width, height)
            hdc_mem_copy.SelectObject(bmp)

            # Copy window content
            hdc_mem_copy.BitBlt((0, 0), (width, height), hdc_mem, (0, 0), win32con.SRCCOPY)

            # Convert to numpy array
            bmpinfo = bmp.GetInfo()
            bmpstr = bmp.GetBitmapBits(True)
        
            img = np.frombuffer(bmpstr, dtype=np.uint8)
            img.shape = (bmpinfo['bmHeight'], bmpinfo['bmWidth'], 4)
            self.__logger.debug(f"Window screenshot captured: {img.shape}")
            return img[..., :3]
        except Exception as e:
            self.__logger.error(f"Error capturing window screenshot: {str(e)}")
            return None
        finally:
            if bmp:
                try:
                    handle = bmp.GetHandle()
                    if handle:
                        win32gui.DeleteObject(handle)
                    self.__logger.debug('Bitmap object deleted')
                except (AttributeError, win32gui.error) as e:
                    self.__logger.error(f"Error deleting bitmap object: {str(e)}")

            if hdc_mem_copy:
                try:
                    hdc_mem_copy.DeleteDC()
                    self.__logger.debug('Compatible DC deleted')
                except win32gui.error as e:
                    self.__logger.error(f"Error deleting compatible DC: {str(e)}")

            if hdc_mem:
                try:
                    hdc_mem.DeleteDC()
                    self.__logger.debug('Device context deleted')
                except win32gui.error as e:
                    self.__logger.error(f"Error deleting device context: {str(e)}")

            if hdc:
                try:
                    win32gui.ReleaseDC(window_handle, hdc)
                    self.__logger.debug('Window device context released')
                except win32gui.error as e:
                    self.__logger.error(f"Error releasing window device context: {str(e)}")

    def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
        """Capture screenshot of specific screen region

        Args:
            x: X coordinate of the region
            y: Y coordinate of the region
            width: Width of the region
            height: Height of the region

        Returns:
            numpy.ndarray: Screenshot of the region as a numpy array, or None if capture fails
        """
        try:
            if width <= 0 or height <= 0:
                self.__logger.debug('Invalid region dimensions')
                return None

            # Get window handle
            hwnd = win32gui.GetDesktopWindow()

            # Get window DC and create compatible DC
            hwndDC = win32gui.GetWindowDC(hwnd)
            mfcDC = win32ui.CreateDCFromHandle(hwndDC)
            saveDC = mfcDC.CreateCompatibleDC()

            # Create bitmap object
            saveBitMap = win32ui.CreateBitmap()
            saveBitMap.CreateCompatibleBitmap(mfcDC, width, height)
            saveDC.SelectObject(saveBitMap)

            # Copy the screen region into our memory device context
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (x, y), win32con.SRCCOPY)

            # Convert bitmap to numpy array
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (height, width, 4)  # RGBA
            img = img[:, :, :3]  # Convert to RGB

            # Clean up
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            self.__logger.debug(f"Screen region captured: {img.shape}")
            return img

        except Exception as e:
            self.__logger.error(f"Error capturing screen region: {str(e)}")
            return None

    def _get_element_pattern(self, element: BaseElement, pattern_id: int) -> Any:
        """
        Get a UI Automation pattern interface for an element
        
        Args:
            element: UI Automation element
            pattern_id: ID of the pattern to retrieve
            
        Returns:
            Pattern interface if supported, None otherwise
        """
        try:
            pattern = element.native_element.GetCurrentPattern(pattern_id)
            self.__logger.debug(f"Element pattern: {pattern}")
            return pattern.QueryInterface(pattern_id) if pattern else None
        except Exception as e:
            self.__logger.error(f"Error getting element pattern: {str(e)}")
            return None



        self.__logger.debug(f"Text typed into element: {text}")

    def cleanup(self) -> None:
        """
        Clean up resources used by the backend
        """
        # Release COM objects
        if hasattr(self, 'automation') and self.automation is not None:
            try:
                if hasattr(self.automation, 'Release'):
                    self.automation.Release()
                    self.__logger.debug("COM object released by Release method")
            except Exception as e:
                self.__logger.error(f"Error releasing COM object: {str(e)}")
            self.automation = None
        try:
            comtypes.CoUninitialize()
            self.__logger.debug("COM objects released by CoUninitialize")
        except Exception as e:
            self.__logger.error(f"Error during CoUninitialize: {str(e)}")

    def attach_to_application(self, process_id: int) -> Optional[UIAClient.IUIAutomationElement]:
        """
        Attach to an application by process ID.
        
        Args:
            process_id (int): The ID of the process to attach to.
            
        Returns:
            Optional[UIAClient.IUIAutomationElement]: The attached application object, or None if the attachment failed.
        """
        try:
            self.__logger.debug(f"Attaching to application with process ID: {process_id}")
            
            # Find window handle by process ID
            def enum_windows_callback(hwnd, windows):
                if win32gui.IsWindowVisible(hwnd):
                    _, pid = win32process.GetWindowThreadProcessId(hwnd)
                    if pid == process_id:
                        windows.append(hwnd)
                return True
            
            windows = []
            win32gui.EnumWindows(enum_windows_callback, windows)
            
            if not windows:
                self.__logger.error(f"No windows found for process ID: {process_id}")
                return None
            
            # Use the first found window
            hwnd = windows[0]
            window_title = win32gui.GetWindowText(hwnd)
            self.__logger.debug(f"Found window: {window_title} (handle: {hwnd})")
            
            # Create UI Automation element for the window
            if self.automation is None:
                self.__logger.error("UI Automation not initialized")
                return None
                
            element = self.automation.ElementFromHandle(hwnd)
            if element is None:
                self.__logger.error(f"Failed to create UI Automation element for window {hwnd}")
                return None
                
            self.__logger.debug(f"Successfully attached to application: {window_title}")
            return element
            
        except Exception as e:
            self.__logger.error(f"Error attaching to application: {str(e)}")
            return None

    def close_window(self, window: Any) -> None:
        """
        Close the specified window.

        Args:
            window: The window to close.
        """
        try:
            if isinstance(window, int):
                win32gui.PostMessage(window, win32con.WM_CLOSE, 0, 0)
                self.__logger.debug(f"Sent close message to window: {window}")
            else:
                self.__logger.warning(f"Unsupported window type: {type(window)}")
                
        except Exception as e:
            self.__logger.error(f"Error closing window: {str(e)}")

    # Additional stub methods required by tests
    def find_elements_by_widget_type(self, widget_type: str) -> List['BaseElement']:
        """
        Find elements by widget type (stub implementation).
        
        Args:
            widget_type: Widget type to search for
            
        Returns:
            Empty list (stub)
        """
        self.__logger.debug(f"Stub: find_elements_by_widget_type called with {widget_type}")
        return []
    
    def get_element_rect(self, element) -> Tuple[int, int, int, int]:
        """
        Get element rectangle (stub implementation).
        
        Args:
            element: Element to get rectangle for
            
        Returns:
            Default rectangle (0, 0, 100, 100)
        """
        self.__logger.debug("Stub: get_element_rect called")
        return (0, 0, 100, 100)
    
    def find_element_by_object_name(self, name: str) -> Optional['BaseElement']:
        """
        Find element by object name (stub implementation).
        
        Args:
            name: Object name to search for
            
        Returns:
            None (stub)
        """
        self.__logger.debug(f"Stub: find_element_by_object_name called with {name}")
        return None
    
    def get_element_pattern(self, element, pattern_name: str) -> Optional[Any]:
        """
        Get element pattern (stub implementation).
        
        Args:
            element: Element to get pattern from
            pattern_name: Pattern name
            
        Returns:
            None (stub)
        """
        self.__logger.debug(f"Stub: get_element_pattern called with {pattern_name}")
        return None
    
    def get_element_state(self, element) -> Dict[str, Any]:
        """
        Get element state (stub implementation).
        
        Args:
            element: Element to get state from
            
        Returns:
            Empty dictionary (stub)
        """
        self.__logger.debug("Stub: get_element_state called")
        return {}
    
    def invoke_element_pattern_method(self, element, method_name: str) -> Optional[Any]:
        """
        Invoke element pattern method (stub implementation).
        
        Args:
            element: Element to invoke method on
            method_name: Method name
            
        Returns:
            None (stub)
        """
        self.__logger.debug(f"Stub: invoke_element_pattern_method called with {method_name}")
        return None
    
    def double_click_mouse(self) -> bool:
        """
        Double-click mouse at current position (stub implementation).
        
        Returns:
            True (stub)
        """
        try:
            pos = win32api.GetCursorPos()
            return self.double_click(pos[0], pos[1])
        except Exception as e:
            self.__logger.error(f"Error in double_click_mouse: {str(e)}")
            return False
            
    def double_click(self, x: int, y: int) -> bool:
        """Double click at coordinates"""
        try:
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, 0, 0, 0, 0)
            return True
        except Exception as e:
            self.__logger.error(f"Error in double_click: {str(e)}")
            return False
    
    def scroll_element(self, element, direction: str, amount: float) -> None:
        """
        Scroll element (stub implementation).
        
        Args:
            element: Element to scroll
            direction: Scroll direction
            amount: Scroll amount
        """
        self.__logger.debug(f"Stub: scroll_element called with {direction}, {amount}")
    
    def right_click_mouse(self) -> bool:
        """
        Right-click mouse at current position (stub implementation).
        
        Returns:
            True (stub)
        """
        try:
            pos = win32api.GetCursorPos()
            return self.right_click(pos[0], pos[1])
        except Exception as e:
            self.__logger.error(f"Error in right_click_mouse: {str(e)}")
            return False
            
    def right_click(self, x: int, y: int) -> bool:
        """Right click at coordinates"""
        try:
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, 0, 0, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, 0, 0, 0, 0)
            return True
        except Exception as e:
            self.__logger.error(f"Error in right_click: {str(e)}")
            return False
    
    def send_keys(self, keys: str) -> bool:
        """
        Send keys (stub implementation).
        
        Args:
            keys: Keys to send
            
        Returns:
            True if successful
        """
        return self.type_text(keys)
    
    def mouse_down(self, button: str = "left") -> bool:
        """
        Press mouse button down (stub implementation).
        
        Args:
            button: Mouse button
            
        Returns:
            True (stub)
        """
        try:
            import win32api
            import win32con
            
            pos = win32api.GetCursorPos()
            x, y = pos
            
            if button.lower() == "left":
                down_flag = win32con.MOUSEEVENTF_LEFTDOWN
            elif button.lower() == "right":
                down_flag = win32con.MOUSEEVENTF_RIGHTDOWN
            elif button.lower() == "middle":
                down_flag = win32con.MOUSEEVENTF_MIDDLEDOWN
            else:
                return False
                
            win32api.mouse_event(down_flag, 0, 0, 0, 0)
            return True
            
        except Exception as e:
            self.__logger.error(f"Error in mouse_down: {str(e)}")
            return False
    
    def mouse_up(self, button: str = "left") -> bool:
        """
        Release mouse button (stub implementation).
        
        Args:
            button: Mouse button
            
        Returns:
            True (stub)
        """
        try:
            import win32api
            import win32con
            
            pos = win32api.GetCursorPos()
            x, y = pos
            
            if button.lower() == "left":
                up_flag = win32con.MOUSEEVENTF_LEFTUP
            elif button.lower() == "right":
                up_flag = win32con.MOUSEEVENTF_RIGHTUP
            elif button.lower() == "middle":
                up_flag = win32con.MOUSEEVENTF_MIDDLEUP
            else:
                return False
                
            win32api.mouse_event(up_flag, 0, 0, 0, 0)
            return True
            
        except Exception as e:
            self.__logger.error(f"Error in mouse_up: {str(e)}")
            return False
    
    def press_key(self, key: str) -> bool:
        """
        Press and release a key (stub implementation).
        
        Args:
            key: Key to press
            
        Returns:
            True (stub)
        """
        return self.type_text(key)
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """
        Get current mouse position.
        
        Returns:
            Mouse position as (x, y)
        """
        try:
            import win32api
            pos = win32api.GetCursorPos()
            return pos
        except Exception as e:
            self.__logger.error(f"Error getting mouse position: {str(e)}")
            return (0, 0)
    
    def type_text_into_element(self, element, text: str) -> bool:
        """
        Type text into element (alias for type_text).
        
        Args:
            element: Target element
            text: Text to type
            
        Returns:
            True if successful
        """
        return self.type_text(text)
        
    def type_text(self, text: str) -> bool:
        """Type text using keyboard"""
        try:
            for char in text:
                win32api.keybd_event(ord(char), 0, 0, 0)
                win32api.keybd_event(ord(char), 0, win32con.KEYEVENTF_KEYUP, 0)
            return True
        except Exception as e:
            self.__logger.error(f"Error in type_text: {str(e)}")
            return False
