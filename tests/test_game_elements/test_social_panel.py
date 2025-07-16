import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements import SocialPanel


@pytest.fixture
def mock_element():
    mock = MagicMock()
    mock.find_elements.return_value = []
    mock.get_property.return_value = None
    mock.get_attribute.return_value = None
    return mock

@pytest.fixture
def mock_session():
    mock = MagicMock()
    mock.find_element.return_value = None
    mock.find_elements.return_value = []
    return mock

@pytest.fixture
def social_panel(mock_element, mock_session):
    return SocialPanel(mock_element({}), mock_session)


def test_get_friends(social_panel, mock_element):
    """Test getting friends list"""
    friend1 = MagicMock()
    friend1.get_property.side_effect = lambda key: {'name': 'Player1', 'online': True, 'status': 'online'}.get(key)
    
    friend2 = MagicMock()
    friend2.get_property.side_effect = lambda key: {'name': 'Player2', 'online': False, 'status': 'offline'}.get(key)
    
    # Мокаем find_elements для друзей
    mock_element.find_elements.side_effect = lambda **kwargs: [friend1, friend2] if kwargs.get('by') == 'type' and kwargs.get('value') == 'friend' else []
    social_panel = SocialPanel(mock_element, MagicMock())
    
    friends = social_panel.get_friends()
    assert len(friends) == 2
    assert friends[0].name == 'Player1'
    assert friends[0].is_online is True
    assert friends[1].name == 'Player2'
    assert friends[1].is_online is False


def test_get_blocked_players(social_panel, mock_element):
    """Test getting blocked players list"""
    block1 = MagicMock()
    block1.get_property.side_effect = lambda key: {'name': 'Spammer1'}.get(key)
    
    block2 = MagicMock()
    block2.get_property.side_effect = lambda key: {'name': 'Spammer2'}.get(key)
    
    # Мокаем find_elements для блокированных
    mock_element.find_elements.side_effect = lambda **kwargs: [block1, block2] if kwargs.get('by') == 'type' and kwargs.get('value') == 'block' else []
    social_panel = SocialPanel(mock_element, MagicMock())
    
    blocked = social_panel.get_blocked_players()
    assert len(blocked) == 2
    assert blocked[0].name == 'Spammer1'
    assert blocked[1].name == 'Spammer2'


def test_add_friend(social_panel, mock_element):
    """Test adding a friend"""
    add_button = MagicMock()
    add_button.click = lambda: None
    mock_element.find_element.return_value = add_button
    
    name_input = MagicMock()
    name_input.send_keys = lambda text: None
    mock_element.find_element.return_value = name_input
    
    social_panel.add_friend('NewFriend')
    # Success if no exception raised


def test_remove_friend(social_panel, mock_element):
    """Test removing a friend"""
    friend = MagicMock()
    friend.get_property.side_effect = lambda key: {'name': 'Player1', 'online': True}.get(key)
    friend.right_click = lambda: None
    
    mock_element.find_elements.return_value = [friend]
    
    social_panel.remove_friend('Player1')
    # Success if no exception raised


def test_block_player(social_panel, mock_element):
    """Test blocking a player"""
    block_button = MagicMock()
    block_button.click = lambda: None
    mock_element.find_element.return_value = block_button
    
    name_input = MagicMock()
    name_input.send_keys = lambda text: None
    mock_element.find_element.return_value = name_input
    
    social_panel.block_player('Spammer')
    # Success if no exception raised


def test_unblock_player(social_panel, mock_element):
    """Test unblocking a player"""
    block = MagicMock()
    block.get_property.side_effect = lambda key: {'name': 'Spammer'}.get(key)
    block.right_click = lambda: None
    
    mock_element.find_elements.return_value = [block]
    
    social_panel.unblock_player('Spammer')
    # Success if no exception raised


def test_send_whisper(social_panel, mock_element):
    """Test sending a whisper"""
    chat_input = MagicMock()
    chat_input.send_keys = lambda text: None
    mock_element.find_element.return_value = chat_input
    
    social_panel.send_whisper('Player1', 'Hello!')
    # Success if no exception raised


def test_invite_to_group(social_panel, mock_element):
    """Test inviting to group"""
    friend = MagicMock()
    friend.get_property.side_effect = lambda key: {'name': 'Player1', 'online': True}.get(key)
    friend.right_click = lambda: None
    
    mock_element.find_elements.return_value = [friend]
    
    social_panel.invite_to_group('Player1')
    # Success if no exception raised


def test_is_friend_online(social_panel, mock_element):
    """Test checking if friend is online"""
    friend = MagicMock()
    friend.get_property.side_effect = lambda key: {'name': 'Player1', 'online': True}.get(key)
    
    mock_element.find_elements.return_value = [friend]
    
    assert social_panel.is_friend_online('Player1') is True


def test_wait_for_friend_online(social_panel, mock_element):
    """Test waiting for friend to come online"""
    friend = MagicMock()
    friend.get_property.side_effect = lambda key: {'name': 'Player1', 'online': True, 'status': 'online'}.get(key)
    mock_element.find_elements.side_effect = lambda **kwargs: [friend] if kwargs.get('by') == 'type' and kwargs.get('value') == 'friend' else []
    # Мокаем метод ожидания
    social_panel._session.wait_for_condition = lambda *a, **kw: True
    assert social_panel.wait_for_friend_online('Player1', timeout=1.0) is True
