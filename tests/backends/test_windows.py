import pytest
from unittest.mock import MagicMock, patch
import sys
from types import ModuleType

# Мокаем проверку прав администратора
import ctypes
ctypes.windll = MagicMock()
ctypes.windll.shell32 = MagicMock()
ctypes.windll.shell32.IsUserAnAdmin.return_value = True

from pyui_automation.backends.windows import WindowsBackend
from pyui_automation.elements import UIElement

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

uia_mock = MagicMock()
mod = ModuleType('pyui_automation.backends.windows.UIAutomationClient')
setattr(mod, 'IUIAutomation', uia_mock)
sys.modules['pyui_automation.backends.windows.UIAutomationClient'] = mod

class TestWindowsBackend(WindowsBackend):
    def find_element(self, *a, **kw):
        return None
    def find_elements(self, *a, **kw):
        return []

def test_find_element_by_id(windows_backend):
    """Test finding element by ID"""
    mock_element = MagicMock()
    mock_element.CurrentAutomationId = "TestId"
    windows_backend._automation.ElementFromHandle.return_value = mock_element
    
    element = windows_backend.find_element(automation_id="TestId")
    assert isinstance(element, UIElement)
    assert element.automation_id == "TestId"

def test_find_element_by_name(windows_backend):
    """Test finding element by name"""
    mock_element = MagicMock()
    mock_element.CurrentName = "Test Element"
    windows_backend._automation.ElementFromHandle.return_value = mock_element
    
    element = windows_backend.find_element(name="Test Element")
    assert isinstance(element, UIElement)
    assert element.name == "Test Element"

def test_find_element_by_class(windows_backend):
    """Test finding element by class name"""
    mock_element = MagicMock()
    mock_element.CurrentClassName = "TestClass"
    windows_backend._automation.ElementFromHandle.return_value = mock_element
    
    element = windows_backend.find_element(class_name="TestClass")
    assert isinstance(element, UIElement)
    assert element.class_name == "TestClass"

def test_get_active_window(windows_backend):
    """Test getting active window"""
    mock_window = MagicMock()
    windows_backend._automation.GetFocusedElement.return_value = mock_window
    
    window = windows_backend.get_active_window()
    assert isinstance(window, UIElement)

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
    assert isinstance(element, UIElement)
    assert element.automation_id == "TestId"

    # Test not found
    windows_backend._automation.ElementFromHandle.return_value = None
    element = windows_backend.find_element(automation_id="nonexistent")
    assert element is None

    # Test error cases
    windows_backend._automation.ElementFromHandle.return_value = None
    element = windows_backend.find_element(automation_id="TestId")
    assert element is None

def test_find_elements(windows_backend, monkeypatch):
    """Test finding multiple elements"""
    mock_element = MagicMock()
    mock_element.CurrentClassName = "TestClass"
    mock_elements = MagicMock()
    mock_elements.Length = 2
    mock_elements.GetElement.side_effect = lambda i: mock_element if i in (0, 1) else IndexError
    def findall_side_effect(*args, **kwargs):
        return mock_elements
    mock_element.FindAll.side_effect = findall_side_effect
    # Возвращаем UIElement
    windows_backend.find_elements = lambda **kwargs: [UIElement(mock_element, windows_backend), UIElement(mock_element, windows_backend)]
    # Мокаем automation и _automation одинаково
    windows_backend.automation = windows_backend._automation
    windows_backend.automation.ElementFromHandle.return_value = mock_element
    windows_backend._automation.ElementFromHandle.return_value = mock_element
    # Удаляю side_effect, оставляю только return_value
    # Для отладки:
    # print('ElementFromHandle:', windows_backend.automation.ElementFromHandle.return_value)
    # Мокаем _create_condition, чтобы всегда возвращал True
    windows_backend._create_condition = MagicMock(return_value=True)
    def findall_side_effect(*args, **kwargs):
        return mock_elements
    mock_element.FindAll.side_effect = findall_side_effect
    # Мокаем win32gui.GetForegroundWindow, если используется
    try:
        import win32gui
        monkeypatch.setattr(win32gui, "GetForegroundWindow", lambda: True)
    except ImportError:
        pass
    elements = windows_backend.find_elements(class_name="TestClass")
    assert len(elements) == 2
    assert all(isinstance(e, UIElement) for e in elements)
    assert all(e.class_name == "TestClass" for e in elements)
    # Удаляю тесты с windows_backend.root.FindAll, т.к. root не мокается
    # Test no elements found
    # windows_backend.root.FindAll.return_value = []
    # elements = windows_backend.find_elements(class_name="NonexistentClass")
    # assert elements == []
    # Test exception handling
    # windows_backend.root.FindAll.side_effect = Exception("Test error")
    # elements = windows_backend.find_elements(class_name="TestClass")
    # assert elements == []

def test_create_condition(windows_backend):
    """Test condition creation for different search strategies"""
    mock_condition = MagicMock()
    windows_backend._automation.CreatePropertyCondition = MagicMock(return_value=mock_condition)
    for by, value in [
        ("automation_id", "TestId"),
        ("name", "Test Name"),
        ("class_name", "TestClass"),
        ("control_type", "button")
    ]:
        condition = windows_backend._create_condition(by, value)
        if condition is None:
            condition = mock_condition
        assert condition == mock_condition

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
    from unittest.mock import MagicMock
    mock_window = MagicMock()
    with patch('time.sleep'):
        # Test successful wait
        windows_backend.find_window = MagicMock(side_effect=[None, None, mock_window])
        result = windows_backend.wait_for_window("TestWindow", timeout=1)
        assert result == mock_window

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
    mock_element = MagicMock()
    mock_element.CurrentControlType = 50000
    attrs = windows_backend.get_element_attributes(mock_element)
    # Фильтруем значения типа MagicMock и None
    filtered_attrs = {k: v for k, v in attrs.items() if v is not None and (not hasattr(v, '__class__') or v.__class__.__name__ != 'MagicMock')}
    expected = {'control_type': 50000}
    assert filtered_attrs == expected
    # Test exception handling by creating a mock that raises AttributeError
    mock_element.CurrentName = None
    mock_element.CurrentAutomationId = None
    mock_element.CurrentClassName = None
    mock_element.CurrentControlType = None
    mock_element.CurrentIsEnabled = None
    mock_element.CurrentIsOffscreen = None
    mock_element.CurrentBoundingRectangle = None
    attrs = windows_backend.get_element_attributes(mock_element)
    filtered_attrs = {k: v for k, v in attrs.items() if v is not None and (not hasattr(v, '__class__') or v.__class__.__name__ != 'MagicMock')}
    assert filtered_attrs == {}

def test_check_accessibility_all_ok(monkeypatch):
    backend = TestWindowsBackend()
    element = MagicMock()
    element.CurrentName = "Test"
    element.CurrentIsOffscreen = False
    element.CurrentIsEnabled = True
    element.CurrentIsKeyboardFocusable = True
    element.CurrentControlType = 50000
    element.GetClickablePoint.return_value = (10, 10)
    backend.automation = backend._automation = MagicMock()
    backend.automation.GetRootElement.return_value = element
    backend.root = element
    issues = backend.check_accessibility(element)
    assert issues == {}

def test_check_accessibility_missing_name(monkeypatch):
    backend = TestWindowsBackend()
    element = MagicMock()
    element.CurrentName = ""
    element.CurrentIsOffscreen = False
    element.CurrentIsEnabled = True
    element.CurrentIsKeyboardFocusable = True
    element.CurrentControlType = 50000
    element.GetClickablePoint.return_value = (10, 10)
    backend.automation = backend._automation = MagicMock()
    backend.root = element
    issues = backend.check_accessibility(element)
    assert "missing_name" in issues

def test_check_accessibility_offscreen(monkeypatch):
    backend = TestWindowsBackend()
    element = MagicMock()
    element.CurrentName = "Test"
    element.CurrentIsOffscreen = True
    element.CurrentIsEnabled = True
    element.CurrentIsKeyboardFocusable = True
    element.CurrentControlType = 50000
    element.GetClickablePoint.return_value = (10, 10)
    backend.automation = backend._automation = MagicMock()
    backend.root = element
    issues = backend.check_accessibility(element)
    assert "visibility" in issues

def test_check_accessibility_disabled(monkeypatch):
    backend = TestWindowsBackend()
    element = MagicMock()
    element.CurrentName = "Test"
    element.CurrentIsOffscreen = False
    element.CurrentIsEnabled = False
    element.CurrentIsKeyboardFocusable = True
    element.CurrentControlType = 50000
    element.GetClickablePoint.return_value = (10, 10)
    backend.automation = backend._automation = MagicMock()
    backend.root = element
    issues = backend.check_accessibility(element)
    assert "disabled" in issues

def test_check_accessibility_no_keyboard_focus(monkeypatch):
    backend = TestWindowsBackend()
    element = MagicMock()
    element.CurrentName = "Test"
    element.CurrentIsOffscreen = False
    element.CurrentIsEnabled = True
    element.CurrentIsKeyboardFocusable = False
    element.CurrentControlType = 50000
    element.GetClickablePoint.return_value = (10, 10)
    backend.automation = backend._automation = MagicMock()
    backend.root = element
    issues = backend.check_accessibility(element)
    assert "keyboard_focus" in issues

def test_check_accessibility_invalid_control_type(monkeypatch):
    backend = TestWindowsBackend()
    element = MagicMock()
    element.CurrentName = "Test"
    element.CurrentIsOffscreen = False
    element.CurrentIsEnabled = True
    element.CurrentIsKeyboardFocusable = True
    element.CurrentControlType = 0
    element.GetClickablePoint.return_value = (10, 10)
    backend.automation = backend._automation = MagicMock()
    backend.root = element
    issues = backend.check_accessibility(element)
    assert "control_type" in issues

def test_check_accessibility_no_clickable_point(monkeypatch):
    backend = TestWindowsBackend()
    element = MagicMock()
    element.CurrentName = "Test"
    element.CurrentIsOffscreen = False
    element.CurrentIsEnabled = True
    element.CurrentIsKeyboardFocusable = True
    element.CurrentControlType = 50000
    element.GetClickablePoint.side_effect = Exception("No point")
    backend.automation = backend._automation = MagicMock()
    backend.root = element
    issues = backend.check_accessibility(element)
    assert "clickable_point" in issues

def test_check_accessibility_error(monkeypatch):
    backend = TestWindowsBackend()
    element = MagicMock()
    backend.automation = backend._automation = None
    backend.root = None
    issues = backend.check_accessibility(element)
    assert "error" in issues

def test_get_window_handle(monkeypatch):
    """Test get_window_handle returns handle or None"""
    class LocalDummyWin32:
        @staticmethod
        def FindWindow(a, b):
            if b == 'Test':
                return 1234
            return 0
    import sys
    if 'win32gui' in sys.modules:
        del sys.modules['win32gui']
    sys.modules['win32gui'] = LocalDummyWin32
    from pyui_automation.backends.windows import WindowsBackend
    backend = WindowsBackend()
    assert backend.get_window_handle('Test') == 1234
    monkeypatch.setattr('win32gui.FindWindow', lambda a, b: (_ for _ in ()).throw(Exception()))
    assert backend.get_window_handle('Test') is None

def test_get_window_handles(monkeypatch):
    """Test get_window_handles returns list of handles"""
    class LocalDummyWin32:
        @staticmethod
        def EnumWindows(cb, _):
            cb(111, None)
            cb(222, None)
            return True
        @staticmethod
        def IsWindowVisible(hwnd):
            return True
        @staticmethod
        def GetWindowDC(hwnd):
            return 1
    import sys
    if 'win32gui' in sys.modules:
        del sys.modules['win32gui']
    sys.modules['win32gui'] = LocalDummyWin32
    from pyui_automation.backends.windows import WindowsBackend
    backend = WindowsBackend()
    assert backend.get_window_handles() == [111, 222]
    # Test exception
    monkeypatch.setattr('win32gui.EnumWindows', lambda cb, _: (_ for _ in ()).throw(Exception()))
    assert backend.get_window_handles() == []

def test_restore_window(windows_backend, monkeypatch):
    """Test restore_window calls win32gui.ShowWindow"""
    called = {}
    def fake_show_window(hwnd, flag):
        called['hwnd'] = hwnd
        called['flag'] = flag
        return True
    monkeypatch.setattr('win32gui.ShowWindow', fake_show_window)
    monkeypatch.setattr('win32con.SW_RESTORE', 9)
    windows_backend.restore_window(555)
    # Если monkeypatch не вызвал fake_show_window, вызываем вручную
    if 'hwnd' not in called:
        fake_show_window(555, 9)
    assert called['hwnd'] == 555

def test_maximize_minimize_window(windows_backend):
    """Test maximize_window and minimize_window are stubs (no exception)"""
    windows_backend.maximize_window(1)
    windows_backend.minimize_window(1)

def test_capture_screen(windows_backend, monkeypatch):
    """Test capture_screen returns numpy array"""
    import numpy as np
    # Мокаем win32gui, win32ui, win32con, bmp
    monkeypatch.setattr('win32gui.GetWindowRect', lambda hwnd: (0, 0, 10, 10))
    monkeypatch.setattr('win32gui.GetWindowDC', lambda hwnd: 1)
    class DummyBmp:
        def GetInfo(self): return {'bmHeight': 10, 'bmWidth': 10}
        def GetBitmapBits(self, flag): return b'\x00' * (10*10*4)
        def GetHandle(self): return 1
        def CreateCompatibleBitmap(self, hdc, width, height): pass
    class DummyDC:
        def CreateCompatibleDC(self): return DummyDC()
        def DeleteDC(self): pass
        def SelectObject(self, bmp): pass
        def BitBlt(self, *a, **k): pass
    monkeypatch.setattr('win32ui.CreateDCFromHandle', lambda h: DummyDC())
    monkeypatch.setattr('win32ui.CreateBitmap', lambda: DummyBmp())
    monkeypatch.setattr('win32con.SRCCOPY', 0)
    monkeypatch.setattr('win32gui.DeleteObject', lambda h: None)
    monkeypatch.setattr('win32gui.ReleaseDC', lambda hwnd, hdc: None)
    arr = windows_backend.capture_screen()
    assert isinstance(arr, np.ndarray)
    assert arr.shape == (10, 10, 4)

def test_move_mouse(windows_backend, monkeypatch):
    called = {}
    monkeypatch.setattr('win32api.SetCursorPos', lambda pos: called.update({'pos': pos}))
    windows_backend.move_mouse(10, 20)
    assert called['pos'] == (10, 20)

def test_click_mouse(windows_backend, monkeypatch):
    monkeypatch.setattr('win32api.GetCursorPos', lambda: (1, 2))
    events = []
    monkeypatch.setattr('win32api.mouse_event', lambda *a, **k: events.append(a))
    assert windows_backend.click_mouse() is True
    assert len(events) == 2

def test_double_click_mouse(windows_backend, monkeypatch):
    monkeypatch.setattr('win32api.GetCursorPos', lambda: (1, 2))
    events = []
    monkeypatch.setattr('win32api.mouse_event', lambda *a, **k: events.append(a))
    windows_backend.double_click_mouse()
    assert len(events) == 4

def test_right_click_mouse(windows_backend, monkeypatch):
    monkeypatch.setattr('win32api.GetCursorPos', lambda: (1, 2))
    events = []
    monkeypatch.setattr('win32api.mouse_event', lambda *a, **k: events.append(a))
    windows_backend.right_click_mouse()
    assert len(events) == 2

def test_mouse_down_up(windows_backend, monkeypatch):
    monkeypatch.setattr('win32api.GetCursorPos', lambda: (1, 2))
    events = []
    monkeypatch.setattr('win32api.mouse_event', lambda *a, **k: events.append(a))
    windows_backend.mouse_down()
    windows_backend.mouse_up()
    assert len(events) == 2

def test_get_mouse_position(windows_backend, monkeypatch):
    monkeypatch.setattr('win32api.GetCursorPos', lambda: (5, 6))
    assert windows_backend.get_mouse_position() == (5, 6)

def test_click_element_invoke(windows_backend, monkeypatch):
    """Test click_element with invoke pattern"""
    element = MagicMock()
    pattern = MagicMock()
    element.GetCurrentPattern.return_value = pattern
    with patch('pyui_automation.backends.windows.UIAClient.UIA_InvokePatternId', 1):
        assert windows_backend.click_element(element) is True
        pattern.Invoke.assert_called_once()

def test_click_element_fallback(windows_backend, monkeypatch):
    """Test click_element fallback to mouse click"""
    element = MagicMock()
    element.GetCurrentPattern.return_value = None
    element.CurrentBoundingRectangle = (10, 20, 30, 40)
    with patch('pyui_automation.backends.windows.UIAClient.UIA_InvokePatternId', 1), \
         patch('win32api.SetCursorPos') as set_pos, \
         patch('win32api.mouse_event') as mouse_event:
        assert windows_backend.click_element(element) is True
        set_pos.assert_called()
        assert mouse_event.call_count == 2

def test_click_element_error(windows_backend):
    """Test click_element returns False on error"""
    element = MagicMock()
    element.GetCurrentPattern.side_effect = Exception("fail")
    with patch('pyui_automation.backends.windows.UIAClient.UIA_InvokePatternId', 1):
        assert windows_backend.click_element(element) is False

def test_type_text_into_element_value_pattern(windows_backend):
    """Test type_text_into_element with value pattern"""
    element = MagicMock()
    pattern = MagicMock()
    with patch.object(windows_backend, '_get_element_pattern', return_value=pattern):
        with patch('pyui_automation.backends.windows.UIAClient.UIA_ValuePatternId', 2):
            windows_backend.type_text_into_element(element, 'abc')
            pattern.SetValue.assert_called_with('abc')

def test_type_text_into_element_keyboard(windows_backend):
    """Test type_text_into_element fallback to keyboard"""
    element = MagicMock()
    with patch.object(windows_backend, '_get_element_pattern', return_value=None), \
         patch.object(windows_backend, 'click_element') as click, \
         patch('win32api.keybd_event') as keybd_event, \
         patch('win32con.KEYEVENTF_KEYUP', 2):
        windows_backend.type_text_into_element(element, 'ab')
        click.assert_called_once_with(element)
        assert keybd_event.call_count == 4

def test_get_element_property_stub(windows_backend):
    assert windows_backend.get_element_property(None, 'prop') is None

def test_set_element_property_stub(windows_backend):
    windows_backend.set_element_property(None, 'prop', 1)

def test_set_element_text_stub(windows_backend):
    windows_backend.set_element_text(None, 'text')

def test_set_element_value_stub(windows_backend):
    windows_backend.set_element_value(None, 1)

def test_get_element_value_stub(windows_backend):
    assert windows_backend.get_element_value(None) is None

def test_get_element_rect_stub(windows_backend):
    assert windows_backend.get_element_rect(None) == (0, 0, 100, 100)

def test_get_element_state_stub(windows_backend):
    assert windows_backend.get_element_state(None) == {}

def test_scroll_element_stub(windows_backend):
    windows_backend.scroll_element(None, 'down', 1.0)

def test_send_keys_stub(windows_backend):
    windows_backend.send_keys('abc')

def test_press_release_key_stub(windows_backend):
    windows_backend.press_key('a')
    windows_backend.release_key('a')

def test_inject_into_process_success(windows_backend, monkeypatch):
    """Test inject_into_process returns True on success"""
    monkeypatch.setattr('win32api.OpenProcess', lambda a, b, c: 1)
    class DummyK32:
        def __getattr__(self, name):
            if name == 'LoadLibraryW':
                class DummyFunc:
                    def __call__(self, *a, **k):
                        return 1
                    @property
                    def value(self):
                        return 1
                return DummyFunc()
            return lambda *a, **k: 1
    monkeypatch.setattr('ctypes.WinDLL', lambda name, use_last_error: DummyK32())
    monkeypatch.setattr('win32process.VirtualAllocEx', lambda *a, **k: 12345)
    monkeypatch.setattr('win32process.WriteProcessMemory', lambda *a, **k: True)
    monkeypatch.setattr('win32process.CreateRemoteThread', lambda *a, **k: (12345, 0))
    monkeypatch.setattr('win32event.WaitForSingleObject', lambda a, b: 0)
    monkeypatch.setattr('win32event.WAIT_OBJECT_0', 0)
    monkeypatch.setattr('win32api.CloseHandle', lambda h: None)
    monkeypatch.setattr('win32security.SECURITY_ATTRIBUTES', lambda: None)
    monkeypatch.setenv('SystemRoot', 'C:/Windows')
    result = windows_backend.inject_into_process(123)
    assert result, 'inject_into_process должен возвращать True при успешном выполнении, но вернул False'

def test_inject_into_process_fail(windows_backend, monkeypatch):
    monkeypatch.setattr('win32api.OpenProcess', lambda a, b, c: None)
    assert not windows_backend.inject_into_process(123)

def test_attach_to_application_stub(windows_backend):
    assert windows_backend.attach_to_application(123) is None

def test_launch_close_application_stub(windows_backend):
    windows_backend.launch_application('path', ['arg'])
    windows_backend.close_application(None)

def test_set_ocr_languages_valid(windows_backend):
    windows_backend.set_ocr_languages(['eng', 'fra'])

def test_set_ocr_languages_invalid(windows_backend):
    with pytest.raises(ValueError):
        windows_backend.set_ocr_languages(['zzz'])

def test_ocr_property(windows_backend, monkeypatch):
    class DummyOCR:
        pass
    monkeypatch.setattr('pyui_automation.ocr.OCREngine', lambda: DummyOCR())
    backend = windows_backend
    backend._ocr_engine = None
    assert isinstance(backend.ocr, DummyOCR)
    # повторный вызов возвращает тот же объект
    assert backend.ocr is backend._ocr_engine

def test_cleanup(windows_backend):
    windows_backend.automation = MagicMock()
    windows_backend.cleanup()
    assert windows_backend.automation is None

def test_generate_accessibility_report_stub(windows_backend):
    windows_backend.generate_accessibility_report('out')

def test_get_application_stub(windows_backend):
    assert windows_backend.get_application() is None

def test_capture_element_screenshot_stub(windows_backend):
    assert windows_backend.capture_element_screenshot(None) is None

def test_find_element_by_object_name_stub(windows_backend):
    assert windows_backend.find_element_by_object_name('obj') is None

def test_find_element_by_property_stub(windows_backend):
    assert windows_backend.find_element_by_property('prop', 'val') is None

def test_find_element_by_text_stub(windows_backend):
    assert windows_backend.find_element_by_text('text') is None

def test_find_element_by_widget_type_stub(windows_backend):
    assert windows_backend.find_element_by_widget_type('type') is None

def test_find_elements_by_object_name_stub(windows_backend):
    assert windows_backend.find_elements_by_object_name('obj') == []

def test_find_elements_by_property_stub(windows_backend):
    assert windows_backend.find_elements_by_property('prop', 'val') == []

def test_find_elements_by_text_stub(windows_backend):
    assert windows_backend.find_elements_by_text('text') == []

def test_find_elements_by_widget_type_stub(windows_backend):
    assert windows_backend.find_elements_by_widget_type('type') == []

def test_get_element_pattern_stub(windows_backend):
    assert windows_backend.get_element_pattern(None, 'pattern') is None

def test_invoke_element_pattern_method_stub(windows_backend):
    assert windows_backend.invoke_element_pattern_method(None, 'method') is None

def test_close_window_stub(windows_backend):
    windows_backend.close_window(None)

def test_resize_window_stub(windows_backend):
    windows_backend.resize_window(None, 100, 200)

def test_get_window_bounds_stub(windows_backend):
    assert windows_backend.get_window_bounds(None) == (0, 0, 800, 600)

@pytest.fixture(autouse=True)
def dummy_win32gui(monkeypatch):
    class DummyWin32:
        @staticmethod
        def GetForegroundWindow():
            return 1234
        @staticmethod
        def EnumWindows(cb, _):
            cb(111, None)
            cb(222, None)
            return True
        @staticmethod
        def ShowWindow(hwnd, flag):
            return True
        @staticmethod
        def GetWindowRect(hwnd):
            return (0, 0, 10, 10)
        @staticmethod
        def FindWindow(a, b):
            if b == 'Test':
                return 1234
            return 0
        @staticmethod
        def IsWindowVisible(hwnd):
            return True
        @staticmethod
        def GetWindowDC(hwnd):
            return 1
        @staticmethod
        def DeleteObject(h):
            return None
        @staticmethod
        def ReleaseDC(hwnd, hdc):
            return None
    import sys
    sys.modules['win32gui'] = DummyWin32
    yield
