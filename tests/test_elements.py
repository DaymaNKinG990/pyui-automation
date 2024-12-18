"""Tests for UI element functionality"""

import pytest
from unittest.mock import MagicMock, patch
import numpy as np

from pyui_automation.core.element import Element


def test_text_with_get_text(mock_element_with_get, mock_automation):
    ui_element = UIElement(mock_element_with_get, mock_automation)
    assert ui_element.text == "test text"


def test_text_without_text(mock_automation):
    element = MagicMock()
    element.text = ""
    ui_element = UIElement(element, mock_automation)
    assert ui_element.text == ""


def test_location_with_get_location(mock_element_with_get, mock_automation):
    ui_element = UIElement(mock_element_with_get, mock_automation)
    assert ui_element.location == {'x': 30, 'y': 40}


def test_location_without_location(mock_automation):
    element = MagicMock()
    element.location = {'x': 0, 'y': 0}
    ui_element = UIElement(element, mock_automation)
    assert ui_element.location == {'x': 0, 'y': 0}


def test_size_with_get_size(mock_element_with_get, mock_automation):
    ui_element = UIElement(mock_element_with_get, mock_automation)
    assert ui_element.size == {'width': 50, 'height': 60}


def test_size_without_size(mock_automation):
    element = MagicMock()
    element.size = {'width': 0, 'height': 0}
    ui_element = UIElement(element, mock_automation)
    assert ui_element.size == {'width': 0, 'height': 0}


def test_is_enabled_with_current(mock_element_with_current, mock_automation):
    ui_element = UIElement(mock_element_with_current, mock_automation)
    assert ui_element.is_enabled()


def test_is_enabled_with_get(mock_element_with_get, mock_automation):
    ui_element = UIElement(mock_element_with_get, mock_automation)
    assert ui_element.is_enabled()
    mock_element_with_get.is_enabled.assert_called_once()


def test_is_enabled_without_enabled(mock_automation):
    element = MagicMock()
    element.is_enabled.return_value = False
    ui_element = UIElement(element, mock_automation)
    assert not ui_element.is_enabled()


def test_is_displayed_with_current(mock_element_with_current, mock_automation):
    ui_element = UIElement(mock_element_with_current, mock_automation)
    assert ui_element.is_displayed()


def test_is_displayed_with_get(mock_element_with_get, mock_automation):
    ui_element = UIElement(mock_element_with_get, mock_automation)
    assert ui_element.is_displayed()
    mock_element_with_get.is_displayed.assert_called_once()


def test_is_displayed_without_displayed(mock_automation):
    element = MagicMock()
    element.is_displayed.return_value = False
    ui_element = UIElement(element, mock_automation)
    assert not ui_element.is_displayed()


def test_click(mock_element_with_current, mock_automation):
    ui_element = UIElement(mock_element_with_current, mock_automation)
    ui_element.click()
    mock_element_with_current.click.assert_called_once()


def test_right_click(mock_element_with_current, mock_automation):
    ui_element = UIElement(mock_element_with_current, mock_automation)
    ui_element.right_click()
    mock_automation.mouse.right_click.assert_called_once_with(10, 20)


def test_double_click(mock_element_with_current, mock_automation):
    ui_element = UIElement(mock_element_with_current, mock_automation)
    ui_element.double_click()
    mock_automation.mouse.double_click.assert_called_once_with(10, 20)


def test_hover(mock_element_with_current, mock_automation):
    ui_element = UIElement(mock_element_with_current, mock_automation)
    ui_element.hover()
    mock_automation.mouse.move_to.assert_called_once_with(10, 20)


def test_send_keys(mock_element_with_current, mock_automation):
    ui_element = UIElement(mock_element_with_current, mock_automation)
    ui_element.send_keys("test")
    mock_element_with_current.send_keys.assert_called_once_with("test")


def test_get_attribute_with_attribute(mock_element_with_get, mock_automation):
    ui_element = UIElement(mock_element_with_get, mock_automation)
    assert ui_element.get_attribute("test_attr") == "test_value"
    mock_element_with_get.get_attribute.assert_called_once_with("test_attr")


def test_get_attribute_without_attribute(mock_automation):
    element = MagicMock()
    element.get_attribute.return_value = None
    ui_element = UIElement(element, mock_automation)
    assert ui_element.get_attribute("test_attr") is None


def test_get_property_with_property(mock_element_with_get, mock_automation):
    ui_element = UIElement(mock_element_with_get, mock_automation)
    assert ui_element.get_property("test_prop") == "test_value"
    mock_element_with_get.get_property.assert_called_once_with("test_prop")


def test_get_property_without_property(mock_automation):
    element = MagicMock()
    element.get_property.return_value = None
    ui_element = UIElement(element, mock_automation)
    assert ui_element.get_property("test_prop") is None


def test_name_with_current_name(mock_automation):
    """Test getting element name with CurrentName attribute"""
    element = MagicMock()
    element.CurrentName = "test_name"
    ui_element = UIElement(element, mock_automation)
    assert ui_element.name == "test_name"


def test_name_with_get_name(mock_automation):
    """Test getting element name with get_name method"""
    element = MagicMock()
    element.get_name = MagicMock(return_value="test_name")
    ui_element = UIElement(element, mock_automation)
    assert ui_element.name == "test_name"


def test_name_without_name(mock_automation):
    """Test getting element name without name attribute or method"""
    element = MagicMock()
    # Ensure neither CurrentName nor get_name exists
    type(element).CurrentName = MagicMock(side_effect=AttributeError())
    type(element).get_name = MagicMock(side_effect=AttributeError())
    ui_element = UIElement(element, mock_automation)
    assert ui_element.name == ""


def test_location_with_bounding_rectangle(mock_automation):
    """Test getting element location with CurrentBoundingRectangle"""
    element = MagicMock()
    element.CurrentBoundingRectangle = (10, 20, 110, 120)
    ui_element = UIElement(element, mock_automation)
    assert ui_element.location == (10, 20)


def test_size_with_bounding_rectangle(mock_automation):
    """Test getting element size with CurrentBoundingRectangle"""
    element = MagicMock()
    element.CurrentBoundingRectangle = (10, 20, 110, 120)
    ui_element = UIElement(element, mock_automation)
    assert ui_element.size == (100, 100)


def test_enabled_with_current_is_enabled(mock_automation):
    """Test checking enabled state with CurrentIsEnabled"""
    element = MagicMock()
    element.CurrentIsEnabled = True
    ui_element = UIElement(element, mock_automation)
    assert ui_element.is_enabled is True


def test_visible_with_current_is_offscreen(mock_automation):
    """Test checking visibility with CurrentIsOffscreen"""
    element = MagicMock()
    element.CurrentIsOffscreen = False
    ui_element = UIElement(element, mock_automation)
    assert ui_element.visible is True


def test_click_disabled_element(mock_automation):
    """Test clicking a disabled element"""
    element = MagicMock()
    element.CurrentIsEnabled = False
    element.CurrentIsOffscreen = False
    ui_element = UIElement(element, mock_automation)
    ui_element.click()
    mock_automation.mouse.click.assert_not_called()


def test_click_invisible_element(mock_automation):
    """Test clicking an invisible element"""
    element = MagicMock()
    element.CurrentIsEnabled = True
    element.CurrentIsOffscreen = True
    ui_element = UIElement(element, mock_automation)
    ui_element.click()
    mock_automation.mouse.click.assert_not_called()


def test_type_text_with_interval(mock_automation):
    """Test typing text with interval"""
    element = MagicMock()
    element.CurrentIsEnabled = True
    element.CurrentIsOffscreen = False
    ui_element = UIElement(element, mock_automation)
    ui_element.send_keys("test", interval=0.1)
    mock_automation.keyboard.type_text.assert_called_with("test", interval=0.1)


def test_clear_with_clear_method(mock_automation):
    """Test clearing element with clear method"""
    element = MagicMock()
    element.clear = MagicMock()
    ui_element = UIElement(element, mock_automation)
    ui_element.clear()
    assert element.clear.called


def test_clear_without_clear_method(mock_automation):
    """Test clearing element without clear method"""
    element = MagicMock()
    element.CurrentIsEnabled = True
    element.CurrentIsOffscreen = False
    ui_element = UIElement(element, mock_automation)
    ui_element.clear()
    # Should simulate Ctrl+A and Delete
    assert mock_automation.keyboard.press_keys.called


def test_get_click_point(mock_automation):
    """Test getting click point"""
    element = MagicMock()
    element.CurrentBoundingRectangle = (10, 20, 110, 120)
    ui_element = UIElement(element, mock_automation)
    x, y = ui_element._get_click_point()
    assert x == 60  # center x: 10 + (110-10)/2
    assert y == 70  # center y: 20 + (120-20)/2


def test_drag_and_drop(mock_element_with_current, mock_automation):
    """Test drag and drop functionality"""
    target_element = MagicMock()
    target_element.location = {'x': 100, 'y': 100}
    
    ui_element = UIElement(mock_element_with_current, mock_automation)
    ui_element.drag_and_drop(target_element)
    
    # Check mouse actions sequence
    assert mock_automation.mouse.move_to.call_count == 2
    assert mock_automation.mouse.press.called
    assert mock_automation.mouse.release.called


def test_scroll_into_view(mock_element_with_current, mock_automation):
    """Test scrolling element into view"""
    ui_element = UIElement(mock_element_with_current, mock_automation)
    ui_element.scroll_into_view()
    
    mock_element_with_current.scroll_into_view.assert_called_once()


def test_wait_for_enabled(mock_element_with_current, mock_automation):
    """Test waiting for element to become enabled"""
    ui_element = UIElement(mock_element_with_current, mock_automation)
    assert ui_element.wait_for_enabled(timeout=1)
    mock_element_with_current.is_enabled.assert_called()


def test_wait_for_visible(mock_element_with_current, mock_automation):
    """Test waiting for element to become visible"""
    ui_element = UIElement(mock_element_with_current, mock_automation)
    assert ui_element.wait_for_visible(timeout=1)
    mock_element_with_current.is_displayed.assert_called()


def test_get_parent(mock_element_with_current, mock_automation):
    """Test getting parent element"""
    parent = MagicMock()
    mock_element_with_current.get_parent.return_value = parent
    
    ui_element = UIElement(mock_element_with_current, mock_automation)
    parent_element = ui_element.get_parent()
    
    assert isinstance(parent_element, UIElement)
    mock_element_with_current.get_parent.assert_called_once()


def test_get_children(mock_element_with_current, mock_automation):
    """Test getting child elements"""
    child1, child2 = MagicMock(), MagicMock()
    mock_element_with_current.get_children.return_value = [child1, child2]
    
    ui_element = UIElement(mock_element_with_current, mock_automation)
    children = ui_element.get_children()
    
    assert len(children) == 2
    assert all(isinstance(child, UIElement) for child in children)
    mock_element_with_current.get_children.assert_called_once()


def test_find_element(mock_element_with_current, mock_automation):
    """Test finding child element"""
    child = MagicMock()
    mock_element_with_current.find_element.return_value = child
    
    ui_element = UIElement(mock_element_with_current, mock_automation)
    found_element = ui_element.find_element("id", "test-id")
    
    assert isinstance(found_element, UIElement)
    mock_element_with_current.find_element.assert_called_with("id", "test-id")


def test_find_elements(mock_element_with_current, mock_automation):
    """Test finding multiple child elements"""
    child1, child2 = MagicMock(), MagicMock()
    mock_element_with_current.find_elements.return_value = [child1, child2]
    
    ui_element = UIElement(mock_element_with_current, mock_automation)
    found_elements = ui_element.find_elements("class", "test-class")
    
    assert len(found_elements) == 2
    assert all(isinstance(elem, UIElement) for elem in found_elements)
    mock_element_with_current.find_elements.assert_called_with("class", "test-class")


def test_element_screenshot(mock_element_with_current, mock_automation):
    """Test taking element screenshot"""
    mock_element_with_current.screenshot.return_value = b"fake_image_data"
    
    ui_element = UIElement(mock_element_with_current, mock_automation)
    screenshot_data = ui_element.take_screenshot()
    
    assert screenshot_data == b"fake_image_data"
    mock_element_with_current.screenshot.assert_called_once()


def test_element_attributes(mock_element_with_current, mock_automation):
    """Test getting all element attributes"""
    attrs = {
        "id": "test-id",
        "class": "test-class",
        "name": "test-name"
    }
    mock_element_with_current.get_attributes.return_value = attrs
    
    ui_element = UIElement(mock_element_with_current, mock_automation)
    element_attrs = ui_element.get_attributes()
    
    assert element_attrs == attrs
    mock_element_with_current.get_attributes.assert_called_once()


def test_element_properties(mock_element_with_current, mock_automation):
    """Test getting all element properties"""
    props = {
        "value": "test-value",
        "checked": True,
        "selected": False
    }
    mock_element_with_current.get_properties.return_value = props
    
    ui_element = UIElement(mock_element_with_current, mock_automation)
    element_props = ui_element.get_properties()
    
    assert element_props == props
    mock_element_with_current.get_properties.assert_called_once()


def test_element_rect(mock_element_with_current, mock_automation):
    """Test getting element rectangle"""
    mock_element_with_current.rect = {'x': 10, 'y': 20, 'width': 100, 'height': 50}
    
    ui_element = UIElement(mock_element_with_current, mock_automation)
    rect = ui_element.rect
    
    assert rect == {'x': 10, 'y': 20, 'width': 100, 'height': 50}


def test_element_center(mock_element_with_current, mock_automation):
    """Test getting element center point"""
    ui_element = UIElement(mock_element_with_current, mock_automation)
    center = ui_element.center
    
    assert center == {'x': 60, 'y': 70}  # Based on mock_element_with_current location and size


def test_element_value(mock_element_with_current, mock_automation):
    """Test getting and setting element value"""
    mock_element_with_current.get_property.return_value = "initial_value"
    
    ui_element = UIElement(mock_element_with_current, mock_automation)
    
    # Get value
    assert ui_element.value == "initial_value"
    mock_element_with_current.get_property.assert_called_with("value")
    
    # Set value
    ui_element.value = "new_value"
    mock_element_with_current.send_keys.assert_called_with("new_value")


def test_element_selected(mock_element_with_current, mock_automation):
    """Test checking if element is selected"""
    mock_element_with_current.is_selected.return_value = True
    
    ui_element = UIElement(mock_element_with_current, mock_automation)
    assert ui_element.is_selected()
    mock_element_with_current.is_selected.assert_called_once()


@pytest.fixture
def mock_backend():
    backend = MagicMock()
    backend.get_element_attributes.return_value = {
        'name': 'test_name',
        'automation_id': 'test_id',
        'class_name': 'test_class',
        'value': 'test_value',
        'bounding_rectangle': (10, 20, 50, 60)
    }
    backend.capture_element_screenshot.return_value = np.ones((50, 50, 3), dtype=np.uint8)
    return backend


@pytest.fixture
def mock_native_element():
    element = MagicMock()
    element.CurrentName = 'test_name'
    element.CurrentAutomationId = 'test_id'
    element.CurrentClassName = 'test_class'
    element.CurrentValue = 'test_value'
    element.CurrentBoundingRectangle = (10, 20, 50, 60)
    return element


@pytest.fixture
def element(mock_backend, mock_native_element):
    return Element(mock_backend, mock_native_element)


def test_element_screenshot(element):
    """Test capturing element screenshot"""
    screenshot = element.capture_screenshot()
    assert isinstance(screenshot, np.ndarray)
    assert screenshot.shape == (50, 50, 3)


def test_hover(element):
    """Test hovering over element"""
    with patch.object(element._backend, 'move_mouse') as mock_move:
        element.hover()
        mock_move.assert_called_once()


def test_get_attribute_with_attribute(element):
    """Test getting existing attribute"""
    assert element.get_attribute('name') == 'test_name'
    assert element.get_attribute('automation_id') == 'test_id'
    assert element.get_attribute('class_name') == 'test_class'


def test_get_property_with_property(element):
    """Test getting existing property"""
    assert element.get_property('value') == 'test_value'


def test_name_with_get_name(element):
    """Test getting element name"""
    assert element.name == 'test_name'


def test_name_without_name(element):
    """Test getting element name when not available"""
    element._backend.get_element_attributes.return_value = {}
    assert element.name == ''


def test_location_with_bounding_rectangle(element):
    """Test getting element location"""
    assert element.location == (10, 20)


def test_element_rect(element):
    """Test getting element rectangle"""
    assert element.rect == {
        'x': 10,
        'y': 20,
        'width': 40,  # 50 - 10
        'height': 40  # 60 - 20
    }


def test_element_selected(element):
    """Test element selected state"""
    element._backend.get_element_state.return_value = {'selected': True}
    assert element.is_selected


def test_element_value(element):
    """Test getting element value"""
    assert element.value == 'test_value'
