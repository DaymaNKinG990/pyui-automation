import pytest
import platform
from unittest.mock import MagicMock
import sys
import numpy as np
from pyui_automation.backends.macos import MacOSBackend

# Skip all macOS tests if not on macOS
pytestmark = pytest.mark.skipif(
    platform.system() != "Darwin",
    reason="macOS-specific tests can only run on macOS"
)

# Mock macOS-specific modules
mock_objc = MagicMock()
mock_objc.ObjCClass = MagicMock(return_value=MagicMock())

mock_quartz = MagicMock()
mock_quartz.kCGWindowListOptionOnScreenOnly = 1
mock_quartz.kCGNullWindowID = 0
mock_quartz.kCGWindowImageDefault = 0
mock_quartz.CGWindowListCreateImage = MagicMock(return_value=MagicMock())
mock_quartz.CGImageGetWidth = MagicMock(return_value=1920)
mock_quartz.CGImageGetHeight = MagicMock(return_value=1080)
mock_quartz.CGImageGetBytesPerRow = MagicMock(return_value=1920 * 4)
mock_quartz.CGImageGetDataProvider = MagicMock()
mock_quartz.CGDataProviderCopyData = MagicMock(return_value=b'\x00' * (1920 * 1080 * 4))

mock_nsworkspace = MagicMock()
mock_nsscreen = MagicMock()
mock_nsobject = MagicMock()
mock_nspoint = MagicMock()

mock_appkit = MagicMock()
mock_appkit.NSWorkspace = mock_nsworkspace
mock_appkit.NSScreen = mock_nsscreen

mock_foundation = MagicMock()
mock_foundation.NSObject = mock_nsobject
mock_foundation.NSPoint = mock_nspoint

mock_cocoa = MagicMock()

# Mock the macOS modules
sys.modules['objc'] = mock_objc
sys.modules['Quartz'] = mock_quartz
sys.modules['AppKit'] = mock_appkit
sys.modules['Foundation'] = mock_foundation
sys.modules['Cocoa'] = mock_cocoa


@pytest.fixture
def mock_ax():
    ax = MagicMock()
    ax.systemWide = MagicMock()
    ax.systemWide.return_value = MagicMock()
    return ax

@pytest.fixture
def mock_element():
    element = MagicMock()
    element.AXRole = "AXButton"
    element.AXTitle = "Test Button"
    element.AXEnabled = True
    element.AXPosition = (0, 0)
    element.AXSize = (100, 50)
    return element

@pytest.fixture
def mock_workspace():
    workspace = MagicMock()
    workspace.frontmostApplication.return_value = MagicMock()
    return workspace

@pytest.fixture
def backend(mock_ax, monkeypatch):
    monkeypatch.setattr(sys, 'platform', 'darwin')
    mock_objc.ObjCClass.return_value = mock_ax
    return MacOSBackend()

def test_find_element(backend, mock_element):
    """Test finding a UI element"""
    backend.system.AXFocusedUIElement.return_value = mock_element
    element = backend.find_element("role", "AXButton")
    assert element is not None
    assert element.AXRole == "AXButton"

def test_find_elements(backend, mock_element):
    """Test finding multiple UI elements"""
    backend.system.AXFocusedUIElement.return_value = mock_element
    elements = backend.find_elements("role", "AXButton")
    assert len(elements) > 0
    assert elements[0].AXRole == "AXButton"

def test_get_active_window(backend, mock_element):
    """Test getting active window"""
    backend.system.AXFocusedWindow.return_value = mock_element
    window = backend.get_active_window()
    assert window is not None
    assert window.AXRole == "AXButton"

def test_take_screenshot(backend):
    """Test taking screenshot"""
    screenshot = backend.take_screenshot()
    assert isinstance(screenshot, np.ndarray)
    assert screenshot.shape == (1080, 1920, 4)

def test_get_screen_size(backend):
    """Test getting screen size"""
    size = backend.get_screen_size()
    assert isinstance(size, tuple)
    assert len(size) == 2
    assert size == (1920, 1080)

def test_get_frontmost_application(backend, mock_workspace):
    """Test getting frontmost application"""
    app = backend._get_frontmost_application()
    assert app is not None

def test_matches_criteria(backend, mock_element):
    """Test element criteria matching"""
    assert backend._matches_criteria(mock_element, "role", "AXButton")
    assert backend._matches_criteria(mock_element, "name", "Test Button")
    assert not backend._matches_criteria(mock_element, "role", "AXWindow")

def test_get_attribute(backend, mock_element):
    """Test getting element attribute"""
    value = backend._get_attribute(mock_element, "AXRole")
    assert value == "AXButton"
    value = backend._get_attribute(mock_element, "NonExistentAttribute")
    assert value is None

def test_check_accessibility_all_ok(monkeypatch):
    backend = MacOSBackend()
    element = MagicMock()
    element.AXRole.return_value = "AXButton"
    element.AXTitle.return_value = "Test"
    element.AXHelp.return_value = "Help"
    element.AXEnabled.return_value = True
    element.AXFocused.return_value = True
    element.AXPosition.return_value = (0, 0)
    element.AXSize.return_value = (100, 50)
    issues = backend.check_accessibility(element)
    assert issues == {}

def test_check_accessibility_role_unknown(monkeypatch):
    backend = MacOSBackend()
    element = MagicMock()
    element.AXRole.return_value = "AXUnknown"
    element.AXTitle.return_value = "Test"
    element.AXHelp.return_value = "Help"
    element.AXEnabled.return_value = True
    element.AXFocused.return_value = True
    element.AXPosition.return_value = (0, 0)
    element.AXSize.return_value = (100, 50)
    issues = backend.check_accessibility(element)
    assert "role" in issues

def test_check_accessibility_missing_title(monkeypatch):
    backend = MacOSBackend()
    element = MagicMock()
    element.AXRole.return_value = "AXButton"
    element.AXTitle.return_value = ""
    element.AXHelp.return_value = "Help"
    element.AXEnabled.return_value = True
    element.AXFocused.return_value = True
    element.AXPosition.return_value = (0, 0)
    element.AXSize.return_value = (100, 50)
    issues = backend.check_accessibility(element)
    assert "missing_title" in issues

def test_check_accessibility_missing_help(monkeypatch):
    backend = MacOSBackend()
    element = MagicMock()
    element.AXRole.return_value = "AXButton"
    element.AXTitle.return_value = "Test"
    element.AXHelp.return_value = ""
    element.AXEnabled.return_value = True
    element.AXFocused.return_value = True
    element.AXPosition.return_value = (0, 0)
    element.AXSize.return_value = (100, 50)
    issues = backend.check_accessibility(element)
    assert "missing_help" in issues

def test_check_accessibility_disabled(monkeypatch):
    backend = MacOSBackend()
    element = MagicMock()
    element.AXRole.return_value = "AXButton"
    element.AXTitle.return_value = "Test"
    element.AXHelp.return_value = "Help"
    element.AXEnabled.return_value = False
    element.AXFocused.return_value = True
    element.AXPosition.return_value = (0, 0)
    element.AXSize.return_value = (100, 50)
    issues = backend.check_accessibility(element)
    assert "disabled" in issues

def test_check_accessibility_not_focused(monkeypatch):
    backend = MacOSBackend()
    element = MagicMock()
    element.AXRole.return_value = "AXButton"
    element.AXTitle.return_value = "Test"
    element.AXHelp.return_value = "Help"
    element.AXEnabled.return_value = True
    element.AXFocused.return_value = False
    element.AXPosition.return_value = (0, 0)
    element.AXSize.return_value = (100, 50)
    issues = backend.check_accessibility(element)
    assert "focus" in issues

def test_check_accessibility_missing_bounds(monkeypatch):
    backend = MacOSBackend()
    element = MagicMock()
    element.AXRole.return_value = "AXButton"
    element.AXTitle.return_value = "Test"
    element.AXHelp.return_value = "Help"
    element.AXEnabled.return_value = True
    element.AXFocused.return_value = True
    element.AXPosition.return_value = None
    element.AXSize.return_value = None
    issues = backend.check_accessibility(element)
    assert "bounds" in issues

def test_check_accessibility_error(monkeypatch):
    backend = MacOSBackend()
    # Передаём None, чтобы вызвать ошибку
    issues = backend.check_accessibility(None)
    assert "error" in issues

def test_capture_screenshot(backend, monkeypatch):
    monkeypatch.setattr('PIL.Image.frombytes', lambda *a, **k: MagicMock(size=(10, 10)))
    import numpy as np
    monkeypatch.setattr(np, 'array', lambda img: np.zeros((10, 10, 4)))
    monkeypatch.setattr('Quartz.CGWindowListCreateImage', lambda *a, **k: MagicMock())
    monkeypatch.setattr('Quartz.CGImageGetWidth', lambda img: 10)
    monkeypatch.setattr('Quartz.CGImageGetHeight', lambda img: 10)
    monkeypatch.setattr('Quartz.CGDataProviderCopyData', lambda provider: b'\x00' * (10*10*4))
    monkeypatch.setattr('Quartz.CGImageGetDataProvider', lambda img: MagicMock())
    arr = backend.capture_screenshot()
    assert arr.shape == (10, 10, 4)

def test_capture_screenshot_error(backend, monkeypatch):
    monkeypatch.setattr('Quartz.CGWindowListCreateImage', lambda *a, **kw: (_ for _ in ()).throw(Exception()))
    assert backend.capture_screenshot() is None

def test_get_window_handle(backend, monkeypatch):
    app = MagicMock()
    app.localizedName.return_value = 'TestApp'
    ws = MagicMock()
    ws.frontmostApplication.return_value = app
    monkeypatch.setattr('AppKit.NSWorkspace.sharedWorkspace', lambda: ws)
    window = { 'kCGWindowOwnerName': 'TestApp', 'kCGWindowNumber': 42 }
    monkeypatch.setattr('Quartz.CGWindowListCopyWindowInfo', lambda *a, **k: [window])
    monkeypatch.setattr('Quartz.kCGWindowListOptionOnScreenOnly', 1)
    monkeypatch.setattr('Quartz.kCGWindowListExcludeDesktopElements', 2)
    monkeypatch.setattr('Quartz.kCGNullWindowID', 0)
    assert backend.get_window_handle() == 42
    # По pid
    window2 = { 'kCGWindowOwnerPID': 123, 'kCGWindowNumber': 99 }
    monkeypatch.setattr('Quartz.CGWindowListCopyWindowInfo', lambda *a, **k: [window2])
    monkeypatch.setattr('Quartz.kCGWindowListOptionAll', 3)
    assert backend.get_window_handle(pid=123) == 99

def test_get_window_handle_error(backend, monkeypatch):
    monkeypatch.setattr('Quartz.CGWindowListCopyWindowInfo', lambda *a, **kw: (_ for _ in ()).throw(Exception()))
    assert backend.get_window_handle() is None

def test_get_window_handles(backend, monkeypatch):
    app = MagicMock()
    app.isActive.return_value = True
    app.processIdentifier.return_value = 1
    ax_app = MagicMock()
    ax_app.attributeValue_.return_value = [MagicMock(), MagicMock()]
    backend.ax.applicationWithPID_ = MagicMock(return_value=ax_app)
    ws = MagicMock()
    ws.runningApplications.return_value = [app]
    monkeypatch.setattr('AppKit.NSWorkspace.sharedWorkspace', lambda: ws)
    handles = backend.get_window_handles()
    assert len(handles) == 2

def test_get_window_handles_error(backend, monkeypatch):
    monkeypatch.setattr('Quartz.CGWindowListCopyWindowInfo', lambda *a, **kw: (_ for _ in ()).throw(Exception()))
    assert backend.get_window_handles() == []

def test_find_window(backend, monkeypatch):
    backend.find_element = MagicMock(return_value='win')
    assert backend.find_window('title') == 'win'

def test_find_window_error(backend, monkeypatch):
    monkeypatch.setattr(backend, 'find_element', lambda *a, **kw: (_ for _ in ()).throw(Exception()))
    assert backend.find_window('Test') is None

def test_cleanup(backend):
    backend.ax = MagicMock()
    backend.system = MagicMock()
    backend.cleanup()
    assert backend.ax is None
    assert backend.system is None

def test_set_ocr_languages(backend):
    backend.set_ocr_languages(['eng', 'fra'])
