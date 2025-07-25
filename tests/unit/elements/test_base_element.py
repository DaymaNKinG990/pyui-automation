"""
Tests for BaseElement class
"""
import pytest
from typing import Dict, Any, Optional
import numpy as np

from pyui_automation.elements.base_element import BaseElement


class TestBaseElement:
    """Test BaseElement class"""
    
    def test_init(self, mocker):
        """Test BaseElement initialization"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        assert self.element._element == self.mock_native_element
        assert self.element._session == self.mock_session
        assert self.element._interaction_service is not None
        assert self.element._search_service is not None
        assert self.element._state_service is not None
        assert self.element._wait_service is not None
        assert self.element._properties is not None

    def test_native_element_property(self, mocker):
        """Test native_element property"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        assert self.element.native_element == self.mock_native_element

    def test_session_property(self, mocker):
        """Test session property"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        assert self.element.session == self.mock_session

    def test_automation_id_property(self, mocker):
        """Test automation_id property"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        # Mock the native element to return the expected value
        self.mock_native_element.get_attribute.return_value = "test_id"
        assert self.element.automation_id == "test_id"

    def test_name_property(self, mocker):
        """Test name property"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        # Mock the native element to return the expected value
        self.mock_native_element.get_attribute.return_value = "test_name"
        assert self.element.name == "test_name"

    def test_class_name_property(self, mocker):
        """Test class_name property"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        # Mock the native element to return the expected value
        self.mock_native_element.get_attribute.return_value = "Button"
        assert self.element.class_name == "Button"

    def test_control_type_property(self, mocker):
        """Test control_type property"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        # Mock the native element to return the expected value
        self.mock_native_element.get_attribute.return_value = "Button"
        self.mock_native_element.GetCurrentPattern.return_value = None
        mocker.patch.object(self.element, 'get_property', return_value=None)
        assert self.element.control_type == "Button"

    def test_text_property(self, mocker):
        """Test text property"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        # Mock the native element to return the expected value
        self.mock_native_element.get_attribute.return_value = "Click me"
        assert self.element.text == "Click me"

    def test_value_property_getter(self, mocker):
        """Test value property getter"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        # Mock the native element to return the expected value
        self.mock_native_element.get_attribute.return_value = "test_value"
        assert self.element.value == "test_value"

    def test_location_property_with_current_bounding_rectangle(self, mocker):
        """Test location property with CurrentBoundingRectangle"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mock_rect = mocker.Mock()
        mock_rect.left = 100
        mock_rect.top = 200
        self.mock_native_element.CurrentBoundingRectangle = mock_rect
        location = self.element.location
        assert location['x'] == 100
        assert location['y'] == 200

    def test_size_property_with_current_bounding_rectangle(self, mocker):
        """Test size property with CurrentBoundingRectangle"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mock_rect = mocker.Mock()
        mock_rect.width = 150
        mock_rect.height = 50
        self.mock_native_element.CurrentBoundingRectangle = mock_rect
        size = self.element.size
        assert size['width'] == 150
        assert size['height'] == 50

    def test_is_pressed(self, mocker):
        """Test is_pressed method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        # Mock the native element to return the expected value
        self.mock_native_element.get_attribute.return_value = True
        assert self.element.is_pressed() is True

    def test_click(self, mocker):
        """Test click method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._interaction_service, 'click')
        self.element.click()
        self.element._interaction_service.click.assert_called_once()

    def test_double_click(self, mocker):
        """Test double_click method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._interaction_service, 'double_click')
        self.element.double_click()
        self.element._interaction_service.double_click.assert_called_once()

    def test_right_click(self, mocker):
        """Test right_click method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._interaction_service, 'right_click')
        self.element.right_click()
        self.element._interaction_service.right_click.assert_called_once()

    def test_hover(self, mocker):
        """Test hover method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._interaction_service, 'hover')
        self.element.hover()
        self.element._interaction_service.hover.assert_called_once()

    def test_focus(self, mocker):
        """Test focus method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._interaction_service, 'focus')
        self.element.focus()
        self.element._interaction_service.focus.assert_called_once()

    def test_send_keys(self, mocker):
        """Test send_keys method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._interaction_service, 'send_keys')
        self.element.send_keys("test")
        self.element._interaction_service.send_keys.assert_called_once_with("test")

    def test_clear(self, mocker):
        """Test clear method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._interaction_service, 'clear')
        self.element.clear()
        self.element._interaction_service.clear.assert_called_once()

    def test_select_all(self, mocker):
        """Test select_all method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._interaction_service, 'select_all')
        self.element.select_all()
        self.element._interaction_service.select_all.assert_called_once()

    def test_copy(self, mocker):
        """Test copy method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._interaction_service, 'copy')
        self.element.copy()
        self.element._interaction_service.copy.assert_called_once()

    def test_paste(self, mocker):
        """Test paste method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._interaction_service, 'paste')
        self.element.paste()
        self.element._interaction_service.paste.assert_called_once()

    def test_append(self, mocker):
        """Test append method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._interaction_service, 'append')
        self.element.append("test")
        self.element._interaction_service.append.assert_called_once_with("test")

    def test_check(self, mocker):
        """Test check method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._state_service, 'check')
        self.element.check()
        self.element._state_service.check.assert_called_once()

    def test_uncheck(self, mocker):
        """Test uncheck method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._state_service, 'uncheck')
        self.element.uncheck()
        self.element._state_service.uncheck.assert_called_once()

    def test_toggle(self, mocker):
        """Test toggle method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._state_service, 'toggle')
        self.element.toggle()
        self.element._state_service.toggle.assert_called_once()

    def test_expand(self, mocker):
        """Test expand method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._state_service, 'expand')
        self.element.expand()
        self.element._state_service.expand.assert_called_once()

    def test_collapse(self, mocker):
        """Test collapse method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._state_service, 'collapse')
        self.element.collapse()
        self.element._state_service.collapse.assert_called_once()

    def test_select_item(self, mocker):
        """Test select_item method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._state_service, 'select_item')
        self.element.select_item("item")
        self.element._state_service.select_item.assert_called_once_with("item")

    def test_is_selected(self, mocker):
        """Test is_selected method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'get_property', return_value=True)
        assert self.element.is_selected() is True
        self.element.get_property.assert_called_with("IsSelected")

    def test_take_screenshot(self, mocker):
        """Test take_screenshot method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mocker.patch.object(self.element, 'capture_screenshot', return_value=mock_image)
        result = self.element.take_screenshot()
        assert result is not None
        assert isinstance(result, np.ndarray)

    def test_capture_screenshot_with_element_method(self, mocker):
        """Test capture_screenshot method with element method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mocker.patch.object(self.element._session, 'screenshot_service')
        self.element._session.screenshot_service.capture_screenshot.return_value = mock_image
        result = self.element.capture_screenshot()
        assert result is not None
        assert isinstance(result, np.ndarray)

    def test_capture_screenshot_exception(self, mocker):
        """Test capture_screenshot method with exception"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._session, 'screenshot_service')
        self.element._session.screenshot_service.capture_screenshot.side_effect = Exception("Screenshot failed")
        result = self.element.capture_screenshot()
        assert result is None

    def test_scroll_into_view_success(self, mocker):
        """Test scroll_into_view method with success"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        self.mock_native_element.ScrollIntoView = mocker.Mock()
        result = self.element.scroll_into_view()
        assert result is None
        self.mock_native_element.ScrollIntoView.assert_called_once()

    def test_scroll_into_view_exception(self, mocker):
        """Test scroll_into_view method with exception"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        self.mock_native_element.ScrollIntoView = mocker.Mock(side_effect=Exception("Scroll failed"))
        result = self.element.scroll_into_view()
        assert result is None

    def test_safe_click_success(self, mocker):
        """Test safe_click method with success"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'wait_until_clickable', return_value=True)
        mocker.patch.object(self.element, 'click')
        result = self.element.safe_click()
        assert result is True
        self.element.wait_until_clickable.assert_called_once()
        self.element.click.assert_called_once()

    def test_safe_click_not_clickable(self, mocker):
        """Test safe_click method when element is not clickable"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'wait_until_clickable', return_value=False)
        mocker.patch.object(self.element, 'click')
        result = self.element.safe_click()
        assert result is False
        self.element.click.assert_not_called()

    def test_safe_click_exception(self, mocker):
        """Test safe_click method with exception"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'wait_until_clickable', side_effect=Exception("Wait failed"))
        mocker.patch.object(self.element, 'click')
        result = self.element.safe_click()
        assert result is False
        self.element.click.assert_not_called()

    def test_drag_and_drop_invalid_target(self, mocker):
        """Test drag_and_drop method with invalid target"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._interaction_service, 'drag_and_drop')
        self.element.drag_and_drop(None)
        self.element._interaction_service.drag_and_drop.assert_not_called()

    def test_get_property_with_get_current_pattern(self, mocker):
        """Test get_property method with get_current_pattern"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._properties, 'get_property', return_value="test_value")
        result = self.element.get_property("test_property")
        assert result == "test_value"
        self.element._properties.get_property.assert_called_once_with("test_property")

    def test_get_property_exception(self, mocker):
        """Test get_property method with exception"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._properties, 'get_property', side_effect=Exception("Property failed"))
        result = self.element.get_property("test_property")
        assert result is None

    def test_get_property_no_pattern_found(self, mocker):
        """Test get_property method when no pattern found"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._properties, 'get_property', return_value=None)
        result = self.element.get_property("test_property")
        assert result is None

    def test_get_attribute_with_current_automation_id(self, mocker):
        """Test get_attribute method with CurrentAutomationId"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'get_property', return_value="test_id")
        result = self.element.get_attribute("automation_id")
        assert result == "test_id"
        self.element.get_property.assert_called_with("AutomationId")

    def test_get_attribute_with_current_name(self, mocker):
        """Test get_attribute method with CurrentName"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'get_property', return_value="test_name")
        result = self.element.get_attribute("name")
        assert result == "test_name"
        self.element.get_property.assert_called_with("Name")

    def test_get_attribute_with_current_class_name(self, mocker):
        """Test get_attribute method with CurrentClassName"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'get_property', return_value="Button")
        result = self.element.get_attribute("class_name")
        assert result == "Button"
        self.element.get_property.assert_called_with("ClassName")

    def test_get_attribute_with_current_control_type(self, mocker):
        """Test get_attribute method with CurrentControlType"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'get_property', return_value="Button")
        result = self.element.get_attribute("control_type")
        assert result == "Button"
        self.element.get_property.assert_called_with("ControlType")

    def test_get_attribute_with_name_property(self, mocker):
        """Test get_attribute method with name property"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'get_property', return_value="test_name")
        result = self.element.get_attribute("name")
        assert result == "test_name"
        self.element.get_property.assert_called_with("Name")

    def test_get_attribute_with_description_property(self, mocker):
        """Test get_attribute method with description property"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'get_property', return_value="test_description")
        result = self.element.get_attribute("description")
        assert result == "test_description"
        self.element.get_property.assert_called_with("HelpText")

    def test_get_attribute_with_get_role_method(self, mocker):
        """Test get_attribute method with get_role method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'get_property', return_value="Button")
        result = self.element.get_attribute("role")
        assert result == "Button"
        self.element.get_property.assert_called_with("ControlType")

    def test_get_attribute_with_get_attribute_method(self, mocker):
        """Test get_attribute method with get_attribute method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'get_property', return_value="test_value")
        result = self.element.get_attribute("custom_attribute")
        assert result == "test_value"
        self.element.get_property.assert_called_with("custom_attribute")

    def test_get_attribute_exception(self, mocker):
        """Test get_attribute method with exception"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'get_property', side_effect=Exception("Attribute failed"))
        result = self.element.get_attribute("test_attribute")
        assert result is None

    def test_get_attributes(self, mocker):
        """Test get_attributes method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element, 'get_attribute', side_effect=lambda x: {"name": "test", "id": "123"}.get(x))
        result = self.element.get_attributes(["name", "id"])
        assert result == {"name": "test", "id": "123"}

    def test_wait_until_clickable(self, mocker):
        """Test wait_until_clickable method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._wait_service, 'wait_until_clickable', return_value=True)
        result = self.element.wait_until_clickable()
        assert result is True
        self.element._wait_service.wait_until_clickable.assert_called_once()

    def test_wait_until_enabled(self, mocker):
        """Test wait_until_enabled method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._wait_service, 'wait_until_enabled', return_value=True)
        result = self.element.wait_until_enabled()
        assert result is True
        self.element._wait_service.wait_until_enabled.assert_called_once()

    def test_wait_until_checked(self, mocker):
        """Test wait_until_checked method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._wait_service, 'wait_until_checked', return_value=True)
        result = self.element.wait_until_checked()
        assert result is True
        self.element._wait_service.wait_until_checked.assert_called_once()

    def test_wait_until_unchecked(self, mocker):
        """Test wait_until_unchecked method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._wait_service, 'wait_until_unchecked', return_value=True)
        result = self.element.wait_until_unchecked()
        assert result is True
        self.element._wait_service.wait_until_unchecked.assert_called_once()

    def test_wait_until_expanded(self, mocker):
        """Test wait_until_expanded method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._wait_service, 'wait_until_expanded', return_value=True)
        result = self.element.wait_until_expanded()
        assert result is True
        self.element._wait_service.wait_until_expanded.assert_called_once()

    def test_wait_until_collapsed(self, mocker):
        """Test wait_until_collapsed method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._wait_service, 'wait_until_collapsed', return_value=True)
        result = self.element.wait_until_collapsed()
        assert result is True
        self.element._wait_service.wait_until_collapsed.assert_called_once()

    def test_wait_until_value_is(self, mocker):
        """Test wait_until_value_is method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._wait_service, 'wait_until_value_is', return_value=True)
        result = self.element.wait_until_value_is("test_value")
        assert result is True
        self.element._wait_service.wait_until_value_is.assert_called_once_with("test_value")

    def test_wait_for_visible(self, mocker):
        """Test wait_for_visible method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._wait_service, 'wait_for_visible', return_value=True)
        result = self.element.wait_for_visible()
        assert result is True
        self.element._wait_service.wait_for_visible.assert_called_once()

    def test_wait_for_visible_exception(self, mocker):
        """Test wait_for_visible method with exception"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._wait_service, 'wait_for_visible', side_effect=Exception("Wait failed"))
        result = self.element.wait_for_visible()
        assert result is False

    def test_wait_for_enabled(self, mocker):
        """Test wait_for_enabled method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._wait_service, 'wait_for_enabled', return_value=True)
        result = self.element.wait_for_enabled()
        assert result is True
        self.element._wait_service.wait_for_enabled.assert_called_once()

    def test_wait_for_condition(self, mocker):
        """Test wait_for_condition method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._wait_service, 'wait_for_condition', return_value=True)
        condition = mocker.Mock()
        result = self.element.wait_for_condition(condition)
        assert result is True
        self.element._wait_service.wait_for_condition.assert_called_once_with(condition)

    def test_wait_for_condition_exception(self, mocker):
        """Test wait_for_condition method with exception"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._wait_service, 'wait_for_condition', side_effect=Exception("Wait failed"))
        condition = mocker.Mock()
        result = self.element.wait_for_condition(condition)
        assert result is False

    def test_get_state_summary(self, mocker):
        """Test get_state_summary method"""
        self.mock_session = mocker.Mock()
        self.mock_native_element = mocker.Mock()
        self.element = BaseElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.element._state_service, 'get_state_summary', return_value={"enabled": True, "visible": True})
        result = self.element.get_state_summary()
        assert result == {"enabled": True, "visible": True}
        self.element._state_service.get_state_summary.assert_called_once() 