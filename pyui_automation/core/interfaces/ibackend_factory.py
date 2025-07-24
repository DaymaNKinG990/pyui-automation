"""
IBackendFactory interface - defines contract for backend factory.

Responsible for:
- Platform detection
- Backend creation
- Backend registration
"""

from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, Type

from ...backends.base_backend import BaseBackend


class IBackendFactory(ABC):
    """Interface for backend factory"""
    
    @abstractmethod
    def detect_platform(self) -> str:
        """Detect current platform"""
        pass
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """Get current platform name"""
        pass
    
    @abstractmethod
    def create_backend(self, platform_name: Optional[str] = None) -> BaseBackend:
        """Create backend for specified platform"""
        pass
    
    @abstractmethod
    def register_backend(self, platform_name: str, backend_class: Type[BaseBackend]) -> None:
        """Register custom backend for platform"""
        pass
    
    @abstractmethod
    def unregister_backend(self, platform_name: str) -> bool:
        """Unregister custom backend for platform"""
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
    def get_backend_info(self, platform_name: str) -> Dict[str, Any]:
        """Get information about backend for platform"""
        pass 