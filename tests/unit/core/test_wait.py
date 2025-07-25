"""
Tests for wait functionality
"""
import pytest

from pyui_automation.core.wait import wait_until, ElementWaits
from pyui_automation.core.exceptions import WaitTimeout


class TestWaitUntil:
    """Test wait_until function"""
    
    def test_wait_until_success(self):
        """Test wait_until with successful condition"""
        condition_called = False
        
        def condition():
            nonlocal condition_called
            condition_called = True
            return True
        
        result = wait_until(condition, timeout=1.0)
        assert result is True
        assert condition_called is True
    
    def test_wait_until_timeout(self):
        """Test wait_until with timeout"""
        def condition():
            return False
        
        with pytest.raises(WaitTimeout):
            wait_until(condition, timeout=0.1)
    
    def test_wait_until_custom_error_message(self):
        """Test wait_until with custom error message"""
        def condition():
            return False
        
        with pytest.raises(WaitTimeout) as exc_info:
            wait_until(condition, timeout=0.1, error_message="Custom timeout")
        assert "Custom timeout" in str(exc_info.value)
    
    def test_wait_until_invalid_condition(self):
        """Test wait_until with invalid condition"""
        with pytest.raises(TypeError):
            wait_until("not callable", timeout=1.0)
    
    def test_wait_until_negative_timeout(self):
        """Test wait_until with negative timeout"""
        def condition():
            return True
        
        with pytest.raises(ValueError):
            wait_until(condition, timeout=-1.0)
    
    def test_wait_until_negative_poll_frequency(self):
        """Test wait_until with negative poll frequency"""
        def condition():
            return True
        
        with pytest.raises(ValueError):
            wait_until(condition, timeout=1.0, poll_frequency=-0.1)


class TestElementWaits:
    """Test ElementWaits class"""
    
    def test_init(self, mocker):
        """Test ElementWaits initialization"""
        mock_automation = mocker.Mock()
        waits = ElementWaits(mock_automation)
        assert waits.automation == mock_automation
    
    def test_wait_until_method(self, mocker):
        """Test ElementWaits.wait_until method"""
        mock_automation = mocker.Mock()
        waits = ElementWaits(mock_automation)
        
        def condition():
            return True
        
        result = waits.wait_until(condition, timeout=1.0)
        assert result is True
    
    def test_for_element_by_object_name_success(self, mocker):
        """Test for_element_by_object_name with success"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        mock_automation.backend.find_element_by_object_name.return_value = mock_element
        
        waits = ElementWaits(mock_automation)
        result = waits.for_element_by_object_name("test_object", timeout=1.0)
        
        assert result == mock_element
        mock_automation.backend.find_element_by_object_name.assert_called_with("test_object")
    
    def test_for_element_by_object_name_timeout(self, mocker):
        """Test for_element_by_object_name with timeout"""
        mock_automation = mocker.Mock()
        mock_automation.backend.find_element_by_object_name.return_value = None
        
        waits = ElementWaits(mock_automation)
        
        with pytest.raises(WaitTimeout):
            waits.for_element_by_object_name("test_object", timeout=0.1)
    
    def test_for_element_by_object_name_invalid_name(self, mocker):
        """Test for_element_by_object_name with invalid name"""
        mock_automation = mocker.Mock()
        waits = ElementWaits(mock_automation)
        
        with pytest.raises(ValueError):
            waits.for_element_by_object_name("", timeout=1.0)
    
    def test_for_element_by_widget_type_success(self, mocker):
        """Test for_element_by_widget_type with success"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        mock_automation.backend.find_element_by_widget_type.return_value = mock_element
        
        waits = ElementWaits(mock_automation)
        result = waits.for_element_by_widget_type("Button", timeout=1.0)
        
        assert result == mock_element
        mock_automation.backend.find_element_by_widget_type.assert_called_with("Button")
    
    def test_for_element_by_text_success(self, mocker):
        """Test for_element_by_text with success"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        mock_automation.backend.find_element_by_text.return_value = mock_element
        
        waits = ElementWaits(mock_automation)
        result = waits.for_element_by_text("Click me", timeout=1.0)
        
        assert result == mock_element
        mock_automation.backend.find_element_by_text.assert_called_with("Click me")
    
    def test_for_element_by_property_success(self, mocker):
        """Test for_element_by_property with success"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        mock_automation.backend.find_element_by_property.return_value = mock_element
        
        waits = ElementWaits(mock_automation)
        result = waits.for_element_by_property("name", "test", timeout=1.0)
        
        assert result == mock_element
        mock_automation.backend.find_element_by_property.assert_called_with("name", "test")
    
    def test_for_element_pattern_success(self, mocker):
        """Test for_element_pattern with success"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        mock_element.has_pattern.return_value = True
        
        waits = ElementWaits(mock_automation)
        result = waits.for_element_pattern(mock_element, "InvokePattern", timeout=1.0)
        
        assert result is True
        mock_element.has_pattern.assert_called_with("InvokePattern")
    
    def test_for_element_pattern_invalid_element(self, mocker):
        """Test for_element_pattern with invalid element"""
        mock_automation = mocker.Mock()
        waits = ElementWaits(mock_automation)
        
        with pytest.raises(TypeError):
            waits.for_element_pattern("not an element", "pattern", timeout=1.0)
    
    def test_for_element_pattern_invalid_pattern_name(self, mocker):
        """Test for_element_pattern with invalid pattern name"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        waits = ElementWaits(mock_automation)
        
        with pytest.raises(ValueError):
            waits.for_element_pattern(mock_element, "", timeout=1.0) 