import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.world_map import WorldMap, MapMarkerData

@pytest.fixture
def mock_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: 10.0 if key in ['player_x', 'player_y'] else None
    el.find_element.side_effect = lambda *a, **kw: None
    el.find_elements.side_effect = lambda *a, **kw: []
    el.click = MagicMock()
    el.set_property = MagicMock()
    el.pan_to = MagicMock()
    return el

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def world_map(mock_element, mock_session):
    return WorldMap(mock_element, mock_session)

def test_open_close(world_map, mock_element):
    assert world_map.open() is True
    assert world_map.close() is True
    assert mock_element.click.call_count == 2

def test_pan_to_coordinates(world_map, mock_element):
    assert world_map.pan_to_coordinates(5.0, 7.0) is True
    mock_element.set_property.assert_any_call('pan_x', 5.0)
    mock_element.set_property.assert_any_call('pan_y', 7.0)

def test_get_current_position(world_map):
    assert world_map.get_current_position() == (10.0, 10.0)

def test_set_zoom(world_map, mock_element):
    assert world_map.set_zoom(2.5) is True
    mock_element.set_property.assert_called_with('zoom', 2.5)

def test_add_remove_marker(world_map):
    marker = world_map.add_marker(1.0, 2.0, 'quest')
    assert marker in world_map._markers
    assert world_map.remove_marker(marker) is True
    assert world_map.remove_marker(marker) is False

def test_get_areas_empty(world_map, mock_element):
    mock_element.find_elements.side_effect = lambda *a, **kw: []
    assert world_map.get_areas() == []

def test_get_area_none(world_map, mock_element):
    mock_element.find_element.side_effect = lambda *a, **kw: None
    assert world_map.get_area('Stormwind') is None

def test_get_markers_empty(world_map, mock_element):
    mock_element.find_elements.side_effect = lambda *a, **kw: []
    assert world_map.get_markers() == []

def test_get_marker_none(world_map, mock_element):
    mock_element.find_element.side_effect = lambda *a, **kw: None
    assert world_map.get_marker('QuestMarker') is None

def test_pan_to(world_map, mock_element):
    assert world_map.pan_to(3.0, 4.0) is True
    mock_element.pan_to.assert_called_with(3.0, 4.0)

def test_create_marker_no_button(world_map, mock_element):
    mock_element.find_element.side_effect = lambda *a, **kw: None
    assert world_map.create_marker(1.0, 2.0, 'TestMarker') is None

def test_create_marker_success(world_map, mock_element):
    create_btn = MagicMock()
    create_btn.click = MagicMock()
    name_input = MagicMock()
    name_input.send_keys = MagicMock()
    type_dropdown = MagicMock()
    type_dropdown.select_option = MagicMock()
    confirm_btn = MagicMock()
    confirm_btn.click = MagicMock()
    marker_obj = MagicMock()
    marker_obj.get_property.side_effect = lambda key: 1.0 if key == 'x' else 2.0 if key == 'y' else 'custom' if key == 'type' else 'TestMarker' if key == 'name' else None
    def find_element_side_effect(*a, **kw):
        if kw.get('value') == 'create_marker':
            return create_btn
        if kw.get('value') == 'marker_name':
            return name_input
        if kw.get('value') == 'marker_type':
            return type_dropdown
        if kw.get('value') == 'confirm_marker':
            return confirm_btn
        if kw.get('value') == 'map_marker' and kw.get('name') == 'TestMarker':
            return marker_obj
        return None
    mock_element.find_element.side_effect = find_element_side_effect
    world_map.pan_to = MagicMock()
    marker = world_map.create_marker(1.0, 2.0, 'TestMarker')
    assert isinstance(marker, MapMarkerData)
    assert marker.x == 1.0 and marker.y == 2.0 and marker.marker_type == 'custom'

def test_clear_markers_no_button(world_map, mock_element):
    mock_element.find_element.side_effect = lambda *a, **kw: None
    assert world_map.clear_markers() is False
