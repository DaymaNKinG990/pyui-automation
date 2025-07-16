import pytest
from unittest.mock import MagicMock
from pyui_automation.elements.radio import RadioButton


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session


@pytest.fixture
def mock_radio_element():
    element = MagicMock()
    
    # Set up default property values
    element.get_property.side_effect = lambda prop: {
        'selected': False,
        'group_name': 'options'
    }.get(prop)
    
    return element


@pytest.fixture
def mock_radio_group():
    # Create mock radio buttons for the group
    mock_radio1 = MagicMock()
    mock_radio1.get_property.side_effect = lambda prop: {
        'selected': True,
        'group_name': 'options'
    }.get(prop)
    
    mock_radio2 = MagicMock()
    mock_radio2.get_property.side_effect = lambda prop: {
        'selected': False,
        'group_name': 'options'
    }.get(prop)
    
    mock_radio3 = MagicMock()
    mock_radio3.get_property.side_effect = lambda prop: {
        'selected': False,
        'group_name': 'options'
    }.get(prop)
    
    return [mock_radio1, mock_radio2, mock_radio3]


@pytest.fixture
def radio_button(mock_radio_element, mock_session):
    radio = RadioButton(mock_radio_element, mock_session)
    
    # Set up find_elements behavior for group buttons
    mock_radio_element.find_elements.side_effect = lambda by, value: (
        mock_radio_group() if by == 'group' and value == 'options' else []
    )
    
    return radio


def test_radio_init(radio_button, mock_radio_element, mock_session):
    """Test radio button initialization."""
    assert radio_button._element == mock_radio_element
    assert radio_button._session == mock_session


def test_radio_is_selected(radio_button, mock_radio_element):
    """Test checking if radio button is selected."""
    assert not radio_button.is_selected
    mock_radio_element.get_property.assert_called_with('selected')


def test_radio_is_selected_when_true(radio_button, mock_radio_element):
    """Test checking if radio button is selected when it is."""
    mock_radio_element.get_property.side_effect = lambda prop: {
        'selected': True,
        'group_name': 'options'
    }.get(prop)
    
    assert radio_button.is_selected
    mock_radio_element.get_property.assert_called_with('selected')


def test_radio_group_name(radio_button, mock_radio_element):
    """Test getting radio button group name."""
    assert radio_button.group_name == 'options'
    mock_radio_element.get_property.assert_called_with('group_name')


def test_radio_select_when_not_selected(radio_button):
    """Test selecting unselected radio button."""
    radio_button.select()
    radio_button._element.click.assert_called_once()


def test_radio_select_when_already_selected(radio_button, mock_radio_element):
    """Test selecting already selected radio button."""
    mock_radio_element.get_property.side_effect = lambda prop: {
        'selected': True,
        'group_name': 'options'
    }.get(prop)
    
    radio_button.select()
    radio_button._element.click.assert_not_called()


def test_radio_get_group_buttons(radio_button, mock_radio_element):
    """Test getting all radio buttons in the same group."""
    # Создаём mock-объекты группы
    mock_radio1 = MagicMock()
    mock_radio1.get_property.side_effect = lambda prop: {'selected': True, 'group_name': 'options'}.get(prop)
    mock_radio2 = MagicMock()
    mock_radio2.get_property.side_effect = lambda prop: {'selected': False, 'group_name': 'options'}.get(prop)
    mock_radio3 = MagicMock()
    mock_radio3.get_property.side_effect = lambda prop: {'selected': False, 'group_name': 'options'}.get(prop)
    mock_radio_element.find_elements.side_effect = lambda by, value: [mock_radio1, mock_radio2, mock_radio3] if by == 'group' and value == 'options' else []
    group_buttons = radio_button.get_group_buttons()
    assert len(group_buttons) == 3
    assert all(isinstance(btn, RadioButton) for btn in group_buttons)
    assert group_buttons[0].is_selected
    assert not group_buttons[1].is_selected
    assert not group_buttons[2].is_selected
    mock_radio_element.find_elements.assert_called_once_with(by='group', value='options')


class RadioButtonMock(RadioButton):
    def __init__(self, native_element, session, selected=False):
        super().__init__(native_element, session)
        self._mock_selected = selected
    @property
    def is_selected(self):
        return self._mock_selected

def test_radio_wait_until_selected(mock_radio_element, mock_session):
    """Test waiting for radio button to become selected (без patch.object, через double)."""
    radio_button = RadioButtonMock(mock_radio_element, mock_session, selected=True)
    assert radio_button.wait_until_selected(timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    radio_button._mock_selected = True
    assert condition_func()
    radio_button._mock_selected = False
    assert not condition_func()

def test_radio_wait_until_not_selected(mock_radio_element, mock_session):
    """Test waiting for radio button to become not selected (без patch.object, через double)."""
    radio_button = RadioButtonMock(mock_radio_element, mock_session, selected=False)
    assert radio_button.wait_until_not_selected(timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    radio_button._mock_selected = False
    assert condition_func()
    radio_button._mock_selected = True
    assert not condition_func()


def test_radio_group_interaction(radio_button, mock_radio_element):
    """Test interaction between radio buttons in a group."""
    # Создаём mock-объекты группы
    mock_radio1 = MagicMock()
    mock_radio1.get_property.side_effect = lambda prop: {'selected': True, 'group_name': 'options'}.get(prop)
    mock_radio2 = MagicMock()
    mock_radio2.get_property.side_effect = lambda prop: {'selected': False, 'group_name': 'options'}.get(prop)
    mock_radio3 = MagicMock()
    mock_radio3.get_property.side_effect = lambda prop: {'selected': False, 'group_name': 'options'}.get(prop)
    mock_radio_element.find_elements.side_effect = lambda by, value: [mock_radio1, mock_radio2, mock_radio3] if by == 'group' and value == 'options' else []
    group_buttons = radio_button.get_group_buttons()
    # Initially, first button is selected
    assert group_buttons[0].is_selected
    assert not group_buttons[1].is_selected
    assert not group_buttons[2].is_selected
    # Verify all buttons are in the same group
    assert all(btn.group_name == 'options' for btn in group_buttons)
    # Verify find_elements was called correctly
    mock_radio_element.find_elements.assert_called_with(by='group', value='options')
