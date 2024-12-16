import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from pyui_automation.backends.game_backend import GameBackend


class MockGameBackend(GameBackend):
    """Mock implementation of GameBackend for testing"""
    
    def __init__(self):
        self._mock_app = MagicMock()
        self._mock_window = MagicMock()
        self._mock_element = MagicMock()
        
    def application(self):
        return self._mock_app
        
    def capture_element_screenshot(self, element):
        return np.zeros((100, 100, 3))
        
    def capture_screenshot(self, region=None):
        return np.zeros((100, 100, 3))
        
    def check_accessibility(self, element=None):
        return {}
        
    def click_mouse(self, x, y):
        pass
        
    def double_click_mouse(self, x, y):
        pass
        
    def find_elements(self, by, value, region=None):
        return []
        
    def get_active_window(self):
        return self._mock_window
        
    def get_mouse_position(self):
        return (0, 0)
        
    def get_screen_size(self):
        return (1920, 1080)
        
    def get_window_handle(self):
        return "mock_handle"
        
    def mouse_down(self, x, y, button="left"):
        pass
        
    def mouse_up(self, x, y, button="left"):
        pass
        
    def move_mouse(self, x, y):
        pass
        
    def right_click_mouse(self, x, y):
        pass
        
    def press_key(self, key):
        pass
        
    def type_text(self, text):
        pass
        
    def get_window_title(self, window):
        return "Mock Window"
        
    def get_window_rect(self, window):
        return (0, 0, 800, 600)
        
    def maximize_window(self, window):
        pass
        
    def minimize_window(self, window):
        pass
        
    def restore_window(self, window):
        pass
        
    def close_window(self, window):
        pass
        
    def get_element_attributes(self, element):
        return {}
        
    def get_element_property(self, element, property_name):
        return None
        
    def set_element_property(self, element, property_name, value):
        pass
        
    def get_element_pattern(self, element, pattern_name):
        return None
        
    def invoke_element_pattern_method(self, pattern, method_name, *args):
        return None
        
    def get_element_rect(self, element):
        return (0, 0, 100, 100)
        
    def scroll_element(self, element, direction, amount):
        pass
        
    def get_element_text(self, element):
        return ""
        
    def set_element_text(self, element, text):
        pass
        
    def get_element_value(self, element):
        return None
        
    def set_element_value(self, element, value):
        pass
        
    def get_element_state(self, element):
        return {}
        
    def wait_for_element(self, by, value, timeout=10):
        return None
        
    def wait_for_element_state(self, element, state, timeout=10):
        return False
        
    def wait_for_element_property(self, element, property_name, value, timeout=10):
        return False
        
    def generate_accessibility_report(self, output_dir):
        pass
        
    def get_application(self):
        return self._mock_app
        
    def launch_application(self, path, *args, **kwargs):
        return self._mock_app
        
    def attach_to_application(self, process_id):
        return self._mock_app
        
    def close_application(self, application):
        pass
        
    def get_window_bounds(self, window):
        return (0, 0, 800, 600)
        
    def release_key(self, key):
        pass
        
    def resize_window(self, window, width, height):
        pass
        
    def send_keys(self, text):
        pass
        
    def set_window_position(self, window, x, y):
        pass
        
    def take_screenshot(self, filepath):
        pass


@pytest.fixture
def game_backend():
    return MockGameBackend()


@pytest.mark.parametrize("platform,expected", [
    ("Windows", True),
    ("Darwin", True),
    ("Linux", True)
])
def test_connect(platform, expected, game_backend):
    """Test connecting to game on different platforms."""
    with patch('platform.system', return_value=platform):
        assert game_backend.connect("Test Game Window") == expected


def test_connect_failure(game_backend):
    """Test connection failure handling."""
    with patch.object(game_backend, 'check_accessibility', return_value=False):
        assert not game_backend.connect("Test Game Window")


def test_capture_screen_with_region(game_backend):
    """Test screen capture with specific region."""
    region = (10, 20, 100, 100)
    screenshot = game_backend.capture_screen(region)
    assert isinstance(screenshot, np.ndarray)
    assert screenshot.shape == (100, 100, 3)


def test_capture_screen_without_region(game_backend):
    """Test full screen capture."""
    screenshot = game_backend.capture_screen()
    assert isinstance(screenshot, np.ndarray)
    assert screenshot.shape == (100, 100, 3)


def test_capture_screen_failure(game_backend):
    """Test screen capture failure handling."""
    with patch.object(game_backend, 'capture_screenshot', side_effect=Exception("Screenshot failed")):
        assert game_backend.capture_screen() is None


def test_find_element_success(game_backend):
    """Test successful element finding."""
    mock_element = MagicMock()
    with patch.object(game_backend, 'find_elements', return_value=[mock_element]):
        element = game_backend.find_element(by="image", value="button.png")
        assert element == mock_element


def test_find_element_not_found(game_backend):
    """Test element not found case."""
    with patch.object(game_backend, 'find_elements', return_value=[]):
        element = game_backend.find_element(by="image", value="nonexistent.png")
        assert element is None


def test_find_element_with_region(game_backend):
    """Test finding element in specific region."""
    mock_element = MagicMock()
    region = (10, 20, 100, 100)
    with patch.object(game_backend, 'find_elements', return_value=[mock_element]) as mock_find:
        element = game_backend.find_element(by="image", value="button.png", region=region)
        assert element == mock_element
        mock_find.assert_called_with(by="image", value="button.png", region=region)


def test_find_element_screen_capture_failure(game_backend):
    """Test element finding with screen capture failure."""
    with patch.object(game_backend, 'capture_screenshot', side_effect=Exception("Screenshot failed")):
        element = game_backend.find_element(by="image", value="button.png")
        assert element is None


def test_init(game_backend):
    """Test GameBackend initialization."""
    assert game_backend.window_title is None
    assert game_backend.region is None


@pytest.mark.parametrize("platform_name,expected", [
    ("Windows", True),
    ("Darwin", True),
    ("Linux", True)
])
def test_connect_original(game_backend, platform_name, expected):
    """Test connecting to game window on different platforms."""
    with patch('platform.system', return_value=platform_name):
        result = game_backend.connect("Test Game")
        assert result == expected
        
        if platform_name == "Windows":
            assert game_backend.region == (0, 0, 800, 600)
        elif platform_name == "Darwin":
            assert game_backend.region is None
        else:  # Linux
            assert game_backend.region == (0, 0, 800, 600)


def test_connect_failure_original(game_backend):
    """Test connection failure handling."""
    with patch('platform.system', return_value="Windows"):
        with patch('win32gui.FindWindow', side_effect=Exception("Connection failed")):
            result = game_backend.connect("Test Game")
            assert result is False


def test_capture_screen_with_region_original(game_backend, mock_screenshot):
    """Test screen capture with specific region."""
    game_backend.region = (0, 0, 800, 600)
    screenshot = game_backend.capture_screen()
    assert isinstance(screenshot, Image.Image)
    assert screenshot.size == (800, 600)


def test_capture_screen_without_region_original(game_backend, mock_screenshot):
    """Test full screen capture."""
    screenshot = game_backend.capture_screen()
    assert isinstance(screenshot, Image.Image)
    assert screenshot.size == (800, 600)


def test_capture_screen_failure_original(game_backend):
    """Test screen capture failure handling."""
    with patch('pyautogui.screenshot', side_effect=Exception("Screenshot failed")):
        screenshot = game_backend.capture_screen()
        assert screenshot is None


def test_find_element_success_original(game_backend):
    """Test successful element finding."""
    # Create a test screen with a white background
    screen = Image.new('RGB', (800, 600), color='white')
    # Create a test template with a black rectangle
    template = Image.new('RGB', (50, 50), color='black')
    
    # Draw the template onto the screen at position (100, 100)
    screen.paste(template, (100, 100))
    
    with patch.object(game_backend, 'capture_screen', return_value=screen):
        result = game_backend.find_element(template, threshold=0.8)
        assert result is not None
        x, y = result
        assert abs(x - 100) <= 1  # Allow small deviation due to matching
        assert abs(y - 100) <= 1


def test_find_element_not_found_original(game_backend):
    """Test element not found case."""
    # Create different images for screen and template
    screen = Image.new('RGB', (800, 600), color='white')
    template = Image.new('RGB', (50, 50), color='black')
    
    with patch.object(game_backend, 'capture_screen', return_value=screen):
        result = game_backend.find_element(template, threshold=0.9)
        assert result is None


def test_find_element_with_region_original(game_backend):
    """Test element finding with window region offset."""
    screen = Image.new('RGB', (800, 600), color='white')
    template = Image.new('RGB', (50, 50), color='black')
    screen.paste(template, (100, 100))
    
    game_backend.region = (50, 50, 850, 650)  # Offset the window
    
    with patch.object(game_backend, 'capture_screen', return_value=screen):
        result = game_backend.find_element(template, threshold=0.8)
        assert result is not None
        x, y = result
        assert abs(x - 150) <= 1  # 100 + 50 (region offset)
        assert abs(y - 150) <= 1


def test_find_element_screen_capture_failure_original(game_backend):
    """Test element finding when screen capture fails."""
    template = Image.new('RGB', (50, 50), color='black')
    
    with patch.object(game_backend, 'capture_screen', return_value=None):
        result = game_backend.find_element(template)
        assert result is None
