"""
PyUI Automation - High-level interface for QA Automation engineers

This module provides a simplified interface that hides the complexity of the underlying
framework and provides easy-to-use methods for common automation tasks.
"""

import os
import time
import sys
from typing import Optional, List, Any, Dict, Tuple
from contextlib import contextmanager
from pathlib import Path

from .core import AutomationSession
from .core.services.backend_factory import BackendFactory
from .locators import ByName, ByClassName
from .core.exceptions import ElementNotFoundError, TimeoutError


class PyUIAutomation:
    """
    High-level automation interface for PyUI Automation.
    
    Provides simple methods for common automation tasks without requiring
    knowledge of the underlying framework architecture.
    """
    
    def __init__(self, app_path: Optional[str] = None, window_title: Optional[str] = None, platform: str = 'auto'):
        """
        Initialize PyUIAutomation with optional application launch.
        
        Args:
            app_path: Path to the application executable
            window_title: Title of the main window to wait for
            platform: Platform to use ('windows', 'linux', 'macos', 'auto')
        """
        # Auto-detect platform and create backend
        factory = BackendFactory()
        self.backend = factory.create_backend(platform)
        
        # Create platform-specific locator
        from pyui_automation.locators.windows import WindowsLocator
        from pyui_automation.locators.linux import LinuxLocator
        from pyui_automation.locators.macos import MacOSLocator
        
        # Initialize locator as Any to avoid type conflicts
        self.locator: Any
        
        if platform == 'windows' or (platform == 'auto' and sys.platform == 'win32'):
            self.locator = WindowsLocator(self.backend)
        elif platform == 'linux' or (platform == 'auto' and sys.platform == 'linux'):
            self.locator = LinuxLocator(self.backend)
        elif platform == 'macos' or (platform == 'auto' and sys.platform == 'darwin'):
            self.locator = MacOSLocator(self.backend)
        else:
            # Default to Windows locator
            self.locator = WindowsLocator(self.backend)
        
        self.session = AutomationSession(self.backend, self.locator)
        
        # Application state
        self.app: Optional[Any] = None
        self.window: Optional[Any] = None
        self.window_title = window_title
        
        # Initialize visual testing if baseline directory exists
        self._init_visual_testing()
        
        # Launch application if path provided
        if app_path:
            self.launch(app_path, window_title)
    
    def _init_visual_testing(self) -> None:
        """Initialize visual testing if baseline directory exists."""
        baseline_dir = "visual_baseline"
        if os.path.exists(baseline_dir):
            try:
                self.session.init_visual_testing(baseline_dir)
            except Exception:
                pass  # Visual testing not critical
    
    def launch(self, app_path: str, window_title: Optional[str] = None) -> 'PyUIAutomation':
        """
        Launch an application and wait for its window.
        If the application is already running, it will attach to the existing process.
        
        Args:
            app_path: Path to the application executable
            window_title: Title of the main window to wait for
            
        Returns:
            Self for method chaining
        """
        from pyui_automation.core.application import Application
        
        # Use the new smart launch logic that checks for existing processes
        self.app = Application.launch(Path(app_path)) if app_path else None
        self.window_title = window_title or self.window_title
        
        if self.window_title:
            if self.app is not None:
                self.window = self.app.wait_for_window(self.window_title)
            else:
                self.window = None
        
        return self
    
    # Basic element interactions
    def click(self, element_name: str, timeout: float = 10.0) -> 'PyUIAutomation':
        """Click on an element by name."""
        element = self._find_element(element_name, timeout)
        if element is not None:
            element.click()
        return self
    
    def double_click(self, element_name: str, timeout: float = 10.0) -> 'PyUIAutomation':
        """Double click on an element by name."""
        element = self._find_element(element_name, timeout)
        if element is not None:
            element.double_click()
        return self
    
    def right_click(self, element_name: str, timeout: float = 10.0) -> 'PyUIAutomation':
        """Right click on an element by name."""
        element = self._find_element(element_name, timeout)
        if element is not None:
            element.right_click()
        return self
    
    def type_text(self, element_name: str, text: str, timeout: float = 10.0) -> 'PyUIAutomation':
        """Type text into an element."""
        element = self._find_element(element_name, timeout)
        if element is not None:
            element.clear()
            element.send_keys(text)
        return self
    
    def get_text(self, element_name: str, timeout: float = 10.0) -> str:
        """Get text from an element."""
        element = self._find_element(element_name, timeout)
        if element is None:
            return ""
        return element.text if hasattr(element, 'text') else ""
    
    def is_visible(self, element_name: str, timeout: float = 5.0) -> bool:
        """Check if an element is visible."""
        try:
            element = self._find_element(element_name, timeout)
            if element is None:
                return False
            return element.visible if hasattr(element, 'visible') else False
        except (ElementNotFoundError, TimeoutError):
            return False
    
    def is_enabled(self, element_name: str, timeout: float = 5.0) -> bool:
        """Check if an element is enabled."""
        try:
            element = self._find_element(element_name, timeout)
            if element is None:
                return False
            return element.is_enabled() if hasattr(element, 'is_enabled') else False
        except (ElementNotFoundError, TimeoutError):
            return False
    
    def wait_for_element(self, element_name: str, timeout: float = 10.0) -> Any:
        """Wait for an element to appear."""
        return self._find_element(element_name, timeout)
    
    def wait_for_text(self, element_name: str, expected_text: str, timeout: float = 10.0) -> 'PyUIAutomation':
        """Wait for an element to contain specific text."""
        start_time = time.time()
        while time.time() - start_time < timeout:
            try:
                actual_text = self.get_text(element_name, timeout=1.0)
                if expected_text in actual_text:
                    return self
            except Exception:
                pass
            time.sleep(0.5)
        
        raise TimeoutError(f"Element '{element_name}' did not contain text '{expected_text}' within {timeout}s")
    
    def find_elements_by_class(self, class_name: str) -> List[Any]:
        """Find all elements by class name."""
        return self.session.find_elements(ByClassName(class_name))
    
    def find_element_by_text(self, text: str, timeout: float = 10.0) -> Any:
        """Find an element by its text content."""
        return self._find_element(text, timeout)
    
    # Visual testing methods
    def capture_screenshot(self, name: str) -> 'PyUIAutomation':
        """Capture a screenshot and save it with the given name."""
        screenshot = self.session.backend.capture_screenshot()
        filename = f"{name}_{int(time.time())}.png"
        if screenshot is not None:
            self.session.utils.save_image(screenshot, filename)
        print(f"Screenshot saved: {filename}")
        return self
    
    def capture_baseline(self, name: str) -> 'PyUIAutomation':
        """Capture a baseline image for visual testing."""
        try:
            self.session.capture_visual_baseline(name)
            print(f"Baseline captured: {name}")
        except Exception as e:
            print(f"Warning: Could not capture baseline '{name}': {e}")
        return self
    
    def assert_visual_match(self, baseline_name: str, threshold: float = 0.95) -> 'PyUIAutomation':
        """Assert that current screen matches baseline."""
        try:
            result = self.session.compare_visual(baseline_name)
            if isinstance(result, (tuple, list)) and len(result) >= 2:
                match, similarity = result
            elif hasattr(result, 'get'):
                match = result.get("match", False)
                similarity = result.get("similarity", 0.0)
            else:
                match = False
                similarity = 0.0
            
            if not match or similarity < threshold:
                # Capture current screenshot for comparison
                self.capture_screenshot(f"failed_{baseline_name}")
                raise AssertionError(
                    f"Visual test failed for '{baseline_name}'. "
                    f"Similarity: {similarity:.3f}, "
                    f"Threshold: {threshold}"
                )
            else:
                print(f"Visual test passed: {baseline_name}")
        except Exception as e:
            if "baseline not found" in str(e).lower():
                print(f"Creating new baseline: {baseline_name}")
                self.capture_baseline(baseline_name)
            else:
                raise
        return self
    
    # OCR methods
    def get_ocr_text(self, element_name: str, timeout: float = 10.0) -> str:
        """Get text from an element using OCR."""
        element = self._find_element(element_name, timeout)
        if element is None or self.session.ocr is None:
            return ""
        if hasattr(self.session.ocr, 'read_text'):
            result = self.session.ocr.read_text(element, "")
            return str(result)
        return ""
    
    def ocr_recognize_text(self, image_path: str) -> str:
        """Recognize text from image file."""
        if self.session.ocr is None:
            return ""
        if hasattr(self.session.ocr, 'recognize_text'):
            result = self.session.ocr.recognize_text(image_path)
            return str(result)
        return ""
    
    def ocr_set_languages(self, languages: List[str]) -> 'PyUIAutomation':
        """Set languages for OCR recognition."""
        if self.session.ocr is not None and hasattr(self.session.ocr, 'set_languages'):
            self.session.ocr.set_languages(languages)
        return self
    
    # Performance monitoring methods
    def start_performance_monitoring(self, interval: float = 1.0) -> 'PyUIAutomation':
        """Start performance monitoring."""
        self.session.start_performance_monitoring(interval)
        return self
    
    def stop_performance_monitoring(self) -> Dict[str, Any]:
        """Stop performance monitoring and return results."""
        return self.session.stop_performance_monitoring()
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics."""
        return self.session.get_performance_metrics()
    
    def measure_action_performance(self, action: Any, runs: int = 3) -> Dict[str, Any]:
        """Measure performance of an action."""
        return self.session.measure_action_performance(action, runs)
    
    def run_stress_test(self, action: Any, duration: float) -> Dict[str, Any]:
        """Run stress test for specified duration."""
        return self.session.run_stress_test(action, duration)
    
    def check_memory_leaks(self, action: Optional[Any] = None, iterations: int = 100) -> Dict[str, Any]:
        """Check for memory leaks."""
        return self.session.check_memory_leaks(action, iterations)
    
    # Accessibility methods
    def check_accessibility(self) -> List[Dict[str, Any]]:
        """Check for accessibility violations."""
        # TODO: Implement accessibility checking
        return []
    
    def generate_accessibility_report(self, output_path: str) -> 'PyUIAutomation':
        """Generate accessibility report."""
        # TODO: Implement accessibility report generation
        return self
    
    # Keyboard and mouse methods
    def keyboard_type(self, text: str, interval: float = 0.1) -> 'PyUIAutomation':
        """Type text using keyboard."""
        self.session.keyboard.type_text(text, interval)
        return self
    
    def keyboard_press_key(self, key: str) -> 'PyUIAutomation':
        """Press a key."""
        self.session.keyboard.press_key(key)
        return self
    
    def keyboard_release_key(self, key: str) -> 'PyUIAutomation':
        """Release a key."""
        self.session.keyboard.release_key(key)
        return self
    
    def keyboard_send_keys(self, *keys: str) -> 'PyUIAutomation':
        """Send multiple keys."""
        self.session.keyboard.send_keys(*keys)
        return self
    
    def mouse_move(self, x: int, y: int) -> 'PyUIAutomation':
        """Move mouse to coordinates."""
        self.session.mouse.move(x, y)
        return self
    
    def mouse_click(self, x: int, y: int, button: str = 'left') -> 'PyUIAutomation':
        """Click at coordinates."""
        self.session.mouse.click(x, y, button)
        return self
    
    def mouse_double_click(self, x: int, y: int, button: str = 'left') -> 'PyUIAutomation':
        """Double click at coordinates."""
        self.session.mouse.double_click(x, y, button)
        return self
    
    def mouse_right_click(self, x: int, y: int) -> 'PyUIAutomation':
        """Right click at coordinates."""
        self.session.mouse.right_click(x, y)
        return self
    
    def mouse_drag(self, start_x: int, start_y: int, end_x: int, end_y: int, button: str = 'left') -> 'PyUIAutomation':
        """Drag from start to end coordinates."""
        self.session.mouse.drag(start_x, start_y, end_x, end_y, button)
        return self
    
    def get_mouse_position(self) -> Tuple[int, int]:
        """Get current mouse position."""
        position = self.session.mouse.get_position()
        if isinstance(position, tuple) and len(position) == 2:
            return (int(position[0]), int(position[1]))
        return (0, 0)
    
    # Utility methods
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions."""
        return self.session.get_screen_size()
    
    def get_window_handle(self, window_title: str) -> int:
        """Get window handle by title."""
        # TODO: Implement window handle retrieval
        return 0
    
    def focus_window(self, window_title: str) -> 'PyUIAutomation':
        """Focus window by title."""
        # TODO: Implement window focus
        return self
    
    def minimize_window(self, window_title: str) -> 'PyUIAutomation':
        """Minimize window by title."""
        self.session.backend.minimize_window(window_title)
        return self
    
    def maximize_window(self, window_title: str) -> 'PyUIAutomation':
        """Maximize window by title."""
        self.session.backend.maximize_window(window_title)
        return self
    
    def close_window(self, window_title: str) -> 'PyUIAutomation':
        """Close window by title."""
        self.session.backend.close_window(window_title)
        return self
    
    # Internal methods
    def _find_element(self, element_name: str, timeout: float = 10.0) -> Any:
        """Internal method to find element with fallback strategies."""
        try:
            return self.session.find_element_by_object_name(element_name)
        except ElementNotFoundError:
            # Try alternative strategies
            try:
                return self.session.find_element(ByClassName(element_name))
            except ElementNotFoundError:
                try:
                    return self.session.find_element(ByName(element_name))
                except ElementNotFoundError:
                    raise ElementNotFoundError(f"Element '{element_name}' not found with any strategy")
    
    def close(self) -> None:
        """Close the application."""
        if self.app:
            self.app.terminate()
    
    def __enter__(self) -> 'PyUIAutomation':
        return self
    
    def __exit__(self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]) -> None:
        self.close()


class TestHelper:
    """
    Helper class for common test operations.
    """
    
    def __init__(self, app: PyUIAutomation):
        self.app = app
        self.step_count = 0
    
    def log_step(self, step_name: str) -> 'TestHelper':
        """Log a test step with screenshot."""
        self.step_count += 1
        self.app.capture_screenshot(f"step_{self.step_count}_{step_name}")
        print(f"Step {self.step_count}: {step_name}")
        return self
    
    def assert_text_equals(self, element_name: str, expected_text: str) -> 'TestHelper':
        """Assert that element text equals expected text."""
        actual_text = self.app.get_text(element_name)
        assert actual_text == expected_text, f"Expected '{expected_text}', got '{actual_text}'"
        return self
    
    def assert_text_contains(self, element_name: str, expected_text: str) -> 'TestHelper':
        """Assert that element text contains expected text."""
        actual_text = self.app.get_text(element_name)
        assert expected_text in actual_text, f"Text '{expected_text}' not found in '{actual_text}'"
        return self
    
    def assert_visible(self, element_name: str) -> 'TestHelper':
        """Assert that element is visible."""
        assert self.app.is_visible(element_name), f"Element '{element_name}' is not visible"
        return self
    
    def assert_enabled(self, element_name: str) -> 'TestHelper':
        """Assert that element is enabled."""
        assert self.app.is_enabled(element_name), f"Element '{element_name}' is not enabled"
        return self
    
    def wait_and_assert(self, element_name: str, expected_text: str, timeout: float = 10.0) -> 'TestHelper':
        """Wait for element and assert its text."""
        self.app.wait_for_text(element_name, expected_text, timeout)
        self.assert_text_contains(element_name, expected_text)
        return self


# Convenience functions for quick access
def launch_app(app_path: str, window_title: Optional[str] = None, platform: str = 'auto') -> PyUIAutomation:
    """Quick function to launch an application."""
    return PyUIAutomation(app_path, window_title, platform)


@contextmanager
def app_session(app_path: str, window_title: Optional[str] = None, platform: str = 'auto') -> Any:
    """
    Context manager for application sessions.
    
    Usage:
        with app_session("notepad++.exe", "Notepad++") as app:
            app.click("someButton")
    """
    app = PyUIAutomation(app_path, window_title, platform)
    try:
        yield app
    finally:
        app.close() 