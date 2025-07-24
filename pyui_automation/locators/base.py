"""
Base locator classes and strategies for element finding.

This module provides the foundation for platform-specific locators
and defines various search strategies.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Any, Union
from dataclasses import dataclass
import time

from .interfaces import IBackendForLocator, ILocator, ILocatorStrategy


@dataclass
class LocatorStrategy(ILocatorStrategy):
    """
    Base class for locator strategies.
    Defines how to find elements using different search methods.
    """
    _value: str
    _timeout: Optional[float] = None

    @property
    def value(self) -> str:
        """Get strategy value"""
        return self._value

    @property
    def timeout(self) -> Optional[float]:
        """Get strategy timeout"""
        return self._timeout


# Windows-specific strategies
@dataclass
class ByName(LocatorStrategy):
    """Find element by name/text"""
    _value: str
    _timeout: Optional[float] = None


@dataclass
class ByClassName(LocatorStrategy):
    """Find element by class name"""
    _value: str
    _timeout: Optional[float] = None


@dataclass
class ByAutomationId(LocatorStrategy):
    """Find element by automation ID"""
    _value: str
    _timeout: Optional[float] = None


@dataclass
class ByControlType(LocatorStrategy):
    """Find element by control type"""
    _value: str
    _timeout: Optional[float] = None


@dataclass
class ByXPath(LocatorStrategy):
    """Find element by XPath"""
    _value: str
    _timeout: Optional[float] = None


@dataclass
class ByAccessibilityId(LocatorStrategy):
    """Find element by accessibility ID"""
    _value: str
    _timeout: Optional[float] = None


# Linux-specific strategies
@dataclass
class ByRole(LocatorStrategy):
    """Find element by AT-SPI2 role"""
    _value: str
    _timeout: Optional[float] = None


@dataclass
class ByDescription(LocatorStrategy):
    """Find element by AT-SPI2 description"""
    _value: str
    _timeout: Optional[float] = None


@dataclass
class ByPath(LocatorStrategy):
    """Find element by AT-SPI2 path"""
    _value: str
    _timeout: Optional[float] = None


@dataclass
class ByState(LocatorStrategy):
    """Find element by AT-SPI2 state"""
    _value: str
    _timeout: Optional[float] = None


# macOS-specific strategies
@dataclass
class ByAXIdentifier(LocatorStrategy):
    """Find element by macOS Accessibility identifier"""
    _value: str
    _timeout: Optional[float] = None


@dataclass
class ByAXTitle(LocatorStrategy):
    """Find element by macOS Accessibility title"""
    _value: str
    _timeout: Optional[float] = None


@dataclass
class ByAXRole(LocatorStrategy):
    """Find element by macOS Accessibility role"""
    _value: str
    _timeout: Optional[float] = None


@dataclass
class ByAXDescription(LocatorStrategy):
    """Find element by macOS Accessibility description"""
    _value: str
    _timeout: Optional[float] = None


@dataclass
class ByAXValue(LocatorStrategy):
    """Find element by macOS Accessibility value"""
    _value: str
    _timeout: Optional[float] = None


class BaseLocator(ILocator):
    """
    Base class that ensures LSP compliance for all locator implementations.
    
    This class provides default implementations and validation to ensure
    that all derived classes can be substituted without breaking functionality.
    """

    def __init__(self, backend: IBackendForLocator) -> None:
        """Initialize base locator with LSP compliance"""
        if backend is None:
            raise ValueError("Backend cannot be None")
        
        self._backend = backend
        self._logger = backend.logger if hasattr(backend, 'logger') else None
        self._validate_implementation()
    
    def _validate_implementation(self) -> None:
        """Validate that all required methods are implemented"""
        required_methods = [
            '_find_element_impl',
            '_find_elements_impl'
        ]
        
        missing_methods = []
        for method_name in required_methods:
            if not hasattr(self, method_name):
                missing_methods.append(method_name)
        
        if missing_methods:
            raise NotImplementedError(
                f"Locator {self.__class__.__name__} is missing required methods: {missing_methods}"
            )
    
    @property
    def backend(self) -> IBackendForLocator:
        """Get backend instance"""
        return self._backend
    
    @property
    def logger(self):
        """Get logger instance"""
        return self._logger
    
    def find_element(self, strategy: LocatorStrategy) -> Optional[Any]:
        """Find element with validation"""
        if strategy is None:
            raise ValueError("Strategy cannot be None")
        
        if not isinstance(strategy, LocatorStrategy):
            raise ValueError("Strategy must be a LocatorStrategy instance")
        
        if not strategy.value:
            raise ValueError("Strategy value cannot be empty")
        
        return self._find_element_impl(strategy)
    
    @abstractmethod
    def _find_element_impl(self, strategy: LocatorStrategy) -> Optional[Any]:
        """Implementation-specific element finding"""
        pass
    
    def find_elements(self, strategy: LocatorStrategy) -> List[Any]:
        """Find elements with validation"""
        if strategy is None:
            raise ValueError("Strategy cannot be None")
        
        if not isinstance(strategy, LocatorStrategy):
            raise ValueError("Strategy must be a LocatorStrategy instance")
        
        if not strategy.value:
            raise ValueError("Strategy value cannot be empty")
        
        elements = self._find_elements_impl(strategy)
        
        if not isinstance(elements, list):
            raise ValueError("find_elements must return a list")
        
        return elements
    
    @abstractmethod
    def _find_elements_impl(self, strategy: LocatorStrategy) -> List[Any]:
        """Implementation-specific elements finding"""
        pass
    
    def find_element_with_timeout(self, strategy: LocatorStrategy, timeout: float = 10.0) -> Optional[Any]:
        """Find element with timeout and validation"""
        if timeout <= 0:
            raise ValueError("Timeout must be positive")
        
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            element = self.find_element(strategy)
            if element:
                return element
            time.sleep(0.1)
        
        return None
    
    def wait_for_element(self, strategy: LocatorStrategy, timeout: float = 10.0) -> Optional[Any]:
        """Wait for element to appear (alias for find_element_with_timeout)"""
        return self.find_element_with_timeout(strategy, timeout)


