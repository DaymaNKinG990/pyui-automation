"""
Tests for core exceptions
"""
import pytest

from pyui_automation.core.exceptions import (
    AutomationError,
    ElementNotFoundError,
    ElementStateError,
    TimeoutError,
    BackendError,
    ConfigurationError,
    ValidationError,
    OCRError,
    VisualError,
    InputError,
    WindowError,
    WaitTimeout
)


class TestAutomationError:
    """Test AutomationError base class"""
    
    def test_automation_error_inheritance(self):
        """Test that AutomationError inherits from Exception"""
        error = AutomationError("Test error")
        assert isinstance(error, Exception)
    
    def test_automation_error_message(self):
        """Test AutomationError message"""
        message = "Test error message"
        error = AutomationError(message)
        assert str(error) == message


class TestExceptionInheritance:
    """Test exception inheritance and message handling"""
    
    @pytest.mark.parametrize("exception_class,message", [
        (ElementNotFoundError, "Element not found"),
        (ElementStateError, "Invalid state"),
        (TimeoutError, "Operation timed out"),
        (BackendError, "Backend failed"),
        (ConfigurationError, "Invalid configuration"),
        (ValidationError, "Validation failed"),
        (OCRError, "OCR failed"),
        (VisualError, "Visual operation failed"),
        (InputError, "Input operation failed"),
        (WindowError, "Window operation failed"),
        (WaitTimeout, "Wait timed out"),
    ])
    def test_exception_inheritance_and_message(self, exception_class, message):
        """Test that exceptions inherit from AutomationError and have correct messages"""
        error = exception_class(message)
        assert isinstance(error, AutomationError)
        assert str(error) == message
    
    def test_exception_with_empty_message(self):
        """Test exceptions with empty messages"""
        error = ElementNotFoundError("")
        assert str(error) == ""
    
    def test_exception_with_special_characters(self):
        """Test exceptions with special characters in messages"""
        message = "Error with special chars: éñüßáö!@#$%^&*()"
        error = ValidationError(message)
        assert str(error) == message 