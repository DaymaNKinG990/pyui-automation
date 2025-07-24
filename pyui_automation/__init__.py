"""
PyUI Automation - Cross-platform desktop UI automation framework

A powerful Python library for automating desktop applications across Windows, Linux, and macOS.
Supports Qt applications, visual testing, accessibility checks, performance monitoring, and OCR.
"""

# Core imports
from .core.session import AutomationSession
from .core.services.backend_factory import BackendFactory
from .core.di_manager import DIAutomationManager

# Application management
from .core.application import Application

# High-level API
from .pyui_automation import PyUIAutomation, TestHelper, app_session, launch_app

# Locators
from .locators import (
    BaseLocator,
    LocatorStrategy,
    ByName,
    ByClassName,
    ByAutomationId,
    ByControlType,
    ByXPath,
    ByAccessibilityId,
    ByRole,
    ByDescription,
    ByPath,
    ByState,
    ByAXIdentifier,
    ByAXTitle,
    ByAXRole,
    ByAXDescription,
    ByAXValue,
    IBackendForLocator,
    ILocator,
    ILocatorStrategy,
    WindowsLocator,
    LinuxLocator,
    MacOSLocator,
)

# Elements
from .elements.base_element import BaseElement
from .elements.properties import Property, StringProperty, IntProperty, BoolProperty, DictProperty, OptionalStringProperty

# Input
from .input.keyboard import Keyboard
from .input.mouse import Mouse

# OCR
from .ocr import (
    OCREngine,
    StubOCREngine,
    UnifiedOCREngine,
    OCRResult,
    TextLocation,
    ImagePreprocessor,
    recognize_text,
    set_languages,
    get_implementation_info,
    default_engine
)

# Services - исправлено: импортируем из правильных мест
from .core.services.performance_monitor import PerformanceMonitor
from .core.services.performance_analyzer import PerformanceAnalyzer
from .core.services.performance_reporter import PerformanceReporter
from .core.services.performance_tester import PerformanceTester
from .core.services.memory_leak_detector import MemoryLeakDetector

# Utils
from .utils.core import retry, get_temp_path
from .utils.image import (
    load_image, save_image, resize_image, compare_images,
    find_template, highlight_region, crop_image, preprocess_image,
    create_mask, enhance_image
)
from .utils.file import ensure_dir, get_temp_dir, safe_remove
from .utils.validation import validate_type, validate_not_none, validate_string_not_empty, validate_number_range
from .utils.metrics import MetricsCollector, MetricPoint

# Exceptions
from .core.exceptions import (
    AutomationError,
    ElementNotFoundError,
    TimeoutError,
    BackendError,
    ConfigurationError,
    VisualError,
    OCRError,
)

# Version
__version__ = "1.0.0"

__all__ = [
    # Core
    "AutomationSession",
    "BackendFactory", 
    "DIAutomationManager",
    
    # Application
    "Application",
    
    # High-level API
    "PyUIAutomation",
    "TestHelper", 
    "app_session",
    "launch_app",
    
    # Locators
    "BaseLocator",
    "LocatorStrategy",
    "ByName",
    "ByClassName", 
    "ByAutomationId",
    "ByControlType",
    "ByXPath",
    "ByAccessibilityId",
    "ByRole",
    "ByDescription",
    "ByPath", 
    "ByState",
    "ByAXIdentifier",
    "ByAXTitle",
    "ByAXRole",
    "ByAXDescription",
    "ByAXValue",
    "IBackendForLocator",
    "ILocator",
    "ILocatorStrategy",
    "WindowsLocator",
    "LinuxLocator",
    "MacOSLocator",
    
    # Elements
    "BaseElement",
    "Property",
    "StringProperty", 
    "IntProperty", 
    "BoolProperty",
    "DictProperty",
    "OptionalStringProperty",
    
    # Input
    "Keyboard",
    "Mouse",
    
    # OCR
    "OCREngine",
    "StubOCREngine",
    "UnifiedOCREngine",
    "OCRResult",
    "TextLocation",
    "ImagePreprocessor",
    "recognize_text",
    "set_languages",
    "get_implementation_info",
    "default_engine",
    
    # Services
    "PerformanceMonitor",
    "PerformanceAnalyzer",
    "PerformanceReporter",
    "PerformanceTester",
    "MemoryLeakDetector",
    
    # Utils
    "retry",
    "get_temp_path",
    "load_image",
    "save_image",
    "resize_image", 
    "compare_images",
    "find_template",
    "highlight_region",
    "crop_image",
    "preprocess_image",
    "create_mask",
    "enhance_image",
    "ensure_dir",
    "get_temp_dir",
    "safe_remove",
    "validate_type",
    "validate_not_none",
    "validate_string_not_empty",
    "validate_number_range",
    "MetricsCollector",
    "MetricPoint",
    
    # Exceptions
    "AutomationError",
    "ElementNotFoundError",
    "TimeoutError",
    "BackendError",
    "ConfigurationError",
    "VisualError",
    "OCRError",
]
