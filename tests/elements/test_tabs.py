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


def test_tab_select_already_selected(tab_item, mock_tab_element):
    mock_tab_element.get_property.side_effect = lambda prop: {
        'text': 'Tab 1',
        'selected': True,
        'enabled': True
    }[prop]
    tab_item.select()
    tab_item._element.click.assert_not_called()


class TabItemMock(TabItem):
    def __init__(self, native_element, session, selected=False):
        super().__init__(native_element, session)
        self._mock_selected = selected
    @property
    def is_selected(self):
        return self._mock_selected

def test_tab_wait_until_selected(mock_tab_element, mock_session):
    """Test waiting until tab is selected (без patch.object, через double)."""
    tab_item = TabItemMock(mock_tab_element, mock_session, selected=True)
    assert tab_item.wait_until_selected()
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    tab_item._mock_selected = True
    assert condition_func()
    tab_item._mock_selected = False
    assert not condition_func()


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


def test_tabcontrol_get_tab(tab_control, mock_tabcontrol_element, mock_session):
    """Test getting tab by text."""
    from pyui_automation.elements.tabs import TabItem
    mock_tab_element = MagicMock()
    mock_tab_element.get_property.side_effect = lambda prop: {'text': 'Tab 1', 'selected': False, 'enabled': True}.get(prop)
    # Возвращаем список mock-элементов, чтобы tabs создал TabItem
    mock_tabcontrol_element.find_elements.return_value = [mock_tab_element]
    tab_control = tab_control  # уже создан через фикстуру
    tab = tab_control.get_tab('Tab 1')
    assert isinstance(tab, TabItem)


def test_tabcontrol_get_tab_not_found(tab_control, mock_tabcontrol_element):
    """Test getting tab by text when not found."""
    mock_tab = MagicMock()
    mock_tab.text = 'Tab 1'
    mock_tabcontrol_element.find_elements.return_value = [mock_tab]
    
    assert tab_control.get_tab('Nonexistent') is None


def test_tabcontrol_select_tab_found(tab_control, mock_tabcontrol_element):
    tab = MagicMock()
    tab.select = MagicMock()
    tab.text = "Tab 1"
    with patch.object(type(tab_control), 'get_tab', return_value=tab):
        tab_control.select_tab("Tab 1")
        tab.select.assert_called_once()

def test_tabcontrol_select_tab_not_found(tab_control):
    tab_control.get_tab = MagicMock(return_value=None)
    with pytest.raises(ValueError):
        tab_control.select_tab("Nonexistent")

def test_wait_until_tab_selected_success(tab_control, mock_session):
    tab = MagicMock()
    tab.is_selected = True
    tab_control.get_tab = MagicMock(return_value=tab)
    mock_session.wait_for_condition = MagicMock(return_value=True)
    result = tab_control.wait_until_tab_selected("Tab 1", timeout=1)
    assert result is True

def test_wait_until_tab_selected_not_found(tab_control, mock_session):
    tab_control.get_tab = MagicMock(return_value=None)
    mock_session.wait_for_condition = MagicMock(return_value=False)
    result = tab_control.wait_until_tab_selected("Tab 1", timeout=1)
    assert result is False

def test_wait_until_tab_selected_not_selected(tab_control, mock_session):
    tab = MagicMock()
    tab.is_selected = False
    tab_control.get_tab = MagicMock(return_value=tab)
    mock_session.wait_for_condition = MagicMock(return_value=False)
    result = tab_control.wait_until_tab_selected("Tab 1", timeout=1)
    assert result is False
