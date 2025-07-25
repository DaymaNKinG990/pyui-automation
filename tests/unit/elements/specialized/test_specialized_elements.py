"""
Tests for specialized UI elements
"""
import pytest

from pyui_automation.elements.specialized.text_element import TextElement
from pyui_automation.elements.specialized.checkbox_element import CheckboxElement
from pyui_automation.elements.specialized.dropdown_element import DropdownElement
from pyui_automation.elements.specialized.input_element import InputElement
from pyui_automation.elements.specialized.window_element import WindowElement


class TestTextElement:
    """Test TextElement class"""
    
    def __init__(self):
        """Initialize test attributes"""
        self.mock_native_element = None
        self.mock_session = None
        self.text_element = None
    
    def test_get_text_content(self, mocker):
        """Test get_text_content method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.text_element = TextElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.text_element, 'get_attribute', return_value="Sample text")
        result = self.text_element.get_text_content()
        assert result == "Sample text"

    def test_get_text_length(self, mocker):
        """Test get_text_length method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.text_element = TextElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.text_element, 'get_attribute', return_value="Hello World")
        result = self.text_element.get_text_length()
        assert result == 11

    def test_is_text_empty(self, mocker):
        """Test is_text_empty method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.text_element = TextElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.text_element, 'get_attribute', return_value="")
        result = self.text_element.is_text_empty()
        assert result is True

    def test_is_text_visible(self, mocker):
        """Test is_text_visible method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.text_element = TextElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.text_element, 'is_displayed', return_value=True)
        result = self.text_element.is_text_visible()
        assert result is True

    def test_get_text_bounds(self, mocker):
        """Test get_text_bounds method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.text_element = TextElement(self.mock_native_element, self.mock_session)
        # Mock the native element properties
        mock_rect = mocker.Mock()
        mock_rect.left = 100
        mock_rect.top = 200
        mock_rect.width = 150
        mock_rect.height = 25
        self.mock_native_element.CurrentBoundingRectangle = mock_rect
        result = self.text_element.get_text_bounds()
        assert result['x'] == 100
        assert result['y'] == 200
        assert result['width'] == 150
        assert result['height'] == 25

    def test_get_text_state(self, mocker):
        """Test get_text_state method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.text_element = TextElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.text_element, 'get_attribute', return_value="Test Text")
        mocker.patch.object(self.text_element, 'is_displayed', return_value=True)
        # Mock the native element properties
        mock_rect = mocker.Mock()
        mock_rect.left = 100
        mock_rect.top = 200
        mock_rect.width = 150
        mock_rect.height = 25
        self.mock_native_element.CurrentBoundingRectangle = mock_rect
        state = self.text_element.get_text_state()
        assert state['content'] == "Test Text"
        assert state['visible'] is True


class TestCheckboxElement:
    """Test CheckboxElement class"""
    
    def __init__(self):
        """Initialize test attributes"""
        self.mock_native_element = None
        self.mock_session = None
        self.checkbox = None
    
    def test_get_checked_state(self, mocker):
        """Test get_checked_state method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.checkbox = CheckboxElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.checkbox, 'get_property', return_value=True)
        result = self.checkbox.get_checked_state()
        assert result is True
        self.checkbox.get_property.assert_called_with("IsChecked")

    def test_check_when_unchecked(self, mocker):
        """Test check method when checkbox is unchecked"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.checkbox = CheckboxElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.checkbox, 'get_property', return_value=False)
        mocker.patch.object(self.checkbox, 'click')
        self.checkbox.check()
        self.checkbox.click.assert_called_once()

    def test_check_when_already_checked(self, mocker):
        """Test check method when checkbox is already checked"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.checkbox = CheckboxElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.checkbox, 'get_property', return_value=True)
        mocker.patch.object(self.checkbox, 'click')
        self.checkbox.check()
        self.checkbox.click.assert_not_called()

    def test_uncheck_when_checked(self, mocker):
        """Test uncheck method when checkbox is checked"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.checkbox = CheckboxElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.checkbox, 'get_property', return_value=True)
        mocker.patch.object(self.checkbox, 'click')
        self.checkbox.uncheck()
        self.checkbox.click.assert_called_once()

    def test_uncheck_when_already_unchecked(self, mocker):
        """Test uncheck method when checkbox is already unchecked"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.checkbox = CheckboxElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.checkbox, 'get_property', return_value=False)
        mocker.patch.object(self.checkbox, 'click')
        self.checkbox.uncheck()
        self.checkbox.click.assert_not_called()

    def test_toggle(self, mocker):
        """Test toggle method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.checkbox = CheckboxElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.checkbox, 'click')
        self.checkbox.toggle()
        self.checkbox.click.assert_called_once()

    def test_get_checkbox_state(self, mocker):
        """Test get_checkbox_state method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.checkbox = CheckboxElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.checkbox, 'get_checked_state', return_value=True)
        state = self.checkbox.get_checkbox_state()
        assert state['checked'] is True


class TestDropdownElement:
    """Test DropdownElement class"""
    
    def __init__(self):
        """Initialize test attributes"""
        self.mock_native_element = None
        self.mock_session = None
        self.dropdown = None
    
    def test_expand_when_not_expanded(self, mocker):
        """Test expand method when dropdown is not expanded"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.dropdown, 'get_property', return_value=False)
        mocker.patch.object(self.dropdown, 'click')
        self.dropdown.expand()
        self.dropdown.click.assert_called_once()

    def test_expand_when_already_expanded(self, mocker):
        """Test expand method when dropdown is already expanded"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.dropdown, 'get_property', return_value=True)
        mocker.patch.object(self.dropdown, 'click')
        self.dropdown.expand()
        self.dropdown.click.assert_not_called()

    def test_collapse_when_expanded(self, mocker):
        """Test collapse method when dropdown is expanded"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.dropdown, 'get_property', return_value=True)
        mocker.patch.object(self.dropdown, 'click')
        self.dropdown.collapse()
        self.dropdown.click.assert_called_once()

    def test_collapse_when_already_collapsed(self, mocker):
        """Test collapse method when dropdown is already collapsed"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.dropdown, 'get_property', return_value=False)
        mocker.patch.object(self.dropdown, 'click')
        self.dropdown.collapse()
        self.dropdown.click.assert_not_called()

    def test_toggle_expansion(self, mocker):
        """Test toggle_expansion method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.dropdown, 'click')
        self.dropdown.toggle_expansion()
        self.dropdown.click.assert_called_once()

    def test_get_all_items(self, mocker):
        """Test get_all_items method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        mock_items = [mocker.Mock(), mocker.Mock(), mocker.Mock()]
        # Mock text property for each item
        mock_items[0].text = "Item 1"
        mock_items[1].text = "Item 2"
        mock_items[2].text = "Item 3"
        mocker.patch.object(self.dropdown, 'get_children', return_value=mock_items)
        result = self.dropdown.get_all_items()
        assert result == ["Item 1", "Item 2", "Item 3"]

    def test_select_item_success(self, mocker):
        # Arrange
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        mock_item = mocker.Mock()
        mock_item.click = mocker.Mock()
        mocker.patch.object(self.dropdown, 'expand')
        mocker.patch.object(self.dropdown, 'find_child_by_text', return_value=mock_item)

        # Act
        self.dropdown.select_item("Item 1")

        # Assert
        self.dropdown.expand.assert_called_once()
        self.dropdown.find_child_by_text.assert_called_once_with("Item 1")
        mock_item.click.assert_called_once()

    def test_select_item_not_found(self, mocker):
        """Test select_item method when item is not found"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.dropdown, 'expand')
        mocker.patch.object(self.dropdown, 'find_child_by_text', return_value=None)
        
        with pytest.raises(ValueError, match="Item 'Non-existent Item' not found in dropdown"):
            self.dropdown.select_item("Non-existent Item")

    def test_select_item_by_index_success(self, mocker):
        """Test select_item_by_index method with successful selection"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        mock_items = [mocker.Mock(), mocker.Mock(), mocker.Mock()]
        mocker.patch.object(self.dropdown, 'expand')
        mocker.patch.object(self.dropdown, 'get_all_items', return_value=mock_items)
        mocker.patch.object(self.dropdown, 'click')
        result = self.dropdown.select_item_by_index(1)
        assert result is True

    def test_select_item_by_index_out_of_range(self, mocker):
        """Test select_item_by_index method with out of range index"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.dropdown, 'expand')
        mocker.patch.object(self.dropdown, 'get_all_items', return_value=[mocker.Mock()])
        result = self.dropdown.select_item_by_index(5)
        assert result is False

    def test_get_selected_item(self, mocker):
        """Test get_selected_item method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        mock_selected_item = mocker.Mock()
        mocker.patch.object(self.dropdown, 'get_property', return_value=mock_selected_item)
        result = self.dropdown.get_selected_item()
        assert result == mock_selected_item

    def test_get_dropdown_state(self, mocker):
        """Test get_dropdown_state method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.dropdown, 'get_property', return_value=False)
        state = self.dropdown.get_dropdown_state()
        assert state['expanded'] is False


class TestInputElement:
    """Test InputElement class"""
    
    def __init__(self):
        """Initialize test attributes"""
        self.mock_native_element = None
        self.mock_session = None
        self.input_element = None
    
    def test_type_text_with_clear(self, mocker):
        """Test type_text method with clear=True"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.input_element = InputElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.input_element, 'clear')
        mocker.patch.object(self.input_element, 'send_keys')
        self.input_element.type_text("test")
        self.input_element.clear.assert_called_once()
        self.input_element.send_keys.assert_called_once_with("test")

    def test_type_text_without_clear(self, mocker):
        """Test type_text method with clear=False"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.input_element = InputElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.input_element, 'clear')
        mocker.patch.object(self.input_element, 'send_keys')
        self.input_element.type_text("test", clear=False)
        self.input_element.clear.assert_not_called()
        self.input_element.send_keys.assert_called_once_with("test")

    def test_append_text(self, mocker):
        """Test append_text method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.input_element = InputElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.input_element, 'append')
        self.input_element.append_text("appended")
        self.input_element.append.assert_called_once_with("appended")

    def test_clear_and_type(self, mocker):
        """Test clear_and_type method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.input_element = InputElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.input_element, 'clear')
        mocker.patch.object(self.input_element, 'send_keys')
        self.input_element.clear_and_type("new text")
        self.input_element.clear.assert_called_once()
        self.input_element.send_keys.assert_called_once_with("new text")

    def test_get_input_value(self, mocker):
        """Test get_input_value method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.input_element = InputElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.input_element, 'get_attribute', return_value="input value")
        result = self.input_element.get_input_value()
        assert result == "input value"

    def test_get_input_value_empty(self, mocker):
        """Test get_input_value method when input is empty"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.input_element = InputElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.input_element, 'get_attribute', return_value="")
        result = self.input_element.get_input_value()
        assert result == ""

    def test_set_input_value(self, mocker):
        """Test set_input_value method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.input_element = InputElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.input_element, 'send_keys')
        self.input_element.set_input_value("new value")
        self.input_element.send_keys.assert_called_once_with("new value")

    def test_is_input_empty(self, mocker):
        """Test is_input_empty method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.input_element = InputElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.input_element, 'get_input_value', return_value="")
        result = self.input_element.is_input_empty()
        assert result is True

    def test_is_input_focused(self, mocker):
        """Test is_input_focused method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.input_element = InputElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.input_element, 'get_property', return_value=True)
        result = self.input_element.is_input_focused()
        assert result is True
        self.input_element.get_property.assert_called_with("HasKeyboardFocus")

    def test_focus_input(self, mocker):
        """Test focus_input method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.input_element = InputElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.input_element, 'focus')
        self.input_element.focus_input()
        self.input_element.focus.assert_called_once()


class TestWindowElement:
    """Test WindowElement class"""
    
    def __init__(self):
        """Initialize test attributes"""
        self.mock_native_element = None
        self.mock_session = None
        self.window = None
    
    def test_get_window_title(self, mocker):
        """Test get_window_title method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.window = WindowElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.window, 'get_attribute', return_value="Test Window")
        result = self.window.get_window_title()
        assert result == "Test Window"

    def test_get_window_bounds(self, mocker):
        """Test get_window_bounds method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.window = WindowElement(self.mock_native_element, self.mock_session)
        # Mock the native element properties
        mock_rect = mocker.Mock()
        mock_rect.left = 100
        mock_rect.top = 200
        mock_rect.width = 800
        mock_rect.height = 600
        self.mock_native_element.CurrentBoundingRectangle = mock_rect
        result = self.window.get_window_bounds()
        assert result['x'] == 100
        assert result['y'] == 200
        assert result['width'] == 800
        assert result['height'] == 600

    def test_get_window_position(self, mocker):
        """Test get_window_position method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.window = WindowElement(self.mock_native_element, self.mock_session)
        # Mock the native element properties
        mock_rect = mocker.Mock()
        mock_rect.left = 100
        mock_rect.top = 200
        self.mock_native_element.CurrentBoundingRectangle = mock_rect
        result = self.window.get_window_position()
        assert result['x'] == 100
        assert result['y'] == 200

    def test_get_window_size(self, mocker):
        """Test get_window_size method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.window = WindowElement(self.mock_native_element, self.mock_session)
        # Mock the native element properties
        mock_rect = mocker.Mock()
        mock_rect.width = 800
        mock_rect.height = 600
        self.mock_native_element.CurrentBoundingRectangle = mock_rect
        result = self.window.get_window_size()
        assert result['width'] == 800
        assert result['height'] == 600

    def test_is_window_active(self, mocker):
        """Test is_window_active method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.window = WindowElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.window, 'get_property', return_value=True)
        result = self.window.is_window_active()
        assert result is True
        self.window.get_property.assert_called_with("IsKeyboardFocusable")

    def test_is_window_maximized(self, mocker):
        """Test is_window_maximized method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.window = WindowElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.window, 'get_property', return_value=True)
        result = self.window.is_window_maximized()
        assert result is True
        self.window.get_property.assert_called_with("IsMaximized")

    def test_is_window_minimized(self, mocker):
        """Test is_window_minimized method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.window = WindowElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.window, 'get_property', return_value=True)
        result = self.window.is_window_minimized()
        assert result is True
        self.window.get_property.assert_called_with("IsMinimized")

    def test_activate_window(self, mocker):
        """Test activate_window method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.window = WindowElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.window, 'focus')
        self.window.activate_window()
        self.window.focus.assert_called_once()

    def test_maximize_window_when_not_maximized(self, mocker):
        """Test maximize_window method when window is not maximized"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.window = WindowElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.window, 'get_property', return_value=False)
        mocker.patch.object(self.window, 'send_keys')
        self.window.maximize_window()
        self.window.send_keys.assert_called_once_with("F11")

    def test_maximize_window_when_already_maximized(self, mocker):
        """Test maximize_window method when window is already maximized"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.window = WindowElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.window, 'get_property', return_value=True)
        mocker.patch.object(self.window, 'send_keys')
        self.window.maximize_window()
        self.window.send_keys.assert_not_called()

    def test_minimize_window(self, mocker):
        """Test minimize_window method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.window = WindowElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.window, 'send_keys')
        self.window.minimize_window()
        self.window.send_keys.assert_called_once_with("F9")

    def test_close_window(self, mocker):
        """Test close_window method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.window = WindowElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.window, 'send_keys')
        self.window.close_window()
        self.window.send_keys.assert_called_once_with("Alt+F4")


class TestSpecializedElementsIntegration:
    """Test integration between specialized elements"""
    
    def __init__(self):
        """Initialize test attributes"""
        self.mock_native_element = None
        self.mock_session = None
        self.text_element = None
        self.checkbox = None
        self.dropdown = None
        self.input_element = None
        self.window = None
    
    def test_all_elements_inherit_from_base_element(self, mocker):
        """Test that all specialized elements inherit from BaseElement"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.text_element = TextElement(self.mock_native_element, self.mock_session)
        self.checkbox = CheckboxElement(self.mock_native_element, self.mock_session)
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        self.input_element = InputElement(self.mock_native_element, self.mock_session)
        self.window = WindowElement(self.mock_native_element, self.mock_session)
        
        from pyui_automation.elements.base_element import BaseElement
        
        assert isinstance(self.text_element, BaseElement)
        assert isinstance(self.checkbox, BaseElement)
        assert isinstance(self.dropdown, BaseElement)
        assert isinstance(self.input_element, BaseElement)
        assert isinstance(self.window, BaseElement)

    def test_elements_delegate_to_base_methods(self, mocker):
        """Test that elements delegate to base methods"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.text_element = TextElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.text_element, 'get_attribute', return_value="test")
        result = self.text_element.get_text_content()
        assert result == "test"
        self.text_element.get_attribute.assert_called_with("name")

    def test_elements_use_correct_property_names(self, mocker):
        """Test that elements use correct property names"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.checkbox = CheckboxElement(self.mock_native_element, self.mock_session)
        self.dropdown = DropdownElement(self.mock_native_element, self.mock_session)
        
        mocker.patch.object(self.checkbox, 'get_checked_state', return_value=True)
        state = self.checkbox.get_checkbox_state()
        assert 'checked' in state
        assert state['checked'] is True
        
        mocker.patch.object(self.dropdown, 'get_property', return_value=False)
        state = self.dropdown.get_dropdown_state()
        assert 'expanded' in state
        assert state['expanded'] is False 