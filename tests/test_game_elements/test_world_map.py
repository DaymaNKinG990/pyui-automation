import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.game_elements import WorldMap, MapMarker, MapArea


@pytest.fixture
def mock_element():
    element = MagicMock()
    element.properties = {}
    element.clicks = 0
    
    def mock_click():
        element.clicks += 1
    
    element.click = mock_click
    element.get_property = lambda key: element.properties.get(key)
    element.set_property = lambda key, value: element.properties.update({key: value})
    return element


@pytest.fixture
def mock_session():
    return MagicMock()


@pytest.fixture
def world_map(mock_element, mock_session):
    return WorldMap(mock_element, mock_session)


def test_open_close(world_map, mock_element):
    """Test opening and closing the map"""
    world_map.open()
    assert mock_element.clicks == 1
    
    world_map.close()
    assert mock_element.clicks == 2


def test_pan_to_coordinates(world_map, mock_element):
    """Test panning to specific coordinates"""
    world_map.pan_to_coordinates(100, 200)
    assert mock_element.properties['pan_x'] == 100
    assert mock_element.properties['pan_y'] == 200


def test_get_current_position(world_map, mock_element):
    """Test getting current position"""
    mock_element.properties.update({'player_x': 100, 'player_y': 200})
    x, y = world_map.get_current_position()
    assert x == 100
    assert y == 200


def test_set_zoom(world_map, mock_element):
    """Test setting zoom level"""
    world_map.set_zoom(2.0)
    assert mock_element.properties['zoom'] == 2.0


def test_add_marker(world_map):
    """Test adding a map marker"""
    marker = world_map.add_marker(100, 200, 'Quest')
    assert isinstance(marker, MapMarker)
    assert marker.x == 100
    assert marker.y == 200
    assert marker.type == 'Quest'


def test_remove_marker(world_map):
    """Test removing a map marker"""
    marker = MapMarker(100, 200, 'Quest')
    world_map.add_marker(100, 200, 'Quest')
    assert world_map.remove_marker(marker)


def test_get_markers(world_map, mock_element):
    """Test getting all markers"""
    marker1 = MagicMock()
    marker1.get_property.side_effect = lambda key: {'type': 'Quest', 'x': 100, 'y': 200}.get(key)
    
    marker2 = MagicMock()
    marker2.get_property.side_effect = lambda key: {'type': 'Vendor', 'x': 300, 'y': 400}.get(key)
    
    mock_element.find_elements.return_value = [marker1, marker2]
    
    markers = world_map.get_markers()
    assert len(markers) == 2
    assert markers[0].type == 'Quest'
    assert markers[1].type == 'Vendor'


def test_get_areas(world_map, mock_element):
    """Test getting map areas"""
    area1 = MagicMock()
    area1.get_property.side_effect = lambda key: {'name': 'Forest', 'level': '1-10'}.get(key)
    
    area2 = MagicMock()
    area2.get_property.side_effect = lambda key: {'name': 'Desert', 'level': '20-30'}.get(key)
    
    mock_element.find_elements.return_value = [area1, area2]
    
    areas = world_map.get_areas()
    assert len(areas) == 2
    assert areas[0].name == 'Forest'
    assert areas[1].name == 'Desert'
