import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.achievement_panel import AchievementPanel, Achievement, AchievementCriteria
from datetime import datetime

@pytest.fixture
def mock_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'title': 'Champion',
        'description': 'Win 100 battles',
        'points': 10,
        'category': 'Combat',
        'completed': True,
        'completion_timestamp': 1700000000,
        'rewards': {'gold': 100},
        'total_points': 100,
        'completed_count': 5,
        'categories': ['Combat', 'Exploration'],
    }.get(key)
    el.find_elements.side_effect = lambda by=None, value=None: []
    el.find_element.side_effect = lambda by=None, value=None: None
    return el

@pytest.fixture
def mock_session():
    s = MagicMock()
    s.wait_for_condition.return_value = True
    return s

@pytest.fixture
def achievement(mock_element, mock_session):
    return Achievement(mock_element, mock_session)

@pytest.fixture
def achievement_panel(mock_element, mock_session):
    return AchievementPanel(mock_element, mock_session)

@pytest.fixture
def criteria_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'description': 'Win 10 battles',
        'current_progress': 10,
        'required_progress': 10,
    }.get(key)
    return el

@pytest.fixture
def achievement_criteria(criteria_element, mock_session):
    return AchievementCriteria(criteria_element, mock_session)

def test_achievement_properties(achievement):
    assert achievement.title == 'Champion'
    assert achievement.description == 'Win 100 battles'
    assert achievement.points == 10
    assert achievement.category == 'Combat'
    assert achievement.is_completed is True
    assert isinstance(achievement.completion_date, datetime)
    assert achievement.rewards == {'gold': 100}

def test_achievement_criteria_properties(achievement_criteria):
    assert achievement_criteria.description == 'Win 10 battles'
    assert achievement_criteria.progress == (10, 10)
    assert achievement_criteria.is_completed is True

def test_achievement_criteria_in_achievement(mock_element, mock_session, criteria_element):
    mock_element.find_elements.side_effect = lambda by=None, value=None: [criteria_element]
    ach = Achievement(mock_element, mock_session)
    crits = ach.criteria
    assert len(crits) == 1
    assert isinstance(crits[0], AchievementCriteria)

def test_track_and_show_in_map(achievement, mock_element):
    btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: btn if value in ["Track", "ShowInMap"] else None
    achievement.track()
    achievement.show_in_map()
    assert btn.click.call_count == 2

def test_wait_until_completed(achievement, mock_session):
    assert achievement.wait_until_completed(timeout=1.0) is True

def test_achievement_panel_properties(achievement_panel):
    assert achievement_panel.total_points == 100
    assert achievement_panel.completed_count == 5
    assert achievement_panel.categories == ['Combat', 'Exploration']

def test_tracked_achievements(achievement_panel, mock_element, mock_session):
    tracked_el = MagicMock()
    mock_element.find_elements.side_effect = lambda by=None, value=None: [tracked_el] if value and value.get('tracked') else []
    tracked = achievement_panel.tracked_achievements
    assert all(isinstance(a, Achievement) for a in tracked)

def test_get_achievements_filtering(mock_element, mock_session):
    el1 = MagicMock()
    el1.get_property.side_effect = lambda key: {'category': 'Combat', 'completed': True, 'title': 'A1'}.get(key)
    el2 = MagicMock()
    el2.get_property.side_effect = lambda key: {'category': 'Exploration', 'completed': False, 'title': 'A2'}.get(key)
    mock_element.find_elements.side_effect = lambda by=None, value=None: [el1, el2]
    panel = AchievementPanel(mock_element, mock_session)
    all_ach = panel.get_achievements()
    combat = panel.get_achievements(category='Combat')
    completed = panel.get_achievements(completed_only=True)
    assert len(all_ach) == 2
    assert all(a.category in ['Combat', 'Exploration'] for a in all_ach)
    assert all(a.category == 'Combat' for a in combat)
    assert all(a.is_completed for a in completed)

def test_get_achievement_by_title(mock_element, mock_session):
    el1 = MagicMock()
    el1.get_property.side_effect = lambda key: {'title': 'A1'}.get(key)
    mock_element.find_elements.side_effect = lambda by=None, value=None: [el1]
    panel = AchievementPanel(mock_element, mock_session)
    ach = panel.get_achievement('A1')
    assert ach is not None
    assert ach.title == 'A1'

def test_get_achievement_by_title_not_found(mock_element, mock_session):
    mock_element.find_elements.side_effect = lambda by=None, value=None: []
    panel = AchievementPanel(mock_element, mock_session)
    ach = panel.get_achievement('NotExist')
    assert ach is None 

def test_search(achievement_panel, mock_element, mock_session):
    search_box = MagicMock()
    search_box.send_keys = MagicMock()
    result_el = MagicMock()
    result_el.get_property.side_effect = lambda key: 'FindMe' if key == 'title' else None
    mock_element.find_element.side_effect = lambda by=None, value=None: search_box if by == 'type' and value == 'search' else None
    mock_element.find_elements.side_effect = lambda by=None, value=None: [result_el] if by == 'type' and value == 'search_result' else []
    panel = achievement_panel.__class__(mock_element, mock_session)
    result = panel.search('FindMe')
    assert len(result) == 1
    assert result[0].title == 'FindMe'
    search_box.send_keys.assert_called_with('FindMe')

def test_select_category(achievement_panel, mock_element):
    category_list = MagicMock()
    category_item = MagicMock()
    category_item.click = MagicMock()
    category_list.find_element.side_effect = lambda by=None, value=None: category_item if by == 'name' and value == 'Combat' else None
    mock_element.get_property.side_effect = lambda key: ['Combat', 'Exploration'] if key == 'categories' else None
    mock_element.find_element.side_effect = lambda by=None, value=None: category_list if by == 'type' and value == 'category_list' else None
    panel = achievement_panel.__class__(mock_element, achievement_panel._session)
    panel.select_category('Combat')
    category_item.click.assert_called()

def test_wait_until_achievement_unlocked(achievement_panel, mock_session):
    mock_session.wait_for_condition.return_value = True
    assert achievement_panel.wait_until_achievement_unlocked('Champion', timeout=1.0) is True

def test_wait_until_points_earned(achievement_panel, mock_session):
    mock_session.wait_for_condition.return_value = True
    assert achievement_panel.wait_until_points_earned(100, timeout=1.0) is True

def test_get_achievements_empty(mock_element, mock_session):
    mock_element.find_elements.side_effect = lambda by=None, value=None: []
    panel = AchievementPanel(mock_element, mock_session)
    assert panel.get_achievements() == []

def test_criteria_empty(mock_element, mock_session):
    mock_element.find_elements.side_effect = lambda by=None, value=None: []
    ach = Achievement(mock_element, mock_session)
    assert ach.criteria == []

def test_track_no_button(achievement, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    achievement.track()  # Не должно быть исключения

def test_show_in_map_no_button(achievement, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    achievement.show_in_map()  # Не должно быть исключения

def test_completion_date_none(mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: None if key == 'completion_timestamp' else 'x'
    ach = Achievement(mock_element, mock_session)
    assert ach.completion_date is None

def test_is_completed_false(mock_element, mock_session):
    mock_element.get_property.side_effect = lambda key: False if key == 'completed' else 'x'
    ach = Achievement(mock_element, mock_session)
    assert ach.is_completed is False

def test_criteria_is_completed_false(criteria_element, mock_session):
    criteria_element.get_property.side_effect = lambda key: 5 if key == 'current_progress' else 10 if key == 'required_progress' else 'desc'
    crit = AchievementCriteria(criteria_element, mock_session)
    assert crit.is_completed is False 