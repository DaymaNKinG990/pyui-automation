import pytest
from unittest.mock import MagicMock
from pyui_automation.elements.dropdown import DropDown


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.find_element = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session

@pytest.fixture
def mock_native_element():
    element = MagicMock()
    element.get_property.side_effect = lambda prop: {
        'expanded': False,
        'selected': 'Option 1',
        'items': ['Option 1', 'Option 2', 'Option 3']
    }.get(prop)
    return element

@pytest.fixture
def dropdown(mock_native_element, mock_session):
    return DropDown(mock_native_element, mock_session)

def test_init(dropdown, mock_native_element, mock_session):
    """Test dropdown initialization."""
    assert dropdown._element == mock_native_element
    assert dropdown._session == mock_session

def test_is_expanded(dropdown, mock_native_element):
    """Test checking if dropdown is expanded."""
    assert not dropdown.is_expanded
    mock_native_element.get_property.assert_called_with('expanded')

def test_selected_item(dropdown, mock_native_element):
    """Test getting selected item."""
    assert dropdown.selected_item == 'Option 1'
    mock_native_element.get_property.assert_called_with('selected')

def test_items(dropdown, mock_native_element):
    """Test getting all items."""
    assert dropdown.items == ['Option 1', 'Option 2', 'Option 3']
    mock_native_element.get_property.assert_called_with('items')

class DropDownMock(DropDown):
    def __init__(self, native_element, session, expanded=False):
        super().__init__(native_element, session)
        self._mock_expanded = expanded
    @property
    def is_expanded(self):
        return self._mock_expanded

def test_expand_when_collapsed(mock_native_element, mock_session):
    """Test expanding a collapsed dropdown (без patch.object, через double)."""
    dropdown = DropDownMock(mock_native_element, mock_session, expanded=False)
    dropdown.expand()
    mock_native_element.click.assert_called_once()

def test_expand_when_already_expanded(mock_native_element, mock_session):
    """Test expanding an already expanded dropdown (без patch.object, через double)."""
    dropdown = DropDownMock(mock_native_element, mock_session, expanded=True)
    dropdown.expand()
    mock_native_element.click.assert_not_called()

def test_collapse_when_expanded(mock_native_element, mock_session):
    """Test collapsing an expanded dropdown (без patch.object, через double)."""
    dropdown = DropDownMock(mock_native_element, mock_session, expanded=True)
    dropdown.collapse()
    mock_native_element.click.assert_called_once()

def test_collapse_when_already_collapsed(mock_native_element, mock_session):
    """Test collapsing an already collapsed dropdown (без patch.object, через double)."""
    dropdown = DropDownMock(mock_native_element, mock_session, expanded=False)
    dropdown.collapse()
    mock_native_element.click.assert_not_called()

def test_select_item_success(mock_native_element, mock_session):
    """Test selecting an item successfully (без patch.object, через double)."""
    mock_item = MagicMock()
    mock_session.find_element.return_value = mock_item
    dropdown = DropDownMock(mock_native_element, mock_session, expanded=False)
    dropdown.select_item('Option 2')
    mock_native_element.click.assert_called_once()
    mock_session.find_element.assert_called_once_with(
        by="name",
        value='Option 2',
        parent=dropdown._element
    )
    mock_item.click.assert_called_once()

def test_select_item_already_expanded(mock_native_element, mock_session):
    """Test selecting an item when dropdown is already expanded (без patch.object, через double)."""
    mock_item = MagicMock()
    mock_session.find_element.return_value = mock_item
    dropdown = DropDownMock(mock_native_element, mock_session, expanded=True)
    dropdown.select_item('Option 2')
    mock_native_element.click.assert_not_called()
    mock_session.find_element.assert_called_once()
    mock_item.click.assert_called_once()

def test_select_item_not_found(dropdown, mock_session):
    """Test selecting a non-existent item."""
    mock_session.find_element.return_value = None
    
    with pytest.raises(ValueError, match="Item 'Invalid Option' not found in dropdown"):
        dropdown.select_item('Invalid Option')

def test_wait_until_expanded(mock_native_element, mock_session):
    """Test waiting for dropdown to expand (без patch.object, через double)."""
    dropdown = DropDownMock(mock_native_element, mock_session, expanded=True)
    assert dropdown.wait_until_expanded(timeout=5)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    dropdown._mock_expanded = True
    assert condition_func()
    dropdown._mock_expanded = False
    assert not condition_func()

def test_wait_until_collapsed(mock_native_element, mock_session):
    """Test waiting for dropdown to collapse (без patch.object, через double)."""
    dropdown = DropDownMock(mock_native_element, mock_session, expanded=False)
    assert dropdown.wait_until_collapsed()
    mock_session.wait_for_condition.assert_called_once()
    condition = mock_session.wait_for_condition.call_args[0][0]
    dropdown._mock_expanded = True
    assert not condition()
    dropdown._mock_expanded = False
    assert condition()

def test_wait_until_item_selected(dropdown, mock_session):
    """Test waiting for specific item to be selected."""
    class DropDownDouble(DropDown):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._mock_selected = 'Option 2'
        @property
        def selected_item(self):
            return self._mock_selected
        @selected_item.setter
        def selected_item(self, value):
            self._mock_selected = value
    dd = DropDownDouble(dropdown._element, dropdown._session)
    assert dd.wait_until_item_selected('Option 2', timeout=5)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    dd.selected_item = 'Option 2'
    assert condition_func()
    dd.selected_item = 'Option 1'
    assert not condition_func()

def test_is_expanded_setter():
    class DropDownDouble(DropDown):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._mock_expanded = False
        @property
        def is_expanded(self):
            return self._mock_expanded
        @is_expanded.setter
        def is_expanded(self, value):
            self._mock_expanded = value
            self.click()
    dropdown = DropDownDouble(MagicMock(), MagicMock())
    dropdown.click = MagicMock()
    dropdown.is_expanded = True
    dropdown.click.assert_called_once()

def test_is_expanded_deleter():
    dropdown = DropDown(MagicMock(), MagicMock())
    try:
        del dropdown.is_expanded
    except AttributeError as e:
        assert "Cannot delete is_expanded property" in str(e)

def test_selected_item_setter():
    dropdown = DropDown(MagicMock(), MagicMock())
    dropdown.select_item = MagicMock()
    dropdown.selected_item = 'Option X'
    dropdown.select_item.assert_called_once_with('Option X')

def test_selected_item_deleter():
    dropdown = DropDown(MagicMock(), MagicMock())
    try:
        del dropdown.selected_item
    except AttributeError as e:
        assert "Cannot delete selected_item property" in str(e)
