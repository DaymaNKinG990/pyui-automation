"""
IBackendLifecycle interface - defines contract for backend lifecycle.

Responsible for:
- Backend initialization
- Backend cleanup
- Resource management
"""

from abc import ABC, abstractmethod


class IBackendLifecycle(ABC):
    """Interface for backend lifecycle operations"""
    
    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup backend resources"""
        pass
    
    @abstractmethod
    def is_initialized(self) -> bool:
        """Check if backend is initialized"""
        pass
    
    @abstractmethod
    def initialize(self) -> None:
        """Initialize backend"""
        pass 