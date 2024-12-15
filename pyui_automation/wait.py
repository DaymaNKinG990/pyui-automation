import time
from typing import Callable, Optional, Any, TYPE_CHECKING
from .exceptions import WaitTimeout

if TYPE_CHECKING:
    from .core.session import AutomationSession


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

    def for_element(self, by: str, value: str, timeout: float = 10) -> Any:
        """
        Wait for element to be present
        
        Args:
            by: Strategy to find element (e.g., 'id', 'name', 'class', 'xpath', etc.)
            value: Value to search for using the specified strategy
            timeout: Maximum time to wait in seconds
        
        Returns:
            Found element
        """
        found_element: list[Any] = [None]  # Use list to store element in closure
        
        def condition() -> bool:
            element = self.automation.backend.find_element(by, value)  # Call backend directly with positional args
            if element is not None:
                found_element[0] = element  # Store found element
                return True
            return False

        self.wait_until(
            condition,
            timeout,
            error_message=f"Element not found with {by}={value}"
        )
        return found_element[0]

    def for_element_visible(self, element: Any, timeout: float = 10) -> bool:
        """Wait for element to become visible"""
        def condition():
            return not element.is_offscreen

        return self.wait_until(
            condition,
            timeout,
            error_message="Element not visible"
        )

    def for_element_enabled(self, element: Any, timeout: float = 10) -> bool:
        """Wait for element to become enabled"""
        def condition():
            return element.is_enabled

        return self.wait_until(
            condition,
            timeout,
            error_message="Element not enabled"
        )

    def for_element_property(
        self,
        element: Any,
        property_name: str,
        expected_value: Any,
        timeout: float = 10
    ) -> bool:
        """Wait for element property to match expected value"""
        def condition():
            return element.get_property(property_name) == expected_value

        return self.wait_until(
            condition,
            timeout,
            error_message="Property mismatch"
        )

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
        return self.wait_until(
            lambda: element.has_pattern(pattern_name),
            timeout,
            error_message=f"Pattern not supported: {pattern_name}"
        )

    def for_element_text(
        self,
        by: str,
        value: str,
        text: str,
        timeout: float = 10
    ) -> Any:
        """
        Wait for element to have specific text

        Args:
            by: Strategy to find element (e.g., 'id', 'name', 'class', 'xpath', etc.)
            value: Value to search for using the specified strategy
            text: Expected text content of the element
            timeout: Maximum time to wait in seconds

        Returns:
            Found element

        Raises:
            WaitTimeout: If element text does not match expected value
        """
        element = self.for_element(by, value, timeout)
        
        def condition():
            return element.text == text

        self.wait_until(condition, timeout,
                  error_message=f"Element text mismatch: {by}={value}")
        return element

    def for_element_contains_text(
        self,
        by: str,
        value: str,
        text: str,
        timeout: float = 10
    ) -> Any:
        """
        Wait for element to contain specific text

        Args:
            by: Strategy to find element (e.g., 'id', 'name', 'class', 'xpath', etc.)
            value: Value to search for using the specified strategy
            text: Substring expected to be present in the element's text content
            timeout: Maximum time to wait in seconds

        Returns:
            Found element

        Raises:
            WaitTimeout: If the element does not contain the specified text within the timeout period
        """
        element = self.for_element(by, value, timeout)
        
        def condition():
            return text in element.text

        self.wait_until(condition, timeout,
                  error_message=f"Element text does not contain: {text}")
        return element
