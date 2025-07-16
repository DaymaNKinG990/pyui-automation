import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.party_frame import PartyMember, PartyFrame

@pytest.fixture
def mock_member_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'name': 'Player1',
        'class': 'Warrior',
        'role': 'tank',
        'level': 60,
        'current_health': 5000,
        'max_health': 5000,
        'current_resource': 100,
        'max_resource': 100,
        'online': True,
        'dead': False,
        'leader': False,
        'buffs': [{'name': 'Fortitude'}],
        'debuffs': [],
    }.get(key)
    el.find_element.side_effect = lambda *a, **kw: None
    el.click = MagicMock()
    return el

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def member(mock_member_element, mock_session):
    return PartyMember(mock_member_element, mock_session)

def test_member_properties(member):
    assert member.name == 'Player1'
    assert member.class_name == 'Warrior'
    assert member.role == 'tank'
    assert member.level == 60
    assert member.health == (5000, 5000)
    assert member.resource == (100, 100)
    assert member.is_online is True
    assert member.is_dead is False
    assert member.is_leader is False
    assert member.buffs == [{'name': 'Fortitude'}]
    assert member.debuffs == []

def test_member_target(member, mock_member_element):
    member.target()
    assert mock_member_element.click.called

def test_member_promote_leader_success(member, mock_member_element):
    mock_member_element.get_property.side_effect = lambda key: False if key == 'leader' else None
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    mock_member_element.find_element.side_effect = lambda *a, **kw: btn if kw.get('value') == 'promote_leader' else None
    assert member.promote_leader() is True
    assert btn.click.called

def test_member_promote_leader_already_leader(member, mock_member_element):
    mock_member_element.get_property.side_effect = lambda key: True if key == 'leader' else None
    assert member.promote_leader() is False

def test_member_promote_leader_button_disabled(member, mock_member_element):
    mock_member_element.get_property.side_effect = lambda key: False if key == 'leader' else None
    btn = MagicMock()
    btn.is_enabled.return_value = False
    mock_member_element.find_element.side_effect = lambda *a, **kw: btn if kw.get('value') == 'promote_leader' else None
    assert member.promote_leader() is False

def test_member_kick_success(member, mock_member_element):
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    confirm = MagicMock()
    confirm.click = MagicMock()
    def find_element_side_effect(*a, **kw):
        if kw.get('value') == 'kick_button':
            return btn
        if kw.get('value') == 'confirm_kick':
            return confirm
        return None
    mock_member_element.find_element.side_effect = find_element_side_effect
    assert member.kick() is True
    assert btn.click.called
    assert confirm.click.called

def test_member_kick_button_disabled(member, mock_member_element):
    btn = MagicMock()
    btn.is_enabled.return_value = False
    mock_member_element.find_element.side_effect = lambda *a, **kw: btn if kw.get('value') == 'kick_button' else None
    assert member.kick() is False

def test_member_kick_no_confirm(member, mock_member_element):
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    mock_member_element.find_element.side_effect = lambda *a, **kw: btn if kw.get('value') == 'kick_button' else None
    assert member.kick() is False

def test_member_set_role_success(member, mock_member_element):
    btn = MagicMock()
    btn.click = MagicMock()
    option = MagicMock()
    option.click = MagicMock()
    def find_element_side_effect(*a, **kw):
        if kw.get('value') == 'role_button':
            return btn
        if kw.get('value') == 'role_option' and kw.get('role') == 'healer':
            return option
        return None
    mock_member_element.find_element.side_effect = find_element_side_effect
    assert member.set_role('healer') is True
    assert btn.click.called
    assert option.click.called

def test_member_set_role_no_button(member, mock_member_element):
    mock_member_element.find_element.side_effect = lambda *a, **kw: None
    assert member.set_role('healer') is False

def test_member_set_role_no_option(member, mock_member_element):
    btn = MagicMock()
    btn.click = MagicMock()
    mock_member_element.find_element.side_effect = lambda *a, **kw: btn if kw.get('value') == 'role_button' else None
    assert member.set_role('healer') is False

def test_member_get_property_exception(member, mock_member_element):
    mock_member_element.get_property.side_effect = Exception('fail')
    with pytest.raises(Exception):
        _ = member.name

def test_member_promote_leader_find_element_exception(member, mock_member_element):
    mock_member_element.get_property.side_effect = lambda key: False if key == 'leader' else None
    mock_member_element.find_element.side_effect = Exception('fail')
    with pytest.raises(Exception):
        member.promote_leader()

def test_member_kick_find_element_exception(member, mock_member_element):
    mock_member_element.find_element.side_effect = Exception('fail')
    with pytest.raises(Exception):
        member.kick()

def test_member_set_role_find_element_exception(member, mock_member_element):
    mock_member_element.find_element.side_effect = Exception('fail')
    with pytest.raises(Exception):
        member.set_role('healer')

@pytest.fixture
def mock_frame_element():
    el = MagicMock()
    el.find_elements.side_effect = lambda *a, **kw: []
    el.get_property.side_effect = lambda key: False if key == 'is_raid' else None
    return el

@pytest.fixture
def frame(mock_frame_element, mock_session):
    return PartyFrame(mock_frame_element, mock_session)

def test_frame_is_raid(frame, mock_frame_element):
    mock_frame_element.get_property.side_effect = lambda key: True if key == 'is_raid' else None
    assert frame.is_raid is True

def test_frame_size_empty(frame, mock_frame_element):
    mock_frame_element.find_elements.side_effect = lambda *a, **kw: []
    assert frame.size == 0

def test_frame_leader_none(frame, mock_frame_element):
    mock_frame_element.find_elements.side_effect = lambda *a, **kw: []
    assert frame.leader is None

def test_frame_get_members_empty(frame, mock_frame_element):
    mock_frame_element.find_elements.side_effect = lambda *a, **kw: []
    assert frame.get_members() == []

def test_frame_get_member_none(frame, mock_frame_element):
    mock_frame_element.find_elements.side_effect = lambda *a, **kw: []
    assert frame.get_member('Player1') is None

def test_frame_get_members_find_elements_exception(frame, mock_frame_element):
    mock_frame_element.find_elements.side_effect = Exception('fail')
    with pytest.raises(Exception):
        frame.get_members() 