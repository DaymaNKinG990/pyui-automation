import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from pyui_automation.core.session import AutomationSession
from pyui_automation.core.config import AutomationConfig
from pyui_automation.elements.base import UIElement
from pyui_automation.backends.base import BaseBackend


@pytest.fixture
def mock_backend():
    """Create a mock backend"""
    backend = MagicMock(spec=BaseBackend)
    backend.find_element.return_value = MagicMock()
    backend.find_elements.return_value = [MagicMock()]
    backend.get_active_window.return_value = MagicMock()
    backend.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
    backend.capture_element_screenshot.return_value = np.zeros((50, 50, 3), dtype=np.uint8)
    return backend


@pytest.fixture
def mock_components():
    """Create mock components"""
    with patch('pyui_automation.core.factory.ComponentFactory') as mock_factory:
        mock_factory.return_value.create_keyboard.return_value = MagicMock()
        mock_factory.return_value.create_mouse.return_value = MagicMock()
        mock_factory.return_value.create_ocr_engine.return_value = MagicMock()
        yield mock_factory


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
def mock_session(mock_backend, mock_element_waits):
    """Create mock session with dependencies"""
    session = AutomationSession(backend=mock_backend)
    session.waits = mock_element_waits
    
    # Create a proper mock for visual_tester
    mock_visual = MagicMock()
    mock_visual.capture_baseline = MagicMock()
    session._visual_tester = mock_visual
    
    return session


@pytest.fixture
def mock_visual_tester():
    """Create mock visual tester"""
    with patch('pyui_automation.core.visual.VisualTester') as mock_tester:
        yield mock_tester


def test_session_init_default_backend():
    """Test session initialization with default backend"""
    with patch('pyui_automation.core.factory.BackendFactory.create_backend') as mock_create:
        mock_backend = MagicMock(spec=BaseBackend)
        mock_create.return_value = mock_backend
        session = AutomationSession(backend=mock_backend)
        assert session.backend == mock_backend


def test_session_init_custom_backend():
    """Test session initialization with custom backend"""
    mock_backend = MagicMock(spec=BaseBackend)
    session = AutomationSession(backend=mock_backend)
    assert session.backend == mock_backend


def test_get_active_window(mock_session, mock_backend):
    """Test getting active window"""
    mock_window = MagicMock()
    mock_backend.get_active_window.return_value = mock_window
    
    window = mock_session.get_active_window()
    assert isinstance(window, UIElement)
    mock_backend.get_active_window.assert_called_once()


def test_get_active_window_none(mock_session, mock_backend):
    """Test getting active window when none exists"""
    mock_backend.get_active_window.return_value = None
    
    window = mock_session.get_active_window()
    assert window is None


def test_init_visual_testing(mock_session, tmp_path):
    """Test initializing visual testing"""
    baseline_dir = tmp_path / "visual_baseline"
    mock_session.init_visual_testing(str(baseline_dir))
    assert mock_session._visual_tester is not None
    assert baseline_dir.exists()


def test_capture_screenshot(mock_session, mock_backend):
    """Test capturing screenshot"""
    mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_backend.capture_screenshot.return_value = mock_image
    
    screenshot = mock_session.capture_screenshot()
    assert isinstance(screenshot, np.ndarray)
    assert screenshot.shape == (100, 100, 3)
    mock_backend.capture_screenshot.assert_called_once()


def test_capture_element_screenshot(mock_session):
    """Test capturing element screenshot"""
    mock_element = MagicMock()
    mock_image = np.zeros((50, 50, 3), dtype=np.uint8)
    mock_element.capture_screenshot.return_value = mock_image
    
    screenshot = mock_session.capture_element_screenshot(mock_element)
    assert isinstance(screenshot, np.ndarray)
    assert screenshot.shape == (50, 50, 3)
    mock_element.capture_screenshot.assert_called_once()


def test_verify_visual_state(mock_session):
    """Test verifying visual state"""
    mock_element = MagicMock()
    mock_image = np.zeros((50, 50, 3), dtype=np.uint8)
    mock_element.capture_screenshot.return_value = mock_image

    # Mock baseline path existence and image reading
    with patch('pathlib.Path.exists', return_value=True), \
         patch('cv2.imread', return_value=mock_image), \
         patch.object(mock_session.visual_tester, 'verify_hash') as mock_verify:
        mock_verify.return_value = True
        result = mock_session.verify_visual_hash('test_state', mock_element)
        assert result['match']
        assert len(result['differences']) == 0


def test_verify_visual_state_with_differences(mock_session):
    """Test verifying visual state with differences"""
    mock_element = MagicMock()
    mock_image = np.zeros((50, 50, 3), dtype=np.uint8)
    mock_element.capture_screenshot.return_value = mock_image

    # Mock baseline path existence and image reading
    with patch('pathlib.Path.exists', return_value=True), \
         patch('cv2.imread', return_value=mock_image), \
         patch.object(mock_session.visual_tester, 'verify_hash') as mock_verify:
        mock_verify.return_value = False
        result = mock_session.verify_visual_hash('test_state', mock_element)
        assert not result['match']
        assert len(result['differences']) > 0


def test_capture_baseline(mock_session):
    """Test capturing baseline state"""
    mock_element = MagicMock()
    mock_image = np.zeros((50, 50, 3), dtype=np.uint8)
    mock_element.capture_screenshot.return_value = mock_image

    with patch.object(mock_session.visual_tester, 'capture_baseline') as mock_capture:
        mock_session.capture_visual_baseline('test_baseline', mock_element)
        mock_capture.assert_called_once_with('test_baseline.png', mock_image)


def test_capture_visual_baseline_with_element(mock_session):
    """Test capturing visual baseline with element"""
    element = MagicMock()
    image = np.zeros((50, 50, 3), dtype=np.uint8)
    element.capture_screenshot.return_value = image
    
    mock_session.capture_visual_baseline("test_baseline", element)
    
    element.capture_screenshot.assert_called_once()
    mock_session.visual_tester.capture_baseline.assert_called_once_with("test_baseline.png", image)


def test_capture_visual_baseline_full_screen(mock_session):
    """Test capturing visual baseline full screen"""
    image = np.zeros((50, 50, 3), dtype=np.uint8)
    mock_session.capture_screenshot = MagicMock(return_value=image)
    
    mock_session.capture_visual_baseline("test_baseline")
    
    mock_session.capture_screenshot.assert_called_once()
    mock_session.visual_tester.capture_baseline.assert_called_once_with("test_baseline.png", image)


def test_config_access(mock_session):
    """Test accessing configuration"""
    assert isinstance(mock_session.config, AutomationConfig)
    assert hasattr(mock_session.config, 'default_timeout')
    assert hasattr(mock_session.config, 'polling_interval')


def test_component_access(mock_session):
    """Test accessing components"""
    assert mock_session.keyboard is not None
    assert mock_session.mouse is not None
    assert mock_session.ocr is not None
    assert mock_session.waits is not None


def test_backend_property(mock_session, mock_backend):
    """Test backend property"""
    assert mock_session.backend == mock_backend


# Удалён тест test_find_element_strategies (устаревший by/value)


def test_session_cleanup(mock_session, mock_backend):
    """Test session cleanup"""
    if hasattr(mock_session, 'cleanup'):
        mock_session.cleanup()
        if hasattr(mock_backend, 'cleanup'):
            mock_backend.cleanup.assert_called_once()


def test_start_performance_monitoring(mock_session):
    """Test starting performance monitoring"""
    # Start monitoring
    mock_session.start_performance_monitoring(interval=1.0)
    
    # Check that performance monitor was created
    assert mock_session._performance_monitor is not None
    
    # Check that monitoring was started
    assert mock_session._performance_monitor.monitor.is_monitoring
    
    # Stop monitoring and check metrics
    metrics = mock_session.stop_performance_monitoring()
    assert isinstance(metrics, dict)
    assert "cpu_usage" in metrics
    assert "memory_usage" in metrics
    assert "duration" in metrics


@pytest.fixture
def mock_backend():
    backend = MagicMock()
    backend.capture_element_screenshot.return_value = np.ones((100, 100, 3), dtype=np.uint8)
    backend.capture_screenshot.return_value = np.ones((1920, 1080, 3), dtype=np.uint8)
    return backend


@pytest.fixture
def session(mock_backend):
    return AutomationSession(backend=mock_backend)


@pytest.fixture
def mock_element(mock_backend):
    element = UIElement(mock_backend, MagicMock())
    return element


def test_verify_visual_state(session, mock_element):
    """Test verifying visual state of element"""
    with patch.object(session, '_visual_tester') as mock_tester:
        mock_tester.compare.return_value = 0.98
        result = session.verify_visual_state("test_state")
        assert result == 0.98


def test_verify_visual_state_with_differences(session, mock_element):
    """Test verifying visual state with differences"""
    with patch.object(session, '_visual_tester') as mock_tester:
        mock_tester.compare.return_value = 0.85
        result = session.verify_visual_state("test_state")
        assert result < 0.95


def test_capture_baseline(session, mock_element):
    """Test capturing visual baseline"""
    with patch.object(session, '_visual_tester') as mock_tester:
        session.capture_visual_baseline(mock_element, "test_baseline")
        mock_tester.capture_baseline.assert_called_once()


def test_capture_visual_baseline_with_element(session, mock_element):
    """Test capturing visual baseline with element"""
    with patch.object(session, '_visual_tester') as mock_tester:
        mock_tester.capture_baseline.return_value = True
        session.capture_visual_baseline(mock_element, "test_baseline")
        assert mock_tester.capture_baseline.call_args[0][0] == "test_baseline"


def test_capture_visual_baseline_full_screen(session):
    """Test capturing full screen baseline"""
    with patch.object(session, '_visual_tester') as mock_tester:
        session.capture_visual_baseline('test_baseline')
        assert mock_tester.capture_baseline.call_args[0][0] == 'test_baseline'


def test_find_element_by_object_name(mock_session, mock_backend):
    mock_element = MagicMock()
    mock_backend.find_element_by_object_name.return_value = mock_element
    element = mock_session.find_element_by_object_name("test-object")
    assert isinstance(element, UIElement)
    mock_backend.find_element_by_object_name.assert_called_once_with("test-object")

def test_find_elements_by_object_name(mock_session, mock_backend):
    mock_elements = [MagicMock(), MagicMock()]
    mock_backend.find_elements_by_object_name.return_value = mock_elements
    elements = mock_session.find_elements_by_object_name("test-object")
    assert len(elements) == 2
    assert all(isinstance(e, UIElement) for e in elements)
    mock_backend.find_elements_by_object_name.assert_called_once_with("test-object")

def test_find_element_by_widget_type(mock_session, mock_backend):
    mock_element = MagicMock()
    mock_backend.find_element_by_widget_type.return_value = mock_element
    element = mock_session.find_element_by_widget_type("Button")
    assert isinstance(element, UIElement)
    mock_backend.find_element_by_widget_type.assert_called_once_with("Button")

def test_find_elements_by_widget_type(mock_session, mock_backend):
    mock_elements = [MagicMock(), MagicMock()]
    mock_backend.find_elements_by_widget_type.return_value = mock_elements
    elements = mock_session.find_elements_by_widget_type("Button")
    assert len(elements) == 2
    assert all(isinstance(e, UIElement) for e in elements)
    mock_backend.find_elements_by_widget_type.assert_called_once_with("Button")

def test_find_element_by_text(mock_session, mock_backend):
    mock_element = MagicMock()
    mock_backend.find_element_by_text.return_value = mock_element
    element = mock_session.find_element_by_text("OK")
    assert isinstance(element, UIElement)
    mock_backend.find_element_by_text.assert_called_once_with("OK")

def test_find_elements_by_text(mock_session, mock_backend):
    mock_elements = [MagicMock(), MagicMock()]
    mock_backend.find_elements_by_text.return_value = mock_elements
    elements = mock_session.find_elements_by_text("OK")
    assert len(elements) == 2
    assert all(isinstance(e, UIElement) for e in elements)
    mock_backend.find_elements_by_text.assert_called_once_with("OK")

def test_find_element_by_property(mock_session, mock_backend):
    mock_element = MagicMock()
    mock_backend.find_element_by_property.return_value = mock_element
    element = mock_session.find_element_by_property("role", "button")
    assert isinstance(element, UIElement)
    mock_backend.find_element_by_property.assert_called_once_with("role", "button")

def test_find_elements_by_property(mock_session, mock_backend):
    mock_elements = [MagicMock(), MagicMock()]
    mock_backend.find_elements_by_property.return_value = mock_elements
    elements = mock_session.find_elements_by_property("role", "button")
    assert len(elements) == 2
    assert all(isinstance(e, UIElement) for e in elements)
    mock_backend.find_elements_by_property.assert_called_once_with("role", "button")


def test_visual_tester_not_initialized():
    """Test error when visual_tester is not initialized"""
    from pyui_automation.core.session import AutomationSession
    session = AutomationSession(backend=MagicMock())
    with pytest.raises(RuntimeError):
        _ = session.visual_tester
    with pytest.raises(RuntimeError):
        session.find_element('template')
    with pytest.raises(RuntimeError):
        session.find_all_elements('template')
    with pytest.raises(RuntimeError):
        session.wait_for_image('template')
    with pytest.raises(RuntimeError):
        session.highlight_differences(MagicMock(), MagicMock())
    with pytest.raises(ValueError):
        session.capture_baseline('name')
    with pytest.raises(ValueError):
        session.capture_visual_baseline('name')
    with pytest.raises(ValueError):
        session.verify_visual('name')
    with pytest.raises(ValueError):
        session.generate_visual_report([], 'name')


def test_performance_monitoring_not_started():
    """Test error when performance monitoring is not started"""
    from pyui_automation.core.session import AutomationSession
    session = AutomationSession(backend=MagicMock())
    with pytest.raises(ValueError):
        session.get_performance_metrics()


def test_invalid_ocr_language():
    """Test error when setting invalid OCR language"""
    from pyui_automation.core.session import AutomationSession
    session = AutomationSession(backend=MagicMock())
    with pytest.raises(ValueError):
        session.set_ocr_languages(['invalid'])
    with pytest.raises(ValueError):
        session.set_ocr_language('invalid')


def test_mouse_move_invalid():
    """Test error when moving mouse with invalid coordinates"""
    from pyui_automation.core.session import AutomationSession
    session = AutomationSession(backend=MagicMock())
    with pytest.raises(ValueError):
        session.mouse_move(-1, 10)
    with pytest.raises(ValueError):
        session.mouse_move(10, -1)
    with pytest.raises(ValueError):
        session.mouse_move('a', 10)
    with pytest.raises(ValueError):
        session.mouse_move(10, 'b')


def test_press_key_invalid():
    """Test error when pressing invalid key"""
    from pyui_automation.core.session import AutomationSession
    session = AutomationSession(backend=MagicMock())
    with pytest.raises(ValueError):
        session.press_key('invalid')


def test_capture_screenshot_backend_error():
    """Test error when backend.capture_screenshot returns None"""
    from pyui_automation.core.session import AutomationSession
    backend = MagicMock()
    backend.capture_screenshot.return_value = None
    session = AutomationSession(backend=backend)
    with pytest.raises(RuntimeError):
        session.capture_screenshot()


def test_capture_element_screenshot_error():
    """Test error when element.capture_screenshot returns None"""
    from pyui_automation.core.session import AutomationSession
    session = AutomationSession(backend=MagicMock())
    element = MagicMock()
    element.capture_screenshot.return_value = None
    with pytest.raises(RuntimeError):
        session.capture_element_screenshot(element)


def test_attach_to_process_invalid_pid():
    """Test error when attaching to non-existent process"""
    from pyui_automation.core.session import AutomationSession
    import psutil
    session = AutomationSession(backend=MagicMock())
    with pytest.raises(psutil.NoSuchProcess):
        session.attach_to_process(999999)


def test_run_stress_test_invalid_duration():
    """Test error when running stress test with invalid duration"""
    from pyui_automation.core.session import AutomationSession
    session = AutomationSession(backend=MagicMock())
    with pytest.raises(ValueError):
        session.run_stress_test(lambda: None, 0)


def test_measure_action_performance_invalid_runs():
    """Test error when measuring action performance with invalid runs"""
    from pyui_automation.core.session import AutomationSession
    session = AutomationSession(backend=MagicMock())
    with pytest.raises(ValueError):
        session.measure_action_performance(lambda: None, 0)


def test_check_memory_leaks_no_action():
    """Test error when check_memory_leaks called without action"""
    from pyui_automation.core.session import AutomationSession
    session = AutomationSession(backend=MagicMock())
    with pytest.raises(ValueError):
        session.check_memory_leaks()


def test_check_memory_leaks_invalid_iterations():
    """Test error when check_memory_leaks called with invalid iterations"""
    from pyui_automation.core.session import AutomationSession
    session = AutomationSession(backend=MagicMock())
    with pytest.raises(ValueError):
        session.check_memory_leaks(lambda: None, 0)


def test_save_image_invalid_type():
    """Test error when _save_image called with non-numpy array"""
    from pyui_automation.core.session import AutomationSession
    session = AutomationSession(backend=MagicMock())
    with pytest.raises(ValueError):
        session._save_image('not_an_array', 'path.png')


def test_ocr_property_not_supported():
    """Test error when backend does not support ocr property"""
    from pyui_automation.core.session import AutomationSession
    backend = MagicMock()
    del backend.ocr
    session = AutomationSession(backend=backend)
    with pytest.raises(AttributeError):
        _ = session.ocr


def test_take_screenshot_save_path_error(mock_session, mock_backend, monkeypatch):
    # Ошибка при создании директории
    mock_backend.capture_screenshot.return_value = np.zeros((10, 10, 3), dtype=np.uint8)
    monkeypatch.setattr("pathlib.Path.mkdir", lambda *a, **k: (_ for _ in ()).throw(PermissionError("No permission")))
    with pytest.raises(PermissionError):
        mock_session.take_screenshot("/forbidden_dir/screenshot.png")

def test_take_screenshot_backend_returns_none(mock_session, mock_backend):
    mock_backend.capture_screenshot.return_value = None
    with pytest.raises(RuntimeError):
        mock_session.take_screenshot()

def test_take_screenshot_backend_returns_wrong_type(mock_session, mock_backend):
    mock_backend.capture_screenshot.return_value = "not an array"
    with pytest.raises(RuntimeError):
        mock_session.take_screenshot()

def test__save_image_invalid_type(mock_session):
    with pytest.raises(Exception):
        mock_session._save_image("not an array", "file.png")

def test_visual_tester_property_not_initialized(mock_session):
    mock_session._visual_tester = None
    with pytest.raises(RuntimeError):
        _ = mock_session.visual_tester

def test_keyboard_property_not_initialized(mock_session):
    mock_session._keyboard = None
    kb = mock_session.keyboard
    assert kb is not None

def test_mouse_property_not_initialized(mock_session):
    mock_session._mouse = None
    mouse = mock_session.mouse
    assert mouse is not None
