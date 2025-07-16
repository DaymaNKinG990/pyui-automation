from abc import ABC, abstractmethod
from typing import Any, Optional

class ApplicationService(ABC):
    """Abstract application service interface."""

    @abstractmethod
    def launch_application(self, path: str, args: Optional[list] = None, cwd: Optional[str] = None, env: Optional[dict] = None) -> Any:
        pass

    @abstractmethod
    def attach_to_application(self, pid: int) -> Optional[Any]:
        pass

    @abstractmethod
    def get_current_application(self) -> Optional[Any]:
        pass 