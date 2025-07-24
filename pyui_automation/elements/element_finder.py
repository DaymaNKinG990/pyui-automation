"""
Element finder for dynamic element discovery.

This module provides functionality to find elements and their children
based on various properties and attributes.
"""
# Python imports
from typing import Any, List, Optional, Callable
from logging import getLogger

# Local imports
from .properties import Property, ELEMENT_PROPERTIES, StringProperty, BoolProperty


class ElementFinder:
    """Helper class for finding elements based on properties."""
    
    def __init__(self, element: Any) -> None:
        """
        Initialize element finder.
        
        Args:
            element: Native element reference
        """
        self._element = element
        self._logger = getLogger(__name__)
    
    def find_child_by_property(
        self,
        property_name: str,
        expected_value: Any, 
        property_type: Optional[type[Property]] = None
    ) -> Optional[Any]:
        """
        Find child element by property value.
        
        Args:
            property_name: Name of the property to check
            expected_value: Expected value of the property
            property_type: Type of property (optional, auto-detected if not provided)
            
        Returns:
            Found child element or None
        """
        try:
            children = self._get_children()
            if not children:
                self._logger.warning("No children found")
                return None
            self._logger.debug(f"Found {len(children)} children")

            # Auto-detect property type if not provided
            if property_type is None:
                property_type = self._detect_property_type(property_name)
            self._logger.debug(f"Detected property type: {property_type}")

            for child in children:
                property_obj = property_type(property_name, child)
                if property_obj.get_value() == expected_value:
                    self._logger.debug(f"Found child by property: {property_name}")
                    return child
            
            self._logger.warning("No child found by property")
            return None
        except Exception:
            self._logger.error(f"Failed to find child by property: {property_name}")
            return None
    
    def find_children_by_property(
        self,
        property_name: str,
        expected_value: Any,
        property_type: Optional[type[Property]] = None
    ) -> List[Any]:
        """
        Find all child elements by property value.
        
        Args:
            property_name: Name of the property to check
            expected_value: Expected value of the property
            property_type: Type of property (optional, auto-detected if not provided)
            
        Returns:
            List of found child elements
        """
        try:
            children = self._get_children()
            if not children:
                self._logger.warning("No children found")
                return []
            self._logger.debug(f"Found {len(children)} children")

            # Auto-detect property type if not provided
            if property_type is None:
                property_type = self._detect_property_type(property_name)
            self._logger.debug(f"Detected property type: {property_type}")

            found_children = []
            for child in children:
                property_obj = property_type(property_name, child)
                if property_obj.get_value() == expected_value:
                    self._logger.debug(f"Found child by property: {property_name}")
                    found_children.append(child)
            
            self._logger.warning("No children found by property")
            return found_children
        except Exception:
            self._logger.error(f"Failed to find children by property: {property_name}")
            return []
    
    def find_child_by_predicate(self, predicate: Callable[[Any], bool]) -> Optional[Any]:
        """
        Find child element using custom predicate function.
        
        Args:
            predicate: Function that takes an element and returns True if it matches
            
        Returns:
            Found child element or None
        """
        try:
            children = self._get_children()
            if not children:
                self._logger.warning("No children found")
                return None
            
            for child in children:
                if predicate(child):
                    self._logger.debug("Found child by predicate")
                    return child
            
            self._logger.warning("No child found by predicate")
            return None
        except Exception:
            self._logger.error("Failed to find child by predicate")
            return None
    
    def find_children_by_predicate(self, predicate: Callable[[Any], bool]) -> List[Any]:
        """
        Find all child elements using custom predicate function.
        
        Args:
            predicate: Function that takes an element and returns True if it matches
            
        Returns:
            List of found child elements
        """
        try:
            children = self._get_children()
            if not children:
                self._logger.warning("No children found")
                return []
            
            found_children = []
            for child in children:
                if predicate(child):
                    self._logger.debug("Found child by predicate")
                    found_children.append(child)
            
            self._logger.warning("No children found by predicate")
            return found_children
        except Exception:
            self._logger.error("Failed to find children by predicate")
            return []
    
    def find_child_by_text(self, text: str, exact_match: bool = True) -> Optional[Any]:
        """
        Find child element by text content.
        
        Args:
            text: Text to search for
            exact_match: If True, requires exact match; if False, uses partial match
            
        Returns:
            Found child element or None
        """
        def text_predicate(child: Any) -> bool:
            try:
                child_text = StringProperty('text', child).get_value()
                if exact_match:
                    self._logger.debug(f"Exact match: {child_text} == {text}")
                    return child_text == text
                else:
                    self._logger.debug(f"Partial match: {text} in {child_text}")
                    return text.lower() in child_text.lower()
            except Exception:
                self._logger.error(f"Failed to find child by text: {text}")
                return False
        
        self._logger.debug(f"Finding child by text: {text}")
        return self.find_child_by_predicate(text_predicate)
    
    def find_children_by_text(self, text: str, exact_match: bool = True) -> List[Any]:
        """
        Find all child elements by text content.
        
        Args:
            text: Text to search for
            exact_match: If True, requires exact match; if False, uses partial match
            
        Returns:
            List of found child elements
        """
        def text_predicate(child: Any) -> bool:
            try:
                child_text = StringProperty('text', child).get_value()
                if exact_match:
                    self._logger.debug(f"Exact match: {child_text} == {text}")
                    return child_text == text
                else:
                    self._logger.debug(f"Partial match: {text} in {child_text}")
                    return text.lower() in child_text.lower()
            except Exception:
                self._logger.error(f"Failed to find children by text: {text}")
                return False
        
        self._logger.debug(f"Finding children by text: {text}")
        return self.find_children_by_predicate(text_predicate)
    
    def find_child_by_name(self, name: str, exact_match: bool = True) -> Optional[Any]:
        """
        Find child element by name.
        
        Args:
            name: Name to search for
            exact_match: If True, requires exact match; if False, uses partial match
            
        Returns:
            Found child element or None
        """
        def name_predicate(child: Any) -> bool:
            try:
                child_name = StringProperty('name', child).get_value()
                if exact_match:
                    self._logger.debug(f"Exact match: {child_name} == {name}")
                    return child_name == name
                else:
                    self._logger.debug(f"Partial match: {name} in {child_name}")
                    return name.lower() in child_name.lower()
            except Exception:
                self._logger.error(f"Failed to find child by name: {name}")
                return False
        
        self._logger.debug(f"Finding child by name: {name}")
        return self.find_child_by_predicate(name_predicate)
    
    def find_children_by_name(self, name: str, exact_match: bool = True) -> List[Any]:
        """
        Find all child elements by name.
        
        Args:
            name: Name to search for
            exact_match: If True, requires exact match; if False, uses partial match
            
        Returns:
            List of found child elements
        """
        def name_predicate(child: Any) -> bool:
            try:
                child_name = StringProperty('name', child).get_value()
                if exact_match:
                    self._logger.debug(f"Exact match: {child_name} == {name}")
                    return child_name == name
                else:
                    self._logger.debug(f"Partial match: {name} in {child_name}")
                    return name.lower() in child_name.lower()
            except Exception:
                self._logger.error(f"Failed to find children by name: {name}")
                return False
        
        self._logger.debug(f"Finding children by name: {name}")
        return self.find_children_by_predicate(name_predicate)
    
    def find_child_by_control_type(self, control_type: str) -> Optional[Any]:
        """
        Find child element by control type.
        
        Args:
            control_type: Control type to search for
            
        Returns:
            Found child element or None
        """
        self._logger.debug(f"Finding child by control type: {control_type}")
        return self.find_child_by_property('control_type', control_type, StringProperty)
    
    def find_children_by_control_type(self, control_type: str) -> List[Any]:
        """
        Find all child elements by control type.
        
        Args:
            control_type: Control type to search for
            
        Returns:
            List of found child elements
        """
        self._logger.debug(f"Finding children by control type: {control_type}")
        return self.find_children_by_property('control_type', control_type, StringProperty)
    
    def find_child_by_automation_id(self, automation_id: str) -> Optional[Any]:
        """
        Find child element by automation ID.
        
        Args:
            automation_id: Automation ID to search for
            
        Returns:
            Found child element or None
        """
        self._logger.debug(f"Finding child by automation ID: {automation_id}")
        return self.find_child_by_property('automation_id', automation_id, StringProperty)
    
    def find_children_by_automation_id(self, automation_id: str) -> List[Any]:
        """
        Find all child elements by automation ID.
        
        Args:
            automation_id: Automation ID to search for
            
        Returns:
            List of found child elements
        """
        self._logger.debug(f"Finding children by automation ID: {automation_id}")
        return self.find_children_by_property('automation_id', automation_id, StringProperty)
    
    def find_visible_children(self) -> List[Any]:
        """
        Find all visible child elements.
        
        Returns:
            List of visible child elements
        """
        self._logger.debug("Finding visible children")
        return self.find_children_by_property('visible', True, BoolProperty)
    
    def find_enabled_children(self) -> List[Any]:
        """
        Find all enabled child elements.
        
        Returns:
            List of enabled child elements
        """
        def enabled_predicate(child: Any) -> bool:
            try:
                self._logger.debug(f"Checking if child is enabled: {child}")
                return hasattr(child, 'is_enabled') and child.is_enabled()
            except Exception:
                self._logger.error("Failed to find enabled children")
                return False
        
        self._logger.debug("Finding enabled children")
        return self.find_children_by_predicate(enabled_predicate)
    
    def _get_children(self) -> List[Any]:
        """
        Get all child elements.

        Returns:
            List[Any]: List of child elements.
        """
        try:
            if hasattr(self._element, 'get_children'):
                self._logger.debug("Using get_children method")
                return self._element.get_children()
            elif hasattr(self._element, 'children'):
                self._logger.debug("Using children attribute")
                return self._element.children
            elif hasattr(self._element, 'FindAll'):
                # Windows UIA
                self._logger.debug("Using FindAll method")
                return list(self._element.FindAll())
            else:
                self._logger.debug("No children found")
                return []
        except Exception:
            self._logger.error("Failed to get children")
            return []
    
    def _detect_property_type(self, property_name: str) -> type[Property]:
        """
        Auto-detect property type based on property name.

        Args:
            property_name (str): The name of the property to detect the type of.
        """
        try:
            if property_name in ELEMENT_PROPERTIES:
                self._logger.debug(f"Detected property type: {ELEMENT_PROPERTIES[property_name].property_class}")
                return ELEMENT_PROPERTIES[property_name].property_class
            self._logger.debug("No property type detected")
            # Default to StringProperty for unknown properties
            return StringProperty 
        except Exception:
            self._logger.error(f"Failed to detect property type: {property_name}")
            return StringProperty 