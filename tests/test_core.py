import pytest
from unittest.mock import MagicMock, patch
import numpy as np
import comtypes.gen.UIAutomationClient as UIAutomationClient
import psutil

from pyui_automation.core import AutomationSession
from pyui_automation.core.config import AutomationConfig
from pyui_automation.core.visual import VisualTester, VisualMatcher, VisualDifference
from pyui_automation.wait import ElementWaits

@pytest.fixture
def mock_uiautomation():
    """Mock the UIAutomation COM interface"""
    mock_uia = MagicMock(spec=UIAutomationClient.IUIAutomation)
    mock_root = MagicMock()
    mock_uia.GetRootElement.return_value = mock_root
    
    mock_element = MagicMock()
    mock_element.CurrentName = "test-button"
    mock_element.CurrentAutomationId = "test-id"
    mock_element.GetCurrentPropertyValue.return_value = "test-value"
    mock_element.CurrentIsEnabled = True
    mock_element.CurrentIsOffscreen = False
    mock_element.CurrentBoundingRectangle = (0, 0, 100, 30)
    
    mock_condition = MagicMock()
    mock_uia.CreatePropertyCondition.return_value = mock_condition
    mock_root.FindFirst.return_value = mock_element
    mock_root.FindAll.return_value = [mock_element]
    
    return mock_uia

@pytest.fixture
def mock_element():
    """Create a mock element with all required methods and properties"""
    element = MagicMock()
    element.get_attribute.side_effect = lambda name: {
        "AutomationId": "test-id",
        "Name": "test-button"
    }.get(name)
    element.get_property.return_value = "test-value"
    element.text = "test text"
    element.is_enabled.return_value = True
    element.is_visible.return_value = True
    element.get_location.return_value = (0, 0)
    element.get_size.return_value = (100, 30)
    element.capture_screenshot.return_value = np.zeros((30, 100, 3), dtype=np.uint8)  # Black image
    return element

@pytest.fixture
def mock_element_waits():
    """Create mock ElementWaits"""
    waits = MagicMock()
    waits.wait_until = MagicMock()
    waits.for_element = MagicMock()
    waits.for_element_visible = MagicMock()
    waits.for_element_enabled = MagicMock()
    return waits

@pytest.fixture
def mock_windows_backend(mock_uiautomation, mock_element):
    """Create mock Windows backend"""
    with patch('comtypes.client.CreateObject', return_value=mock_uiautomation):
        with patch('pyui_automation.backends.windows.WindowsBackend') as mock_backend:
            instance = mock_backend.return_value
            instance.automation = mock_uiautomation
            instance.root = mock_uiautomation.GetRootElement()
            instance.find_element.return_value = mock_element
            instance.find_elements.return_value = [mock_element]
            instance.get_active_window.return_value = mock_element
            instance.get_window.return_value = mock_element
            instance.get_window_title.return_value = "Test Window"
            instance.take_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
            yield instance

@pytest.fixture
def mock_visual_tester():
    """Create mock visual tester"""
    with patch('pyui_automation.core.visual.VisualTester') as mock_tester:
        instance = mock_tester.return_value
        instance.capture_baseline.return_value = True
        instance.compare.return_value = (True, 0.0)
        instance.verify_hash.return_value = True
        yield instance

@pytest.fixture
def ui_automation(mock_windows_backend, mock_visual_tester, mock_element_waits):
    """Create UIAutomation instance with mock dependencies"""
    automation = AutomationSession(backend=mock_windows_backend)
    automation._visual_tester = mock_visual_tester
    automation.waits = mock_element_waits
    return automation

@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory for testing"""
    return tmp_path

def test_find_element(ui_automation):
    """Test finding an element"""
    element = ui_automation.find_element(by="name", value="test-button")
    assert element is not None
    assert element.text == "test text"

def test_find_element_with_timeout(ui_automation):
    """Test finding an element with timeout"""
    element = ui_automation.find_element(by="name", value="test-button", timeout=1)
    assert element is not None

def test_take_screenshot(ui_automation, temp_dir):
    """Test taking a screenshot"""
    screenshot_path = temp_dir / "screenshot.png"
    ui_automation.take_screenshot(screenshot_path)
    assert screenshot_path.exists()

def test_keyboard_input(ui_automation):
    """Test keyboard input"""
    element = ui_automation.find_element(by="name", value="test-button")
    ui_automation.keyboard.type_text("test")
    ui_automation.keyboard.press_key("enter")
    ui_automation.keyboard.release_key("enter")
    ui_automation.keyboard.send_keys("ctrl+a")

def test_mouse_click(ui_automation):
    """Test mouse click"""
    element = ui_automation.find_element(by="name", value="test-button")
    ui_automation.mouse.click(element)
    ui_automation.mouse.double_click(element)
    ui_automation.mouse.right_click(element)
    ui_automation.mouse.move_to(element)

def test_wait_until(ui_automation):
    """Test wait until condition"""
    result = ui_automation.wait_until(lambda: True, timeout=1)
    assert result is True

def test_init_visual_testing(ui_automation, temp_dir):
    """Test initializing visual testing"""
    ui_automation.init_visual_testing(temp_dir)
    assert ui_automation._visual_tester is not None

def test_capture_visual_baseline(ui_automation, temp_dir):
    """Test capturing visual baseline"""
    ui_automation.init_visual_testing(temp_dir)
    element = ui_automation.find_element(by="name", value="test-button")  # Используем элемент вместо строки
    result = ui_automation.capture_visual_baseline(element, "test")
    assert result is True

def test_compare_visual(ui_automation, temp_dir):
    """Test visual comparison"""
    ui_automation.init_visual_testing(temp_dir)
    element = ui_automation.find_element(by="name", value="test-button")  # Используем элемент вместо строки
    result, diff = ui_automation.compare_visual(element, "test")
    assert result is True
    assert diff == 0.0

def test_verify_visual_hash(ui_automation, temp_dir):
    """Test visual hash verification"""
    ui_automation.init_visual_testing(temp_dir)
    element = ui_automation.find_element(by="name", value="test-button")  # Используем элемент вместо строки
    result = ui_automation.verify_visual_hash(element, "test")
    assert result is True

def test_launch_application(ui_automation):
    """Test application launch"""
    mock_process = MagicMock(spec=psutil.Process)
    mock_process.pid = 12345
    mock_process.name.return_value = "test.exe"
    
    with patch('subprocess.Popen') as mock_popen, \
         patch('psutil.Process', return_value=mock_process):
        mock_popen.return_value.pid = 12345
        app = ui_automation.launch_application("test.exe")
        assert app.pid == 12345

def test_attach_to_application(ui_automation):
    """Test attaching to application"""
    mock_process = MagicMock(spec=psutil.Process)
    mock_process.pid = 12345
    mock_process.name.return_value = "test.exe"
    
    with patch('psutil.Process', return_value=mock_process):
        app = ui_automation.attach_to_application(12345)
        assert app.pid == 12345

def test_find_elements(ui_automation):
    """Test finding multiple elements"""
    elements = ui_automation.find_elements(by="name", value="test-button")
    assert len(elements) == 1

def test_get_active_window(ui_automation):
    """Test getting active window"""
    window = ui_automation.get_active_window()
    assert window is not None

def test_set_ocr_languages(ui_automation):
    """Test setting OCR languages"""
    ui_automation.set_ocr_languages(['eng'])
    assert ui_automation._ocr_languages == ['eng']

def test_performance_monitoring(ui_automation):
    """Test performance monitoring functionality"""
    ui_automation.start_performance_monitoring()
    element = ui_automation.find_element(by="name", value="test-button")
    ui_automation.mouse.click(element)
    metrics = ui_automation.stop_performance_monitoring()
    
    assert isinstance(metrics, dict)
    assert 'cpu_usage' in metrics
    assert 'memory_usage' in metrics
    assert 'response_times' in metrics

def test_measure_action_performance(ui_automation):
    def test_action():
        element = ui_automation.find_element(by="name", value="test-button")
        ui_automation.mouse.click(element)
    
    results = ui_automation.measure_action_performance(test_action, runs=3)
    
    assert isinstance(results, dict)
    assert 'min_time' in results
    assert 'max_time' in results
    assert 'avg_time' in results

def test_run_stress_test(ui_automation):
    def test_action():
        element = ui_automation.find_element(by="name", value="test-button")
        ui_automation.mouse.click(element)
    
    results = ui_automation.run_stress_test(test_action, test_duration=1)
    
    assert isinstance(results, dict)
    assert 'total_actions' in results
    assert 'success_rate' in results

def test_check_memory_leaks(ui_automation):
    def test_action():
        element = ui_automation.find_element(by="name", value="test-button")
        ui_automation.mouse.click(element)
    
    results = ui_automation.check_memory_leaks(test_action, test_iterations=3)
    
    assert isinstance(results, dict)
    assert 'memory_growth' in results
    assert 'leak_detected' in results

def test_check_accessibility(ui_automation):
    """Test accessibility checking"""
    element = ui_automation.find_element(by="name", value="test-button")
    results = ui_automation.check_accessibility(element)
    
    assert isinstance(results, list)
    for violation in results:
        assert 'rule' in violation
        assert 'severity' in violation

def test_visual_testing_workflow(ui_automation, temp_dir):
    """Test complete visual testing workflow"""
    ui_automation.init_visual_testing(temp_dir)
    element = ui_automation.find_element(by="name", value="test-button")
    
    # Capture baseline
    assert ui_automation.capture_visual_baseline(element, "test")
    
    # Compare with baseline
    match, diff = ui_automation.compare_visual(element, "test")
    assert match
    assert diff == 0.0
    
    # Verify hash
    assert ui_automation.verify_visual_hash(element, "test")

def test_visual_testing_not_initialized(ui_automation):
    """Test visual testing methods without initialization"""
    with pytest.raises(ValueError):
        ui_automation.capture_visual_baseline("test")
    with pytest.raises(ValueError):
        ui_automation.compare_visual("test")
    with pytest.raises(ValueError):
        ui_automation.verify_visual_hash("test")

def test_generate_visual_report(ui_automation, temp_dir):
    """Test generating visual report"""
    differences = [
        {
            "location": (10, 10),
            "size": (20, 20),
            "area": 400,
            "type": "changed"
        }
    ]
    ui_automation.generate_visual_report("test", differences, str(temp_dir))

def test_generate_accessibility_report(ui_automation, temp_dir):
    """Test generating accessibility report"""
    ui_automation.generate_accessibility_report(str(temp_dir))

def test_get_current_application_none(ui_automation):
    """Test getting current application when none is set"""
    app = ui_automation.get_current_application()
    assert app is None

def test_attach_to_invalid_pid(ui_automation):
    """Test attaching to invalid process ID"""
    with pytest.raises(RuntimeError):
        ui_automation.attach_to_application(999999)  # Non-existent PID

def test_performance_monitoring_not_started(ui_automation):
    """Test getting performance metrics without starting monitoring"""
    metrics = ui_automation.get_performance_metrics()
    assert metrics["cpu_usage"] == 0
    assert metrics["memory_usage"] == 0
    assert metrics["response_time"] == 0

def test_stress_test_invalid_duration(ui_automation):
    """Test running stress test with invalid duration"""
    def test_action():
        return True
    
    with pytest.raises(ValueError):
        # Изменим вызов метода, чтобы избежать дублирования аргумента duration
        ui_automation.run_stress_test(test_action, test_duration=-1)

def test_memory_leak_check_invalid_iterations(ui_automation):
    """Test memory leak check with invalid iterations"""
    def test_action():
        return True
    
    with pytest.raises(ValueError):
        # Изменим вызов метода, чтобы избежать дублирования аргумента iterations
        ui_automation.check_memory_leaks(test_action, test_iterations=0)

def test_measure_performance_invalid_runs(ui_automation):
    """Test measuring performance with invalid number of runs"""
    def test_action():
        return True
    
    with pytest.raises(ValueError):
        # Изменим имя аргумента с test_runs на iterations
        ui_automation.measure_action_performance(test_action, runs=0)

def test_ocr_invalid_language(ui_automation):
    """Test setting invalid OCR language"""
    with pytest.raises(ValueError):
        ui_automation.set_ocr_languages(["invalid_lang"])

def test_mouse_invalid_coordinates(ui_automation):
    """Test mouse move with invalid coordinates"""
    with pytest.raises(ValueError):
        ui_automation.mouse_move(-1, -1)

def test_keyboard_invalid_key(ui_automation):
    """Test pressing invalid keyboard key"""
    with pytest.raises(ValueError):
        ui_automation.press_key("invalid_key")

def test_find_element_invalid_strategy(ui_automation):
    """Test finding element with invalid strategy"""
    with pytest.raises(ValueError):
        ui_automation.find_element("invalid_strategy", "value")

def test_wait_for_invalid_timeout(ui_automation):
    """Test waiting for element with invalid timeout"""
    with pytest.raises(ValueError):
        ui_automation.wait_for("id", "test-id", timeout=-1)

# Additional mock fixtures
@pytest.fixture
def mock_backend_with_errors():
    """Mock backend that simulates various error conditions"""
    mock_backend = MagicMock()
    mock_backend.find_element.side_effect = RuntimeError("Element not found")
    mock_backend.get_active_window.side_effect = RuntimeError("No active window")
    mock_backend.take_screenshot.side_effect = RuntimeError("Screenshot failed")
    return mock_backend

@pytest.fixture
def mock_visual_tester_with_errors():
    """Mock visual tester that simulates various error conditions"""
    mock_tester = MagicMock()
    mock_tester.compare_images.side_effect = RuntimeError("Image comparison failed")
    mock_tester.compute_hash.side_effect = RuntimeError("Hash computation failed")
    return mock_tester

@pytest.fixture
def mock_process():
    """Mock process for testing process-related functionality"""
    mock_proc = MagicMock(spec=psutil.Process)
    mock_proc.cpu_percent.return_value = 10.0
    mock_proc.memory_info.return_value = MagicMock(rss=1024*1024)  # 1MB
    mock_proc.children.return_value = []
    return mock_proc

def test_backend_error_handling(ui_automation, mock_backend_with_errors):
    """Test error handling when backend operations fail"""
    ui_automation._backend = mock_backend_with_errors
    
    with pytest.raises(RuntimeError, match="Element not found"):
        ui_automation.find_element("id", "test")
    
    with pytest.raises(RuntimeError, match="No active window"):
        ui_automation.get_active_window()
    
    with pytest.raises(RuntimeError, match="Screenshot failed"):
        ui_automation.take_screenshot("test.png")

def test_visual_tester_error_handling(ui_automation, mock_visual_tester_with_errors, temp_dir):
    """Test error handling when visual testing operations fail"""
    ui_automation._visual_tester = mock_visual_tester_with_errors
    ui_automation.init_visual_testing(str(temp_dir))
    
    with pytest.raises(RuntimeError, match="Image comparison failed"):
        ui_automation.compare_visual("test")
    
    with pytest.raises(RuntimeError, match="Hash computation failed"):
        ui_automation.verify_visual_hash("test")

def test_process_monitoring(ui_automation):
    """Test process monitoring functionality"""
    # Start monitoring
    ui_automation.start_performance_monitoring()
    
    try:
        # Perform some operations
        element = ui_automation.find_element(by="name", value="test-button")
        ui_automation.mouse.click(element)
        
        # Get metrics using stop_performance_monitoring instead of get_metrics
        metrics = ui_automation.stop_performance_monitoring()
        
        # Verify metrics structure
        assert isinstance(metrics, dict)
        assert 'cpu_usage' in metrics
        assert 'memory_usage' in metrics
        assert 'response_times' in metrics
        
    finally:
        # Ensure monitoring is stopped
        ui_automation.stop_performance_monitoring()

def test_numpy_dependency(ui_automation, temp_dir):
    """Test numpy dependency for image processing"""
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    image_path = temp_dir / "test_image.png"
    ui_automation._save_image(test_image, str(image_path))
    assert image_path.exists()

def test_backend_abstract_methods():
    """Test that abstract methods raise NotImplementedError"""
    from pyui_automation.backends.base import BaseBackend
    
    class TestBackend(BaseBackend):
        pass
    
    backend = TestBackend()
    abstract_methods = [
        (backend.find_element, ["id", "value"]),
        (backend.find_elements, ["id", "value"]),
        (backend.get_active_window, []),
        (backend.take_screenshot, ["path"]),
        (backend.move_mouse, [0, 0]),
        (backend.click_mouse, []),
        (backend.press_key, ["key"]),
        (backend.release_key, ["key"])
    ]
    
    for method, args in abstract_methods:
        with pytest.raises(NotImplementedError):
            method(*args)

def test_backend_initialization_with_config():
    """Test backend initialization with different configurations"""
    config = AutomationConfig(
        screenshot_format="png",
        screenshot_quality=90,
        default_timeout=10,
        polling_interval=0.5,
        visual_threshold=0.95
    )
    
    ui = AutomationSession(config=config)
    assert ui._config.screenshot_format == "png"
    assert ui._config.screenshot_quality == 90
    assert ui._config.default_timeout == 10
    assert ui._config.polling_interval == 0.5
    assert ui._config.visual_threshold == 0.95

def test_element_waits_configuration(ui_automation):
    """Test element waits configuration"""
    custom_timeout = 15
    custom_interval = 0.2
    
    ui_automation.configure_waits(timeout=custom_timeout, polling_interval=custom_interval)
    assert ui_automation._config.default_timeout == custom_timeout
    assert ui_automation._config.polling_interval == custom_interval

def test_visual_testing_configuration(ui_automation, temp_dir):
    """Test visual testing configuration"""
    custom_threshold = 0.98
    ui_automation.init_visual_testing(
        str(temp_dir),
        threshold=custom_threshold
    )
    assert ui_automation._config.visual_threshold == custom_threshold
    assert ui_automation._visual_tester is not None

def test_performance_monitoring_configuration(ui_automation):
    """Test performance monitoring configuration"""
    custom_interval = 2.0
    ui_automation.start_performance_monitoring(interval=custom_interval)
    assert hasattr(ui_automation, "_monitoring_thread")
    assert ui_automation._monitoring_interval == custom_interval
    ui_automation.stop_performance_monitoring()

def test_multiple_backend_operations(ui_automation):
    """Test multiple backend operations in sequence"""
    # Prepare test data
    element_id = "test-id"
    key_sequence = ["shift", "a", "b", "c"]
    mouse_coords = [(100, 100), (200, 200), (300, 300)]
    
    # Test element operations
    ui_automation.wait_for("id", element_id)
    element = ui_automation.find_element("id", element_id)
    assert element is not None
    
    # Test keyboard operations
    for key in key_sequence:
        ui_automation.keyboard.press_key(key)
        ui_automation.keyboard.release_key(key)
    
    # Test mouse operations
    for x, y in mouse_coords:
        ui_automation.mouse.move_to((x, y))  # Changed to move_to with tuple coordinates
        ui_automation.mouse.click(None)  # Changed to click with None as argument

def test_concurrent_operations(ui_automation):
    """Test concurrent operations handling"""
    import threading
    
    def parallel_operation():
        ui_automation.find_element("id", "test-id")
        ui_automation.mouse.move(100, 100)
        ui_automation.mouse.click()
    
    threads = []
    for _ in range(3):
        thread = threading.Thread(target=parallel_operation)
        thread.start()
        threads.append(thread)
    
    for thread in threads:
        thread.join()
