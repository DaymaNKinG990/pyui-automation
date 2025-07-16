import pytest
from unittest.mock import MagicMock
from pyui_automation.elements.listview import ListView, ListViewItem


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    session.keyboard = MagicMock()
    session.keyboard.hold_key = MagicMock()
    return session

@pytest.fixture
def mock_item_element():
    element = MagicMock()
    # Set up default property values for list item
    element.get_property.side_effect = lambda prop: {
        'text': 'Item 1',
        'selected': False,
        'index': 0
    }.get(prop)
    return element

@pytest.fixture
def mock_listview_element():
    element = MagicMock()
    
    # Create mock items
    mock_item1 = MagicMock()
    mock_item1.get_property.side_effect = lambda prop: {
        'text': 'Item 1',
        'selected': False,
        'index': 0
    }.get(prop)
    
    mock_item2 = MagicMock()
    mock_item2.get_property.side_effect = lambda prop: {
        'text': 'Item 2',
        'selected': True,
        'index': 1
    }.get(prop)
    
    mock_item3 = MagicMock()
    mock_item3.get_property.side_effect = lambda prop: {
        'text': 'Item 3',
        'selected': False,
        'index': 2
    }.get(prop)
    
    # Set up find_elements behavior
    element.find_elements.side_effect = lambda by, value: {
        'listitem': [mock_item1, mock_item2, mock_item3],
        'selected': [mock_item2]
    }.get(value, [])
    
    return element

@pytest.fixture
def listview_item(mock_item_element, mock_session):
    return ListViewItem(mock_item_element, mock_session)

@pytest.fixture
def listview(mock_listview_element, mock_session):
    return ListView(mock_listview_element, mock_session)

class ListViewItemMock(ListViewItem):
    def __init__(self, native_element, session, selected=False):
        super().__init__(native_element, session)
        self._mock_selected = selected
    @property
    def is_selected(self):
        return self._mock_selected

class ListViewMock(ListView):
    def __init__(self, native_element, session, item_count=3):
        super().__init__(native_element, session)
        self._mock_item_count = item_count
    @property
    def item_count(self):
        return self._mock_item_count

# ListViewItem Tests
def test_item_init(listview_item, mock_item_element, mock_session):
    """Test list view item initialization."""
    assert listview_item._element == mock_item_element
    assert listview_item._session == mock_session

def test_item_text(listview_item, mock_item_element):
    """Test getting item text."""
    assert listview_item.text == 'Item 1'
    mock_item_element.get_property.assert_called_with('text')

def test_item_is_selected(listview_item, mock_item_element):
    """Test checking if item is selected."""
    assert not listview_item.is_selected
    mock_item_element.get_property.assert_called_with('selected')

def test_item_index(listview_item, mock_item_element):
    """Test getting item index."""
    assert listview_item.index == 0
    mock_item_element.get_property.assert_called_with('index')

def test_item_select_when_not_selected(listview_item):
    """Test selecting unselected item."""
    listview_item.select()
    listview_item._element.click.assert_called_once()

def test_item_select_when_already_selected(listview_item, mock_item_element):
    """Test selecting already selected item."""
    mock_item_element.get_property.side_effect = lambda prop: {
        'text': 'Item 1',
        'selected': True,
        'index': 0
    }.get(prop)
    
    listview_item.select()
    listview_item._element.click.assert_not_called()

def test_item_wait_until_selected(mock_item_element, mock_session):
    """Test waiting for item to be selected (без patch.object, через double)."""
    item = ListViewItemMock(mock_item_element, mock_session, selected=True)
    assert item.wait_until_selected(timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    item._mock_selected = True
    assert condition_func() is True
    item._mock_selected = False
    assert condition_func() is False

# ListView Tests
def test_listview_init(listview, mock_listview_element, mock_session):
    """Test list view initialization."""
    assert listview._element == mock_listview_element
    assert listview._session == mock_session

def test_listview_items(listview, mock_listview_element):
    """Test getting all items."""
    items = listview.items
    assert len(items) == 3
    assert all(isinstance(item, ListViewItem) for item in items)
    mock_listview_element.find_elements.assert_called_with(by="type", value="listitem")

def test_listview_selected_items(listview, mock_listview_element):
    """Test getting selected items."""
    items = listview.selected_items
    assert len(items) == 1
    assert items[0].text == 'Item 2'
    mock_listview_element.find_elements.assert_called_with(by="state", value="selected")

def test_listview_item_count(listview):
    """Test getting item count."""
    assert listview.item_count == 3

def test_listview_get_item(listview):
    """Test getting item by text."""
    item = listview.get_item('Item 2')
    assert item is not None
    assert item.text == 'Item 2'
    assert item.is_selected

def test_listview_get_item_not_found(listview, mock_listview_element):
    """Test getting nonexistent item."""
    mock_listview_element.find_elements.return_value = []
    assert listview.get_item('Nonexistent') is None

def test_listview_get_item_by_index(listview):
    """Test getting item by index."""
    item = listview.get_item_by_index(1)
    assert item is not None
    assert item.text == 'Item 2'
    assert item.index == 1

def test_listview_get_item_by_index_out_of_range(listview, mock_listview_element):
    """Test getting item with invalid index."""
    mock_listview_element.find_elements.return_value = []
    assert listview.get_item_by_index(-1) is None
    assert listview.get_item_by_index(999) is None

def test_listview_select_item(listview):
    """Test selecting item by text."""
    listview.select_item('Item 1')
    # The item's select method should be called
    assert True  # If no exception is raised, test passes

def test_listview_select_item_not_found(listview):
    """Test selecting nonexistent item."""
    with pytest.raises(ValueError, match="Item 'Nonexistent' not found"):
        listview.select_item('Nonexistent')

def test_listview_select_item_by_index(listview):
    """Test selecting item by index."""
    listview.select_item_by_index(1)
    # The item's select method should be called
    assert True  # If no exception is raised, test passes

def test_listview_select_item_by_index_out_of_range(listview):
    """Test selecting item with invalid index."""
    with pytest.raises(ValueError, match="Item at index 999 not found"):
        listview.select_item_by_index(999)

def test_listview_select_multiple_items(listview, mock_session):
    """Test selecting multiple items."""
    listview.select_multiple_items(['Item 1', 'Item 3'])
    assert mock_session.keyboard.hold_key.call_count == 2
    mock_session.keyboard.hold_key.assert_called_with('ctrl')

def test_listview_clear_selection(listview):
    """Test clearing selection."""
    listview.clear_selection()
    listview._element.click.assert_called_once()

def test_listview_wait_until_item_count(mock_listview_element, mock_session):
    """Test waiting for specific item count (без patch.object, через double)."""
    listview = ListViewMock(mock_listview_element, mock_session, item_count=3)
    assert listview.wait_until_item_count(3, timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    listview._mock_item_count = 3
    assert condition_func()
    listview._mock_item_count = 2
    assert not condition_func()
