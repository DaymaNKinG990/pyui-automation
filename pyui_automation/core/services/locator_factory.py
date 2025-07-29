"""
Locator Factory - handles locator creation for different platforms.

Responsible for:
- Locator creation
- Platform-specific locator mapping
- Locator registration
"""

from typing import Dict, Type, Any, List
from logging import getLogger

from ...locators.windows import WindowsLocator
from ...locators.linux import LinuxLocator
from ...locators.macos import MacOSLocator
from ...locators.interfaces import IBackendForLocator
from ..interfaces.ilocator_factory import ILocatorFactory


class LocatorFactory(ILocatorFactory):
    """Factory for creating platform-specific locators"""
    
    def __init__(self) -> None:
        self._logger = getLogger(__name__)
        self._locators: Dict[str, Type] = {
            'windows': WindowsLocator,
            'linux': LinuxLocator,
            'darwin': MacOSLocator,  # macOS
        }
        self._custom_locators: Dict[str, Type] = {}
    
    def create_locator(self, platform_name: str, backend: IBackendForLocator) -> Any:
        """Create locator for specified platform"""
        try:
            # Check custom locators first
            if platform_name in self._custom_locators:
                locator_class = self._custom_locators[platform_name]
                self._logger.info(f"Using custom locator for {platform_name}")
            elif platform_name in self._locators:
                locator_class = self._locators[platform_name]
                self._logger.info(f"Using built-in locator for {platform_name}")
            else:
                raise RuntimeError(f"Unsupported platform for locator: {platform_name}")
            
            locator = locator_class(backend)
            self._logger.info(f"Created locator for platform: {platform_name}")
            return locator
            
        except Exception as e:
            self._logger.error(f"Failed to create locator for platform {platform_name}: {e}")
            raise
    
    def register_locator(self, platform_name: str, locator_class: Type) -> None:
        """Register custom locator for platform"""
        try:
            self._custom_locators[platform_name] = locator_class
            self._logger.info(f"Registered custom locator for platform: {platform_name}")
        except Exception as e:
            self._logger.error(f"Failed to register locator for {platform_name}: {e}")
            raise
    
    def unregister_locator(self, platform_name: str) -> bool:
        """Unregister custom locator for platform"""
        try:
            if platform_name in self._custom_locators:
                del self._custom_locators[platform_name]
                self._logger.info(f"Unregistered custom locator for platform: {platform_name}")
                return True
            return False
        except Exception as e:
            self._logger.error(f"Failed to unregister locator for {platform_name}: {e}")
            return False
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        all_platforms = set(self._locators.keys()) | set(self._custom_locators.keys())
        return list(all_platforms)
    
    def is_platform_supported(self, platform_name: str) -> bool:
        """Check if platform is supported"""
        return platform_name in self._locators or platform_name in self._custom_locators
    
    def get_locator_info(self, platform_name: str) -> Dict[str, Any]:
        """Get information about locator for platform"""
        try:
            if platform_name in self._custom_locators:
                locator_class = self._custom_locators[platform_name]
                locator_type = "custom"
            elif platform_name in self._locators:
                locator_class = self._locators[platform_name]
                locator_type = "built-in"
            else:
                return {"supported": False}
            
            return {
                "supported": True,
                "type": locator_type,
                "class": locator_class.__name__,
                "module": locator_class.__module__
            }
        except Exception as e:
            self._logger.error(f"Failed to get locator info for {platform_name}: {e}")
            return {"supported": False, "error": str(e)} 