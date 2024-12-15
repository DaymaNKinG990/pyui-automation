import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from pyui_automation.core.session import AutomationSession
from pyui_automation.core.config import AutomationConfig
from pyui_automation.elements.base import UIElement
from pyui_automation.backends.base import BaseBackend
from pyui_automation.wait import ElementWaits
from pyui_automation.core.visual import VisualTester


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


def test_find_element(mock_session, mock_backend):
    """Test finding a single element"""
    mock_element = MagicMock()
    mock_backend.find_element.return_value = mock_element
    
    element = mock_session.find_element('id', 'test-id')
    assert isinstance(element, UIElement)
    mock_backend.find_element.assert_called_once_with('id', 'test-id')


def test_find_element_with_timeout(mock_session, mock_backend):
    """Test finding element with timeout"""
    mock_element = MagicMock()
    mock_backend.find_element.return_value = mock_element
    
    element = mock_session.find_element('id', 'test-id', timeout=5.0)
    assert isinstance(element, UIElement)
    mock_backend.find_element.assert_called_once_with('id', 'test-id')


def test_find_element_not_found(mock_session, mock_backend):
    """Test finding non-existent element"""
    mock_backend.find_element.return_value = None
    
    element = mock_session.find_element('id', 'non-existent')
    assert element is None


def test_find_elements(mock_session, mock_backend):
    """Test finding multiple elements"""
    mock_elements = [MagicMock(), MagicMock()]
    mock_backend.find_elements.return_value = mock_elements
    
    elements = mock_session.find_elements('class', 'test-class')
    assert len(elements) == 2
    assert all(isinstance(elem, UIElement) for elem in elements)
    mock_backend.find_elements.assert_called_once_with('class', 'test-class')


def test_find_elements_not_found(mock_session, mock_backend):
    """Test finding elements with no matches"""
    mock_backend.find_elements.return_value = []
    
    elements = mock_session.find_elements('class', 'non-existent')
    assert elements == []


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
    assert hasattr(mock_session.config, 'timeout')
    assert hasattr(mock_session.config, 'poll_frequency')


def test_component_access(mock_session):
    """Test accessing components"""
    assert mock_session.keyboard is not None
    assert mock_session.mouse is not None
    assert mock_session.ocr is not None
    assert mock_session.waits is not None


def test_backend_property(mock_session, mock_backend):
    """Test backend property"""
    assert mock_session.backend == mock_backend


@pytest.mark.parametrize("by,value", [
    ('id', 'test-id'),
    ('name', 'test-name'),
    ('class', 'test-class'),
    ('xpath', '//div[@id="test"]'),
])
def test_find_element_strategies(mock_session, mock_backend, by, value):
    """Test different element finding strategies"""
    mock_element = MagicMock()
    mock_backend.find_element.return_value = mock_element
    
    element = mock_session.find_element(by, value)
    assert isinstance(element, UIElement)
    mock_backend.find_element.assert_called_once_with(by, value)


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
