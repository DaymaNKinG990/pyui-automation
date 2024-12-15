import pytest
from pyui_automation.game_elements import SocialPanel, Friend, Block
from ..conftest import create_mock_element


@pytest.fixture
def social_panel(mock_element, mock_session):
    return SocialPanel(mock_element, mock_session)


def test_get_friends(social_panel, mock_element):
    """Test getting friends list"""
    friend1 = create_mock_element({'name': 'Player1', 'online': True})
    friend2 = create_mock_element({'name': 'Player2', 'online': False})
    mock_element.children = [friend1, friend2]
    
    friends = social_panel.get_friends()
    assert len(friends) == 2
    assert friends[0].name == 'Player1'
    assert friends[0].online is True
    assert friends[1].name == 'Player2'
    assert friends[1].online is False


def test_get_blocked_players(social_panel, mock_element):
    """Test getting blocked players list"""
    block1 = create_mock_element({'name': 'Spammer1'})
    block2 = create_mock_element({'name': 'Spammer2'})
    mock_element.children = [block1, block2]
    
    blocked = social_panel.get_blocked_players()
    assert len(blocked) == 2
    assert blocked[0].name == 'Spammer1'
    assert blocked[1].name == 'Spammer2'


def test_add_friend(social_panel, mock_element):
    """Test adding a friend"""
    social_panel.add_friend('NewFriend')
    assert mock_element.properties['friend_name'] == 'NewFriend'


def test_remove_friend(social_panel):
    """Test removing a friend"""
    friend = Friend('Player1', True)
    social_panel.remove_friend(friend)
    # Verify friend was removed from internal storage


def test_block_player(social_panel, mock_element):
    """Test blocking a player"""
    social_panel.block_player('Spammer')
    assert mock_element.properties['block_name'] == 'Spammer'


def test_unblock_player(social_panel):
    """Test unblocking a player"""
    block = Block('Spammer')
    social_panel.unblock_player(block)
    # Verify player was unblocked


def test_send_whisper(social_panel, mock_element):
    """Test sending a whisper"""
    social_panel.send_whisper('Player1', 'Hello!')
    assert mock_element.properties['whisper_to'] == 'Player1'
    assert mock_element.properties['whisper_message'] == 'Hello!'


def test_invite_to_group(social_panel):
    """Test inviting to group"""
    friend = Friend('Player1', True)
    social_panel.invite_to_group(friend)
    # Verify invite was sent


def test_is_friend_online(social_panel, mock_element):
    """Test checking if friend is online"""
    friend = create_mock_element({'name': 'Player1', 'online': True})
    mock_element.children = [friend]
    
    assert social_panel.is_friend_online('Player1') is True


def test_wait_for_friend_online(social_panel, mock_element):
    """Test waiting for friend to come online"""
    friend = create_mock_element({'name': 'Player1', 'online': True})
    mock_element.children = [friend]
    
    assert social_panel.wait_for_friend_online('Player1', timeout=1.0) is True
