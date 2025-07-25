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


class TestElementNotFoundError:
    """Test ElementNotFoundError"""
    
    def test_element_not_found_error_inheritance(self):
        """Test that ElementNotFoundError inherits from AutomationError"""
        error = ElementNotFoundError("Element not found")
        assert isinstance(error, AutomationError)


class TestElementStateError:
    """Test ElementStateError"""
    
    def test_element_state_error_inheritance(self):
        """Test that ElementStateError inherits from AutomationError"""
        error = ElementStateError("Invalid state")
        assert isinstance(error, AutomationError)


class TestTimeoutError:
    """Test TimeoutError"""
    
    def test_timeout_error_inheritance(self):
        """Test that TimeoutError inherits from AutomationError"""
        error = TimeoutError("Operation timed out")
        assert isinstance(error, AutomationError)


class TestBackendError:
    """Test BackendError"""
    
    def test_backend_error_inheritance(self):
        """Test that BackendError inherits from AutomationError"""
        error = BackendError("Backend failed")
        assert isinstance(error, AutomationError)


class TestConfigurationError:
    """Test ConfigurationError"""
    
    def test_configuration_error_inheritance(self):
        """Test that ConfigurationError inherits from AutomationError"""
        error = ConfigurationError("Invalid configuration")
        assert isinstance(error, AutomationError)


class TestValidationError:
    """Test ValidationError"""
    
    def test_validation_error_inheritance(self):
        """Test that ValidationError inherits from AutomationError"""
        error = ValidationError("Validation failed")
        assert isinstance(error, AutomationError)


class TestOCRError:
    """Test OCRError"""
    
    def test_ocr_error_inheritance(self):
        """Test that OCRError inherits from AutomationError"""
        error = OCRError("OCR failed")
        assert isinstance(error, AutomationError)


class TestVisualError:
    """Test VisualError"""
    
    def test_visual_error_inheritance(self):
        """Test that VisualError inherits from AutomationError"""
        error = VisualError("Visual operation failed")
        assert isinstance(error, AutomationError)


class TestInputError:
    """Test InputError"""
    
    def test_input_error_inheritance(self):
        """Test that InputError inherits from AutomationError"""
        error = InputError("Input operation failed")
        assert isinstance(error, AutomationError)


class TestWindowError:
    """Test WindowError"""
    
    def test_window_error_inheritance(self):
        """Test that WindowError inherits from AutomationError"""
        error = WindowError("Window operation failed")
        assert isinstance(error, AutomationError)


class TestWaitTimeout:
    """Test WaitTimeout"""
    
    def test_wait_timeout_inheritance(self):
        """Test that WaitTimeout inherits from AutomationError"""
        error = WaitTimeout("Wait timed out")
        assert isinstance(error, AutomationError) 