"""
IBackend interface - composite interface for complete backend functionality.

This interface combines all backend capabilities through composition
of specialized interfaces, following Interface Segregation Principle.
"""

from abc import ABC
from typing import Any

from .ibackend_screen import IBackendScreen
from .ibackend_window import IBackendWindow
from .ibackend_application import IBackendApplication
from .ibackend_lifecycle import IBackendLifecycle


class IBackend(IBackendScreen, IBackendWindow, IBackendApplication, IBackendLifecycle):
    """
    Complete backend interface that combines all capabilities.
    
    This interface inherits from all specialized interfaces to provide
    a complete backend contract while maintaining interface segregation.
    """
    
    @property
    def logger(self) -> Any:
        """Get logger instance"""
        pass
    
    @property
    def application(self) -> Any:
        """Get current application instance"""
        pass 