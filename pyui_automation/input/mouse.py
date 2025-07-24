"""Mouse input handling"""

import time
from typing import Tuple, Optional, Any
from ..core.interfaces.iinput_backend import IInputBackend


class Mouse:
    """
    Cross-platform mouse input handler.

    Позволяет программно управлять мышью: перемещать, кликать, двойной клик, правый клик и т.д.
    Используется сервисным слоем InputService.

    Example usage:
        mouse = Mouse()
        mouse.move(100, 200)
        mouse.click()
        mouse.double_click()
        mouse.right_click()
    """

    def __init__(self, backend: IInputBackend):
        """
        Initialize mouse input handler.

        Args:
            backend: Platform-specific backend to use
        """
        if backend is None:
            raise ValueError("Backend cannot be None")
        self._backend = backend

    def move(self, x: int, y: int) -> bool:
        """
        Move mouse cursor to absolute coordinates.

        Args:
            x: X coordinate
            y: Y coordinate

        Returns:
            bool: True if the move was successful, False otherwise

        Raises:
            ValueError: If coordinates are not numbers
        """
        if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
            raise ValueError("Coordinates must be numbers")
        try:
            return self._backend.move_mouse(int(x), int(y))
        except Exception:
            return False

    def click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left") -> bool:
        """
        Click at current position or specified coordinates.

        Args:
            x: Optional X coordinate
            y: Optional Y coordinate
            button: The button to click. Defaults to "left". Can be "left", "right", or "middle".

        Returns:
            bool: True if the click was successful, False otherwise

        Raises:
            ValueError: If coordinates are not numbers or button is invalid
        """
        if x is not None and y is not None:
            if not isinstance(x, (int, float)) or not isinstance(y, (int, float)):
                raise ValueError("Coordinates must be numbers")
            if not self.move(x, y):
                return False
        if not isinstance(button, str):
            raise ValueError("Button must be a string")
        if button not in ["left", "right", "middle"]:
            raise ValueError("Invalid button type. Must be 'left', 'right', or 'middle'")
        return self._backend.click_mouse(button)

    def double_click(self, x: Optional[int] = None, y: Optional[int] = None, button: str = "left") -> bool:
        """
        Double click at current position or specified coordinates.

        Args:
            x: Optional X coordinate
            y: Optional Y coordinate
            button: The button to double click. Defaults to "left". Can be "left", "right", or "middle".

        Returns:
            bool: True if the double click was successful, False otherwise

        Raises:
            ValueError: If coordinates are not numbers or button is invalid
        """
        success = self.click(x, y, button)
        if not success:
            return False
        time.sleep(0.1)  # Small delay between clicks
        return self.click(None, None, button)  # Already at position from first click

    def right_click(self, x: Optional[int] = None, y: Optional[int] = None) -> bool:
        """
        Right click at current position or specified coordinates.

        Args:
            x: Optional X coordinate
            y: Optional Y coordinate

        Returns:
            bool: True if the right click was successful, False otherwise
        """
        return self.click(x, y, button="right")

    def drag(self, start_x: int, start_y: int, end_x: int, end_y: int, button: str = "left") -> bool:
        """
        Drag from start coordinates to end coordinates.

        Args:
            start_x: Starting X coordinate
            start_y: Starting Y coordinate
            end_x: Ending X coordinate
            end_y: Ending Y coordinate
            button: The button to use for dragging. Defaults to "left". Can be "left", "right", or "middle".

        Returns:
            bool: True if the drag was successful, False otherwise

        Raises:
            ValueError: If coordinates are not numbers or button is invalid
        """
        if not all(isinstance(coord, (int, float)) for coord in [start_x, start_y, end_x, end_y]):
            raise ValueError("Coordinates must be numbers")
        if not isinstance(button, str):
            raise ValueError("Button must be a string")
        if button not in ["left", "right", "middle"]:
            raise ValueError("Invalid button type. Must be 'left', 'right', or 'middle'")

        # Move to start position
        if not self.move(start_x, start_y):
            return False
        time.sleep(0.1)

        # Press button
        if not self._backend.mouse_down(button):
            return False
        time.sleep(0.1)

        # Move to end position
        if not self.move(end_x, end_y):
            self._backend.mouse_up(button)  # Release button if move fails
            return False
        time.sleep(0.1)

        # Release button
        self._backend.mouse_up(button)
        return True

    def move_to(self, element: Any) -> bool:
        """
        Move mouse cursor to the center of an element.

        Args:
            element: UI element to move to

        Returns:
            bool: True if the move was successful, False otherwise
        """
        try:
            location = element.get_location()
            size = element.get_size()
            if location and size:
                x = location[0] + size[0] // 2
                y = location[1] + size[1] // 2
                return self.move(x, y)
            return False
        except Exception:
            return False

    def get_position(self) -> Tuple[int, int]:
        """
        Get current mouse cursor position.

        Returns:
            Tuple of (x, y) coordinates
        """
        return self._backend.get_mouse_position()
