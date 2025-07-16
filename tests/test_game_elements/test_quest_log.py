import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.quest_log import QuestLog, Quest

@pytest.fixture
def mock_quest_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'name': 'Find the Sword',
        'title': 'Find the Sword',
        'description': 'Retrieve the lost sword',
        'status': 'active',
        'is_tracked': False,
        'objectives': ['Go to cave', 'Defeat boss'],
        'rewards': {'xp': 100, 'gold': 50},
    }.get(key)
    el.find_element.side_effect = lambda by=None, value=None: None
    return el

@pytest.fixture
def mock_quest_element_completed():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'name': 'Find the Sword',
        'title': 'Find the Sword',
        'description': 'Retrieve the lost sword',
        'status': 'completed',
        'is_tracked': True,
        'objectives': ['Go to cave', 'Defeat boss'],
        'rewards': {'xp': 100, 'gold': 50},
    }.get(key)
    el.find_element.side_effect = lambda by=None, value=None: None
    return el

@pytest.fixture
def mock_log_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'quests': []
    }.get(key)
    el.find_elements.side_effect = lambda by=None, value=None: []
    return el

@pytest.fixture
def mock_session():
    s = MagicMock()
    s.find_element.return_value = MagicMock()
    return s

@pytest.fixture
def quest(mock_quest_element, mock_session):
    return Quest(mock_quest_element, mock_session)

@pytest.fixture
def quest_completed(mock_quest_element_completed, mock_session):
    return Quest(mock_quest_element_completed, mock_session)

@pytest.fixture
def quest_log(mock_log_element, mock_session):
    return QuestLog(mock_log_element, mock_session)

def test_quest_properties(quest):
    assert quest.title == 'Find the Sword'
    assert quest.description == 'Retrieve the lost sword'
    assert quest.status == 'active'
    assert quest.is_tracked is False
    # objectives и rewards не тестируем здесь

def test_quest_track_untrack(quest, mock_quest_element):
    btn = MagicMock()
    mock_quest_element.get_property.side_effect = lambda key: False if key == 'tracked' else 'Find the Sword' if key == 'title' else 'active' if key == 'status' else None
    mock_quest_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'Track' else None
    quest.track()
    assert btn.click.called
    mock_quest_element.get_property.side_effect = lambda key: True if key == 'tracked' else 'Find the Sword' if key == 'title' else 'active' if key == 'status' else None
    btn2 = MagicMock()
    mock_quest_element.find_element.side_effect = lambda by=None, value=None: btn2 if value == 'Untrack' else None
    quest.untrack()
    assert btn2.click.called

def test_quest_abandon_success(quest, mock_quest_element, mock_session):
    mock_quest_element.get_property.side_effect = lambda key: 'active' if key == 'status' else 'Find the Sword' if key == 'title' else None
    btn = MagicMock()
    mock_quest_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'Abandon' else None
    mock_session.find_element.return_value = MagicMock()
    quest._session = mock_session
    quest.abandon()
    assert btn.click.called
    assert mock_session.find_element.return_value.click.called

def test_quest_abandon_completed(quest_completed, mock_quest_element_completed):
    mock_quest_element_completed.get_property.side_effect = lambda key: 'completed' if key == 'status' else 'Find the Sword' if key == 'title' else None
    with pytest.raises(ValueError):
        quest_completed.abandon()

def test_quest_show_on_map(quest, mock_quest_element):
    btn = MagicMock()
    mock_quest_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'ShowOnMap' else None
    quest.show_on_map()
    assert btn.click.called

def test_quest_log_active_quests(quest_log, mock_log_element, mock_session):
    quest_el = MagicMock()
    mock_log_element.find_elements.side_effect = lambda by=None, value=None: [quest_el] if by == 'state' and value == {'status': 'active'} else []
    log = QuestLog(mock_log_element, mock_session)
    quests = log.active_quests
    assert all(isinstance(q, Quest) for q in quests)

def test_quest_log_get_quest_found(quest_log, mock_log_element, mock_session):
    quest_el = MagicMock()
    quest_el.get_property.side_effect = lambda key: 'Find the Sword' if key == 'title' else 'active'
    mock_log_element.find_elements.side_effect = lambda by=None, value=None: [quest_el] if by == 'state' and value == {'status': 'active'} else []
    log = QuestLog(mock_log_element, mock_session)
    q = log.get_quest('Find the Sword')
    assert q is not None
    assert q.title == 'Find the Sword'

def test_quest_log_get_quest_not_found(quest_log, mock_log_element, mock_session):
    mock_log_element.find_elements.side_effect = lambda by=None, value=None: []
    log = QuestLog(mock_log_element, mock_session)
    q = log.get_quest('NotExist')
    assert q is None 