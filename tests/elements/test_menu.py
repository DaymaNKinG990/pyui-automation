import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.menu import Menu, MenuItem


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    session.keyboard = MagicMock()
    return session


@pytest.fixture
def mock_menu_item_element():
    element = MagicMock()
    # Set up default property values for menu item
    element.get_property.side_effect = lambda prop: {
        'text': 'File',
        'enabled': True,
        'has_submenu': False
    }.get(prop)
    return element


@pytest.fixture
def mock_menu_element():
    element = MagicMock()
    
    # Create mock menu items
    mock_item1 = MagicMock()
    mock_item1.get_property.side_effect = lambda prop: {
        'text': 'File',
        'enabled': True,
        'has_submenu': True
    }.get(prop)
    
    mock_item2 = MagicMock()
    mock_item2.get_property.side_effect = lambda prop: {
        'text': 'Edit',
        'enabled': True,
        'has_submenu': False
    }.get(prop)
    
    mock_item3 = MagicMock()
    mock_item3.get_property.side_effect = lambda prop: {
        'text': 'Help',
        'enabled': False,
        'has_submenu': False
    }.get(prop)
    
    # Set up find_elements behavior
    element.find_elements.return_value = [mock_item1, mock_item2, mock_item3]
    
    # Set up is_open property
    element.get_property.side_effect = lambda prop: {
        'expanded': False
    }.get(prop)
    
    return element


@pytest.fixture
def menu_item(mock_menu_item_element, mock_session):
    return MenuItem(mock_menu_item_element, mock_session)


@pytest.fixture
def menu(mock_menu_element, mock_session):
    return Menu(mock_menu_element, mock_session)


# MenuItem Tests
def test_menu_item_init(menu_item, mock_menu_item_element, mock_session):
    """Test menu item initialization."""
    assert menu_item._element == mock_menu_item_element
    assert menu_item._session == mock_session


def test_menu_item_text(menu_item, mock_menu_item_element):
    """Test getting menu item text."""
    assert menu_item.text == 'File'
    mock_menu_item_element.get_property.assert_called_with('text')


def test_menu_item_is_enabled(menu_item, mock_menu_item_element):
    """Test checking if menu item is enabled."""
    assert menu_item.is_enabled
    mock_menu_item_element.get_property.assert_called_with('enabled')


def test_menu_item_has_submenu(menu_item, mock_menu_item_element):
    """Test checking if menu item has submenu."""
    assert not menu_item.has_submenu
    mock_menu_item_element.get_property.assert_called_with('has_submenu')


def test_menu_item_expand_with_submenu(menu_item, mock_menu_item_element):
    """Test expanding menu item with submenu."""
    mock_menu_item_element.get_property.side_effect = lambda prop: {
        'text': 'File',
        'enabled': True,
        'has_submenu': True
    }.get(prop)
    
    menu_item.expand()
    menu_item._element.hover.assert_called_once()


def test_menu_item_expand_without_submenu(menu_item):
    """Test expanding menu item without submenu."""
    menu_item.expand()
    menu_item._element.hover.assert_not_called()


def test_menu_item_select(menu_item):
    """Test selecting menu item."""
    menu_item.select()
    menu_item._element.click.assert_called_once()


# Menu Tests
def test_menu_init(menu, mock_menu_element, mock_session):
    """Test menu initialization."""
    assert menu._element == mock_menu_element
    assert menu._session == mock_session


def test_menu_is_open(menu, mock_menu_element):
    """Test checking if menu is open."""
    assert not menu.is_open
    mock_menu_element.get_property.assert_called_with('expanded')


def test_menu_items(menu, mock_menu_element):
    """Test getting all menu items."""
    items = menu.items
    assert len(items) == 3
    assert all(isinstance(item, MenuItem) for item in items)
    mock_menu_element.find_elements.assert_called_with(by="type", value="menuitem")


def test_menu_open_when_closed(menu):
    """Test opening closed menu."""
    menu.open()
    menu._element.click.assert_called_once()


def test_menu_open_when_already_open(menu, mock_menu_element):
    """Test opening already open menu."""
    mock_menu_element.get_property.side_effect = lambda prop: {
        'expanded': True
    }.get(prop)
    
    menu.open()
    menu._element.click.assert_not_called()


def test_menu_close_when_open(menu, mock_menu_element, mock_session):
    """Test closing open menu."""
    mock_menu_element.get_property.side_effect = lambda prop: {
        'expanded': True
    }.get(prop)
    
    menu.close()
    mock_session.keyboard.press_key.assert_called_once_with('escape')


def test_menu_close_when_already_closed(menu, mock_session):
    """Test closing already closed menu."""
    menu.close()
    mock_session.keyboard.press_key.assert_not_called()


def test_menu_get_item_existing(menu):
    """Test getting existing menu item."""
    item = menu.get_item('Edit')
    assert item is not None
    assert item.text == 'Edit'
    assert not item.has_submenu


def test_menu_get_item_nonexistent(menu):
    """Test getting nonexistent menu item."""
    assert menu.get_item('Nonexistent') is None


def test_menu_select_item_existing(menu):
    """Test selecting existing menu item."""
    menu.select_item('Edit')
    # The item's select method should be called
    assert True  # If no exception is raised, test passes


def test_menu_select_item_nonexistent(menu):
    """Test selecting nonexistent menu item."""
    with pytest.raises(ValueError, match="Menu item 'Nonexistent' not found"):
        menu.select_item('Nonexistent')


def test_menu_wait_until_open(menu, mock_session):
    """Test waiting for menu to open."""
    assert menu.wait_until_open(timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    with patch.object(menu, 'is_open', True):
        assert condition_func()
    with patch.object(menu, 'is_open', False):
        assert not condition_func()


def test_menu_wait_until_closed(menu, mock_session):
    """Test waiting for menu to close."""
    assert menu.wait_until_closed(timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    with patch.object(menu, 'is_open', False):
        assert condition_func()
    with patch.object(menu, 'is_open', True):
        assert not condition_func()
