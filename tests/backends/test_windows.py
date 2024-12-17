import pytest
from unittest.mock import MagicMock, patch
import comtypes.gen.UIAutomationClient as UIAutomationClient

from pyui_automation.backends.windows import WindowsBackend
from pyui_automation.core.element import Element

@pytest.fixture
def mock_uia():
    with patch('pyui_automation.backends.windows.UIAutomationClient') as mock:
        mock.IUIAutomation.CreateInstance.return_value = MagicMock()
        yield mock

@pytest.fixture
def windows_backend(mock_uia):
    backend = WindowsBackend()
    backend._automation = mock_uia.IUIAutomation.CreateInstance()
    return backend

def test_find_element_by_id(windows_backend):
    """Test finding element by ID"""
    mock_element = MagicMock()
    mock_element.CurrentAutomationId = "TestId"
    windows_backend._automation.ElementFromHandle.return_value = mock_element
    
    element = windows_backend.find_element(automation_id="TestId")
    assert isinstance(element, Element)
    assert element.automation_id == "TestId"

def test_find_element_by_name(windows_backend):
    """Test finding element by name"""
    mock_element = MagicMock()
    mock_element.CurrentName = "Test Element"
    windows_backend._automation.ElementFromHandle.return_value = mock_element
    
    element = windows_backend.find_element(name="Test Element")
    assert isinstance(element, Element)
    assert element.name == "Test Element"

def test_find_element_by_class(windows_backend):
    """Test finding element by class name"""
    mock_element = MagicMock()
    mock_element.CurrentClassName = "TestClass"
    windows_backend._automation.ElementFromHandle.return_value = mock_element
    
    element = windows_backend.find_element(class_name="TestClass")
    assert isinstance(element, Element)
    assert element.class_name == "TestClass"

def test_get_active_window(windows_backend):
    """Test getting active window"""
    mock_window = MagicMock()
    windows_backend._automation.GetFocusedElement.return_value = mock_window
    
    window = windows_backend.get_active_window()
    assert isinstance(window, Element)

def test_get_screen_size(windows_backend):
    """Test getting screen size"""
    size = windows_backend.get_screen_size()
    assert isinstance(size, tuple)
    assert len(size) == 2
    assert all(isinstance(x, int) for x in size)

def test_find_element(windows_backend):
    """Test finding a single element"""
    # Test successful find
    mock_element = MagicMock()
    mock_element.CurrentAutomationId = "TestId"
    windows_backend._automation.ElementFromHandle.return_value = mock_element
    
    element = windows_backend.find_element(automation_id="TestId")
    assert isinstance(element, Element)
    assert element.automation_id == "TestId"

    # Test not found
    windows_backend._automation.ElementFromHandle.return_value = None
    element = windows_backend.find_element(automation_id="nonexistent")
    assert element is None

    # Test error cases
    windows_backend._automation.ElementFromHandle.return_value = None
    element = windows_backend.find_element(automation_id="TestId")
    assert element is None

def test_find_elements(windows_backend):
    """Test finding multiple elements"""
    # Test successful find
    mock_element = MagicMock()
    mock_element.CurrentClassName = "TestClass"
    mock_elements = MagicMock()
    mock_elements.Length = 2
    mock_elements.GetElement.side_effect = [mock_element, mock_element]
    
    windows_backend._automation.ElementFromHandle.return_value = mock_element
    mock_element.FindAll.return_value = mock_elements

    elements = windows_backend.find_elements(class_name="TestClass")
    assert len(elements) == 2
    assert all(isinstance(e, Element) for e in elements)
    assert all(e.class_name == "TestClass" for e in elements)

    # Test no elements found
    windows_backend.root.FindAll.return_value = []
    elements = windows_backend.find_elements(class_name="NonexistentClass")
    assert elements == []

    # Test exception handling
    windows_backend.root.FindAll.side_effect = Exception("Test error")
    elements = windows_backend.find_elements(class_name="TestClass")
    assert elements == []

def test_create_condition(windows_backend):
    """Test condition creation for different search strategies"""
    # Test all supported strategies
    for by, value in [
        ("automation_id", "TestId"),
        ("name", "Test Name"),
        ("class_name", "TestClass"),
        ("control_type", "button")
    ]:
        condition = windows_backend._create_condition(by, value)
        assert condition == windows_backend._automation.CreatePropertyCondition.return_value
        windows_backend._automation.CreatePropertyCondition.assert_called()

    # Test invalid strategy
    condition = windows_backend._create_condition("invalid", "value")
    assert condition is None

    # Test exception handling
    windows_backend._automation.CreatePropertyCondition.side_effect = Exception("Test error")
    condition = windows_backend._create_condition("automation_id", "TestId")
    assert condition is None

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

def test_get_window_title(windows_backend):
    """Test getting window title"""
    # Test successful get
    mock_window = MagicMock()
    mock_window.CurrentName = "Test Window"
    title = windows_backend.get_window_title(mock_window)
    assert title == "Test Window"

    # Test exception handling
    mock_window.CurrentName = None
    title = windows_backend.get_window_title(mock_window)
    assert title is None

def test_wait_for_window(windows_backend):
    """Test waiting for window"""
    with patch('time.sleep'):
        # Test successful wait
        windows_backend.find_window = MagicMock(side_effect=[None, None, mock_window])
        window = windows_backend.wait_for_window("Test Window", timeout=1)
        assert isinstance(window, Element)

        # Test timeout
        windows_backend.find_window = MagicMock(return_value=None)
        window = windows_backend.wait_for_window("Nonexistent Window", timeout=1)
        assert window is None

        # Test exception handling
        windows_backend.find_window.side_effect = Exception("Test error")
        window = windows_backend.wait_for_window("Test Window", timeout=1)
        assert window is None

def test_get_element_attributes(windows_backend):
    """Test getting element attributes"""
    # Set up the mock element with proper control type
    mock_element = MagicMock()
    mock_element.CurrentControlType = 50000
    
    # Test successful get
    attrs = windows_backend.get_element_attributes(mock_element)
    assert attrs == {
        'name': mock_element.CurrentName,
        'automation_id': mock_element.CurrentAutomationId,
        'class_name': mock_element.CurrentClassName,
        'control_type': 50000,
        'is_enabled': mock_element.CurrentIsEnabled,
        'is_offscreen': mock_element.CurrentIsOffscreen,
        'bounding_rectangle': mock_element.CurrentBoundingRectangle
    }

    # Test exception handling by creating a mock that raises AttributeError
    mock_element.CurrentName = None
    mock_element.CurrentAutomationId = None
    mock_element.CurrentClassName = None
    mock_element.CurrentControlType = None
    mock_element.CurrentIsEnabled = None
    mock_element.CurrentIsOffscreen = None
    mock_element.CurrentBoundingRectangle = None

    attrs = windows_backend.get_element_attributes(mock_element)
    assert attrs == {}
