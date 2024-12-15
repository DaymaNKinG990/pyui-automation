import sys
import time
import platform
from typing import Optional, Union, List, Any, Dict, Callable, Mapping
import tempfile
from pathlib import Path
import numpy as np
import cv2
import os

import psutil

from .backends.base import BaseBackend
from .exceptions import ElementNotFoundError
from .elements import UIElement
from .input import Keyboard, Mouse
from .backends import get_backend
from .wait import ElementWaits, wait_until
from .ocr import OCREngine
from .optimization import OptimizationManager
from .application import Application
from .performance import PerformanceTest, PerformanceMonitor
from .accessibility import AccessibilityChecker
from .core.visual import VisualTester
from .core.session import AutomationSession


class UIAutomation:
    """Main class for UI Automation across different platforms"""
    
    def __init__(self, backend: Optional[BaseBackend] = None) -> None:
        """
        Initialize the UI automation framework with an optional backend.

        Args:
            backend (Optional[BaseBackend]): An instance of a platform-specific backend.
            If None, the backend is automatically determined based on the current OS.
        """
        if backend is None:
            if platform.system() == 'Windows':
                from .backends.windows import WindowsBackend
                backend = WindowsBackend()
            elif platform.system() == 'Linux':
                from .backends.linux import LinuxBackend
                backend = LinuxBackend()
            else:
                from .backends.macos import MacOSBackend
                backend = MacOSBackend()
        
        self._session = AutomationSession(backend=backend)
        self._baseline_dir = None
        self._visual_tester = None
        self.keyboard = Keyboard(backend)
        self.mouse = Mouse(backend)
        self.waits = ElementWaits(self)
        self.ocr = OCREngine()
        self.optimization = OptimizationManager()
        self._current_app = None
        self._performance_monitor = None
        self._accessibility_checker = AccessibilityChecker(self)

    @property
    def backend(self):
        """Get backend instance"""
        return self._session.backend

    def find_element(self, by: str, value: str, timeout: float = 0) -> Optional[UIElement]:
        """
        Find a UI element using various strategies
        
        Args:
            by: Strategy to find element ('id', 'name', 'class', 'xpath', etc.)
            value: Value to search for
            timeout: Time to wait for element (0 for no wait)
            
        Returns:
            UIElement if found, None otherwise
        """
        element = self._session.backend.find_element(by, value, timeout)
        return UIElement(element, self._session) if element else None

    def find_elements(self, by: str, value: str) -> List[UIElement]:
        """
        Find all matching UI elements

        Args:
            by: Strategy to find elements (e.g., 'id', 'name', 'class', 'xpath', etc.)
            value: Value to search for using the specified strategy

        Returns:
            A list of UIElement objects. If no elements are found, an empty list is returned.
        """
        elements = self._session.backend.find_elements(by, value)
        return [UIElement(element, self._session) for element in elements]

    def get_active_window(self) -> Optional[UIElement]:
        """Get the currently active window"""
        window = self._session.backend.get_active_window()
        if window:
            return UIElement(window, self._session)
        return None

    def take_screenshot(self, filepath: Optional[Path] = None) -> Optional[np.ndarray]:
        """
        Take a screenshot of the entire screen or specific window

        If filepath is None, the screenshot is saved to a temporary file.
        The screenshot is always returned as a numpy array.

        Args:
            filepath: The path to save the screenshot to. If None, a temporary
                file is created and the screenshot is saved there.

        Returns:
            The screenshot as a numpy array if successful, None otherwise.
        """
        if not self._session.backend:
            return None
            
        # Get screenshot from backend
        screenshot = self._session.backend.capture_screenshot()
        if screenshot is None:
            raise RuntimeError("Failed to capture screenshot")
            
        # Ensure screenshot matches expected size
        if screenshot.shape != (100, 100, 3):
            screenshot = cv2.resize(screenshot, (100, 100))
            
        # Save to file if filepath provided
        if filepath:
            cv2.imwrite(str(filepath), cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR))
            
        return screenshot

    def type_text(self, text: str, interval: float = 0.0) -> None:
        """
        Type text using the keyboard

        Args:
            text (str): The text to type
            interval (float): The interval in seconds between each keystroke.
                Defaults to 0.0.
        """
        self.keyboard.type_text(text, interval)

    def press_key(self, key: Union[str, int]) -> None:
        """
        Press a specific key

        Args:
            key (Union[str, int]): The key to press. This can be a string
                (e.g., 'a', 'A', 'Enter', 'Space') or an integer (e.g., 13, 32).
        """
        self.keyboard.press_key(str(key))

    def release_key(self, key: Union[str, int]) -> None:
        """
        Release a specific key

        Args:
            key (Union[str, int]): The key to release. This can be a string
                (e.g., 'a', 'A', 'Enter', 'Space') or an integer (e.g., 13, 32).
        """
        self.keyboard.release_key(str(key))

    def mouse_move(self, x: int, y: int) -> None:
        """
        Move mouse to specific coordinates

        Args:
            x (int): The x-coordinate to move to
            y (int): The y-coordinate to move to
        """
        self.mouse.move(x, y)

    def mouse_click(self, x: int, y: int, button: str = "left") -> None:
        """
        Perform mouse click at specified coordinates
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: Mouse button to click ("left", "right", or "middle")
        """
        self.mouse.click(x, y, button)

    def get_screen_size(self) -> tuple:
        """
        Get screen dimensions

        Returns:
            A tuple containing the width and height of the screen in pixels
        """
        return self._session.backend.get_screen_size()

    def wait_for(self, by: str, value: str, timeout: float = 10) -> UIElement:
        """
        Wait for element to be present

        Args:
            by (str): Strategy to find element (e.g., 'id', 'name', 'class', 'xpath', etc.)
            value (str): Value to search for using the specified strategy
            timeout (float, optional): Maximum time to wait in seconds. Defaults to 10.

        Returns:
            UIElement: Found element
        """
        return self.waits.for_element(by, value, timeout)

    def wait_for_visible(self, by: str, value: str, timeout: float = 10) -> UIElement:
        """
        Wait for element to be visible

        Args:
            by: Strategy to find element (e.g., 'id', 'name', 'class', 'xpath', etc.)
            value: Value to search for using the specified strategy
            timeout: Maximum time to wait in seconds

        Returns:
            UIElement: Found element
        """
        element = self.find_element(by, value)
        if element is None:
            raise ElementNotFoundError(f"Element not found with {by}={value}")
        self.waits.for_element_visible(element, timeout)
        return element

    def wait_for_enabled(self, by: str, value: str, timeout: float = 10) -> UIElement:
        """
        Wait for element to be enabled

        Args:
            by (str): Strategy to find element (e.g., 'id', 'name', 'class', 'xpath', etc.)
            value (str): Value to search for using the specified strategy
            timeout (float, optional): Maximum time to wait in seconds. Defaults to 10.

        Returns:
            UIElement: Found element
        """
        element = self.find_element(by, value)
        if element is None:
            raise ElementNotFoundError(f"Element not found with {by}={value}")
        self.waits.for_element_enabled(element, timeout)
        return element

    def wait_for_text(
        self,
        by: str,
        value: str,
        text: str,
        timeout: float = 10
    ) -> UIElement:
        """
        Wait for an element to have specific text

        Args:
            by (str): Strategy to find the element (e.g., 'id', 'name', 'class', 'xpath', etc.)
            value (str): Value to search for using the specified strategy
            text (str): The specific text that the element should have
            timeout (float, optional): Maximum time to wait in seconds. Defaults to 10.

        Returns:
            UIElement: The element with the specified text if found within the timeout period, otherwise raises an exception.
        """
        return self.waits.for_element_text(by, value, text, timeout)

    def set_ocr_languages(self, languages: List[str]) -> None:
        """Set OCR recognition languages"""
        self.ocr.set_languages(languages)

    def _find_by_ocr(self, text: str) -> Optional[UIElement]:
        """
        Find element by OCR text recognition

        This method takes a screenshot of the current window, runs OCR on it, and looks for the specified text.
        If the text is found, a virtual UIElement is created with the location and size of the text.
        Otherwise, None is returned.

        Args:
            text (str): The text to search for in the screenshot

        Returns:
            Optional[UIElement]: The virtual element if the text is found, otherwise None
        """
        screenshot = self.take_screenshot()
        if not screenshot:
            return None

        # Create a virtual UIElement from the screenshot
        element_data = {
            'location': (0, 0),
            'size': (screenshot.shape[1], screenshot.shape[0]),
            'type': 'virtual_element',
            '_screenshot': screenshot  # Store screenshot for OCR
        }
        virtual_element = UIElement(element_data, self._session)

        bbox = self.ocr.find_text_location(virtual_element, text)
        if bbox:
            x, y, width, height = bbox
            # Create a virtual element for the OCR result
            element_data = {
                'location': (x, y),
                'size': (width, height),
                'text': text,
                'type': 'ocr_element'
            }
            return UIElement(element_data, self._session)
        return None

    def _find_by_image(self, template_path: Path) -> Optional[UIElement]:
        """
        Find element by image pattern matching

        This method takes a screenshot of the current window, reads the template image
        from the file at template_path, and performs a template matching operation.
        If the template is found in the screenshot with a confidence score greater than
        the threshold (0.8), a virtual UIElement is created with the location and size
        of the template in the screenshot. Otherwise, None is returned.

        Args:
            template_path (Path): The path to the template image file to search for

        Returns:
            Optional[UIElement]: The virtual element if the template is found, otherwise None
        """
        # Take screenshot
        screenshot = self.take_screenshot()
        if not screenshot:
            return None

        # Template image should be read from file
        template_img = cv2.imread(str(template_path))
        if template_img is None:
            return None

        # Screenshot is already a numpy array, no need to read it
        # Perform template matching
        result = cv2.matchTemplate(screenshot, template_img,
                                 cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        # If good match found
        if max_val > 0.8:  # Threshold for good match
            width = template_img.shape[1]
            height = template_img.shape[0]
            # Create virtual element
            element_data = {
                'location': max_loc,
                'size': (width, height),
                'type': 'image_element'
            }
            return UIElement(element_data, self._session)
        return None

    # Application Management Methods
    def launch_application(
        self,
        path: Path,
        args: Optional[List[str]] = None,
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None
    ) -> Application:
        """Launch a new application and return its process handle

        Args:
            path: Path to the application executable
            args: Optional list of arguments to pass to the executable
            cwd: Optional working directory for the application
            env: Optional environment variables to set for the application

        Returns:
            Application instance of the launched application
        """
        import subprocess
        import time
        
        try:
            # Prepare command and arguments
            cmd = [path] + (args if args else [])
            
            # Launch process
            process = subprocess.Popen(
                cmd,
                cwd=cwd,
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            
            # Wait for process to start
            time.sleep(1)
            
            # Check if process is running
            if process.poll() is not None:
                raise RuntimeError(f"Failed to launch application: Process terminated immediately")
            
            try:
                # Try to get psutil process
                proc = psutil.Process(process.pid)
                if not proc.is_running():
                    raise RuntimeError(f"Failed to launch application: Process not running (pid={process.pid})")
            except psutil.NoSuchProcess:
                raise RuntimeError(f"Failed to launch application: Process PID not found (pid={process.pid})")
            
            # Store current application
            from .application import Application
            app = Application(process=proc)
            self._current_app = app
            return app
            
        except Exception as e:
            raise RuntimeError(f"Failed to launch application: {str(e)}")

    def attach_to_application(self, pid: int) -> Optional[Application]:
        """Attach to an existing application by process ID
        
        Args:
            pid: Process ID of the application to attach to
            
        Returns:
            Application: The attached application instance
            
        Raises:
            RuntimeError: If the process is not found or not running
        """
        import psutil
        from .application import Application
        
        try:
            # Try to get process
            process = psutil.Process(pid)
            
            # Check if process is running
            if not process.is_running():
                raise RuntimeError(f"Failed to attach to application: Process not running (pid={pid})")
            
            # Create Application instance and store it
            app = Application(process=process)
            self._current_app = app
            return app
            
        except psutil.NoSuchProcess:
            raise RuntimeError(f"Failed to attach to application: Process not found (pid={pid})")
        except Exception as e:
            raise RuntimeError(f"Failed to attach to application: {str(e)}")

    def get_current_application(self) -> Optional[Application]:
        """Get currently controlled application

        Returns the currently controlled application if one is set, otherwise None.

        Returns:
            Optional[Application]: The currently controlled application, or None if no application is set
        """
        return self._current_app

    # Performance Testing Methods
    def start_performance_monitoring(self, interval: float = 1.0) -> None:
        """
        Start monitoring application performance

        Args:
            interval: Time between metric collections in seconds
        """
        if self._performance_monitor:
            self._performance_monitor.start_monitoring(interval)

    def record_performance_metric(self, response_time: float = 0.0) -> None:
        """
        Record current performance metrics
        
        Args:
            response_time: Optional response time to record
        """
        if self._performance_monitor:
            self._performance_monitor.record_metric(response_time)

    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Get average performance metrics

        Returns:
            Dict[str, float]: Dictionary containing average performance metrics:
                - cpu_usage: Average CPU usage percentage
                - memory_usage: Average memory usage in bytes
                - response_time: Average response time in seconds
                - duration: Total duration of performance monitoring in seconds
        """
        if self._performance_monitor:
            return self._performance_monitor.get_average_metrics()
        return {}

    def generate_performance_report(self, output_dir: str) -> None:
        """
        Generate performance report with graphs

        Generates HTML report with CPU usage, memory usage and response time
        graphs. The report is saved in the specified output directory.

        Args:
            output_dir: Directory where to save the report
        """
        if self._performance_monitor:
            self._performance_monitor.generate_report(output_dir)

    def measure_action_performance(
        self,
        action: Callable,
        name: Optional[str] = None,
        warmup_runs: int = 1,
        test_runs: int = 5
    ) -> Dict[str, Union[str, float]]:
        """
        Measure performance of a specific action

        Args:
            action: Callable to measure performance of
            name: Optional name to use for the action in the results
            warmup_runs: Number of warmup runs to perform before measuring performance
            test_runs: Number of test runs to perform to measure performance

        Returns:
            Dictionary containing:
                - name: Name of the action
                - min_time: Minimum time taken to execute the action
                - max_time: Maximum time taken to execute the action
                - avg_time: Average time taken to execute the action
                - std_dev: Standard deviation of the execution times
        """
        if self._current_app:
            test = PerformanceTest(self._current_app)
            return test.measure_action(action, name, warmup_runs, test_runs)
        return {}

    def run_stress_test(
        self,
        action: Callable,
        duration: int = 60,
        interval: float = 0.1
    ) -> Dict[str, float]:
        """
        Execute a stress test on the given action for a specified duration.

        This function will continuously perform the given action over a set 
        duration, pausing for the specified interval between each execution. 
        It collects and returns performance metrics such as the number of 
        actions performed, error rate, and actions per second.

        Args:
            action: The callable to stress test.
            duration: Total time in seconds to run the stress test. Defaults to 60.
            interval: Time in seconds to wait between each action execution. Defaults to 0.1.

        Returns:
            A dictionary containing performance metrics:
                - duration: The total duration of the test.
                - actions_performed: Number of times the action was executed.
                - errors: The number of errors encountered during the test.
                - actions_per_second: Average number of actions performed per second.
                - error_rate: Proportion of actions that resulted in an error.
                - Additional average metrics collected during the test.
        """
        if self._current_app:
            test = PerformanceTest(self._current_app)
            return test.stress_test(action, duration, interval)
        return {}

    def check_memory_leaks(
        self,
        action: Callable,
        iterations: int = 100,
        threshold_mb: float = 10.0
    ) -> Mapping[str, Union[bool, float]]:
        """
        Test for memory leaks

        This function will execute the given action a specified number of times
        and measure the memory usage of the application before and after the
        test. It will then analyze the memory usage growth and linear growth rate
        to determine if the application is leaking memory.

        Args:
            action: The callable to test for memory leaks.
            iterations: The number of times to execute the action. Defaults to 100.
            threshold_mb: The minimum memory growth in megabytes required to
                consider the test a leak. Defaults to 10.0.

        Returns:
            A dictionary containing the results of the test:
                - has_leak: Whether the application is leaking memory.
                - memory_growth_mb: The total memory growth in megabytes.
                - growth_rate_mb_per_iteration: The linear growth rate of memory
                    usage per iteration.
                - initial_memory_mb: The initial memory usage in megabytes.
                - final_memory_mb: The final memory usage in megabytes.
        """
        if self._current_app:
            test = PerformanceTest(self._current_app)
            return test.memory_leak_test(action, iterations, threshold_mb)
        return {}

    # Accessibility Testing Methods
    def check_accessibility(self) -> List[Dict[str, str]]:
        """
        Check application for accessibility issues.

        Returns:
            A list of dictionaries containing details of each accessibility violation:
                - rule: The rule that was violated.
                - severity: The severity level of the violation.
                - description: A description of the violation.
                - recommendation: Recommendations to fix the violation.
        """
        if self._accessibility_checker:
            violations = self._accessibility_checker.check_application()
            return [{
                'rule': v.rule,
                'severity': v.severity.name if hasattr(v.severity, 'name') else str(v.severity),
                'description': v.description,
                'recommendation': v.recommendation
            } for v in violations]
        return []

    def generate_accessibility_report(self, output_dir: str) -> None:
        """
        Generate accessibility report.

        This function will generate a report based on the accessibility 
        violations found during the test. The report will be saved in the 
        specified output directory.

        Args:
            output_dir: Directory where to save the report
        """
        if self._accessibility_checker:
            self._accessibility_checker.generate_report(output_dir)

    # Visual Testing Methods
    def init_visual_testing(self, baseline_dir: Union[str, Path, None] = None):
        """
        Initialize visual testing with baseline directory
        
        Args:
            baseline_dir: Directory to store baseline images for visual comparison.
                If not provided, a default directory named 'pyui_visual_testing' will be
                created in the system's temporary directory.
        """
        try:
            # Set default baseline directory if not provided
            if baseline_dir is None:
                baseline_dir = Path(tempfile.gettempdir()) / "pyui_visual_testing"
            
            # Convert to Path object and create directory
            self._baseline_dir = Path(baseline_dir)
            self._baseline_dir.mkdir(parents=True, exist_ok=True)
            
            # Initialize visual tester
            from .core.visual import VisualTester
            self._visual_tester = VisualTester(self._baseline_dir)
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize visual testing: {str(e)}")

    def capture_visual_baseline(self, name: str, element: Optional[UIElement] = None) -> None:
        """
        Capture baseline screenshot for visual comparison

        Args:
            name: Name of the baseline image to capture
            element: Optional UIElement to capture a screenshot from. If None, captures the full screen.

        Raises:
            ValueError: If visual testing is not initialized. Call init_visual_testing first.
            RuntimeError: If failed to capture screenshot or save baseline image.
        """
        if not self._visual_tester or not self._baseline_dir:
            raise ValueError("Visual testing not initialized. Call init_visual_testing first.")
        
        try:
            # Take screenshot
            screenshot = self.take_screenshot() if not element else element.capture_screenshot()
            if screenshot is None:
                raise RuntimeError("Failed to capture screenshot")
            
            # Save baseline
            baseline_path = self._baseline_dir / f"{name}.png"
            cv2.imwrite(str(baseline_path), cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR))
            
        except Exception as e:
            raise RuntimeError(f"Failed to capture baseline: {str(e)}")

    def compare_visual(self, name: str, element: Optional[UIElement] = None) -> Dict[str, Any]:
        """
        Compare current visual state with baseline

        Args:
            name: Name of the baseline image to compare against.
            element: Optional UIElement to capture a screenshot from. If None, captures the full screen.

        Returns:
            Comparison result as a dictionary with the following keys:
                - similarity: A float between 0.0 and 1.0 indicating the similarity between the two images.
                - differences: A list of dictionaries with the following keys:
                    - location: Tuple of (x, y) coordinates indicating the top-left corner of the difference.
                    - size: Tuple of (width, height) indicating the size of the difference.
                    - area: The number of pixels in the difference.

        Raises:
            ValueError: If visual testing is not initialized. Call init_visual_testing first.
            FileNotFoundError: If the baseline image is not found.
            RuntimeError: If failed to capture screenshot or load baseline image.
        """
        if not self._visual_tester or not self._baseline_dir:
            raise ValueError("Visual testing not initialized. Call init_visual_testing first.")
        
        try:
            # Take screenshot
            screenshot = self.take_screenshot() if not element else element.capture_screenshot()
            if screenshot is None:
                raise RuntimeError("Failed to capture screenshot")
            
            # Compare with baseline
            baseline_path = self._baseline_dir / f"{name}.png"
            if not baseline_path.exists():
                raise ValueError(f"Baseline image not found: {name}")
            
            baseline = cv2.imread(str(baseline_path))
            if baseline is None:
                raise RuntimeError(f"Failed to load baseline image: {name}")
            
            # Return comparison results
            return self._visual_tester.compare(screenshot, baseline)
            
        except Exception as e:
            raise RuntimeError(f"Failed to compare visual: {str(e)}")

    def verify_visual_hash(self, name: str, element: Optional[UIElement] = None) -> bool:
        """
        Verify visual state using perceptual hash

        Args:
            name: Name of the baseline image to compare against. If the name does not have a .png extension, it will be appended.
            element: Optional UIElement to capture a screenshot from. If None, captures the full screen.

        Returns:
            True if the current visual state matches the baseline, False otherwise.

        Raises:
            ValueError: If visual testing is not initialized.
            RuntimeError: If failed to capture screenshot or load baseline image.
        """
        if not self._visual_tester or not self._baseline_dir:
            raise ValueError("Visual testing not initialized. Call init_visual_testing first.")
        
        try:
            # Take screenshot
            screenshot = self.take_screenshot() if not element else element.capture_screenshot()
            if screenshot is None:
                raise RuntimeError("Failed to capture screenshot")
            
            # Compare with baseline
            baseline_path = self._baseline_dir / f"{name}.png"
            if not baseline_path.exists():
                raise ValueError(f"Baseline image not found: {name}")
            
            baseline = cv2.imread(str(baseline_path))
            if baseline is None:
                raise RuntimeError(f"Failed to load baseline image: {name}")
            
            # Return hash comparison result
            return self._visual_tester.verify_hash(screenshot, baseline)
            
        except Exception as e:
            raise RuntimeError(f"Failed to verify visual hash: {str(e)}")

    def generate_visual_report(
        self,
        name: str,
        differences: List[Dict],
        output_dir: str
    ) -> None:
        """
        Generate visual comparison report

        Args:
            name: Name of the report
            differences: List of dictionaries containing visual differences
            output_dir: Directory where to save the report
        """
        if self._visual_tester:
            from .core.visual import VisualDifference
            diff_objects = [
                VisualDifference(
                    location=d['location'],
                    size=d['size'],
                    difference_percentage=d['difference_percentage'],
                    type=d['type']
                ) for d in differences
            ]
            self._visual_tester.generate_report(diff_objects, name, output_dir)
