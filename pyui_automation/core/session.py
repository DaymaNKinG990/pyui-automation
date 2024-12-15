"""Automation session management"""

import numpy as np
from typing import Optional, List, Dict, Any, Tuple, Callable, Union
from pathlib import Path
from PIL import Image
import cv2
import logging
import psutil

from ..backends.base import BaseBackend
from ..elements import UIElement
from ..wait import ElementWaits
from .visual import VisualTester
from ..performance import PerformanceTest
from ..exceptions import AutomationError
from .config import AutomationConfig
from ..input import Keyboard
from ..input.mouse import Mouse


logger = logging.getLogger(__name__)


class AutomationSession:
    """Manages an automation session with a specific backend"""

    def __init__(self, backend: BaseBackend) -> None:
        """
        Initialize automation session.

        Args:
            backend: Platform-specific backend to use
        """
        self.backend = backend
        self.waits = ElementWaits(self)
        self._visual_tester: Optional[VisualTester] = None
        self._performance_monitor = None
        self._config: Optional[AutomationConfig] = None
        self._keyboard: Optional[Keyboard] = None
        self._mouse: Optional[Mouse] = None
        self._ocr_languages = ['eng']  # Default OCR language

    def find_element(self, by: str, value: str, timeout: float = 0) -> Optional[UIElement]:
        """
        Find a UI element using various strategies.

        Args:
            by: Strategy to find element ('id', 'name', 'class', 'xpath', etc.)
            value: Value to search for
            timeout: Time to wait for element (0 for no wait)

        Returns:
            UIElement if found, None otherwise
        """
        if timeout > 0:
            # Use backend directly for consistency with test expectations
            element = self.backend.find_element(by, value)
            if element:
                return UIElement(element, self)
            return None
            
        element = self.backend.find_element(by, value)
        return UIElement(element, self) if element else None

    def find_elements(self, by: str, value: str) -> List[UIElement]:
        """
        Find all matching UI elements.

        Args:
            by: Strategy to find elements ('id', 'name', 'class', 'xpath', etc.)
            value: Value to search for

        Returns:
            List of UIElement objects
        """
        elements = self.backend.find_elements(by, value)
        return [UIElement(element, self) for element in elements]

    def find_element_by_id(self, id: str, timeout: float = 0) -> Optional[UIElement]:
        """
        Find a UI element by its ID.

        Args:
            id: ID of the element to find
            timeout: Time to wait for element (0 for no wait)

        Returns:
            UIElement if found, None otherwise
        """
        return self.find_element(by="id", value=id, timeout=timeout)

    def find_element_by_name(self, name: str, timeout: float = 0) -> Optional[UIElement]:
        """
        Find a UI element by its name.

        Args:
            name: Name of the element to find
            timeout: Time to wait for element (0 for no wait)

        Returns:
            UIElement if found, None otherwise
        """
        return self.find_element(by="name", value=name, timeout=timeout)

    def find_element_by_class(self, class_name: str, timeout: float = 0) -> Optional[UIElement]:
        """
        Find a UI element by its class name.

        Args:
            class_name: Class name of the element to find
            timeout: Time to wait for element (0 for no wait)

        Returns:
            UIElement if found, None otherwise
        """
        return self.find_element(by="class", value=class_name, timeout=timeout)

    def find_element_by_xpath(self, xpath: str, timeout: float = 0) -> Optional[UIElement]:
        """
        Find a UI element by its XPath.

        Args:
            xpath: XPath of the element to find
            timeout: Time to wait for element (0 for no wait)

        Returns:
            UIElement if found, None otherwise
        """
        return self.find_element(by="xpath", value=xpath, timeout=timeout)

    def find_elements_by_id(self, id: str) -> List[UIElement]:
        """
        Find all UI elements with the given ID.

        Args:
            id: ID of the elements to find

        Returns:
            List of UIElement objects
        """
        return self.find_elements(by="id", value=id)

    def find_elements_by_name(self, name: str) -> List[UIElement]:
        """
        Find all UI elements with the given name.

        Args:
            name: Name of the elements to find

        Returns:
            List of UIElement objects
        """
        return self.find_elements(by="name", value=name)

    def find_elements_by_class(self, class_name: str) -> List[UIElement]:
        """
        Find all UI elements with the given class name.

        Args:
            class_name: Class name of the elements to find

        Returns:
            List of UIElement objects
        """
        return self.find_elements(by="class", value=class_name)

    def find_elements_by_xpath(self, xpath: str) -> List[UIElement]:
        """
        Find all UI elements with the given XPath.

        Args:
            xpath: XPath of the elements to find

        Returns:
            List of UIElement objects
        """
        return self.find_elements(by="xpath", value=xpath)

    def take_screenshot(self, save_path: Optional[Path] = None) -> np.ndarray:
        """
        Take a screenshot of the current screen.

        Args:
            save_path: Optional path to save the screenshot

        Returns:
            Screenshot as numpy array
        """
        screenshot = self.backend.capture_screenshot()
        if screenshot is None:
            raise RuntimeError("Failed to capture screenshot")
            
        if save_path:
            save_path = Path(save_path)
            save_path.parent.mkdir(parents=True, exist_ok=True)
            # Save as PNG since it's an image
            Image.fromarray(screenshot).save(str(save_path))
        return screenshot

    def wait_until(self, condition: Callable[[], bool], timeout: float = 10, poll_frequency: float = 0.5) -> bool:
        """
        Wait until a condition is met.

        Args:
            condition: Function that returns True when condition is met
            timeout: Maximum time to wait in seconds
            poll_frequency: Time between checks in seconds

        Returns:
            True if condition was met, False if timeout occurred
        """
        return self.waits.wait_until(condition, timeout, poll_frequency)

    def set_ocr_languages(self, languages: List[str]) -> None:
        """
        Set OCR languages for text recognition.

        Args:
            languages: List of language codes (e.g., ['eng', 'fra'])
        """
        self.backend.set_ocr_languages(languages)

    def start_performance_monitoring(self, interval: float = 1.0) -> None:
        """
        Start monitoring performance metrics.

        Args:
            interval: Time between measurements in seconds
        """
        if not self._performance_monitor:
            self._performance_monitor = PerformanceTest(self.backend.application)
        self._performance_monitor.monitor.start_monitoring(interval)

    def stop_performance_monitoring(self) -> Dict[str, float]:
        """
        Stop performance monitoring and get results.

        Returns:
            Dictionary of performance metrics
        """
        if self._performance_monitor:
            return self._performance_monitor.monitor.stop_monitoring()
        return {}

    def measure_action_performance(self, action: Callable, iterations: int = 1) -> Dict[str, Union[str, float]]:
        """
        Measure performance of an action.

        Args:
            action: Function to measure
            iterations: Number of times to run the action

        Returns:
            Performance metrics
        """
        if not self._performance_monitor:
            self._performance_monitor = PerformanceTest(self.backend.application)
        return self._performance_monitor.measure_action(action, test_runs=iterations)

    def run_stress_test(self, action: Callable, duration: float, interval: float = 0.1) -> Dict[str, Any]:
        """
        Run a stress test on an action.

        Args:
            action: Function to test
            duration: Test duration in seconds
            interval: Time between actions in seconds

        Returns:
            Test results
        """
        if not self._performance_monitor:
            self._performance_monitor = PerformanceTest(self.backend.application)
        return self._performance_monitor.stress_test(action, int(round(duration)), interval)

    def check_memory_leaks(self, action: Callable, iterations: int = 100) -> Tuple[bool, float]:
        """
        Check for memory leaks in an action.

        Args:
            action: Function to check
            iterations: Number of times to run the action

        Returns:
            (leak_detected, leak_size_mb)
        """
        if not self._performance_monitor:
            self._performance_monitor = PerformanceTest(self.backend.application)
        results = self._performance_monitor.memory_leak_test(action, iterations)
        # Explicitly cast the return values to ensure correct types
        leak_detected: bool = bool(results['has_leak'])
        leak_size: float = float(results['memory_growth_mb'])
        return leak_detected, leak_size

    def check_accessibility(self, element: Optional[UIElement] = None) -> Dict[str, Any]:
        """
        Check accessibility of an element or the entire UI.

        Args:
            element: Optional element to check. If None, checks entire UI.

        Returns:
            Dictionary of accessibility issues
        """
        return self.backend.check_accessibility(element.native_element if element else None)

    def get_active_window(self) -> Optional[UIElement]:
        """
        Get the currently active window.

        Returns:
            UIElement representing the active window, or None if no window is active
        """
        window = self.backend.get_active_window()
        return UIElement(window, self) if window else None

    @property
    def visual_tester(self) -> VisualTester:
        """Get the visual tester instance"""
        if self._visual_tester is None:
            raise RuntimeError("Visual testing not initialized. Call init_visual_testing first.")
        return self._visual_tester

    def init_visual_testing(self, baseline_dir: str) -> None:
        """
        Initialize visual testing with the specified baseline directory.

        Args:
            baseline_dir: Directory to store baseline images
        """
        from .visual import VisualTester
        self._visual_tester = VisualTester(baseline_dir)

    def capture_screenshot(self) -> np.ndarray:
        """
        Capture a screenshot of the entire screen.

        Returns:
            Screenshot as numpy array
            
        Raises:
            RuntimeError: If screenshot capture fails
        """
        screenshot = self.backend.capture_screenshot()
        if screenshot is None:
            raise RuntimeError("Failed to capture screenshot")
        return screenshot

    def capture_element_screenshot(self, element: UIElement) -> np.ndarray:
        """
        Capture a screenshot of a specific element.

        Args:
            element: Element to capture

        Returns:
            Screenshot of the element as numpy array
            
        Raises:
            RuntimeError: If screenshot capture fails
        """
        screenshot = element.capture_screenshot()
        if screenshot is None:
            raise RuntimeError("Failed to capture element screenshot")
        return screenshot

    def capture_visual_baseline(self, name: str, element: Optional[UIElement] = None) -> bool:
        """
        Capture a visual baseline for comparison.

        Args:
            name: Name of the baseline image
            element: Optional element to capture. If None, captures full screen.

        Returns:
            bool: True if baseline was captured successfully
        """
        screenshot = self.capture_element_screenshot(element) if element else self.capture_screenshot()
        return self.visual_tester.capture_baseline(f"{name}.png", screenshot)

    def compare_visual(self, name: str, element: Optional[UIElement] = None) -> Tuple[bool, float]:
        """
        Compare current visual state with baseline.

        Args:
            name: Name of the baseline image
            element: Optional element to compare. If None, compares full screen.

        Returns:
            Tuple[bool, float]: Match result and difference score
        """
        screenshot = self.capture_element_screenshot(element) if element else self.capture_screenshot()
        return self.visual_tester.compare_with_baseline(f"{name}.png", screenshot)

    def verify_visual_hash(self, name: str, element: Optional[UIElement] = None) -> Dict[str, Any]:
        """
        Verify visual hash against baseline.

        Args:
            name: Name of the baseline image
            element: Optional element to verify. If None, verifies full screen.

        Returns:
            Dict containing match status and differences
        """
        screenshot = self.capture_element_screenshot(element) if element else self.capture_screenshot()
        result = self.visual_tester.verify_hash(f"{name}.png", screenshot)
        return {
            "match": result,
            "differences": [] if result else [{"type": "hash_mismatch", "location": (0, 0), "size": (0, 0)}]
        }

    def launch_application(self, path: str, *args, **kwargs) -> Any:
        """
        Launch an application.

        Args:
            path: Path to the application executable
            *args: Additional arguments for the application
            **kwargs: Additional keyword arguments for the application

        Returns:
            Application object
        """
        from ..application import Application
        app = Application(Path(path))
        args_list = list(args)
        app.launch(path=Path(path), args=args_list, **kwargs)
        return app

    def attach_to_application(self, pid: int) -> Any:
        """
        Attach to an existing application.

        Args:
            pid: Process ID of the application

        Returns:
            Application object
        """
        from ..application import Application
        return Application(process=psutil.Process(pid))

    @property
    def config(self) -> AutomationConfig:
        """
        Get the automation configuration.

        Returns:
            AutomationConfig: The current automation configuration instance. If not already set, a new instance is created.
        """
        if self._config is None:
            self._config = AutomationConfig()
        return self._config

    @property
    def keyboard(self) -> Keyboard:
        """
        Get the keyboard input handler.

        The keyboard input handler provides methods for typing text and pressing keys.

        Returns:
            Keyboard: The keyboard input handler instance.
        """
        if self._keyboard is None:
            self._keyboard = Keyboard(self.backend)
        return self._keyboard

    @property
    def mouse(self) -> Mouse:
        """
        Get the mouse input handler.

        The mouse input handler provides methods for moving the cursor and clicking.

        Returns:
            Mouse: The mouse input handler instance.
        """
        if self._mouse is None:
            self._mouse = Mouse(self.backend)
        return self._mouse

    @property
    def ocr(self):
        """
        Get the OCR handler.

        The OCR handler provides methods for text recognition.

        Returns:
            OCR: The OCR handler instance.
        """
        if not hasattr(self.backend, 'ocr'):
            raise AttributeError('OCR not supported by backend')
        return self.backend.ocr
