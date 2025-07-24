"""
DI Automation Manager - Dependency Injection based automation manager.

This module provides a singleton automation manager that uses dependency injection
to manage all services and their dependencies.
"""

from typing import Optional, Any, Dict, List, Union
from pathlib import Path
import logging
from logging import getLogger

from .services.di_container import get_container, register_service, get_service, set_config
from .interfaces import (
    IBackendFactory, ILocatorFactory, ISessionManager, IConfigurationManager,
    IElementDiscoveryService, IScreenshotService, IPerformanceService,
    IVisualTestingService, IInputService, IBackend, IElement
)
from .session import AutomationSession
from .config import AutomationConfig


class DIAutomationManager:
    """
    Dependency Injection based automation manager.
    
    This class serves as the main entry point for the automation framework,
    using dependency injection to manage all services and their dependencies.
    """
    
    _instance: Optional['DIAutomationManager'] = None
    _initialized: bool = False
    
    def __new__(cls) -> 'DIAutomationManager':
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize DI Automation Manager"""
        if self._initialized:
            return
        
        self._logger = getLogger(__name__)
        self._container = get_container()
        self._current_session: Optional[AutomationSession] = None
        self._config: Optional[AutomationConfig] = None
        
        # Initialize DI container with services
        self._initialize_services()
        self._initialized = True
        self._logger.info("DIAutomationManager initialized successfully")
    
    def _initialize_services(self) -> None:
        """Initialize all services in DI container"""
        try:
            # Register core services
            from .services.backend_factory import BackendFactory
            from .services.locator_factory import LocatorFactory
            from .services.session_manager import SessionManager
            from .services.configuration_manager import ConfigurationManager
            from .services.element_discovery_service import ElementDiscoveryService
            from .services.screenshot_service import ScreenshotService
            from .services.performance_monitor import PerformanceMonitor
            from .services.performance_analyzer import PerformanceAnalyzer
            from .services.performance_tester import PerformanceTester
            from .services.memory_leak_detector import MemoryLeakDetector
            from .services.visual_testing_service import VisualTestingService
            from .services.input_service import InputService
            
            # Register services with their interfaces
            register_service('backend_factory', BackendFactory, singleton=True)
            register_service('locator_factory', LocatorFactory, singleton=True)
            register_service('session_manager', SessionManager, singleton=True)
            register_service('configuration_manager', ConfigurationManager, singleton=True)
            register_service('element_discovery_service', ElementDiscoveryService, singleton=True)
            register_service('screenshot_service', ScreenshotService, singleton=True)
            register_service('performance_monitor', PerformanceMonitor, singleton=True)
            register_service('performance_analyzer', PerformanceAnalyzer, singleton=True)
            register_service('performance_tester', PerformanceTester, singleton=True)
            register_service('memory_leak_detector', MemoryLeakDetector, singleton=True)
            register_service('visual_testing_service', VisualTestingService, singleton=True)
            register_service('input_service', InputService, singleton=True)
            
            # Register specialized element services
            from .elements.specialized import (
                ButtonElement, TextElement, CheckboxElement, 
                DropdownElement, InputElement, WindowElement
            )
            from .elements.element_factory import ElementFactory
            
            register_service('element_factory', ElementFactory, singleton=True)
            register_service('button_element', ButtonElement, singleton=False)
            register_service('text_element', TextElement, singleton=False)
            register_service('checkbox_element', CheckboxElement, singleton=False)
            register_service('dropdown_element', DropdownElement, singleton=False)
            register_service('input_element', InputElement, singleton=False)
            register_service('window_element', WindowElement, singleton=False)
            
            # Set default configuration
            self._set_default_config()
            
            self._logger.info("All services registered successfully")
            
        except Exception as e:
            self._logger.error(f"Failed to initialize services: {e}")
            raise
    
    def _set_default_config(self) -> None:
        """Set default configuration"""
        default_config = {
            'timeout': 30.0,
            'retry_attempts': 3,
            'retry_delay': 1.0,
            'screenshot_format': 'png',
            'log_level': 'INFO',
            'performance_monitoring': True,
            'visual_testing': True,
            'ocr_enabled': True
        }
        
        for key, value in default_config.items():
            set_config(key, value)
    
    @property
    def backend_factory(self) -> IBackendFactory:
        """Get backend factory service"""
        return get_service('backend_factory')
    
    @property
    def locator_factory(self) -> ILocatorFactory:
        """Get locator factory service"""
        return get_service('locator_factory')
    
    @property
    def session_manager(self) -> ISessionManager:
        """Get session manager service"""
        return get_service('session_manager')
    
    @property
    def configuration_manager(self) -> IConfigurationManager:
        """Get configuration manager service"""
        return get_service('configuration_manager')
    
    @property
    def element_discovery_service(self) -> IElementDiscoveryService:
        """Get element discovery service"""
        return get_service('element_discovery_service')
    
    @property
    def screenshot_service(self) -> IScreenshotService:
        """Get screenshot service"""
        return get_service('screenshot_service')
    
    @property
    def performance_monitor(self) -> Any:
        """Get performance monitor service"""
        return get_service('performance_monitor')

    @property
    def performance_analyzer(self) -> Any:
        """Get performance analyzer service"""
        return get_service('performance_analyzer')

    @property
    def performance_tester(self) -> Any:
        """Get performance tester service"""
        return get_service('performance_tester')

    @property
    def memory_leak_detector(self) -> Any:
        """Get memory leak detector service"""
        return get_service('memory_leak_detector')
    
    @property
    def visual_testing_service(self) -> IVisualTestingService:
        """Get visual testing service"""
        return get_service('visual_testing_service')
    
    @property
    def input_service(self) -> IInputService:
        """Get input service"""
        return get_service('input_service')
    
    @property
    def element_factory(self) -> Any:
        """Get element factory service"""
        return get_service('element_factory')
    
    def create_session(self, config: Optional[AutomationConfig] = None) -> AutomationSession:
        """
        Create a new automation session.
        
        Args:
            config: Optional configuration for the session
            
        Returns:
            AutomationSession: New automation session
        """
        try:
            if config:
                self._config = config
                # Update DI container config
                for key, value in config.__dict__.items():
                    if value is not None:
                        set_config(key, value)
            
            # Create session using session manager
            session = self.session_manager.create_session()
            self._current_session = session
            
            self._logger.info("Automation session created successfully")
            return session
            
        except Exception as e:
            self._logger.error(f"Failed to create session: {e}")
            raise
    
    def get_current_session(self) -> Optional[AutomationSession]:
        """Get current automation session"""
        return self._current_session
    
    def close_session(self) -> None:
        """Close current automation session"""
        try:
            if self._current_session:
                self.session_manager.close_session(self._current_session)
                self._current_session = None
                self._logger.info("Automation session closed successfully")
        except Exception as e:
            self._logger.error(f"Failed to close session: {e}")
            raise
    
    def create_backend(self, platform: Optional[str] = None) -> IBackend:
        """
        Create a backend for the specified platform.
        
        Args:
            platform: Platform name (windows, linux, macos)
            
        Returns:
            IBackend: Platform-specific backend
        """
        try:
            backend = self.backend_factory.create_backend(platform)
            self._logger.info(f"Backend created for platform: {platform or 'auto'}")
            return backend
        except Exception as e:
            self._logger.error(f"Failed to create backend: {e}")
            raise
    
    def create_element(self, element_type: str, native_element: Any, session: AutomationSession) -> IElement:
        """
        Create a specialized element.
        
        Args:
            element_type: Type of element (button, text, checkbox, etc.)
            native_element: Native platform element
            session: Automation session
            
        Returns:
            IElement: Specialized element instance
        """
        try:
            element = self.element_factory.create_element(element_type, native_element, session)
            self._logger.debug(f"Element created: {element_type}")
            return element
        except Exception as e:
            self._logger.error(f"Failed to create element: {e}")
            raise
    
    def find_element(self, session: AutomationSession, **kwargs) -> Optional[IElement]:
        """
        Find element using discovery service.
        
        Args:
            session: Automation session
            **kwargs: Search criteria
            
        Returns:
            Optional[IElement]: Found element or None
        """
        try:
            element = self.element_discovery_service.find_element(session, **kwargs)
            if element:
                self._logger.debug(f"Element found: {kwargs}")
            return element
        except Exception as e:
            self._logger.error(f"Failed to find element: {e}")
            raise
    
    def find_elements(self, session: AutomationSession, **kwargs) -> List[IElement]:
        """
        Find multiple elements using discovery service.
        
        Args:
            session: Automation session
            **kwargs: Search criteria
            
        Returns:
            List[IElement]: List of found elements
        """
        try:
            elements = self.element_discovery_service.find_elements(session, **kwargs)
            self._logger.debug(f"Found {len(elements)} elements: {kwargs}")
            return elements
        except Exception as e:
            self._logger.error(f"Failed to find elements: {e}")
            raise
    
    def take_screenshot(self, session: AutomationSession, region: Optional[Dict] = None) -> Optional[Any]:
        """
        Take screenshot using screenshot service.
        
        Args:
            session: Automation session
            region: Optional region to capture
            
        Returns:
            Optional[Any]: Screenshot data or None
        """
        try:
            screenshot = self.screenshot_service.capture_screenshot(session, region)
            self._logger.debug("Screenshot captured successfully")
            return screenshot
        except Exception as e:
            self._logger.error(f"Failed to take screenshot: {e}")
            raise
    
    def get_performance_metrics(self, session: AutomationSession) -> Dict[str, Any]:
        """
        Get performance metrics using performance monitor.
        
        Args:
            session: Automation session
            
        Returns:
            Dict[str, Any]: Performance metrics
        """
        try:
            metrics = self.performance_monitor.get_metrics()
            self._logger.debug("Performance metrics retrieved")
            return metrics
        except Exception as e:
            self._logger.error(f"Failed to get performance metrics: {e}")
            raise
    
    def perform_visual_test(self, session: AutomationSession, baseline_path: str, 
                          current_screenshot: Any) -> Dict[str, Any]:
        """
        Perform visual testing using visual testing service.
        
        Args:
            session: Automation session
            baseline_path: Path to baseline image
            current_screenshot: Current screenshot data
            
        Returns:
            Dict[str, Any]: Visual test results
        """
        try:
            results = self.visual_testing_service.compare_with_baseline(
                session, baseline_path, current_screenshot
            )
            self._logger.debug("Visual test completed")
            return results
        except Exception as e:
            self._logger.error(f"Failed to perform visual test: {e}")
            raise
    
    def send_input(self, session: AutomationSession, input_type: str, **kwargs) -> bool:
        """
        Send input using input service.
        
        Args:
            session: Automation session
            input_type: Type of input (keyboard, mouse, etc.)
            **kwargs: Input parameters
            
        Returns:
            bool: Success status
        """
        try:
            success = self.input_service.send_input(session, input_type, **kwargs)
            self._logger.debug(f"Input sent: {input_type}")
            return success
        except Exception as e:
            self._logger.error(f"Failed to send input: {e}")
            raise
    
    def get_configuration(self) -> Dict[str, Any]:
        """Get current configuration"""
        return self.configuration_manager.get_configuration()
    
    def update_configuration(self, config: Dict[str, Any]) -> None:
        """Update configuration"""
        self.configuration_manager.update_configuration(config)
    
    def get_service_info(self) -> Dict[str, Any]:
        """Get information about registered services"""
        container = get_container()
        return {
            'registered_services': container.get_registered_services(),
            'singleton_services': container.get_singleton_services(),
            'configuration': container.get_all_config()
        }
    
    def cleanup(self) -> None:
        """Cleanup all resources"""
        try:
            # Close current session
            if self._current_session:
                self.close_session()
            
            # Cleanup container
            from .services.di_container import cleanup
            cleanup()
            
            # Reset singleton
            DIAutomationManager._instance = None
            DIAutomationManager._initialized = False
            
            self._logger.info("DIAutomationManager cleanup completed")
            
        except Exception as e:
            self._logger.error(f"Failed to cleanup: {e}")
            raise
    
    def __enter__(self):
        """Context manager entry"""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.cleanup()


# Global instance for easy access
_global_manager: Optional[DIAutomationManager] = None


def get_automation_manager() -> DIAutomationManager:
    """Get global automation manager instance"""
    global _global_manager
    if _global_manager is None:
        _global_manager = DIAutomationManager()
    return _global_manager


def create_session(config: Optional[AutomationConfig] = None) -> AutomationSession:
    """Create automation session using global manager"""
    return get_automation_manager().create_session(config)


def get_current_session() -> Optional[AutomationSession]:
    """Get current session using global manager"""
    return get_automation_manager().get_current_session()


def close_session() -> None:
    """Close current session using global manager"""
    get_automation_manager().close_session()


def cleanup() -> None:
    """Cleanup global manager"""
    global _global_manager
    if _global_manager:
        _global_manager.cleanup()
        _global_manager = None 