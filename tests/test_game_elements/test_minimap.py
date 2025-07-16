import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.minimap import Minimap, MinimapMarker

@pytest.fixture
def mock_marker_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'marker_type': 'quest',
        'x': 10.0,
        'y': 20.0,
        'highlighted': True,
        'tooltip': 'Quest marker',
    }.get(key)
    return el

@pytest.fixture
def mock_marker_element_no_tooltip():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'marker_type': 'enemy',
        'x': 5.0,
        'y': 7.0,
        'highlighted': False,
        'tooltip': None,
    }.get(key)
    return el

@pytest.fixture
def mock_minimap_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'zoom': 1.5,
        'can_rotate': True,
        'rotation': 45.0,
        'player_x': 100.0,
        'player_y': 200.0,
    }.get(key)
    el.find_elements.side_effect = lambda by=None, value=None: []
    return el

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def marker(mock_marker_element, mock_session):
    return MinimapMarker(mock_marker_element, mock_session)

@pytest.fixture
def marker_no_tooltip(mock_marker_element_no_tooltip, mock_session):
    return MinimapMarker(mock_marker_element_no_tooltip, mock_session)

@pytest.fixture
def minimap(mock_minimap_element, mock_session):
    return Minimap(mock_minimap_element, mock_session)

def test_marker_properties(marker, marker_no_tooltip):
    assert marker.marker_type == 'quest'
    assert marker.position == (10.0, 20.0)
    assert marker.is_highlighted is True
    assert marker.tooltip == 'Quest marker'
    assert marker_no_tooltip.tooltip is None
    assert marker_no_tooltip.is_highlighted is False

def test_minimap_properties(minimap):
    assert minimap.zoom_level == 1.5
    assert minimap.is_rotatable is True
    assert minimap.rotation == 45.0
    assert minimap.player_position == (100.0, 200.0)

def test_minimap_get_markers_all_types(minimap, mock_minimap_element, mock_session):
    marker1 = MagicMock()
    marker1.get_property.side_effect = lambda key: 'quest' if key == 'marker_type' else None
    marker2 = MagicMock()
    marker2.get_property.side_effect = lambda key: 'enemy' if key == 'marker_type' else None
    mock_minimap_element.find_elements.side_effect = lambda by=None, value=None: [marker1, marker2] if value == 'marker' else []
    m = Minimap(mock_minimap_element, mock_session)
    markers = m.get_markers()
    assert len(markers) == 2
    assert all(isinstance(x, MinimapMarker) for x in markers)

def test_minimap_get_markers_filtered(minimap, mock_minimap_element, mock_session):
    marker1 = MagicMock()
    marker1.get_property.side_effect = lambda key: 'quest' if key == 'marker_type' else None
    marker2 = MagicMock()
    marker2.get_property.side_effect = lambda key: 'enemy' if key == 'marker_type' else None
    mock_minimap_element.find_elements.side_effect = lambda by=None, value=None: [marker1, marker2] if value == 'marker' else []
    m = Minimap(mock_minimap_element, mock_session)
    quest_markers = m.get_markers('quest')
    assert len(quest_markers) == 1
    assert quest_markers[0].marker_type == 'quest'
    enemy_markers = m.get_markers('enemy')
    assert len(enemy_markers) == 1
    assert enemy_markers[0].marker_type == 'enemy' 