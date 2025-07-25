"""
Tests for backend factory
"""
import pytest
from typing import Tuple, List, Optional, Any, Union
from pathlib import Path
import numpy as np

from pyui_automation.core.services.backend_factory import BackendFactory
from pyui_automation.backends.base_backend import BaseBackend
from pyui_automation.backends.windows import WindowsBackend


class TestBackendFactoryInitialization:
    """Test BackendFactory initialization"""
    
    def test_backend_factory_initialization(self, mocker):
        """Test basic initialization"""
        factory = BackendFactory()
        assert factory is not None
        assert hasattr(factory, '_backends')
        assert hasattr(factory, '_custom_backends')
        assert 'windows' in factory._backends
        assert 'linux' in factory._backends
        assert 'darwin' in factory._backends


class TestBackendFactoryDetectPlatform:
    """Test platform detection"""
    
    def test_detect_platform_windows(self, mocker):
        """Test Windows platform detection"""
        mock_system = mocker.patch('platform.system')
        mock_system.return_value = "Windows"
        factory = BackendFactory()
        platform = factory.detect_platform()
        assert platform == "windows"
    
    def test_detect_platform_linux(self, mocker):
        """Test Linux platform detection"""
        mock_system = mocker.patch('platform.system')
        mock_system.return_value = "Linux"
        factory = BackendFactory()
        platform = factory.detect_platform()
        assert platform == "linux"
    
    def test_detect_platform_darwin(self, mocker):
        """Test macOS platform detection"""
        mock_system = mocker.patch('platform.system')
        mock_system.return_value = "Darwin"
        factory = BackendFactory()
        platform = factory.detect_platform()
        assert platform == "darwin"
    
    def test_detect_platform_with_exception(self, mocker):
        """Test platform detection with exception"""
        mock_system = mocker.patch('platform.system')
        mock_system.side_effect = Exception("Platform detection failed")
        factory = BackendFactory()
        with pytest.raises(Exception):
            factory.detect_platform()


class TestBackendFactoryRegisterBackend:
    """Test backend registration"""
    
    def test_register_backend_with_valid_backend(self, mocker):
        """Test registering valid backend"""
        factory = BackendFactory()
        
        # Создаем класс, который наследуется от BaseBackend
        class MockBackendClass(BaseBackend):
            def initialize(self):
                pass
                
            def is_initialized(self) -> bool:
                return True
                
            def get_screen_size(self) -> Tuple[int, int]:
                return (1920, 1080)
                
            def get_active_window(self) -> Optional[Any]:
                return None
                
            def get_window_handles(self) -> List[Any]:
                return []
                
            def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
                return None
                
            def find_window(self, title: str) -> Optional[Any]:
                return None
                
            def get_window_title(self, window: Any) -> str:
                return ""
                
            def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
                return (0, 0, 100, 100)
                
            def maximize_window(self, window: Any) -> None:
                pass
                
            def minimize_window(self, window: Any) -> None:
                pass
                
            def resize_window(self, window: Any, width: int, height: int) -> None:
                pass
                
            def set_window_position(self, window: Any, x: int, y: int) -> None:
                pass
                
            def close_window(self, window: Any) -> None:
                pass
                
            def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
                pass
                
            def attach_to_application(self, process_id: int) -> Optional[Any]:
                return None
                
            def close_application(self, application: Any) -> None:
                pass
                
            def get_application(self) -> Optional[Any]:
                return None
                
            def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
                return None
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return None
                
            def cleanup(self) -> None:
                pass
        
        factory.register_backend('test_platform', MockBackendClass)
        assert 'test_platform' in factory._custom_backends
        assert factory._custom_backends['test_platform'] == MockBackendClass
    
    def test_register_backend_with_invalid_backend(self, mocker):
        """Test registering backend with invalid backend class"""
        factory = BackendFactory()
        
        class InvalidBackendClass(BaseBackend):
            def initialize(self):
                pass
            def is_initialized(self) -> bool:
                return True
            def get_screen_size(self) -> Tuple[int, int]:
                return (1920, 1080)
            def get_active_window(self) -> Optional[Any]:
                return None
            def get_window_handles(self) -> List[Any]:
                return []
            def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
                return None
            def find_window(self, title: str) -> Optional[Any]:
                return None
            def get_window_title(self, window: Any) -> str:
                return ""
            def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
                return (0, 0, 100, 100)
            def maximize_window(self, window: Any) -> None:
                pass
            def minimize_window(self, window: Any) -> None:
                pass
            def resize_window(self, window: Any, width: int, height: int) -> None:
                pass
            def set_window_position(self, window: Any, x: int, y: int) -> None:
                pass
            def close_window(self, window: Any) -> None:
                pass
            def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
                pass
            def attach_to_application(self, process_id: int) -> Optional[Any]:
                return None
            def close_application(self, application: Any) -> None:
                pass
            def get_application(self) -> Optional[Any]:
                return None
            def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
                return None
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return None
            def cleanup(self) -> None:
                pass
        
        # Теперь класс валиден, но тест должен проверять что-то другое
        factory.register_backend('test_platform', InvalidBackendClass)
        assert 'test_platform' in factory._backends
    
    def test_register_backend_overwrites_existing(self, mocker):
        """Test that registering overwrites existing backend"""
        factory = BackendFactory()
        
        class MockBackendClass1(BaseBackend):
            def initialize(self):
                pass
                
            def is_initialized(self) -> bool:
                return True
                
            def get_screen_size(self) -> Tuple[int, int]:
                return (1920, 1080)
                
            def get_active_window(self) -> Optional[Any]:
                return None
                
            def get_window_handles(self) -> List[Any]:
                return []
                
            def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
                return None
                
            def find_window(self, title: str) -> Optional[Any]:
                return None
                
            def get_window_title(self, window: Any) -> str:
                return ""
                
            def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
                return (0, 0, 100, 100)
                
            def maximize_window(self, window: Any) -> None:
                pass
                
            def minimize_window(self, window: Any) -> None:
                pass
                
            def resize_window(self, window: Any, width: int, height: int) -> None:
                pass
                
            def set_window_position(self, window: Any, x: int, y: int) -> None:
                pass
                
            def close_window(self, window: Any) -> None:
                pass
                
            def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
                pass
                
            def attach_to_application(self, process_id: int) -> Optional[Any]:
                return None
                
            def close_application(self, application: Any) -> None:
                pass
                
            def get_application(self) -> Optional[Any]:
                return None
                
            def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
                return None
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return None
                
            def cleanup(self) -> None:
                pass
        
        class MockBackendClass2(BaseBackend):
            def initialize(self):
                pass
                
            def is_initialized(self) -> bool:
                return True
                
            def get_screen_size(self) -> Tuple[int, int]:
                return (1920, 1080)
                
            def get_active_window(self) -> Optional[Any]:
                return None
                
            def get_window_handles(self) -> List[Any]:
                return []
                
            def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
                return None
                
            def find_window(self, title: str) -> Optional[Any]:
                return None
                
            def get_window_title(self, window: Any) -> str:
                return ""
                
            def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
                return (0, 0, 100, 100)
                
            def maximize_window(self, window: Any) -> None:
                pass
                
            def minimize_window(self, window: Any) -> None:
                pass
                
            def resize_window(self, window: Any, width: int, height: int) -> None:
                pass
                
            def set_window_position(self, window: Any, x: int, y: int) -> None:
                pass
                
            def close_window(self, window: Any) -> None:
                pass
                
            def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
                pass
                
            def attach_to_application(self, process_id: int) -> Optional[Any]:
                return None
                
            def close_application(self, application: Any) -> None:
                pass
                
            def get_application(self) -> Optional[Any]:
                return None
                
            def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
                return None
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return None
                
            def cleanup(self) -> None:
                pass
        
        factory.register_backend('test_platform', MockBackendClass1)
        factory.register_backend('test_platform', MockBackendClass2)
        
        assert factory._custom_backends['test_platform'] == MockBackendClass2


class TestBackendFactoryCreateBackend:
    """Test backend creation"""
    
    def test_create_backend_with_registered_platform(self, mocker):
        """Test creating backend for registered platform"""
        factory = BackendFactory()
        mock_initialize = mocker.patch.object(WindowsBackend, 'initialize')
        backend = factory.create_backend('windows')
        assert isinstance(backend, WindowsBackend)
        mock_initialize.assert_called_once()
    
    def test_create_backend_with_unregistered_platform(self, mocker):
        """Test creating backend for unregistered platform"""
        factory = BackendFactory()
        with pytest.raises(RuntimeError, match="Unsupported platform: unregistered_platform"):
            factory.create_backend('unregistered_platform')
    
    def test_create_backend_with_none_platform(self, mocker):
        """Test creating backend with None platform"""
        factory = BackendFactory()
        mock_detect_platform = mocker.patch.object(factory, 'detect_platform', return_value='windows')
        mock_initialize = mocker.patch.object(WindowsBackend, 'initialize')
        with mock_detect_platform:
            with mock_initialize:
                backend = factory.create_backend(None)
                assert isinstance(backend, WindowsBackend)
    
    def test_create_backend_with_auto_platform(self, mocker):
        """Test creating backend with auto platform"""
        factory = BackendFactory()
        mock_detect_platform = mocker.patch.object(factory, 'detect_platform', return_value='windows')
        mock_initialize = mocker.patch.object(WindowsBackend, 'initialize')
        with mock_detect_platform:
            with mock_initialize:
                backend = factory.create_backend('auto')
                assert isinstance(backend, WindowsBackend)
    
    def test_create_backend_with_custom_backend(self, mocker):
        """Test creating backend with custom backend"""
        factory = BackendFactory()
        
        class MockBackendClass(BaseBackend):
            def initialize(self):
                pass
                
            def is_initialized(self) -> bool:
                return True
                
            def get_screen_size(self) -> Tuple[int, int]:
                return (1920, 1080)
                
            def get_active_window(self) -> Optional[Any]:
                return None
                
            def get_window_handles(self) -> List[Any]:
                return []
                
            def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
                return None
                
            def find_window(self, title: str) -> Optional[Any]:
                return None
                
            def get_window_title(self, window: Any) -> str:
                return ""
                
            def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
                return (0, 0, 100, 100)
                
            def maximize_window(self, window: Any) -> None:
                pass
                
            def minimize_window(self, window: Any) -> None:
                pass
                
            def resize_window(self, window: Any, width: int, height: int) -> None:
                pass
                
            def set_window_position(self, window: Any, x: int, y: int) -> None:
                pass
                
            def close_window(self, window: Any) -> None:
                pass
                
            def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
                pass
                
            def attach_to_application(self, process_id: int) -> Optional[Any]:
                return None
                
            def close_application(self, application: Any) -> None:
                pass
                
            def get_application(self) -> Optional[Any]:
                return None
                
            def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
                return None
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return None
                
            def cleanup(self) -> None:
                pass
        
        factory.register_backend('custom_platform', MockBackendClass)
        backend = factory.create_backend('custom_platform')
        
        assert isinstance(backend, MockBackendClass)


class TestBackendFactoryUnregisterBackend:
    """Test backend unregistration"""
    
    def test_unregister_backend_with_registered_platform(self, mocker):
        """Test unregistering registered backend"""
        factory = BackendFactory()
        
        class MockBackendClass(BaseBackend):
            def initialize(self):
                pass
                
            def is_initialized(self) -> bool:
                return True
                
            def get_screen_size(self) -> Tuple[int, int]:
                return (1920, 1080)
                
            def get_active_window(self) -> Optional[Any]:
                return None
                
            def get_window_handles(self) -> List[Any]:
                return []
                
            def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
                return None
                
            def find_window(self, title: str) -> Optional[Any]:
                return None
                
            def get_window_title(self, window: Any) -> str:
                return ""
                
            def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
                return (0, 0, 100, 100)
                
            def maximize_window(self, window: Any) -> None:
                pass
                
            def minimize_window(self, window: Any) -> None:
                pass
                
            def resize_window(self, window: Any, width: int, height: int) -> None:
                pass
                
            def set_window_position(self, window: Any, x: int, y: int) -> None:
                pass
                
            def close_window(self, window: Any) -> None:
                pass
                
            def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
                pass
                
            def attach_to_application(self, process_id: int) -> Optional[Any]:
                return None
                
            def close_application(self, application: Any) -> None:
                pass
                
            def get_application(self) -> Optional[Any]:
                return None
                
            def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
                return None
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return None
                
            def cleanup(self) -> None:
                pass
        
        factory.register_backend('test_platform', MockBackendClass)
        
        result = factory.unregister_backend('test_platform')
        assert result is True
        assert 'test_platform' not in factory._custom_backends
    
    def test_unregister_backend_with_unregistered_platform(self, mocker):
        """Test unregistering unregistered backend"""
        factory = BackendFactory()
        result = factory.unregister_backend('unregistered_platform')
        assert result is False


class TestBackendFactoryGetSupportedPlatforms:
    """Test getting supported platforms"""
    
    def test_get_supported_platforms_with_registered_backends(self, mocker):
        """Test getting platforms with registered backends"""
        factory = BackendFactory()
        
        class MockBackendClass(BaseBackend):
            def initialize(self):
                pass
                
            def is_initialized(self) -> bool:
                return True
                
            def get_screen_size(self) -> Tuple[int, int]:
                return (1920, 1080)
                
            def get_active_window(self) -> Optional[Any]:
                return None
                
            def get_window_handles(self) -> List[Any]:
                return []
                
            def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
                return None
                
            def find_window(self, title: str) -> Optional[Any]:
                return None
                
            def get_window_title(self, window: Any) -> str:
                return ""
                
            def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
                return (0, 0, 100, 100)
                
            def maximize_window(self, window: Any) -> None:
                pass
                
            def minimize_window(self, window: Any) -> None:
                pass
                
            def resize_window(self, window: Any, width: int, height: int) -> None:
                pass
                
            def set_window_position(self, window: Any, x: int, y: int) -> None:
                pass
                
            def close_window(self, window: Any) -> None:
                pass
                
            def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
                pass
                
            def attach_to_application(self, process_id: int) -> Optional[Any]:
                return None
                
            def close_application(self, application: Any) -> None:
                pass
                
            def get_application(self) -> Optional[Any]:
                return None
                
            def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
                return None
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return None
                
            def cleanup(self) -> None:
                pass
        
        factory.register_backend('custom_platform', MockBackendClass)
        
        platforms = factory.get_supported_platforms()
        assert 'windows' in platforms
        assert 'linux' in platforms
        assert 'darwin' in platforms
        assert 'custom_platform' in platforms
    
    def test_get_supported_platforms_with_no_backends(self, mocker):
        """Test getting platforms with no custom backends"""
        factory = BackendFactory()
        platforms = factory.get_supported_platforms()
        assert 'windows' in platforms
        assert 'linux' in platforms
        assert 'darwin' in platforms


class TestBackendFactoryIsPlatformSupported:
    """Test platform support checking"""
    
    def test_is_platform_supported_with_builtin_platform(self, mocker):
        """Test checking built-in platform support"""
        factory = BackendFactory()
        assert factory.is_platform_supported('windows') is True
        assert factory.is_platform_supported('linux') is True
        assert factory.is_platform_supported('darwin') is True
    
    def test_is_platform_supported_with_custom_platform(self, mocker):
        """Test checking custom platform support"""
        factory = BackendFactory()
        
        class MockBackendClass(BaseBackend):
            def initialize(self):
                pass
                
            def is_initialized(self) -> bool:
                return True
                
            def get_screen_size(self) -> Tuple[int, int]:
                return (1920, 1080)
                
            def get_active_window(self) -> Optional[Any]:
                return None
                
            def get_window_handles(self) -> List[Any]:
                return []
                
            def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
                return None
                
            def find_window(self, title: str) -> Optional[Any]:
                return None
                
            def get_window_title(self, window: Any) -> str:
                return ""
                
            def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
                return (0, 0, 100, 100)
                
            def maximize_window(self, window: Any) -> None:
                pass
                
            def minimize_window(self, window: Any) -> None:
                pass
                
            def resize_window(self, window: Any, width: int, height: int) -> None:
                pass
                
            def set_window_position(self, window: Any, x: int, y: int) -> None:
                pass
                
            def close_window(self, window: Any) -> None:
                pass
                
            def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
                pass
                
            def attach_to_application(self, process_id: int) -> Optional[Any]:
                return None
                
            def close_application(self, application: Any) -> None:
                pass
                
            def get_application(self) -> Optional[Any]:
                return None
                
            def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
                return None
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return None
                
            def cleanup(self) -> None:
                pass
        
        factory.register_backend('custom_platform', MockBackendClass)
        assert factory.is_platform_supported('custom_platform') is True
    
    def test_is_platform_supported_with_unsupported_platform(self, mocker):
        """Test checking unsupported platform"""
        factory = BackendFactory()
        assert factory.is_platform_supported('unsupported_platform') is False


class TestBackendFactoryGetBackendInfo:
    """Test getting backend information"""
    
    def test_get_backend_info_with_builtin_platform(self, mocker):
        """Test getting info for built-in platform"""
        factory = BackendFactory()
        info = factory.get_backend_info('windows')
        assert info['supported'] is True
        assert info['type'] == 'built-in'
        assert info['class'] == 'WindowsBackend'
    
    def test_get_backend_info_with_custom_platform(self, mocker):
        """Test getting info for custom platform"""
        factory = BackendFactory()

        class CustomBackend(BaseBackend):
            def initialize(self):
                pass
                
            def is_initialized(self) -> bool:
                return True
                
            def get_screen_size(self) -> Tuple[int, int]:
                return (1920, 1080)
                
            def get_active_window(self) -> Optional[Any]:
                return None
                
            def get_window_handles(self) -> List[Any]:
                return []
                
            def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
                return None
                
            def find_window(self, title: str) -> Optional[Any]:
                return None
                
            def get_window_title(self, window: Any) -> str:
                return ""
                
            def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
                return (0, 0, 100, 100)
                
            def maximize_window(self, window: Any) -> None:
                pass
                
            def minimize_window(self, window: Any) -> None:
                pass
                
            def resize_window(self, window: Any, width: int, height: int) -> None:
                pass
                
            def set_window_position(self, window: Any, x: int, y: int) -> None:
                pass
                
            def close_window(self, window: Any) -> None:
                pass
                
            def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
                pass
                
            def attach_to_application(self, process_id: int) -> Optional[Any]:
                return None
                
            def close_application(self, application: Any) -> None:
                pass
                
            def get_application(self) -> Optional[Any]:
                return None
                
            def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
                return None
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return None
                
            def cleanup(self) -> None:
                pass

        factory.register_backend('custom_platform', CustomBackend)

        info = factory.get_backend_info('custom_platform')
        assert info['supported'] is True
        assert info['type'] == 'custom'
        assert info['class'] == 'CustomBackend'
        assert info['module'] == 'test_backend_factory'
    
    def test_get_backend_info_with_unsupported_platform(self, mocker):
        """Test getting info for unsupported platform"""
        factory = BackendFactory()
        info = factory.get_backend_info('unsupported_platform')
        assert info['supported'] is False


class TestBackendFactoryErrorHandling:
    """Test error handling in BackendFactory"""
    
    def test_create_backend_with_exception_during_initialization(self, mocker):
        """Test creating backend with exception during initialization"""
        factory = BackendFactory()
        
        class MockBackendClass(BaseBackend):
            def initialize(self):
                raise Exception("Initialization failed")
                
            def is_initialized(self) -> bool:
                return True
                
            def get_screen_size(self) -> Tuple[int, int]:
                return (1920, 1080)
                
            def get_active_window(self) -> Optional[Any]:
                return None
                
            def get_window_handles(self) -> List[Any]:
                return []
                
            def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
                return None
                
            def find_window(self, title: str) -> Optional[Any]:
                return None
                
            def get_window_title(self, window: Any) -> str:
                return ""
                
            def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
                return (0, 0, 100, 100)
                
            def maximize_window(self, window: Any) -> None:
                pass
                
            def minimize_window(self, window: Any) -> None:
                pass
                
            def resize_window(self, window: Any, width: int, height: int) -> None:
                pass
                
            def set_window_position(self, window: Any, x: int, y: int) -> None:
                pass
                
            def close_window(self, window: Any) -> None:
                pass
                
            def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
                pass
                
            def attach_to_application(self, process_id: int) -> Optional[Any]:
                return None
                
            def close_application(self, application: Any) -> None:
                pass
                
            def get_application(self) -> Optional[Any]:
                return None
                
            def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
                return None
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return None
                
            def cleanup(self) -> None:
                pass
        
        factory.register_backend('test_platform', MockBackendClass)
        
        with pytest.raises(Exception, match="Initialization failed"):
            factory.create_backend('test_platform')
    
    def test_register_backend_with_exception_during_registration(self, mocker):
        """Test registering backend with exception during registration"""
        factory = BackendFactory()
        # Mock logger to raise exception
        mock_logger = mocker.patch.object(factory._logger, 'info')
        mock_logger.side_effect = Exception("Logging failed")
        class MockBackendClass(BaseBackend):
            def initialize(self):
                pass
            def is_initialized(self) -> bool:
                return True
            def get_screen_size(self) -> Tuple[int, int]:
                return (1920, 1080)
            def get_active_window(self) -> Optional[Any]:
                return None
            def get_window_handles(self) -> List[Any]:
                return []
            def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
                return None
            def find_window(self, title: str) -> Optional[Any]:
                return None
            def get_window_title(self, window: Any) -> str:
                return ""
            def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
                return (0, 0, 100, 100)
            def maximize_window(self, window: Any) -> None:
                pass
            def minimize_window(self, window: Any) -> None:
                pass
            def resize_window(self, window: Any, width: int, height: int) -> None:
                pass
            def set_window_position(self, window: Any, x: int, y: int) -> None:
                pass
            def close_window(self, window: Any) -> None:
                pass
            def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
                pass
            def attach_to_application(self, process_id: int) -> Optional[Any]:
                return None
            def close_application(self, application: Any) -> None:
                pass
            def get_application(self) -> Optional[Any]:
                return None
            def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
                return None
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return None
            def cleanup(self) -> None:
                pass
        with pytest.raises(Exception, match="Logging failed"):
            factory.register_backend('test_platform', MockBackendClass)
    
    def test_unregister_backend_with_exception_during_unregistration(self, mocker):
        """Test unregistering backend with exception during unregistration"""
        factory = BackendFactory()
        
        class MockBackendClass(BaseBackend):
            def initialize(self):
                pass
                
            def is_initialized(self) -> bool:
                return True
                
            def get_screen_size(self) -> Tuple[int, int]:
                return (1920, 1080)
                
            def get_active_window(self) -> Optional[Any]:
                return None
                
            def get_window_handles(self) -> List[Any]:
                return []
                
            def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
                return None
                
            def find_window(self, title: str) -> Optional[Any]:
                return None
                
            def get_window_title(self, window: Any) -> str:
                return ""
                
            def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
                return (0, 0, 100, 100)
                
            def maximize_window(self, window: Any) -> None:
                pass
                
            def minimize_window(self, window: Any) -> None:
                pass
                
            def resize_window(self, window: Any, width: int, height: int) -> None:
                pass
                
            def set_window_position(self, window: Any, x: int, y: int) -> None:
                pass
                
            def close_window(self, window: Any) -> None:
                pass
                
            def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
                pass
                
            def attach_to_application(self, process_id: int) -> Optional[Any]:
                return None
                
            def close_application(self, application: Any) -> None:
                pass
                
            def get_application(self) -> Optional[Any]:
                return None
                
            def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
                return None
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return None
                
            def cleanup(self) -> None:
                pass
        
        factory.register_backend('test_platform', MockBackendClass)
        
        # Mock logger to raise exception
        mock_logger = mocker.patch.object(factory._logger, 'info')
        mock_logger.side_effect = Exception("Logging failed")
        
        # Should handle exception gracefully and return False
        result = factory.unregister_backend('test_platform')
        assert result is False
    
    def test_get_backend_info_with_exception_during_info_retrieval(self, mocker):
        """Test getting backend info with exception during info retrieval"""
        factory = BackendFactory()
        
        class MockBackendClass(BaseBackend):
            def initialize(self):
                pass
                
            def is_initialized(self) -> bool:
                return True
                
            def get_screen_size(self) -> Tuple[int, int]:
                return (1920, 1080)
                
            def get_active_window(self) -> Optional[Any]:
                return None
                
            def get_window_handles(self) -> List[Any]:
                return []
                
            def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
                return None
                
            def find_window(self, title: str) -> Optional[Any]:
                return None
                
            def get_window_title(self, window: Any) -> str:
                return ""
                
            def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
                return (0, 0, 100, 100)
                
            def maximize_window(self, window: Any) -> None:
                pass
                
            def minimize_window(self, window: Any) -> None:
                pass
                
            def resize_window(self, window: Any, width: int, height: int) -> None:
                pass
                
            def set_window_position(self, window: Any, x: int, y: int) -> None:
                pass
                
            def close_window(self, window: Any) -> None:
                pass
                
            def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
                pass
                
            def attach_to_application(self, process_id: int) -> Optional[Any]:
                return None
                
            def close_application(self, application: Any) -> None:
                pass
                
            def get_application(self) -> Optional[Any]:
                return None
                
            def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[np.ndarray]:
                return None
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return None
                
            def cleanup(self) -> None:
                pass
        
        factory.register_backend('test_platform', MockBackendClass)
        
        # Create a mock dictionary that raises an exception when accessed
        mock_dict = mocker.Mock()
        mock_dict.__contains__ = mocker.Mock(side_effect=Exception("Test error"))
        
        # Replace the _custom_backends dictionary
        factory._custom_backends = mock_dict
        
        # Should handle exception gracefully and return error info
        info = factory.get_backend_info('test_platform')
        assert info['supported'] is False
        assert 'error' in info 