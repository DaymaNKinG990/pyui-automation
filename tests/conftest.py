"""
Common fixtures for pyui-automation tests
"""
import pytest
import numpy as np
from unittest.mock import Mock

from pyui_automation.core.interfaces import IBackend, IApplication, ISessionManager
from pyui_automation.elements.base_element import BaseElement


# pytest-mock provides the mocker fixture automatically
# No need to define it manually


@pytest.fixture
def mock_backend(mocker):
    """Mock backend for testing"""
    backend = Mock(spec=IBackend)
    backend.initialize.return_value = None
    backend.is_initialized.return_value = True
    backend.cleanup.return_value = None
    backend.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
    backend.get_screen_size.return_value = (1920, 1080)
    backend.get_active_window.return_value = 12345
    backend.get_window_handles.return_value = [12345, 67890]
    backend.get_window_title.return_value = "Test Window"
    backend.get_window_bounds.return_value = (0, 0, 800, 600)
    return backend


@pytest.fixture
def mock_locator():
    """Mock locator for testing"""
    locator = Mock()
    locator.find_element.return_value = Mock(spec=BaseElement)
    locator.find_elements.return_value = [Mock(spec=BaseElement)]
    locator.wait_for_element.return_value = Mock(spec=BaseElement)
    locator.is_element_present.return_value = True
    locator.get_element_count.return_value = 1
    return locator


@pytest.fixture
def mock_application(mocker):
    """Mock application for testing"""
    app = Mock(spec=IApplication)
    app.process_id = 12345
    app.name = "test_app"
    app.path = "/path/to/test_app"
    app.is_running.return_value = True
    app.memory_info = 1024.5
    app.cpu_usage = 5.2
    return app


@pytest.fixture
def mock_session_manager(mocker):
    """Mock session manager for testing"""
    session_manager = Mock(spec=ISessionManager)
    session_manager.create_session.return_value = "test_session_id"
    session_manager.get_session.return_value = Mock()
    session_manager.cleanup_all_sessions.return_value = None
    return session_manager


@pytest.fixture
def mock_element():
    """Mock UI element for testing"""
    element = Mock(spec=BaseElement)
    element.id = "test_element"
    element.name = "Test Element"
    element.tag_name = "button"
    element.text = "Click me"
    element.is_visible.return_value = True
    element.is_enabled.return_value = True
    element.get_attribute.return_value = "test_value"
    element.click.return_value = None
    element.send_keys.return_value = None
    element.clear.return_value = None
    element.get_rect.return_value = (10, 20, 100, 50)
    return element


@pytest.fixture
def sample_image():
    """Sample image for testing"""
    return np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)


@pytest.fixture
def temp_file(tmp_path):
    """Temporary file for testing"""
    file_path = tmp_path / "test_file.txt"
    file_path.write_text("test content")
    return file_path


@pytest.fixture
def sample_config():
    """Sample configuration for testing"""
    return {
        "timeout": 30,
        "retry_attempts": 3,
        "screenshot_dir": "/tmp/screenshots",
        "log_level": "INFO",
        "platform": "windows"
    }


@pytest.fixture
def mock_process(mocker):
    """Mock process for testing"""
    process = Mock()
    process.pid = 12345
    process.name.return_value = "test_process"
    process.is_running.return_value = True
    process.terminate.return_value = None
    process.kill.return_value = None
    
    # Mock memory_info
    memory_info = Mock()
    memory_info.rss = 1024 * 1024 * 100  # 100MB
    process.memory_info.return_value = memory_info
    
    return process


@pytest.fixture
def mock_ocr_result():
    """Mock OCR result for testing"""
    return [
        {
            "text": "Hello World",
            "confidence": 0.95,
            "bbox": [[10, 10], [100, 10], [100, 30], [10, 30]]
        },
        {
            "text": "Test Button",
            "confidence": 0.88,
            "bbox": [[50, 50], [150, 50], [150, 80], [50, 80]]
        }
    ]


@pytest.fixture
def mock_performance_data():
    """Mock performance data for testing"""
    return {
        "cpu_usage": [5.2, 6.1, 4.8, 5.9],
        "memory_usage": [1024.5, 1028.2, 1022.1, 1026.8],
        "response_times": [0.1, 0.15, 0.12, 0.18],
        "timestamps": [1000, 2000, 3000, 4000]
    }


@pytest.fixture
def mock_visual_baseline():
    """Mock visual baseline for testing"""
    return {
        "baseline_image": np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8),
        "threshold": 0.95,
        "regions": [(10, 10, 50, 50), (60, 60, 100, 100)],
        "metadata": {
            "created_at": "2024-01-01T00:00:00Z",
            "version": "1.0.0",
            "platform": "windows"
        }
    } 