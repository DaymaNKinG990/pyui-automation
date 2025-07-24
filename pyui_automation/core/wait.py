import time
from typing import Callable, Optional, Any, TYPE_CHECKING
from .exceptions import WaitTimeout

if TYPE_CHECKING:
    from .session import AutomationSession


def wait_until(
    condition: Callable[[], bool],
    timeout: float = 10,
    poll_frequency: float = 0.05,  # Reduced to 50ms for more responsive testing
    error_message: Optional[str] = None
) -> bool:
    """
    Wait until condition is true or timeout occurs
    
    Args:
        condition: Function that returns bool
        timeout: Maximum time to wait in seconds
        poll_frequency: How often to check condition in seconds
        error_message: Custom error message for timeout
    
    Returns:
        True if condition was met, raises WaitTimeout otherwise
    """
    if not callable(condition):
        raise TypeError("condition must be callable")
    if timeout < 0:
        raise ValueError("timeout must be non-negative")
    if poll_frequency < 0:
        raise ValueError("poll_frequency must be non-negative")
    # For short timeouts, use a shorter poll frequency
    if timeout < poll_frequency:
        poll_frequency = timeout / 4

    end_time = time.time() + timeout
    
    while time.time() < end_time:
        if condition():
            return True
        time.sleep(poll_frequency)
    
    if error_message:
        raise WaitTimeout(error_message)
    raise WaitTimeout(f"Timed out after {timeout} seconds")


class ElementWaits:
    """Element wait conditions"""

    def __init__(self, automation: 'AutomationSession') -> None:
        """
        Initialize ElementWaits.
        
        Args:
            automation: AutomationSession instance
        """
        self.automation = automation

    def wait_until(
        self,
        condition: Callable[[], bool],
        timeout: float = 10,
        poll_frequency: float = 0.05,
        error_message: Optional[str] = None
    ) -> bool:
        """
        Wait until condition is true or timeout occurs
        
        Args:
            condition: Function that returns bool
            timeout: Maximum time to wait in seconds
            poll_frequency: How often to check condition in seconds
            error_message: Custom error message for timeout
        
        Returns:
            True if condition was met, raises WaitTimeout otherwise
        """
        return wait_until(condition, timeout, poll_frequency, error_message)

    def for_element_by_object_name(self, object_name: str, timeout: float = 10) -> Any:
        """Wait for element by object_name to appear."""
        if not isinstance(object_name, str) or not object_name:
            raise ValueError("object_name must be a non-empty string")
        found_element = [None]
        def condition():
            element = self.automation.backend.find_element_by_object_name(object_name)
            if element is not None:
                found_element[0] = element
                return True
            return False
        self.wait_until(condition, timeout, error_message=f"Element not found with object_name={object_name}")
        return found_element[0]

    def for_element_by_widget_type(self, widget_type: str, timeout: float = 10) -> Any:
        """Wait for element by widget_type to appear."""
        if not isinstance(widget_type, str) or not widget_type:
            raise ValueError("widget_type must be a non-empty string")
        found_element = [None]
        def condition():
            element = self.automation.backend.find_element_by_widget_type(widget_type)
            if element is not None:
                found_element[0] = element
                return True
            return False
        self.wait_until(condition, timeout, error_message=f"Element not found with widget_type={widget_type}")
        return found_element[0]

    def for_element_by_text(self, text: str, timeout: float = 10) -> Any:
        """Wait for element by visible text to appear."""
        if not isinstance(text, str) or not text:
            raise ValueError("text must be a non-empty string")
        found_element = [None]
        def condition():
            element = self.automation.backend.find_element_by_text(text)
            if element is not None:
                found_element[0] = element
                return True
            return False
        self.wait_until(condition, timeout, error_message=f"Element not found with text={text}")
        return found_element[0]

    def for_element_by_property(self, property_name: str, value: str, timeout: float = 10) -> Any:
        """Wait for element by property to appear."""
        if not isinstance(property_name, str) or not property_name:
            raise ValueError("property_name must be a non-empty string")
        if not isinstance(value, str) or not value:
            raise ValueError("value must be a non-empty string")
        found_element = [None]
        def condition():
            element = self.automation.backend.find_element_by_property(property_name, value)
            if element is not None:
                found_element[0] = element
                return True
            return False
        self.wait_until(condition, timeout, error_message=f"Element not found with {property_name}={value}")
        return found_element[0]

    def for_element_pattern(
        self,
        element: Any,
        pattern_name: str,
        timeout: float = 10
    ) -> bool:
        """
        Wait for element to support pattern

        Args:
            element: Element to wait for
            pattern_name: Name of the pattern to wait for
            timeout: Maximum time to wait in seconds

        Returns:
            True if element supports the pattern, raises WaitTimeout otherwise
        """
        if not hasattr(element, 'has_pattern') or not callable(getattr(element, 'has_pattern', None)):
            raise TypeError("element must have a callable has_pattern method")
        if not isinstance(pattern_name, str) or not pattern_name:
            raise ValueError("pattern_name must be a non-empty string")
        return self.wait_until(
            lambda: element.has_pattern(pattern_name),
            timeout,
            error_message=f"Pattern not supported: {pattern_name}"
        )

    # Удалены устаревшие методы for_element_text и for_element_contains_text (универсальные by/value)
