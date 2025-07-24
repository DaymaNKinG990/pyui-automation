from typing import Optional, List, Any
from .base import BaseLocator, LocatorStrategy, ByName, ByClassName, ByAutomationId, ByControlType, ByXPath, ByAccessibilityId


class WindowsLocator(BaseLocator):
    """
    Windows UI Automation locator implementation.
    Supports various element finding strategies using UI Automation API.
    """

    def _find_element_impl(self, strategy: LocatorStrategy) -> Optional[Any]:
        """
        Find a single element using the specified strategy.
        
        Args:
            strategy: LocatorStrategy instance defining the search method
            
        Returns:
            UI Automation element if found, None otherwise
        """
        try:
            if isinstance(strategy, ByName):
                return self.backend.find_element_by_text(strategy.value)
            elif isinstance(strategy, ByClassName):
                return self.backend.find_element_by_property("class", strategy.value)
            elif isinstance(strategy, ByAutomationId):
                return self.backend.find_element_by_object_name(strategy.value)
            elif isinstance(strategy, ByControlType):
                return self.backend.find_element_by_widget_type(strategy.value)
            elif isinstance(strategy, ByXPath):
                return self._find_element_by_xpath(strategy.value)
            elif isinstance(strategy, ByAccessibilityId):
                return self.backend.find_element_by_property("automation_id", strategy.value)
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
            List of UI Automation elements
        """
        try:
            if isinstance(strategy, ByName):
                return self.backend.find_elements_by_text(strategy.value)
            elif isinstance(strategy, ByClassName):
                return self.backend.find_elements_by_property("class", strategy.value)
            elif isinstance(strategy, ByAutomationId):
                return self.backend.find_elements_by_object_name(strategy.value)
            elif isinstance(strategy, ByControlType):
                return self.backend.find_elements_by_widget_type(strategy.value)
            elif isinstance(strategy, ByXPath):
                return self._find_elements_by_xpath(strategy.value)
            elif isinstance(strategy, ByAccessibilityId):
                return self.backend.find_elements_by_property("automation_id", strategy.value)
            else:
                if self.logger:
                    self.logger.error(f"Unsupported locator strategy: {type(strategy).__name__}")
                return []
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements with strategy {type(strategy).__name__}: {str(e)}")
            return []

    def _find_element_by_xpath(self, xpath: str) -> Optional[Any]:
        """
        Find element by XPath (basic implementation).
        
        Args:
            xpath: XPath expression
            
        Returns:
            UI Automation element if found, None otherwise
        """
        # Basic XPath implementation - can be extended for complex queries
        try:
            # Simple XPath parsing for common cases
            if xpath.startswith("//"):
                # Remove // prefix
                xpath = xpath[2:]
            
            # Handle element type queries like "//button"
            if "/" not in xpath and xpath in ["button", "edit", "text", "window", "menu", "list", "tree", "checkbox", "radio", "combobox", "slider", "progressbar", "scrollbar", "tab"]:
                return self.backend.find_element_by_widget_type(xpath)
            
            # Handle attribute queries like "//*[@Name='value']"
            if "[@" in xpath and "=" in xpath:
                # Extract attribute and value
                attr_start = xpath.find("[@") + 2
                attr_end = xpath.find("=", attr_start)
                attr_name = xpath[attr_start:attr_end]
                
                value_start = xpath.find("'", attr_end) + 1
                value_end = xpath.find("'", value_start)
                attr_value = xpath[value_start:value_end]
                
                if attr_name.lower() == "name":
                    return self.backend.find_element_by_text(attr_value)
                elif attr_name.lower() == "automationid":
                    return self.backend.find_element_by_object_name(attr_value)
                elif attr_name.lower() == "class":
                    return self.backend.find_element_by_property("class", attr_value)
            
            if self.logger:
                self.logger.warning(f"Complex XPath not supported: {xpath}")
            return None
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error parsing XPath {xpath}: {str(e)}")
            return None

    def _find_elements_by_xpath(self, xpath: str) -> List[Any]:
        """
        Find elements by XPath (basic implementation).
        
        Args:
            xpath: XPath expression
            
        Returns:
            List of UI Automation elements
        """
        # Basic XPath implementation for multiple elements
        try:
            # Simple XPath parsing for common cases
            if xpath.startswith("//"):
                xpath = xpath[2:]
            
            # Handle element type queries
            if "/" not in xpath and xpath in ["button", "edit", "text", "window", "menu", "list", "tree", "checkbox", "radio", "combobox", "slider", "progressbar", "scrollbar", "tab"]:
                return self.backend.find_elements_by_widget_type(xpath)
            
            # Handle attribute queries
            if "[@" in xpath and "=" in xpath:
                attr_start = xpath.find("[@") + 2
                attr_end = xpath.find("=", attr_start)
                attr_name = xpath[attr_start:attr_end]
                
                value_start = xpath.find("'", attr_end) + 1
                value_end = xpath.find("'", value_start)
                attr_value = xpath[value_start:value_end]
                
                if attr_name.lower() == "name":
                    return self.backend.find_elements_by_text(attr_value)
                elif attr_name.lower() == "automationid":
                    return self.backend.find_elements_by_object_name(attr_value)
                elif attr_name.lower() == "class":
                    return self.backend.find_elements_by_property("class", attr_value)
            
            if self.logger:
                self.logger.warning(f"Complex XPath not supported: {xpath}")
            return []
            
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error parsing XPath {xpath}: {str(e)}")
            return []
