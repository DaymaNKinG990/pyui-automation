"""
Tests for BaseElement class
"""
import pytest
import numpy as np
from unittest.mock import Mock

from pyui_automation.elements.base_element import BaseElement


@pytest.fixture
def base_element(mock_session, mock_native_element):
    """Fixture for BaseElement instance"""
    return BaseElement(mock_native_element, mock_session)


class TestBaseElement:
    """Test BaseElement class"""
    
    def test_init(self, mock_session, mock_native_element):
        """Test BaseElement initialization"""
        element = BaseElement(mock_native_element, mock_session)
        assert element._element == mock_native_element
        assert element._session == mock_session
        assert element._interaction_service is not None
        assert element._search_service is not None
        assert element._state_service is not None
        assert element._wait_service is not None
        assert element._properties is not None

    def test_native_element_property(self, base_element, mock_native_element):
        """Test native_element property"""
        assert base_element.native_element == mock_native_element

    def test_session_property(self, base_element, mock_session):
        """Test session property"""
        assert base_element.session == mock_session

    def test_automation_id_property(self, base_element, mock_native_element):
        """Test automation_id property"""
        mock_native_element.get_attribute.return_value = "test_id"
        assert base_element.automation_id == "test_id"
        mock_native_element.get_attribute.assert_called_with("automation_id")

    def test_name_property(self, base_element, mock_native_element):
        """Test name property"""
        mock_native_element.get_attribute.return_value = "test_name"
        assert base_element.name == "test_name"
        mock_native_element.get_attribute.assert_called_with("name")

    def test_class_name_property(self, base_element, mock_native_element):
        """Test class_name property"""
        mock_native_element.get_attribute.return_value = "Button"
        assert base_element.class_name == "Button"
        mock_native_element.get_attribute.assert_called_with("class_name")

    def test_control_type_property(self, base_element, mock_native_element):
        """Test control_type property"""
        mock_native_element.get_attribute.return_value = "Button"
        assert base_element.control_type == "Button"
        mock_native_element.get_attribute.assert_called_with("controlType")

    def test_text_property(self, base_element, mock_native_element):
        """Test text property"""
        mock_native_element.get_attribute.return_value = "Click me"
        assert base_element.text == "Click me"

    def test_value_property_getter(self, base_element, mock_native_element):
        """Test value property getter"""
        mock_native_element.get_attribute.return_value = "test_value"
        assert base_element.value == "test_value"
        mock_native_element.get_attribute.assert_called_with("value")

    def test_value_property_setter(self, base_element, mock_native_element):
        """Test value property setter"""
        test_value = "new_value"
        base_element.value = test_value

    def test_location_property_with_current_bounding_rectangle(self, base_element, mock_native_element):
        """Test location property with current bounding rectangle"""
        # Setup mock rectangle
        mock_rect = Mock()
        mock_rect.left = 10
        mock_rect.top = 20
        mock_native_element.CurrentBoundingRectangle = mock_rect
        
        location = base_element.location
        assert location == {"x": 10, "y": 20}

    def test_size_property_with_current_bounding_rectangle(self, base_element, mock_native_element):
        """Test size property with current bounding rectangle"""
        mock_rect = Mock()
        mock_rect.width = 100
        mock_rect.height = 50
        mock_native_element.CurrentBoundingRectangle = mock_rect
        size = base_element.size
        assert size == {"width": 100, "height": 50}

    def test_is_pressed(self, base_element, mocker):
        """Test is_pressed property"""
        mocker.patch.object(base_element._state_service, 'is_pressed', return_value=True)
        assert base_element.is_pressed() is True

    def test_is_pressed_false(self, base_element, mocker):
        """Test is_pressed property when false"""
        mocker.patch.object(base_element._state_service, 'is_pressed', return_value=False)
        assert base_element.is_pressed() is False

    def test_click(self, base_element, mocker):
        """Test click method"""
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        base_element.click()
        mock_interaction.click.assert_called()

    def test_double_click(self, base_element, mocker):
        """Test double_click method"""
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        base_element.double_click()
        mock_interaction.double_click.assert_called()

    def test_right_click(self, base_element, mocker):
        """Test right_click method"""
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        base_element.right_click()
        mock_interaction.right_click.assert_called()

    def test_hover(self, base_element, mocker):
        """Test hover method"""
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        base_element.hover()
        mock_interaction.hover.assert_called()

    def test_focus(self, base_element, mocker):
        """Test focus method"""
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        base_element.focus()
        mock_interaction.focus.assert_called()

    def test_send_keys(self, base_element, mocker):
        """Test send_keys method"""
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        test_text = "Hello World"
        base_element.send_keys(test_text)
        mock_interaction.send_keys.assert_called()

    def test_send_keys_with_interval(self, base_element, mocker):
        """Test send_keys method with interval"""
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        test_text = "Hello World"
        base_element.send_keys(test_text, interval=0.1)
        mock_interaction.send_keys.assert_called()

    def test_clear(self, base_element, mocker):
        """Test clear method"""
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        base_element.clear()
        mock_interaction.clear.assert_called()

    def test_select_all(self, base_element, mocker):
        """Test select_all method"""
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        base_element.select_all()
        mock_interaction.select_all.assert_called()

    def test_copy(self, base_element, mocker):
        """Test copy method"""
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        base_element.copy()
        mock_interaction.copy.assert_called()

    def test_paste(self, base_element, mocker):
        """Test paste method"""
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        base_element.paste()
        mock_interaction.paste.assert_called()

    def test_append(self, base_element, mocker):
        """Test append method"""
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        test_text = "Additional text"
        base_element.append(test_text)
        mock_interaction.append.assert_called()

    def test_check(self, base_element, mocker):
        """Test check method"""
        mock_state = mocker.patch.object(base_element, '_state_service')
        base_element.check()
        mock_state.check.assert_called()

    def test_uncheck(self, base_element, mocker):
        """Test uncheck method"""
        mock_state = mocker.patch.object(base_element, '_state_service')
        base_element.uncheck()
        mock_state.uncheck.assert_called()

    def test_toggle(self, base_element, mocker):
        """Test toggle method"""
        mock_state = mocker.patch.object(base_element, '_state_service')
        base_element.toggle()
        mock_state.toggle.assert_called()

    def test_expand(self, base_element, mocker):
        """Test expand method"""
        mock_state = mocker.patch.object(base_element, '_state_service')
        base_element.expand()
        mock_state.expand.assert_called()

    def test_collapse(self, base_element, mocker):
        """Test collapse method"""
        mock_state = mocker.patch.object(base_element, '_state_service')
        base_element.collapse()
        mock_state.collapse.assert_called()

    def test_select_item(self, base_element, mocker):
        """Test select_item method"""
        mock_state = mocker.patch.object(base_element, '_state_service')
        test_item = "Test Item"
        base_element.select_item(test_item)
        mock_state.select_item.assert_called()

    def test_is_selected(self, base_element, mocker):
        """Test is_selected property"""
        mocker.patch.object(base_element._state_service, 'is_selected', return_value=True)
        assert base_element.is_selected() is True

    def test_take_screenshot(self, base_element, mocker):
        """Test take_screenshot method"""
        mock_screenshot = np.array([[1, 2], [3, 4]], dtype=np.uint8)
        mocker.patch.object(base_element, 'capture_screenshot', return_value=mock_screenshot)
        result = base_element.take_screenshot()
        assert result is not None
        assert isinstance(result, np.ndarray)

    def test_capture_screenshot_with_session_service(self, base_element, mock_session, mocker):
        """Test capture_screenshot with session screenshot service"""
        mock_image = np.array([[1, 2], [3, 4]], dtype=np.uint8)
        mock_session.screenshot_service = Mock()
        mock_session.screenshot_service.capture_element_screenshot.return_value = mock_image
        result = base_element.capture_screenshot()
        assert result is not None
        assert isinstance(result, np.ndarray)

    def test_scroll_into_view_success(self, base_element, mocker):
        """Test scroll_into_view success"""
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        base_element.scroll_into_view()
        mock_interaction.scroll_into_view.assert_called()

    def test_safe_click_success(self, base_element, mocker):
        """Test safe_click success"""
        mock_wait = mocker.patch.object(base_element, '_wait_service')
        mock_interaction = mocker.patch.object(base_element, '_interaction_service')
        mock_wait.wait_until_clickable.return_value = True
        result = base_element.safe_click()
        assert result is True
        mock_interaction.click.assert_called()

    def test_safe_click_not_clickable(self, base_element, mocker):
        """Test safe_click when element is not clickable"""
        mock_wait = mocker.patch.object(base_element, '_wait_service')
        mock_wait.wait_until_clickable.return_value = False
        result = base_element.safe_click()
        assert result is False

    def test_drag_and_drop_invalid_target(self, base_element, mocker):
        """Test drag_and_drop with invalid target"""
        mocker.patch.object(base_element, '_interaction_service')
        with pytest.raises(ValueError):
            base_element.drag_and_drop(None)

    def test_get_property_with_get_current_pattern(self, base_element, mock_native_element, mocker):
        """Test get_property with get_current_pattern"""
        mock_pattern = Mock()
        mock_pattern.get_property.return_value = "test_value"
        mock_native_element.GetCurrentPattern.return_value = mock_pattern
        result = base_element.get_property("test_property")
        assert result == "test_value"

    def test_get_property_no_pattern_found(self, base_element, mock_native_element):
        """Test get_property when no pattern found"""
        mock_native_element.GetCurrentPattern.return_value = None
        mock_native_element.get_property = None
        result = base_element.get_property("test_property")
        assert result is None

    def test_get_attribute_with_current_automation_id(self, base_element, mock_native_element):
        """Test get_attribute with current automation id"""
        mock_native_element.CurrentAutomationId = "test_id"
        # Remove get_attribute to force using CurrentAutomationId
        mock_native_element.get_attribute = None
        result = base_element.get_attribute("automation_id")
        assert result == "test_id"

    def test_get_attribute_with_current_name(self, base_element, mock_native_element):
        """Test get_attribute with current name"""
        mock_native_element.CurrentName = "test_name"
        # Remove get_attribute to force using CurrentName
        mock_native_element.get_attribute = None
        result = base_element.get_attribute("name")
        assert result == "test_name"

    def test_get_attribute_with_current_class_name(self, base_element, mock_native_element):
        """Test get_attribute with current class name"""
        mock_native_element.CurrentClassName = "Button"
        # Remove get_attribute to force using CurrentClassName
        mock_native_element.get_attribute = None
        result = base_element.get_attribute("class_name")
        assert result == "Button"

    def test_get_attribute_with_current_control_type(self, base_element, mock_native_element):
        """Test get_attribute with current control type"""
        mock_native_element.CurrentControlType = "Button"
        # Remove get_attribute to force using CurrentControlType
        mock_native_element.get_attribute = None
        result = base_element.get_attribute("control_type")
        assert result == "Button"

    def test_get_attribute_with_name_property(self, base_element, mock_native_element):
        """Test get_attribute with name property"""
        mock_native_element.Name = "test_name"
        # Remove get_attribute to force using name property
        mock_native_element.get_attribute = None
        result = base_element.get_attribute("name")
        assert result == "test_name"

    def test_get_attribute_with_description_property(self, base_element, mock_native_element):
        """Test get_attribute with description property"""
        mock_native_element.Description = "test_description"
        # Remove get_attribute to force using description property
        mock_native_element.get_attribute = None
        result = base_element.get_attribute("description")
        assert result == "test_description"

    def test_get_attribute_with_get_role_method(self, base_element, mock_native_element):
        """Test get_attribute with get_role method"""
        mock_native_element.getRole = Mock(return_value="Button")
        # Remove get_attribute to force using getRole method
        mock_native_element.get_attribute = None
        result = base_element.get_attribute("role")
        assert result == "Button"

    def test_get_attribute_with_get_attribute_method(self, base_element, mock_native_element):
        """Test get_attribute with get_attribute method"""
        mock_native_element.get_attribute.return_value = "test_value"
        result = base_element.get_attribute("custom_attribute")
        assert result == "test_value"

    def test_get_attributes(self, base_element, mocker):
        """Test get_attributes method"""
        def mock_get_attribute(name):
            if name == "name":
                return "test"
            elif name == "id":
                return "123"
            return None
            
        mocker.patch.object(base_element, 'get_attribute', side_effect=mock_get_attribute)
        result = base_element.get_attributes(["name", "id"])
        assert result == {"name": "test", "id": "123"}

    def test_wait_until_clickable(self, base_element, mocker):
        """Test wait_until_clickable method"""
        mock_wait = mocker.patch.object(base_element, '_wait_service')
        mock_wait.wait_until_clickable.return_value = True
        result = base_element.wait_until_clickable()
        assert result is True

    def test_wait_until_enabled(self, base_element, mocker):
        """Test wait_until_enabled method"""
        mock_wait = mocker.patch.object(base_element, '_wait_service')
        mock_wait.wait_until_enabled.return_value = True
        result = base_element.wait_until_enabled()
        assert result is True

    def test_wait_until_checked(self, base_element, mocker):
        """Test wait_until_checked method"""
        mock_wait = mocker.patch.object(base_element, '_wait_service')
        mock_wait.wait_until_checked.return_value = True
        result = base_element.wait_until_checked()
        assert result is True

    def test_wait_until_unchecked(self, base_element, mocker):
        """Test wait_until_unchecked method"""
        mock_wait = mocker.patch.object(base_element, '_wait_service')
        mock_wait.wait_until_unchecked.return_value = True
        result = base_element.wait_until_unchecked()
        assert result is True

    def test_wait_until_expanded(self, base_element, mocker):
        """Test wait_until_expanded method"""
        mock_wait = mocker.patch.object(base_element, '_wait_service')
        mock_wait.wait_until_expanded.return_value = True
        result = base_element.wait_until_expanded()
        assert result is True

    def test_wait_until_collapsed(self, base_element, mocker):
        """Test wait_until_collapsed method"""
        mock_wait = mocker.patch.object(base_element, '_wait_service')
        mock_wait.wait_until_collapsed.return_value = True
        result = base_element.wait_until_collapsed()
        assert result is True

    def test_wait_until_value_is(self, base_element, mocker):
        """Test wait_until_value_is method"""
        mock_wait = mocker.patch.object(base_element, '_wait_service')
        mock_wait.wait_until_value_is.return_value = True
        test_value = "expected_value"
        result = base_element.wait_until_value_is(test_value)
        assert result is True

    def test_wait_for_visible(self, base_element, mocker):
        """Test wait_for_visible method"""
        mock_wait = mocker.patch.object(base_element, '_wait_service')
        mock_wait.wait_for_condition.return_value = True
        mocker.patch.object(base_element, 'is_displayed', return_value=True)
        result = base_element.wait_for_visible()
        assert result is True

    def test_wait_for_enabled(self, base_element, mocker):
        """Test wait_for_enabled method"""
        mocker.patch.object(base_element, 'wait_until_enabled', return_value=True)
        result = base_element.wait_for_enabled()
        assert result is True

    def test_wait_for_condition(self, base_element, mocker):
        """Test wait_for_condition method"""
        mock_wait = mocker.patch.object(base_element, '_wait_service')
        mock_wait.wait_for_condition.return_value = True
        condition = Mock()
        result = base_element.wait_for_condition(condition)
        assert result is True

    def test_get_state_summary(self, base_element, mocker):
        """Test get_state_summary method"""
        mock_state = mocker.patch.object(base_element, '_state_service')
        mock_state.get_state_summary.return_value = {"enabled": True, "visible": True}
        result = base_element.get_state_summary()
        assert result == {"enabled": True, "visible": True}

    def test_is_displayed(self, base_element, mocker):
        """Test is_displayed method"""
        mocker.patch.object(base_element, 'get_property', return_value=True)
        assert base_element.is_displayed() is True

    def test_is_enabled(self, base_element, mocker):
        """Test is_enabled method"""
        mocker.patch.object(base_element, 'get_property', return_value=True)
        assert base_element.is_enabled() is True

    def test_visible_property(self, base_element, mocker):
        """Test visible property"""
        mocker.patch.object(base_element, 'is_displayed', return_value=True)
        assert base_element.visible is True

    def test_is_checked_property(self, base_element, mocker):
        """Test is_checked property"""
        mocker.patch.object(base_element, 'get_property', return_value=True)
        assert base_element.is_checked is True

    def test_is_expanded_property(self, base_element, mocker):
        """Test is_expanded property"""
        mocker.patch.object(base_element, 'get_property', return_value=True)
        assert base_element.is_expanded is True

    def test_selected_item_property(self, base_element, mocker):
        """Test selected_item property"""
        mocker.patch.object(base_element, 'get_property', return_value="selected")
        assert base_element.selected_item == "selected"

    def test_get_parent(self, base_element, mocker):
        """Test get_parent method"""
        mock_parent = Mock()
        base_element._finder.get_parent.return_value = mock_parent
        result = base_element.get_parent()
        assert result == mock_parent

    def test_get_children(self, base_element, mocker):
        """Test get_children method"""
        mock_children = [Mock(), Mock()]
        base_element._finder.get_children.return_value = mock_children
        result = base_element.get_children()
        assert result == mock_children

    def test_find_child_by_property(self, base_element, mocker):
        """Test find_child_by_property method"""
        mock_child = Mock()
        base_element._finder.find_child_by_property.return_value = mock_child
        result = base_element.find_child_by_property("name", "test")
        assert result == mock_child

    def test_find_children_by_property(self, base_element, mocker):
        """Test find_children_by_property method"""
        mock_children = [Mock(), Mock()]
        base_element._finder.find_children_by_property.return_value = mock_children
        result = base_element.find_children_by_property("name", "test")
        assert result == mock_children

    def test_find_child_by_text(self, base_element, mocker):
        """Test find_child_by_text method"""
        mock_child = Mock()
        base_element._finder.find_child_by_text.return_value = mock_child
        result = base_element.find_child_by_text("test")
        assert result == mock_child

    def test_find_children_by_text(self, base_element, mocker):
        """Test find_children_by_text method"""
        mock_children = [Mock(), Mock()]
        base_element._finder.find_children_by_text.return_value = mock_children
        result = base_element.find_children_by_text("test")
        assert result == mock_children

    def test_find_child_by_name(self, base_element, mocker):
        """Test find_child_by_name method"""
        mock_child = Mock()
        base_element._finder.find_child_by_name.return_value = mock_child
        result = base_element.find_child_by_name("test")
        assert result == mock_child

    def test_find_children_by_name(self, base_element, mocker):
        """Test find_children_by_name method"""
        mock_children = [Mock(), Mock()]
        base_element._finder.find_children_by_name.return_value = mock_children
        result = base_element.find_children_by_name("test")
        assert result == mock_children

    def test_find_child_by_control_type(self, base_element, mocker):
        """Test find_child_by_control_type method"""
        mock_child = Mock()
        base_element._finder.find_child_by_control_type.return_value = mock_child
        result = base_element.find_child_by_control_type("Button")
        assert result == mock_child

    def test_find_children_by_control_type(self, base_element, mocker):
        """Test find_children_by_control_type method"""
        mock_children = [Mock(), Mock()]
        base_element._finder.find_children_by_control_type.return_value = mock_children
        result = base_element.find_children_by_control_type("Button")
        assert result == mock_children

    def test_find_child_by_automation_id(self, base_element, mocker):
        """Test find_child_by_automation_id method"""
        mock_child = Mock()
        base_element._finder.find_child_by_automation_id.return_value = mock_child
        result = base_element.find_child_by_automation_id("test_id")
        assert result == mock_child

    def test_find_children_by_automation_id(self, base_element, mocker):
        """Test find_children_by_automation_id method"""
        mock_children = [Mock(), Mock()]
        base_element._finder.find_children_by_automation_id.return_value = mock_children
        result = base_element.find_children_by_automation_id("test_id")
        assert result == mock_children

    def test_find_visible_children(self, base_element, mocker):
        """Test find_visible_children method"""
        mock_children = [Mock(), Mock()]
        base_element._finder.find_visible_children.return_value = mock_children
        result = base_element.find_visible_children()
        assert result == mock_children

    def test_find_enabled_children(self, base_element, mocker):
        """Test find_enabled_children method"""
        mock_children = [Mock(), Mock()]
        base_element._finder.find_enabled_children.return_value = mock_children
        result = base_element.find_enabled_children()
        assert result == mock_children

    def test_find_child_by_predicate(self, base_element, mocker):
        """Test find_child_by_predicate method"""
        mock_child = Mock()
        
        def predicate(x):
            return True
            
        base_element._finder.find_child_by_predicate.return_value = mock_child
        result = base_element.find_child_by_predicate(predicate)
        assert result == mock_child

    def test_find_children_by_predicate(self, base_element, mocker):
        """Test find_children_by_predicate method"""
        mock_children = [Mock(), Mock()]
        
        def predicate(x):
            return True
            
        base_element._finder.find_children_by_predicate.return_value = mock_children
        result = base_element.find_children_by_predicate(predicate)
        assert result == mock_children

    def test_get_properties(self, base_element, mocker):
        """Test get_properties method"""
        mock_properties = {"name": "test", "id": "123"}
        base_element._properties = mock_properties
        result = base_element.get_properties()
        assert result == mock_properties

    def test_rect_property(self, base_element, mocker):
        """Test rect property"""
        mock_location = {"x": 10, "y": 20}
        mock_size = {"width": 100, "height": 50}
        mocker.patch.object(base_element, 'location', mock_location)
        mocker.patch.object(base_element, 'size', mock_size)
        rect = base_element.rect
        assert rect == {"x": 10, "y": 20, "width": 100, "height": 50}

    def test_center_property(self, base_element, mocker):
        """Test center property"""
        mock_location = {"x": 10, "y": 20}
        mock_size = {"width": 100, "height": 50}
        mocker.patch.object(base_element, 'location', mock_location)
        mocker.patch.object(base_element, 'size', mock_size)
        center = base_element.center
        assert center == {"x": 60, "y": 45} 