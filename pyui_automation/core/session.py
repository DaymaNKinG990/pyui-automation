"""
Refactored AutomationSession - follows SOLID principles.

This is a refactored version of AutomationSession that uses specialized services
to handle different responsibilities, following the Single Responsibility Principle.
"""
# Python imports
import time
import logging
from typing import Optional, List, Any, Dict, Union, Callable, Tuple, Type
from pathlib import Path
import numpy as np
import cv2 # Added for SessionUtils

# Local imports
from ..backends.base_backend import BaseBackend
from ..elements.base_element import BaseElement
from .wait import ElementWaits
from .config import AutomationConfig
from ..locators.base import LocatorStrategy
from .services.element_discovery_service import ElementDiscoveryService
from .services.screenshot_service import ScreenshotService
from .services.performance_monitor import PerformanceMonitor
from .services.performance_analyzer import PerformanceAnalyzer
from .services.performance_tester import PerformanceTester
from .services.memory_leak_detector import MemoryLeakDetector
from .services.visual_testing_service import VisualTestingService
from .services.input_service import InputService
from ..utils import (
    load_image, save_image, resize_image, compare_images,
    find_template, highlight_region, crop_image, preprocess_image,
    create_mask, enhance_image, ensure_dir, get_temp_dir, safe_remove,
    validate_type, validate_not_none, validate_string_not_empty, validate_number_range,
    retry, get_temp_path, MetricsCollector, MetricPoint
)


logger = logging.getLogger(__name__)


class AutomationSession:
    """
    Automation session that follows SOLID principles.
    
    Responsibilities:
    - Session management and coordination
    - Delegating element discovery to ElementDiscoveryService
    - Delegating screenshots to ScreenshotService
    - Delegating performance monitoring to PerformanceService
    - Delegating visual testing to VisualTestingService
    - Delegating input operations to InputService
    """
    
    def __init__(self, backend: BaseBackend, locator, session_id: Optional[str] = None, config: Optional[AutomationConfig] = None) -> None:
        """
        Initialize refactored automation session.

        Args:
            backend: Platform-specific backend to use
            locator: Platform-specific locator to use
            session_id: Optional session identifier
            config: Optional automation configuration
        """
        self.backend = backend
        self.locator = locator
        self.session_id = session_id or f"session_{id(self)}"
        self.waits = ElementWaits(self)
        self._config = config or AutomationConfig()
        self._ocr_languages = ['eng']  # Default OCR language
        self._current_application = None
        
        # Initialize services
        self._element_discovery_service = ElementDiscoveryService(backend, locator, self)
        self._screenshot_service = ScreenshotService(backend, self)
        self._performance_monitor = PerformanceMonitor(None)  # Pass None instead of backend
        self._performance_analyzer = PerformanceAnalyzer()
        self._performance_tester = PerformanceTester()
        self._memory_leak_detector = MemoryLeakDetector(None)  # Pass None instead of backend
        self._visual_testing_service = VisualTestingService(self)
        self._input_service = InputService(self)
        
        # Initialize utils
        self._utils = SessionUtils()
        self.is_closed = False
    
    @property
    def config(self) -> AutomationConfig:
        """Get configuration"""
        return self._config
    
    @property
    def logger(self):
        """Get logger"""
        return logger
    
    @property
    def utils(self):
        """Get utils for common operations"""
        return self._utils
    
    # Element discovery - delegated to ElementDiscoveryService
    def find_element(self, strategy: LocatorStrategy) -> Optional[BaseElement]:
        """Find element using locator strategy"""
        return self._element_discovery_service.find_element(strategy)
    
    def find_elements(self, strategy: LocatorStrategy) -> List[BaseElement]:
        """Find elements using locator strategy"""
        return self._element_discovery_service.find_elements(strategy)
    
    def find_element_with_timeout(self, strategy: LocatorStrategy, timeout: float = 10.0) -> Optional[BaseElement]:
        """Find element with timeout"""
        return self._element_discovery_service.find_element_with_timeout(strategy, timeout)
    
    def find_element_by_object_name(self, object_name: str, timeout: float = 0) -> Optional[BaseElement]:
        """Find element by object name"""
        return self._element_discovery_service.find_element_by_object_name(object_name, timeout)
    
    def find_elements_by_object_name(self, object_name: str) -> List[BaseElement]:
        """Find elements by object name"""
        return self._element_discovery_service.find_elements_by_object_name(object_name)
    
    def find_element_by_widget_type(self, widget_type: str, timeout: float = 0) -> Optional[BaseElement]:
        """Find element by widget type"""
        return self._element_discovery_service.find_element_by_widget_type(widget_type, timeout)
    
    def find_elements_by_widget_type(self, widget_type: str) -> List[BaseElement]:
        """Find elements by widget type"""
        return self._element_discovery_service.find_elements_by_widget_type(widget_type)
    
    def find_element_by_text(self, text: str, timeout: float = 0) -> Optional[BaseElement]:
        """Find element by text"""
        return self._element_discovery_service.find_element_by_text(text, timeout)
    
    def find_elements_by_text(self, text: str) -> List[BaseElement]:
        """Find elements by text"""
        return self._element_discovery_service.find_elements_by_text(text)
    
    def find_element_by_property(self, property_name: str, value: str, timeout: float = 0) -> Optional[BaseElement]:
        """Find element by property"""
        return self._element_discovery_service.find_element_by_property(property_name, value, timeout)
    
    def find_elements_by_property(self, property_name: str, value: str) -> List[BaseElement]:
        """Find elements by property"""
        return self._element_discovery_service.find_elements_by_property(property_name, value)
    
    def get_active_window(self) -> Optional[BaseElement]:
        """Get active window"""
        return self._element_discovery_service.get_active_window()
    
    # Screenshot operations - delegated to ScreenshotService
    def take_screenshot(self, save_path: Optional[Path] = None) -> np.ndarray:
        """Take screenshot of entire screen"""
        return self._screenshot_service.take_screenshot(save_path)
    
    def capture_screenshot(self) -> np.ndarray:
        """Capture screenshot (alias for take_screenshot)"""
        return self._screenshot_service.capture_screenshot()
    
    def capture_element_screenshot(self, element: BaseElement) -> np.ndarray:
        """Capture screenshot of specific element"""
        return self._screenshot_service.capture_element_screenshot(element)
    
    def capture_screen_region(self, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Capture screenshot of specific screen region"""
        return self._screenshot_service.capture_screen_region(x, y, width, height)
    
    def save_screenshot(self, image: np.ndarray, path: Union[str, Path]) -> None:
        """Save screenshot to file"""
        self._screenshot_service.save_screenshot(image, path)
    
    def get_screen_size(self) -> tuple[int, int]:
        """Get screen dimensions"""
        return self._screenshot_service.get_screen_size()
    
    # Performance operations - delegated to PerformanceService
    def start_performance_monitoring(self, interval: float = 1.0, metrics: Optional[List[str]] = None) -> None:
        """Start performance monitoring"""
        # TODO: Implement performance monitoring start
        pass
    
    def stop_performance_monitoring(self) -> Dict[str, Any]:
        """Stop performance monitoring and return results"""
        return self._performance_monitor.stop_performance_monitoring()
    
    def measure_action_performance(self, action: Callable, runs: int = 3) -> Dict[str, float]:
        """Measure performance of an action"""
        # TODO: Implement action performance measurement
        return {"execution_time": 0.0, "memory_usage": 0.0}
    
    def run_stress_test(self, action: Callable, duration: float) -> Dict[str, Any]:
        """Run stress test for specified duration"""
        return self._performance_tester.run_stress_test(action, duration)
    
    def check_memory_leaks(self, action: Optional[Callable] = None, iterations: int = 100) -> Dict[str, Any]:
        """Check for memory leaks"""
        # TODO: Implement memory leak detection
        return {"leak_detected": False, "memory_growth": 0.0}
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        # TODO: Implement performance metrics retrieval
        return {"cpu_usage": 0.0, "memory_usage": 0.0}
    
    def get_system_performance(self) -> Dict[str, float]:
        """Get system-wide performance metrics"""
        # TODO: Implement system performance retrieval
        return {"cpu_usage": 0.0, "memory_usage": 0.0, "disk_usage": 0.0}
    
    # Visual testing operations - delegated to VisualTestingService
    def init_visual_testing(self, baseline_dir: Union[str, Path], threshold: float = 0.95) -> None:
        """Initialize visual testing"""
        self._visual_testing_service.init_visual_testing(baseline_dir, threshold)
    
    def configure_visual_testing(self, baseline_dir: Union[str, Path], threshold: float = 0.95) -> None:
        """Configure visual testing"""
        self._visual_testing_service.configure_visual_testing(baseline_dir, threshold)
    
    def capture_baseline(self, name: str, element: Optional[BaseElement] = None) -> bool:
        """Capture visual baseline"""
        return self._visual_testing_service.capture_baseline(name, element)
    
    def verify_visual(self, name: str, element: Optional[BaseElement] = None) -> Tuple[bool, float]:
        """Verify visual state against baseline"""
        return self._visual_testing_service.verify_visual(name, element)
    
    def compare_visual(self, name: str, element: Optional[BaseElement] = None) -> Tuple[bool, float]:
        """Compare visual state"""
        return self._visual_testing_service.compare_visual(name, element)
    
    def verify_visual_state(self, name: str, element: Optional[BaseElement] = None, threshold: Optional[float] = None) -> bool:
        """Verify visual state and return boolean result"""
        return self._visual_testing_service.verify_visual_state(name, element, threshold)
    
    def capture_visual_baseline(self, name: str, element: Optional[BaseElement] = None) -> bool:
        """Capture visual baseline"""
        return self._visual_testing_service.capture_visual_baseline(name, element)
    
    def generate_visual_report(self, differences: list, name: str, output_dir: Optional[Union[str, Path]] = None) -> None:
        """Generate visual testing report"""
        self._visual_testing_service.generate_visual_report(differences, name, output_dir)
    
    def generate_diff_report(self, img1: np.ndarray, img2: np.ndarray, output_path: Union[str, Path]) -> None:
        """Generate difference report between two images"""
        self._visual_testing_service.generate_diff_report(img1, img2, output_path)
    
    def find_all_elements(self, template: np.ndarray, threshold: float = 0.8) -> list:
        """Find all elements matching template"""
        return self._visual_testing_service.find_all_elements(template, threshold)
    
    def wait_for_image(self, template: np.ndarray, timeout: float = 10) -> bool:
        """Wait for image to appear"""
        return self._visual_testing_service.wait_for_image(template, timeout)
    
    def highlight_differences(self, img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        """Highlight differences between two images"""
        return self._visual_testing_service.highlight_differences(img1, img2)
    
    # Input operations - delegated to InputService
    @property
    def keyboard(self):
        """Get keyboard instance"""
        return self._input_service.keyboard
    
    @property
    def mouse(self):
        """Get mouse instance"""
        return self._input_service.mouse
    
    def press_key(self, key: str) -> None:
        """Press a key"""
        self._input_service.press_key(key)
    
    def press_keys(self, *keys: str) -> None:
        """Press multiple keys"""
        self._input_service.press_keys(*keys)
    
    def type_text(self, text: str, interval: Optional[float] = None) -> None:
        """Type text with optional interval between characters"""
        self._input_service.type_text(text, interval)
    
    def mouse_move(self, x: int, y: int) -> None:
        """Move mouse to coordinates"""
        self._input_service.mouse_move(x, y)
    
    def mouse_click(self, x: int, y: int, button: str = "left") -> None:
        """Click mouse at coordinates"""
        self._input_service.mouse_click(x, y, button)
    
    def mouse_double_click(self, x: int, y: int) -> None:
        """Double click mouse at coordinates"""
        self._input_service.mouse_double_click(x, y)
    
    def mouse_right_click(self, x: int, y: int) -> None:
        """Right click mouse at coordinates"""
        self._input_service.mouse_right_click(x, y)
    
    def mouse_drag_and_drop(self, start_x: int, start_y: int, end_x: int, end_y: int) -> None:
        """Drag and drop from start to end coordinates"""
        self._input_service.mouse_drag_and_drop(start_x, start_y, end_x, end_y)
    
    def mouse_scroll(self, x: int, y: int, direction: str = "down", amount: int = 1) -> None:
        """Scroll mouse at coordinates"""
        self._input_service.mouse_scroll(x, y, direction, amount)
    
    def hotkey(self, *keys: str) -> None:
        """Press hotkey combination"""
        self._input_service.hotkey(*keys)
    
    def copy(self) -> None:
        """Copy selected text"""
        self._input_service.copy()
    
    def paste(self) -> None:
        """Paste text"""
        self._input_service.paste()
    
    def select_all(self) -> None:
        """Select all text"""
        self._input_service.select_all()
    
    def undo(self) -> None:
        """Undo last action"""
        self._input_service.undo()
    
    def redo(self) -> None:
        """Redo last action"""
        self._input_service.redo()
    
    def save(self) -> None:
        """Save (Ctrl+S)"""
        self._input_service.save()
    
    def open(self) -> None:
        """Open (Ctrl+O)"""
        self._input_service.open()
    
    def new(self) -> None:
        """New (Ctrl+N)"""
        self._input_service.new()
    
    def close(self) -> None:
        """Close (Ctrl+W)"""
        self._input_service.close()
    
    def quit(self) -> None:
        """Quit (Alt+F4)"""
        self._input_service.quit()
    
    # Wait operations
    def wait_until(self, condition: Callable[[], bool], timeout: float = 10, poll_frequency: float = 0.5) -> bool:
        """Wait until condition is true"""
        try:
            start_time = time.time()
            while time.time() - start_time < timeout:
                if condition():
                    return True
                time.sleep(poll_frequency)
            return False
        except Exception as e:
            logger.error(f"Wait until failed: {e}")
            return False
    
    def wait_for(self, condition: Callable[[], bool], timeout: Optional[float] = None, interval: Optional[float] = None) -> bool:
        """Wait for condition (alias for wait_until)"""
        timeout = timeout or self._config.default_timeout
        interval = interval or self._config.default_interval
        return self.wait_until(condition, timeout, interval)
    
    # OCR operations
    def set_ocr_languages(self, languages: List[str]) -> None:
        """Set OCR languages"""
        try:
            self._ocr_languages = languages
            logger.info(f"OCR languages set to: {languages}")
        except Exception as e:
            logger.error(f"Failed to set OCR languages: {e}")
    
    def set_ocr_language(self, language: str) -> None:
        """Set single OCR language"""
        self.set_ocr_languages([language])
    
    @property
    def ocr(self):
        """Get OCR engine"""
        try:
            from ..ocr.engine import OCREngine
            ocr_engine = OCREngine()
            ocr_engine.set_languages(self._ocr_languages)
            return ocr_engine
        except Exception as e:
            logger.error(f"Failed to get OCR engine: {e}")
            return None
    
    # Application management
    def get_current_application(self) -> Optional[Any]:
        """Get current application"""
        return self._current_application
    
    def attach_to_process(self, pid: int) -> None:
        """Attach to process by PID"""
        try:
            self._current_application = self.backend.attach_to_application(pid)
            logger.info(f"Attached to process {pid}")
        except Exception as e:
            logger.error(f"Failed to attach to process {pid}: {e}")
    
    def attach_to_application(self, pid: int) -> Any:
        """Attach to application (alias for attach_to_process)"""
        self.attach_to_process(pid)
        return self._current_application
    
    def launch_application(self, path: str, *args, **kwargs) -> Any:
        """Launch application"""
        try:
            self._current_application = self.backend.launch_application(path, list(args))
            logger.info(f"Launched application: {path}")
            return self._current_application
        except Exception as e:
            logger.error(f"Failed to launch application {path}: {e}")
            return None
    
    # Configuration
    def configure_waits(self, timeout: float = 10.0, polling_interval: float = 0.5) -> None:
        """Configure wait settings"""
        try:
            self._config.default_timeout = timeout
            self._config.default_interval = polling_interval
            logger.info(f"Wait configuration updated: timeout={timeout}, interval={polling_interval}")
        except Exception as e:
            logger.error(f"Failed to configure waits: {e}")
    
    # Service accessors
    @property
    def element_discovery(self) -> ElementDiscoveryService:
        """Get element discovery service"""
        return self._element_discovery_service
    
    @property
    def screenshot_service(self) -> ScreenshotService:
        """Get screenshot service"""
        return self._screenshot_service
    
    @property
    def performance_service(self) -> PerformanceMonitor:
        """Get performance service"""
        return self._performance_monitor
    
    @property
    def visual_testing_service(self) -> VisualTestingService:
        """Get visual testing service"""
        return self._visual_testing_service
    
    @property
    def input_service(self) -> InputService:
        """Get input service"""
        return self._input_service
    
    # Cleanup
    def cleanup(self) -> None:
        """Cleanup session resources"""
        try:
            if self._performance_monitor:
                self._performance_monitor.stop_performance_monitoring()
            
            if self.backend:
                self.backend.cleanup()
            
            logger.info(f"Session {self.session_id} cleaned up")
        except Exception as e:
            logger.error(f"Failed to cleanup session: {e}")
    
    def __del__(self):
        """Destructor"""
        try:
            self.cleanup()
        except Exception:
            pass 

    def close(self):
        """Close session"""
        self.is_closed = True


class SessionUtils:
    """
    Utility methods for automation session.
    
    Provides convenient access to common utility functions.
    """
    
    def __init__(self):
        """Initialize session utils"""
        pass
    
    # Image utilities
    def load_image(self, path: Union[str, Path]) -> Optional[np.ndarray]:
        """Load image from file"""
        return load_image(Path(path) if isinstance(path, str) else path)
    
    def save_image(self, image: np.ndarray, path: Union[str, Path]) -> bool:
        """Save image to file"""
        return save_image(image, Path(path) if isinstance(path, str) else path)
    
    def resize_image(self, image: np.ndarray, width: Optional[int] = None, height: Optional[int] = None) -> np.ndarray:
        """Resize image while maintaining aspect ratio"""
        return resize_image(image, width, height)
    
    def compare_images(self, img1: np.ndarray, img2: np.ndarray, threshold: float = 0.95) -> bool:
        """Compare two images for similarity"""
        result = compare_images(img1, img2, threshold)
        return result > threshold
    
    def find_template(self, image: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> List[Tuple[int, int, float]]:
        """Find template in image using template matching"""
        return find_template(image, template, threshold)
    
    def highlight_region(self, image: np.ndarray, x: int, y: int, width: int, height: int, 
                        color: Tuple[int, int, int] = (0, 255, 0), thickness: int = 2) -> np.ndarray:
        """Draw a rectangle around a specified region"""
        return highlight_region(image, x, y, width, height, color, thickness)
    
    def crop_image(self, image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
        """Crop image to specified region"""
        return crop_image(image, x, y, width, height)
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better analysis"""
        return preprocess_image(image)
    
    def create_mask(self, image: np.ndarray, lower: Tuple[int, int, int], upper: Tuple[int, int, int]) -> np.ndarray:
        """Create color mask for image"""
        return create_mask(image, lower, upper)
    
    def enhance_image(self, image: np.ndarray, method: str = "contrast") -> np.ndarray:
        """Enhance image using specified method"""
        return enhance_image(image, method)
    
    # File utilities
    def ensure_dir(self, path: Union[str, Path]) -> Path:
        """Ensure directory exists"""
        return ensure_dir(Path(path) if isinstance(path, str) else path)
    
    def get_temp_dir(self) -> Path:
        """Get temporary directory"""
        return get_temp_dir()
    
    def safe_remove(self, path: Union[str, Path]) -> bool:
        """Safely remove file or directory"""
        return safe_remove(Path(path) if isinstance(path, str) else path)
    
    def get_temp_path(self, suffix: str = '') -> Path:
        """Get a unique temporary file path"""
        return get_temp_path(suffix)
    
    # Validation utilities
    def validate_type(self, value: Any, expected_type: Union[Type, tuple]) -> bool:
        """Validate that a value is of the expected type"""
        return validate_type(value, expected_type)
    
    def validate_not_none(self, value: Any) -> bool:
        """Validate that a value is not None"""
        return validate_not_none(value)
    
    def validate_string_not_empty(self, value: Optional[str]) -> bool:
        """Validate string is not empty"""
        return validate_string_not_empty(value)
    
    def validate_number_range(self, value: Union[int, float], 
                            min_value: Optional[Union[int, float]] = None,
                            max_value: Optional[Union[int, float]] = None) -> bool:
        """Validate that a number is within a specified range"""
        return validate_number_range(value, min_value, max_value)
    
    # Retry utility
    def retry(self, attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)) -> Callable:
        """Retry decorator for functions that may fail"""
        return retry(attempts, delay, exceptions)
    
    # Metrics utilities
    def create_metrics_collector(self) -> MetricsCollector:
        """Create a new metrics collector"""
        return MetricsCollector()
    
    def create_metric_point(self, value: float) -> MetricPoint:
        """Create a new metric point"""
        return MetricPoint(value)
    
    # Additional convenience methods
    def convert_image_format(self, image: np.ndarray, format: str = "PNG") -> np.ndarray:
        """Convert image to specified format"""
        # This is a placeholder - actual implementation would depend on format
        return image
    
    def create_difference_image(self, img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        """Create difference image between two images"""
        if img1.shape != img2.shape:
            # Resize img2 to match img1
            img2 = resize_image(img2, img1.shape[1], img1.shape[0])
        
        # Calculate absolute difference
        diff = cv2.absdiff(img1, img2)
        return diff 