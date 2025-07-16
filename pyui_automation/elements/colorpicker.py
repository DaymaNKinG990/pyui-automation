from typing import Any, Tuple, Union, TYPE_CHECKING
from .base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class ColorPicker(UIElement):
    """Represents a color picker control element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def color(self) -> str:
        """
        Get the current color in hex format.

        Returns:
            str: Color in hex format (e.g., '#FF0000')
        """
        return self._element.get_property("color")

    @color.deleter
    def color(self):
        self._color = "#000000"

    @property
    def rgb(self) -> Tuple[int, int, int]:
        """
        Get the current color in RGB format.

        Returns:
            Tuple[int, int, int]: RGB values (0-255)
        """
        return self._element.get_property("rgb")

    @rgb.deleter
    def rgb(self):
        self._rgb = (0, 0, 0)

    @property
    def alpha(self) -> float:
        """
        Get the current alpha value.

        Returns:
            float: Alpha value (0-1)
        """
        return self._element.get_property("alpha")

    @property
    def is_expanded(self) -> bool:
        """
        Check if the color picker popup is expanded.

        Returns:
            bool: True if expanded, False otherwise
        """
        return self._element.get_property("expanded")

    @is_expanded.deleter
    def is_expanded(self):
        self._is_expanded = False

    def set_color(self, color: Union[str, Tuple[int, int, int]]) -> None:
        """
        Set the color value.

        Args:
            color (Union[str, Tuple[int, int, int]]): Color in hex format or RGB tuple
        """
        if isinstance(color, str):
            self._element.set_property("color", color)
        else:
            self._element.set_property("rgb", color)

    def set_alpha(self, alpha: float) -> None:
        """
        Set the alpha value.

        Args:
            alpha (float): Alpha value between 0 and 1

        Raises:
            ValueError: If alpha not between 0 and 1
        """
        if not 0 <= alpha <= 1:
            raise ValueError("Alpha must be between 0 and 1")
        self._element.set_property("alpha", alpha)

    def expand(self) -> None:
        """Expand the color picker popup if not already expanded"""
        if not self.is_expanded:
            self.click()

    def collapse(self) -> None:
        """Collapse the color picker popup if expanded"""
        if self.is_expanded:
            self.click()

    def select_preset(self, preset_name: str) -> None:
        """
        Select a preset color by its name.

        Args:
            preset_name (str): Name of the preset color

        Raises:
            ValueError: If preset not found
        """
        if not self.is_expanded:
            self.expand()

        preset = self._element.find_element(
            by="name",
            value=preset_name
        )
        if preset:
            preset.click()
        else:
            raise ValueError(f"Preset color '{preset_name}' not found")

    def wait_until_color(self, color: Union[str, Tuple[int, int, int]], timeout: float = 10) -> bool:
        """
        Wait until a specific color is selected.

        Args:
            color (Union[str, Tuple[int, int, int]]): Expected color
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if color matched within timeout, False otherwise
        """
        if isinstance(color, str):
            return self._session.wait_for_condition(
                lambda: self.color == color,
                timeout=timeout,
                error_message=f"Color did not become {color}"
            )
        else:
            return self._session.wait_for_condition(
                lambda: self.rgb == color,
                timeout=timeout,
                error_message=f"Color did not become {color}"
            )

    def wait_until_expanded(self, timeout: float = 10) -> bool:
        """
        Wait until the color picker popup becomes expanded.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if popup became expanded within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_expanded,
            timeout=timeout,
            error_message="Color picker did not expand"
        )

    def wait_until_collapsed(self, timeout: float = 10) -> bool:
        """
        Wait until the color picker popup becomes collapsed.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if popup became collapsed within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: not self.is_expanded,
            timeout=timeout,
            error_message="Color picker did not collapse"
        )
