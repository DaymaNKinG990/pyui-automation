from typing import Optional, List, Any
from .base import BaseLocator, LocatorStrategy, ByName, ByAXIdentifier, ByAXTitle, ByAXRole, ByAXDescription, ByAXValue


class MacOSLocator(BaseLocator):
    """
    macOS Accessibility API locator implementation.
    Supports element finding strategies using macOS Accessibility framework.
    """

    def _find_element_impl(self, strategy: LocatorStrategy) -> Optional[Any]:
        """
        Find a single element using the specified strategy.
        
        Args:
            strategy: LocatorStrategy instance defining the search method
            
        Returns:
            Accessibility element if found, None otherwise
        """
        try:
            if isinstance(strategy, ByName):
                return self._find_element_by_name(strategy.value)
            elif isinstance(strategy, ByAXIdentifier):
                return self._find_element_by_ax_identifier(strategy.value)
            elif isinstance(strategy, ByAXTitle):
                return self._find_element_by_ax_title(strategy.value)
            elif isinstance(strategy, ByAXRole):
                return self._find_element_by_ax_role(strategy.value)
            elif isinstance(strategy, ByAXDescription):
                return self._find_element_by_ax_description(strategy.value)
            elif isinstance(strategy, ByAXValue):
                return self._find_element_by_ax_value(strategy.value)
            else:
                if self.logger:
                    self.logger.error(f"Unsupported locator strategy: {type(strategy).__name__}")
                return None
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding element with strategy {type(strategy).__name__}: {str(e)}")
            return None

    def _find_elements_impl(self, strategy: LocatorStrategy) -> List[Any]:
        """
        Find multiple elements using the specified strategy.
        
        Args:
            strategy: LocatorStrategy instance defining the search method
            
        Returns:
            List of Accessibility elements
        """
        try:
            if isinstance(strategy, ByName):
                return self._find_elements_by_name(strategy.value)
            elif isinstance(strategy, ByAXIdentifier):
                return self._find_elements_by_ax_identifier(strategy.value)
            elif isinstance(strategy, ByAXTitle):
                return self._find_elements_by_ax_title(strategy.value)
            elif isinstance(strategy, ByAXRole):
                return self._find_elements_by_ax_role(strategy.value)
            elif isinstance(strategy, ByAXDescription):
                return self._find_elements_by_ax_description(strategy.value)
            elif isinstance(strategy, ByAXValue):
                return self._find_elements_by_ax_value(strategy.value)
            else:
                if self.logger:
                    self.logger.error(f"Unsupported locator strategy: {type(strategy).__name__}")
                return []
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements with strategy {type(strategy).__name__}: {str(e)}")
            return []

    def _find_element_by_name(self, name: str) -> Optional[Any]:
        """Find element by name using Accessibility API"""
        try:
            return self.backend._find_element_recursive(self.backend.root, "name", name)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding element by name: {str(e)}")
            return None

    def _find_elements_by_name(self, name: str) -> List[Any]:
        """Find elements by name using Accessibility API"""
        try:
            results = []
            self.backend._find_elements_recursive(self.backend.root, "name", name, results)
            return results
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements by name: {str(e)}")
            return []

    def _find_element_by_ax_identifier(self, identifier: str) -> Optional[Any]:
        """Find element by AXIdentifier using Accessibility API"""
        try:
            return self.backend._find_element_recursive(self.backend.root, "ax_identifier", identifier)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding element by AXIdentifier: {str(e)}")
            return None

    def _find_elements_by_ax_identifier(self, identifier: str) -> List[Any]:
        """Find elements by AXIdentifier using Accessibility API"""
        try:
            results = []
            self.backend._find_elements_recursive(self.backend.root, "ax_identifier", identifier, results)
            return results
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements by AXIdentifier: {str(e)}")
            return []

    def _find_element_by_ax_title(self, title: str) -> Optional[Any]:
        """Find element by AXTitle using Accessibility API"""
        try:
            return self.backend._find_element_recursive(self.backend.root, "ax_title", title)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding element by AXTitle: {str(e)}")
            return None

    def _find_elements_by_ax_title(self, title: str) -> List[Any]:
        """Find elements by AXTitle using Accessibility API"""
        try:
            results = []
            self.backend._find_elements_recursive(self.backend.root, "ax_title", title, results)
            return results
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements by AXTitle: {str(e)}")
            return []

    def _find_element_by_ax_role(self, role: str) -> Optional[Any]:
        """Find element by AXRole using Accessibility API"""
        try:
            return self.backend._find_element_recursive(self.backend.root, "ax_role", role)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding element by AXRole: {str(e)}")
            return None

    def _find_elements_by_ax_role(self, role: str) -> List[Any]:
        """Find elements by AXRole using Accessibility API"""
        try:
            results = []
            self.backend._find_elements_recursive(self.backend.root, "ax_role", role, results)
            return results
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements by AXRole: {str(e)}")
            return []

    def _find_element_by_ax_description(self, description: str) -> Optional[Any]:
        """Find element by AXDescription using Accessibility API"""
        try:
            return self.backend._find_element_recursive(self.backend.root, "ax_description", description)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding element by AXDescription: {str(e)}")
            return None

    def _find_elements_by_ax_description(self, description: str) -> List[Any]:
        """Find elements by AXDescription using Accessibility API"""
        try:
            results = []
            self.backend._find_elements_recursive(self.backend.root, "ax_description", description, results)
            return results
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements by AXDescription: {str(e)}")
            return []

    def _find_element_by_ax_value(self, value: str) -> Optional[Any]:
        """Find element by AXValue using Accessibility API"""
        try:
            return self.backend._find_element_recursive(self.backend.root, "ax_value", value)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding element by AXValue: {str(e)}")
            return None

    def _find_elements_by_ax_value(self, value: str) -> List[Any]:
        """Find elements by AXValue using Accessibility API"""
        try:
            results = []
            self.backend._find_elements_recursive(self.backend.root, "ax_value", value, results)
            return results
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements by AXValue: {str(e)}")
            return [] 