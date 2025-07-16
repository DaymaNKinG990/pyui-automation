import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.chat_window import ChatMessage, ChatTab, ChatWindow
from datetime import datetime

@pytest.fixture
def mock_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'sender': 'Alice',
        'content': 'Hello!',
        'timestamp': 1700000000,
        'channel': 'general',
        'system_message': False,
        'name': 'general',
        'active': True,
        'unread_count': 2,
        'visible': True,
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
def chat_message(mock_element, mock_session):
    return ChatMessage(mock_element, mock_session)

@pytest.fixture
def chat_tab(mock_element, mock_session):
    return ChatTab(mock_element, mock_session)

@pytest.fixture
def chat_window(mock_element, mock_session):
    return ChatWindow(mock_element, mock_session)

def test_chat_message_properties(chat_message):
    assert chat_message.sender == 'Alice'
    assert chat_message.content == 'Hello!'
    assert isinstance(chat_message.timestamp, datetime)
    assert chat_message.channel == 'general'
    assert chat_message.is_system_message is False

def test_chat_message_reply_report(chat_message, mock_element):
    btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: btn if value in ['Reply', 'Report'] else None
    chat_message.reply()
    chat_message.report()
    assert btn.click.call_count == 2

def test_chat_tab_properties(chat_tab):
    assert chat_tab.name == 'general'
    assert chat_tab.is_active is True
    assert chat_tab.unread_count == 2

def test_chat_tab_activate(chat_tab, mock_element):
    mock_element.get_property.side_effect = lambda key: False if key == 'active' else 'x'
    chat_tab.click = MagicMock()
    chat_tab.activate()
    assert chat_tab.click.called

def test_chat_tab_close(chat_tab, mock_element):
    btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'Close' else None
    chat_tab.close()
    assert btn.click.called

def test_chat_window_messages(chat_window, mock_element, mock_session):
    msg_el = MagicMock()
    mock_element.find_elements.side_effect = lambda by=None, value=None: [msg_el] if value == 'message' else []
    win = ChatWindow(mock_element, mock_session)
    msgs = win.messages
    assert all(isinstance(m, ChatMessage) for m in msgs)

def test_chat_window_tabs(chat_window, mock_element, mock_session):
    tab_el = MagicMock()
    mock_element.find_elements.side_effect = lambda by=None, value=None: [tab_el] if value == 'tab' else []
    win = ChatWindow(mock_element, mock_session)
    tabs = win.tabs
    assert all(isinstance(t, ChatTab) for t in tabs)

def test_chat_window_active_tab(chat_window, mock_element, mock_session):
    tab_el = MagicMock()
    tab_el.get_property.side_effect = lambda key: True if key == 'active' else 'general' if key == 'name' else 'x'
    mock_element.find_elements.side_effect = lambda by=None, value=None: [tab_el] if value == 'tab' else []
    win = ChatWindow(mock_element, mock_session)
    tab = win.active_tab
    assert tab is not None
    assert tab.is_active is True

def test_chat_window_get_tab(chat_window, mock_element, mock_session):
    tab_el = MagicMock()
    tab_el.get_property.side_effect = lambda key: 'general' if key == 'name' else True if key == 'active' else 'x'
    mock_element.find_elements.side_effect = lambda by=None, value=None: [tab_el] if value == 'tab' else []
    win = ChatWindow(mock_element, mock_session)
    tab = win.get_tab('general')
    assert tab is not None
    assert tab.name == 'general'

def test_chat_window_send_message(chat_window, mock_element, mock_session):
    input_box = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: input_box if value == 'input' else None
    win = ChatWindow(mock_element, mock_session)
    win.send_message('Hi!')
    assert input_box.send_keys.call_count == 2

def test_chat_window_send_message_with_channel(chat_window, mock_element, mock_session):
    tab_el = MagicMock()
    tab_el.get_property.side_effect = lambda key: 'general' if key == 'name' else None
    tab_el.activate = MagicMock()
    mock_element.find_elements.side_effect = lambda by=None, value=None: [tab_el] if value == 'tab' else []
    input_box = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: input_box if value == 'input' else None
    win = chat_window.__class__(mock_element, mock_session)
    win.send_message('Hi!', channel='general')
    tab_el.activate.assert_called()

def test_chat_window_clear_chat(chat_window, mock_element):
    btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'Clear' else None
    chat_window.clear_chat()
    assert btn.click.called

def test_chat_window_create_tab(chat_window, mock_element, mock_session):
    new_tab_btn = MagicMock()
    mock_element.find_element.side_effect = lambda by=None, value=None: new_tab_btn if value == 'NewTab' else None
    mock_session.find_element.return_value = MagicMock()
    chat_window._session = mock_session
    chat_window.create_tab('party')
    assert new_tab_btn.click.called
    assert mock_session.find_element.return_value.send_keys.called

def test_chat_window_filter_messages(chat_window, mock_element, mock_session):
    msg1 = MagicMock()
    msg1.sender = 'Alice'
    msg1.channel = 'general'
    msg1.is_system_message = False
    msg2 = MagicMock()
    msg2.sender = 'Bob'
    msg2.channel = 'party'
    msg2.is_system_message = True
    win = chat_window.__class__(mock_element, mock_session)
    win._messages = [msg1, msg2]
    filtered = win.filter_messages(sender='Alice', channel='general')
    assert filtered == [msg1]
    assert chat_window.filter_messages(channel='party') == [msg2]
    assert chat_window.filter_messages(system_only=True) == [msg2]

def test_chat_window_wait_for_message_success(chat_window, mock_session):
    mock_session.wait_for_condition.return_value = True
    chat_window._session = mock_session
    assert chat_window.wait_for_message(content='Hello!', timeout=1.0) is True

def test_chat_window_wait_for_message_fail(chat_window, mock_session):
    mock_session.wait_for_condition.return_value = False
    chat_window._session = mock_session
    assert chat_window.wait_for_message(content='Hello!', timeout=1.0) is False

def test_chat_window_wait_for_system_message_success(chat_window, mock_session):
    mock_session.wait_for_condition.return_value = True
    chat_window._session = mock_session
    assert chat_window.wait_for_system_message('SystemMsg', timeout=1.0) is True

def test_chat_window_wait_for_system_message_fail(chat_window, mock_session):
    mock_session.wait_for_condition.return_value = False
    chat_window._session = mock_session
    assert chat_window.wait_for_system_message('SystemMsg', timeout=1.0) is False

def test_chat_message_reply_no_button(chat_message, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    chat_message.reply()  # Не должно быть исключения

def test_chat_message_report_no_button(chat_message, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    chat_message.report()  # Не должно быть исключения

def test_chat_tab_close_no_button(chat_tab, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    chat_tab.close()  # Не должно быть исключения

def test_chat_window_clear_chat_no_button(chat_window, mock_element):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    chat_window.clear_chat()  # Не должно быть исключения

def test_chat_window_create_tab_no_button(chat_window, mock_element, mock_session):
    mock_element.find_element.side_effect = lambda by=None, value=None: None
    chat_window._session = mock_session
    chat_window.create_tab('party')  # Не должно быть исключения 