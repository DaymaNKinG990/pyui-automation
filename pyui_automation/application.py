import subprocess
import time
import psutil
import platform
from typing import Optional, Dict, List
import os

class Application:
    """Class for managing desktop applications"""

    def __init__(self, path: str = None, process: psutil.Process = None):
        self.path = path
        self.process = process
        self.platform = platform.system().lower()
        self._window_handle = None

    @classmethod
    def launch(cls, path: str, args: List[str] = None, cwd: str = None,
               env: Dict[str, str] = None) -> 'Application':
        """Launch a new application"""
        if args is None:
            args = []
        
        try:
            process = subprocess.Popen(
                [path] + args,
                cwd=cwd,
                env=env or os.environ,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            return cls(path=path, process=psutil.Process(process.pid))
        except Exception as e:
            raise RuntimeError(f"Failed to launch application: {e}")

    @classmethod
    def attach(cls, process_name: str) -> Optional['Application']:
        """Attach to an existing application process"""
        for proc in psutil.process_iter(['name', 'exe']):
            try:
                if proc.info['name'] == process_name or \
                   (proc.info['exe'] and os.path.basename(proc.info['exe']) == process_name):
                    return cls(path=proc.info['exe'], process=proc)
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue
        return None

    def terminate(self, timeout: int = 5):
        """Terminate the application"""
        if self.process:
            self.process.terminate()
            try:
                self.process.wait(timeout=timeout)
            except psutil.TimeoutExpired:
                self.process.kill()

    def is_running(self) -> bool:
        """Check if the application is running"""
        if self.process:
            return self.process.is_running()
        return False

    def get_memory_usage(self) -> float:
        """Get application memory usage in MB"""
        if self.process:
            return self.process.memory_info().rss / (1024 * 1024)
        return 0.0

    def get_cpu_usage(self) -> float:
        """Get application CPU usage percentage"""
        if self.process:
            return self.process.cpu_percent(interval=0.1)
        return 0.0

    def get_child_processes(self) -> List[psutil.Process]:
        """Get list of child processes"""
        if self.process:
            return self.process.children(recursive=True)
        return []

    def wait_for_window(self, title: str = None, timeout: int = 10) -> bool:
        """Wait for application window to appear"""
        end_time = time.time() + timeout
        while time.time() < end_time:
            if self._find_window(title):
                return True
            time.sleep(0.1)
        return False

    def _find_window(self, title: str = None) -> bool:
        """Find application window"""
        if self.platform == 'windows':
            import win32gui
            def callback(hwnd, ctx):
                if win32gui.IsWindowVisible(hwnd):
                    window_title = win32gui.GetWindowText(hwnd)
                    if title is None or title in window_title:
                        try:
                            _, pid = win32gui.GetWindowThreadProcessId(hwnd)
                            if pid == self.process.pid:
                                self._window_handle = hwnd
                                return False
                        except Exception:
                            pass
                return True
            win32gui.EnumWindows(callback, None)
            return self._window_handle is not None
        
        elif self.platform == 'linux':
            import Xlib.display
            display = Xlib.display.Display()
            root = display.screen().root
            window_ids = root.get_full_property(
                display.intern_atom('_NET_CLIENT_LIST'),
                display.intern_atom('WINDOW')
            ).value
            for window_id in window_ids:
                window = display.create_resource_object('window', window_id)
                try:
                    window_pid = window.get_full_property(
                        display.intern_atom('_NET_WM_PID'),
                        display.intern_atom('CARDINAL')
                    )
                    if window_pid and window_pid.value[0] == self.process.pid:
                        if title is None or title in window.get_wm_name():
                            self._window_handle = window_id
                            return True
                except Exception:
                    continue
            return False
        
        elif self.platform == 'darwin':
            from AppKit import NSWorkspace
            workspace = NSWorkspace.sharedWorkspace()
            for app in workspace.runningApplications():
                if app.processIdentifier() == self.process.pid:
                    if title is None or title in str(app.localizedName()):
                        return True
            return False
        
        return False
