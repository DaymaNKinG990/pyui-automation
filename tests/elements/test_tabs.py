import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.tabs import TabControl, TabItem


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session


@pytest.fixture
def mock_tab_element():
    element = MagicMock()
    element.get_property.side_effect = lambda prop: {
        'text': 'Tab 1',
        'selected': False,
        'enabled': True
    }.get(prop)
    return element


@pytest.fixture
def mock_tabcontrol_element():
    element = MagicMock()
    
    tab1 = MagicMock()
    tab2 = MagicMock()
    element.find_elements.return_value = [tab1, tab2]
    element.find_element.return_value = tab1
    
    return element


@pytest.fixture
def tab_item(mock_tab_element, mock_session):
    return TabItem(mock_tab_element, mock_session)


@pytest.fixture
def tab_control(mock_tabcontrol_element, mock_session):
    return TabControl(mock_tabcontrol_element, mock_session)


def test_tab_text(tab_item, mock_tab_element):
    """Test getting tab text."""
    assert tab_item.text == 'Tab 1'
    mock_tab_element.get_property.assert_called_with('text')


def test_tab_is_selected(tab_item, mock_tab_element):
    """Test checking if tab is selected."""
    assert not tab_item.is_selected
    mock_tab_element.get_property.assert_called_with('selected')


def test_tab_is_enabled(tab_item, mock_tab_element):
    """Test checking if tab is enabled."""
    assert tab_item.is_enabled
    mock_tab_element.get_property.assert_called_with('enabled')


def test_tab_select_when_enabled(tab_item):
    """Test selecting enabled tab."""
    tab_item.select()
    tab_item._element.click.assert_called_once()


def test_tab_select_when_disabled(tab_item, mock_tab_element):
    """Test selecting disabled tab."""
    mock_tab_element.get_property.side_effect = lambda prop: {
        'text': 'Tab 1',
        'selected': False,
        'enabled': False
    }.get(prop)
    
    tab_item.select()
    tab_item._element.click.assert_not_called()


def test_tab_wait_until_selected(tab_item, mock_session):
    """Test waiting until tab is selected."""
    assert tab_item.wait_until_selected()
    mock_session.wait_for_condition.assert_called_once()


def test_tabcontrol_tabs(tab_control, mock_tabcontrol_element):
    """Test getting all tabs."""
    tabs = tab_control.tabs
    assert len(tabs) == 2
    assert all(isinstance(tab, TabItem) for tab in tabs)
    mock_tabcontrol_element.find_elements.assert_called_with(by='type', value='tabitem')


def test_tabcontrol_selected_tab(tab_control, mock_tabcontrol_element):
    """Test getting selected tab."""
    tab = tab_control.selected_tab
    assert isinstance(tab, TabItem)
    mock_tabcontrol_element.find_element.assert_called_with(by='state', value='selected')


def test_tabcontrol_selected_tab_none(tab_control, mock_tabcontrol_element):
    """Test getting selected tab when none selected."""
    mock_tabcontrol_element.find_element.return_value = None
    assert tab_control.selected_tab is None


def test_tabcontrol_get_tab(tab_control, mock_tabcontrol_element):
    """Test getting tab by text."""
    mock_tab = MagicMock()
    mock_tab.text = 'Tab 1'
    mock_tabcontrol_element.find_elements.return_value = [mock_tab]
    
    tab = tab_control.get_tab('Tab 1')
    assert isinstance(tab, TabItem)


def test_tabcontrol_get_tab_not_found(tab_control, mock_tabcontrol_element):
    """Test getting tab by text when not found."""
    mock_tab = MagicMock()
    mock_tab.text = 'Tab 1'
    mock_tabcontrol_element.find_elements.return_value = [mock_tab]
    
    assert tab_control.get_tab('Nonexistent') is None
