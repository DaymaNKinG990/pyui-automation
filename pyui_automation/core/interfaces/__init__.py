"""
Interfaces package - defines contracts for services.

This package contains abstract base classes and interfaces
that define contracts for different services in the automation framework.
"""

# Backend interfaces
from .ibackend import IBackend
from .ibackend_lifecycle import IBackendLifecycle
from .ibackend_application import IBackendApplication
from .ibackend_window import IBackendWindow
from .ibackend_screen import IBackendScreen

# Application interface
from .iapplication import IApplication

# Element interfaces
from .ielement import IElement
from .ielement_interaction import IElementInteraction
from .ielement_wait import IElementWait
from .ielement_search import IElementSearch
from .ielement_state import IElementState
from .ielement_geometry import IElementGeometry
from .ielement_properties import IElementProperties
from .ielement_screenshot import IElementScreenshot

# Service interfaces
from .iinput_service import IInputService
from .ivisual_testing_service import IVisualTestingService
from .iperformance_service import IPerformanceService
from .iscreenshot_service import IScreenshotService
from .ielement_discovery_service import IElementDiscoveryService
from .iconfiguration_manager import IConfigurationManager
from .isession_manager import ISessionManager
from .ilocator_factory import ILocatorFactory
from .ibackend_factory import IBackendFactory

# Input backend interface
from .iinput_backend import IInputBackend

# OCR service interfaces
from .iocr_service import (
    ITextRecognition,
    ITextLocation,
    ITextVerification,
    IImagePreprocessing,
    IOCRService
)

__all__ = [
    # Backend interfaces
    "IBackend",
    "IBackendLifecycle", 
    "IBackendApplication",
    "IBackendWindow",
    "IBackendScreen",
    
    # Application interface
    "IApplication",
    
    # Element interfaces
    "IElement",
    "IElementInteraction",
    "IElementWait",
    "IElementSearch", 
    "IElementState",
    "IElementGeometry",
    "IElementProperties",
    "IElementScreenshot",
    
    # Service interfaces
    "IInputService",
    "IVisualTestingService",
    "IPerformanceService",
    "IScreenshotService",
    "IElementDiscoveryService",
    "IConfigurationManager",
    "ISessionManager",
    "ILocatorFactory",
    "IBackendFactory",
    
    # Input backend interface
    "IInputBackend",
    
    # OCR service interfaces
    "ITextRecognition",
    "ITextLocation", 
    "ITextVerification",
    "IImagePreprocessing",
    "IOCRService",
] 