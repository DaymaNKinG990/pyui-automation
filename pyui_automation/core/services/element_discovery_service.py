"""
Element Discovery Service - handles all element discovery operations.

Responsible for:
- Finding elements using locator strategies
- Finding elements by various criteria
- Element search with timeouts
"""

from typing import Optional, List, TYPE_CHECKING
from logging import getLogger

if TYPE_CHECKING:
    from ..session import AutomationSession
    from ...backends.base_backend import BaseBackend
    from ...locators.base import BaseLocator

# Local imports
from ...elements.base_element import BaseElement
from ...locators.base import LocatorStrategy
from ..interfaces.ielement_discovery_service import IElementDiscoveryService


class ElementDiscoveryService(IElementDiscoveryService):
    """Service for element discovery operations"""
    
    def __init__(self, backend: 'BaseBackend', locator: 'BaseLocator', session: 'AutomationSession'):
        self._backend = backend
        self._locator = locator
        self._session = session
        self._logger = getLogger(__name__)
    
    def find_element(self, strategy: LocatorStrategy) -> Optional[BaseElement]:
        """Find element using locator strategy"""
        try:
            native_element = self._locator.find_element(strategy)
            return BaseElement(native_element, self._session) if native_element else None
        except Exception as e:
            self._logger.error(f"Error finding element with strategy {type(strategy).__name__}: {str(e)}")
            return None
    
    def find_elements(self, strategy: LocatorStrategy) -> List[BaseElement]:
        """Find elements using locator strategy"""
        try:
            native_elements = self._locator.find_elements(strategy)
            return [BaseElement(element, self._session) for element in native_elements]
        except Exception as e:
            self._logger.error(f"Error finding elements with strategy {type(strategy).__name__}: {str(e)}")
            return []
    
    def find_element_with_timeout(self, strategy: LocatorStrategy, timeout: float = 10.0) -> Optional[BaseElement]:
        """Find element with timeout"""
        try:
            return self._locator.find_element_with_timeout(strategy, timeout)
        except Exception as e:
            self._logger.error(f"Error finding element with timeout: {str(e)}")
            return None
    
    def find_element_by_object_name(self, object_name: str, timeout: float = 0) -> Optional[BaseElement]:
        """Find element by object name"""
        try:
            from ...locators import ByName
            strategy = ByName(_value=object_name)
            if timeout > 0:
                return self.find_element_with_timeout(strategy, timeout)
            return self.find_element(strategy)
        except Exception as e:
            self._logger.error(f"Error finding element by object name: {str(e)}")
            return None
    
    def find_elements_by_object_name(self, object_name: str) -> List[BaseElement]:
        """Find elements by object name"""
        try:
            from ...locators import ByName
            strategy = ByName(_value=object_name)
            return self.find_elements(strategy)
        except Exception as e:
            self._logger.error(f"Error finding elements by object name: {str(e)}")
            return []
    
    def find_element_by_widget_type(self, widget_type: str, timeout: float = 0) -> Optional[BaseElement]:
        """Find element by widget type"""
        try:
            from ...locators import ByControlType
            strategy = ByControlType(_value=widget_type)
            if timeout > 0:
                return self.find_element_with_timeout(strategy, timeout)
            return self.find_element(strategy)
        except Exception as e:
            self._logger.error(f"Error finding element by widget type: {str(e)}")
            return None
    
    def find_elements_by_widget_type(self, widget_type: str) -> List[BaseElement]:
        """Find elements by widget type"""
        try:
            from ...locators import ByControlType
            strategy = ByControlType(_value=widget_type)
            return self.find_elements(strategy)
        except Exception as e:
            self._logger.error(f"Error finding elements by widget type: {str(e)}")
            return []
    
    def find_element_by_text(self, text: str, timeout: float = 0) -> Optional[BaseElement]:
        """Find element by text"""
        try:
            from ...locators import ByName
            strategy = ByName(_value=text)
            if timeout > 0:
                return self.find_element_with_timeout(strategy, timeout)
            return self.find_element(strategy)
        except Exception as e:
            self._logger.error(f"Error finding element by text: {str(e)}")
            return None
    
    def find_elements_by_text(self, text: str) -> List[BaseElement]:
        """Find elements by text"""
        try:
            from ...locators import ByName
            strategy = ByName(_value=text)
            return self.find_elements(strategy)
        except Exception as e:
            self._logger.error(f"Error finding elements by text: {str(e)}")
            return []
    
    def find_element_by_property(self, property_name: str, value: str, timeout: float = 0) -> Optional[BaseElement]:
        """Find element by property"""
        try:
            # This is a simplified implementation
            # In a real scenario, you might need platform-specific locators
            from ...locators import ByAutomationId
            strategy = ByAutomationId(_value=value)
            if timeout > 0:
                return self.find_element_with_timeout(strategy, timeout)
            return self.find_element(strategy)
        except Exception as e:
            self._logger.error(f"Error finding element by property: {str(e)}")
            return None
    
    def find_elements_by_property(self, property_name: str, value: str) -> List[BaseElement]:
        """Find elements by property"""
        try:
            from ...locators import ByAutomationId
            strategy = ByAutomationId(_value=value)
            return self.find_elements(strategy)
        except Exception as e:
            self._logger.error(f"Error finding elements by property: {str(e)}")
            return []
    
    def get_active_window(self) -> Optional[BaseElement]:
        """Get active window as element"""
        try:
            active_window = self._backend.get_active_window()
            if active_window:
                return BaseElement(active_window, self._session)
            return None
        except Exception as e:
            self._logger.error(f"Error getting active window: {str(e)}")
            return None 