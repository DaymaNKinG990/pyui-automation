"""
Tests for backend factory
"""
import pytest
from typing import Tuple, List, Optional, Any, Union
from pathlib import Path
import numpy as np

from pyui_automation.core.services.backend_factory import BackendFactory
from pyui_automation.backends.base_backend import BaseBackend


@pytest.fixture
def mock_backend_class():
    """Create a mock backend class for testing"""
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
            return np.zeros((height, width, 3), dtype=np.uint8)
            
        def capture_screenshot(self) -> Optional[np.ndarray]:
            return np.zeros((1080, 1920, 3), dtype=np.uint8)
            
        def cleanup(self) -> None:
            pass
    
    return MockBackendClass


@pytest.fixture
def invalid_backend_class():
    """Create an invalid backend class for testing"""
    class InvalidBackendClass:
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
            return np.zeros((height, width, 3), dtype=np.uint8)
            
        def capture_screenshot(self) -> Optional[np.ndarray]:
            return np.zeros((1080, 1920, 3), dtype=np.uint8)
            
        def cleanup(self) -> None:
            pass
    
    return InvalidBackendClass


@pytest.fixture
def exception_backend_class():
    """Create a backend class that raises exceptions"""
    class ExceptionBackendClass(BaseBackend):
        def initialize(self):
            raise Exception("Initialization failed")
            
        def is_initialized(self) -> bool:
            return False
            
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
            return np.zeros((height, width, 3), dtype=np.uint8)
            
        def capture_screenshot(self) -> Optional[np.ndarray]:
            return np.zeros((1080, 1920, 3), dtype=np.uint8)
            
        def cleanup(self) -> None:
            pass
    
    return ExceptionBackendClass


class TestBackendFactoryInitialization:
    """Test BackendFactory initialization"""
    
    def test_backend_factory_initialization(self):
        """Test basic initialization"""
        factory = BackendFactory()
        assert factory is not None
        assert hasattr(factory, '_backends')
        assert hasattr(factory, '_custom_backends')
        assert 'windows' in factory._backends
        assert 'linux' in factory._backends or 'darwin' in factory._backends


class TestBackendFactoryDetectPlatform:
    """Test platform detection"""
    
    @pytest.mark.parametrize("system_name,expected_platform", [
        ("Windows", "windows"),
        ("Linux", "linux"),
        ("Darwin", "darwin"),
    ])
    def test_detect_platform(self, mocker, system_name, expected_platform):
        """Test platform detection for different systems"""
        mock_system = mocker.patch('platform.system')
        mock_system.return_value = system_name
        factory = BackendFactory()
        platform = factory.detect_platform()
        assert platform == expected_platform
    
    def test_detect_platform_with_exception(self, mocker):
        """Test platform detection with exception"""
        mock_system = mocker.patch('platform.system')
        mock_system.side_effect = Exception("Platform detection failed")
        factory = BackendFactory()
        with pytest.raises(Exception):
            factory.detect_platform()


class TestBackendFactoryRegisterBackend:
    """Test backend registration"""
    
    def test_register_backend_with_valid_backend(self, mock_backend_class):
        """Test registering valid backend"""
        factory = BackendFactory()
        factory.register_backend("test_platform", mock_backend_class)
        assert "test_platform" in factory._custom_backends
        assert factory._custom_backends["test_platform"] == mock_backend_class
    
    def test_register_backend_with_invalid_backend(self, invalid_backend_class):
        """Test registering invalid backend"""
        factory = BackendFactory()
        with pytest.raises(ValueError):
            factory.register_backend("test_platform", invalid_backend_class)
    
    def test_register_backend_overwrites_existing(self, mock_backend_class):
        """Test that registering overwrites existing backend"""
        factory = BackendFactory()
        
        # Register first backend
        factory.register_backend("test_platform", mock_backend_class)
        assert factory._custom_backends["test_platform"] == mock_backend_class
        
        # Create second backend class
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
                return np.zeros((height, width, 3), dtype=np.uint8)
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return np.zeros((1080, 1920, 3), dtype=np.uint8)
                
            def cleanup(self) -> None:
                pass
        
        # Register second backend (should overwrite)
        factory.register_backend("test_platform", MockBackendClass2)
        assert factory._custom_backends["test_platform"] == MockBackendClass2


class TestBackendFactoryCreateBackend:
    """Test backend creation"""
    
    def test_create_backend_with_registered_platform(self, mock_backend_class):
        """Test creating backend with registered platform"""
        factory = BackendFactory()
        factory.register_backend("test_platform", mock_backend_class)
        backend = factory.create_backend("test_platform")
        assert isinstance(backend, mock_backend_class)
    
    def test_create_backend_with_unregistered_platform(self):
        """Test creating backend with unregistered platform"""
        factory = BackendFactory()
        with pytest.raises(RuntimeError):
            factory.create_backend("nonexistent_platform")
    
    def test_create_backend_with_none_platform(self, mocker):
        """Test creating backend with None platform"""
        mock_system = mocker.patch('platform.system')
        mock_system.return_value = "Windows"
        factory = BackendFactory()
        backend = factory.create_backend(None)
        assert backend is not None
    
    def test_create_backend_with_auto_platform(self, mocker):
        """Test creating backend with auto platform"""
        mock_system = mocker.patch('platform.system')
        mock_system.return_value = "Windows"
        factory = BackendFactory()
        backend = factory.create_backend("auto")
        assert backend is not None


class TestBackendFactoryUnregisterBackend:
    """Test backend unregistration"""
    
    def test_unregister_backend_with_registered_platform(self, mock_backend_class):
        """Test unregistering registered platform"""
        factory = BackendFactory()
        factory.register_backend("test_platform", mock_backend_class)
        assert "test_platform" in factory._custom_backends
        
        result = factory.unregister_backend("test_platform")
        assert result is True
        assert "test_platform" not in factory._custom_backends
    
    def test_unregister_backend_with_unregistered_platform(self):
        """Test unregistering unregistered platform"""
        factory = BackendFactory()
        result = factory.unregister_backend("nonexistent_platform")
        assert result is False


class TestBackendFactoryGetSupportedPlatforms:
    """Test getting supported platforms"""
    
    def test_get_supported_platforms_with_registered_backends(self, mock_backend_class):
        """Test getting supported platforms with registered backends"""
        factory = BackendFactory()
        factory.register_backend("test_platform", mock_backend_class)
        
        platforms = factory.get_supported_platforms()
        assert "windows" in platforms
        assert "test_platform" in platforms
    
    def test_get_supported_platforms_with_no_backends(self):
        """Test getting supported platforms with no custom backends"""
        factory = BackendFactory()
        platforms = factory.get_supported_platforms()
        assert "windows" in platforms


class TestBackendFactoryIsPlatformSupported:
    """Test platform support checking"""
    
    def test_is_platform_supported_with_builtin_platform(self):
        """Test checking support for builtin platform"""
        factory = BackendFactory()
        assert factory.is_platform_supported("windows") is True
    
    def test_is_platform_supported_with_custom_platform(self, mock_backend_class):
        """Test checking support for custom platform"""
        factory = BackendFactory()
        factory.register_backend("test_platform", mock_backend_class)
        assert factory.is_platform_supported("test_platform") is True
    
    def test_is_platform_supported_with_unsupported_platform(self):
        """Test checking support for unsupported platform"""
        factory = BackendFactory()
        assert factory.is_platform_supported("nonexistent") is False


class TestBackendFactoryGetBackendInfo:
    """Test getting backend information"""
    
    def test_get_backend_info_with_builtin_platform(self):
        """Test getting info for builtin platform"""
        factory = BackendFactory()
        info = factory.get_backend_info("windows")
        assert info is not None
        assert info["supported"] is True
        assert info["type"] == "built-in"
        assert "class" in info
        assert "module" in info
    
    def test_get_backend_info_with_custom_platform(self, mock_backend_class):
        """Test getting info for custom platform"""
        factory = BackendFactory()
        factory.register_backend("test_platform", mock_backend_class)
        info = factory.get_backend_info("test_platform")
        assert info is not None
        assert info["supported"] is True
        assert info["type"] == "custom"
        assert "class" in info
        assert "module" in info
    
    def test_get_backend_info_with_unsupported_platform(self):
        """Test getting info for unsupported platform"""
        factory = BackendFactory()
        info = factory.get_backend_info("nonexistent")
        assert info["supported"] is False


class TestBackendFactoryErrorHandling:
    """Test error handling"""
    
    def test_create_backend_with_exception_during_initialization(self, exception_backend_class):
        """Test creating backend with exception during initialization"""
        factory = BackendFactory()
        factory.register_backend("test_platform", exception_backend_class)
        with pytest.raises(Exception):
            factory.create_backend("test_platform")
    
    def test_register_backend_with_exception_during_registration(self, mocker):
        """Test registering backend with exception during registration"""
        factory = BackendFactory()
        
        # Mock the issubclass check to raise exception
        mocker.patch('pyui_automation.core.services.backend_factory.issubclass', side_effect=Exception("Registration failed"))
        
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
                return np.zeros((height, width, 3), dtype=np.uint8)
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return np.zeros((1080, 1920, 3), dtype=np.uint8)
                
            def cleanup(self) -> None:
                pass
        
        with pytest.raises(Exception):
            factory.register_backend("test_platform", MockBackendClass)
    
    def test_unregister_backend_with_exception_during_unregistration(self, mocker):
        """Test unregister_backend with exception during unregistration"""
        factory = BackendFactory()
        
        # Create a proper backend class for testing
        class TestBackendClass(BaseBackend):
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
                return np.zeros((height, width, 3), dtype=np.uint8)
                
            def capture_screenshot(self) -> Optional[np.ndarray]:
                return np.zeros((1080, 1920, 3), dtype=np.uint8)
                
            def cleanup(self) -> None:
                pass
        
        factory.register_backend("test_platform", TestBackendClass)
        
        # Mock the unregistration to raise an exception
        mocker.patch.object(factory, '_custom_backends', side_effect=Exception("Unregistration failed"))
        
        # Should not raise exception, just return False
        result = factory.unregister_backend("test_platform")
        assert result is False
    
    def test_get_backend_info_with_exception_during_info_retrieval(self, mocker):
        """Test get_backend_info with exception during info retrieval"""
        factory = BackendFactory()
        
        # Mock the info retrieval to raise an exception
        mocker.patch.object(factory, '_get_builtin_backend_info', side_effect=Exception("Info retrieval failed"))
        
        result = factory.get_backend_info("windows")
        assert result == {"supported": False} 