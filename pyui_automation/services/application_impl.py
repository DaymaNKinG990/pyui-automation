from .application import ApplicationService
from typing import Any, Optional

class ApplicationServiceImpl(ApplicationService):
    def __init__(self, app_manager):
        self.app_manager = app_manager

    def launch_application(self, path: str, args: Optional[list] = None, cwd: Optional[str] = None, env: Optional[dict] = None) -> Any:
        return self.app_manager.launch_application(path, args, cwd, env)

    def attach_to_application(self, pid: int) -> Optional[Any]:
        return self.app_manager.attach_to_application(pid)

    def get_current_application(self) -> Optional[Any]:
        return self.app_manager.get_current_application() 