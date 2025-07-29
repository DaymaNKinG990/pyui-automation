"""
Element Factory - creates specialized elements based on control type.

This factory creates appropriate specialized element classes based on
the control type, following the Interface Segregation Principle.
"""
# Python imports
from typing import Any, TYPE_CHECKING
from logging import getLogger

# Local imports
if TYPE_CHECKING:
    from ..core.session import AutomationSession

from .base_element import BaseElement
from .specialized.button_element import ButtonElement
from .specialized.text_element import TextElement
from .specialized.checkbox_element import CheckboxElement
from .specialized.dropdown_element import DropdownElement
from .specialized.input_element import InputElement
from .specialized.window_element import WindowElement


class ElementFactory:
    """Factory for creating specialized elements"""
    
    def __init__(self) -> None:
        """Initialize the ElementFactory."""
        self._logger = getLogger(__name__)
        self._element_mapping = {
            'Button': ButtonElement,
            'Text': TextElement,
            'CheckBox': CheckboxElement,
            'ComboBox': DropdownElement,
            'Edit': InputElement,
            'Window': WindowElement,
            'Pane': WindowElement,
            'Dialog': WindowElement,
        }
    
    def create_element(self, native_element: Any, session: 'AutomationSession') -> BaseElement:
        """
        Create appropriate specialized element based on control type.
        
        Args:
            native_element: Native element representation
            session: Automation session
            
        Returns:
            Specialized element instance
            
        Raises:
            ValueError: If native_element is None
        """
        if native_element is None:
            raise ValueError("Native element cannot be None")
            
        try:
            control_type = self._get_control_type(native_element)
            element_class = self._element_mapping.get(control_type, TextElement)  # Default to TextElement instead of BaseElement
            
            self._logger.debug(f"Creating {element_class.__name__} for control type: {control_type}")
            return element_class(native_element, session)
            
        except Exception as e:
            self._logger.warning(f"Failed to create specialized element, falling back to TextElement: {e}")
            return TextElement(native_element, session)
    
    def _get_control_type(self, native_element: Any) -> str:
        """
        Get control type from native element.

        Args:
            native_element (Any): The native element to get the control type from.

        Returns:
            str: The control type of the native element.
        """
        if native_element is None:
            raise ValueError("Native element cannot be None")
            
        try:
            if hasattr(native_element, 'CurrentControlType') and native_element.CurrentControlType and native_element.CurrentControlType.ProgrammaticName:
                return str(native_element.CurrentControlType.ProgrammaticName)
            elif hasattr(native_element, 'get_property'):
                control_type = native_element.get_property("ControlType")
                if control_type:
                    return str(control_type)
            elif hasattr(native_element, 'control_type'):
                return str(native_element.control_type)
            elif hasattr(native_element, 'ControlType') and native_element.ControlType:
                return str(native_element.ControlType.ProgrammaticName)
            elif hasattr(native_element, 'CurrentClassName'):
                # Fallback based on class name
                class_name = native_element.CurrentClassName
                if 'Text' in class_name or 'Label' in class_name:
                    return 'Text'
                elif 'Button' in class_name:
                    return 'Button'
                elif 'CheckBox' in class_name:
                    return 'CheckBox'
                elif 'ComboBox' in class_name or 'DropDown' in class_name:
                    return 'ComboBox'
                elif 'Edit' in class_name or 'TextBox' in class_name:
                    return 'Edit'
                elif 'Window' in class_name or 'Dialog' in class_name:
                    return 'Window'
                else:
                    return 'Text'  # Default fallback
            else:
                return "Unknown"
        except Exception as e:
            self._logger.warning(f"Failed to get control type: {e}")
            return "Unknown"
        
        # Fallback return to satisfy type checker
        return "Unknown"
    
    def register_element_type(self, control_type: str, element_class: type) -> None:
        """
        Register custom element type.

        Args:
            control_type (str): The control type to register.
            element_class (type): The element class to register.
        """
        try:
            self._element_mapping[control_type] = element_class  # type: ignore
            self._logger.info(f"Registered element type: {control_type} -> {element_class.__name__}")
        except Exception as e:
            self._logger.error(f"Failed to register element type: {e}")
    
    @property
    def _element_types(self) -> dict:
        """Get element types mapping for compatibility with tests"""
        return self._element_mapping
    
    def unregister_element_type(self, control_type: str) -> bool:
        """
        Unregister element type.

        Args:
            control_type (str): The control type to unregister.
        """
        try:
            if control_type in self._element_mapping:
                del self._element_mapping[control_type]
                self._logger.info(f"Unregistered element type: {control_type}")
                return True
            return False
        except Exception as e:
            self._logger.error(f"Failed to unregister element type: {e}")
            return False
    
    def get_supported_types(self) -> list[str]:
        """
        Get list of supported control types.

        Returns:
            list[str]: The list of supported control types.
        """
        return list(self._element_mapping.keys())
    
    def is_type_supported(self, control_type: str) -> bool:
        """
        Check if control type is supported.

        Args:
            control_type (str): The control type to check.
        """
        return control_type in self._element_mapping


# Global factory instance
_element_factory = None


def get_element_factory() -> ElementFactory:
    """
    Get global element factory instance.
    
    Returns:
        ElementFactory: Global element factory instance
    """
    global _element_factory
    if _element_factory is None:
        _element_factory = ElementFactory()
    return _element_factory


def create_element(native_element: Any, session: 'AutomationSession') -> BaseElement:
    """
    Create element using global factory.

    Args:
        native_element (Any): The native element to create the element from.
        session (AutomationSession): The session to use for the element.

    Returns:
        BaseElement: The created element.
    """
    factory = get_element_factory()
    return factory.create_element(native_element, session)

# Remove problematic static method assignment that causes recursion 