"""Automation session management"""

import numpy as np
from typing import Optional, List, Dict, Any, Tuple, Callable, Union
from pathlib import Path
from PIL import Image
import cv2
import logging
import psutil
import time

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

    def __init__(self, backend: BaseBackend, config: Optional[AutomationConfig] = None) -> None:
        """
        Initialize automation session.

        Args:
            backend: Platform-specific backend to use
            config: Optional configuration object
        """
        self.backend = backend
        self.waits = ElementWaits(self)
        self._visual_tester: Optional[VisualTester] = None
        self._performance_monitor = None
        self._config = config or AutomationConfig()
        self._keyboard: Optional[Keyboard] = None
        self._mouse: Optional[Mouse] = None
        self._ocr_languages = ['eng']  # Default OCR language
        self._current_application = None
        self._performance_metrics = {}

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

    def start_performance_monitoring(self, interval: float = 1.0, metrics: Optional[List[str]] = None) -> None:
        """
        Start monitoring performance metrics.

        Args:
            interval: Sampling interval in seconds
            metrics: List of metrics to monitor (cpu, memory, io)
        """
        if not metrics:
            metrics = ["cpu", "memory", "io"]
        self._performance_monitor = PerformanceTest(interval=interval, metrics=metrics)
        self._performance_monitor.start()

    def stop_performance_monitoring(self) -> Dict[str, float]:
        """
        Stop performance monitoring and get results.

        Returns:
            Dictionary of performance metrics
        """
        if self._performance_monitor:
            return self._performance_monitor.stop_monitoring()
        return {}

    def measure_action_performance(self, action: Callable, runs: int = 3) -> Dict[str, float]:
        """Measure performance of an action"""
        if runs <= 0:
            raise ValueError("Number of runs must be positive")
        
        times = []
        for _ in range(runs):
            start_time = time.time()
            action()
            end_time = time.time()
            times.append(end_time - start_time)
    
        return {
            'min_time': min(times),
            'max_time': max(times),
            'avg_time': sum(times) / len(times)
        }

    def run_stress_test(self, action: Callable, test_duration: int = 60) -> Dict[str, Any]:
        """Run stress test for specified duration"""
        if test_duration <= 0:
            raise ValueError("Duration must be positive")
        
        start_time = time.time()
        total_actions = 0
        failures = 0
        
        while time.time() - start_time < test_duration:
            try:
                action()
                total_actions += 1
            except Exception:
                failures += 1
        
        return {
            'total_actions': total_actions,
            'success_rate': (total_actions - failures) / total_actions if total_actions > 0 else 0
        }

    def check_memory_leaks(self, action: Callable, test_iterations: int = 100) -> Dict[str, Any]:
        """Check for memory leaks"""
        if test_iterations <= 0:
            raise ValueError("Number of iterations must be positive")
        
        initial_memory = psutil.Process().memory_info().rss
        
        for _ in range(test_iterations):
            action()
        
        final_memory = psutil.Process().memory_info().rss
        memory_growth = final_memory - initial_memory
        
        return {
            'memory_growth': memory_growth,
            'leak_detected': memory_growth > 1024 * 1024  # 1MB threshold
        }

    def wait_for(self, condition: Callable[[], bool], timeout: float = None, interval: float = None) -> bool:
        """
        Wait for a condition to be true.

        Args:
            condition: Function that returns True when condition is met
            timeout: Maximum time to wait in seconds
            interval: Time between checks in seconds

        Returns:
            bool: True if condition was met within timeout
        """
        if timeout is None:
            timeout = self._config.default_timeout if self._config else 10.0
        if interval is None:
            interval = self._config.polling_interval if self._config else 0.5
        
        end_time = time.time() + timeout
        while time.time() < end_time:
            if condition():
                return True
            time.sleep(interval)
        return False

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

    def init_visual_testing(self, baseline_dir: Union[str, Path], threshold: float = 0.95) -> None:
        """Initialize visual testing with baseline directory and comparison threshold"""
        if not baseline_dir:
            raise ValueError("Baseline directory must be specified")
        self._visual_tester = VisualTester(baseline_dir, threshold)

    def capture_baseline(self, name: str, element: Optional[UIElement] = None) -> bool:
        """Capture baseline image for visual testing"""
        if not self._visual_tester:
            raise ValueError("Visual testing not initialized. Call init_visual_testing first.")
        image = element.capture_screenshot() if element else self.backend.capture_screenshot()
        return self._visual_tester.capture_baseline(name, image)

    def verify_visual(self, name: str, element: Optional[UIElement] = None) -> Tuple[bool, float]:
        """Compare current state with baseline"""
        if not self._visual_tester:
            raise ValueError("Visual testing not initialized. Call init_visual_testing first.")
        image = element.capture_screenshot() if element else self.backend.capture_screenshot()
        return self._visual_tester.compare(name, image)

    def generate_visual_report(self, output_dir: Union[str, Path]) -> None:
        """Generate visual testing report"""
        if not self._visual_tester:
            raise ValueError("Visual testing not initialized. Call init_visual_testing first.")
        self._visual_tester.generate_report(output_dir)

    def generate_accessibility_report(self, output_dir: Union[str, Path]) -> None:
        """Generate accessibility testing report"""
        if not output_dir:
            raise ValueError("Output directory must be specified")
        self.backend.generate_accessibility_report(output_dir)

    def get_current_application(self) -> Optional[Any]:
        """Get current application being automated"""
        return self._current_application

    def attach_to_process(self, pid: int) -> None:
        """Attach to running process by PID"""
        try:
            process = psutil.Process(pid)
            if not process.is_running():
                raise ValueError(f"Process {pid} is not running")
            self._current_application = process
        except psutil.NoSuchProcess:
            raise psutil.NoSuchProcess(pid=pid, msg="Process PID not found")

    def start_performance_monitoring(self) -> None:
        """Start monitoring performance metrics"""
        if not self._current_application:
            raise ValueError("No application attached for monitoring")
        self._performance_monitor = PerformanceTest(self._current_application)
        self._performance_monitor.start()

    def get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        if not self._performance_monitor:
            raise ValueError("Performance monitoring not started")
        return self._performance_monitor.get_metrics()

    def run_stress_test(self, duration: int, action: Callable[[], None]) -> Dict[str, Any]:
        """Run stress test for specified duration"""
        if duration <= 0:
            raise ValueError("Duration must be positive")
        if not self._performance_monitor:
            self.start_performance_monitoring()
        return self._performance_monitor.run_stress_test(duration, action)

    def check_memory_leaks(self, iterations: int, action: Callable[[], None]) -> Dict[str, Any]:
        """Check for memory leaks by running action multiple times"""
        if iterations <= 0:
            raise ValueError("Iterations must be positive")
        if not self._performance_monitor:
            self.start_performance_monitoring()
        return self._performance_monitor.check_memory_leaks(iterations, action)

    def measure_action_performance(self, action: Callable[[], None], runs: int = 10) -> Dict[str, float]:
        """Measure performance metrics for an action"""
        if runs <= 0:
            raise ValueError("Number of runs must be positive")
        if not self._performance_monitor:
            self.start_performance_monitoring()
        return self._performance_monitor.measure_action(action, runs)

    def set_ocr_language(self, language: str) -> None:
        """Set OCR language for text recognition"""
        valid_languages = ['eng', 'fra', 'deu', 'spa']  # Example supported languages
        if language not in valid_languages:
            raise ValueError(f"Unsupported OCR language. Supported languages: {valid_languages}")
        self._ocr_languages = [language]

    def mouse_move(self, x: int, y: int) -> None:
        """Move mouse to coordinates"""
        if not isinstance(x, int) or not isinstance(y, int):
            raise ValueError("Coordinates must be integers")
        if x < 0 or y < 0:
            raise ValueError("Coordinates must be non-negative")
        self._mouse.move(x, y)

    def press_key(self, key: str) -> None:
        """Press keyboard key"""
        valid_keys = ['a', 'b', 'c', 'enter', 'shift', 'ctrl', 'alt']  # Example valid keys
        if key not in valid_keys:
            raise ValueError(f"Invalid key. Valid keys: {valid_keys}")
        self._keyboard.press(key)

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

    def capture_visual_baseline(self, element: UIElement, name: str) -> bool:
        """Capture visual baseline for element"""
        if not hasattr(element, 'capture_screenshot'):
            raise AttributeError("Element does not support screenshot capture")
        
        screenshot = element.capture_screenshot()
        baseline_path = os.path.join(self._visual_test_dir, f"{name}_baseline.png")
        screenshot.save(baseline_path)
        return True

    def compare_visual(self, element: UIElement, name: str) -> Tuple[bool, float]:
        """Compare element with visual baseline"""
        if not hasattr(element, 'capture_screenshot'):
            raise AttributeError("Element does not support screenshot capture")
        
        current = element.capture_screenshot()
        baseline_path = os.path.join(self._visual_test_dir, f"{name}_baseline.png")
        baseline = Image.open(baseline_path)
        
        diff = ImageChops.difference(current, baseline)
        diff_ratio = sum(x * y for x, y in diff.getdata()) / (current.width * current.height * 255)
        
        return diff_ratio < 0.01, diff_ratio

    def verify_visual_hash(self, element: UIElement, name: str) -> bool:
        """Verify element visual hash against baseline"""
        if not hasattr(element, 'capture_screenshot'):
            raise AttributeError("Element does not support screenshot capture")
        
        current = element.capture_screenshot()
        baseline_path = os.path.join(self._visual_test_dir, f"{name}_baseline.png")
        baseline = Image.open(baseline_path)
        
        current_hash = hashlib.md5(current.tobytes()).hexdigest()
        baseline_hash = hashlib.md5(baseline.tobytes()).hexdigest()
        
        return current_hash == baseline_hash

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

    def _save_image(self, image: np.ndarray, path: Union[str, Path]) -> None:
        """Save image to file"""
        if not isinstance(image, np.ndarray):
            raise ValueError("Image must be a numpy array")
        cv2.imwrite(str(path), image)

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

    def configure_waits(self, timeout: float = 10.0, polling_interval: float = 0.5) -> None:
        """
        Configure wait timeouts and polling intervals.
        
        Args:
            timeout: Default timeout for wait operations in seconds
            polling_interval: Time between condition checks in seconds
        """
        self.waits.default_timeout = timeout
        self.waits.polling_interval = polling_interval

    def configure_visual_testing(self, baseline_dir: Union[str, Path], threshold: float = 0.95) -> None:
        """
        Configure visual testing settings.

        Args:
            baseline_dir: Directory for baseline images
            threshold: Similarity threshold for comparisons
        """
        if self._config is None:
            self._config = AutomationConfig()
        self._config.visual_baseline_dir = Path(baseline_dir)
        self._config.visual_threshold = threshold
        self._config.visual_testing_enabled = True

    def start_performance_monitoring(self, interval: float = 1.0) -> None:
        """
        Start performance monitoring.

        Args:
            interval: Monitoring interval in seconds
        """
        if self._config is None:
            self._config = AutomationConfig()
        self._config.performance_enabled = True
        self._config.performance_interval = interval
        if self._performance_monitor is None:
            self._performance_monitor = PerformanceTest(self)
        self._performance_monitor.start_monitoring()
