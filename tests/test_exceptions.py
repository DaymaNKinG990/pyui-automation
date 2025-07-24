import pytest
from pyui_automation.core.exceptions import (
    AutomationError,
    ElementNotFoundError,
    ElementStateError,
    TimeoutError,
    BackendError,
    ConfigurationError,
    ValidationError,
    VisualError,
    OCRError,
    InputError,
    WindowError,
    WaitTimeout,
)


def test_automation_error():
    """Test base automation error"""
    with pytest.raises(AutomationError) as exc:
        raise AutomationError("Test error")
    assert str(exc.value) == "Test error"
    assert isinstance(exc.value, Exception)

def test_element_not_found_error():
    """Test element not found error"""
    with pytest.raises(ElementNotFoundError) as exc:
        raise ElementNotFoundError("Element '#test' not found")
    assert str(exc.value) == "Element '#test' not found"
    assert isinstance(exc.value, AutomationError)

def test_element_state_error():
    """Test element state error"""
    with pytest.raises(ElementStateError) as exc:
        raise ElementStateError("Element not enabled")
    assert str(exc.value) == "Element not enabled"
    assert isinstance(exc.value, AutomationError)

def test_timeout_error():
    """Test timeout error"""
    from pyui_automation.core.exceptions import TimeoutError as AutomationTimeoutError
    with pytest.raises(AutomationTimeoutError) as exc:
        raise AutomationTimeoutError("Operation timed out after 30s")
    assert str(exc.value) == "Operation timed out after 30s"
    assert isinstance(exc.value, AutomationError)

def test_backend_error():
    """Test backend error"""
    with pytest.raises(BackendError) as exc:
        raise BackendError("Failed to initialize Windows backend")
    assert str(exc.value) == "Failed to initialize Windows backend"
    assert isinstance(exc.value, AutomationError)

def test_configuration_error():
    """Test configuration error"""
    with pytest.raises(ConfigurationError) as exc:
        raise ConfigurationError("Invalid timeout value: -1")
    assert str(exc.value) == "Invalid timeout value: -1"
    assert isinstance(exc.value, AutomationError)

def test_validation_error():
    """Test validation error"""
    with pytest.raises(ValidationError) as exc:
        raise ValidationError("Invalid selector format")
    assert str(exc.value) == "Invalid selector format"
    assert isinstance(exc.value, AutomationError)

def test_ocr_error():
    """Test OCR error"""
    with pytest.raises(OCRError) as exc:
        raise OCRError("Failed to initialize OCR engine")
    assert str(exc.value) == "Failed to initialize OCR engine"
    assert isinstance(exc.value, AutomationError)

def test_visual_error():
    """Test visual error"""
    with pytest.raises(VisualError) as exc:
        raise VisualError("Failed to load template image")
    assert str(exc.value) == "Failed to load template image"
    assert isinstance(exc.value, AutomationError)

def test_input_error():
    """Test input error"""
    with pytest.raises(InputError) as exc:
        raise InputError("Invalid key combination")
    assert str(exc.value) == "Invalid key combination"
    assert isinstance(exc.value, AutomationError)

def test_window_error():
    """Test window error"""
    with pytest.raises(WindowError) as exc:
        raise WindowError("Window not found: Calculator")
    assert str(exc.value) == "Window not found: Calculator"
    assert isinstance(exc.value, AutomationError)

def test_wait_timeout():
    """Test wait timeout error"""
    with pytest.raises(WaitTimeout) as exc:
        raise WaitTimeout("Condition not met after 10s")
    assert str(exc.value) == "Condition not met after 10s"
    assert isinstance(exc.value, AutomationError)

def test_exception_inheritance():
    """Test exception inheritance relationships"""
    exceptions = [
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
    ]
    
    # All exceptions should inherit from AutomationError
    for exc_class in exceptions:
        assert issubclass(exc_class, AutomationError)
        
    # AutomationError should inherit from Exception
    assert issubclass(AutomationError, Exception)

def test_exception_with_nested_data():
    """Test exceptions with nested error data"""
    original_error = ValueError("Original error")
    with pytest.raises(AutomationError) as exc:
        try:
            raise original_error
        except ValueError as e:
            raise AutomationError("Wrapped error") from e
    
    assert str(exc.value) == "Wrapped error"
    assert exc.value.__cause__ == original_error

def test_exception_no_message():
    exc = AutomationError()
    assert str(exc) == ""
    assert exc.args == ()
    exc2 = ElementNotFoundError()
    assert str(exc2) == ""
    assert exc2.args == ()

def test_exception_non_string_message():
    exc = AutomationError(123)
    assert str(exc) == "123"
    exc2 = ElementNotFoundError({'a': 1})
    assert str(exc2) == "{'a': 1}"
    assert exc2.args[0] == {'a': 1}

def test_exception_pickle():
    import pickle
    exc = AutomationError("msg")
    data = pickle.dumps(exc)
    exc2 = pickle.loads(data)
    assert isinstance(exc2, AutomationError)
    assert str(exc2) == "msg"

def test_exception_cause_context():
    try:
        try:
            raise ValueError("inner")
        except ValueError as e:
            raise AutomationError("outer") from e
    except AutomationError as exc:
        assert isinstance(exc.__cause__, ValueError)
        assert exc.__context__ is exc.__cause__
        assert str(exc) == "outer"
