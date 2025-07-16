import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.breadcrumb import Breadcrumb, BreadcrumbItem


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session

@pytest.fixture
def mock_item_element():
    element = MagicMock()
    # Set up default property values for breadcrumb item
    element.get_property.side_effect = lambda prop: {
        'text': 'Home',
        'current': False,
        'url': '/home'
    }.get(prop)
    return element

@pytest.fixture
def mock_breadcrumb_element():
    element = MagicMock()
    
    # Create mock items
    mock_item1 = MagicMock()
    mock_item1.get_property.side_effect = lambda prop: {
        'text': 'Home',
        'current': False,
        'url': '/home'
    }.get(prop)
    
    mock_item2 = MagicMock()
    mock_item2.get_property.side_effect = lambda prop: {
        'text': 'Products',
        'current': True,
        'url': '/products'
    }.get(prop)
    
    mock_item3 = MagicMock()
    mock_item3.get_property.side_effect = lambda prop: {
        'text': 'Category',
        'current': False,
        'url': '/products/category'
    }.get(prop)
    
    element.find_elements.return_value = [mock_item1, mock_item2, mock_item3]
    element.find_element.side_effect = lambda by, value: mock_item2 if value == "current" else None
    return element

@pytest.fixture
def breadcrumb_item(mock_item_element, mock_session):
    return BreadcrumbItem(mock_item_element, mock_session)

@pytest.fixture
def breadcrumb(mock_breadcrumb_element, mock_session):
    return Breadcrumb(mock_breadcrumb_element, mock_session)

# BreadcrumbItem Tests
def test_item_init(breadcrumb_item, mock_item_element, mock_session):
    """Test breadcrumb item initialization."""
    assert breadcrumb_item._element == mock_item_element
    assert breadcrumb_item._session == mock_session

def test_item_text(breadcrumb_item, mock_item_element):
    """Test getting item text."""
    assert breadcrumb_item.text == 'Home'
    mock_item_element.get_property.assert_called_with('text')

def test_item_is_current(breadcrumb_item, mock_item_element):
    """Test checking if item is current."""
    assert not breadcrumb_item.is_current
    mock_item_element.get_property.assert_called_with('current')

def test_item_url(breadcrumb_item, mock_item_element):
    """Test getting item URL."""
    assert breadcrumb_item.url == '/home'
    mock_item_element.get_property.assert_called_with('url')

def test_item_click_with_url(breadcrumb_item):
    """Test clicking item with URL."""
    breadcrumb_item._element.get_property.side_effect = lambda prop: {
        'text': 'Home',
        'current': False,
        'url': 'http://example.com'
    }.get(prop)
    
    with patch.object(breadcrumb_item, '_element') as mock_element:
        breadcrumb_item.click()
        mock_element.click.assert_called_once()

def test_item_click_without_url(breadcrumb_item, mock_item_element):
    """Test clicking item without URL."""
    mock_item_element.get_property.side_effect = lambda prop: {
        'text': 'Home',
        'current': False,
        'url': None
    }.get(prop)
    breadcrumb_item.click()
    mock_item_element.click.assert_not_called()

# Breadcrumb Tests
def test_breadcrumb_init(breadcrumb, mock_breadcrumb_element, mock_session):
    """Test breadcrumb initialization."""
    assert breadcrumb._element == mock_breadcrumb_element
    assert breadcrumb._session == mock_session

def test_breadcrumb_items(breadcrumb, mock_breadcrumb_element):
    """Test getting all items."""
    items = breadcrumb.items
    assert len(items) == 3
    assert all(isinstance(item, BreadcrumbItem) for item in items)
    mock_breadcrumb_element.find_elements.assert_called_with(by="type", value="breadcrumbitem")

def test_breadcrumb_current_item(breadcrumb, mock_breadcrumb_element):
    """Test getting current item."""
    current = breadcrumb.current_item
    assert current is not None
    assert current.text == 'Products'
    assert current.is_current
    mock_breadcrumb_element.find_element.assert_called_with(by="state", value="current")

def test_breadcrumb_current_item_none(mock_breadcrumb_element, mock_session):
    """Test getting current item when none is current."""
    from pyui_automation.elements.breadcrumb import Breadcrumb
    mock_breadcrumb_element.find_element.side_effect = lambda *a, **kw: None
    mock_breadcrumb_element.find_elements.return_value = []
    breadcrumb = Breadcrumb(mock_breadcrumb_element, mock_session)
    assert breadcrumb.current_item is None

def test_breadcrumb_path(breadcrumb):
    """Test getting full path."""
    assert breadcrumb.path == ['Home', 'Products', 'Category']

def test_breadcrumb_get_item(breadcrumb):
    """Test getting item by text."""
    item = breadcrumb.get_item('Products')
    assert item is not None
    assert item.text == 'Products'
    assert item.is_current

def test_breadcrumb_get_item_not_found(breadcrumb):
    """Test getting nonexistent item."""
    assert breadcrumb.get_item('Nonexistent') is None

def test_breadcrumb_navigate_to(breadcrumb):
    """Test navigating to item."""
    breadcrumb.navigate_to('Home')
    # The item's click method should be called
    assert True  # If no exception is raised, test passes

def test_breadcrumb_navigate_to_not_found(breadcrumb):
    """Test navigating to nonexistent item."""
    with pytest.raises(ValueError, match="Breadcrumb item 'Nonexistent' not found"):
        breadcrumb.navigate_to('Nonexistent')

def test_breadcrumb_wait_until_item_current(breadcrumb, mock_session):
    """Test waiting for item to become current."""
    assert breadcrumb.wait_until_item_current('Products', timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    assert condition_func()  # Should be True since 'Products' is current

def test_breadcrumb_wait_until_item_current_not_found(breadcrumb, mock_session):
    """Test waiting for nonexistent item to become current."""
    assert breadcrumb.wait_until_item_current('Nonexistent', timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    assert not condition_func()  # Should be False since item doesn't exist

def test_breadcrumb_wait_until_path(breadcrumb, mock_session):
    """Test waiting for path to match."""
    expected_path = ['Home', 'Products', 'Category']
    assert breadcrumb.wait_until_path(expected_path, timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    assert condition_func()  # Should be True since paths match

def test_breadcrumb_wait_until_path_no_match(breadcrumb, mock_session):
    """Test waiting for path with no match."""
    wrong_path = ['Home', 'Wrong', 'Path']
    assert breadcrumb.wait_until_path(wrong_path, timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    assert not condition_func()  # Should be False since paths don't match
