"""
Property classes for UI elements.

This module provides property classes that encapsulate element properties
and provide type-safe access to element attributes.
"""
# Python imports
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Union
from dataclasses import dataclass


class Property(ABC):
    """Base class for all element properties."""
    
    def __init__(self, name: str, element: Any) -> None:
        """
        Initialize property.
        
        Args:
            name: Property name
            element: Native element reference
        """
        self.name = name
        self._element = element
    
    @abstractmethod
    def get_value(self) -> Any:
        """
        Get property value.

        Returns:
            Any: The value of the property.
        """
        pass
    
    def __str__(self) -> str:
        return f"{self.__class__.__name__}({self.name})"
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(name='{self.name}', value={self.get_value()})"


class StringProperty(Property):
    """String property for text-based element attributes."""
    
    def get_value(self) -> str:
        """
        Get string value from element.

        Returns:
            str: The string value of the element.
        """
        try:
            if hasattr(self._element, 'get_attribute'):
                return self._element.get_attribute(self.name) or ""
            
            # Platform-specific handling
            if self.name == 'name' and hasattr(self._element, 'CurrentName'):
                return self._element.CurrentName or ""
            elif self.name == 'automation_id' and hasattr(self._element, 'CurrentAutomationId'):
                return self._element.CurrentAutomationId or ""
            elif self.name == 'class_name' and hasattr(self._element, 'CurrentClassName'):
                return self._element.CurrentClassName or ""
            elif self.name == 'control_type' and hasattr(self._element, 'CurrentControlType'):
                return str(self._element.CurrentControlType) or ""
            elif self.name == 'text' and hasattr(self._element, 'text'):
                return self._element.text or ""
            elif self.name == 'value' and hasattr(self._element, 'value'):
                return self._element.value or ""
            elif hasattr(self._element, self.name):
                return str(getattr(self._element, self.name)) or ""
            
            return ""
        except Exception:
            return ""


class IntProperty(Property):
    """Integer property for numeric element attributes."""
    
    def get_value(self) -> int:
        """
        Get integer value from element.

        Returns:
            int: The integer value of the element.
        """
        try:
            if hasattr(self._element, 'get_property'):
                value = self._element.get_property(self.name)
                return int(value) if value is not None else 0
            
            if hasattr(self._element, self.name):
                value = getattr(self._element, self.name)
                return int(value) if value is not None else 0
            
            return 0
        except (ValueError, TypeError):
            return 0


class BoolProperty(Property):
    """Boolean property for true/false element attributes."""
    
    def get_value(self) -> bool:
        """
        Get boolean value from element.

        Returns:
            bool: The boolean value of the element.
        """
        try:
            if hasattr(self._element, 'get_property'):
                value = self._element.get_property(self.name)
                return bool(value)
            
            if self.name == 'visible' and hasattr(self._element, 'CurrentIsOffscreen'):
                return not self._element.CurrentIsOffscreen
            elif self.name == 'is_checked' and hasattr(self._element, 'get_property'):
                return bool(self._element.get_property('checked') or self._element.get_property('is_checked'))
            elif self.name == 'is_expanded' and hasattr(self._element, 'get_property'):
                return bool(self._element.get_property('expanded') or self._element.get_property('is_expanded'))
            elif self.name == 'is_selected' and hasattr(self._element, 'get_property'):
                return bool(self._element.get_property('selected') or self._element.get_property('is_selected'))
            elif hasattr(self._element, self.name):
                return bool(getattr(self._element, self.name))
            
            return False
        except Exception:
            return False


class DictProperty(Property):
    """Dictionary property for complex element attributes like location, size."""
    
    def get_value(self) -> Dict[str, Union[int, float, str, bool]]:
        """
        Get dictionary value from element.

        Returns:
            Dict[str, Union[int, float, str, bool]]: The dictionary value of the element.
        """
        try:
            if self.name == 'location' and hasattr(self._element, 'location'):
                return self._element.location  # type: ignore[no-any-return]
            elif self.name == 'size' and hasattr(self._element, 'size'):
                return self._element.size  # type: ignore[no-any-return]
            elif self.name == 'rect' and hasattr(self._element, 'rect'):
                return self._element.rect  # type: ignore[no-any-return]
            elif self.name == 'center':
                # Calculate center from location and size
                location = self._element.location if hasattr(self._element, 'location') else {'x': 0, 'y': 0}
                size = self._element.size if hasattr(self._element, 'size') else {'width': 0, 'height': 0}
                return {
                    'x': location.get('x', 0) + size.get('width', 0) // 2,
                    'y': location.get('y', 0) + size.get('height', 0) // 2
                }
            elif hasattr(self._element, self.name):
                value = getattr(self._element, self.name)
                return value if isinstance(value, dict) else {}
            
            return {}
        except Exception:
            return {}


class OptionalStringProperty(Property):
    """Optional string property that can return None."""
    
    def get_value(self) -> Optional[str]:
        """
        Get optional string value from element.

        Returns:
            Optional[str]: The optional string value of the element.
        """
        try:
            if hasattr(self._element, 'get_property'):
                value = self._element.get_property(self.name)
                return str(value) if value is not None else None
            
            if self.name == 'value' and hasattr(self._element, 'value'):
                value = self._element.value
                return str(value) if value is not None else None
            elif self.name == 'selected_item' and hasattr(self._element, 'get_property'):
                selected = self._element.get_property("selected") or self._element.get_property("selected_item")
                return str(selected) if selected is not None else None
            elif hasattr(self._element, self.name):
                value = getattr(self._element, self.name)
                return str(value) if value is not None else None
            
            return None
        except Exception:
            return None


@dataclass
class PropertyDefinition:
    """Definition of an element property."""

    name: str
    property_class: type[Property]
    description: str = ""


# Predefined property definitions
ELEMENT_PROPERTIES = {
    'text': PropertyDefinition('text', StringProperty, 'Element text content'),
    'name': PropertyDefinition('name', StringProperty, 'Element name'),
    'automation_id': PropertyDefinition('automation_id', StringProperty, 'Element automation ID'),
    'class_name': PropertyDefinition('class_name', StringProperty, 'Element class name'),
    'control_type': PropertyDefinition('control_type', StringProperty, 'Element control type'),
    'value': PropertyDefinition('value', OptionalStringProperty, 'Element value'),
    'selected_item': PropertyDefinition('selected_item', OptionalStringProperty, 'Selected item text'),
    
    'visible': PropertyDefinition('visible', BoolProperty, 'Element visibility'),
    'is_checked': PropertyDefinition('is_checked', BoolProperty, 'Element checked state'),
    'is_expanded': PropertyDefinition('is_expanded', BoolProperty, 'Element expanded state'),
    'is_selected': PropertyDefinition('is_selected', BoolProperty, 'Element selected state'),
    
    'location': PropertyDefinition('location', DictProperty, 'Element location coordinates'),
    'size': PropertyDefinition('size', DictProperty, 'Element size dimensions'),
    'rect': PropertyDefinition('rect', DictProperty, 'Element rectangle bounds'),
    'center': PropertyDefinition('center', DictProperty, 'Element center coordinates'),
} 