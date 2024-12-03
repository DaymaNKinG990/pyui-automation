import pytest
from unittest.mock import MagicMock, patch
import sys
import numpy as np
from PIL import Image
from pyui_automation.backends.macos import MacOSBackend


# Create mock modules
mock_objc = MagicMock()
mock_objc.ObjCClass = MagicMock()

mock_quartz = MagicMock()
mock_quartz.kCGWindowListOptionOnScreenOnly = 1
mock_quartz.kCGNullWindowID = 0
mock_quartz.kCGWindowImageDefault = 0
mock_quartz.CGWindowListCreateImage = MagicMock()
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


# Configure test environment before any tests run
sys.modules['objc'] = mock_objc
sys.modules['Quartz'] = mock_quartz
sys.modules['AppKit'] = mock_appkit
sys.modules['Foundation'] = mock_foundation
sys.modules['Cocoa'] = mock_cocoa
sys.platform = 'darwin'


@pytest.fixture(autouse=True)
def setup_platform():
    """Ensure platform is set to darwin for each test"""
    original_platform = sys.platform
    sys.platform = 'darwin'
    yield
    sys.platform = original_platform


@pytest.fixture
def mock_ax():
    """Create a mock AXUIElement class"""
    ax = MagicMock()
    ax.systemWide.return_value = MagicMock()
    ax.applicationElementForPID_.return_value = MagicMock()
    mock_objc.ObjCClass.return_value = ax
    return ax


@pytest.fixture
def mock_element():
    """Create a mock UI element"""
    element = MagicMock()
    element.attributeValue_.side_effect = lambda attr: {
        'AXRole': 'button',
        'AXTitle': 'Test Button',
        'AXDescription': 'Test Description',
        'AXIdentifier': 'test_id',
        'AXChildren': [],
        'AXWindows': [MagicMock()]
    }.get(attr)
    return element


@pytest.fixture
def mock_workspace():
    """Create a mock NSWorkspace"""
    workspace = MagicMock()
    app = MagicMock()
    app.processIdentifier.return_value = 12345
    workspace.frontmostApplication.return_value = app
    mock_nsworkspace.sharedWorkspace.return_value = workspace
    return workspace


@pytest.fixture
def backend(mock_ax):
    """Create a MacOSBackend instance with mocked dependencies"""
    return MacOSBackend()


def test_init_success(mock_ax):
    """Test successful initialization on macOS"""
    backend = MacOSBackend()
    assert isinstance(backend.ax, MagicMock)
    assert isinstance(backend.system, MagicMock)
    mock_objc.ObjCClass.assert_called_with('AXUIElement')


def test_init_failure():
    """Test initialization failure on non-macOS platform"""
    with patch('sys.platform', 'win32'):
        with pytest.raises(RuntimeError) as exc:
            MacOSBackend()
        assert "MacOSBackend can only be used on macOS systems" in str(exc.value)


def test_find_element(backend, mock_element):
    """Test finding a single element"""
    # Mock frontmost application
    backend._get_frontmost_application = MagicMock(return_value=mock_element)

    # Test successful find
    element = backend.find_element("role", "button")
    assert element == mock_element

    # Test with children
    child = MagicMock()
    child.attributeValue_.side_effect = lambda attr: {
        'AXRole': 'textfield',
        'AXChildren': []
    }.get(attr)
    mock_element.attributeValue_.side_effect = lambda attr: {
        'AXRole': 'window',
        'AXChildren': [child]
    }.get(attr)

    element = backend.find_element("role", "textfield")
    assert element == child

    # Test element not found
    element = backend.find_element("role", "nonexistent")
    assert element is None

    # Test no frontmost application
    backend._get_frontmost_application.return_value = None
    element = backend.find_element("role", "button")
    assert element is None


def test_find_elements(backend, mock_element):
    """Test finding multiple elements"""
    # Mock frontmost application
    backend._get_frontmost_application = MagicMock(return_value=mock_element)

    # Create mock hierarchy
    child1 = MagicMock()
    child1.attributeValue_.side_effect = lambda attr: {
        'AXRole': 'button',
        'AXChildren': []
    }.get(attr)
    child2 = MagicMock()
    child2.attributeValue_.side_effect = lambda attr: {
        'AXRole': 'button',
        'AXChildren': []
    }.get(attr)
    mock_element.attributeValue_.side_effect = lambda attr: {
        'AXRole': 'window',
        'AXChildren': [child1, child2]
    }.get(attr)

    # Test finding multiple elements
    elements = backend.find_elements("role", "button")
    assert len(elements) == 2
    assert child1 in elements
    assert child2 in elements

    # Test no elements found
    elements = backend.find_elements("role", "nonexistent")
    assert elements == []

    # Test no frontmost application
    backend._get_frontmost_application.return_value = None
    elements = backend.find_elements("role", "button")
    assert elements == []


def test_get_active_window(backend, mock_element):
    """Test getting active window"""
    # Mock frontmost application
    backend._get_frontmost_application = MagicMock(return_value=mock_element)

    # Test successful get
    window = backend.get_active_window()
    assert window == mock_element.attributeValue_('AXWindows')[0]

    # Test no windows
    mock_element.attributeValue_.side_effect = lambda attr: {
        'AXWindows': []
    }.get(attr)
    window = backend.get_active_window()
    assert window is None

    # Test no frontmost application
    backend._get_frontmost_application.return_value = None
    window = backend.get_active_window()
    assert window is None


def test_take_screenshot(backend):
    """Test screenshot functionality"""
    # Mock NSScreen
    screen = MagicMock()
    frame = MagicMock()
    frame.size.width = 1920
    frame.size.height = 1080
    screen.frame.return_value = frame
    backend.nsscreen.mainScreen.return_value = screen

    # Mock Quartz image functions
    image = MagicMock()
    backend.quartz.CGWindowListCreateImage.return_value = image
    backend.quartz.CGImageGetWidth.return_value = 1920
    backend.quartz.CGImageGetHeight.return_value = 1080
    backend.quartz.CGImageGetBytesPerRow.return_value = 1920 * 4
    backend.quartz.CGImageGetDataProvider.return_value = MagicMock()
    backend.quartz.CGDataProviderCopyData.return_value = b'\x00' * (1920 * 1080 * 4)

    with patch('PIL.Image.frombytes') as mock_frombytes:
        # Mock PIL image
        pil_image = MagicMock()
        mock_frombytes.return_value = pil_image

        # Test successful screenshot
        assert backend.take_screenshot("test.png") is True
        pil_image.save.assert_called_with("test.png")

        # Test failure during image creation
        backend.quartz.CGWindowListCreateImage.side_effect = Exception("Test error")
        assert backend.take_screenshot("test.png") is False


def test_get_screen_size(backend):
    """Test getting screen dimensions"""
    with patch('AppKit.NSScreen') as mock_screen:
        # Mock screen dimensions
        screen = MagicMock()
        frame = MagicMock()
        frame.size.width = 1920
        frame.size.height = 1080
        screen.frame.return_value = frame
        mock_screen.mainScreen.return_value = screen

        # Test successful get
        width, height = backend.get_screen_size()
        assert width == 1920
        assert height == 1080


def test_get_frontmost_application(backend, mock_workspace):
    """Test getting frontmost application"""
    with patch('AppKit.NSWorkspace') as mock_ns_workspace:
        mock_ns_workspace.sharedWorkspace.return_value = mock_workspace

        # Test successful get
        app = backend._get_frontmost_application()
        assert app == backend.ax.applicationElementForPID_.return_value
        backend.ax.applicationElementForPID_.assert_called_with(12345)

        # Test no frontmost application
        mock_workspace.frontmostApplication.return_value = None
        app = backend._get_frontmost_application()
        assert app is None


def test_matches_criteria(backend, mock_element):
    """Test element criteria matching"""
    # Test all supported criteria
    assert backend._matches_criteria(mock_element, "role", "button") is True
    assert backend._matches_criteria(mock_element, "title", "Test Button") is True
    assert backend._matches_criteria(mock_element, "description", "Test Description") is True
    assert backend._matches_criteria(mock_element, "identifier", "test_id") is True

    # Test non-matching criteria
    assert backend._matches_criteria(mock_element, "role", "textfield") is False
    assert backend._matches_criteria(mock_element, "title", "Wrong Title") is False

    # Test invalid criteria type
    assert backend._matches_criteria(mock_element, "invalid", "value") is False

    # Test exception handling
    mock_element.attributeValue_.side_effect = Exception("Test error")
    assert backend._matches_criteria(mock_element, "role", "button") is False


def test_get_attribute(backend, mock_element):
    """Test getting element attributes"""
    # Test successful get
    assert backend._get_attribute(mock_element, "AXRole") == "button"
    assert backend._get_attribute(mock_element, "AXTitle") == "Test Button"

    # Test non-existent attribute
    assert backend._get_attribute(mock_element, "NonexistentAttr") is None

    # Test exception handling
    mock_element.attributeValue_.side_effect = Exception("Test error")
    assert backend._get_attribute(mock_element, "AXRole") is None
