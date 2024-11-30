import time
from typing import Callable, Optional, Any
from functools import partial


class WaitTimeout(Exception):
    """Exception raised when wait condition times out"""
    pass


def wait_until(condition: Callable[[], bool],
               timeout: float = 10,
               poll_frequency: float = 0.5,
               error_message: str = None) -> bool:
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

    def __init__(self, automation):
        self.automation = automation

    def for_element(self, by: str, value: str, timeout: float = 10) -> Any:
        """Wait for element to be present"""
        def condition():
            element = self.automation.find_element(by, value)
            return element is not None

        wait_until(condition, timeout,
                  error_message=f"Element not found: {by}={value}")
        return self.automation.find_element(by, value)

    def for_element_visible(self, by: str, value: str, timeout: float = 10) -> Any:
        """Wait for element to be visible"""
        element = self.for_element(by, value, timeout)
        
        def condition():
            return element.visible

        wait_until(condition, timeout,
                  error_message=f"Element not visible: {by}={value}")
        return element

    def for_element_enabled(self, by: str, value: str, timeout: float = 10) -> Any:
        """Wait for element to be enabled"""
        element = self.for_element(by, value, timeout)
        
        def condition():
            return element.enabled

        wait_until(condition, timeout,
                  error_message=f"Element not enabled: {by}={value}")
        return element

    def for_element_text(self, by: str, value: str, text: str,
                        timeout: float = 10) -> Any:
        """Wait for element to have specific text"""
        element = self.for_element(by, value, timeout)
        
        def condition():
            return element.text == text

        wait_until(condition, timeout,
                  error_message=f"Element text mismatch: {by}={value}")
        return element

    def for_element_contains_text(self, by: str, value: str, text: str,
                                timeout: float = 10) -> Any:
        """Wait for element to contain specific text"""
        element = self.for_element(by, value, timeout)
        
        def condition():
            return text in element.text

        wait_until(condition, timeout,
                  error_message=f"Element does not contain text: {by}={value}")
        return element
