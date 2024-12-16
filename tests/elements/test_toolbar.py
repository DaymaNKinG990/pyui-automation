import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.toolbar import Toolbar, ToolbarButton


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session


@pytest.fixture
def mock_button_element():
    element = MagicMock()
    element.get_property.side_effect = lambda prop: {
        'text': 'Button 1',
        'tooltip': 'Tooltip text',
        'enabled': True,
        'pressed': False
    }.get(prop)
    return element


@pytest.fixture
def mock_toolbar_element():
    element = MagicMock()
    
    button1 = MagicMock()
    button2 = MagicMock()
    element.find_elements.return_value = [button1, button2]
    
    return element


@pytest.fixture
def toolbar_button(mock_button_element, mock_session):
    return ToolbarButton(mock_button_element, mock_session)


@pytest.fixture
def toolbar(mock_toolbar_element, mock_session):
    return Toolbar(mock_toolbar_element, mock_session)


def test_button_text(toolbar_button, mock_button_element):
    """Test getting button text."""
    assert toolbar_button.text == 'Button 1'
    mock_button_element.get_property.assert_called_with('text')


def test_button_tooltip(toolbar_button, mock_button_element):
    """Test getting button tooltip."""
    assert toolbar_button.tooltip == 'Tooltip text'
    mock_button_element.get_property.assert_called_with('tooltip')


def test_button_is_enabled(toolbar_button, mock_button_element):
    """Test checking if button is enabled."""
    assert toolbar_button.is_enabled
    mock_button_element.get_property.assert_called_with('enabled')


def test_button_is_pressed(toolbar_button, mock_button_element):
    """Test checking if button is pressed."""
    assert not toolbar_button.is_pressed
    mock_button_element.get_property.assert_called_with('pressed')


def test_button_click_when_enabled(toolbar_button):
    """Test clicking enabled button."""
    toolbar_button.click()
    toolbar_button._element.click.assert_called_once()


def test_button_click_when_disabled(toolbar_button, mock_button_element):
    """Test clicking disabled button."""
    mock_button_element.get_property.side_effect = lambda prop: {
        'text': 'Button 1',
        'tooltip': 'Tooltip text',
        'enabled': False,
        'pressed': False
    }.get(prop)
    
    toolbar_button.click()
    toolbar_button._element.click.assert_not_called()


def test_button_wait_until_enabled(toolbar_button, mock_session):
    """Test waiting until button is enabled."""
    assert toolbar_button.wait_until_enabled()
    mock_session.wait_for_condition.assert_called_once()


def test_toolbar_buttons(toolbar, mock_toolbar_element):
    """Test getting all buttons."""
    buttons = toolbar.buttons
    assert len(buttons) == 2
    assert all(isinstance(button, ToolbarButton) for button in buttons)
    mock_toolbar_element.find_elements.assert_called_with(by='type', value='button')


def test_toolbar_get_button(toolbar, mock_toolbar_element):
    """Test getting button by text."""
    mock_button = MagicMock()
    mock_button.text = 'Button 1'
    mock_toolbar_element.find_elements.return_value = [mock_button]
    
    button = toolbar.get_button('Button 1')
    assert isinstance(button, ToolbarButton)


def test_toolbar_get_button_not_found(toolbar, mock_toolbar_element):
    """Test getting button by text when not found."""
    mock_button = MagicMock()
    mock_button.text = 'Button 1'
    mock_toolbar_element.find_elements.return_value = [mock_button]
    
    assert toolbar.get_button('Nonexistent') is None
