"""
Tests for ElementFactory class
"""
import pytest

from pyui_automation.elements.element_factory import (
    ElementFactory, ButtonElement, CheckboxElement, TextElement, 
    InputElement, DropdownElement, WindowElement
)


class TestElementFactory:
    """Test ElementFactory class"""
    
    def test_create_element_button(self, mocker):
        """Test creating a button element"""
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'Button'
        
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='Button')
        element = ElementFactory().create_element(mock_native, mocker.Mock())
        
        assert isinstance(element, ButtonElement)

    def test_create_element_checkbox(self, mocker):
        """Test creating a checkbox element"""
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'CheckBox'
        
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='CheckBox')
        element = ElementFactory().create_element(mock_native, mocker.Mock())
        
        assert isinstance(element, CheckboxElement)

    def test_create_element_text(self, mocker):
        """Test creating a text element"""
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'Text'
        
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='Text')
        element = ElementFactory().create_element(mock_native, mocker.Mock())
        
        assert isinstance(element, TextElement)

    def test_create_element_input(self, mocker):
        """Test creating an input element"""
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'Edit'
        
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='Edit')
        element = ElementFactory().create_element(mock_native, mocker.Mock())
        
        assert isinstance(element, InputElement)

    def test_create_element_dropdown(self, mocker):
        """Test creating a dropdown element"""
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'ComboBox'
        
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='ComboBox')
        element = ElementFactory().create_element(mock_native, mocker.Mock())
        
        assert isinstance(element, DropdownElement)

    def test_create_element_window(self, mocker):
        """Test creating a window element"""
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'Window'
        
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='Window')
        element = ElementFactory().create_element(mock_native, mocker.Mock())
        
        assert isinstance(element, WindowElement)

    def test_create_element_unknown_type(self, mocker):
        """Test creating an element with unknown type"""
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'Unknown'
        
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='Unknown')
        element = ElementFactory().create_element(mock_native, mocker.Mock())
        
        assert isinstance(element, TextElement)  # Default fallback

    def test_get_control_type(self, mocker):
        """Test _get_control_type method"""
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'Button'
        
        factory = ElementFactory()
        control_type = factory._get_control_type(mock_native)
        
        assert control_type == 'Button'

    def test_get_control_type_fallback(self, mocker):
        """Test _get_control_type method with fallback"""
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = None
        mock_native.ControlType.ProgrammaticName = 'TextBox'
        mock_native.get_property.return_value = 'TextBox'  # Mock get_property to return TextBox
        
        factory = ElementFactory()
        control_type = factory._get_control_type(mock_native)
        
        assert control_type == 'TextBox'

    def test_register_and_create_custom_element(self, mocker):
        """Test registering and creating a custom element type"""
        class CustomElement(TextElement):
            pass
        
        factory = ElementFactory()
        factory.register_element_type('Custom', CustomElement)
        
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'Custom'
        
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='Custom')
        element = factory.create_element(mock_native, mocker.Mock())
        
        assert isinstance(element, CustomElement)

    def test_unregister_element_type(self, mocker):
        """Test unregistering an element type"""
        factory = ElementFactory()
        factory.unregister_element_type('Button')
        
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'Button'
        
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='Button')
        element = factory.create_element(mock_native, mocker.Mock())
        
        assert isinstance(element, TextElement)  # Should fallback to default


class TestGlobalFactory:
    """Test global factory functions"""
    
    def test_create_element_global(self, mocker):
        """Test global create_element function"""
        from pyui_automation.elements.element_factory import create_element
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'Button'
        
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='Button')
        element = create_element(mock_native, mocker.Mock())
        
        assert isinstance(element, ButtonElement)


class TestElementFactoryIntegration:
    """Integration tests for ElementFactory"""
    
    def test_factory_registry_operations(self, mocker):
        """Test factory registry operations"""
        class TestElement(TextElement):
            pass
        
        factory = ElementFactory()
        
        # Test registration
        factory.register_element_type('Test', TestElement)
        assert 'Test' in factory._element_types
        
        # Test creation
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'Test'
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='Test')
        element = factory.create_element(mock_native, mocker.Mock())
        assert isinstance(element, TestElement)
        
        # Test unregistration
        factory.unregister_element_type('Test')
        assert 'Test' not in factory._element_types

    def test_element_creation_with_session(self, mocker):
        """Test element creation with session parameter"""
        mock_session = mocker.Mock()
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'Button'
        
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='Button')
        element = ElementFactory().create_element(mock_native, mock_session)
        
        assert element.session == mock_session

    def test_element_creation_with_native_element(self, mocker):
        """Test element creation with native element parameter"""
        mock_session = mocker.Mock()
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'Button'
        
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='Button')
        element = ElementFactory().create_element(mock_native, mock_session)
        
        assert element.native_element == mock_native

    def test_factory_error_handling(self, mocker):
        """Test factory error handling"""
        mock_native = mocker.Mock()
        mock_native.CurrentControlType.ProgrammaticName = 'Invalid'
        
        mocker.patch.object(ElementFactory, '_get_control_type', return_value='Invalid')
        element = ElementFactory().create_element(mock_native, mocker.Mock())
        
        # Should fallback to TextElement for unknown types
        assert isinstance(element, TextElement) 