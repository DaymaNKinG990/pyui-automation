import pytest
from unittest.mock import MagicMock
from pyui_automation.elements.notification import Notification


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session


@pytest.fixture
def mock_notification_element():
    element = MagicMock()
    
    # Set up default property values
    element.get_property.side_effect = lambda prop: {
        'text': 'Operation completed successfully',
        'type': 'success',
        'visible': True,
        'auto_close': True,
        'duration': 5.0
    }.get(prop)
    
    # Set up mock action buttons
    mock_button1 = MagicMock()
    mock_button1.get_property.return_value = 'Undo'
    
    mock_button2 = MagicMock()
    mock_button2.get_property.return_value = 'Dismiss'
    
    # find_elements_by_widget_type для кнопок
    element.find_elements_by_widget_type = MagicMock(return_value=[mock_button1, mock_button2])
    # find_element_by_text для кнопок
    def find_element_by_text_side_effect(text):
        if text == 'Close':
            close_btn = MagicMock()
            close_btn.click = MagicMock()
            return close_btn
        elif text == 'Undo':
            return mock_button1
        elif text == 'Dismiss':
            return mock_button2
        return None
    element.find_element_by_text = MagicMock(side_effect=find_element_by_text_side_effect)
    
    return element


@pytest.fixture
def notification(mock_notification_element, mock_session):
    return Notification(mock_notification_element, mock_session)


def test_notification_init(notification, mock_notification_element, mock_session):
    """Test notification initialization."""
    assert notification._element == mock_notification_element
    assert notification._session == mock_session


def test_notification_text(notification, mock_notification_element):
    """Test getting notification text."""
    assert notification.text == 'Operation completed successfully'
    mock_notification_element.get_property.assert_called_with('text')


def test_notification_type(notification, mock_notification_element):
    """Test getting notification type."""
    assert notification.type == 'success'
    mock_notification_element.get_property.assert_called_with('type')


def test_notification_is_visible(notification, mock_notification_element):
    """Test checking if notification is visible."""
    assert notification.is_visible
    mock_notification_element.get_property.assert_called_with('visible')


def test_notification_auto_close(notification, mock_notification_element):
    """Test checking if notification auto-closes."""
    assert notification.auto_close
    mock_notification_element.get_property.assert_called_with('auto_close')


def test_notification_duration_with_auto_close(notification, mock_notification_element):
    """Test getting duration when auto-close is enabled."""
    assert notification.duration == 5.0
    mock_notification_element.get_property.assert_called_with('duration')


def test_notification_duration_without_auto_close(notification, mock_notification_element):
    """Test getting duration when auto-close is disabled."""
    mock_notification_element.get_property.side_effect = lambda prop: {
        'text': 'Operation completed successfully',
        'type': 'success',
        'visible': True,
        'auto_close': False,
        'duration': 5.0
    }.get(prop)
    
    assert notification.duration is None


def test_notification_close(notification, mock_notification_element):
    """Test closing notification manually."""
    close_btn = MagicMock()
    close_btn.click = MagicMock()
    def side_effect(text):
        if text == 'Close':
            return close_btn
        return None
    mock_notification_element.find_element_by_text.side_effect = side_effect
    notification.close()
    mock_notification_element.find_element_by_text.assert_called_with('Close')
    close_btn.click.assert_called_once()


def test_notification_get_action_buttons(notification, mock_notification_element):
    """Test getting action button texts."""
    buttons = notification.get_action_buttons()
    assert buttons == ['Undo', 'Dismiss']
    mock_notification_element.find_elements_by_widget_type.assert_called_with('button')


def test_notification_click_action_existing(notification, mock_notification_element):
    """Test clicking existing action button."""
    action_btn = MagicMock()
    action_btn.click = MagicMock()
    def side_effect(text):
        if text == 'Undo':
            return action_btn
        return None
    mock_notification_element.find_element_by_text.side_effect = side_effect
    notification.click_action('Undo')
    mock_notification_element.find_element_by_text.assert_called_with('Undo')
    action_btn.click.assert_called_once()


def test_notification_click_action_nonexistent(notification, mock_notification_element):
    """Test clicking nonexistent action button."""
    mock_notification_element.find_element_by_text.return_value = None
    with pytest.raises(ValueError, match="Action button 'Nonexistent' not found"):
        notification.click_action('Nonexistent')


class NotificationMock(Notification):
    def __init__(self, native_element, session, visible=True, text='Operation completed successfully'):
        super().__init__(native_element, session)
        self._mock_visible = visible
        self._mock_text = text
    @property
    def is_visible(self):
        return self._mock_visible
    @property
    def text(self):
        return self._mock_text

def test_notification_wait_until_visible(mock_notification_element, mock_session):
    """Test waiting for notification to become visible (без patch.object, через double)."""
    notification = NotificationMock(mock_notification_element, mock_session, visible=True)
    assert notification.wait_until_visible(timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    notification._mock_visible = True
    assert condition_func()
    notification._mock_visible = False
    assert not condition_func()

def test_notification_wait_until_hidden(mock_notification_element, mock_session):
    """Test waiting for notification to become hidden (без patch.object, через double)."""
    notification = NotificationMock(mock_notification_element, mock_session, visible=False)
    assert notification.wait_until_hidden(timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    notification._mock_visible = False
    assert condition_func()
    notification._mock_visible = True
    assert not condition_func()

def test_notification_wait_until_text(mock_notification_element, mock_session):
    """Test waiting for notification text to match (без patch.object, через double)."""
    expected_text = 'New notification text'
    notification = NotificationMock(mock_notification_element, mock_session, text=expected_text)
    assert notification.wait_until_text(expected_text, timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    notification._mock_text = expected_text
    assert condition_func()
    notification._mock_text = 'Different text'
    assert not condition_func()
