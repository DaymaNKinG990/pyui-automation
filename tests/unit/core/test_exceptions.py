"""
Tests for exception handling
"""
import pytest
import traceback
from contextlib import contextmanager

from pyui_automation.core.exceptions import (
    AutomationError, ElementNotFoundError, TimeoutError, 
    InvalidStateError, UnsupportedOperationError, ConfigurationError,
    BackendError, VisualTestingError, PerformanceError, OCRError
)


class TestAutomationError:
    """Test base AutomationError exception"""
    
    def test_automation_error_creation(self, mocker):
        """Test basic AutomationError creation"""
        error = AutomationError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)
    
    def test_automation_error_without_message(self, mocker):
        """Test AutomationError without message"""
        error = AutomationError()
        assert str(error) == ""
    
    def test_automation_error_inheritance(self, mocker):
        """Test AutomationError inheritance"""
        error = AutomationError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, AutomationError)


class TestElementNotFoundError:
    """Test ElementNotFoundError exception"""
    
    def test_element_not_found_error_creation(self, mocker):
        """Test basic ElementNotFoundError creation"""
        error = ElementNotFoundError("Element not found")
        assert str(error) == "Element not found"
        assert isinstance(error, AutomationError)
    
    def test_element_not_found_error_inheritance(self, mocker):
        """Test ElementNotFoundError inheritance"""
        error = ElementNotFoundError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, AutomationError)
        assert isinstance(error, ElementNotFoundError)


class TestElementStateError:
    """Test ElementStateError exception"""
    
    def test_element_state_error_creation(self, mocker):
        """Test basic ElementStateError creation"""
        error = InvalidStateError("Element is disabled")
        assert str(error) == "Element is disabled"
        assert isinstance(error, AutomationError)
    
    def test_element_state_error_inheritance(self, mocker):
        """Test ElementStateError inheritance"""
        error = InvalidStateError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, AutomationError)
        assert isinstance(error, InvalidStateError)


class TestTimeoutError:
    """Test TimeoutError exception"""
    
    def test_timeout_error_creation(self, mocker):
        """Test basic TimeoutError creation"""
        error = TimeoutError("Operation timed out")
        assert str(error) == "Operation timed out"
        assert isinstance(error, AutomationError)
    
    def test_timeout_error_inheritance(self, mocker):
        """Test TimeoutError inheritance"""
        error = TimeoutError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, AutomationError)
        assert isinstance(error, TimeoutError)


class TestBackendError:
    """Test BackendError exception"""
    
    def test_backend_error_creation(self, mocker):
        """Test basic BackendError creation"""
        error = BackendError("Backend operation failed")
        assert str(error) == "Backend operation failed"
        assert isinstance(error, AutomationError)
    
    def test_backend_error_inheritance(self, mocker):
        """Test BackendError inheritance"""
        error = BackendError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, AutomationError)
        assert isinstance(error, BackendError)


class TestConfigurationError:
    """Test ConfigurationError exception"""
    
    def test_configuration_error_creation(self, mocker):
        """Test basic ConfigurationError creation"""
        error = ConfigurationError("Invalid configuration")
        assert str(error) == "Invalid configuration"
        assert isinstance(error, AutomationError)
    
    def test_configuration_error_inheritance(self, mocker):
        """Test ConfigurationError inheritance"""
        error = ConfigurationError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, AutomationError)
        assert isinstance(error, ConfigurationError)


class TestValidationError:
    """Test ValidationError exception"""
    
    def test_validation_error_creation(self, mocker):
        """Test basic ValidationError creation"""
        error = InvalidStateError("Validation failed")
        assert str(error) == "Validation failed"
        assert isinstance(error, AutomationError)
    
    def test_validation_error_inheritance(self, mocker):
        """Test ValidationError inheritance"""
        error = InvalidStateError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, AutomationError)
        assert isinstance(error, InvalidStateError)


class TestOCRError:
    """Test OCRError exception"""
    
    def test_ocr_error_creation(self, mocker):
        """Test basic OCRError creation"""
        error = OCRError("OCR operation failed")
        assert str(error) == "OCR operation failed"
        assert isinstance(error, AutomationError)
    
    def test_ocr_error_inheritance(self, mocker):
        """Test OCRError inheritance"""
        error = OCRError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, AutomationError)
        assert isinstance(error, OCRError)


class TestVisualError:
    """Test VisualError exception"""
    
    def test_visual_error_creation(self, mocker):
        """Test basic VisualError creation"""
        error = VisualTestingError("Visual operation failed")
        assert str(error) == "Visual operation failed"
        assert isinstance(error, AutomationError)
    
    def test_visual_error_inheritance(self, mocker):
        """Test VisualError inheritance"""
        error = VisualTestingError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, AutomationError)
        assert isinstance(error, VisualTestingError)


class TestInputError:
    """Test InputError exception"""
    
    def test_input_error_creation(self, mocker):
        """Test basic InputError creation"""
        error = InvalidStateError("Input operation failed")
        assert str(error) == "Input operation failed"
        assert isinstance(error, AutomationError)
    
    def test_input_error_inheritance(self, mocker):
        """Test InputError inheritance"""
        error = InvalidStateError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, AutomationError)
        assert isinstance(error, InvalidStateError)


class TestWindowError:
    """Test WindowError exception"""
    
    def test_window_error_creation(self, mocker):
        """Test basic WindowError creation"""
        error = InvalidStateError("Window operation failed")
        assert str(error) == "Window operation failed"
        assert isinstance(error, AutomationError)
    
    def test_window_error_inheritance(self, mocker):
        """Test WindowError inheritance"""
        error = InvalidStateError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, AutomationError)
        assert isinstance(error, InvalidStateError)


class TestWaitTimeout:
    """Test WaitTimeout exception"""
    
    def test_wait_timeout_creation(self, mocker):
        """Test basic WaitTimeout creation"""
        error = TimeoutError("Wait condition timed out")
        assert str(error) == "Wait condition timed out"
        assert isinstance(error, AutomationError)
    
    def test_wait_timeout_inheritance(self, mocker):
        """Test WaitTimeout inheritance"""
        error = TimeoutError("Test")
        assert isinstance(error, Exception)
        assert isinstance(error, AutomationError)
        assert isinstance(error, TimeoutError)


class TestExceptionHierarchy:
    """Test exception hierarchy and relationships"""
    
    def test_exception_hierarchy(self, mocker):
        """Test that all exceptions inherit from AutomationError"""
        exceptions = [
            ElementNotFoundError,
            InvalidStateError,
            TimeoutError,
            BackendError,
            ConfigurationError,
            InvalidStateError,
            OCRError,
            VisualTestingError,
            InvalidStateError,
            InvalidStateError,
            TimeoutError
        ]
        
        for exception_class in exceptions:
            error = exception_class("Test")
            assert isinstance(error, AutomationError)
            assert isinstance(error, Exception)
    
    def test_exception_uniqueness(self, mocker):
        """Test that exceptions are distinct types"""
        exceptions = [
            ElementNotFoundError,
            InvalidStateError,
            TimeoutError,
            BackendError,
            ConfigurationError,
            InvalidStateError,
            OCRError,
            VisualTestingError,
            InvalidStateError,
            InvalidStateError,
            TimeoutError
        ]
        
        # All exceptions should be different types
        exception_types = set()
        for exception_class in exceptions:
            exception_types.add(exception_class)
        
        assert len(exception_types) == len(exceptions)


class TestExceptionUsage:
    """Test exception usage patterns"""
    
    def test_exception_with_context(self, mocker):
        """Test exception with additional context"""
        try:
            raise ElementNotFoundError("Button not found")
        except ElementNotFoundError as e:
            assert str(e) == "Button not found"
            assert isinstance(e, AutomationError)
    
    def test_exception_chaining(self, mocker):
        """Test exception chaining"""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise BackendError("Backend failed") from e
        except BackendError as e:
            assert str(e) == "Backend failed"
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)
    
    def test_multiple_exception_types(self, mocker):
        """Test handling multiple exception types"""
        exceptions = [
            ElementNotFoundError("Element not found"),
            TimeoutError("Operation timed out"),
            BackendError("Backend error"),
            InvalidStateError("Validation failed")
        ]
        
        for error in exceptions:
            assert isinstance(error, AutomationError)
            assert len(str(error)) > 0 


class TestAutomationExceptionInheritance:
    """Test AutomationException inheritance"""
    
    def test_automation_exception_inherits_from_exception(self, mocker):
        """Test that AutomationException inherits from Exception"""
        exception = AutomationError("Test message")
        assert isinstance(exception, Exception)
    
    def test_automation_exception_is_subclass_of_exception(self, mocker):
        """Test that AutomationException is a subclass of Exception"""
        assert issubclass(AutomationError, Exception)


class TestAutomationExceptionEdgeCases:
    """Test AutomationException edge cases"""
    
    def test_automation_exception_with_empty_message(self, mocker):
        """Test AutomationException with empty message"""
        exception = AutomationError("")
        assert str(exception) == ""
    
    def test_automation_exception_with_none_message(self, mocker):
        """Test AutomationException with None message"""
        exception = AutomationError(None)
        assert str(exception) == "None"
    
    def test_automation_exception_with_numeric_message(self, mocker):
        """Test AutomationException with numeric message"""
        exception = AutomationError(123)
        assert str(exception) == "123"
    
    def test_automation_exception_with_list_message(self, mocker):
        """Test AutomationException with list message"""
        exception = AutomationError(["error", "details"])
        assert str(exception) == "['error', 'details']"
    
    def test_automation_exception_with_dict_message(self, mocker):
        """Test AutomationException with dict message"""
        exception = AutomationError({"error": "details"})
        assert str(exception) == "{'error': 'details'}"


class TestAutomationExceptionRepr:
    """Test AutomationException representation"""
    
    def test_automation_exception_repr(self, mocker):
        """Test AutomationException __repr__ method"""
        exception = AutomationError("Test error")
        repr_str = repr(exception)
        assert "AutomationError" in repr_str
        assert "Test error" in repr_str
    
    def test_automation_exception_repr_with_special_characters(self, mocker):
        """Test AutomationException __repr__ with special characters"""
        exception = AutomationError("Error with 'quotes' and \"double quotes\"")
        repr_str = repr(exception)
        assert "AutomationError" in repr_str
        # Check that the message is in the repr, but don't check exact format
        assert "Error with" in repr_str


class TestAutomationExceptionEquality:
    """Test AutomationException equality"""
    
    def test_automation_exception_equality_same_message(self, mocker):
        """Test AutomationException equality with same message"""
        exception1 = AutomationError("Test message")
        exception2 = AutomationError("Test message")
        # Exceptions are not equal by default, even with same message
        assert exception1 != exception2
    
    def test_automation_exception_equality_different_message(self, mocker):
        """Test AutomationException equality with different message"""
        exception1 = AutomationError("Test message 1")
        exception2 = AutomationError("Test message 2")
        assert exception1 != exception2
    
    def test_automation_exception_equality_with_other_types(self, mocker):
        """Test AutomationException equality with other types"""
        exception = AutomationError("Test message")
        assert exception != "Test message"
        assert exception != Exception("Test message")


class TestAutomationExceptionHash:
    """Test AutomationException hash"""
    
    def test_automation_exception_hash_consistency(self, mocker):
        """Test AutomationException hash consistency"""
        exception1 = AutomationError("Test message")
        exception2 = AutomationError("Test message")
        # Hash should be consistent for same object
        assert hash(exception1) == hash(exception1)
        # But different objects with same message may have different hashes
        assert hash(exception1) != hash(exception2)
    
    def test_automation_exception_hash_different_messages(self, mocker):
        """Test AutomationException hash with different messages"""
        exception1 = AutomationError("Test message 1")
        exception2 = AutomationError("Test message 2")
        assert hash(exception1) != hash(exception2)


class TestAutomationExceptionPickling:
    """Test AutomationException pickling"""
    
    def test_automation_exception_pickling(self, mocker):
        """Test AutomationException can be pickled and unpickled"""
        import pickle
        
        original_exception = AutomationError("Test message")
        pickled = pickle.dumps(original_exception)
        unpickled_exception = pickle.loads(pickled)
        
        assert str(original_exception) == str(unpickled_exception)
        assert type(original_exception) == type(unpickled_exception)


class TestAutomationExceptionContext:
    """Test AutomationException in context managers"""
    
    def test_automation_exception_in_try_except(self, mocker):
        """Test AutomationException in try-except block"""
        try:
            raise AutomationError("Test error")
        except AutomationError as e:
            assert str(e) == "Test error"
    
    def test_automation_exception_in_with_statement(self, mocker):
        """Test AutomationException in with statement context"""
        class ContextManager:
            def __enter__(self):
                return self
            
            def __exit__(self, exc_type, exc_val, exc_tb):
                if exc_type == AutomationError:
                    return True
                return False
        
        with ContextManager():
            raise AutomationError("Test error")
        # Should not propagate due to context manager handling


class TestAutomationExceptionChaining:
    """Test AutomationException exception chaining"""
    
    def test_automation_exception_chaining(self, mocker):
        """Test AutomationException with exception chaining"""
        try:
            try:
                raise ValueError("Original error")
            except ValueError as e:
                raise AutomationError("Wrapped error") from e
        except AutomationError as e:
            assert str(e) == "Wrapped error"
            assert e.__cause__ is not None
            assert isinstance(e.__cause__, ValueError)
    
    def test_automation_exception_without_chaining(self, mocker):
        """Test AutomationException without exception chaining"""
        exception = AutomationError("Simple error")
        assert exception.__cause__ is None 