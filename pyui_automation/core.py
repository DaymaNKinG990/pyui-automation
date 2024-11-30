import sys
import platform
from typing import Optional, Union, List, Any, Dict, Callable
import tempfile
from pathlib import Path

from .elements import UIElement
from .input import Keyboard, Mouse
from .backends import get_backend
from .wait import ElementWaits, wait_until
from .ocr import OCREngine
from .optimization import OptimizationManager
from .application import Application
from .performance import PerformanceTest, PerformanceMonitor
from .accessibility import AccessibilityChecker
from .visual import VisualTester

class UIAutomation:
    """Main class for UI Automation across different platforms"""
    
    def __init__(self):
        self.platform = platform.system().lower()
        self.backend = get_backend()
        self.keyboard = Keyboard()
        self.mouse = Mouse()
        self.waits = ElementWaits(self)
        self.ocr = OCREngine()
        self.optimization = OptimizationManager()
        self._current_app = None
        self._performance_monitor = None
        self._accessibility_checker = None
        self._visual_tester = None

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
        if timeout > 0:
            try:
                return self.waits.for_element(by, value, timeout)
            except Exception:
                return None

        # Check cache first
        cache_key = f"{by}:{value}"
        cached_element = self.optimization.get_cached_element(cache_key)
        if cached_element:
            return UIElement(cached_element, self)

        # Handle OCR and image-based search
        if by == "ocr_text":
            return self._find_by_ocr(value)
        elif by == "image":
            return self._find_by_image(value)

        # Use backend search
        element = self.backend.find_element(by, value)
        if element:
            # Cache the result
            if self.optimization.get_optimization('cache_enabled'):
                self.optimization.cache_element(cache_key, element)
            return UIElement(element, self)
        return None

    def find_elements(self, by: str, value: str) -> List[UIElement]:
        """Find all matching UI elements"""
        elements = self.backend.find_elements(by, value)
        return [UIElement(element, self) for element in elements]

    def get_active_window(self) -> Optional[UIElement]:
        """Get the currently active window"""
        window = self.backend.get_active_window()
        if window:
            return UIElement(window, self)
        return None

    def take_screenshot(self, filepath: str = None) -> Optional[str]:
        """
        Take a screenshot of the entire screen or specific window
        If filepath is None, saves to temporary file
        """
        if filepath is None:
            filepath = str(Path(tempfile.gettempdir()) / f"screenshot_{id(self)}.png")
        
        if self.backend.take_screenshot(filepath):
            return filepath
        return None

    def type_text(self, text: str, interval: float = 0.0):
        """Type text using the keyboard"""
        self.keyboard.type_text(text, interval)

    def press_key(self, key: Union[str, int]):
        """Press a specific key"""
        self.keyboard.press_key(key)

    def release_key(self, key: Union[str, int]):
        """Release a specific key"""
        self.keyboard.release_key(key)

    def mouse_move(self, x: int, y: int):
        """Move mouse to specific coordinates"""
        self.mouse.move(x, y)

    def mouse_click(self, button: str = "left"):
        """Perform mouse click"""
        self.mouse.click(button)

    def get_screen_size(self) -> tuple:
        """Get screen dimensions"""
        return self.backend.get_screen_size()

    def wait_for(self, by: str, value: str, timeout: float = 10) -> UIElement:
        """Wait for element to be present"""
        return self.waits.for_element(by, value, timeout)

    def wait_for_visible(self, by: str, value: str, timeout: float = 10) -> UIElement:
        """Wait for element to be visible"""
        return self.waits.for_element_visible(by, value, timeout)

    def wait_for_enabled(self, by: str, value: str, timeout: float = 10) -> UIElement:
        """Wait for element to be enabled"""
        return self.waits.for_element_enabled(by, value, timeout)

    def wait_for_text(self, by: str, value: str, text: str,
                     timeout: float = 10) -> UIElement:
        """Wait for element to have specific text"""
        return self.waits.for_element_text(by, value, text, timeout)

    def set_ocr_languages(self, languages: List[str]):
        """Set OCR recognition languages"""
        self.ocr.set_languages(languages)

    def _find_by_ocr(self, text: str) -> Optional[UIElement]:
        """Find element by OCR text recognition"""
        screenshot = self.take_screenshot()
        if not screenshot:
            return None

        bbox = self.ocr.find_text_location(screenshot, text)
        if bbox:
            x, y, width, height = bbox
            # Create a virtual element for the OCR result
            element_data = {
                'location': (x, y),
                'size': (width, height),
                'text': text,
                'type': 'ocr_element'
            }
            return UIElement(element_data, self)
        return None

    def _find_by_image(self, template_path: str) -> Optional[UIElement]:
        """Find element by image pattern matching"""
        import cv2
        import numpy as np

        # Take screenshot
        screenshot = self.take_screenshot()
        if not screenshot:
            return None

        # Read images
        screenshot_img = cv2.imread(screenshot)
        template_img = cv2.imread(template_path)
        
        # Perform template matching
        result = cv2.matchTemplate(screenshot_img, template_img,
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
            return UIElement(element_data, self)
        return None

    # Application Management Methods
    def launch_application(self, path: str, args: List[str] = None,
                         cwd: str = None, env: Dict[str, str] = None) -> Application:
        """Launch a new application"""
        self._current_app = Application.launch(path, args, cwd, env)
        self._performance_monitor = PerformanceMonitor(self._current_app)
        self._accessibility_checker = AccessibilityChecker(self)
        return self._current_app

    def attach_to_application(self, process_name: str) -> Optional[Application]:
        """Attach to an existing application"""
        self._current_app = Application.attach(process_name)
        if self._current_app:
            self._performance_monitor = PerformanceMonitor(self._current_app)
            self._accessibility_checker = AccessibilityChecker(self)
        return self._current_app

    def get_current_application(self) -> Optional[Application]:
        """Get currently controlled application"""
        return self._current_app

    # Performance Testing Methods
    def start_performance_monitoring(self, interval: float = 1.0):
        """Start monitoring application performance"""
        if self._performance_monitor:
            self._performance_monitor.start_monitoring(interval)

    def record_performance_metric(self, response_time: float = 0.0):
        """Record current performance metrics"""
        if self._performance_monitor:
            self._performance_monitor.record_metric(response_time)

    def get_performance_metrics(self) -> Dict[str, float]:
        """Get average performance metrics"""
        if self._performance_monitor:
            return self._performance_monitor.get_average_metrics()
        return {}

    def generate_performance_report(self, output_dir: str):
        """Generate performance report with graphs"""
        if self._performance_monitor:
            self._performance_monitor.generate_report(output_dir)

    def measure_action_performance(self, action: Callable, name: str = None,
                                 warmup_runs: int = 1,
                                 test_runs: int = 5) -> Dict[str, float]:
        """Measure performance of a specific action"""
        if self._current_app:
            test = PerformanceTest(self._current_app)
            return test.measure_action(action, name, warmup_runs, test_runs)
        return {}

    def run_stress_test(self, action: Callable, duration: int = 60,
                       interval: float = 0.1) -> Dict[str, float]:
        """Run stress test for specified duration"""
        if self._current_app:
            test = PerformanceTest(self._current_app)
            return test.stress_test(action, duration, interval)
        return {}

    def check_memory_leaks(self, action: Callable, iterations: int = 100,
                          threshold_mb: float = 10.0) -> Dict[str, bool]:
        """Test for memory leaks"""
        if self._current_app:
            test = PerformanceTest(self._current_app)
            return test.memory_leak_test(action, iterations, threshold_mb)
        return {}

    # Accessibility Testing Methods
    def check_accessibility(self) -> List[Dict[str, str]]:
        """Check application for accessibility issues"""
        if self._accessibility_checker:
            violations = self._accessibility_checker.check_application()
            return [{
                'rule': v.rule,
                'severity': v.severity,
                'description': v.description,
                'recommendation': v.recommendation
            } for v in violations]
        return []

    def generate_accessibility_report(self, output_dir: str):
        """Generate accessibility report"""
        if self._accessibility_checker:
            self._accessibility_checker.generate_report(output_dir)

    # Visual Testing Methods
    def init_visual_testing(self, baseline_dir: str):
        """Initialize visual testing with baseline directory"""
        self._visual_tester = VisualTester(self)
        self._visual_tester.set_baseline_directory(baseline_dir)

    def capture_visual_baseline(self, name: str, element=None):
        """Capture baseline screenshot for visual comparison"""
        if self._visual_tester:
            self._visual_tester.capture_baseline(name, element)

    def compare_visual(self, name: str, element=None) -> Optional[List[Dict]]:
        """Compare current visual state with baseline"""
        if self._visual_tester:
            differences = self._visual_tester.compare_with_baseline(name, element)
            if differences:
                return [{
                    'location': diff.location,
                    'size': diff.size,
                    'difference_percentage': diff.difference_percentage,
                    'type': diff.type
                } for diff in differences]
        return None

    def verify_visual_hash(self, name: str, element=None) -> Dict[str, float]:
        """Compare images using perceptual hashing"""
        if self._visual_tester:
            return self._visual_tester.verify_visual_hash(name, element)
        return {'similarity': 0.0, 'match': False}

    def generate_visual_report(self, name: str, differences: List[Dict],
                             output_dir: str):
        """Generate visual comparison report"""
        if self._visual_tester:
            from .visual import VisualDifference
            diff_objects = [
                VisualDifference(
                    location=d['location'],
                    size=d['size'],
                    difference_percentage=d['difference_percentage'],
                    type=d['type']
                ) for d in differences
            ]
            self._visual_tester.generate_visual_report(diff_objects, name, output_dir)
