"""
Tests for ButtonElement
"""
import pytest
from unittest.mock import Mock
from pyui_automation.elements.specialized.button_element import ButtonElement


@pytest.fixture
def button_element(mock_session, mock_native_element):
    """Create a ButtonElement instance for testing"""
    return ButtonElement(mock_native_element, mock_session)


class TestButtonElement:
    """Test ButtonElement class"""
    
    def test_is_pressed(self, button_element, mocker):
        """Test is_pressed method"""
        mocker.patch.object(button_element, 'get_property', return_value=True)
        result = button_element.is_pressed()
        assert result is True

    def test_is_pressed_false(self, button_element, mocker):
        """Test is_pressed method when button is not pressed"""
        mocker.patch.object(button_element, 'get_property', return_value=False)
        result = button_element.is_pressed()
        assert result is False

    def test_is_pressed_none(self, button_element, mocker):
        """Test is_pressed method when property returns None"""
        mocker.patch.object(button_element, 'get_property', return_value=None)
        result = button_element.is_pressed()
        assert result is False

    def test_get_button_text(self, button_element, mocker):
        """Test get_button_text method"""
        mocker.patch.object(button_element, 'get_attribute', return_value="Click me")
        result = button_element.get_button_text()
        assert result == "Click me"

    def test_is_button_enabled(self, button_element, mocker):
        """Test is_button_enabled method"""
        mocker.patch.object(button_element, 'is_enabled', return_value=True)
        result = button_element.is_button_enabled()
        assert result is True

    def test_get_button_state(self, button_element, mocker, mock_native_element):
        """Test get_button_state method"""
        mocker.patch.object(button_element, 'is_pressed', return_value=True)
        mocker.patch.object(button_element, 'is_enabled', return_value=True)
        mocker.patch.object(button_element, 'get_attribute', return_value="Test Button")
        mocker.patch.object(button_element, 'is_displayed', return_value=True)
        
        # Mock the native element properties
        mock_rect = Mock()
        mock_rect.left = 100
        mock_rect.top = 200
        mock_rect.width = 50
        mock_rect.height = 30
        mock_native_element.CurrentBoundingRectangle = mock_rect
        
        state = button_element.get_button_state()
        assert state['pressed'] is True
        assert state['enabled'] is True
        assert state['text'] == "Test Button"

    def test_click_and_wait(self, button_element, mocker):
        """Test click_and_wait method"""
        mocker.patch.object(button_element, 'click')
        mocker.patch.object(button_element, 'wait_until_enabled', return_value=True)
        result = button_element.click_and_wait()
        assert result is True

    def test_click_and_wait_with_timeout(self, button_element, mocker):
        """Test click_and_wait method with custom timeout"""
        mocker.patch.object(button_element, 'click')
        mocker.patch.object(button_element, 'wait_until_enabled', return_value=True)
        result = button_element.click_and_wait(timeout=5.0)
        assert result is True

    def test_double_click_and_wait(self, button_element, mocker):
        """Test double_click_and_wait method"""
        mocker.patch.object(button_element, 'double_click')
        mocker.patch.object(button_element, 'wait_until_enabled', return_value=True)
        result = button_element.double_click_and_wait()
        assert result is True

    def test_double_click_and_wait_with_timeout(self, button_element, mocker):
        """Test double_click_and_wait method with custom timeout"""
        mocker.patch.object(button_element, 'double_click')
        mocker.patch.object(button_element, 'wait_until_enabled', return_value=True)
        result = button_element.double_click_and_wait(timeout=3.0)
        assert result is True


class TestButtonElementIntegration:
    """Integration tests for ButtonElement"""
    
    def test_button_initialization(self, button_element, mock_native_element, mock_session):
        """Test ButtonElement initialization"""
        assert button_element._element == mock_native_element
        assert button_element._session == mock_session

    def test_button_inherits_from_base_element(self, button_element):
        """Test that ButtonElement inherits from BaseElement"""
        from pyui_automation.elements.base_element import BaseElement
        assert isinstance(button_element, BaseElement)

    def test_button_methods_use_correct_properties(self, button_element, mocker):
        """Test that button methods use correct property names"""
        mocker.patch.object(button_element, 'get_property')
        
        # Test is_pressed uses "IsPressed"
        button_element.is_pressed()
        button_element.get_property.assert_called_with("IsPressed")
        
        # Reset mock for next test
        button_element.get_property.reset_mock()
        
        # Test get_button_text uses get_attribute
        mocker.patch.object(button_element, 'get_attribute')
        button_element.get_button_text()
        button_element.get_attribute.assert_called()
        
        # Reset mock for next test
        button_element.get_property.reset_mock()
        
        # Test is_button_enabled uses is_enabled method
        mocker.patch.object(button_element, 'is_enabled')
        button_element.is_button_enabled()
        button_element.is_enabled.assert_called() 