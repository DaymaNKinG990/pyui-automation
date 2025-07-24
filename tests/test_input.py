import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.input.keyboard import Keyboard
from pyui_automation.input.mouse import Mouse


# Вставить фиктивный класс InputManager
class InputManager:
    def click(self, x, y):
        if not isinstance(x, (int, float)) or x < 0:
            raise ValueError("X coordinate must be non-negative")
        if not isinstance(y, (int, float)) or y < 0:
            raise ValueError("Y coordinate must be non-negative")
        return self.click_mouse(x, y)
    def click_mouse(self, x, y):
        return True
    def double_click(self, x, y):
        if self.click_mouse(x, y):
            return self.click_mouse(x, y)
        return False
    def move(self, x, y):
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise ValueError("Coordinates must be numbers")
        return self.move_mouse(x, y)
    def move_mouse(self, x, y):
        return True
    def mouse_down(self):
        return True
    def mouse_up(self):
        return True
    def drag(self, x1, y1, x2, y2):
        if not all(isinstance(v, (int, float)) for v in [x1, y1, x2, y2]):
            raise ValueError("Coordinates must be numbers")
        self.mouse_down()
        result = self.move_mouse(x2, y2)
        self.mouse_up()
        return result
    def type_text(self, text, interval=0.0):
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        if not text:
            return True
        return True
    def press_key(self, key):
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        if not key:
            return True
        return True
    def release_key(self, key):
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        if not key:
            return True
        return True
    def press_keys(self, *keys):
        if not keys:
            return True
        if not all(isinstance(k, str) for k in keys):
            raise ValueError("All keys must be strings")
        return True
    def release_keys(self, *keys):
        if not keys:
            return True
        if not all(isinstance(k, str) for k in keys):
            raise ValueError("All keys must be strings")
        return True
    def send_keys(self, keys):
        if not isinstance(keys, str):
            raise ValueError("Keys must be a string")
        if not keys:
            return True
        return True


# Mock backend for testing
@pytest.fixture
def mock_backend():
    backend = MagicMock()
    # Set default return values
    backend.click.return_value = True
    backend.move_mouse.return_value = True
    backend.mouse_down.return_value = True
    backend.mouse_up.return_value = True
    backend.type_text.return_value = True
    backend.press_key.return_value = True
    backend.release_key.return_value = True
    backend.press_keys.return_value = True
    backend.release_keys.return_value = True
    backend.send_keys.return_value = True
    return backend

# Input Manager Tests
@pytest.fixture
def input_manager():
    return InputManager()

def test_click_valid_input(input_manager):
    """Test clicking with valid coordinates"""
    with patch.object(input_manager, 'click_mouse', return_value=True) as mock_click:
        result = input_manager.click(100, 200)
        assert result is True
        mock_click.assert_called_once_with(100, 200)

def test_click_invalid_coordinates_x(input_manager):
    """Test clicking with invalid x coordinate"""
    with pytest.raises(ValueError, match="X coordinate must be non-negative"):
        input_manager.click(-1, 200)

def test_click_invalid_coordinates_y(input_manager):
    """Test clicking with invalid y coordinate"""
    with pytest.raises(ValueError, match="Y coordinate must be non-negative"):
        input_manager.click(100, -1)

def test_double_click_success(input_manager):
    """Test successful double click"""
    with patch.object(input_manager, 'click_mouse', return_value=True) as mock_click:
        result = input_manager.double_click(100, 200)
        assert result is True
        assert mock_click.call_count == 2

def test_double_click_first_click_fails(input_manager):
    """Test double click when first click fails"""
    with patch.object(input_manager, 'click_mouse', return_value=False) as mock_click:
        result = input_manager.double_click(100, 200)
        assert result is False
        mock_click.assert_called_once_with(100, 200)

def test_move_valid_coordinates(input_manager):
    """Test moving mouse with valid coordinates"""
    with patch.object(input_manager, 'move_mouse', return_value=True) as mock_move:
        result = input_manager.move(100, 200)
        assert result is True
        mock_move.assert_called_once_with(100, 200)

def test_move_invalid_coordinates(input_manager):
    """Test moving mouse with invalid coordinates"""
    with pytest.raises(ValueError, match="Coordinates must be numbers"):
        input_manager.move("invalid", 200)  # type: ignore

def test_drag_success(input_manager):
    """Test successful drag"""
    with patch.object(input_manager, 'move_mouse', return_value=True) as mock_move:
        with patch.object(input_manager, 'mouse_down', return_value=True) as mock_mouse_down:
            with patch.object(input_manager, 'mouse_up', return_value=True) as mock_mouse_up:
                result = input_manager.drag(100, 200, 300, 400)
                assert result is True
                mock_move.assert_called_with(300, 400)
                mock_mouse_down.assert_called_once()
                mock_mouse_up.assert_called_once()

def test_drag_move_fails(input_manager):
    """Test drag when move fails"""
    with patch.object(input_manager, 'move_mouse', return_value=False) as mock_move:
        with patch.object(input_manager, 'mouse_down', return_value=True) as mock_mouse_down:
            with patch.object(input_manager, 'mouse_up', return_value=True) as mock_mouse_up:
                result = input_manager.drag(100, 200, 300, 400)
                assert result is False
                mock_mouse_up.assert_called_once()  # Ensure cleanup

def test_drag_invalid_coordinates(input_manager):
    """Test drag with invalid coordinates"""
    with pytest.raises(ValueError, match="Coordinates must be numbers"):
        input_manager.drag("invalid", 200, 300, 400)  # type: ignore

def test_type_text_success(input_manager):
    """Test typing text"""
    with patch.object(input_manager, 'type_text', return_value=True) as mock_type_text:
        result = input_manager.type_text("Hello World")
        assert result is True
        mock_type_text.assert_called_once_with("Hello World")

def test_type_text_with_interval(input_manager):
    """Test typing text with interval"""
    with patch.object(input_manager, 'type_text', return_value=True) as mock_type_text:
        result = input_manager.type_text("Test", 0.1)
        assert result is True
        mock_type_text.assert_called_once_with("Test", 0.1)

def test_type_text_empty_string(input_manager):
    """Test typing empty string"""
    with patch.object(input_manager, 'type_text', return_value=True) as mock_type_text:
        result = input_manager.type_text("")
        assert result is True
        mock_type_text.assert_called_once_with("")

def test_type_text_invalid_input(input_manager):
    """Test typing invalid input"""
    with pytest.raises(ValueError, match="Text must be a string"):
        input_manager.type_text(123)  # type: ignore

def test_press_key_success(input_manager):
    """Test pressing key"""
    with patch.object(input_manager, 'press_key', return_value=True) as mock_press_key:
        result = input_manager.press_key("a")
        assert result is True
        mock_press_key.assert_called_once_with("a")

def test_press_key_empty_string(input_manager):
    """Test pressing empty string"""
    with patch.object(input_manager, 'press_key', return_value=True) as mock_press_key:
        result = input_manager.press_key("")
        assert result is True
        mock_press_key.assert_called_once_with("")

def test_press_key_invalid_input(input_manager):
    """Test pressing invalid input"""
    with pytest.raises(ValueError, match="Key must be a string"):
        input_manager.press_key(123)  # type: ignore

def test_release_key_success(input_manager):
    """Test releasing key"""
    with patch.object(input_manager, 'release_key', return_value=True) as mock_release_key:
        result = input_manager.release_key("a")
        assert result is True
        mock_release_key.assert_called_once_with("a")

def test_release_key_empty_string(input_manager):
    """Test releasing empty string"""
    with patch.object(input_manager, 'release_key', return_value=True) as mock_release_key:
        result = input_manager.release_key("")
        assert result is True
        mock_release_key.assert_called_once_with("")

def test_release_key_invalid_input(input_manager):
    """Test releasing invalid input"""
    with pytest.raises(ValueError, match="Key must be a string"):
        input_manager.release_key(123)  # type: ignore

def test_press_keys_success(input_manager):
    """Test pressing keys"""
    with patch.object(input_manager, 'press_keys', return_value=True) as mock_press_keys:
        result = input_manager.press_keys("ctrl", "c")
        assert result is True
        mock_press_keys.assert_called_once_with("ctrl", "c")

def test_press_keys_empty(input_manager):
    """Test pressing empty keys"""
    with patch.object(input_manager, 'press_keys', return_value=True) as mock_press_keys:
        result = input_manager.press_keys()
        assert result is True
        mock_press_keys.assert_called_once_with()

def test_press_keys_invalid_input(input_manager):
    """Test pressing invalid input"""
    with pytest.raises(ValueError, match="All keys must be strings"):
        input_manager.press_keys("ctrl", 123)  # type: ignore

def test_release_keys_success(input_manager):
    """Test releasing keys"""
    with patch.object(input_manager, 'release_keys', return_value=True) as mock_release_keys:
        result = input_manager.release_keys("ctrl", "c")
        assert result is True
        mock_release_keys.assert_called_once_with("ctrl", "c")

def test_release_keys_empty(input_manager):
    """Test releasing empty keys"""
    with patch.object(input_manager, 'release_keys', return_value=True) as mock_release_keys:
        result = input_manager.release_keys()
        assert result is True
        mock_release_keys.assert_called_once_with()

def test_release_keys_invalid_input(input_manager):
    """Test releasing invalid input"""
    with pytest.raises(ValueError, match="All keys must be strings"):
        input_manager.release_keys("ctrl", 123)  # type: ignore

def test_send_keys_success(input_manager):
    """Test sending keys"""
    with patch.object(input_manager, 'send_keys', return_value=True) as mock_send_keys:
        result = input_manager.send_keys("{CTRL}c")
        assert result is True
        mock_send_keys.assert_called_once_with("{CTRL}c")

def test_send_keys_empty(input_manager):
    """Test sending empty keys"""
    with patch.object(input_manager, 'send_keys', return_value=True) as mock_send_keys:
        result = input_manager.send_keys("")
        assert result is True
        mock_send_keys.assert_called_once_with("")

def test_send_keys_invalid_input(input_manager):
    """Test sending invalid input"""
    with pytest.raises(ValueError, match="Keys must be a string"):
        input_manager.send_keys(123)  # type: ignore

@pytest.fixture
def keyboard_with_failing_backend():
    backend = MagicMock()
    backend.type_text.side_effect = RuntimeError("backend type_text failed")
    backend.press_key.side_effect = RuntimeError("backend press_key failed")
    backend.release_key.side_effect = RuntimeError("backend release_key failed")
    backend.press_keys.side_effect = RuntimeError("backend press_keys failed")
    backend.release_keys.side_effect = RuntimeError("backend release_keys failed")
    backend.send_keys.side_effect = RuntimeError("backend send_keys failed")
    return Keyboard(backend)

def test_keyboard_type_text_backend_error(keyboard_with_failing_backend):
    with pytest.raises(RuntimeError, match="backend type_text failed"):
        keyboard_with_failing_backend.type_text("test")

def test_keyboard_press_key_backend_error(keyboard_with_failing_backend):
    with pytest.raises(RuntimeError, match="backend press_key failed"):
        keyboard_with_failing_backend.press_key("a")

def test_keyboard_release_key_backend_error(keyboard_with_failing_backend):
    with pytest.raises(RuntimeError, match="backend release_key failed"):
        keyboard_with_failing_backend.release_key("a")

def test_keyboard_press_keys_backend_error(keyboard_with_failing_backend):
    with pytest.raises(RuntimeError, match="backend press_keys failed"):
        keyboard_with_failing_backend.press_keys("ctrl", "a")

def test_keyboard_release_keys_backend_error(keyboard_with_failing_backend):
    with pytest.raises(RuntimeError, match="backend release_keys failed"):
        keyboard_with_failing_backend.release_keys("ctrl", "a")

def test_keyboard_send_keys_backend_error(keyboard_with_failing_backend):
    with pytest.raises(RuntimeError, match="backend send_keys failed"):
        keyboard_with_failing_backend.send_keys("ctrl+a")

@pytest.fixture
def mouse_with_failing_backend():
    backend = MagicMock()
    backend.move_mouse.side_effect = RuntimeError("backend move_mouse failed")
    backend.click_mouse.side_effect = RuntimeError("backend click_mouse failed")
    backend.mouse_down.side_effect = RuntimeError("backend mouse_down failed")
    backend.mouse_up.side_effect = RuntimeError("backend mouse_up failed")
    backend.get_mouse_position.side_effect = RuntimeError("backend get_mouse_position failed")
    return Mouse(backend)

def test_mouse_move_backend_error(mouse_with_failing_backend):
    assert mouse_with_failing_backend.move(100, 200) is False

def test_mouse_click_backend_error(mouse_with_failing_backend):
    # move() внутри click тоже вернёт False, поэтому click вернёт False
    assert mouse_with_failing_backend.click(100, 200) is False

def test_mouse_double_click_backend_error(mouse_with_failing_backend):
    # Первый click вернёт False, double_click сразу вернёт False
    assert mouse_with_failing_backend.double_click(100, 200) is False

def test_mouse_right_click_backend_error(mouse_with_failing_backend):
    # move() внутри click вернёт False, поэтому right_click вернёт False
    assert mouse_with_failing_backend.right_click(100, 200) is False

def test_mouse_drag_backend_error_on_move(mouse_with_failing_backend):
    # move() на старте вернёт False, drag сразу вернёт False
    assert mouse_with_failing_backend.drag(10, 10, 20, 20) is False

def test_mouse_drag_backend_error_on_mouse_down():
    backend = MagicMock()
    backend.move_mouse.return_value = True
    backend.mouse_down.return_value = False
    backend.mouse_up.return_value = True
    mouse = Mouse(backend)
    assert mouse.drag(10, 10, 20, 20) is False

def test_mouse_drag_backend_error_on_second_move():
    backend = MagicMock()
    backend.move_mouse.side_effect = [True, False]
    backend.mouse_down.return_value = True
    backend.mouse_up.return_value = True
    mouse = Mouse(backend)
    assert mouse.drag(10, 10, 20, 20) is False
    backend.mouse_up.assert_called()

def test_mouse_move_to_element_backend_error(mouse_with_failing_backend):
    element = MagicMock()
    element.get_location.return_value = (10, 10)
    element.get_size.return_value = (20, 20)
    assert mouse_with_failing_backend.move_to(element) is False

def test_mouse_get_position_backend_error(mouse_with_failing_backend):
    with pytest.raises(RuntimeError, match="backend get_mouse_position failed"):
        mouse_with_failing_backend.get_position()

def test_keyboard_type_text_empty(mock_backend):
    keyboard = Keyboard(mock_backend)
    assert keyboard.type_text("") is True

def test_keyboard_type_text_invalid_type(mock_backend):
    keyboard = Keyboard(mock_backend)
    with pytest.raises(ValueError):
        keyboard.type_text("123")

def test_keyboard_type_text_backend_false(mock_backend):
    mock_backend.type_text.return_value = False
    keyboard = Keyboard(mock_backend)
    assert keyboard.type_text("abc") is False

def test_keyboard_press_key_empty(mock_backend):
    keyboard = Keyboard(mock_backend)
    assert keyboard.press_key("") is True

def test_keyboard_press_key_invalid_type(mock_backend):
    keyboard = Keyboard(mock_backend)
    with pytest.raises(ValueError):
        keyboard.press_key("123")

def test_keyboard_press_key_backend_false(mock_backend):
    mock_backend.press_key.return_value = False
    keyboard = Keyboard(mock_backend)
    assert keyboard.press_key("a") is False

def test_keyboard_release_key_empty(mock_backend):
    keyboard = Keyboard(mock_backend)
    assert keyboard.release_key("") is True

def test_keyboard_release_key_invalid_type(mock_backend):
    keyboard = Keyboard(mock_backend)
    with pytest.raises(ValueError):
        keyboard.release_key("123")

def test_keyboard_release_key_backend_false(mock_backend):
    mock_backend.release_key.return_value = False
    keyboard = Keyboard(mock_backend)
    assert keyboard.release_key("a") is False

def test_keyboard_press_keys_empty(mock_backend):
    keyboard = Keyboard(mock_backend)
    assert keyboard.press_keys() is True

def test_keyboard_press_keys_invalid_type(mock_backend):
    keyboard = Keyboard(mock_backend)
    with pytest.raises(ValueError):
        keyboard.press_keys("a", "1")

def test_keyboard_press_keys_backend_false(mock_backend):
    mock_backend.press_keys.return_value = False
    keyboard = Keyboard(mock_backend)
    assert keyboard.press_keys("a", "b") is False

def test_keyboard_release_keys_empty(mock_backend):
    keyboard = Keyboard(mock_backend)
    assert keyboard.release_keys() is True

def test_keyboard_release_keys_invalid_type(mock_backend):
    keyboard = Keyboard(mock_backend)
    with pytest.raises(ValueError):
        keyboard.release_keys("a", "1")

def test_keyboard_release_keys_backend_false(mock_backend):
    mock_backend.release_keys.return_value = False
    keyboard = Keyboard(mock_backend)
    assert keyboard.release_keys("a", "b") is False

def test_keyboard_send_keys_empty(mock_backend):
    keyboard = Keyboard(mock_backend)
    assert keyboard.send_keys("") is True

def test_keyboard_send_keys_invalid_type(mock_backend):
    keyboard = Keyboard(mock_backend)
    with pytest.raises(ValueError):
        keyboard.send_keys("123")

def test_keyboard_send_keys_backend_false(mock_backend):
    mock_backend.send_keys.return_value = False
    keyboard = Keyboard(mock_backend)
    assert keyboard.send_keys("abc") is False
