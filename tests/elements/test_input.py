import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.input import Input


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.keyboard = MagicMock()
    session.waits = MagicMock()
    session.waits.wait_until = MagicMock(return_value=True)
    return session

@pytest.fixture
def mock_native_element():
    element = MagicMock()
    element.get_property.return_value = 'current value'
    return element

@pytest.fixture
def input_element(mock_native_element, mock_session):
    return Input(mock_native_element, mock_session)

def test_init(input_element, mock_native_element, mock_session):
    """Test input initialization."""
    assert input_element._element == mock_native_element
    assert input_element._session == mock_session

def test_get_value(input_element, mock_native_element):
    """Test getting input value."""
    assert input_element.value == 'current value'
    mock_native_element.get_property.assert_called_with('value')

def test_set_value(input_element):
    """Test setting input value."""
    input_element.value = 'new value'
    input_element._element.clear.assert_called_once()
    input_element._element.send_keys.assert_called_once_with('new value')

def test_clear(input_element):
    """Test clearing input value."""
    input_element.clear()
    input_element._element.clear.assert_called_once()

def test_append(input_element):
    """Test appending text to input."""
    input_element.append('additional text')
    input_element._element.send_keys.assert_called_once_with('additional text')

def test_focus(input_element):
    """Test setting focus to input."""
    input_element.focus()
    input_element._element.click.assert_called_once()

def test_select_all(input_element, mock_session):
    """Test selecting all text in input."""
    input_element.select_all()
    input_element._element.click.assert_called_once()
    mock_session.keyboard.select_all.assert_called_once()

def test_copy(input_element, mock_session):
    """Test copying selected text."""
    input_element.copy()
    mock_session.keyboard.copy.assert_called_once()

def test_paste(input_element, mock_session):
    """Test pasting text from clipboard."""
    input_element.paste()
    mock_session.keyboard.paste.assert_called_once()

def test_wait_until_value_is_with_default_timeout(input_element, mock_session):
    """Test waiting for specific value with default timeout."""
    assert input_element.wait_until_value_is('expected value')
    
    mock_session.waits.wait_until.assert_called_once()
    args = mock_session.waits.wait_until.call_args
    
    # Verify timeout
    assert args[1]['timeout'] == 10.0
    
    # Verify condition function
    condition_func = args[0][0]
    with patch.object(input_element, 'value', 'expected value'):
        assert condition_func()
    with patch.object(input_element, 'value', 'different value'):
        assert not condition_func()

def test_wait_until_value_is_with_custom_timeout(input_element, mock_session):
    """Test waiting for specific value with custom timeout."""
    assert input_element.wait_until_value_is('expected value', timeout=5.0)
    
    mock_session.waits.wait_until.assert_called_once()
    args = mock_session.waits.wait_until.call_args
    
    # Verify custom timeout
    assert args[1]['timeout'] == 5.0
