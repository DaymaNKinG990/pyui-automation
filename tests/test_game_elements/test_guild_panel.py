import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.guild_panel import GuildMember, GuildRank, GuildPanel
from datetime import datetime

@pytest.fixture
def mock_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'name': 'Player1',
        'rank': 'Officer',
        'level': 50,
        'class': 'Warrior',
        'note': 'Main tank',
        'last_online': datetime(2024, 1, 1, 12, 0, 0),
        'online': True,
        'permissions': ['invite', 'kick'],
        'current_members': 10,
        'max_members': 100,
        'motd': 'Welcome!',
    }.get(key)
    el.find_elements.side_effect = lambda by=None, value=None, **kwargs: []
    el.find_element.side_effect = lambda by=None, value=None, **kwargs: None
    return el

@pytest.fixture
def mock_session():
    s = MagicMock()
    s.wait_for_condition.return_value = True
    s.find_element.return_value = MagicMock()
    return s

@pytest.fixture
def guild_member(mock_element, mock_session):
    return GuildMember(mock_element, mock_session)

@pytest.fixture
def guild_rank(mock_element, mock_session):
    return GuildRank(mock_element, mock_session)

@pytest.fixture
def guild_panel(mock_element, mock_session):
    return GuildPanel(mock_element, mock_session)

def test_guild_member_properties(guild_member):
    assert guild_member.name == 'Player1'
    assert guild_member.rank == 'Officer'
    assert guild_member.level == 50
    assert guild_member.class_name == 'Warrior'
    assert guild_member.note == 'Main tank'
    assert isinstance(guild_member.last_online, datetime)
    assert guild_member.is_online is True

def test_guild_member_promote_success(guild_member, mock_element):
    btn = MagicMock()
    btn.is_enabled.return_value = True
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: btn if value == 'promote_button' else None
    assert guild_member.promote() is True
    assert btn.click.called

def test_guild_member_promote_fail(guild_member, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: None
    assert guild_member.promote() is False

def test_guild_member_demote_success(guild_member, mock_element):
    btn = MagicMock()
    btn.is_enabled.return_value = True
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: btn if value == 'demote_button' else None
    assert guild_member.demote() is True
    assert btn.click.called

def test_guild_member_demote_fail(guild_member, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: None
    assert guild_member.demote() is False

def test_guild_member_kick_success(guild_member, mock_element):
    btn = MagicMock()
    btn.is_enabled.return_value = True
    confirm_btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: btn if value == 'kick_button' else confirm_btn if value == 'confirm_kick' else None
    assert guild_member.kick() is True
    assert btn.click.called
    assert confirm_btn.click.called

def test_guild_member_kick_fail(guild_member, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: None
    assert guild_member.kick() is False

def test_guild_member_set_note_success(guild_member, mock_element):
    note_btn = MagicMock()
    note_input = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: note_btn if value == 'note_button' else note_input if value == 'note_input' else None
    assert guild_member.set_note('New note') is True
    assert note_btn.click.called
    assert note_input.send_keys.called

def test_guild_member_set_note_fail(guild_member, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: None
    assert guild_member.set_note('New note') is False

def test_guild_rank_properties(guild_rank):
    assert guild_rank.name == 'Player1'
    assert guild_rank.permissions == ['invite', 'kick']

def test_guild_rank_rename_success(guild_rank, mock_element):
    name_field = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: name_field if value == 'rank_name' else None
    assert guild_rank.rename('NewRank') is True
    assert name_field.send_keys.called

def test_guild_rank_rename_fail(guild_rank, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: None
    assert guild_rank.rename('NewRank') is False

def test_guild_rank_set_permission_success(guild_rank, mock_element):
    perm_checkbox = MagicMock()
    perm_checkbox.is_checked.return_value = False
    mock_element.find_element.side_effect = lambda by=None, value=None, name=None, **kwargs: perm_checkbox if value == 'permission' and name == 'invite' else None
    assert guild_rank.set_permission('invite', True) is True
    assert perm_checkbox.click.called

def test_guild_rank_set_permission_fail(guild_rank, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None, name=None, **kwargs: None
    assert guild_rank.set_permission('invite', True) is False

def test_guild_panel_properties(guild_panel):
    assert guild_panel.name == 'Player1'
    assert guild_panel.level == 50
    assert guild_panel.member_count == (10, 100)
    assert guild_panel.motd == 'Welcome!'

def test_guild_panel_ranks(guild_panel, mock_element, mock_session):
    rank_el = MagicMock()
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [rank_el] if value == 'guild_rank' else []
    panel = GuildPanel(mock_element, mock_session)
    ranks = panel.ranks
    assert all(isinstance(r, GuildRank) for r in ranks)

def test_guild_panel_get_members(guild_panel, mock_element, mock_session):
    member_el = MagicMock()
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [member_el] if value == 'guild_member' else []
    panel = GuildPanel(mock_element, mock_session)
    members = panel.get_members()
    assert all(isinstance(m, GuildMember) for m in members)

def test_guild_panel_get_member_found(guild_panel, mock_element, mock_session):
    member_el = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None, name=None, **kwargs: member_el if value == 'guild_member' and name == 'Player1' else None
    panel = GuildPanel(mock_element, mock_session)
    member = panel.get_member('Player1')
    assert member is not None

def test_guild_panel_get_member_not_found(guild_panel, mock_element, mock_session):
    mock_element.find_element.side_effect = lambda by=None, value=None, name=None, **kwargs: None
    panel = GuildPanel(mock_element, mock_session)
    member = panel.get_member('NotExist')
    assert member is None

def test_guild_panel_get_rank_found(guild_panel, mock_element, mock_session):
    rank_el = MagicMock()
    rank_el.get_property.side_effect = lambda key: 'Officer' if key == 'name' else []
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [rank_el] if value == 'guild_rank' else []
    panel = GuildPanel(mock_element, mock_session)
    rank = panel.get_rank('Officer')
    assert rank is not None
    assert rank.name == 'Officer'

def test_guild_panel_get_rank_not_found(guild_panel, mock_element, mock_session):
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: []
    panel = GuildPanel(mock_element, mock_session)
    rank = panel.get_rank('NotExist')
    assert rank is None 

def test_guild_panel_set_motd_success(guild_panel, mock_element):
    motd_btn = MagicMock()
    motd_input = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: motd_btn if value == 'motd_button' else motd_input if value == 'motd_input' else None
    assert guild_panel.set_motd('New MOTD') is True
    assert motd_btn.click.called
    assert motd_input.send_keys.called

def test_guild_panel_set_motd_fail(guild_panel, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: None
    assert guild_panel.set_motd('New MOTD') is False

def test_guild_panel_invite_member_success(guild_panel, mock_element):
    invite_btn = MagicMock()
    name_input = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: invite_btn if value == 'invite_button' else name_input if value == 'player_name' else None
    assert guild_panel.invite_member('NewPlayer') is True
    assert invite_btn.click.called
    assert name_input.send_keys.called

def test_guild_panel_invite_member_fail(guild_panel, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: None
    assert guild_panel.invite_member('NewPlayer') is False

def test_guild_panel_search_members_found(guild_panel, mock_element, mock_session):
    search_box = MagicMock()
    result_el = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: search_box if value == 'search' else None
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [result_el] if value == 'search_result' else []
    panel = GuildPanel(mock_element, mock_session)
    results = panel.search_members('Player')
    assert all(isinstance(m, GuildMember) for m in results)
    assert search_box.send_keys.called

def test_guild_panel_search_members_none(guild_panel, mock_element, mock_session):
    search_box = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None, **kwargs: search_box if value == 'search' else None
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: []
    panel = GuildPanel(mock_element, mock_session)
    results = panel.search_members('NotExist')
    assert results == []
    assert search_box.send_keys.called

def test_guild_panel_get_online_members(guild_panel, mock_element, mock_session):
    online_el = MagicMock()
    offline_el = MagicMock()
    online_el.get_property.side_effect = lambda key: True if key == 'online' else None
    offline_el.get_property.side_effect = lambda key: False if key == 'online' else None
    mock_element.find_elements.side_effect = lambda by=None, value=None, **kwargs: [online_el, offline_el] if value == 'guild_member' else []
    panel = GuildPanel(mock_element, mock_session)
    members = panel.get_online_members()
    assert len(members) == 1
    assert members[0].is_online is True

def test_guild_panel_wait_for_member_online_success(guild_panel, mock_session):
    mock_session.wait_for_condition.return_value = True
    assert guild_panel.wait_for_member_online('Player1', timeout=5) is True
    mock_session.wait_for_condition.assert_called()

def test_guild_panel_wait_for_member_online_fail(guild_panel, mock_session):
    mock_session.wait_for_condition.return_value = False
    assert guild_panel.wait_for_member_online('Player1', timeout=1) is False
    mock_session.wait_for_condition.assert_called() 