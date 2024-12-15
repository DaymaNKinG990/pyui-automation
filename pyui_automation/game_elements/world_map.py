from typing import Optional, Any, Dict, List, Tuple
from ..elements.base import UIElement


class MapMarker(UIElement):
    """Represents a marker on the map"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get marker name"""
        return self._element.get_property("name")

    @property
    def type(self) -> str:
        """Get marker type (quest/vendor/etc)"""
        return self._element.get_property("type")

    @property
    def position(self) -> Tuple[float, float]:
        """Get marker position (x, y)"""
        return (
            self._element.get_property("position_x"),
            self._element.get_property("position_y")
        )

    @property
    def is_tracked(self) -> bool:
        """Check if marker is being tracked"""
        return self._element.get_property("tracked")

    def click(self) -> bool:
        """
        Click the marker

        Returns:
            bool: True if successful
        """
        self._element.click()
        return True

    def track(self) -> bool:
        """
        Toggle tracking for this marker

        Returns:
            bool: True if successful
        """
        track_button = self._element.find_element(by="type", value="track_button")
        if track_button:
            track_button.click()
            return True
        return False

    def set_note(self, note: str) -> bool:
        """
        Set marker note

        Args:
            note (str): Note text

        Returns:
            bool: True if successful
        """
        note_button = self._element.find_element(by="type", value="note_button")
        if note_button:
            note_button.click()
            note_input = self._element.find_element(by="type", value="note_input")
            if note_input:
                note_input.send_keys(note)
                note_input.send_keys("\n")
                return True
        return False


class MapArea(UIElement):
    """Represents a map area/zone"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def name(self) -> str:
        """Get area name"""
        return self._element.get_property("name")

    @property
    def level_range(self) -> Tuple[int, int]:
        """Get area level range"""
        return (
            self._element.get_property("min_level"),
            self._element.get_property("max_level")
        )

    @property
    def is_discovered(self) -> bool:
        """Check if area has been discovered"""
        return self._element.get_property("discovered")

    @property
    def is_contested(self) -> bool:
        """Check if area is contested territory"""
        return self._element.get_property("contested")

    @property
    def faction(self) -> Optional[str]:
        """Get controlling faction if any"""
        return self._element.get_property("faction")

    def get_markers(self, marker_type: Optional[str] = None) -> List[MapMarker]:
        """
        Get markers in this area

        Args:
            marker_type (Optional[str]): Filter by marker type

        Returns:
            List[MapMarker]: List of markers
        """
        markers = self._element.find_elements(
            by="type",
            value="map_marker",
            marker_type=marker_type
        )
        return [MapMarker(m, self._session) for m in markers]


class WorldMap(UIElement):
    """Represents the world map interface"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def current_area(self) -> Optional[MapArea]:
        """Get currently viewed area"""
        area = self._element.find_element(
            by="type",
            value="current_area"
        )
        return MapArea(area, self._session) if area else None

    @property
    def player_position(self) -> Tuple[float, float]:
        """Get player position on map"""
        return (
            self._element.get_property("player_x"),
            self._element.get_property("player_y")
        )

    @property
    def zoom_level(self) -> float:
        """Get current zoom level"""
        return self._element.get_property("zoom")

    def get_areas(self) -> List[MapArea]:
        """
        Get all map areas

        Returns:
            List[MapArea]: List of areas
        """
        areas = self._element.find_elements(by="type", value="map_area")
        return [MapArea(a, self._session) for a in areas]

    def get_area(self, name: str) -> Optional[MapArea]:
        """
        Find area by name

        Args:
            name (str): Area name

        Returns:
            Optional[MapArea]: Found area or None
        """
        area = self._element.find_element(
            by="type",
            value="map_area",
            name=name
        )
        return MapArea(area, self._session) if area else None

    def get_markers(self, 
                   marker_type: Optional[str] = None,
                   area: Optional[str] = None) -> List[MapMarker]:
        """
        Get map markers

        Args:
            marker_type (Optional[str]): Filter by marker type
            area (Optional[str]): Filter by area name

        Returns:
            List[MapMarker]: List of markers
        """
        markers = self._element.find_elements(
            by="type",
            value="map_marker",
            marker_type=marker_type,
            area=area
        )
        return [MapMarker(m, self._session) for m in markers]

    def get_marker(self, name: str) -> Optional[MapMarker]:
        """
        Find marker by name

        Args:
            name (str): Marker name

        Returns:
            Optional[MapMarker]: Found marker or None
        """
        marker = self._element.find_element(
            by="type",
            value="map_marker",
            name=name
        )
        return MapMarker(marker, self._session) if marker else None

    def set_zoom(self, level: float) -> bool:
        """
        Set map zoom level

        Args:
            level (float): New zoom level

        Returns:
            bool: True if successful
        """
        zoom_slider = self._element.find_element(by="type", value="zoom_slider")
        if zoom_slider:
            zoom_slider.set_value(level)
            return True
        return False

    def pan_to(self, x: float, y: float) -> bool:
        """
        Pan map to coordinates

        Args:
            x (float): X coordinate
            y (float): Y coordinate

        Returns:
            bool: True if successful
        """
        self._element.pan_to(x, y)
        return True

    def create_marker(self, 
                     x: float,
                     y: float,
                     name: str,
                     marker_type: str = "custom") -> Optional[MapMarker]:
        """
        Create new map marker

        Args:
            x (float): X coordinate
            y (float): Y coordinate
            name (str): Marker name
            marker_type (str): Marker type

        Returns:
            Optional[MapMarker]: Created marker or None
        """
        create_button = self._element.find_element(by="type", value="create_marker")
        if create_button:
            create_button.click()
            self.pan_to(x, y)
            self._element.click()
            
            name_input = self._element.find_element(by="type", value="marker_name")
            if name_input:
                name_input.send_keys(name)
                
                type_dropdown = self._element.find_element(by="type", value="marker_type")
                if type_dropdown:
                    type_dropdown.select_option(marker_type)
                    
                    confirm_button = self._element.find_element(by="type", value="confirm_marker")
                    if confirm_button:
                        confirm_button.click()
                        return self.get_marker(name)
        return None

    def clear_markers(self, marker_type: Optional[str] = None) -> bool:
        """
        Clear map markers

        Args:
            marker_type (Optional[str]): Only clear specific type

        Returns:
            bool: True if successful
        """
        clear_button = self._element.find_element(by="type", value="clear_markers")
        if clear_button:
            clear_button.click()
            if marker_type:
                type_dropdown = self._element.find_element(by="type", value="marker_type")
                if type_dropdown:
                    type_dropdown.select_option(marker_type)
            confirm_button = self._element.find_element(by="type", value="confirm_clear")
            if confirm_button:
                confirm_button.click()
                return True
        return False

    def toggle_filter(self, filter_type: str, enabled: bool = True) -> bool:
        """
        Toggle map filter

        Args:
            filter_type (str): Filter to toggle
            enabled (bool): Enable or disable

        Returns:
            bool: True if successful
        """
        filter_checkbox = self._element.find_element(
            by="type",
            value="map_filter",
            filter=filter_type
        )
        if filter_checkbox:
            if filter_checkbox.is_checked() != enabled:
                filter_checkbox.click()
            return True
        return False

    def wait_for_area_load(self, area_name: str, timeout: float = 10) -> bool:
        """
        Wait for area to load

        Args:
            area_name (str): Area name
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if area loaded within timeout
        """
        return self._session.wait_for_condition(
            lambda: self.current_area and self.current_area.name == area_name,
            timeout=timeout,
            error_message=f"Area '{area_name}' did not load"
        )

    def wait_for_player_move(self, 
                           target_x: float,
                           target_y: float,
                           threshold: float = 0.1,
                           timeout: float = 10) -> bool:
        """
        Wait for player to reach position

        Args:
            target_x (float): Target X coordinate
            target_y (float): Target Y coordinate
            threshold (float): Distance threshold
            timeout (float): Maximum wait time in seconds

        Returns:
            bool: True if position reached within timeout
        """
        def check_position():
            x, y = self.player_position
            dx = abs(x - target_x)
            dy = abs(y - target_y)
            return dx <= threshold and dy <= threshold

        return self._session.wait_for_condition(
            check_position,
            timeout=timeout,
            error_message=f"Player did not reach position ({target_x}, {target_y})"
        )
