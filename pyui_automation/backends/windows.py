import os
from typing import Optional, Any, List, Tuple, Dict
import win32gui
import win32con
import win32api
import win32ui
import win32process
import win32event
import time
import numpy as np
from PIL import Image
import comtypes.client
import comtypes.gen.UIAutomationClient as UIAClient
import ctypes
import win32security
from .base import BaseBackend

class WindowsBackend(BaseBackend):
    """Windows UI Automation backend"""

    def __init__(self):
        """Initialize Windows UI Automation"""
        # Check if running with admin privileges
        if not ctypes.windll.shell32.IsUserAnAdmin():
            raise RuntimeError("Windows UI Automation requires admin privileges")

        try:
            # Create UI Automation object
            try:
                self.automation = comtypes.client.CreateObject(
                    "{ff48dba4-60ef-4201-aa87-54103eef594e}",
                    interface=UIAClient.IUIAutomation,
                )
            except Exception as e:
                raise RuntimeError(f"Failed to create UIAutomation COM object: {str(e)}")

            if not self.automation:
                raise RuntimeError("Failed to create UIAutomation object")

            # Get desktop root element
            self.root = self.automation.GetRootElement()
            if not self.root:
                raise RuntimeError("Failed to get root element")

        except Exception as e:
            raise RuntimeError(f"Critical error initializing Windows UI Automation: {str(e)}")

        self._init_patterns()
        self._current_app = None
        self._ocr_engine = None

    @property
    def ocr(self) -> Any:
        """
        Get the OCR engine instance.
        
        Returns:
            The OCR engine instance for text recognition
        """
        if self._ocr_engine is None:
            from ..ocr import OCREngine
            self._ocr_engine = OCREngine()
        return self._ocr_engine

    @property
    def application(self) -> Any:
        """
        Get the current application instance.
        
        Returns:
            The Windows application object
        """
        return self._current_app

    def _init_patterns(self):
        """Initialize commonly used UI Automation patterns"""
        self.value_pattern = None
        self.invoke_pattern = None
        self.window_pattern = None
        self.transform_pattern = None

    def find_element(self, by: str, value: str, timeout: float = 0) -> Optional[Any]:
        """
        Find a UI element using Windows UI Automation
        
        Args:
            by: Strategy to find element (e.g., 'id', 'name', 'class', 'xpath', etc.)
            value: Value to search for using the specified strategy
            timeout: Time to wait for element (0 for no wait)
        
        Returns:
            Found element, or None if no element is found or an error occurs
        """
        try:
            if self.automation is None:
                print("Error: UI Automation not initialized. Make sure __init__ completed successfully.")
                return None

            condition = self._create_condition(by, value)
            if not condition:
                print(f"Error: Could not create condition for {by}={value}")
                return None
                
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                print("Error: Could not get foreground window handle")
                return None

            element = self.automation.ElementFromHandle(hwnd)
            if not element:
                print("Error: Could not get element from window handle")
                return None
                
            return element.FindFirst(UIAClient.TreeScope_Descendants, condition)
        except:  # Catch all exceptions to ensure we return None
            return None

    def find_elements(self, by: str, value: str) -> List[Any]:
        """
        Find all matching UI elements using Windows UI Automation

        Args:
            by: Strategy to find elements (e.g., 'id', 'name', 'class', 'xpath', etc.)
            value: Value to search for using the specified strategy

        Returns:
            A list of all matching elements. If no elements are found or an error occurs, an empty list is returned.
        """
        try:
            if self.automation is None:
                print("Error: UI Automation not initialized properly")
                return []
                
            condition = self._create_condition(by, value)
            if not condition:
                return []
                
            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                print("Error: Could not get foreground window handle")
                return []
                
            element = self.automation.ElementFromHandle(hwnd)
            if not element:
                print("Error: Could not get element from window handle")
                return []
                
            elements = element.FindAll(UIAClient.TreeScope_Descendants, condition)
            if not elements:
                return []
            
            # Convert COM array to Python list
            result = []
            for i in range(elements.Length):
                result.append(elements.GetElement(i))
            return result
        except:  # Catch all exceptions to ensure we return empty list
            return []

    def get_active_window(self) -> Optional[Any]:
        """
        Get the currently active window
        
        Returns:
            Active window element, or None if not found or an error occurs
        """
        try:
            if not self.automation:
                print("Error: UI Automation is not initialized")
                return None

            hwnd = win32gui.GetForegroundWindow()
            if not hwnd:
                print("Error: No foreground window found")
                return None
            return self.automation.ElementFromHandle(hwnd)
        except:  # Catch all exceptions to ensure we return None
            return None

    def get_window_handle(self, title: str) -> Optional[int]:
        """
        Get the window handle for a specific title.

        Args:
            title: The window title to search for.

        Returns:
            Optional[int]: The window handle if found, otherwise None.
        """
        try:
            return win32gui.FindWindow(None, str(title))
        except:  # Catch all exceptions to ensure we return None
            return None

    def get_window_handles(self) -> List[int]:
        """
        Get all window handles

        Returns:
            List[int]: A list of window handles. If an exception is encountered, an empty list is returned.
        """
        try:
            handles = []
            def enum_windows(hwnd, results):
                if win32gui.IsWindowVisible(hwnd):
                    handles.append(hwnd)
                return True
            win32gui.EnumWindows(enum_windows, None)
            return handles
        except Exception as e:
            print(f"Error getting window handles: {str(e)}")
            return []

    def click(self, x: int, y: int, button: str = "left"):
        """
        Perform mouse click at coordinates

        Args:
            x (int): The x-coordinate of the click
            y (int): The y-coordinate of the click
            button (str): The button to click. Defaults to "left". Can be "left", "right", or "middle".

        Returns:
            bool: True if the click was successful, False otherwise
        """
        try:
            # Move cursor to position
            win32api.SetCursorPos((x, y))
            time.sleep(0.1)  # Small delay for cursor movement
            
            # Map button names to win32 constants
            button_map = {
                "left": (win32con.MOUSEEVENTF_LEFTDOWN, win32con.MOUSEEVENTF_LEFTUP),
                "right": (win32con.MOUSEEVENTF_RIGHTDOWN, win32con.MOUSEEVENTF_RIGHTUP),
                "middle": (win32con.MOUSEEVENTF_MIDDLEDOWN, win32con.MOUSEEVENTF_MIDDLEUP)
            }
            
            if button not in button_map:
                raise ValueError(f"Invalid button: {button}")
                
            down_event, up_event = button_map[button]
            
            # Perform click
            win32api.mouse_event(down_event, x, y, 0, 0)
            time.sleep(0.1)  # Small delay between down and up
            win32api.mouse_event(up_event, x, y, 0, 0)
            return True
        except Exception as e:
            print(f"Error performing click: {str(e)}")
            return False

    def type_text(self, element: Any, text: str, interval: float = 0.0) -> bool:
        """
        Type text into a UI element using UI Automation

        Args:
            element: UI Automation element to type into
            text: The text to type
            interval: The interval in seconds between each keystroke (only used if falling back to keyboard events)

        Returns:
            bool: True if the text was typed successfully, False otherwise
        """
        try:
            # First try using UI Automation Value pattern
            value_pattern = element.GetCurrentPattern(UIAClient.UIA_ValuePatternId)
            if value_pattern:
                value_pattern.SetValue(text)
                return True

            # Fall back to keyboard events if Value pattern is not supported
            for char in text:
                vk = win32api.VkKeyScan(char)
                if vk == -1:
                    continue
                    
                # Handle shift state
                if vk >> 8:  # If shift state is set
                    win32api.keybd_event(win32con.VK_SHIFT, 0, 0, 0)
                
                # Press and release the key
                win32api.keybd_event(vk & 0xFF, 0, 0, 0)
                win32api.keybd_event(vk & 0xFF, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                # Release shift if it was pressed
                if vk >> 8:
                    win32api.keybd_event(win32con.VK_SHIFT, 0, win32con.KEYEVENTF_KEYUP, 0)
                
                if interval > 0:
                    time.sleep(interval)
            return True
        except:  # Catch all exceptions to ensure we return False
            return False

    def get_screen_size(self) -> Tuple[int, int]:
        """
        Get screen dimensions

        Returns:
            tuple: A tuple containing the width and height of the screen in pixels.
        """
        try:
            width = win32api.GetSystemMetrics(win32con.SM_CXVIRTUALSCREEN)
            height = win32api.GetSystemMetrics(win32con.SM_CYVIRTUALSCREEN)
            return (width, height)
        except Exception as e:
            print(f"Error getting screen size: {str(e)}")
            return (0, 0)

    def take_screenshot(self, filepath: str) -> bool:
        """
        Take a screenshot and save to file

        Args:
            filepath (str): The path to save the screenshot to

        Returns:
            bool: True if the screenshot was taken and saved successfully, False otherwise
        """
        try:
            # Get screen dimensions
            width, height = self.get_screen_size()
            
            # Create device context and bitmap
            hdesktop = win32gui.GetDesktopWindow()
            desktop_dc = win32gui.GetWindowDC(hdesktop)
            img_dc = win32ui.CreateDCFromHandle(desktop_dc)
            mem_dc = img_dc.CreateCompatibleDC()
            
            # Create bitmap and select it into DC
            screenshot = win32ui.CreateBitmap()
            screenshot.CreateCompatibleBitmap(img_dc, width, height)
            mem_dc.SelectObject(screenshot)
            mem_dc.BitBlt((0, 0), (width, height), img_dc, (0, 0), win32con.SRCCOPY)
            
            # Convert to PIL Image and save
            bmpstr = screenshot.GetBitmapBits(True)
            im = Image.frombuffer('RGB', (width, height), bmpstr, 'raw', 'BGRX', 0, 1)
            
            im.save(filepath)
            
            # Cleanup
            mem_dc.DeleteDC()
            win32gui.DeleteObject(screenshot.GetHandle())
            
            return True
        except Exception as e:
            print(f"Error taking screenshot: {str(e)}")
            return False

    def capture_screenshot(self) -> Optional[np.ndarray]:
        """
        Capture screenshot as numpy array

        Returns:
            Screenshot as numpy array if successful, None otherwise
        """
        try:
            # Get screen dimensions
            width, height = self.get_screen_size()
            if width is None or height is None:
                print("Failed to get screen dimensions")
                return None
                
            # Create device context and bitmap
            hdesktop = win32gui.GetDesktopWindow()
            desktop_dc = win32gui.GetWindowDC(hdesktop)
            img_dc = win32ui.CreateDCFromHandle(desktop_dc)
            mem_dc = img_dc.CreateCompatibleDC()
            
            screenshot = win32ui.CreateBitmap()
            screenshot.CreateCompatibleBitmap(img_dc, width, height)
            mem_dc.SelectObject(screenshot)
            mem_dc.BitBlt((0, 0), (width, height), img_dc, (0, 0), win32con.SRCCOPY)
            
            # Convert to numpy array
            bmpstr = screenshot.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (height, width, 4)
            
            # Cleanup
            mem_dc.DeleteDC()
            win32gui.DeleteObject(screenshot.GetHandle())
            
            return img[..., :3]  # Remove alpha channel
        except Exception as e:
            print(f"Error capturing screenshot: {str(e)}")
            return None

    def find_window(self, title: str) -> Optional[Any]:
        """
        Find a window using its title.

        Args:
            title: The title of the window to search for. If an integer is passed, it will be converted to string.

        Returns:
            The window object if found, None otherwise.
        """
        try:
            if self.automation is None or self.root is None:
                print("UI Automation not properly initialized. Make sure the backend was initialized successfully.")
                return None

            # Convert title to string if it's not already
            title_str = str(title)
            condition = self.automation.CreatePropertyCondition(
                UIAClient.UIA_NamePropertyId, title_str
            )
            return self.root.FindFirst(
                UIAClient.TreeScope_Children | UIAClient.TreeScope_Descendants, condition
            )
        except Exception as e:
            print(f"Error finding window: {str(e)}")
            return None

    def get_window_title(self, window: Any) -> Optional[str]:
        """
        Retrieve the title of a given window.

        Args:
            window: The window object from which to retrieve the title.

        Returns:
            The title of the window as a string, or None if an error occurs.
        """
        try:
            return window.CurrentName
        except Exception as e:
            print(f"Error getting window title: {str(e)}")
            return None

    def wait_for_window(self, title: str, timeout: int = 30) -> Optional[Any]:
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
                print("UI Automation not properly initialized. Make sure the backend was initialized successfully.")
                return None

            start_time = time.time()
            while time.time() - start_time < timeout:
                window = self.find_window(title)
                if window:
                    return window
                time.sleep(0.5)
        except Exception as e:
            print(f"Error waiting for window: {str(e)}")
        return None

    def get_element_attributes(self, element: Any) -> dict:
        """
        Retrieve attributes from an element.

        Args:
            element: The element object from which to retrieve the attributes.

        Returns:
            A dictionary containing the element's attributes. If an error occurs, an empty dictionary is returned.

        Attributes retrieved:
            - name: The name of the element.
            - id: The automation ID of the element.
            - class_name: The class name of the element.
            - control_type: The type of control represented by the element.
            - is_enabled: Whether the element is currently enabled.
            - is_offscreen: Whether the element is currently off the screen.
            - bounding_rectangle: The bounding rectangle of the element.
        """
        try:
            return {
                'name': element.CurrentName,
                'id': element.CurrentAutomationId,
                'class_name': element.CurrentClassName,
                'control_type': element.CurrentControlType,
                'is_enabled': element.CurrentIsEnabled,
                'is_offscreen': element.CurrentIsOffscreen,
                'bounding_rectangle': element.CurrentBoundingRectangle
            }
        except Exception as e:
            print(f"Error getting element attributes: {str(e)}")
            return {}

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
                return False

            # Get the address of LoadLibrary function
            kernel32 = ctypes.WinDLL('kernel32', use_last_error=True)
            load_library = kernel32.LoadLibraryW
            if not load_library:
                return False

            load_library_ptr = ctypes.cast(load_library, ctypes.c_void_p)
            if not load_library_ptr:
                return False

            load_library_addr = load_library_ptr.value
            if not load_library_addr:
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
                return False

            # Write DLL path to remote process memory
            if not win32process.WriteProcessMemory(handle, path_address, dll_path.encode('utf-16le') + b'\x00\x00', 0):
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
                return False

            # Wait for thread completion and cleanup
            result = win32event.WaitForSingleObject(thread_handle, win32event.INFINITE)
            if result != win32event.WAIT_OBJECT_0:
                return False
                
            return True

        except Exception as e:
            return False
            
        finally:
            # Clean up handles in finally block to ensure they're always closed
            if thread_handle:
                try:
                    win32api.CloseHandle(thread_handle)
                except:
                    pass
            if handle:
                try:
                    win32api.CloseHandle(handle)
                except:
                    pass

    def maximize_window(self, window_handle: int) -> None:
        """
        Maximize a window
        
        Args:
            window_handle: Handle to the window
        """
        win32gui.ShowWindow(window_handle, win32con.SW_MAXIMIZE)

    def minimize_window(self, window_handle: int) -> None:
        """
        Minimize a window
        
        Args:
            window_handle: Handle to the window
        """
        win32gui.ShowWindow(window_handle, win32con.SW_MINIMIZE)

    def restore_window(self, window_handle: int) -> None:
        """
        Restore a window to its normal state
        
        Args:
            window_handle: Handle to the window
        """
        win32gui.ShowWindow(window_handle, win32con.SW_RESTORE)

    def capture_screen(self) -> np.ndarray:
        """
        Capture the entire screen
        
        Returns:
            Screenshot as numpy array
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
            return img
        finally:
            # Clean up
            if bmp:
                try:
                    handle = bmp.GetHandle()
                    if handle:
                        win32gui.DeleteObject(handle)
                except (AttributeError, win32gui.error):
                    pass

            if hdc_mem_copy:
                try:
                    hdc_mem_copy.DeleteDC()
                except win32gui.error:
                    pass

            if hdc_mem:
                try:
                    hdc_mem.DeleteDC()
                except win32gui.error:
                    pass

            if hdc:
                try:
                    win32gui.ReleaseDC(0, hdc)
                except win32gui.error:
                    pass

    def capture_window(self, window_handle: int) -> np.ndarray:
        """
        Capture a specific window
        
        Args:
            window_handle: Handle to the window to capture
            
        Returns:
            Window screenshot as numpy array
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
            return img
        finally:
            # Clean up
            if bmp:
                try:
                    handle = bmp.GetHandle()
                    if handle:
                        win32gui.DeleteObject(handle)
                except (AttributeError, win32gui.error):
                    pass

            if hdc_mem_copy:
                try:
                    hdc_mem_copy.DeleteDC()
                except win32gui.error:
                    pass

            if hdc_mem:
                try:
                    hdc_mem.DeleteDC()
                except win32gui.error:
                    pass

            if hdc:
                try:
                    win32gui.ReleaseDC(window_handle, hdc)
                except win32gui.error:
                    pass

    def capture_element_screenshot(self, element: Any) -> Optional[np.ndarray]:
        """Capture screenshot of a specific UI element

        Args:
            element: UI Automation element to capture

        Returns:
            numpy.ndarray: Screenshot of the element as a numpy array, or None if capture fails
        """
        try:
            # Get element's bounding rectangle
            rect = element.CurrentBoundingRectangle
            if not rect:
                return None

            # Convert rect from IUIAutomationElement format to tuple
            left, top, right, bottom = rect.left, rect.top, rect.right, rect.bottom
            width = right - left
            height = bottom - top

            if width <= 0 or height <= 0:
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

            # Copy the screen into our memory device context
            saveDC.BitBlt((0, 0), (width, height), mfcDC, (left, top), win32con.SRCCOPY)

            # Convert bitmap to numpy array
            bmpinfo = saveBitMap.GetInfo()
            bmpstr = saveBitMap.GetBitmapBits(True)
            img = np.frombuffer(bmpstr, dtype='uint8')
            img.shape = (height, width, 4)  # RGBA
            img = img[:, :, :3]  # Convert to RGB

            # Clean up
            win32gui.DeleteObject(saveBitMap.GetHandle())
            saveDC.DeleteDC()
            mfcDC.DeleteDC()
            win32gui.ReleaseDC(hwnd, hwndDC)

            return img

        except Exception as e:
            print(f"Error capturing element screenshot: {str(e)}")
            return None

    def _get_element_pattern(self, element: Any, pattern_id: int) -> Any:
        """
        Get a UI Automation pattern interface for an element
        
        Args:
            element: UI Automation element
            pattern_id: ID of the pattern to retrieve
            
        Returns:
            Pattern interface if supported, None otherwise
        """
        try:
            pattern = element.GetCurrentPattern(pattern_id)
            return pattern.QueryInterface(pattern_id) if pattern else None
        except:
            return None

    def click_element(self, element: Any) -> bool:
        """
        Click on a UI element
        
        Args:
            element: UI Automation element to click
            
        Returns:
            bool: True if the click was successful, False otherwise
        """
        try:
            # First try using UI Automation Invoke pattern
            invoke_pattern = element.GetCurrentPattern(UIAClient.UIA_InvokePatternId)
            if invoke_pattern:
                invoke_pattern.Invoke()
                return True
                
            # Fall back to mouse click if invoke pattern not supported
            rect = element.CurrentBoundingRectangle
            x = (rect[0] + rect[2]) // 2
            y = (rect[1] + rect[3]) // 2
            win32api.SetCursorPos((x, y))
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            return True
        except:  # Catch all exceptions to ensure we return False
            return False

    def get_element_property(self, element: Any, property_id: int) -> Optional[Any]:
        """
        Get a property value from a UI element

        Args:
            element: UI Automation element
            property_id: ID of the property to retrieve

        Returns:
            Property value if successful, None if there was an error
        """
        try:
            return element.GetCurrentPropertyValue(property_id)
        except:  # Catch all exceptions to ensure we return None
            return None

    def get_element_location(self, element: Any) -> Tuple[int, int]:
        """
        Get the screen coordinates of a UI element
        
        Args:
            element: UI Automation element
            
        Returns:
            Tuple of (x, y) coordinates
        """
        rect = element.CurrentBoundingRectangle
        return (rect[0], rect[1])

    def get_element_size(self, element: Any) -> Tuple[int, int]:
        """
        Get the size of a UI element
        
        Args:
            element: UI Automation element
            
        Returns:
            Tuple of (width, height)
        """
        rect = element.CurrentBoundingRectangle
        return (rect[2] - rect[0], rect[3] - rect[1])

    def is_element_enabled(self, element: Any) -> bool:
        """
        Check if a UI element is enabled
        
        Args:
            element: UI Automation element
            
        Returns:
            True if enabled, False otherwise
        """
        return element.CurrentIsEnabled

    def is_element_visible(self, element: Any) -> bool:
        """
        Check if a UI element is visible
        
        Args:
            element: UI Automation element
            
        Returns:
            True if visible, False otherwise
        """
        return not element.CurrentIsOffscreen

    def get_element_text(self, element: Any) -> str:
        """
        Get the text content of a UI element
        
        Args:
            element: UI Automation element
            
        Returns:
            Element text content
        """
        return element.CurrentName

    def type_text_into_element(self, element: Any, text: str) -> None:
        """
        Type text into a UI element
        
        Args:
            element: UI Automation element
            text: Text to type
        """
        pattern = self._get_element_pattern(element, UIAClient.UIA_ValuePatternId)
        if pattern:
            pattern.SetValue(text)
        else:
            # Fall back to keyboard input if value pattern not supported
            self.click_element(element)  # Focus the element
            for char in text:
                win32api.keybd_event(ord(char), 0, 0, 0)  # Key down
                win32api.keybd_event(ord(char), 0, win32con.KEYEVENTF_KEYUP, 0)  # Key up

    def cleanup(self) -> None:
        """
        Clean up resources used by the backend
        """
        # Release COM objects
        if hasattr(self, 'automation'):
            self.automation = None

    def set_ocr_languages(self, languages: List[str]) -> None:
        """
        Set OCR languages for text recognition.

        Args:
            languages: List of language codes (e.g., ['eng', 'fra'])
        """
        # Windows UI Automation does not directly handle OCR
        # This is handled by the OCREngine class
        pass

    def _create_condition(self, by: str, value: str) -> Optional[Any]:
        """
        Create a search condition for a UI element based on the specified strategy.

        Args:
            by (str): The strategy to find the element ('id', 'name', 'class', 'type').
            value (str): The value to search for using the specified strategy.

        Returns:
            Optional[Any]: A UI Automation property condition object if the strategy is valid,
                           otherwise None. Returns None if an exception is encountered.
        """
        try:
            if self.automation is None:
                print("UI Automation not properly initialized. Make sure the backend was initialized successfully.")
                return None

            if by == "id":
                return self.automation.CreatePropertyCondition(
                    UIAClient.UIA_AutomationIdPropertyId, value
                )
            elif by == "name":
                return self.automation.CreatePropertyCondition(
                    UIAClient.UIA_NamePropertyId, value
                )
            elif by == "class":
                return self.automation.CreatePropertyCondition(
                    UIAClient.UIA_ClassNamePropertyId, value
                )
            elif by == "type":
                return self.automation.CreatePropertyCondition(
                    UIAClient.UIA_ControlTypePropertyId, value
                )
            return None
        except Exception:
            return None

    def check_accessibility(self, element: Optional[Any] = None) -> Dict[str, Any]:
        """
        Check accessibility of an element or the entire UI using Windows UI Automation.

        Args:
            element: Optional element to check. If None, checks entire UI.

        Returns:
            Dictionary containing accessibility issues and their details
        """
        issues = {}
        try:
            if self.automation is None:
                return {"error": "UI Automation not initialized"}

            # Get the element to check
            target = element if element else self.root
            if not target:
                return {"error": "No target element available"}

            # Check name property
            try:
                name = target.CurrentName
                if not name or name.isspace():
                    issues["missing_name"] = "Element lacks a descriptive name"
            except:
                issues["name_error"] = "Could not retrieve element name"

            # Check if element is offscreen
            try:
                if target.CurrentIsOffscreen:
                    issues["visibility"] = "Element is not visible on screen"
            except:
                issues["visibility_error"] = "Could not check element visibility"

            # Check if element is enabled
            try:
                if not target.CurrentIsEnabled:
                    issues["disabled"] = "Element is disabled"
            except:
                issues["enabled_error"] = "Could not check if element is enabled"

            # Check keyboard focus
            try:
                if not target.CurrentIsKeyboardFocusable:
                    issues["keyboard_focus"] = "Element cannot receive keyboard focus"
            except:
                issues["focus_error"] = "Could not check keyboard focus capability"

            # Check control type
            try:
                control_type = target.CurrentControlType
                if control_type == 0:  # Invalid control type
                    issues["control_type"] = "Element has invalid control type"
            except:
                issues["control_type_error"] = "Could not check control type"

            # Check clickable point
            try:
                target.GetClickablePoint()
            except:
                issues["clickable_point"] = "Element has no clickable point"

            return issues
        except Exception as e:
            return {"error": f"Accessibility check failed: {str(e)}"}

    def move_mouse(self, x: int, y: int) -> None:
        """Move mouse cursor to absolute coordinates"""
        win32api.SetCursorPos((x, y))

    def click_mouse(self) -> bool:
        """Click at current mouse position"""
        try:
            x, y = win32api.GetCursorPos()
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
            win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
            return True
        except:
            return False

    def double_click_mouse(self) -> None:
        """Double click at current mouse position"""
        x, y = win32api.GetCursorPos()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def right_click_mouse(self) -> None:
        """Right click at current mouse position"""
        x, y = win32api.GetCursorPos()
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN, x, y, 0, 0)
        win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP, x, y, 0, 0)

    def mouse_down(self) -> None:
        """Press and hold primary mouse button"""
        x, y = win32api.GetCursorPos()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTDOWN, x, y, 0, 0)

    def mouse_up(self) -> None:
        """Release primary mouse button"""
        x, y = win32api.GetCursorPos()
        win32api.mouse_event(win32con.MOUSEEVENTF_LEFTUP, x, y, 0, 0)

    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse cursor position"""
        return win32api.GetCursorPos()
