import pytest
from unittest.mock import patch
import pyautogui
from pyui_automation.input.game_input import GameInput

@pytest.fixture
def game_input():
    return GameInput()

@pytest.fixture
def mock_pyautogui():
    with patch('pyui_automation.input.game_input.pyautogui.keyDown') as mock_key_down, \
         patch('pyui_automation.input.game_input.pyautogui.keyUp') as mock_key_up, \
         patch('pyui_automation.input.game_input.pyautogui.moveTo') as mock_move, \
         patch('pyui_automation.input.game_input.pyautogui.click') as mock_click, \
         patch('pyui_automation.input.game_input.pyautogui.dragTo') as mock_drag, \
         patch('pyui_automation.input.game_input.pyautogui.position') as mock_pos, \
         patch('pyui_automation.input.game_input.pyautogui.scroll') as mock_scroll:
        yield {
            'key_down': mock_key_down,
            'key_up': mock_key_up,
            'move': mock_move,
            'click': mock_click,
            'drag': mock_drag,
            'position': mock_pos,
            'scroll': mock_scroll
        }

def test_init(game_input):
    """Test GameInput initialization."""
    assert pyautogui.FAILSAFE is True
    assert pyautogui.PAUSE == 0.1

def test_send_key(game_input, mock_pyautogui):
    """Test key press simulation."""
    game_input.send_key('a', duration=0.1)
    
    mock_pyautogui['key_down'].assert_called_once_with('a')
    mock_pyautogui['key_up'].assert_called_once_with('a')

def test_send_key_failure(game_input, mock_pyautogui):
    """Test key press failure handling."""
    mock_pyautogui['key_down'].side_effect = Exception("Key press failed")
    
    with patch('builtins.print') as mock_print:
        game_input.send_key('a')
        mock_print.assert_called_once_with("Failed to send key: Key press failed")

def test_move_mouse(game_input, mock_pyautogui):
    """Test mouse movement."""
    game_input.move_mouse(100, 200, duration=0.5)
    
    mock_pyautogui['move'].assert_called_once_with(100, 200, duration=0.5)

def test_move_mouse_failure(game_input, mock_pyautogui):
    """Test mouse movement failure handling."""
    mock_pyautogui['move'].side_effect = Exception("Move failed")
    
    with patch('builtins.print') as mock_print:
        game_input.move_mouse(100, 200)
        mock_print.assert_called_once_with("Failed to move mouse: Move failed")

def test_click(game_input, mock_pyautogui):
    """Test mouse click."""
    game_input.click(100, 200, button='left', clicks=2)
    
    mock_pyautogui['click'].assert_called_once_with(
        x=100, y=200, button='left', clicks=2
    )

def test_click_failure(game_input, mock_pyautogui):
    """Test click failure handling."""
    mock_pyautogui['click'].side_effect = Exception("Click failed")
    
    with patch('builtins.print') as mock_print:
        game_input.click(100, 200)
        mock_print.assert_called_once_with("Failed to click: Click failed")

def test_drag(game_input, mock_pyautogui):
    """Test drag operation."""
    start = (100, 100)
    end = (200, 200)
    game_input.drag(start, end, duration=0.5, button='left')
    
    mock_pyautogui['move'].assert_called_once_with(100, 100)
    mock_pyautogui['drag'].assert_called_once_with(
        200, 200, duration=0.5, button='left'
    )

def test_drag_failure(game_input, mock_pyautogui):
    """Test drag failure handling."""
    mock_pyautogui['drag'].side_effect = Exception("Drag failed")
    
    with patch('builtins.print') as mock_print:
        game_input.drag((100, 100), (200, 200))
        mock_print.assert_called_once_with("Failed to drag: Drag failed")

def test_get_position(game_input, mock_pyautogui):
    """Test getting mouse position."""
    mock_pyautogui['position'].return_value = (100, 200)
    
    pos = game_input.get_position()
    assert pos == (100, 200)
    mock_pyautogui['position'].assert_called_once()

def test_get_position_failure(game_input, mock_pyautogui):
    """Test position getting failure handling."""
    mock_pyautogui['position'].side_effect = Exception("Position failed")
    
    with patch('builtins.print') as mock_print:
        pos = game_input.get_position()
        assert pos is None
        mock_print.assert_called_once_with("Failed to get position: Position failed")

def test_scroll(game_input, mock_pyautogui):
    """Test mouse wheel scrolling."""
    game_input.scroll(10)  # Scroll up
    mock_pyautogui['scroll'].assert_called_once_with(10)
    
    mock_pyautogui['scroll'].reset_mock()
    game_input.scroll(-5)  # Scroll down
    mock_pyautogui['scroll'].assert_called_once_with(-5)

def test_scroll_failure(game_input, mock_pyautogui):
    """Test scroll failure handling."""
    mock_pyautogui['scroll'].side_effect = Exception("Scroll failed")
    
    with patch('builtins.print') as mock_print:
        game_input.scroll(10)
        mock_print.assert_called_once_with("Failed to scroll: Scroll failed")
