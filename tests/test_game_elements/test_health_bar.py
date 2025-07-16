import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.health_bar import HealthBar

@pytest.fixture
def mock_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'value': 50.0,
        'max_value': 100.0,
        'color_r': 255,
        'color_g': 0,
        'color_b': 0,
    }.get(key)
    return el

@pytest.fixture
def mock_element_critical():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'value': 10.0,
        'max_value': 100.0,
        'color_r': 255,
        'color_g': 255,
        'color_b': 0,
    }.get(key)
    return el

@pytest.fixture
def mock_element_zero():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'value': 0.0,
        'max_value': 0.0,
        'color_r': 0,
        'color_g': 0,
        'color_b': 0,
    }.get(key)
    return el

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def health_bar(mock_element, mock_session):
    return HealthBar(mock_element, mock_session)

@pytest.fixture
def health_bar_critical(mock_element_critical, mock_session):
    return HealthBar(mock_element_critical, mock_session)

@pytest.fixture
def health_bar_zero(mock_element_zero, mock_session):
    return HealthBar(mock_element_zero, mock_session)

def test_health_bar_properties(health_bar):
    assert health_bar.current_health == 50.0
    assert health_bar.max_health == 100.0
    assert health_bar.health_percentage == 50.0
    assert health_bar.color == (255, 0, 0)
    assert health_bar.is_critical is False

def test_health_bar_critical(health_bar_critical):
    assert health_bar_critical.health_percentage == 10.0
    assert health_bar_critical.is_critical is True

def test_health_bar_zero(health_bar_zero):
    assert health_bar_zero.max_health == 0.0
    assert health_bar_zero.health_percentage == 0.0
    assert health_bar_zero.is_critical is True
