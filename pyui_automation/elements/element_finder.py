"""
Element finder for dynamic element discovery.

This module provides functionality to find elements and their children
based on various properties and attributes.
"""
# Python imports
from typing import Any, List, Optional, Callable, TYPE_CHECKING
from logging import getLogger

# Local imports
from .properties import Property, ELEMENT_PROPERTIES, StringProperty, BoolProperty

if TYPE_CHECKING:
    from .base_element import BaseElement


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
    
    def find_child_by_property(self, property_name: str, value: Any, property_type: Optional[type[Property]] = None) -> Optional[Any]:
        """Find first child by property value"""
        children = self._get_children()
        for child in children:
            if property_type:
                if child.get_property(property_name) == value:
                    return child
            else:
                prop = StringProperty(property_name, child)
                if prop.get_value() == value:
                    return child
        return None
    
    def find_children_by_property(
        self,
        property_name: str,
        expected_value: Any,
        property_type: Optional[type[Property]] = None
    ) -> List["BaseElement"]:
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
            
            if not found_children:
                self._logger.warning("No children found by property")
            return found_children
        except Exception:
            self._logger.error(f"Failed to find children by property: {property_name}")
            return []
    
    def find_child_by_predicate(self, predicate: Callable[["BaseElement"], bool]) -> Optional[Any]:
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
    
    def find_children_by_predicate(self, predicate: Callable[["BaseElement"], bool]) -> List["BaseElement"]:
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
            
            if not found_children:
                self._logger.warning("No children found by predicate")
            return found_children
        except Exception:
            self._logger.error("Failed to find children by predicate")
            return []
    
    def find_child_by_text(self, text: str, exact_match: bool = True, case_sensitive: bool = True) -> Optional[Any]:
        """
        Find child element by text content.
        
        Args:
            text: Text to search for
            exact_match: If True, requires exact match; if False, uses partial match
            case_sensitive: If True, case sensitive matching; if False, case insensitive
            
        Returns:
            Found child element or None
        """
        def text_predicate(child: "BaseElement") -> bool:
            try:
                child_text = StringProperty('text', child).get_value()
                if not case_sensitive:
                    child_text = child_text.lower()
                    text_to_match = text.lower()
                else:
                    text_to_match = text
                
                if exact_match:
                    self._logger.debug(f"Exact match: {child_text} == {text_to_match}")
                    return child_text == text_to_match
                else:
                    self._logger.debug(f"Partial match: {text_to_match} in {child_text}")
                    return text_to_match in child_text
            except Exception:
                self._logger.error(f"Failed to find child by text: {text}")
                return False
        
        self._logger.debug(f"Finding child by text: {text}")
        return self.find_child_by_predicate(text_predicate)
    
    def find_children_by_text(self, text: str, exact_match: bool = True, case_sensitive: bool = True) -> List["BaseElement"]:
        """
        Find all child elements by text content.
        
        Args:
            text: Text to search for
            exact_match: If True, requires exact match; if False, uses partial match
            case_sensitive: If True, case sensitive matching; if False, case insensitive
            
        Returns:
            List of found child elements
        """
        def text_predicate(child: "BaseElement") -> bool:
            try:
                child_text = StringProperty('text', child).get_value()
                if not case_sensitive:
                    child_text = child_text.lower()
                    text_to_match = text.lower()
                else:
                    text_to_match = text
                
                if exact_match:
                    self._logger.debug(f"Exact match: {child_text} == {text_to_match}")
                    return child_text == text_to_match
                else:
                    self._logger.debug(f"Partial match: {text_to_match} in {child_text}")
                    return text_to_match in child_text
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
        def name_predicate(child: "BaseElement") -> bool:
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
    
    def find_children_by_name(self, name: str, exact_match: bool = True) -> List["BaseElement"]:
        """
        Find all child elements by name.
        
        Args:
            name: Name to search for
            exact_match: If True, requires exact match; if False, uses partial match
            
        Returns:
            List of found child elements
        """
        def name_predicate(child: "BaseElement") -> bool:
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
    
    def find_child_by_automation_id(self, automation_id: str) -> Optional[Any]:
        """Find child by automation ID using StringProperty"""
        self._logger.debug(f"Finding child by automation ID: {automation_id}")
        children = self._get_children()
        for child in children:
            prop = StringProperty('automation_id', child)
            if prop.get_value() == automation_id:
                return child
        return None

    def find_child_by_control_type(self, control_type: str) -> Optional[Any]:
        """Find child by control type using StringProperty"""
        self._logger.debug(f"Finding child by control type: {control_type}")
        children = self._get_children()
        for child in children:
            prop = StringProperty('control_type', child)
            if prop.get_value() == control_type:
                return child
        return None
    
    def find_children_by_control_type(self, control_type: str) -> List["BaseElement"]:
        """
        Find all child elements by control type.
        
        Args:
            control_type: Control type to search for
            
        Returns:
            List of found child elements
        """
        self._logger.debug(f"Finding children by control type: {control_type}")
        return self.find_children_by_property('control_type', control_type, StringProperty)
    
    def find_children_by_automation_id(self, automation_id: str) -> List["BaseElement"]:
        """
        Find all child elements by automation ID.
        
        Args:
            automation_id: Automation ID to search for
            
        Returns:
            List of found child elements
        """
        self._logger.debug(f"Finding children by automation ID: {automation_id}")
        return self.find_children_by_property('automation_id', automation_id, StringProperty)
    
    def find_visible_children(self) -> List["BaseElement"]:
        """
        Find all visible child elements.
        
        Returns:
            List of visible child elements
        """
        self._logger.debug("Finding visible children")
        return self.find_children_by_property('visible', True, BoolProperty)
    
    def find_enabled_children(self) -> List["BaseElement"]:
        """
        Find all enabled child elements.
        
        Returns:
            List of enabled child elements
        """
        self._logger.debug("Finding enabled children")
        return self.find_children_by_property('enabled', True, BoolProperty)
    
    def _get_children(self) -> List[Any]:
        """
        Get all child elements.

        Returns:
            List[Any]: List of child elements.
        """
        try:
            if hasattr(self._element, 'get_children'):
                self._logger.debug("Using get_children method")
                children = self._element.get_children()
                return children if children is not None else []
            elif hasattr(self._element, 'children'):
                self._logger.debug("Using children attribute")
                children = self._element.children
                return children if children is not None else []
            elif hasattr(self._element, 'findall'):
                # Generic findall method
                self._logger.debug("Using findall method")
                result = self._element.findall()
                return list(result) if result is not None else []
            elif hasattr(self._element, 'FindAll'):
                # Windows UIA
                self._logger.debug("Using FindAll method")
                result = self._element.FindAll()
                return list(result) if result is not None else []
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