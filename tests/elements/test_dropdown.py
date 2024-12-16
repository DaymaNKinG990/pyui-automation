import pytest
from unittest.mock import MagicMock, patch
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

def test_expand_when_collapsed(dropdown):
    """Test expanding a collapsed dropdown."""
    with patch.object(dropdown, 'is_expanded', False):
        dropdown.expand()
        dropdown._element.click.assert_called_once()

def test_expand_when_already_expanded(dropdown):
    """Test expanding an already expanded dropdown."""
    with patch.object(dropdown, 'is_expanded', True):
        dropdown.expand()
        dropdown._element.click.assert_not_called()

def test_collapse_when_expanded(dropdown):
    """Test collapsing an expanded dropdown."""
    with patch.object(dropdown, 'is_expanded', True):
        dropdown.collapse()
        dropdown._element.click.assert_called_once()

def test_collapse_when_already_collapsed(dropdown):
    """Test collapsing an already collapsed dropdown."""
    with patch.object(dropdown, 'is_expanded', False):
        dropdown.collapse()
        dropdown._element.click.assert_not_called()

def test_select_item_success(dropdown, mock_session):
    """Test selecting an item successfully."""
    mock_item = MagicMock()
    mock_session.find_element.return_value = mock_item
    
    with patch.object(dropdown, 'is_expanded', False):
        dropdown.select_item('Option 2')
        
        # Should expand if collapsed
        dropdown._element.click.assert_called_once()
        
        # Should find and click the item
        mock_session.find_element.assert_called_once_with(
            by="name",
            value='Option 2',
            parent=dropdown._element
        )
        mock_item.click.assert_called_once()

def test_select_item_already_expanded(dropdown, mock_session):
    """Test selecting an item when dropdown is already expanded."""
    mock_item = MagicMock()
    mock_session.find_element.return_value = mock_item
    
    with patch.object(dropdown, 'is_expanded', True):
        dropdown.select_item('Option 2')
        
        # Should not expand if already expanded
        dropdown._element.click.assert_not_called()
        
        # Should find and click the item
        mock_session.find_element.assert_called_once()
        mock_item.click.assert_called_once()

def test_select_item_not_found(dropdown, mock_session):
    """Test selecting a non-existent item."""
    mock_session.find_element.return_value = None
    
    with pytest.raises(ValueError, match="Item 'Invalid Option' not found in dropdown"):
        dropdown.select_item('Invalid Option')

def test_wait_until_expanded(dropdown, mock_session):
    """Test waiting for dropdown to expand."""
    assert dropdown.wait_until_expanded(timeout=5)
    mock_session.wait_for_condition.assert_called_once()
    
    # Verify the condition function
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    with patch.object(dropdown, 'is_expanded', True):
        assert condition_func()
    with patch.object(dropdown, 'is_expanded', False):
        assert not condition_func()

def test_wait_until_collapsed(dropdown, mock_session):
    """Test waiting for dropdown to collapse."""
    assert dropdown.wait_until_collapsed(timeout=5)
    mock_session.wait_for_condition.assert_called_once()
    
    # Verify the condition function
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    with patch.object(dropdown, 'is_expanded', True):
        assert not condition_func()
    with patch.object(dropdown, 'is_expanded', False):
        assert condition_func()

def test_wait_until_item_selected(dropdown, mock_session):
    """Test waiting for specific item to be selected."""
    assert dropdown.wait_until_item_selected('Option 2', timeout=5)
    mock_session.wait_for_condition.assert_called_once()
    
    # Verify the condition function
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    with patch.object(dropdown, 'selected_item', 'Option 2'):
        assert condition_func()
    with patch.object(dropdown, 'selected_item', 'Option 1'):
        assert not condition_func()
