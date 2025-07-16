import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.character_stats import StatAttribute, CharacterStats

@pytest.fixture
def mock_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'name': 'Strength',
        'value': 15.0,
        'base_value': 10.0,
        'modifiers': [{'type': 'buff', 'amount': 5}],
        'level': 5,
        'current_xp': 100,
        'required_xp': 200,
        'unspent_points': 3,
    }.get(key)
    el.find_elements.side_effect = lambda by=None, value=None: []
    el.find_element.side_effect = lambda by=None, value=None: None
    return el

@pytest.fixture
def mock_session():
    s = MagicMock()
    s.wait_for_condition.return_value = True
    s.find_element.return_value = MagicMock()
    return s

@pytest.fixture
def stat_attr(mock_element, mock_session):
    return StatAttribute(mock_element, mock_session)

@pytest.fixture
def char_stats(mock_element, mock_session):
    return CharacterStats(mock_element, mock_session)

def test_stat_attribute_properties(stat_attr):
    assert stat_attr.name == 'Strength'
    assert stat_attr.value == 15.0
    assert stat_attr.base_value == 10.0
    assert stat_attr.bonus_value == 5.0
    assert stat_attr.modifiers == [{'type': 'buff', 'amount': 5}]

def test_stat_attribute_wait_until_value_above(stat_attr, mock_session):
    assert stat_attr.wait_until_value_above(10.0, timeout=1.0) is True

def test_stat_attribute_wait_until_value_below(stat_attr, mock_session):
    assert stat_attr.wait_until_value_below(20.0, timeout=1.0) is True

def test_character_stats_properties(char_stats):
    assert char_stats.level == 5
    assert char_stats.experience == (100, 200)
    assert char_stats.unspent_points == 3

def test_character_stats_attributes(char_stats, mock_element, mock_session):
    attr_el = MagicMock()
    mock_element.find_elements.side_effect = lambda by=None, value=None: [attr_el] if value == 'attribute' else []
    stats = CharacterStats(mock_element, mock_session)
    attrs = stats.attributes
    assert all(isinstance(a, StatAttribute) for a in attrs)

def test_get_attribute_found(char_stats, mock_element, mock_session):
    attr_el = MagicMock()
    attr_el.get_property.side_effect = lambda key: 'Strength' if key == 'name' else 10.0
    mock_element.find_elements.side_effect = lambda by=None, value=None: [attr_el] if value == 'attribute' else []
    stats = CharacterStats(mock_element, mock_session)
    attr = stats.get_attribute('Strength')
    assert attr is not None
    assert attr.name == 'Strength'

def test_get_attribute_not_found(char_stats, mock_element, mock_session):
    mock_element.find_elements.side_effect = lambda by=None, value=None: []
    stats = CharacterStats(mock_element, mock_session)
    attr = stats.get_attribute('Agility')
    assert attr is None

def test_increase_attribute_success(char_stats, mock_element, mock_session):
    attr_el = MagicMock()
    attr_el.get_property.side_effect = lambda key: 'Strength' if key == 'name' else 10.0
    btn = MagicMock()
    attr_el.find_element.side_effect = lambda by=None, value=None: btn if value == 'Increase' else None
    mock_element.find_elements.side_effect = lambda by=None, value=None: [attr_el] if value == 'attribute' else []
    stats = CharacterStats(mock_element, mock_session)
    stats.increase_attribute('Strength', points=2)
    assert btn.click.call_count == 2

def test_increase_attribute_not_enough_points(char_stats, mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: 0 if key == 'unspent_points' else 'x'
    stats = CharacterStats(mock_element, mock_session)
    with pytest.raises(ValueError):
        stats.increase_attribute('Strength', points=1)

def test_increase_attribute_not_found(char_stats, mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: 3 if key == 'unspent_points' else 'x'
    mock_element.find_elements.side_effect = lambda by=None, value=None: []
    stats = CharacterStats(mock_element, mock_session)
    with pytest.raises(ValueError):
        stats.increase_attribute('Agility', points=1)

def test_increase_attribute_no_button(char_stats, mock_element, mock_session):
    attr_el = MagicMock()
    attr_el.get_property.side_effect = lambda key: 'Strength' if key == 'name' else 10.0
    attr_el.find_element.side_effect = lambda by=None, value=None: None
    mock_element.find_elements.side_effect = lambda by=None, value=None: [attr_el] if value == 'attribute' else []
    stats = CharacterStats(mock_element, mock_session)
    stats.increase_attribute('Strength', points=1)  # Не должно быть исключения

def test_reset_attributes_success(char_stats, mock_element, mock_session):
    reset_btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: reset_btn if value == 'Reset' else None
    mock_session.find_element.return_value = MagicMock()
    stats = CharacterStats(mock_element, mock_session)
    stats.reset_attributes()
    assert reset_btn.click.called
    assert mock_session.find_element.return_value.click.called

def test_reset_attributes_no_button(char_stats, mock_element, mock_session):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    stats = CharacterStats(mock_element, mock_session)
    with pytest.raises(ValueError):
        stats.reset_attributes()

def test_wait_until_level_up(char_stats, mock_session):
    assert char_stats.wait_until_level_up(timeout=1.0) is True

def test_wait_until_points_available(char_stats, mock_session):
    assert char_stats.wait_until_points_available(points=2, timeout=1.0) is True 