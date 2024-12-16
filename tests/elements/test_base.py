import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from pyui_automation.elements.base import UIElement

@pytest.fixture
def mock_session():
    session = MagicMock()
    session.mouse = MagicMock()
    session.keyboard = MagicMock()
    session.execute_script = MagicMock()
    session.take_screenshot = MagicMock()
    return session

@pytest.fixture
def mock_element():
    element = MagicMock()
    element.location = {'x': 100, 'y': 100}
    element.size = {'width': 50, 'height': 30}
    element.text = 'Test Element'
    element.CurrentName = 'Test Name'
    element.CurrentIsOffscreen = False
    return element

@pytest.fixture
def ui_element(mock_element, mock_session):
    return UIElement(mock_element, mock_session)

def test_init(ui_element, mock_element, mock_session):
    """Test element initialization."""
    assert ui_element._element == mock_element
    assert ui_element._session == mock_session

def test_native_element(ui_element, mock_element):
    """Test getting native element."""
    assert ui_element.native_element == mock_element

def test_session(ui_element, mock_session):
    """Test getting session."""
    assert ui_element.session == mock_session

def test_get_attribute(ui_element, mock_element):
    """Test getting element attribute."""
    mock_element.get_attribute.return_value = 'test_value'
    assert ui_element.get_attribute('test_attr') == 'test_value'
    mock_element.get_attribute.assert_called_once_with('test_attr')

def test_get_property(ui_element, mock_element):
    """Test getting element property."""
    mock_element.get_property.return_value = 'test_value'
    assert ui_element.get_property('test_prop') == 'test_value'
    mock_element.get_property.assert_called_once_with('test_prop')

def test_text(ui_element):
    """Test getting element text."""
    assert ui_element.text == 'Test Element'

def test_location(ui_element):
    """Test getting element location."""
    assert ui_element.location == {'x': 100, 'y': 100}

def test_size(ui_element):
    """Test getting element size."""
    assert ui_element.size == {'width': 50, 'height': 30}

def test_name(ui_element):
    """Test getting element name."""
    assert ui_element.name == 'Test Name'

def test_name_fallback(mock_element, mock_session):
    """Test name fallback to get_name method."""
    del mock_element.CurrentName
    mock_element.get_name.return_value = 'Fallback Name'
    element = UIElement(mock_element, mock_session)
    assert element.name == 'Fallback Name'

def test_visible(ui_element):
    """Test checking element visibility."""
    assert ui_element.visible == True

def test_is_displayed(ui_element, mock_element):
    """Test checking if element is displayed."""
    mock_element.is_displayed.return_value = True
    assert ui_element.is_displayed() == True
    mock_element.is_displayed.assert_called_once()

def test_is_enabled(ui_element, mock_element):
    """Test checking if element is enabled."""
    mock_element.is_enabled.return_value = True
    assert ui_element.is_enabled() == True
    mock_element.is_enabled.assert_called_once()

def test_get_click_point(ui_element):
    """Test getting click point."""
    x, y = ui_element._get_click_point()
    assert x == 125  # 100 + 50/2
    assert y == 115  # 100 + 30/2

def test_get_click_point_no_location(mock_element, mock_session):
    """Test getting click point with no location."""
    mock_element.location = None
    element = UIElement(mock_element, mock_session)
    with pytest.raises(ValueError):
        element._get_click_point()

def test_click(ui_element, mock_element):
    """Test clicking element."""
    ui_element.click()
    mock_element.click.assert_called_once()

def test_double_click(ui_element, mock_session):
    """Test double clicking element."""
    ui_element.double_click()
    mock_session.mouse.double_click.assert_called_once_with(100, 100)

def test_right_click(ui_element, mock_session):
    """Test right clicking element."""
    ui_element.right_click()
    mock_session.mouse.right_click.assert_called_once_with(100, 100)

def test_hover(ui_element, mock_session):
    """Test hovering over element."""
    ui_element.hover()
    mock_session.mouse.move.assert_called_once_with(100, 100)

def test_send_keys_no_interval(ui_element, mock_element):
    """Test sending keys without interval."""
    ui_element.send_keys('test', 'keys')
    mock_element.send_keys.assert_called_once_with('test', 'keys')

def test_send_keys_with_interval(ui_element, mock_session):
    """Test sending keys with interval."""
    ui_element.send_keys('test', 'keys', interval=0.1)
    mock_session.keyboard.type_text.assert_called_once_with('test', 'keys', interval=0.1)

def test_clear(ui_element, mock_element):
    """Test clearing element content."""
    ui_element.clear()
    mock_element.clear.assert_called_once()

def test_capture_screenshot_native(ui_element, mock_element):
    """Test capturing screenshot using native method."""
    expected_screenshot = np.zeros((30, 50, 3))
    mock_element.capture_screenshot.return_value = expected_screenshot
    assert ui_element.capture_screenshot() is expected_screenshot

def test_capture_screenshot_fallback(ui_element, mock_session):
    """Test capturing screenshot using fallback method."""
    full_screenshot = np.ones((200, 200, 3))
    mock_session.take_screenshot.return_value = full_screenshot
    
    # Мокаем размеры элемента
    ui_element._element.get_property.side_effect = lambda prop: {
        'x': 10,
        'y': 20,
        'width': 50,
        'height': 30
    }.get(prop)
    
    cropped = ui_element.capture_screenshot()
    assert isinstance(cropped, np.ndarray)
    assert cropped.shape == (30, 50, 3)  # Element size

def test_drag_and_drop(ui_element, mock_session):
    """Test drag and drop operation."""
    target = MagicMock()
    target._get_click_point.return_value = (200, 200)
    ui_element.drag_and_drop(target)
    mock_session.mouse.drag_and_drop.assert_called_once_with(125, 115, 200, 200)

def test_scroll_into_view_native(ui_element, mock_element):
    """Test scrolling element into view using native method."""
    ui_element.scroll_into_view()
    mock_element.scroll_into_view.assert_called_once()

def test_scroll_into_view_fallback(mock_element, mock_session):
    """Test scrolling element into view using fallback method."""
    del mock_element.scroll_into_view
    element = UIElement(mock_element, mock_session)
    element.scroll_into_view()
    mock_session.execute_script.assert_called_once_with(
        'arguments[0].scrollIntoView(true);',
        mock_element
    )

def test_wait_for_enabled_success(ui_element, mock_element):
    """Test waiting for element to become enabled - success case."""
    mock_element.is_enabled.side_effect = [False, False, True]
    assert ui_element.wait_for_enabled(timeout=1) == True

def test_wait_for_enabled_timeout(ui_element, mock_element):
    """Test waiting for element to become enabled - timeout case."""
    mock_element.is_enabled.return_value = False
    assert ui_element.wait_for_enabled(timeout=0.1) == False

def test_wait_for_visible_success(ui_element, mock_element):
    """Test waiting for element to become visible - success case."""
    mock_element.is_displayed.side_effect = [False, False, True]
    assert ui_element.wait_for_visible(timeout=1) == True

def test_wait_for_visible_timeout(ui_element, mock_element):
    """Test waiting for element to become visible - timeout case."""
    mock_element.is_displayed.return_value = False
    assert ui_element.wait_for_visible(timeout=0.1) == False

def test_get_parent(ui_element, mock_element, mock_session):
    """Test getting parent element."""
    parent_element = MagicMock()
    mock_element.get_parent.return_value = parent_element
    parent = ui_element.get_parent()
    assert isinstance(parent, UIElement)
    assert parent._element == parent_element
    assert parent._session == mock_session

def test_get_children(ui_element, mock_element, mock_session):
    """Test getting child elements."""
    child_elements = [MagicMock(), MagicMock()]
    mock_element.get_children.return_value = child_elements
    children = ui_element.get_children()
    assert len(children) == 2
    assert all(isinstance(child, UIElement) for child in children)
    assert all(child._session == mock_session for child in children)

def test_find_element(ui_element, mock_element, mock_session):
    """Test finding child element."""
    found_element = MagicMock()
    mock_element.find_element.return_value = found_element
    element = ui_element.find_element('id', 'test-id')
    assert isinstance(element, UIElement)
    assert element._element == found_element
    assert element._session == mock_session
    mock_element.find_element.assert_called_once_with('id', 'test-id')

def test_find_elements(ui_element, mock_element, mock_session):
    """Test finding multiple child elements."""
    found_elements = [MagicMock(), MagicMock()]
    mock_element.find_elements.return_value = found_elements
    elements = ui_element.find_elements('class', 'test-class')
    assert len(elements) == 2
    assert all(isinstance(element, UIElement) for element in elements)
    assert all(element._session == mock_session for element in elements)
    mock_element.find_elements.assert_called_once_with('class', 'test-class')

def test_take_screenshot(ui_element):
    """Test take_screenshot alias."""
    with patch.object(ui_element, 'capture_screenshot') as mock_capture:
        mock_capture.return_value = np.zeros((30, 50, 3))
        screenshot = ui_element.take_screenshot()
        assert screenshot is not None
        mock_capture.assert_called_once()

def test_get_attributes(ui_element, mock_element):
    """Test getting all attributes."""
    mock_element.get_attributes.return_value = {'id': 'test-id', 'class': 'test-class'}
    attrs = ui_element.get_attributes()
    assert attrs == {'id': 'test-id', 'class': 'test-class'}

def test_get_attributes_fallback(ui_element, mock_element):
    """Test getting attributes fallback."""
    del mock_element.get_attributes
    mock_element.get_attribute.side_effect = lambda name: f'test-{name}'
    attrs = ui_element.get_attributes()
    assert 'id' in attrs
    assert 'class' in attrs
    assert attrs['id'] == 'test-id'
    assert attrs['class'] == 'test-class'

def test_get_properties(ui_element, mock_element):
    """Test getting all properties."""
    mock_element.get_properties.return_value = {'tagName': 'div', 'textContent': 'test'}
    props = ui_element.get_properties()
    assert props == {'tagName': 'div', 'textContent': 'test'}

def test_get_properties_fallback(ui_element, mock_element):
    """Test getting properties fallback."""
    del mock_element.get_properties
    mock_element.get_property.side_effect = lambda name: f'test-{name}'
    props = ui_element.get_properties()
    assert 'tagName' in props
    assert 'textContent' in props
    assert props['tagName'] == 'test-tagName'
    assert props['textContent'] == 'test-textContent'

def test_rect(ui_element):
    """Test getting element rect."""
    rect = ui_element.rect
    assert rect == {'x': 100, 'y': 100, 'width': 50, 'height': 30}

def test_center(ui_element):
    """Test getting element center point."""
    center = ui_element.center
    assert center == {'x': 125, 'y': 115}

def test_value_get(ui_element, mock_element):
    """Test getting element value."""
    mock_element.value = 'test-value'
    assert ui_element.value == 'test-value'

def test_value_get_fallback(ui_element, mock_element):
    """Test getting element value fallback."""
    del mock_element.value
    mock_element.get_attribute.return_value = 'test-value'
    assert ui_element.value == 'test-value'
    mock_element.get_attribute.assert_called_once_with('value')

def test_value_set(ui_element, mock_element):
    """Test setting element value."""
    ui_element.value = 'new-value'
    assert mock_element.value == 'new-value'

def test_value_set_fallback(ui_element, mock_element):
    """Test setting element value fallback."""
    del mock_element.value
    ui_element.value = 'new-value'
    mock_element.clear.assert_called_once()
    mock_element.send_keys.assert_called_once_with('new-value')
