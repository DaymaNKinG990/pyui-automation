"""
ILocatorFactory interface - defines contract for locator factory.

Responsible for:
- Locator creation
- Platform-specific locator mapping
- Locator registration
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Type

from ...locators.interfaces import IBackendForLocator


class ILocatorFactory(ABC):
    """Interface for locator factory"""
    
    @abstractmethod
    def create_locator(self, platform_name: str, backend: IBackendForLocator) -> Any:
        """Create locator for specified platform"""
        pass
    
    @abstractmethod
    def register_locator(self, platform_name: str, locator_class: Type) -> None:
        """Register custom locator for platform"""
        pass
    
    @abstractmethod
    def unregister_locator(self, platform_name: str) -> bool:
        """Unregister custom locator for platform"""
        pass
    
    @abstractmethod
    def get_supported_platforms(self) -> list[str]:
        """Get list of supported platforms"""
        pass
    
    @abstractmethod
    def is_platform_supported(self, platform_name: str) -> bool:
        """Check if platform is supported"""
        pass
    
    @abstractmethod
    def get_locator_info(self, platform_name: str) -> Dict[str, Any]:
        """Get information about locator for platform"""
        pass 