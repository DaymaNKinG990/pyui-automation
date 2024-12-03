import pytest
from unittest.mock import MagicMock, patch
import sys
import numpy as np
from PIL import Image

# Mock Linux-specific modules before importing LinuxBackend
mock_display = MagicMock()
mock_x = MagicMock()

class MockXlib:
    display = mock_display
    X = mock_x

sys.modules['pyatspi'] = MagicMock()
sys.modules['Xlib'] = MockXlib
sys.modules['Xlib.display'] = mock_display
sys.modules['Xlib.X'] = mock_x

# Now import LinuxBackend after mocking the dependencies
from pyui_automation.backends.linux import LinuxBackend


@pytest.fixture
def mock_display():
    """Create a mock display with screen and root window"""
    disp = MagicMock()
    screen = MagicMock()
    root = MagicMock()
    
    # Set up screen geometry
    geom = MagicMock()
    geom.width = 1920
    geom.height = 1080
    root.get_geometry.return_value = geom
    
    # Set up image data
    image_data = MagicMock()
    image_data.data = b'\x00' * (1920 * 1080 * 4)  # BGRX format
    root.get_image.return_value = image_data
    
    screen.root = root
    disp.screen.return_value = screen

    # Update the global mock_display for Xlib
    global mock_display
    mock_display.Display.return_value = disp
    
    return disp


@pytest.fixture
def mock_registry():
    registry = MagicMock()
    desktop = MagicMock()
    registry.getDesktop.return_value = desktop
    return registry


@pytest.fixture
def mock_element():
    element = MagicMock()
    element.name = "Test Element"
    element.id = "test_id"
    element.description = "Test Description"
    element.childCount = 0
    element.getRole.return_value = 34  # Example role number
    return element


@pytest.fixture
def backend(mock_display, mock_registry):
    """Create a LinuxBackend instance with mocked dependencies"""
    with patch('sys.platform', 'linux'):
        backend = LinuxBackend()
        # Ensure the backend uses our mock display
        backend.display = mock_display.Display()
        backend.screen = backend.display.screen()
        backend.registry = mock_registry
        return backend


def test_init_success(mock_display, mock_registry):
    """Test successful initialization on Linux"""
    with patch('sys.platform', 'linux'):
        backend = LinuxBackend()
        assert backend.display == mock_display.Display()
        assert backend.screen == mock_display.Display().screen()
        assert backend.registry == mock_registry
        mock_registry.start.assert_called_once()


def test_init_failure():
    """Test initialization failure on non-Linux platform"""
    with patch('sys.platform', 'win32'):
        with pytest.raises(RuntimeError) as exc:
            LinuxBackend()
        assert "LinuxBackend can only be used on Linux systems" in str(exc.value)


def test_find_element(backend, mock_element):
    """Test finding a single element"""
    desktop = backend.registry.getDesktop.return_value
    desktop.childCount = 1
    desktop.getChildAtIndex.return_value = mock_element

    # Test successful find with direct match
    mock_element.name = "target"
    element = backend.find_element("name", "target")
    assert element == mock_element

    # Test successful find with nested element
    child = MagicMock()
    child.name = "target"
    child.childCount = 0
    mock_element.name = "parent"
    mock_element.childCount = 1
    mock_element.getChildAtIndex.return_value = child
    
    element = backend.find_element("name", "target")
    assert element == child

    # Test element not found
    element = backend.find_element("name", "nonexistent")
    assert element is None

    # Test exception handling
    mock_element.getChildAtIndex.side_effect = Exception("Test error")
    element = backend.find_element("name", "target")
    assert element is None


def test_find_elements(backend, mock_element):
    """Test finding multiple elements"""
    desktop = backend.registry.getDesktop.return_value
    
    # Create mock hierarchy
    child1 = MagicMock()
    child1.name = "target"
    child1.childCount = 0
    
    child2 = MagicMock()
    child2.name = "target"
    child2.childCount = 0
    
    mock_element.childCount = 2
    mock_element.getChildAtIndex.side_effect = [child1, child2]
    desktop.childCount = 1
    desktop.getChildAtIndex.return_value = mock_element

    # Test finding multiple elements
    elements = backend.find_elements("name", "target")
    assert len(elements) == 2
    assert child1 in elements
    assert child2 in elements

    # Test no elements found
    elements = backend.find_elements("name", "nonexistent")
    assert elements == []

    # Test exception handling
    mock_element.getChildAtIndex.side_effect = Exception("Test error")
    elements = backend.find_elements("name", "target")
    assert elements == []


def test_get_active_window(backend, mock_element):
    """Test getting active window"""
    desktop = backend.registry.getDesktop.return_value
    state = MagicMock()
    state.contains.return_value = True
    mock_element.getState.return_value = state
    
    # Test successful get
    desktop.__iter__ = lambda x: iter([mock_element])
    window = backend.get_active_window()
    assert window == mock_element

    # Test no active window
    state.contains.return_value = False
    window = backend.get_active_window()
    assert window is None

    # Test empty desktop
    desktop.__iter__ = lambda x: iter([])
    window = backend.get_active_window()
    assert window is None


def test_take_screenshot(backend):
    """Test screenshot functionality"""
    with patch('PIL.Image.frombytes') as mock_frombytes:
        # Mock PIL image
        pil_image = MagicMock()
        mock_frombytes.return_value = pil_image

        # Test successful screenshot
        assert backend.take_screenshot("test.png") is True
        pil_image.save.assert_called_with("test.png")

        # Test failure during image creation
        mock_frombytes.side_effect = Exception("Test error")
        assert backend.take_screenshot("test.png") is False


def test_get_screen_size(backend):
    """Test getting screen dimensions"""
    # Test successful get
    width, height = backend.get_screen_size()
    assert width == 1920
    assert height == 1080

    # Test with different dimensions
    geom = backend.display.screen().root.get_geometry()
    geom.width = 2560
    geom.height = 1440
    width, height = backend.get_screen_size()
    assert width == 2560
    assert height == 1440


def test_matches_criteria(backend, mock_element):
    """Test element criteria matching"""
    # Test name matching
    mock_element.name = "test_name"
    assert backend._matches_criteria(mock_element, "name", "test_name") is True
    assert backend._matches_criteria(mock_element, "name", "wrong_name") is False

    # Test role matching
    mock_element.getRole.return_value = 34  # Example role number
    with patch('pyatspi.BUTTON', 34):
        assert backend._matches_criteria(mock_element, "role", "BUTTON") is True
    assert backend._matches_criteria(mock_element, "role", "MENU") is False

    # Test id matching
    mock_element.id = "test_id"
    assert backend._matches_criteria(mock_element, "id", "test_id") is True
    assert backend._matches_criteria(mock_element, "id", "wrong_id") is False

    # Test description matching
    mock_element.description = "test_desc"
    assert backend._matches_criteria(mock_element, "description", "test_desc") is True
    assert backend._matches_criteria(mock_element, "description", "wrong_desc") is False

    # Test invalid criteria type
    assert backend._matches_criteria(mock_element, "invalid", "value") is False

    # Test exception handling
    mock_element.getRole.side_effect = Exception("Test error")
    assert backend._matches_criteria(mock_element, "role", "BUTTON") is False


def test_cleanup(backend):
    """Test cleanup on deletion"""
    # Test successful cleanup
    backend.__del__()
    backend.registry.stop.assert_called_once()

    # Test cleanup with exception
    backend.registry.stop.side_effect = Exception("Test error")
    backend.__del__()  # Should not raise exception
