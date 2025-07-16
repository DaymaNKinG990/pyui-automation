import time
import pyautogui
from typing import Tuple, Union, Optional

class GameInput:
    """
    Cross-platform class for handling game-specific input simulation.

    Позволяет эмулировать игровые действия: нажатия, движения мыши, сложные макросы для автоматизации игр.
    Используется сервисным слоем InputService.

    Example usage:
        game_input = GameInput()
        game_input.move_mouse(100, 100)
        game_input.click(100, 100)
        game_input.send_key('space')
    """
    
    def __init__(self):
        pyautogui.FAILSAFE = True  # Move mouse to corner to abort
        pyautogui.PAUSE = 0.1  # Add small delay between actions
        
    @staticmethod
    def send_key(key: Union[str, int], duration: float = 0.1):
        """
        Simulate keyboard key press in games.
        
        Args:
            key: Key to press (can be character, key name, or key code)
            duration: How long to hold the key (seconds)
        """
        try:
            pyautogui.keyDown(key)
            time.sleep(duration)
            pyautogui.keyUp(key)
        except Exception as e:
            print(f"Failed to send key: {e}")
            
    @staticmethod
    def move_mouse(x: int, y: int, duration: float = 0):
        """
        Move mouse to absolute coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            duration: Time to take for movement (0 for instant)
        """
        try:
            pyautogui.moveTo(x, y, duration=duration)
        except Exception as e:
            print(f"Failed to move mouse: {e}")
            
    @staticmethod
    def click(x: int, y: int, button: str = 'left', clicks: int = 1):
        """
        Perform mouse click at specified coordinates.
        
        Args:
            x: X coordinate
            y: Y coordinate
            button: 'left' or 'right'
            clicks: Number of clicks
        """
        try:
            pyautogui.click(x=x, y=y, button=button, clicks=clicks)
        except Exception as e:
            print(f"Failed to click: {e}")
            
    @staticmethod
    def drag(start: Tuple[int, int], end: Tuple[int, int], duration: float = 0.5, button: str = 'left'):
        """
        Perform drag operation from start to end coordinates.
        
        Args:
            start: (x, y) start coordinates
            end: (x, y) end coordinates
            duration: How long the drag should take
            button: Which mouse button to use
        """
        try:
            pyautogui.moveTo(*start)
            pyautogui.dragTo(*end, duration=duration, button=button)
        except Exception as e:
            print(f"Failed to drag: {e}")
            
    @staticmethod
    def get_position() -> Optional[Tuple[int, int]]:
        """Get current mouse position."""
        try:
            return pyautogui.position()
        except Exception as e:
            print(f"Failed to get position: {e}")
            return None
            
    @staticmethod
    def scroll(clicks: int):
        """
        Scroll the mouse wheel.
        
        Args:
            clicks: Number of scroll clicks (positive for up, negative for down)
        """
        try:
            pyautogui.scroll(clicks)
        except Exception as e:
            print(f"Failed to scroll: {e}")
