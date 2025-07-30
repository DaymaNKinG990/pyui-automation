"""
Tests for specialized UI elements
"""
import pytest

from pyui_automation.elements.specialized.text_element import TextElement
from pyui_automation.elements.specialized.checkbox_element import CheckboxElement
from pyui_automation.elements.specialized.dropdown_element import DropdownElement
from pyui_automation.elements.specialized.input_element import InputElement
from pyui_automation.elements.specialized.window_element import WindowElement
from unittest.mock import Mock


@pytest.fixture
def text_element(mock_session, mock_native_element):
    """Create a TextElement for testing"""
    return TextElement(mock_native_element, mock_session)


@pytest.fixture
def checkbox_element(mock_session, mock_native_element):
    """Create a CheckboxElement for testing"""
    return CheckboxElement(mock_native_element, mock_session)


@pytest.fixture
def dropdown_element(mock_session, mock_native_element):
    """Create a DropdownElement for testing"""
    return DropdownElement(mock_native_element, mock_session)


@pytest.fixture
def input_element(mock_session, mock_native_element):
    """Create an InputElement for testing"""
    return InputElement(mock_native_element, mock_session)


@pytest.fixture
def window_element(mock_session, mock_native_element):
    """Create a WindowElement for testing"""
    return WindowElement(mock_native_element, mock_session)


class TestTextElement:
    """Test TextElement class"""
    
    def test_get_text_content(self, text_element, mocker):
        """Test get_text_content method"""
        mocker.patch.object(text_element, 'get_attribute', return_value="Sample text")
        result = text_element.get_text_content()
        assert result == "Sample text"

    def test_get_text_length(self, text_element, mocker):
        """Test get_text_length method"""
        mocker.patch.object(text_element, 'get_attribute', return_value="Hello World")
        result = text_element.get_text_length()
        assert result == 11

    def test_is_text_empty(self, text_element, mocker):
        """Test is_text_empty method"""
        mocker.patch.object(text_element, 'get_attribute', return_value="")
        result = text_element.is_text_empty()
        assert result is True

    def test_is_text_visible(self, text_element, mocker):
        """Test is_text_visible method"""
        mocker.patch.object(text_element, 'is_displayed', return_value=True)
        result = text_element.is_text_visible()
        assert result is True

    def test_get_text_bounds(self, text_element, mocker):
        """Test get_text_bounds method"""
        # Mock the native element properties
        mock_rect = mocker.Mock()
        mock_rect.left = 100
        mock_rect.top = 200
        mock_rect.width = 150
        mock_rect.height = 25
        text_element.native_element.CurrentBoundingRectangle = mock_rect
        result = text_element.get_text_bounds()
        assert result['x'] == 100
        assert result['y'] == 200
        assert result['width'] == 150
        assert result['height'] == 25

    def test_get_text_state(self, text_element, mocker):
        """Test get_text_state method"""
        mocker.patch.object(text_element, 'get_attribute', return_value="Test Text")
        mocker.patch.object(text_element, 'is_displayed', return_value=True)
        # Mock the native element properties
        mock_rect = mocker.Mock()
        mock_rect.left = 100
        mock_rect.top = 200
        mock_rect.width = 150
        mock_rect.height = 25
        text_element.native_element.CurrentBoundingRectangle = mock_rect
        state = text_element.get_text_state()
        assert state['content'] == "Test Text"
        assert state['visible'] is True


class TestCheckboxElement:
    """Test CheckboxElement class"""
    
    def test_get_checked_state(self, checkbox_element, mocker):
        """Test get_checked_state method"""
        mocker.patch.object(checkbox_element, 'get_property', return_value=True)
        result = checkbox_element.get_checked_state()
        assert result is True

    def test_check_when_unchecked(self, checkbox_element, mocker):
        """Test check method when checkbox is unchecked"""
        mocker.patch.object(checkbox_element, 'get_property', return_value=False)
        mocker.patch.object(checkbox_element, 'click')
        checkbox_element.check()
        checkbox_element.click.assert_called_once()

    def test_check_when_already_checked(self, checkbox_element, mocker):
        """Test check method when already checked"""
        mocker.patch.object(checkbox_element, 'get_property', return_value=True)
        mocker.patch.object(checkbox_element, 'click')
        checkbox_element.check()
        checkbox_element.click.assert_not_called()

    def test_uncheck_when_checked(self, checkbox_element, mocker):
        """Test uncheck method when checked"""
        mocker.patch.object(checkbox_element, 'get_property', return_value=True)
        mocker.patch.object(checkbox_element, 'click')
        checkbox_element.uncheck()
        checkbox_element.click.assert_called_once()

    def test_uncheck_when_already_unchecked(self, checkbox_element, mocker):
        """Test uncheck method when checkbox is already unchecked"""
        mocker.patch.object(checkbox_element, 'get_property', return_value=False)
        mocker.patch.object(checkbox_element, 'click')
        checkbox_element.uncheck()

    def test_toggle(self, checkbox_element, mocker):
        """Test toggle method"""
        mocker.patch.object(checkbox_element, 'get_property', return_value=False)
        mocker.patch.object(checkbox_element, 'click')
        checkbox_element.toggle()
        checkbox_element.click.assert_called_once()

    def test_get_checkbox_state(self, checkbox_element, mocker):
        """Test get_checkbox_state method"""
        mocker.patch.object(checkbox_element, 'get_property', return_value=True)
        result = checkbox_element.get_checkbox_state()
        assert result is True


class TestDropdownElement:
    """Test DropdownElement class"""
    
    def test_expand_when_not_expanded(self, dropdown_element, mocker):
        """Test expand method when dropdown is not expanded"""
        mocker.patch.object(dropdown_element, 'get_property', return_value=False)
        mocker.patch.object(dropdown_element, 'click')
        dropdown_element.expand()

    def test_expand_when_already_expanded(self, dropdown_element, mocker):
        """Test expand method when already expanded"""
        mocker.patch.object(dropdown_element, 'get_property', return_value=True)
        mocker.patch.object(dropdown_element, 'click')
        dropdown_element.expand()
        dropdown_element.click.assert_not_called()

    def test_collapse_when_expanded(self, dropdown_element, mocker):
        """Test collapse method when expanded"""
        mocker.patch.object(dropdown_element, 'get_property', return_value=True)
        mocker.patch.object(dropdown_element, 'click')
        dropdown_element.collapse()
        dropdown_element.click.assert_called_once()

    def test_collapse_when_already_collapsed(self, dropdown_element, mocker):
        """Test collapse method when dropdown is already collapsed"""
        mocker.patch.object(dropdown_element, 'get_property', return_value=False)
        mocker.patch.object(dropdown_element, 'click')
        dropdown_element.collapse()

    def test_toggle_expansion(self, dropdown_element, mocker):
        """Test toggle_expansion method"""
        mocker.patch.object(dropdown_element, 'get_property', return_value=False)
        mocker.patch.object(dropdown_element, 'click')
        dropdown_element.toggle_expansion()
        dropdown_element.click.assert_called_once()

    def test_get_all_items(self, dropdown_element, mocker):
        """Test get_all_items method"""
        mock_items = [Mock(), Mock()]
        mocker.patch.object(dropdown_element, 'get_children', return_value=mock_items)
        result = dropdown_element.get_all_items()
        assert result == mock_items

    def test_select_item_success(self, dropdown_element, mocker):
        """Test select_item method with success"""
        mock_items = [Mock(), Mock()]
        mock_items[0].get_attribute.return_value = "target_item"
        mock_items[1].get_attribute.return_value = "other_item"
        mocker.patch.object(dropdown_element, 'get_children', return_value=mock_items)
        mocker.patch.object(dropdown_element, 'expand')
        mocker.patch.object(mock_items[0], 'click')
        dropdown_element.select_item("target_item")

    def test_select_item_not_found(self, dropdown_element, mocker):
        """Test select_item method when item not found"""
        mock_items = [Mock(), Mock()]
        mock_items[0].get_attribute.return_value = "other_item"
        mock_items[1].get_attribute.return_value = "another_item"
        mocker.patch.object(dropdown_element, 'get_children', return_value=mock_items)
        mocker.patch.object(dropdown_element, 'expand')
        with pytest.raises(ValueError):
            dropdown_element.select_item("nonexistent_item")

    def test_select_item_by_index_success(self, dropdown_element, mocker):
        """Test select_item_by_index method with success"""
        mock_items = [Mock(), Mock()]
        mocker.patch.object(dropdown_element, 'get_children', return_value=mock_items)
        mocker.patch.object(dropdown_element, 'expand')
        mocker.patch.object(mock_items[0], 'click')
        result = dropdown_element.select_item_by_index(0)
        assert result is True

    def test_select_item_by_index_out_of_range(self, dropdown_element, mocker):
        """Test select_item_by_index method with out of range index"""
        mock_items = [mocker.Mock(), mocker.Mock()]
        mocker.patch.object(dropdown_element, 'get_children', return_value=mock_items)
        mocker.patch.object(dropdown_element, 'expand')
        result = dropdown_element.select_item_by_index(5)
        assert result is False

    def test_get_selected_item(self, dropdown_element, mocker):
        """Test get_selected_item method"""
        mocker.patch.object(dropdown_element, 'get_property', return_value="selected_item")
        result = dropdown_element.get_selected_item()
        assert result == "selected_item"

    def test_get_dropdown_state(self, dropdown_element, mocker):
        """Test get_dropdown_state method"""
        mocker.patch.object(dropdown_element, 'get_property', return_value=True)
        result = dropdown_element.get_dropdown_state()
        assert result is True


class TestInputElement:
    """Test InputElement class"""
    
    def test_type_text_with_clear(self, input_element, mocker):
        """Test type_text method with clear"""
        mocker.patch.object(input_element, 'clear')
        mocker.patch.object(input_element, 'send_keys')
        input_element.type_text("test text", clear=True)
        input_element.clear.assert_called_once()
        input_element.send_keys.assert_called_once_with("test text")

    def test_type_text_without_clear(self, input_element, mocker):
        """Test type_text method without clearing"""
        mocker.patch.object(input_element, 'clear')
        mocker.patch.object(input_element, 'send_keys')
        input_element.type_text("new text", clear=False)
        input_element.send_keys.assert_called()

    def test_append_text(self, input_element, mocker):
        """Test append_text method"""
        mocker.patch.object(input_element, 'send_keys')
        input_element.append_text("additional text")
        input_element.send_keys.assert_called()

    def test_clear_and_type(self, input_element, mocker):
        """Test clear_and_type method"""
        mocker.patch.object(input_element, 'clear')
        mocker.patch.object(input_element, 'send_keys')
        input_element.clear_and_type("new text")
        input_element.clear.assert_called_once()
        input_element.send_keys.assert_called_once_with("new text")

    def test_get_input_value(self, input_element, mocker):
        """Test get_input_value method"""
        mocker.patch.object(input_element, 'get_attribute', return_value="input value")
        result = input_element.get_input_value()
        assert result == "input value"

    def test_get_input_value_empty(self, input_element, mocker):
        """Test get_input_value method with empty value"""
        mocker.patch.object(input_element, 'get_attribute', return_value="")
        result = input_element.get_input_value()
        assert result == ""

    def test_set_input_value(self, input_element, mocker):
        """Test set_input_value method"""
        mocker.patch.object(input_element, 'clear')
        mocker.patch.object(input_element, 'send_keys')
        input_element.set_input_value("new value")
        input_element.clear.assert_called_once()
        input_element.send_keys.assert_called_once_with("new value")

    def test_is_input_empty(self, input_element, mocker):
        """Test is_input_empty method"""
        mocker.patch.object(input_element, 'get_attribute', return_value="")
        result = input_element.is_input_empty()
        assert result is True

    def test_is_input_focused(self, input_element, mocker):
        """Test is_input_focused method"""
        mocker.patch.object(input_element, 'get_property', return_value=True)
        result = input_element.is_input_focused()
        assert result is True

    def test_focus_input(self, input_element, mocker):
        """Test focus_input method"""
        mocker.patch.object(input_element, 'focus')
        input_element.focus_input()
        input_element.focus.assert_called_once()


class TestWindowElement:
    """Test WindowElement class"""
    
    def test_get_window_title(self, window_element, mocker):
        """Test get_window_title method"""
        mocker.patch.object(window_element, 'get_attribute', return_value="Window Title")
        result = window_element.get_window_title()
        assert result == "Window Title"

    def test_get_window_bounds(self, window_element, mocker):
        """Test get_window_bounds method"""
        # Mock the native element properties
        mock_rect = mocker.Mock()
        mock_rect.left = 100
        mock_rect.top = 200
        mock_rect.width = 800
        mock_rect.height = 600
        window_element.native_element.CurrentBoundingRectangle = mock_rect
        result = window_element.get_window_bounds()
        assert result['x'] == 100
        assert result['y'] == 200
        assert result['width'] == 800
        assert result['height'] == 600

    def test_get_window_position(self, window_element, mocker):
        """Test get_window_position method"""
        # Mock the native element properties
        mock_rect = mocker.Mock()
        mock_rect.left = 100
        mock_rect.top = 200
        window_element.native_element.CurrentBoundingRectangle = mock_rect
        result = window_element.get_window_position()
        assert result['x'] == 100
        assert result['y'] == 200

    def test_get_window_size(self, window_element, mocker):
        """Test get_window_size method"""
        # Mock the native element properties
        mock_rect = mocker.Mock()
        mock_rect.width = 800
        mock_rect.height = 600
        window_element.native_element.CurrentBoundingRectangle = mock_rect
        result = window_element.get_window_size()
        assert result['width'] == 800
        assert result['height'] == 600

    def test_is_window_active(self, window_element, mocker):
        """Test is_window_active method"""
        mocker.patch.object(window_element, 'get_property', return_value=True)
        result = window_element.is_window_active()
        assert result is True

    def test_is_window_maximized(self, window_element, mocker):
        """Test is_window_maximized method"""
        mocker.patch.object(window_element, 'get_property', return_value=True)
        result = window_element.is_window_maximized()
        assert result is True

    def test_is_window_minimized(self, window_element, mocker):
        """Test is_window_minimized method"""
        mocker.patch.object(window_element, 'get_property', return_value=True)
        result = window_element.is_window_minimized()
        assert result is True

    def test_activate_window(self, window_element, mocker):
        """Test activate_window method"""
        mocker.patch.object(window_element, 'click')
        window_element.activate_window()
        window_element.click.assert_called()

    def test_maximize_window_when_not_maximized(self, window_element, mocker):
        """Test maximize_window method when not maximized"""
        mocker.patch.object(window_element, 'get_property', return_value=False)
        mocker.patch.object(window_element, 'send_keys')
        window_element.maximize_window()
        window_element.send_keys.assert_called()

    def test_maximize_window_when_already_maximized(self, window_element, mocker):
        """Test maximize_window method when already maximized"""
        mocker.patch.object(window_element, 'get_property', return_value=True)
        mocker.patch.object(window_element, 'send_keys')
        window_element.maximize_window()
        window_element.send_keys.assert_not_called()

    def test_minimize_window(self, window_element, mocker):
        """Test minimize_window method"""
        mocker.patch.object(window_element, 'send_keys')
        window_element.minimize_window()
        window_element.send_keys.assert_called_once()

    def test_close_window(self, window_element, mocker):
        """Test close_window method"""
        mocker.patch.object(window_element, 'send_keys')
        window_element.close_window()
        window_element.send_keys.assert_called_once()


class TestSpecializedElementsIntegration:
    """Integration tests for specialized elements"""
    
    def test_all_elements_inherit_from_base_element(self, text_element, checkbox_element, 
                                                   dropdown_element, input_element, window_element):
        """Test that all specialized elements inherit from BaseElement"""
        from pyui_automation.elements.base_element import BaseElement
        
        assert isinstance(text_element, BaseElement)
        assert isinstance(checkbox_element, BaseElement)
        assert isinstance(dropdown_element, BaseElement)
        assert isinstance(input_element, BaseElement)
        assert isinstance(window_element, BaseElement)

    def test_elements_delegate_to_base_methods(self, text_element, mocker):
        """Test that elements delegate to base methods"""
        mocker.patch.object(text_element, 'get_attribute', return_value="test")
        result = text_element.get_text_content()
        assert result == "test"

    def test_elements_use_correct_property_names(self, text_element, mock_native_element):
        """Test that elements use correct property names"""
        assert text_element.native_element == mock_native_element 