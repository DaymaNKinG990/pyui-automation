import pytest
from unittest.mock import MagicMock
from pyui_automation.elements.dialog import Dialog


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session

@pytest.fixture
def mock_dialog_element():
    element = MagicMock()
    # Set up default property values
    element.get_property.side_effect = lambda prop: {
        'title': 'Test Dialog',
        'modal': True,
        'visible': True,
    }.get(prop)
    
    # Mock buttons
    mock_ok = MagicMock()
    mock_ok.get_property.side_effect = lambda prop: {
        'text': 'OK',
        'enabled': True
    }.get(prop)
    
    mock_cancel = MagicMock()
    mock_cancel.get_property.side_effect = lambda prop: {
        'text': 'Cancel',
        'enabled': True
    }.get(prop)
    
    # Mock content and message
    mock_content = MagicMock()
    mock_content.get_property.return_value = "Dialog content"
    
    mock_message = MagicMock()
    mock_message.get_property.return_value = "Dialog message"
    
    # Set up find_elements and find_element behavior
    element.find_elements.return_value = [mock_ok, mock_cancel]
    element.find_element.side_effect = lambda by, value: {
        'OK': mock_ok,
        'Cancel': mock_cancel,
        'Close': mock_ok,
        'content': mock_content,
        'message': mock_message
    }.get(value)
    
    return element

@pytest.fixture
def dialog(mock_dialog_element, mock_session):
    return Dialog(mock_dialog_element, mock_session)

def test_init(dialog, mock_dialog_element, mock_session):
    """Test dialog initialization."""
    assert dialog._element == mock_dialog_element
    assert dialog._session == mock_session

def test_title(dialog, mock_dialog_element):
    """Test getting dialog title."""
    assert dialog.title == 'Test Dialog'
    mock_dialog_element.get_property.assert_called_with('title')

def test_is_modal(dialog, mock_dialog_element):
    """Test checking if dialog is modal."""
    assert dialog.is_modal
    mock_dialog_element.get_property.assert_called_with('modal')

def test_is_visible(dialog, mock_dialog_element):
    """Test checking if dialog is visible."""
    assert dialog.is_visible
    mock_dialog_element.get_property.assert_called_with('visible')

def test_buttons(dialog, mock_dialog_element):
    """Test getting button texts."""
    assert dialog.buttons == ['OK', 'Cancel']
    mock_dialog_element.find_elements.assert_called_with(by="type", value="button")

def test_click_button_found(dialog, mock_dialog_element):
    """Test clicking existing button."""
    dialog.click_button('OK')
    mock_dialog_element.find_element.assert_called_with(by="name", value="OK")

def test_click_button_not_found(dialog):
    """Test clicking nonexistent button."""
    with pytest.raises(ValueError, match="Button 'NonexistentButton' not found"):
        dialog.click_button('NonexistentButton')

def test_close(dialog, mock_dialog_element):
    """Test closing dialog."""
    mock_close = MagicMock()
    mock_dialog_element.find_element_by_object_name = MagicMock(return_value=mock_close)
    dialog.close()
    mock_close.click.assert_called_once()


def test_get_content_text(dialog, mock_dialog_element):
    """Test getting dialog content text."""
    mock_content = MagicMock()
    mock_content.get_property.return_value = "Dialog content"
    mock_dialog_element.find_element_by_widget_type = lambda *a, **kw: mock_content
    assert dialog.get_content_text() == "Dialog content"


def test_get_content_text_none(dialog, mock_dialog_element):
    """Test getting content text when none exists."""
    mock_dialog_element.find_element_by_widget_type = lambda *a, **kw: None
    assert dialog.get_content_text() == ""


def test_get_message(dialog, mock_dialog_element):
    """Test getting dialog message text."""
    mock_message = MagicMock()
    mock_message.get_property.return_value = "Dialog message"
    mock_dialog_element.find_element_by_widget_type = lambda *a, **kw: mock_message
    assert dialog.get_message() == "Dialog message"


def test_get_message_none(dialog, mock_dialog_element):
    """Test getting message when none exists."""
    mock_dialog_element.find_element_by_widget_type = lambda *a, **kw: None
    assert dialog.get_message() is None

class DialogMock(Dialog):
    def __init__(self, native_element, session, visible=True):
        super().__init__(native_element, session)
        self._mock_visible = visible
    @property
    def is_visible(self):
        return self._mock_visible

def test_wait_until_open(mock_dialog_element, mock_session):
    """Test waiting for dialog to open (без patch.object, через double)."""
    dialog = DialogMock(mock_dialog_element, mock_session, visible=True)
    assert dialog.wait_until_open(timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    dialog._mock_visible = True
    assert condition_func()
    dialog._mock_visible = False
    assert not condition_func()

def test_wait_until_closed(mock_dialog_element, mock_session):
    """Test waiting for dialog to close (без patch.object, через double)."""
    dialog = DialogMock(mock_dialog_element, mock_session, visible=False)
    assert dialog.wait_until_closed(timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    dialog._mock_visible = True
    assert not condition_func()
    dialog._mock_visible = False
    assert condition_func()

def test_wait_until_button_enabled(dialog, mock_session):
    """Test waiting for button to become enabled."""
    assert dialog.wait_until_button_enabled('OK', timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    assert condition_func()  # Should be True since button is enabled

def test_wait_until_button_enabled_not_found(dialog, mock_dialog_element):
    """Test waiting for nonexistent button to become enabled."""
    mock_dialog_element.find_element.side_effect = lambda by, value: None
    assert dialog.wait_until_button_enabled('NonexistentButton', timeout=5.0)
    
    condition_func = dialog._session.wait_for_condition.call_args[0][0]
    assert not condition_func()  # Should be False since button doesn't exist
