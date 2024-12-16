import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.checkbox import CheckBox


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session

@pytest.fixture
def mock_native_element():
    element = MagicMock()
    element.get_property.return_value = False  # Default to unchecked
    return element

@pytest.fixture
def checkbox(mock_native_element, mock_session):
    return CheckBox(mock_native_element, mock_session)

def test_init(checkbox, mock_native_element, mock_session):
    """Test checkbox initialization."""
    assert checkbox._element == mock_native_element
    assert checkbox._session == mock_session

def test_is_checked(checkbox, mock_native_element):
    """Test checking if checkbox is checked."""
    assert not checkbox.is_checked
    mock_native_element.get_property.assert_called_with('checked')

def test_check_when_unchecked(checkbox):
    """Test checking an unchecked checkbox."""
    with patch.object(checkbox, 'is_checked', False):
        checkbox.check()
        checkbox._element.click.assert_called_once()

def test_check_when_already_checked(checkbox, mock_native_element):
    """Test checking an already checked checkbox."""
    mock_native_element.get_property.return_value = True
    checkbox.check()
    checkbox._element.click.assert_not_called()

def test_uncheck_when_checked(checkbox, mock_native_element):
    """Test unchecking a checked checkbox."""
    mock_native_element.get_property.return_value = True
    checkbox.uncheck()
    checkbox._element.click.assert_called_once()

def test_uncheck_when_already_unchecked(checkbox, mock_native_element):
    """Test unchecking an already unchecked checkbox."""
    mock_native_element.get_property.return_value = False
    checkbox.uncheck()
    checkbox._element.click.assert_not_called()

def test_toggle(checkbox):
    """Test toggling checkbox state."""
    checkbox.toggle()
    checkbox._element.click.assert_called_once()

def test_wait_until_checked(checkbox, mock_session):
    """Test waiting for checkbox to become checked."""
    assert checkbox.wait_until_checked(timeout=5)
    mock_session.wait_for_condition.assert_called_once()
    
    # Verify the condition function
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    with patch.object(checkbox, 'is_checked', True):
        assert condition_func()
    with patch.object(checkbox, 'is_checked', False):
        assert not condition_func()

def test_wait_until_unchecked(checkbox, mock_session):
    """Test waiting for checkbox to become unchecked."""
    assert checkbox.wait_until_unchecked(timeout=5)
    mock_session.wait_for_condition.assert_called_once()
    
    # Verify the condition function
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    with patch.object(checkbox, 'is_checked', True):
        assert not condition_func()
    with patch.object(checkbox, 'is_checked', False):
        assert condition_func()
