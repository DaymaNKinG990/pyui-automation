import pytest
from unittest.mock import MagicMock
import sys
import numpy as np
import platform
from types import ModuleType

from pyui_automation.backends.linux import LinuxBackend

# Skip all Linux tests if not on Linux
pytestmark = pytest.mark.skipif(
    platform.system() != "Linux",
    reason="Linux-specific tests can only run on Linux"
)

# Mock Linux-specific modules
class MockXlib:
    def __init__(self) -> None:
        """
        Initialize mock Xlib module with mock Display and X objects
        """
        self.Display = MagicMock()
        self.X = MagicMock()

# Create proper module mocks
mock_xlib_module = ModuleType('Xlib')
mock_xlib = MockXlib()
mock_display = MagicMock()
mock_x = MagicMock()

# Copy attributes from MockXlib instance to the module
setattr(mock_xlib_module, 'Display', mock_xlib.Display)
setattr(mock_xlib_module, 'X', mock_xlib.X)

# Set up the mock modules
sys.modules['Xlib'] = mock_xlib_module
display_module = ModuleType('Xlib.display')
setattr(display_module, 'Display', mock_display)
sys.modules['Xlib.display'] = display_module
sys.modules['Xlib.X'] = ModuleType('Xlib.X')
for attr_name, attr_value in vars(mock_x).items():
    setattr(sys.modules['Xlib.X'], attr_name, attr_value)

# Create mock pyatspi module
mock_pyatspi = ModuleType('pyatspi')
mock_pyatspi.__dict__['Backend'] = MagicMock()
sys.modules['pyatspi'] = mock_pyatspi


@pytest.fixture
def mock_window():
    window = MagicMock()
    window.get_geometry.return_value = MagicMock(
        width=1920,
        height=1080,
        x=0,
        y=0
    )
    window.get_attributes.return_value = MagicMock(
        map_state=1,  # IsViewable
        x=0,
        y=0,
        width=1920,
        height=1080
    )
    window.get_wm_name.return_value = "Test Window"
    window.get_wm_class.return_value = ("test_class", "Test_Class")
    return window

@pytest.fixture
def mock_screen(mock_window):
    screen = MagicMock()
    screen.root = mock_window
    screen.width_in_pixels = 1920
    screen.height_in_pixels = 1080
    return screen

@pytest.fixture
def mock_display_instance(mock_screen, mock_window):
    display = MagicMock()
    display.screen.return_value = mock_screen
    display.get_input_focus.return_value = mock_window
    display.create_resource_object.return_value = mock_window
    
    # Set up image data for screenshots
    image = MagicMock()
    image.data = b'\x00' * (1920 * 1080 * 4)
    mock_window.get_image.return_value = image
    
    return display

@pytest.fixture
def backend(mock_display_instance):
    # Configure the Display mock to return our mock display instance
    mock_display.return_value = mock_display_instance
    return LinuxBackend()

def test_init_success(mock_display_instance):
    """Test successful initialization on Linux"""
    backend = LinuxBackend()
    assert backend.display is mock_display_instance

def test_find_element(backend):
    """Test finding a UI element"""
    element = backend.find_element("name", "Test Window")
    assert element is not None
    assert element.get_wm_name() == "Test Window"

def test_find_elements(backend):
    """Test finding multiple UI elements"""
    elements = backend.find_elements("name", "Test Window")
    assert len(elements) > 0
    assert elements[0].get_wm_name() == "Test Window"

def test_get_active_window(backend):
    """Test getting active window"""
    window = backend.get_active_window()
    assert window is not None
    assert window.get_wm_name() == "Test Window"

def test_take_screenshot(backend):
    """Test taking screenshot"""
    screenshot = backend.take_screenshot()
    assert isinstance(screenshot, np.ndarray)
    assert screenshot.shape == (1080, 1920, 4)

def test_get_screen_size(backend):
    """Test getting screen size"""
    width, height = backend.get_screen_size()
    assert width == 1920
    assert height == 1080

def test_matches_criteria(backend, mock_window):
    """Test element criteria matching"""
    assert backend._matches_criteria(mock_window, "name", "Test Window")
    assert backend._matches_criteria(mock_window, "class", "test_class")
    assert not backend._matches_criteria(mock_window, "name", "Wrong Window")

def test_cleanup(backend, mock_display_instance):
    """Test cleanup"""
    backend.__del__()
    mock_display_instance.close.assert_called_once()

def test_check_accessibility_all_ok(monkeypatch):
    backend = LinuxBackend()
    element = MagicMock()
    element.get_role.return_value = "button"
    element.get_name.return_value = "Test"
    issues = backend.check_accessibility(element)
    assert issues == {}

def test_check_accessibility_missing_role(monkeypatch):
    backend = LinuxBackend()
    element = MagicMock()
    del element.get_role
    element.get_name.return_value = "Test"
    issues = backend.check_accessibility(element)
    assert str(element) in issues
    assert "role" in issues[str(element)] or "role" in str(issues[str(element)]) or "missing" in str(issues[str(element)])

def test_check_accessibility_missing_name(monkeypatch):
    backend = LinuxBackend()
    element = MagicMock()
    element.get_role.return_value = "button"
    element.get_name.return_value = None
    issues = backend.check_accessibility(element)
    assert str(element) in issues
    assert "name" in issues[str(element)] or "label" in str(issues[str(element)])

def test_check_accessibility_window_missing_title(monkeypatch):
    backend = LinuxBackend()
    # Проверка для окна без имени
    window = MagicMock()
    window.get_wm_name.return_value = None
    window.get_attributes.return_value = MagicMock(map_state=1)
    backend.display.screen.return_value.root.query_tree.return_value.children = [window]
    issues = backend.check_accessibility(None)
    assert str(window) in issues
    assert "Window missing title" in issues[str(window)]

def test_check_accessibility_error(monkeypatch):
    backend = LinuxBackend()
    # Передаём объект без нужных методов
    class Dummy: pass
    dummy = Dummy()
    issues = backend.check_accessibility(dummy)
    assert str(dummy) in issues

def test_capture_screenshot(backend, mock_window, monkeypatch):
    monkeypatch.setattr(backend.display.screen().root, 'get_geometry', lambda: MagicMock(width=10, height=10))
    class DummyRaw:
        data = b'\x00' * (10*10*4)
    monkeypatch.setattr(backend.display.screen().root, 'get_image', lambda *a, **k: DummyRaw())
    import PIL.Image
    monkeypatch.setattr(PIL.Image, 'frombytes', lambda *a, **k: MagicMock(size=(10, 10)))
    import numpy as np
    monkeypatch.setattr(np, 'array', lambda img: np.zeros((10, 10, 3)))
    arr = backend.capture_screenshot()
    assert arr.shape == (10, 10, 3)

def test_capture_screenshot_error(backend, monkeypatch):
    monkeypatch.setattr(backend.display.screen().root, 'get_geometry', lambda: (_ for _ in ()).throw(Exception()))
    assert backend.capture_screenshot() is None

def test_get_window_handle(backend, mock_window, monkeypatch):
    # Без pid
    monkeypatch.setattr(backend.display.screen().root, 'query_tree', lambda: MagicMock(children=[mock_window]))
    monkeypatch.setattr(mock_window, 'get_wm_class', lambda: True)
    monkeypatch.setattr(mock_window, 'get_attributes', lambda: MagicMock(map_state=1))
    assert backend.get_window_handle() == mock_window.id
    # С pid
    monkeypatch.setattr(mock_window, 'get_full_property', lambda atom, _: MagicMock(value=[42]))
    assert backend.get_window_handle(pid=42) == mock_window.id

def test_get_window_handle_error(backend, monkeypatch):
    monkeypatch.setattr(backend.display.screen().root, 'query_tree', lambda: (_ for _ in ()).throw(Exception()))
    assert backend.get_window_handle() is None

def test_get_window_handles(backend, mock_window, monkeypatch):
    monkeypatch.setattr(backend.display.screen().root, 'query_tree', lambda: MagicMock(children=[mock_window]))
    monkeypatch.setattr(mock_window, 'get_attributes', lambda: MagicMock(map_state=1, override_redirect=False))
    handles = backend.get_window_handles()
    assert mock_window in handles

def test_get_window_handles_error(backend, monkeypatch):
    monkeypatch.setattr(backend.display.screen().root, 'query_tree', lambda: (_ for _ in ()).throw(Exception()))
    assert backend.get_window_handles() == []

def test_find_window(backend, monkeypatch):
    class DummyApp:
        def __iter__(self):
            return iter([DummyWin()])
    class DummyWin:
        def getRole(self): return 1
        @property
        def name(self): return 'TestTitle'
    monkeypatch.setattr('pyatspi.Registry.getDesktop', lambda idx: [DummyApp()])
    monkeypatch.setattr('pyatspi.ROLE_FRAME', 1)
    win = backend.find_window('TestTitle')
    assert win is not None

def test_find_window_error(backend, monkeypatch):
    import sys
    sys.platform = 'linux'
    monkeypatch.setattr('pyatspi.Registry.getDesktop', lambda idx: (_ for _ in ()).throw(Exception()))
    assert backend.find_window('Test') is None

def test_set_ocr_languages(backend):
    backend.set_ocr_languages(['eng', 'deu'])
    assert backend._ocr_languages == ['eng', 'deu']

def test_move_mouse(backend, monkeypatch):
    called = {}
    monkeypatch.setattr(backend.display, 'warp_pointer', lambda x, y: called.update({'x': x, 'y': y}))
    monkeypatch.setattr(backend.display, 'flush', lambda: called.update({'flushed': True}))
    backend.move_mouse(1, 2)
    assert called['x'] == 1 and called['y'] == 2 and called['flushed']

def test_click_mouse(backend, monkeypatch):
    root = backend.display.screen().root
    monkeypatch.setattr(root, 'button_press', lambda btn: None)
    monkeypatch.setattr(root, 'button_release', lambda btn: None)
    monkeypatch.setattr(backend.display, 'flush', lambda: None)
    assert backend.click_mouse() is True

def test_double_click_mouse(backend, monkeypatch):
    called = {'count': 0}
    monkeypatch.setattr(backend, 'click_mouse', lambda: called.update({'count': called['count']+1}))
    backend.double_click_mouse()
    assert called['count'] == 2

def test_right_click_mouse(backend, monkeypatch):
    root = backend.display.screen().root
    monkeypatch.setattr(root, 'button_press', lambda btn: None)
    monkeypatch.setattr(root, 'button_release', lambda btn: None)
    monkeypatch.setattr(backend.display, 'flush', lambda: None)
    backend.right_click_mouse()

def test_mouse_down_up(backend, monkeypatch):
    root = backend.display.screen().root
    monkeypatch.setattr(root, 'button_press', lambda btn: None)
    monkeypatch.setattr(root, 'button_release', lambda btn: None)
    monkeypatch.setattr(backend.display, 'flush', lambda: None)
    backend.mouse_down()
    backend.mouse_up()

def test_get_mouse_position(backend, monkeypatch):
    class DummyPointer:
        root_x = 5
        root_y = 6
    monkeypatch.setattr(backend.display.screen().root, 'query_pointer', lambda: DummyPointer())
    assert backend.get_mouse_position() == (5, 6)
