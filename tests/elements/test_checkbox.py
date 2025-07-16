import pytest
from unittest.mock import MagicMock
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

class CheckBoxMock(CheckBox):
    def __init__(self, native_element, session, checked=False):
        super().__init__(native_element, session)
        self._mock_checked = checked
    @property
    def is_checked(self):
        return self._mock_checked

class TestCheckBoxProperty:
    def setup_method(self):
        self.checkbox = CheckBox(MagicMock(), MagicMock())

    def test_is_checked_setter(self):
        self.checkbox._element.get_property.return_value = False
        self.checkbox.click = MagicMock()
        self.checkbox.is_checked = True
        self.checkbox.click.assert_called_once()
        # Если уже True, click не вызывается
        self.checkbox.click.reset_mock()
        self.checkbox._element.get_property.return_value = True
        self.checkbox.is_checked = True
        self.checkbox.click.assert_not_called()

    def test_is_checked_deleter(self):
        try:
            del self.checkbox.is_checked
        except AttributeError as e:
            assert "Cannot delete is_checked property" in str(e)

def test_init(checkbox, mock_native_element, mock_session):
    """Test checkbox initialization."""
    assert checkbox._element == mock_native_element
    assert checkbox._session == mock_session

def test_is_checked(checkbox, mock_native_element):
    """Test checking if checkbox is checked."""
    assert not checkbox.is_checked
    mock_native_element.get_property.assert_called_with('checked')

def test_check_when_unchecked(mock_native_element, mock_session):
    """Test checking an unchecked checkbox (без patch.object, через double)."""
    checkbox = CheckBoxMock(mock_native_element, mock_session, checked=False)
    checkbox.check()
    mock_native_element.click.assert_called_once()

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

def test_wait_until_checked(mock_native_element, mock_session):
    """Test waiting for checkbox to become checked (без patch.object, через double)."""
    checkbox = CheckBoxMock(mock_native_element, mock_session, checked=True)
    assert checkbox.wait_until_checked(timeout=5)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    checkbox._mock_checked = True
    assert condition_func()
    checkbox._mock_checked = False
    assert not condition_func()

def test_wait_until_unchecked(mock_native_element, mock_session):
    """Test waiting for checkbox to become unchecked (без patch.object, через double)."""
    checkbox = CheckBoxMock(mock_native_element, mock_session, checked=False)
    assert checkbox.wait_until_unchecked(timeout=5)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    checkbox._mock_checked = True
    assert not condition_func()
    checkbox._mock_checked = False
    assert condition_func()
