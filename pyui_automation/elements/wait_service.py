"""
Element Wait Service - handles element wait operations.

Responsible for:
- Waiting for elements to be enabled
- Waiting for elements to be clickable
- Waiting for element state changes
"""
# Python imports
from typing import Optional, TYPE_CHECKING, Callable, Any
import time
from logging import getLogger

# Local imports
if TYPE_CHECKING:
    from .base_element import BaseElement


class ElementWaitService:
    """Service for element waiting operations"""
    
    def __init__(self, session: Any) -> None:
        """
        Initialize the ElementWaitService.

        Args:
            session (Any): The session to use for the wait service.
        """
        self._session = session
        self._logger = getLogger(__name__)
    
    def wait_until_enabled(self, element: "BaseElement", timeout: Optional[float] = None) -> bool:
        """
        Wait until element is enabled.

        Args:
            element (BaseElement): The element to wait for.
            timeout (Optional[float]): The timeout in seconds.
        """
        timeout = timeout or self._session.config.default_timeout
        if timeout is None:
            timeout = 10.0
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if element.is_enabled():
                self._logger.debug("Element is enabled")
                return True
            time.sleep(self._session.config.default_interval)
        
        self._logger.warning(f"Element not enabled after {timeout} seconds")
        return False
    
    def wait_until_clickable(self, element: "BaseElement", timeout: Optional[float] = None) -> bool:
        """
        Wait until element is clickable (enabled and visible).

        Args:
            element (BaseElement): The element to wait for.
            timeout (Optional[float]): The timeout in seconds.
        """
        timeout = timeout or self._session.config.default_timeout
        if timeout is None:
            timeout = 10.0
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if element.is_enabled() and element.is_displayed():
                self._logger.debug("Element is clickable")
                return True
            time.sleep(self._session.config.default_interval)
        
        self._logger.warning(f"Element not clickable after {timeout} seconds")
        return False
    
    def wait_until_checked(self, element: "BaseElement", timeout: float = 10) -> bool:
        """
        Wait until element is checked.

        Args:
            element (BaseElement): The element to wait for.
            timeout (float): The timeout in seconds.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if element.is_checked:
                self._logger.debug("Element is checked")
                return True
            time.sleep(self._session.config.default_interval)
        
        self._logger.warning(f"Element not checked after {timeout} seconds")
        return False
    
    def wait_until_unchecked(self, element: "BaseElement", timeout: float = 10) -> bool:
        """
        Wait until element is unchecked.

        Args:
            element (BaseElement): The element to wait for.
            timeout (float): The timeout in seconds.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not element.is_checked:
                self._logger.debug("Element is unchecked")
                return True
            time.sleep(self._session.config.default_interval)
        
        self._logger.warning(f"Element not unchecked after {timeout} seconds")
        return False
    
    def wait_until_expanded(self, element: "BaseElement", timeout: float = 10) -> bool:
        """
        Wait until element is expanded.

        Args:
            element (BaseElement): The element to wait for.
            timeout (float): The timeout in seconds.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if element.is_expanded:
                self._logger.debug("Element is expanded")
                return True
            time.sleep(self._session.config.default_interval)
        
        self._logger.warning(f"Element not expanded after {timeout} seconds")
        return False
    
    def wait_until_collapsed(self, element: "BaseElement", timeout: float = 10) -> bool:
        """
        Wait until element is collapsed.

        Args:
            element (BaseElement): The element to wait for.
            timeout (float): The timeout in seconds.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if not element.is_expanded:
                self._logger.debug("Element is collapsed")
                return True
            time.sleep(self._session.config.default_interval)
        
        self._logger.warning(f"Element not collapsed after {timeout} seconds")
        return False
    
    def wait_until_value_is(self, element: "BaseElement", expected_value: str, timeout: Optional[float] = None) -> bool:
        """
        Wait until element value equals expected value.

        Args:
            element (BaseElement): The element to wait for.
            expected_value (str): The expected value.
            timeout (Optional[float]): The timeout in seconds.
        """
        timeout = timeout or self._session.config.default_timeout
        if timeout is None:
            timeout = 10.0
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            current_value = element.value
            if current_value == expected_value:
                self._logger.debug(f"Element value is {expected_value}")
                return True
            time.sleep(self._session.config.default_interval)
        
        self._logger.warning(f"Element value not {expected_value} after {timeout} seconds")
        return False
    
    def wait_for_enabled(self, element: "BaseElement", timeout: float = 10) -> bool:
        """Alias for wait_until_enabled"""
        return self.wait_until_enabled(element, timeout)
    
    def wait_for_visible(self, element: "BaseElement", timeout: float = 10) -> bool:
        """
        Wait until element is visible.

        Args:
            element (BaseElement): The element to wait for.
            timeout (float): The timeout in seconds.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if element.is_displayed():
                self._logger.debug("Element is visible")
                return True
            time.sleep(self._session.config.default_interval)
        
        self._logger.warning(f"Element not visible after {timeout} seconds")
        return False
    
    def wait_for_condition(self, condition: Callable[[], bool], timeout: float = 10) -> bool:
        """
        Wait until condition is true.

        Args:
            condition (Callable[[], bool]): The condition to wait for.
            timeout (float): The timeout in seconds.
        """
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if condition():
                self._logger.debug("Condition is true")
                return True
            time.sleep(self._session.config.default_interval)
        
        self._logger.warning(f"Condition not true after {timeout} seconds")
        return False 