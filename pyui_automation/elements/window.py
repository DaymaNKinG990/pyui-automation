from typing import List
from .base import UIElement


class Window(UIElement):
    """Window element class"""
    
    @property
    def title(self) -> str:
        """Get window title"""
        return self.get_property('title')

    def maximize(self) -> None:
        """Maximize window"""
        self._element.maximize()

    def minimize(self) -> None:
        """Minimize window"""
        self._element.minimize()

    def restore(self) -> None:
        """Restore window"""
        self._element.restore()

    def close(self) -> None:
        """Close window"""
        self._element.close()

    def move_to(self, x: int, y: int) -> None:
        """
        Move window to position

        Args:
            x (int): The x-coordinate to move to
            y (int): The y-coordinate to move to
        """
        self._element.move_to(x, y)

    def resize(self, width: int, height: int) -> None:
        """
        Resize window

        Args:
            width (int): The new width of the window
            height (int): The new height of the window
        """
        self._element.resize(width, height)

    def get_child_windows(self) -> List['Window']:
        """
        Retrieve the child windows of the current window.

        Returns:
            List[Window]: A list of Window objects representing the child windows.
        """
        children = self._element.get_child_windows()
        return [Window(child, self._session) for child in children]

    def get_process_id(self) -> int:
        """
        Get the process ID of the window.

        Returns:
            int: The process ID of the window.
        """
        return self._element.get_process_id()

    def bring_to_front(self) -> None:
        """
        Bring window to front

        This method brings the window to front and gives it focus.
        """
        self._element.bring_to_front()
