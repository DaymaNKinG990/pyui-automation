import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.core.input import InputManager


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
        mock_type_text.assert_called_once_with("Hello World", 0.0)

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
        mock_type_text.assert_not_called()

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
        mock_press_key.assert_not_called()

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
        mock_release_key.assert_not_called()

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
        mock_press_keys.assert_not_called()

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
        mock_release_keys.assert_not_called()

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
        mock_send_keys.assert_not_called()

def test_send_keys_invalid_input(input_manager):
    """Test sending invalid input"""
    with pytest.raises(ValueError, match="Keys must be a string"):
        input_manager.send_keys(123)  # type: ignore
