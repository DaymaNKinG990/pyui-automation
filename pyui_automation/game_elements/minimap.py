from typing import Optional, Any, Tuple, List, TYPE_CHECKING, Dict
from ..elements.base import UIElement

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class MinimapMarker(UIElement):
    """Represents a marker/icon on the minimap"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def marker_type(self) -> str:
        """
        Get the marker type.

        Returns:
            str: Marker type (e.g., 'quest', 'player', 'enemy')
        """
        return self._element.get_property("marker_type")

    @property
    def position(self) -> Tuple[float, float]:
        """
        Get marker position on minimap.

        Returns:
            Tuple[float, float]: (x, y) coordinates
        """
        return (
            self._element.get_property("x"),
            self._element.get_property("y")
        )

    @property
    def is_highlighted(self) -> bool:
        """
        Check if marker is highlighted.

        Returns:
            bool: True if highlighted, False otherwise
        """
        return bool(self._element.get_property("highlighted"))

    @property
    def tooltip(self) -> Optional[str]:
        """
        Get marker tooltip text.

        Returns:
            Optional[str]: Tooltip text or None if no tooltip
        """
        return self._element.get_property("tooltip")


class Minimap(UIElement):
    """Represents a game minimap element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def zoom_level(self) -> float:
        """
        Get current zoom level.

        Returns:
            float: Zoom level (usually 1.0 is default)
        """
        return self._element.get_property("zoom")

    @property
    def is_rotatable(self) -> bool:
        """
        Check if minimap can be rotated.

        Returns:
            bool: True if rotatable, False otherwise
        """
        return bool(self._element.get_property("can_rotate"))

    @property
    def rotation(self) -> float:
        """
        Get current rotation in degrees.

        Returns:
            float: Rotation angle (0-360)
        """
        return self._element.get_property("rotation")

    @property
    def player_position(self) -> Tuple[float, float]:
        """
        Get player position on minimap.

        Returns:
            Tuple[float, float]: (x, y) coordinates
        """
        return (
            self._element.get_property("player_x"),
            self._element.get_property("player_y")
        )

    def get_markers(self, marker_type: Optional[str] = None) -> List[MinimapMarker]:
        """
        Get all markers or markers of specific type.

        Args:
            marker_type (Optional[str]): Type of markers to get, or None for all

        Returns:
            List[MinimapMarker]: List of minimap markers
        """
        markers = self._element.find_elements(by="type", value="marker")
        if marker_type:
            return [MinimapMarker(m, self._session) for m in markers 
                   if m.get_property("marker_type") == marker_type]
        return [MinimapMarker(m, self._session) for m in markers]

    def zoom_in(self) -> None:
        """Zoom in the minimap"""
        zoom_in = self._element.find_element(by="name", value="ZoomIn")
        if zoom_in:
            zoom_in.click()

    def zoom_out(self) -> None:
        """Zoom out the minimap"""
        zoom_out = self._element.find_element(by="name", value="ZoomOut")
        if zoom_out:
            zoom_out.click()

    def rotate(self, angle: float) -> None:
        """
        Rotate minimap to specific angle.

        Args:
            angle (float): Target angle in degrees (0-360)

        Raises:
            ValueError: If minimap not rotatable or invalid angle
        """
        if not self.is_rotatable:
            raise ValueError("Minimap is not rotatable")

        if not 0 <= angle <= 360:
            raise ValueError("Angle must be between 0 and 360 degrees")

        self._element.set_property("rotation", angle)

    def click_position(self, x: float, y: float) -> None:
        """
        Click a specific position on minimap.

        Args:
            x (float): X coordinate
            y (float): Y coordinate
        """
        self._element.click_at(x, y)

    def ping_position(self, x: float, y: float) -> None:
        """
        Ping a position on minimap (usually alt+click).

        Args:
            x (float): X coordinate
            y (float): Y coordinate
        """
        self._element.alt_click_at(x, y)

    def wait_until_marker_appears(self, marker_type: str, timeout: float = 10) -> bool:
        """
        Wait until marker of specific type appears.

        Args:
            marker_type (str): Type of marker to wait for
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if marker appeared within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: any(m.marker_type == marker_type for m in self.get_markers()),
            timeout=timeout,
            error_message=f"Marker of type '{marker_type}' did not appear"
        )

    def wait_until_player_reaches(self, x: float, y: float, 
                                threshold: float = 1.0, timeout: float = 10) -> bool:
        """
        Wait until player reaches specific position.

        Args:
            x (float): Target X coordinate
            y (float): Target Y coordinate
            threshold (float): Distance threshold for position match
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if player reached position within timeout, False otherwise
        """
        def check_position():
            px, py = self.player_position
            dx = abs(px - x)
            dy = abs(py - y)
            return dx <= threshold and dy <= threshold

        return self._session.wait_for_condition(
            check_position,
            timeout=timeout,
            error_message=f"Player did not reach position ({x}, {y})"
        )
