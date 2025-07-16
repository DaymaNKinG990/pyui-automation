import pytest
from unittest.mock import MagicMock
from pyui_automation.game_elements.mail_system import MailSystem, Mail, MailAttachment

@pytest.fixture
def mock_mail_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'sender': 'NPC',
        'subject': 'Welcome',
        'body': 'Hello adventurer!',
        'text': 'Hello adventurer!',
        'is_read': False,
        'read': False,
        'has_attachments': True,
        'received_at': '2024-01-01T12:00:00',
    }.get(key)
    el.find_elements.side_effect = lambda by=None, value=None: []
    el.find_element.side_effect = lambda by=None, value=None: None
    return el

@pytest.fixture
def mock_attachment_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'item_name': 'Gold Coin',
        'name': 'Gold Coin',
        'quantity': 100,
    }.get(key)
    return el

@pytest.fixture
def mock_system_element():
    el = MagicMock()
    el.get_property.side_effect = lambda key: {
        'unread_count': 2,
    }.get(key)
    el.find_elements.side_effect = lambda by=None, value=None: []
    return el

@pytest.fixture
def mock_session():
    return MagicMock()

@pytest.fixture
def mail(mock_mail_element, mock_session):
    return Mail(mock_mail_element, mock_session)

@pytest.fixture
def attachment(mock_attachment_element, mock_session):
    return MailAttachment(mock_attachment_element, mock_session)

@pytest.fixture
def mail_system(mock_system_element, mock_session):
    return MailSystem(mock_system_element, mock_session)

def test_mail_properties(mail):
    assert mail.sender == 'NPC'
    assert mail.subject == 'Welcome'
    assert mail.text == 'Hello adventurer!'
    assert mail.is_read is False
    # attachments и gold не тестируем здесь

def test_mail_mark_read(mail, mock_mail_element):
    btn = MagicMock()
    mock_mail_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'MarkRead' else None
    mail.mark_read()
    assert btn.click.called

def test_mail_attachments_property(mail, mock_mail_element, mock_session):
    att_el = MagicMock()
    mock_mail_element.find_elements.side_effect = lambda by=None, value=None: [att_el] if value == 'attachment' else []
    m = Mail(mock_mail_element, mock_session)
    atts = m.attachments
    assert all(isinstance(a, MailAttachment) for a in atts)

def test_mail_attachment_properties(attachment):
    assert attachment.name == 'Gold Coin'
    assert attachment.quantity == 100

def test_mail_attachment_take(attachment, mock_attachment_element):
    mock_attachment_element.get_property.side_effect = lambda key: True if key == 'can_take' else 'Gold Coin' if key == 'name' else 100 if key == 'quantity' else None
    mock_attachment_element.click = MagicMock()
    assert attachment.take() is True
    assert mock_attachment_element.click.called

def test_mail_system_unread_count(mail_system):
    assert mail_system.unread_count == 2

def test_mail_system_get_all_mail(mail_system, mock_system_element, mock_session):
    mail_el = MagicMock()
    mock_system_element.find_elements.side_effect = lambda by=None, value=None: [mail_el] if value == 'mail' else []
    ms = MailSystem(mock_system_element, mock_session)
    mails = ms.get_all_mail()
    assert all(isinstance(m, Mail) for m in mails)

def test_mail_system_get_mail_found(mail_system, mock_system_element, mock_session):
    mail_el = MagicMock()
    mail_el.get_property.side_effect = lambda key: 'Welcome' if key == 'subject' else 'NPC'
    mock_system_element.find_element.side_effect = lambda by=None, value=None, index=0: mail_el if value == 'mail' and index == 0 else None
    ms = MailSystem(mock_system_element, mock_session)
    m = ms.get_mail(0)
    assert m is not None
    assert m.subject == 'Welcome'

def test_mail_system_get_mail_not_found(mail_system, mock_system_element, mock_session):
    mock_system_element.find_element.side_effect = lambda by=None, value=None, index=0: None
    ms = MailSystem(mock_system_element, mock_session)
    m = ms.get_mail(0)
    assert m is None 

def test_mail_take_gold_success(mail, mock_mail_element):
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    mock_mail_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'take_gold' else None
    mock_mail_element.get_property.side_effect = lambda key: True if key == 'has_gold' else None
    assert mail.take_gold() is True
    assert btn.click.called

def test_mail_take_gold_no_gold(mail, mock_mail_element):
    mock_mail_element.get_property.side_effect = lambda key: False if key == 'has_gold' else None
    assert mail.take_gold() is False

def test_mail_take_gold_button_disabled(mail, mock_mail_element):
    btn = MagicMock()
    btn.is_enabled.return_value = False
    mock_mail_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'take_gold' else None
    mock_mail_element.get_property.side_effect = lambda key: True if key == 'has_gold' else None
    assert mail.take_gold() is False

def test_mail_take_all_attachments_success(mail, mock_mail_element):
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    mock_mail_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'take_all' else None
    assert mail.take_all_attachments() is True
    assert btn.click.called

def test_mail_take_all_attachments_button_disabled(mail, mock_mail_element):
    btn = MagicMock()
    btn.is_enabled.return_value = False
    mock_mail_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'take_all' else None
    assert mail.take_all_attachments() is False

def test_mail_delete_success(mail, mock_mail_element):
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    mock_mail_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'delete_button' else None
    assert mail.delete() is True
    assert btn.click.called

def test_mail_delete_button_disabled(mail, mock_mail_element):
    btn = MagicMock()
    btn.is_enabled.return_value = False
    mock_mail_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'delete_button' else None
    assert mail.delete() is False

def test_mail_return_to_sender_success(mail, mock_mail_element):
    btn = MagicMock()
    btn.is_enabled.return_value = True
    btn.click = MagicMock()
    mock_mail_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'return_button' else None
    assert mail.return_to_sender() is True
    assert btn.click.called

def test_mail_return_to_sender_button_disabled(mail, mock_mail_element):
    btn = MagicMock()
    btn.is_enabled.return_value = False
    mock_mail_element.find_element.side_effect = lambda by=None, value=None: btn if value == 'return_button' else None
    assert mail.return_to_sender() is False

def test_mail_mark_read_no_button(mail, mock_mail_element):
    mock_mail_element.find_element.side_effect = lambda by=None, value=None: None
    assert mail.mark_read() is False

def test_mail_attachment_take_cannot_take(attachment, mock_attachment_element):
    mock_attachment_element.get_property.side_effect = lambda key: False if key == 'can_take' else 'Gold Coin' if key == 'name' else 100 if key == 'quantity' else None
    assert attachment.take() is False

def test_mail_properties_invalid_values(mail, mock_mail_element):
    mock_mail_element.get_property.side_effect = lambda key: None
    assert mail.subject is None
    assert mail.sender is None
    assert mail.text is None
    assert mail.received_time is None
    assert mail.expires_in is None
    assert mail.has_gold is None
    assert mail.gold_amount is None
    assert mail.is_read is None
    # attachments должен вернуть пустой список
    mock_mail_element.find_elements.side_effect = lambda by=None, value=None: []
    assert mail.attachments == []

def test_mail_methods_find_element_exception(mail, mock_mail_element):
    mock_mail_element.find_element.side_effect = Exception('fail')
    assert mail.take_gold() is False
    assert mail.take_all_attachments() is False
    assert mail.delete() is False
    assert mail.return_to_sender() is False
    assert mail.mark_read() is False

def test_mail_attachment_get_property_exception(attachment, mock_attachment_element):
    mock_attachment_element.get_property.side_effect = Exception('fail')
    with pytest.raises(Exception):
        _ = attachment.name
    with pytest.raises(Exception):
        _ = attachment.quantity
    with pytest.raises(Exception):
        _ = attachment.can_take 