import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from pyui_automation.backends.game_backend import GameBackend

class TestGameBackend(GameBackend):
    """Тестовая реализация GameBackend для тестирования"""
    
    def __init__(self):
        super().__init__()
        self.mock_screenshot = np.ones((100, 100, 3), dtype=np.uint8) * 255
        self._mock_app = MagicMock()
        self._mock_window = MagicMock()
    
    def attach_to_application(self, app_name: str) -> bool:
        return True
    
    def capture_screenshot(self, region=None):
        return self.mock_screenshot.copy()
    
    def capture_element_screenshot(self, element, region=None):
        return self.mock_screenshot[10:30, 10:30].copy()
    
    def check_accessibility(self) -> bool:
        return True
    
    def get_window_rect(self):
        return {"left": 0, "top": 0, "width": 100, "height": 100}
    
    def move_mouse(self, x: int, y: int):
        pass
    
    def click_mouse(self, x: int, y: int):
        pass
    
    def double_click_mouse(self, x: int, y: int):
        pass
    
    def right_click_mouse(self, x: int, y: int):
        pass
    
    def drag_mouse(self, start_x: int, start_y: int, end_x: int, end_y: int):
        pass
    
    def type_text(self, text: str):
        pass

    def close_application(self):
        pass

    def close_window(self, window):
        pass

    def find_elements(self, by, value, region=None):
        return []

    def generate_accessibility_report(self, output_dir):
        pass

    def get_active_window(self):
        return self._mock_window

    def get_application(self):
        return self._mock_app

    def get_element_attributes(self, element):
        return {}

    def get_element_pattern(self, element, pattern_name):
        return None

    def get_element_property(self, element, property_name):
        return None

    def get_element_rect(self, element):
        return (0, 0, 100, 100)

    def get_element_state(self, element):
        return {}

    def get_element_text(self, element):
        return ""

    def get_element_value(self, element):
        return None

    def get_mouse_position(self):
        return (0, 0)

    def get_screen_size(self):
        return (1920, 1080)

    def get_window_bounds(self, window):
        return (0, 0, 800, 600)

    def get_window_handle(self):
        return "mock_handle"

    def get_window_title(self, window):
        return "Mock Window"

    def invoke_element_pattern_method(self, pattern, method_name, *args):
        return None

    def launch_application(self, path, *args, **kwargs):
        return self._mock_app

    def maximize_window(self, window):
        pass

    def minimize_window(self, window):
        pass

    def mouse_down(self, x, y, button="left"):
        pass

    def mouse_up(self, x, y, button="left"):
        pass

    def press_key(self, key):
        pass

    def release_key(self, key):
        pass

    def restore_window(self, window):
        pass

    def scroll_element(self, element, direction, amount):
        pass

    def send_keys(self, text):
        pass

    def set_element_property(self, element, property_name, value):
        pass

    def set_element_text(self, element, text):
        pass

    def set_element_value(self, element, value):
        pass

    def set_window_position(self, window, x, y):
        pass

    def take_screenshot(self, filepath):
        pass

    def wait_for_element(self, by, value, timeout=10):
        return None

    def wait_for_element_property(self, element, property_name, value, timeout=10):
        return False

    def wait_for_element_state(self, element, state, timeout=10):
        return False

@pytest.fixture
def game_backend():
    return TestGameBackend()

def test_find_element_success(game_backend):
    """Тест успешного поиска элемента"""
    template = np.ones((20, 20, 3), dtype=np.uint8) * 255
    with patch('cv2.matchTemplate', return_value=np.array([[0.99]])):
        element = game_backend.find_element(template)
        assert element is not None

def test_find_element_not_found(game_backend):
    """Тест когда элемент не найден"""
    template = np.ones((20, 20, 3), dtype=np.uint8) * 255
    with patch('cv2.matchTemplate', return_value=np.array([[0.5]])):
        element = game_backend.find_element(template)
        assert element is None

def test_find_element_with_region(game_backend):
    """Тест поиска элемента в заданной области"""
    template = np.ones((20, 20, 3), dtype=np.uint8) * 255
    region = (10, 10, 50, 50)
    with patch('cv2.matchTemplate', return_value=np.array([[0.99]])):
        element = game_backend.find_element(template, region=region)
        assert element is not None

def test_find_element_screen_capture_failure(game_backend):
    """Тест обработки ошибки при захвате экрана"""
    template = np.ones((20, 20, 3), dtype=np.uint8) * 255
    with patch.object(game_backend, 'capture_screenshot', side_effect=Exception("Screen capture failed")):
        element = game_backend.find_element(template)
        assert element is None

def test_capture_screen_with_region_original(game_backend):
    """Тест захвата экрана с указанной областью"""
    region = (10, 10, 50, 50)
    screenshot = game_backend.capture_screenshot(region=region)
    assert isinstance(screenshot, np.ndarray)
    assert screenshot.shape[2] == 3  # RGB изображение

def test_capture_screen_without_region_original(game_backend):
    """Тест захвата всего экрана"""
    screenshot = game_backend.capture_screenshot()
    assert isinstance(screenshot, np.ndarray)
    assert screenshot.shape[2] == 3  # RGB изображение
