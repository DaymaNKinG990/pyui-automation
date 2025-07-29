import platform

from .base_backend import BaseBackend
from .windows import WindowsBackend
try:
    from .linux import LinuxBackend
except ImportError:
    LinuxBackend = None

try:
    from .macos import MacOSBackend
except ImportError:
    MacOSBackend = None


def get_backend() -> BaseBackend:
    """Get the appropriate backend for the current platform"""
    system = platform.system().lower()
    
    if system == 'windows':
        backend = WindowsBackend()
        return backend  # type: ignore[return-value]
    elif system == 'linux':
        if LinuxBackend is not None:
            backend = LinuxBackend()
            return backend  # type: ignore[no-any-return]
        else:
            raise NotImplementedError("Linux backend not available")
    elif system == 'darwin':
        if MacOSBackend is not None:
            backend = MacOSBackend()
            return backend  # type: ignore[no-any-return]
        else:
            raise NotImplementedError("macOS backend not available")
    else:
        raise NotImplementedError(f"Platform {system} is not supported")
