"""
Pytest configuration and shared fixtures for pyui-automation tests
"""
import pytest
import tempfile
import os
import time
from pathlib import Path
from unittest.mock import Mock
from typing import Generator

from pyui_automation import PyUIAutomation


@pytest.fixture(scope="session")
def automation() -> PyUIAutomation:
    """Create a shared automation instance for the test session"""
    return PyUIAutomation()


@pytest.fixture
def mock_session() -> Mock:
    """Create a mock session for unit tests"""
    session = Mock()
    session.screenshot_service = Mock()
    session.input_service = Mock()
    session.visual_testing_service = Mock()
    session.performance_service = Mock()
    session.ocr_service = Mock()
    return session


@pytest.fixture
def mock_native_element() -> Mock:
    """Create a mock native element for unit tests"""
    element = Mock()
    element.get_attribute = Mock(return_value="test_value")
    element.set_attribute = Mock()
    element.get_property = Mock(return_value="test_property")
    element.CurrentBoundingRectangle = Mock()
    element.CurrentBoundingRectangle.left = 10
    element.CurrentBoundingRectangle.top = 20
    element.CurrentBoundingRectangle.width = 100
    element.CurrentBoundingRectangle.height = 50
    return element


@pytest.fixture
def mock_backend(mock_native_element) -> Mock:
    """Create a mock backend for unit tests"""
    backend = Mock()
    backend.find_element = Mock(return_value=mock_native_element)
    backend.find_elements = Mock(return_value=[mock_native_element])
    backend.get_active_window = Mock(return_value=mock_native_element)
    backend.capture_screenshot = Mock(return_value=None)
    return backend


@pytest.fixture
def temp_file() -> Generator[str, None, None]:
    """Create a temporary file for testing"""
    with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
        f.write("Test content for automation\nSecond line\nThird line")
        temp_path = f.name
    
    yield temp_path
    
    # Cleanup
    try:
        os.unlink(temp_path)
    except OSError:
        pass


@pytest.fixture
def temp_dir() -> Generator[str, None, None]:
    """Create a temporary directory for testing"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    
    # Cleanup
    try:
        import shutil
        shutil.rmtree(temp_dir)
    except OSError:
        pass


@pytest.fixture
def sample_image() -> Generator[str, None, None]:
    """Create a sample image file for testing"""
    # Create a simple test image using PIL
    try:
        from PIL import Image
        import numpy as np
        
        # Create a simple test image
        img_array = np.random.randint(0, 255, (100, 100, 3), dtype=np.uint8)
        img = Image.fromarray(img_array)
        
        temp_path = tempfile.mktemp(suffix='.png')
        img.save(temp_path)
        
        yield temp_path
        
        # Cleanup
        try:
            os.unlink(temp_path)
        except OSError:
            pass
    except ImportError:
        # If PIL is not available, create a dummy file
        temp_path = tempfile.mktemp(suffix='.png')
        with open(temp_path, 'w') as f:
            f.write("dummy image file")
        
        yield temp_path
        
        # Cleanup
        try:
            os.unlink(temp_path)
        except OSError:
            pass


@pytest.fixture
def mock_config() -> Mock:
    """Create a mock configuration for testing"""
    config = Mock()
    config.timeout = 10.0
    config.retry_interval = 0.1
    config.screenshot_dir = Path(tempfile.gettempdir())
    config.visual_baseline_dir = Path(tempfile.gettempdir())
    config.performance_output_dir = Path(tempfile.gettempdir())
    config.log_level = "INFO"
    return config


@pytest.fixture
def mock_logger() -> Mock:
    """Create a mock logger for testing"""
    logger = Mock()
    logger.debug = Mock()
    logger.info = Mock()
    logger.warning = Mock()
    logger.error = Mock()
    logger.critical = Mock()
    return logger


@pytest.fixture
def sample_text_data() -> str:
    """Provide sample text data for testing"""
    return """This is a sample text for testing automation.
It contains multiple lines and various characters.
Special chars: éñüßáö!@#$%^&*()
Numbers: 1234567890
Mixed content: Test123!@#"""


@pytest.fixture
def sample_html_data() -> str:
    """Provide sample HTML data for testing"""
    return """<!DOCTYPE html>
<html>
<head>
    <title>Test Page</title>
    <meta charset="UTF-8">
</head>
<body>
    <h1>Test Heading</h1>
    <p>This is a test paragraph.</p>
    <ul>
        <li>Item 1</li>
        <li>Item 2</li>
        <li>Item 3</li>
    </ul>
    <button id="test-button">Click me</button>
</body>
</html>"""


@pytest.fixture
def sample_json_data() -> str:
    """Provide sample JSON data for testing"""
    return """{
    "name": "Test Object",
    "id": 12345,
    "active": true,
    "tags": ["test", "automation", "json"],
    "metadata": {
        "created": "2024-01-01",
        "version": "1.0.0"
    },
    "items": [
        {"id": 1, "name": "Item 1"},
        {"id": 2, "name": "Item 2"},
        {"id": 3, "name": "Item 3"}
    ]
}"""


@pytest.fixture
def mock_element_finder(mock_native_element) -> Mock:
    """Create a mock element finder for testing"""
    finder = Mock()
    finder.find_element = Mock(return_value=mock_native_element)
    finder.find_elements = Mock(return_value=[mock_native_element])
    finder.find_child_by_property = Mock(return_value=mock_native_element)
    finder.find_children_by_property = Mock(return_value=[mock_native_element])
    finder.find_child_by_text = Mock(return_value=mock_native_element)
    finder.find_children_by_text = Mock(return_value=[mock_native_element])
    finder.find_child_by_name = Mock(return_value=mock_native_element)
    finder.find_children_by_name = Mock(return_value=[mock_native_element])
    finder.find_child_by_control_type = Mock(return_value=mock_native_element)
    finder.find_children_by_control_type = Mock(return_value=[mock_native_element])
    finder.find_child_by_automation_id = Mock(return_value=mock_native_element)
    finder.find_children_by_automation_id = Mock(return_value=[mock_native_element])
    finder.find_visible_children = Mock(return_value=[mock_native_element])
    finder.find_enabled_children = Mock(return_value=[mock_native_element])
    finder.find_child_by_predicate = Mock(return_value=mock_native_element)
    finder.find_children_by_predicate = Mock(return_value=[mock_native_element])
    finder.get_parent = Mock(return_value=mock_native_element)
    finder.get_children = Mock(return_value=[mock_native_element])
    return finder


@pytest.fixture
def mock_interaction_service() -> Mock:
    """Create a mock interaction service for testing"""
    service = Mock()
    service.click = Mock()
    service.double_click = Mock()
    service.right_click = Mock()
    service.hover = Mock()
    service.focus = Mock()
    service.send_keys = Mock()
    service.clear = Mock()
    service.select_all = Mock()
    service.copy = Mock()
    service.paste = Mock()
    service.append = Mock()
    service.scroll_into_view = Mock()
    service.drag_and_drop = Mock()
    return service


@pytest.fixture
def mock_wait_service() -> Mock:
    """Create a mock wait service for testing"""
    service = Mock()
    service.wait_until_clickable = Mock(return_value=True)
    service.wait_until_enabled = Mock(return_value=True)
    service.wait_until_checked = Mock(return_value=True)
    service.wait_until_unchecked = Mock(return_value=True)
    service.wait_until_expanded = Mock(return_value=True)
    service.wait_until_collapsed = Mock(return_value=True)
    service.wait_until_value_is = Mock(return_value=True)
    service.wait_for_condition = Mock(return_value=True)
    service.wait_for_visible = Mock(return_value=True)
    service.wait_for_enabled = Mock(return_value=True)
    return service


@pytest.fixture
def mock_state_service() -> Mock:
    """Create a mock state service for testing"""
    service = Mock()
    service.check = Mock()
    service.uncheck = Mock()
    service.toggle = Mock()
    service.expand = Mock()
    service.collapse = Mock()
    service.select_item = Mock()
    service.get_state_summary = Mock(return_value={"enabled": True, "visible": True})
    return service


@pytest.fixture
def mock_search_service(mock_native_element) -> Mock:
    """Create a mock search service for testing"""
    service = Mock()
    service.find_element = Mock(return_value=mock_native_element)
    service.find_elements = Mock(return_value=[mock_native_element])
    service.find_by_text = Mock(return_value=mock_native_element)
    service.find_by_name = Mock(return_value=mock_native_element)
    service.find_by_automation_id = Mock(return_value=mock_native_element)
    service.find_by_control_type = Mock(return_value=mock_native_element)
    return service


@pytest.fixture
def mock_screenshot_service() -> Mock:
    """Create a mock screenshot service for testing"""
    service = Mock()
    service.capture_screenshot = Mock(return_value=None)
    service.capture_element_screenshot = Mock(return_value=None)
    service.save_screenshot = Mock()
    service.load_screenshot = Mock(return_value=None)
    return service


@pytest.fixture
def mock_visual_testing_service() -> Mock:
    """Create a mock visual testing service for testing"""
    service = Mock()
    service.verify_visual = Mock(return_value=(True, 0.95))
    service.compare_images = Mock(return_value=(True, 0.95))
    service.create_baseline = Mock()
    service.update_baseline = Mock()
    return service


@pytest.fixture
def mock_performance_service() -> Mock:
    """Create a mock performance service for testing"""
    service = Mock()
    service.start_monitoring = Mock()
    service.stop_monitoring = Mock()
    service.get_metrics = Mock(return_value={"cpu": 10.0, "memory": 100.0})
    service.generate_report = Mock()
    return service


@pytest.fixture
def mock_ocr_service(mock_native_element) -> Mock:
    """Create a mock OCR service for testing"""
    service = Mock()
    service.extract_text = Mock(return_value="Extracted text")
    service.find_text = Mock(return_value=mock_native_element)
    service.verify_text = Mock(return_value=True)
    return service


@pytest.fixture
def mock_input_service() -> Mock:
    """Create a mock input service for testing"""
    service = Mock()
    service.send_keys = Mock()
    service.click = Mock()
    service.double_click = Mock()
    service.right_click = Mock()
    service.hover = Mock()
    service.drag_and_drop = Mock()
    service.scroll = Mock()
    return service


@pytest.fixture
def sample_test_data() -> dict:
    """Provide sample test data for various scenarios"""
    return {
        "valid_texts": [
            "Hello World",
            "Test automation",
            "Sample content",
            "1234567890",
            "Special chars: !@#$%^&*()",
            "Unicode: éñüßáö"
        ],
        "invalid_texts": [
            "",
            None,
            "   ",
            "\n\t\r"
        ],
        "valid_numbers": [
            0, 1, 100, -1, 3.14, 1e6
        ],
        "invalid_numbers": [
            "not a number",
            None,
            "",
            "123abc"
        ],
        "valid_booleans": [
            True, False
        ],
        "invalid_booleans": [
            "true",
            "false",
            "yes",
            "no",
            None
        ],
        "valid_paths": [
            "test.txt",
            "/path/to/file",
            "C:\\Windows\\System32",
            "relative/path/file.ext"
        ],
        "invalid_paths": [
            "",
            None,
            "file/with/invalid/chars/*?<>|",
            "path/with/../traversal"
        ]
    }


@pytest.fixture
def performance_benchmark() -> Generator[dict, None, None]:
    """Provide performance benchmarking utilities"""
    import time
    
    benchmark_data = {
        "start_time": None,
        "end_time": None,
        "duration": None,
        "memory_usage": None
    }
    
    def start_benchmark():
        benchmark_data["start_time"] = time.time()
        # Could add memory monitoring here
    
    def end_benchmark():
        benchmark_data["end_time"] = time.time()
        benchmark_data["duration"] = benchmark_data["end_time"] - benchmark_data["start_time"]
        # Could add memory monitoring here
    
    benchmark_data["start"] = start_benchmark
    benchmark_data["end"] = end_benchmark
    
    yield benchmark_data


@pytest.fixture
def error_scenarios() -> dict:
    """Provide common error scenarios for testing"""
    return {
        "network_errors": [
            "Connection refused",
            "Timeout",
            "DNS resolution failed",
            "Network unreachable"
        ],
        "file_errors": [
            "File not found",
            "Permission denied",
            "Disk full",
            "File in use"
        ],
        "validation_errors": [
            "Invalid input",
            "Required field missing",
            "Format error",
            "Value out of range"
        ],
        "system_errors": [
            "Out of memory",
            "Process killed",
            "System call failed",
            "Resource unavailable"
        ]
    }


# Pytest configuration
def pytest_configure(config):
    """Configure pytest with custom markers"""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )
    config.addinivalue_line(
        "markers", "performance: marks tests as performance tests"
    )
    config.addinivalue_line(
        "markers", "visual: marks tests as visual testing tests"
    )
    config.addinivalue_line(
        "markers", "ocr: marks tests as OCR tests"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers based on file location"""
    for item in items:
        # Add unit marker for tests in unit directory
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        
        # Add integration marker for tests in integration directory
        if "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)
        
        # Add slow marker for tests with "slow" in the name
        if "slow" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # Add performance marker for tests with "performance" in the name
        if "performance" in item.name.lower():
            item.add_marker(pytest.mark.performance)
        
        # Add visual marker for tests with "visual" in the name
        if "visual" in item.name.lower():
            item.add_marker(pytest.mark.visual)
        
        # Add ocr marker for tests with "ocr" in the name
        if "ocr" in item.name.lower():
            item.add_marker(pytest.mark.ocr)


@pytest.fixture(autouse=True)
def setup_test_environment():
    """Setup test environment before each test"""
    # Set test environment variables
    os.environ["PYUI_AUTOMATION_TEST_MODE"] = "true"
    os.environ["PYUI_AUTOMATION_LOG_LEVEL"] = "DEBUG"
    
    yield
    
    # Cleanup after test
    # Remove test environment variables
    os.environ.pop("PYUI_AUTOMATION_TEST_MODE", None)
    os.environ.pop("PYUI_AUTOMATION_LOG_LEVEL", None)


@pytest.fixture
def test_data_provider():
    """Provide test data for parameterized tests"""
    def _data_provider(data_type: str) -> list:
        """Return test data based on type"""
        data_providers = {
            "text_inputs": [
                ("simple", "Hello World"),
                ("empty", ""),
                ("whitespace", "   "),
                ("special_chars", "!@#$%^&*()"),
                ("unicode", "éñüßáö"),
                ("numbers", "1234567890"),
                ("mixed", "Test123!@#"),
                ("long", "A" * 1000),
                ("newlines", "Line1\nLine2\nLine3"),
                ("tabs", "Tab1\tTab2\tTab3")
            ],
            "file_paths": [
                ("relative", "test.txt"),
                ("absolute_windows", "C:\\test\\file.txt"),
                ("absolute_unix", "/tmp/test/file.txt"),
                ("with_spaces", "test file.txt"),
                ("with_special_chars", "test-file_123.txt"),
                ("nested", "folder/subfolder/file.txt"),
                ("deep_nested", "a/b/c/d/e/f/g/h/i/j/file.txt")
            ],
            "urls": [
                ("http", "http://example.com"),
                ("https", "https://example.com"),
                ("with_path", "https://example.com/path"),
                ("with_query", "https://example.com?param=value"),
                ("with_fragment", "https://example.com#section"),
                ("localhost", "http://localhost:8080"),
                ("ip_address", "http://192.168.1.1")
            ],
            "emails": [
                ("simple", "test@example.com"),
                ("with_name", "John Doe <john@example.com>"),
                ("with_subdomain", "test@sub.example.com"),
                ("with_plus", "test+tag@example.com"),
                ("with_dots", "test.name@example.com"),
                ("with_underscore", "test_name@example.com")
            ],
            "numbers": [
                ("integer", 123),
                ("float", 123.45),
                ("negative", -123),
                ("zero", 0),
                ("large", 999999999),
                ("small_float", 0.001),
                ("scientific", 1e6)
            ],
            "booleans": [
                ("true", True),
                ("false", False)
            ],
            "dates": [
                ("iso_date", "2024-01-01"),
                ("iso_datetime", "2024-01-01T12:00:00"),
                ("us_date", "01/01/2024"),
                ("eu_date", "01.01.2024"),
                ("with_time", "2024-01-01 12:00:00")
            ]
        }
        return data_providers.get(data_type, [])
    
    return _data_provider


@pytest.fixture
def mock_time():
    """Mock time functions for testing"""
    original_time = time.time
    original_sleep = time.sleep
    
    def mock_time_func():
        return 1234567890.0
    
    def mock_sleep_func(seconds):
        pass  # Do nothing during tests
    
    # Store original functions
    time.time = mock_time_func
    time.sleep = mock_sleep_func
    
    yield
    
    # Restore original functions
    try:
        time.time = original_time
        time.sleep = original_sleep
    except Exception:
        # Ensure functions are restored even if test fails
        pass


@pytest.fixture
def test_logger():
    """Create a test logger that captures log messages"""
    import logging
    from io import StringIO
    
    # Create a string buffer to capture log messages
    log_buffer = StringIO()
    
    # Create a handler that writes to the buffer
    handler = logging.StreamHandler(log_buffer)
    handler.setLevel(logging.DEBUG)
    
    # Create a formatter
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    
    # Create a logger
    logger = logging.getLogger('test_logger')
    logger.setLevel(logging.DEBUG)
    
    # Clear any existing handlers and add our handler
    logger.handlers.clear()
    logger.addHandler(handler)
    
    yield logger, log_buffer
    
    # Cleanup
    logger.handlers.clear()
    log_buffer.close() 