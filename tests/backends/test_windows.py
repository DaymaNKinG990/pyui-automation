import pytest
import numpy as np
from unittest.mock import MagicMock, PropertyMock, patch
import win32gui
import win32ui
import win32con
import win32api
from comtypes.client import CreateObject

from pyui_automation.backends.windows import WindowsBackend


@pytest.fixture
def mock_uia():
    """Create a mock UI Automation object"""
    mock = MagicMock()
    mock.GetRootElement.return_value = MagicMock()
    return mock


@pytest.fixture
def mock_element():
    """Create a mock UI Automation element"""
    element = MagicMock()
    # Set up common properties
    element.CurrentName = "Test Element"
    element.CurrentClassName = "TestClass"
    element.CurrentAutomationId = "TestId"
    element.CurrentBoundingRectangle = (0, 0, 100, 100)
    element.CurrentIsEnabled = True
    element.CurrentIsOffscreen = False
    return element


@pytest.fixture
def windows_backend(mock_uia):
    """Create a WindowsBackend instance with mocked automation"""
    with patch('winreg.OpenKey', return_value=MagicMock()), \
         patch('comtypes.client.GetModule'), \
         patch('comtypes.client.CreateObject', return_value=mock_uia), \
         patch('ctypes.windll.shell32.IsUserAnAdmin', return_value=True), \
         patch.dict('sys.modules', {'UIAutomationClient': MagicMock()}):
        backend = WindowsBackend()
        return backend


def test_init_success(mock_uia):
    """Test successful initialization"""
    with patch('winreg.OpenKey', return_value=MagicMock()), \
         patch('comtypes.client.GetModule'), \
         patch('comtypes.client.CreateObject', return_value=mock_uia), \
         patch('ctypes.windll.shell32.IsUserAnAdmin', return_value=True), \
         patch.dict('sys.modules', {'UIAutomationClient': MagicMock()}):
        backend = WindowsBackend()
        assert backend.automation is not None


def test_init_failure():
    """Test initialization failure"""
    with patch('comtypes.client.CreateObject', side_effect=Exception("Failed to create UI Automation")), \
         patch.dict('sys.modules', {'UIAutomationClient': MagicMock()}):
        with pytest.raises(RuntimeError):
            WindowsBackend()


def test_find_element_by_id(windows_backend, mock_element):
    """Test finding element by ID"""
    windows_backend.automation.ElementFromHandle.return_value = mock_element
    mock_element.FindFirst.return_value = mock_element

    element = windows_backend.find_element('id', 'TestId')
    assert element is not None
    assert element.CurrentAutomationId == 'TestId'


def test_find_element_by_name(windows_backend, mock_element):
    """Test finding element by name"""
    windows_backend.automation.ElementFromHandle.return_value = mock_element
    mock_element.FindFirst.return_value = mock_element

    element = windows_backend.find_element('name', 'Test Element')
    assert element is not None
    assert element.CurrentName == 'Test Element'


def test_find_element_by_class(windows_backend, mock_element):
    """Test finding element by class name"""
    windows_backend.automation.ElementFromHandle.return_value = mock_element
    mock_element.FindFirst.return_value = mock_element

    element = windows_backend.find_element('class', 'TestClass')
    assert element is not None
    assert element.CurrentClassName == 'TestClass'


def test_find_elements_by_class(windows_backend, mock_element):
    """Test finding multiple elements by class name"""
    windows_backend.automation.ElementFromHandle.return_value = mock_element
    mock_elements = MagicMock()
    mock_elements.Length = 2
    mock_elements.GetElement.side_effect = [mock_element, mock_element]
    mock_element.FindAll.return_value = mock_elements

    elements = windows_backend.find_elements('class', 'TestClass')
    assert len(elements) == 2
    assert all(e.CurrentClassName == 'TestClass' for e in elements)


def test_get_active_window_basic(windows_backend, mock_element):
    """Test getting active window"""
    mock_element = MagicMock()
    with patch('win32gui.GetForegroundWindow', return_value=12345):
        windows_backend.automation.ElementFromHandle.return_value = mock_element
        window = windows_backend.get_active_window()
        assert window is not None
        assert window == mock_element


def test_capture_screen(windows_backend):
    """Test screen capture"""
    with patch('win32gui.GetDesktopWindow', return_value=12345), \
         patch('win32gui.GetWindowDC', return_value=67890), \
         patch('win32api.GetSystemMetrics', return_value=100), \
         patch('win32gui.DeleteObject', return_value=True), \
         patch('win32gui.ReleaseDC', return_value=True), \
         patch('win32ui.CreateDCFromHandle') as mock_create_dc, \
         patch('win32ui.CreateBitmap') as mock_create_bitmap:

        mock_dc = MagicMock()
        mock_compatible_dc = MagicMock()
        mock_dc.CreateCompatibleDC.return_value = mock_compatible_dc
        mock_create_dc.return_value = mock_dc

        mock_bitmap = MagicMock()
        mock_bitmap.GetInfo.return_value = {'bmWidth': 100, 'bmHeight': 100}
        mock_bitmap.GetBitmapBits.return_value = bytes([0] * (100 * 100 * 4))
        mock_bitmap.GetHandle.return_value = 12345
        mock_create_bitmap.return_value = mock_bitmap

        screenshot = windows_backend.capture_screen()
        assert screenshot is not None
        assert screenshot.shape == (100, 100, 4)


def test_capture_window(windows_backend):
    """Test window capture"""
    with patch('win32gui.GetWindowRect', return_value=(0, 0, 100, 100)), \
         patch('win32gui.GetWindowDC', return_value=67890), \
         patch('win32gui.DeleteObject', return_value=True), \
         patch('win32gui.ReleaseDC', return_value=True), \
         patch('win32ui.CreateDCFromHandle') as mock_create_dc, \
         patch('win32ui.CreateBitmap') as mock_create_bitmap:

        mock_dc = MagicMock()
        mock_compatible_dc = MagicMock()
        mock_dc.CreateCompatibleDC.return_value = mock_compatible_dc
        mock_create_dc.return_value = mock_dc

        mock_bitmap = MagicMock()
        mock_bitmap.GetInfo.return_value = {'bmWidth': 100, 'bmHeight': 100}
        mock_bitmap.GetBitmapBits.return_value = bytes([0] * (100 * 100 * 4))
        mock_bitmap.GetHandle.return_value = 12345
        mock_create_bitmap.return_value = mock_bitmap

        screenshot = windows_backend.capture_window(12345)
        assert screenshot is not None
        assert screenshot.shape == (100, 100, 4)


def test_get_element_pattern(windows_backend, mock_element):
    """Test getting element pattern"""
    pattern_id = 10000  # Some pattern ID
    mock_pattern = MagicMock()
    mock_interface = MagicMock()
    mock_pattern.QueryInterface.return_value = mock_interface
    mock_element.GetCurrentPattern.return_value = mock_pattern

    pattern = windows_backend._get_element_pattern(mock_element, pattern_id)
    assert pattern == mock_interface


def test_find_element(windows_backend, mock_element):
    """Test finding a single element"""
    # Test successful find
    condition = MagicMock()
    windows_backend.automation.CreatePropertyCondition.return_value = condition
    windows_backend.automation.ElementFromHandle.return_value = mock_element
    mock_element.FindFirst.return_value = mock_element

    element = windows_backend.find_element("id", "TestId")
    assert element.CurrentAutomationId == "TestId"

    # Test not found
    mock_element.FindFirst.return_value = None
    element = windows_backend.find_element("id", "nonexistent")
    assert element is None

    # Test error cases
    windows_backend.automation.ElementFromHandle.return_value = None
    element = windows_backend.find_element("id", "TestId")
    assert element is None

    windows_backend.automation.CreatePropertyCondition.return_value = None
    element = windows_backend.find_element("id", "TestId")
    assert element is None


def test_find_elements(windows_backend, mock_element):
    """Test finding multiple elements"""
    # Test successful find
    condition = MagicMock()
    mock_elements = MagicMock()
    mock_elements.Length = 2
    mock_elements.GetElement.side_effect = [mock_element, mock_element]
    
    windows_backend.automation.CreatePropertyCondition.return_value = condition
    windows_backend.automation.ElementFromHandle.return_value = mock_element
    mock_element.FindAll.return_value = mock_elements

    elements = windows_backend.find_elements("class", "TestClass")
    assert len(elements) == 2
    assert all(e.CurrentClassName == "TestClass" for e in elements)

    # Test no elements found
    windows_backend.root.FindAll.return_value = []
    elements = windows_backend.find_elements("class", "NonexistentClass")
    assert elements == []

    # Test exception handling
    windows_backend.root.FindAll.side_effect = Exception("Test error")
    elements = windows_backend.find_elements("class", "TestClass")
    assert elements == []


def test_create_condition(windows_backend):
    """Test condition creation for different search strategies"""
    # Test all supported strategies
    for by, value in [
        ("id", "TestId"),
        ("name", "Test Name"),
        ("class", "TestClass"),
        ("type", "button")
    ]:
        condition = windows_backend._create_condition(by, value)
        assert condition == windows_backend.automation.CreatePropertyCondition.return_value
        windows_backend.automation.CreatePropertyCondition.assert_called()

    # Test invalid strategy
    condition = windows_backend._create_condition("invalid", "value")
    assert condition is None

    # Test exception handling
    windows_backend.automation.CreatePropertyCondition.side_effect = Exception("Test error")
    condition = windows_backend._create_condition("id", "TestId")
    assert condition is None


def test_get_active_window(windows_backend, mock_element):
    """Test getting active window"""
    with patch('win32gui.GetForegroundWindow', return_value=12345):
        windows_backend.automation.ElementFromHandle.return_value = mock_element
        window = windows_backend.get_active_window()
        assert window == mock_element

    # Test no active window
    with patch('win32gui.GetForegroundWindow', return_value=0):
        window = windows_backend.get_active_window()
        assert window is None

    # Test exception handling
    with patch('win32gui.GetForegroundWindow', side_effect=Exception("Test error")):
        window = windows_backend.get_active_window()
        assert window is None


def test_get_window_handles(windows_backend):
    """Test getting window handles"""
    def mock_enum_windows(callback, extra):
        for hwnd in [12345, 67890]:
            callback(hwnd, extra)

    with patch('win32gui.EnumWindows', side_effect=mock_enum_windows), \
         patch('win32gui.IsWindowVisible', return_value=True):
        handles = windows_backend.get_window_handles()
        assert handles == [12345, 67890]

    # Test exception handling
    with patch('win32gui.EnumWindows', side_effect=Exception("Test error")):
        handles = windows_backend.get_window_handles()
        assert handles == []


def test_click(windows_backend):
    """Test mouse click functionality"""
    with patch('win32api.SetCursorPos') as mock_set_pos, \
         patch('win32api.mouse_event') as mock_mouse_event, \
         patch('time.sleep'):
        
        # Test left click
        assert windows_backend.click(100, 200, "left") is True
        mock_set_pos.assert_called_with((100, 200))
        assert mock_mouse_event.call_count == 2  # down and up events

        # Test right click
        assert windows_backend.click(100, 200, "right") is True
        mock_mouse_event.assert_called()

        # Test invalid button
        assert windows_backend.click(100, 200, "invalid") is False

        # Test exception handling
        mock_set_pos.side_effect = Exception("Test error")
        assert windows_backend.click(100, 200) is False


def test_type_text(windows_backend):
    """Test text typing functionality"""
    with patch('win32api.VkKeyScan', return_value=65), \
         patch('win32api.keybd_event') as mock_keybd_event, \
         patch('time.sleep'):
        
        # Test basic typing
        mock_element = MagicMock()
        mock_element.GetCurrentPattern.return_value = None  # Force keyboard event fallback
        assert windows_backend.type_text(mock_element, "test", interval=0) is True
        assert mock_keybd_event.call_count == 8  # 4 chars * (down + up)

        # Test with interval
        assert windows_backend.type_text(mock_element, "test", interval=0.1) is True

        # Test with shift character
        with patch('win32api.VkKeyScan', return_value=(65 | (1 << 8))):
            assert windows_backend.type_text(mock_element, "A") is True
            assert mock_keybd_event.call_count >= 4  # shift down, key down, key up, shift up

        # Test invalid character
        with patch('win32api.VkKeyScan', return_value=-1):
            assert windows_backend.type_text(mock_element, "☺") is True  # Should skip invalid char

        # Test exception handling
        mock_keybd_event.side_effect = Exception("Test error")
        assert windows_backend.type_text(mock_element, "test") is False


def test_get_screen_size(windows_backend):
    """Test screen size retrieval"""
    with patch('win32api.GetSystemMetrics', side_effect=[1920, 1080]):
        size = windows_backend.get_screen_size()
        assert size == (1920, 1080)

    # Test exception handling
    with patch('win32api.GetSystemMetrics', side_effect=Exception("Test error")):
        size = windows_backend.get_screen_size()
        assert size == (0, 0)


def test_find_window(windows_backend, mock_element):
    """Test finding window by title"""
    condition = MagicMock()
    windows_backend.automation.CreatePropertyCondition.return_value = condition
    windows_backend.root.FindFirst.return_value = mock_element

    # Test successful find
    window = windows_backend.find_window("Test Window")
    assert window == mock_element
    windows_backend.automation.CreatePropertyCondition.assert_called_once()

    # Test window not found
    windows_backend.root.FindFirst.return_value = None
    window = windows_backend.find_window("Nonexistent Window")
    assert window is None

    # Test exception handling
    windows_backend.root.FindFirst.side_effect = Exception("Test error")
    window = windows_backend.find_window("Test Window")
    assert window is None


def test_get_window_title(windows_backend, mock_element):
    """Test getting window title"""
    # Test successful get
    type(mock_element).CurrentName = PropertyMock(return_value="Test Element")
    title = windows_backend.get_window_title(mock_element)
    assert title == "Test Element"

    # Test exception handling
    mock = MagicMock()
    type(mock).CurrentName = PropertyMock(side_effect=Exception("No title"))
    title = windows_backend.get_window_title(mock)
    assert title is None


def test_wait_for_window(windows_backend, mock_element):
    """Test waiting for window"""
    with patch('time.sleep'):
        # Test successful wait
        windows_backend.find_window = MagicMock(side_effect=[None, None, mock_element])
        window = windows_backend.wait_for_window("Test Window", timeout=1)
        assert window == mock_element

        # Test timeout
        windows_backend.find_window = MagicMock(return_value=None)
        window = windows_backend.wait_for_window("Nonexistent Window", timeout=1)
        assert window is None

        # Test exception handling
        windows_backend.find_window.side_effect = Exception("Test error")
        window = windows_backend.wait_for_window("Test Window", timeout=1)
        assert window is None


def test_get_element_attributes(windows_backend, mock_element):
    """Test getting element attributes"""
    # Set up the mock element with proper control type
    type(mock_element).CurrentControlType = PropertyMock(return_value=50000)
    
    # Test successful get
    attrs = windows_backend.get_element_attributes(mock_element)
    assert attrs == {
        'name': "Test Element",
        'id': "TestId",
        'class_name': "TestClass",
        'control_type': 50000,
        'is_enabled': True,
        'is_offscreen': False,
        'bounding_rectangle': (0, 0, 100, 100)
    }

    # Test exception handling by creating a mock that raises AttributeError
    mock = MagicMock()
    type(mock).CurrentName = PropertyMock(side_effect=Exception("No name"))
    type(mock).CurrentAutomationId = PropertyMock(side_effect=Exception("No id"))
    type(mock).CurrentClassName = PropertyMock(side_effect=Exception("No class"))
    type(mock).CurrentControlType = PropertyMock(side_effect=Exception("No type"))
    type(mock).CurrentIsEnabled = PropertyMock(side_effect=Exception("Not enabled"))
    type(mock).CurrentIsOffscreen = PropertyMock(side_effect=Exception("Not offscreen"))
    type(mock).CurrentBoundingRectangle = PropertyMock(side_effect=Exception("No bounds"))

    attrs = windows_backend.get_element_attributes(mock)
    assert attrs == {}
