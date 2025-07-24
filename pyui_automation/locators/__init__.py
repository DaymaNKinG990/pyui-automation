"""
Locators module for pyui-automation.

This module provides platform-specific element locators and search strategies.
"""

from .base import (
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
)

from .interfaces import (
    IBackendForLocator,
    ILocator,
    ILocatorStrategy,
)

from .windows import WindowsLocator
from .linux import LinuxLocator
from .macos import MacOSLocator

__all__ = [
    # Base classes
    "BaseLocator",
    "LocatorStrategy",
    
    # Interfaces
    "IBackendForLocator",
    "ILocator",
    "ILocatorStrategy",
    
    # Windows locators
    "ByName",
    "ByClassName", 
    "ByAutomationId",
    "ByControlType",
    "ByXPath",
    "ByAccessibilityId",
    "WindowsLocator",
    
    # Linux locators
    "ByRole",
    "ByDescription",
    "ByPath",
    "ByState",
    "LinuxLocator",
    
    # macOS locators
    "ByAXIdentifier",
    "ByAXTitle",
    "ByAXRole",
    "ByAXDescription",
    "ByAXValue",
    "MacOSLocator",
]
