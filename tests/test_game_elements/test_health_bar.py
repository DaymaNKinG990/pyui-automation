import pytest
from pyui_automation.game_elements import HealthBar
from ..conftest import create_mock_element


@pytest.fixture
def health_bar(mock_element, mock_session):
    return HealthBar(mock_element, mock_session)


def test_get_health_percentage(health_bar, mock_element):
    """Test getting current health percentage"""
    mock_element.properties['value'] = 75
    mock_element.properties['max_value'] = 100
    assert health_bar.health_percentage == 75


def test_is_full_health(health_bar, mock_element):
    """Test checking if health is full"""
    mock_element.properties['value'] = 100
    mock_element.properties['max_value'] = 100
    assert health_bar.health_percentage == 100
    
    mock_element.properties['value'] = 90
    assert health_bar.health_percentage == 90


def test_is_low_health(health_bar, mock_element):
    """Test checking if health is low"""
    mock_element.properties['value'] = 20
    mock_element.properties['max_value'] = 100
    assert health_bar.is_critical is True
    
    mock_element.properties['value'] = 50
    assert health_bar.is_critical is False


def test_wait_for_full_health(health_bar, mock_element):
    """Test waiting for full health"""
    mock_element.properties['value'] = 100
    mock_element.properties['max_value'] = 100
    assert health_bar.wait_until_full(timeout=1.0) is True


def test_wait_for_health_above(health_bar, mock_element):
    """Test waiting for health above threshold"""
    mock_element.properties['value'] = 80
    assert health_bar.wait_until_health_above(75, timeout=1.0) is True


def test_wait_for_health_below(health_bar, mock_element):
    """Test waiting for health below threshold"""
    mock_element.properties['value'] = 20
    assert health_bar.wait_until_health_below(25, timeout=1.0) is True
