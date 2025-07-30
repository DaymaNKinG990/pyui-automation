"""
Backend Factory - handles backend creation and platform detection.

Responsible for:
- Platform detection
- Backend creation
- Backend registration
- Platform strategy pattern
"""

import platform
from typing import Dict, Type, Any, Optional, List
from logging import getLogger

from ...backends.base_backend import BaseBackend
from ...backends.windows import WindowsBackend
from ...backends.backend_utils import OcrLanguage
try:
    from ...backends.linux import LinuxBackend
except ImportError:
    LinuxBackend = None

try:
    from ...backends.macos import MacOSBackend
except ImportError:
    MacOSBackend = None
from ..interfaces.ibackend_factory import IBackendFactory


class BackendFactory(IBackendFactory):
    """Factory for creating platform-specific backends"""
    
    def __init__(self) -> None:
        self._logger = getLogger(__name__)
        self._backends: Dict[str, Type[BaseBackend]] = {
            'windows': WindowsBackend,
        }
        if LinuxBackend is not None:
            self._backends['linux'] = LinuxBackend
        if MacOSBackend is not None:
            self._backends['darwin'] = MacOSBackend
        self._custom_backends: Dict[str, Type[BaseBackend]] = {}
    
    def detect_platform(self) -> str:
        """Detect current platform"""
        try:
            system = platform.system().lower()
            if system == "darwin":
                return "darwin"  # macOS
            return system
        except Exception as e:
            self._logger.error(f"Failed to detect platform: {e}")
            raise
    
    def get_platform_name(self) -> str:
        """Get current platform name"""
        return self.detect_platform()
    
    def create_backend(self, platform_name: Optional[str] = None) -> BaseBackend:
        """Create backend for specified platform"""
        try:
            if platform_name is None or platform_name == 'auto':
                platform_name = self.detect_platform()
            if platform_name in self._custom_backends:
                backend_class = self._custom_backends[platform_name]
            elif platform_name in self._backends:
                backend_class = self._backends[platform_name]
            else:
                raise RuntimeError(f"Unsupported platform: {platform_name}")
            backend = backend_class()
            # Инициализируем backend
            backend.initialize()
            return backend
        except Exception as e:
            self._logger.error(f"Failed to create backend for platform {platform_name}: {e}")
            raise
    
    def register_backend(self, platform_name: str, backend_class: Type[BaseBackend]) -> None:
        """Register custom backend for platform"""
        try:
            if not issubclass(backend_class, BaseBackend):
                raise ValueError("Backend class must inherit from BaseBackend")
            
            self._custom_backends[platform_name] = backend_class
            self._logger.info(f"Registered custom backend for platform: {platform_name}")
        except Exception as e:
            self._logger.error(f"Failed to register backend for {platform_name}: {e}")
            raise
    
    def unregister_backend(self, platform_name: str) -> bool:
        """Unregister custom backend for platform"""
        try:
            if platform_name in self._custom_backends:
                del self._custom_backends[platform_name]
                self._logger.info(f"Unregistered custom backend for platform: {platform_name}")
                return True
            return False
        except Exception as e:
            self._logger.error(f"Failed to unregister backend for {platform_name}: {e}")
            return False
    
    def get_supported_platforms(self) -> List[str]:
        """Get list of supported platforms"""
        all_platforms = set(self._backends.keys()) | set(self._custom_backends.keys())
        return list(all_platforms)
    
    def is_platform_supported(self, platform_name: str) -> bool:
        """Check if platform is supported"""
        return platform_name in self._backends or platform_name in self._custom_backends
    
    def get_backend_info(self, platform_name: str) -> Dict[str, Any]:
        """Get information about backend for platform"""
        try:
            if platform_name in self._custom_backends:
                backend_class = self._custom_backends[platform_name]
                backend_type = "custom"
            elif platform_name in self._backends:
                backend_class = self._backends[platform_name]
                backend_type = "built-in"
            else:
                return {"supported": False}
            
            return {
                "supported": True,
                "type": backend_type,
                "class": backend_class.__name__,
                "module": backend_class.__module__
            }
        except Exception as e:
            self._logger.error(f"Failed to get backend info for {platform_name}: {e}")
            return {"supported": False, "error": str(e)}
    
    def get_supported_ocr_languages(self) -> List[str]:
        """Get list of supported OCR languages"""
        return [lang.value for lang in OcrLanguage.__members__.values()]
    
    def is_ocr_language_supported(self, language_code: str) -> bool:
        """Check if OCR language is supported"""
        return language_code in self.get_supported_ocr_languages()
    
    def get_ocr_language_name(self, language_code: str) -> str:
        """Get display name for OCR language code"""
        for lang in OcrLanguage.__members__.values():
            if lang.value == language_code:
                return lang.name.replace("_", " ").title()
        return language_code 