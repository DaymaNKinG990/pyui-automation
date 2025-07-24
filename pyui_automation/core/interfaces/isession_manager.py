"""
ISessionManager interface - defines contract for session management.

Responsible for:
- Session lifecycle management
- Session configuration
- Session state management
"""

from abc import ABC, abstractmethod
from typing import Optional, TYPE_CHECKING, Any

if TYPE_CHECKING:
    from ..session import AutomationSession


class ISessionManager(ABC):
    """Interface for session management"""
    
    @abstractmethod
    def create_session(self, backend: Any, locator: Any, session_id: Optional[str] = None) -> "AutomationSession":
        """Create new automation session"""
        pass
    
    @abstractmethod
    def get_session(self, session_id: str) -> Optional["AutomationSession"]:
        """Get session by ID"""
        pass
    
    @abstractmethod
    def close_session(self, session_id: str) -> None:
        """Close session by ID"""
        pass
    
    @abstractmethod
    def cleanup_all_sessions(self) -> None:
        """Cleanup all sessions"""
        pass 