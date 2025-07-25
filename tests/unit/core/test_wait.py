"""
Tests for wait functionality
"""
import pytest
import time
from unittest.mock import Mock, patch, MagicMock

from pyui_automation.core.wait import WaitService, WaitCondition, TimeoutError


class TestWaitUntil:
    """Test wait_until function"""
    
    def test_wait_until_with_immediate_true(self, mocker):
        """Test wait_until with condition that returns True immediately"""
        condition = mocker.Mock(return_value=True)
        result = WaitService.wait_until(condition, timeout=1.0)
        assert result is True
        condition.assert_called_once()
    
    def test_wait_until_with_delayed_true(self, mocker):
        """Test wait_until with condition that becomes True after delay"""
        call_count = 0
        def condition():
            nonlocal call_count
            call_count += 1
            return call_count >= 3
        
        result = WaitService.wait_until(condition, timeout=1.0, poll_frequency=0.01)
        assert result is True
        assert call_count >= 3
    
    def test_wait_until_with_timeout(self, mocker):
        """Test wait_until with timeout"""
        condition = mocker.Mock(return_value=False)
        
        with pytest.raises(TimeoutError, match="Timed out after 0.1 seconds"):
            WaitService.wait_until(condition, timeout=0.1, poll_frequency=0.01)
    
    def test_wait_until_with_custom_error_message(self, mocker):
        """Test wait_until with custom error message"""
        condition = mocker.Mock(return_value=False)
        
        with pytest.raises(TimeoutError, match="Custom error message"):
            WaitService.wait_until(condition, timeout=0.1, poll_frequency=0.01, error_message="Custom error message")
    
    def test_wait_until_with_non_callable_condition(self, mocker):
        """Test wait_until with non-callable condition"""
        with pytest.raises(TypeError, match="condition must be callable"):
            WaitService.wait_until("not callable", timeout=1.0)
    
    def test_wait_until_with_negative_timeout(self, mocker):
        """Test wait_until with negative timeout"""
        condition = mocker.Mock(return_value=True)
        
        with pytest.raises(ValueError, match="timeout must be non-negative"):
            WaitService.wait_until(condition, timeout=-1.0)
    
    def test_wait_until_with_negative_poll_frequency(self, mocker):
        """Test wait_until with negative poll frequency"""
        with pytest.raises(ValueError, match="poll_frequency must be non-negative"):
            WaitService.wait_until(lambda: True, poll_frequency=-0.1)
    
    def test_wait_until_with_zero_poll_frequency(self, mocker):
        """Test wait_until with zero poll frequency"""
        # Zero poll frequency should be allowed
        result = WaitService.wait_until(lambda: True, timeout=0.1, poll_frequency=0)
        assert result is True
    
    def test_wait_until_with_short_timeout(self, mocker):
        """Test wait_until with timeout shorter than poll frequency"""
        condition = mocker.Mock(return_value=True)
        
        result = WaitService.wait_until(condition, timeout=0.1, poll_frequency=0.5)
        assert result is True


class TestWaitUntilErrorHandling:
    """Test error handling in wait_until function"""
    
    def test_wait_until_with_non_callable_condition(self, mocker):
        """Test wait_until with non-callable condition"""
        with pytest.raises(TypeError, match="condition must be callable"):
            WaitService.wait_until("not_callable")
    
    def test_wait_until_with_negative_timeout(self, mocker):
        """Test wait_until with negative timeout"""
        with pytest.raises(ValueError, match="timeout must be non-negative"):
            WaitService.wait_until(lambda: True, timeout=-1)
    
    def test_wait_until_with_negative_poll_frequency(self, mocker):
        """Test wait_until with negative poll frequency"""
        with pytest.raises(ValueError, match="poll_frequency must be non-negative"):
            WaitService.wait_until(lambda: True, poll_frequency=-0.1)
    
    def test_wait_until_with_zero_poll_frequency(self, mocker):
        """Test wait_until with zero poll frequency"""
        # Zero poll frequency should be allowed
        result = WaitService.wait_until(lambda: True, timeout=0.1, poll_frequency=0)
        assert result is True
    
    def test_wait_until_with_timeout_less_than_poll_frequency(self, mocker):
        """Test wait_until with timeout less than poll frequency"""
        start_time = time.time()
        result = WaitService.wait_until(lambda: True, timeout=0.1, poll_frequency=0.2)
        end_time = time.time()
        
        assert result is True
        # Should complete quickly due to adjusted poll frequency
        assert end_time - start_time < 0.2


class TestElementWaits:
    """Test ElementWaits class"""
    
    def test_element_waits_initialization(self, mocker):
        """Test ElementWaits initialization"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        assert waits.automation == mock_automation
    
    def test_element_waits_wait_until(self, mocker):
        """Test ElementWaits wait_until method"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        condition = mocker.Mock(return_value=True)
        
        result = waits.wait_until(condition, timeout=1.0)
        assert result is True
        condition.assert_called_once()
    
    def test_for_element_by_object_name_success(self, mocker):
        """Test for_element_by_object_name with success"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        mock_automation.backend.find_element_by_object_name.return_value = mock_element
        
        waits = WaitService.ElementWaits(mock_automation)
        result = waits.for_element_by_object_name("test_object", timeout=1.0)
        
        assert result == mock_element
        mock_automation.backend.find_element_by_object_name.assert_called_with("test_object")
    
    def test_for_element_by_object_name_timeout(self, mocker):
        """Test for_element_by_object_name with timeout"""
        mock_automation = mocker.Mock()
        mock_automation.backend.find_element_by_object_name.return_value = None
        
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(TimeoutError, match="Element not found with object_name=test_object"):
            waits.for_element_by_object_name("test_object", timeout=0.1)
    
    def test_for_element_by_object_name_invalid_input(self, mocker):
        """Test for_element_by_object_name with invalid input"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="object_name must be a non-empty string"):
            waits.for_element_by_object_name("", timeout=1.0)
        
        with pytest.raises(ValueError, match="object_name must be a non-empty string"):
            waits.for_element_by_object_name(None, timeout=1.0)
    
    def test_for_element_by_widget_type_success(self, mocker):
        """Test for_element_by_widget_type with success"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        mock_automation.backend.find_element_by_widget_type.return_value = mock_element
        
        waits = WaitService.ElementWaits(mock_automation)
        result = waits.for_element_by_widget_type("Button", timeout=1.0)
        
        assert result == mock_element
        mock_automation.backend.find_element_by_widget_type.assert_called_with("Button")
    
    def test_for_element_by_widget_type_timeout(self, mocker):
        """Test for_element_by_widget_type with timeout"""
        mock_automation = mocker.Mock()
        mock_automation.backend.find_element_by_widget_type.return_value = None
        
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(TimeoutError, match="Element not found with widget_type=Button"):
            waits.for_element_by_widget_type("Button", timeout=0.1)
    
    def test_for_element_by_widget_type_invalid_input(self, mocker):
        """Test for_element_by_widget_type with invalid input"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="widget_type must be a non-empty string"):
            waits.for_element_by_widget_type("", timeout=1.0)
    
    def test_for_element_by_text_success(self, mocker):
        """Test for_element_by_text with success"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        mock_automation.backend.find_element_by_text.return_value = mock_element
        
        waits = WaitService.ElementWaits(mock_automation)
        result = waits.for_element_by_text("Click me", timeout=1.0)
        
        assert result == mock_element
        mock_automation.backend.find_element_by_text.assert_called_with("Click me")
    
    def test_for_element_by_text_timeout(self, mocker):
        """Test for_element_by_text with timeout"""
        mock_automation = mocker.Mock()
        mock_automation.backend.find_element_by_text.return_value = None
        
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(TimeoutError, match="Element not found with text=Click me"):
            waits.for_element_by_text("Click me", timeout=0.1)
    
    def test_for_element_by_text_invalid_input(self, mocker):
        """Test for_element_by_text with invalid input"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="text must be a non-empty string"):
            waits.for_element_by_text("", timeout=1.0)
    
    def test_for_element_by_property_success(self, mocker):
        """Test for_element_by_property with success"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        mock_automation.backend.find_element_by_property.return_value = mock_element
        
        waits = WaitService.ElementWaits(mock_automation)
        result = waits.for_element_by_property("name", "submit_button", timeout=1.0)
        
        assert result == mock_element
        mock_automation.backend.find_element_by_property.assert_called_with("name", "submit_button")
    
    def test_for_element_by_property_timeout(self, mocker):
        """Test for_element_by_property with timeout"""
        mock_automation = mocker.Mock()
        mock_automation.backend.find_element_by_property.return_value = None
        
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(TimeoutError, match="Element not found with name=submit_button"):
            waits.for_element_by_property("name", "submit_button", timeout=0.1)
    
    def test_for_element_by_property_invalid_input(self, mocker):
        """Test for_element_by_property with invalid input"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="property_name must be a non-empty string"):
            waits.for_element_by_property("", "value", timeout=1.0)
        
        with pytest.raises(ValueError, match="value must be a non-empty string"):
            waits.for_element_by_property("name", "", timeout=1.0)
    
    def test_for_element_pattern_success(self, mocker):
        """Test for_element_pattern with success"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        mock_element.has_pattern.return_value = True
        
        waits = WaitService.ElementWaits(mock_automation)
        result = waits.for_element_pattern(mock_element, "Invoke", timeout=1.0)
        
        assert result is True
        mock_element.has_pattern.assert_called_with("Invoke")
    
    def test_for_element_pattern_timeout(self, mocker):
        """Test for_element_pattern with timeout"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        mock_element.has_pattern.return_value = False
        
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(TimeoutError, match="Pattern not supported: Invoke"):
            waits.for_element_pattern(mock_element, "Invoke", timeout=0.1)
    
    def test_for_element_pattern_invalid_element(self, mocker):
        """Test for_element_pattern with invalid element"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        # Remove has_pattern method
        del mock_element.has_pattern
        
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(TypeError, match="element must have a callable has_pattern method"):
            waits.for_element_pattern(mock_element, "Invoke", timeout=1.0)
    
    def test_for_element_pattern_invalid_pattern_name(self, mocker):
        """Test for_element_pattern with invalid pattern name"""
        mock_automation = mocker.Mock()
        mock_element = mocker.Mock()
        mock_element.has_pattern.return_value = True
        
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="pattern_name must be a non-empty string"):
            waits.for_element_pattern(mock_element, "", timeout=1.0)


class TestElementWaitsErrorHandling:
    """Test error handling in ElementWaits"""
    
    def test_for_element_by_object_name_with_empty_string(self, mocker):
        """Test for_element_by_object_name with empty string"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="object_name must be a non-empty string"):
            waits.for_element_by_object_name("")
    
    def test_for_element_by_object_name_with_none(self, mocker):
        """Test for_element_by_object_name with None"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="object_name must be a non-empty string"):
            waits.for_element_by_object_name(None)
    
    def test_for_element_by_widget_type_with_empty_string(self, mocker):
        """Test for_element_by_widget_type with empty string"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="widget_type must be a non-empty string"):
            waits.for_element_by_widget_type("")
    
    def test_for_element_by_widget_type_with_none(self, mocker):
        """Test for_element_by_widget_type with None"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="widget_type must be a non-empty string"):
            waits.for_element_by_widget_type(None)
    
    def test_for_element_by_text_with_empty_string(self, mocker):
        """Test for_element_by_text with empty string"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="text must be a non-empty string"):
            waits.for_element_by_text("")
    
    def test_for_element_by_text_with_none(self, mocker):
        """Test for_element_by_text with None"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="text must be a non-empty string"):
            waits.for_element_by_text(None)
    
    def test_for_element_by_property_with_empty_property_name(self, mocker):
        """Test for_element_by_property with empty property name"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="property_name must be a non-empty string"):
            waits.for_element_by_property("", "value")
    
    def test_for_element_by_property_with_empty_value(self, mocker):
        """Test for_element_by_property with empty value"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="value must be a non-empty string"):
            waits.for_element_by_property("property", "")
    
    def test_for_element_by_property_with_none_property_name(self, mocker):
        """Test for_element_by_property with None property name"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="property_name must be a non-empty string"):
            waits.for_element_by_property(None, "value")
    
    def test_for_element_by_property_with_none_value(self, mocker):
        """Test for_element_by_property with None value"""
        mock_automation = mocker.Mock()
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(ValueError, match="value must be a non-empty string"):
            waits.for_element_by_property("property", None)


class TestElementWaitsTimeout:
    """Test timeout scenarios in ElementWaits"""
    
    def test_for_element_by_object_name_timeout(self, mocker):
        """Test for_element_by_object_name timeout"""
        mock_automation = mocker.Mock()
        mock_automation.backend.find_element_by_object_name.return_value = None
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(TimeoutError, match="Element not found with object_name=test"):
            waits.for_element_by_object_name("test", timeout=0.1)
    
    def test_for_element_by_widget_type_timeout(self, mocker):
        """Test for_element_by_widget_type timeout"""
        mock_automation = mocker.Mock()
        mock_automation.backend.find_element_by_widget_type.return_value = None
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(TimeoutError, match="Element not found with widget_type=button"):
            waits.for_element_by_widget_type("button", timeout=0.1)
    
    def test_for_element_by_text_timeout(self, mocker):
        """Test for_element_by_text timeout"""
        mock_automation = mocker.Mock()
        mock_automation.backend.find_element_by_text.return_value = None
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(TimeoutError, match="Element not found with text=Hello"):
            waits.for_element_by_text("Hello", timeout=0.1)
    
    def test_for_element_by_property_timeout(self, mocker):
        """Test for_element_by_property timeout"""
        mock_automation = mocker.Mock()
        mock_automation.backend.find_element_by_property.return_value = None
        waits = WaitService.ElementWaits(mock_automation)
        
        with pytest.raises(TimeoutError, match="Element not found with id=test"):
            waits.for_element_by_property("id", "test", timeout=0.1)


class TestElementWaitsSuccess:
    """Test successful scenarios in ElementWaits"""
    
    def test_for_element_by_object_name_success(self, mocker):
        """Test for_element_by_object_name success"""
        mock_element = mocker.Mock()
        mock_automation = mocker.Mock()
        mock_automation.backend.find_element_by_object_name.return_value = mock_element
        waits = WaitService.ElementWaits(mock_automation)
        
        result = waits.for_element_by_object_name("test")
        assert result == mock_element
    
    def test_for_element_by_widget_type_success(self, mocker):
        """Test for_element_by_widget_type success"""
        mock_element = mocker.Mock()
        mock_automation = mocker.Mock()
        mock_automation.backend.find_element_by_widget_type.return_value = mock_element
        waits = WaitService.ElementWaits(mock_automation)
        
        result = waits.for_element_by_widget_type("button")
        assert result == mock_element
    
    def test_for_element_by_text_success(self, mocker):
        """Test for_element_by_text success"""
        mock_element = mocker.Mock()
        mock_automation = mocker.Mock()
        mock_automation.backend.find_element_by_text.return_value = mock_element
        waits = WaitService.ElementWaits(mock_automation)
        
        result = waits.for_element_by_text("Hello")
        assert result == mock_element
    
    def test_for_element_by_property_success(self, mocker):
        """Test for_element_by_property success"""
        mock_element = mocker.Mock()
        mock_automation = mocker.Mock()
        mock_automation.backend.find_element_by_property.return_value = mock_element
        waits = WaitService.ElementWaits(mock_automation)
        
        result = waits.for_element_by_property("id", "test")
        assert result == mock_element


class TestElementWaitsEdgeCases:
    """Test edge cases in ElementWaits"""
    
    def test_for_element_by_object_name_with_delayed_success(self, mocker):
        """Test for_element_by_object_name with delayed success"""
        mock_element = mocker.Mock()
        mock_automation = mocker.Mock()
        # First call returns None, second call returns element
        mock_automation.backend.find_element_by_object_name.side_effect = [None, mock_element]
        waits = WaitService.ElementWaits(mock_automation)
        
        result = waits.for_element_by_object_name("test", timeout=1.0)
        assert result == mock_element
    
    def test_for_element_by_widget_type_with_delayed_success(self, mocker):
        """Test for_element_by_widget_type with delayed success"""
        mock_element = mocker.Mock()
        mock_automation = mocker.Mock()
        # First call returns None, second call returns element
        mock_automation.backend.find_element_by_widget_type.side_effect = [None, mock_element]
        waits = WaitService.ElementWaits(mock_automation)
        
        result = waits.for_element_by_widget_type("button", timeout=1.0)
        assert result == mock_element
    
    def test_for_element_by_text_with_delayed_success(self, mocker):
        """Test for_element_by_text with delayed success"""
        mock_element = mocker.Mock()
        mock_automation = mocker.Mock()
        # First call returns None, second call returns element
        mock_automation.backend.find_element_by_text.side_effect = [None, mock_element]
        waits = WaitService.ElementWaits(mock_automation)
        
        result = waits.for_element_by_text("Hello", timeout=1.0)
        assert result == mock_element
    
    def test_for_element_by_property_with_delayed_success(self, mocker):
        """Test for_element_by_property with delayed success"""
        mock_element = mocker.Mock()
        mock_automation = mocker.Mock()
        # First call returns None, second call returns element
        mock_automation.backend.find_element_by_property.side_effect = [None, mock_element]
        waits = WaitService.ElementWaits(mock_automation)
        
        result = waits.for_element_by_property("id", "test", timeout=1.0)
        assert result == mock_element 