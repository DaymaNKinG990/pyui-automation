"""
IBackendApplication interface - defines contract for application operations.

Responsible for:
- Application launching
- Application attachment
- Application management
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Any, Union
from pathlib import Path


class IBackendApplication(ABC):
    """Interface for application operations"""
    
    @abstractmethod
    def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
        """Launch application"""
        pass
    
    @abstractmethod
    def attach_to_application(self, process_id: int) -> Optional[Any]:
        """Attach to existing application by process ID"""
        pass
    
    @abstractmethod
    def close_application(self, application: Any) -> None:
        """Close application"""
        pass
    
    @abstractmethod
    def get_application(self) -> Optional[Any]:
        """Get current application instance"""
        pass 