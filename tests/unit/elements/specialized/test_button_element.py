"""
Tests for ButtonElement
"""
import pytest

from pyui_automation.elements.specialized.button_element import ButtonElement


class TestButtonElement:
    """Test ButtonElement class"""
    
    def test_is_pressed(self, mocker):
        """Test is_pressed method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.button = ButtonElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.button, 'get_property', return_value=True)
        result = self.button.is_pressed()
        assert result is True
        self.button.get_property.assert_called_with("IsPressed")

    def test_is_pressed_false(self, mocker):
        """Test is_pressed method when button is not pressed"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.button = ButtonElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.button, 'get_property', return_value=False)
        result = self.button.is_pressed()
        assert result is False

    def test_is_pressed_none(self, mocker):
        """Test is_pressed method when property returns None"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.button = ButtonElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.button, 'get_property', return_value=None)
        result = self.button.is_pressed()
        assert result is False

    def test_get_button_text(self, mocker):
        """Test get_button_text method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.button = ButtonElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.button, 'get_attribute', return_value="Click me")
        result = self.button.get_button_text()
        assert result == "Click me"

    def test_is_button_enabled(self, mocker):
        """Test is_button_enabled method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.button = ButtonElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.button, 'is_enabled', return_value=True)
        result = self.button.is_button_enabled()
        assert result is True

    def test_get_button_state(self, mocker):
        """Test get_button_state method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.button = ButtonElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.button, 'is_pressed', return_value=True)
        mocker.patch.object(self.button, 'is_enabled', return_value=True)
        mocker.patch.object(self.button, 'get_attribute', return_value="Test Button")
        mocker.patch.object(self.button, 'is_displayed', return_value=True)
        # Mock the native element properties
        mock_rect = mocker.Mock()
        mock_rect.left = 100
        mock_rect.top = 200
        mock_rect.width = 50
        mock_rect.height = 30
        self.mock_native_element.CurrentBoundingRectangle = mock_rect
        state = self.button.get_button_state()
        assert state['pressed'] is True
        assert state['enabled'] is True
        assert state['text'] == "Test Button"

    def test_click_and_wait(self, mocker):
        """Test click_and_wait method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.button = ButtonElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.button, 'click')
        mocker.patch.object(self.button, 'wait_until_enabled', return_value=True)
        result = self.button.click_and_wait()
        assert result is True
        self.button.click.assert_called_once()
        self.button.wait_until_enabled.assert_called_once()

    def test_click_and_wait_with_timeout(self, mocker):
        """Test click_and_wait method with custom timeout"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.button = ButtonElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.button, 'click')
        mocker.patch.object(self.button, 'wait_until_enabled', return_value=True)
        result = self.button.click_and_wait(timeout=5.0)
        assert result is True
        self.button.click.assert_called_once()
        self.button.wait_until_enabled.assert_called_once_with(5.0)

    def test_double_click_and_wait(self, mocker):
        """Test double_click_and_wait method"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.button = ButtonElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.button, 'double_click')
        mocker.patch.object(self.button, 'wait_until_enabled', return_value=True)
        result = self.button.double_click_and_wait()
        assert result is True
        self.button.double_click.assert_called_once()
        self.button.wait_until_enabled.assert_called_once()

    def test_double_click_and_wait_with_timeout(self, mocker):
        """Test double_click_and_wait method with custom timeout"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.button = ButtonElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.button, 'double_click')
        mocker.patch.object(self.button, 'wait_until_enabled', return_value=True)
        result = self.button.double_click_and_wait(timeout=3.0)
        assert result is True
        self.button.double_click.assert_called_once()
        self.button.wait_until_enabled.assert_called_once_with(3.0)


class TestButtonElementIntegration:
    """Integration tests for ButtonElement"""
    
    def test_button_initialization(self, mocker):
        """Test ButtonElement initialization"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.button = ButtonElement(self.mock_native_element, self.mock_session)
        assert self.button._element == self.mock_native_element
        assert self.button._session == self.mock_session

    def test_button_inherits_from_base_element(self, mocker):
        """Test that ButtonElement inherits from BaseElement"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.button = ButtonElement(self.mock_native_element, self.mock_session)
        from pyui_automation.elements.base_element import BaseElement
        assert isinstance(self.button, BaseElement)

    def test_button_methods_use_correct_properties(self, mocker):
        """Test that button methods use correct property names"""
        self.mock_native_element = mocker.Mock()
        self.mock_session = mocker.Mock()
        self.button = ButtonElement(self.mock_native_element, self.mock_session)
        mocker.patch.object(self.button, 'get_property')
        
        # Test is_pressed uses "IsPressed"
        self.button.is_pressed()
        self.button.get_property.assert_called_with("IsPressed")
        
        # Reset mock for next test
        self.button.get_property.reset_mock()
        
        # Test get_button_text uses get_attribute
        self.button.get_button_text()
        # get_button_text uses get_attribute, not get_property
        
        # Reset mock for next test
        self.button.get_property.reset_mock()
        
        # Test is_button_enabled uses is_enabled method
        self.button.is_button_enabled()
        # is_button_enabled uses is_enabled method, not get_property 