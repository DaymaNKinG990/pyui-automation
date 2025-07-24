"""
Element Search Service - handles element search operations.

Responsible for:
- Finding child elements
- Finding elements by properties
- Finding elements by text
"""
# Python imports
from typing import Optional, List, Any, TYPE_CHECKING, Callable
from logging import getLogger

# Local imports
if TYPE_CHECKING:
    from .base_element import BaseElement


class ElementSearchService:
    """Service for element search operations"""
    
    def __init__(self, session: Any) -> None:
        """
        Initialize the ElementSearchService.

        Args:
            session (Any): The session to use for the search service.
        """
        self._session = session
        self._logger = getLogger(__name__)
    
    def get_parent(self, element: "BaseElement") -> Optional["BaseElement"]:
        """
        Get parent element.

        Args:
            element (BaseElement): The element to get the parent of.
        """
        try:
            native_parent = element.native_element.GetParent()
            if native_parent:
                return BaseElement(native_parent, self._session)
            return None
        except Exception as e:
            self._logger.error(f"Failed to get parent element: {e}")
            return None
    
    def get_children(self, element: "BaseElement") -> List["BaseElement"]:
        """
        Get all child elements.

        Args:
            element (BaseElement): The element to get the children of.
        """
        try:
            native_children = element.native_element.GetChildren()
            return [BaseElement(child, self._session) for child in native_children]
        except Exception as e:
            self._logger.error(f"Failed to get child elements: {e}")
            return []
    
    def find_child_by_property(self, element: "BaseElement", property_name: str, expected_value: Any) -> Optional["BaseElement"]:
        """
        Find child element by property.

        Args:
            element (BaseElement): The element to find the child in.
            property_name (str): The name of the property to find the child by.
            expected_value (Any): The expected value of the property.
        """
        try:
            children = self.get_children(element)
            for child in children:
                if child.get_property(property_name) == expected_value:
                    return child
            return None
        except Exception as e:
            self._logger.error(f"Failed to find child by property: {e}")
            return None
    
    def find_children_by_property(self, element: "BaseElement", property_name: str, expected_value: Any) -> List["BaseElement"]:
        """
        Find child elements by property.

        Args:
            element (BaseElement): The element to find the children in.
            property_name (str): The name of the property to find the children by.
            expected_value (Any): The expected value of the property.
        """
        try:
            children = self.get_children(element)
            return [child for child in children if child.get_property(property_name) == expected_value]
        except Exception as e:
            self._logger.error(f"Failed to find children by property: {e}")
            return []
    
    def find_child_by_text(self, element: "BaseElement", text: str, exact_match: bool = True) -> Optional["BaseElement"]:
        """
        Find child element by text.

        Args:
            element (BaseElement): The element to find the child in.
            text (str): The text to find the child by.
            exact_match (bool): Whether to use exact match.
        """
        try:
            children = self.get_children(element)
            for child in children:
                child_text = child.text
                if exact_match and child_text == text:
                    return child
                elif not exact_match and text in child_text:
                    return child
            return None
        except Exception as e:
            self._logger.error(f"Failed to find child by text: {e}")
            return None
    
    def find_children_by_text(self, element: "BaseElement", text: str, exact_match: bool = True) -> List["BaseElement"]:
        """
        Find child elements by text.

        Args:
            element (BaseElement): The element to find the children in.
            text (str): The text to find the children by.
            exact_match (bool): Whether to use exact match.
        """
        try:
            children = self.get_children(element)
            if exact_match:
                return [child for child in children if child.text == text]
            else:
                return [child for child in children if text in child.text]
        except Exception as e:
            self._logger.error(f"Failed to find children by text: {e}")
            return []
    
    def find_child_by_name(self, element: "BaseElement", name: str, exact_match: bool = True) -> Optional["BaseElement"]:
        """
        Find child element by name.

        Args:
            element (BaseElement): The element to find the child in.
            name (str): The name to find the child by.
            exact_match (bool): Whether to use exact match.
        """
        try:
            children = self.get_children(element)
            for child in children:
                child_name = child.name
                if exact_match and child_name == name:
                    return child
                elif not exact_match and name in child_name:
                    return child
            return None
        except Exception as e:
            self._logger.error(f"Failed to find child by name: {e}")
            return None
    
    def find_children_by_name(self, element: "BaseElement", name: str, exact_match: bool = True) -> List["BaseElement"]:
        """
        Find child elements by name.

        Args:
            element (BaseElement): The element to find the children in.
            name (str): The name to find the children by.
            exact_match (bool): Whether to use exact match.
        """
        try:
            children = self.get_children(element)
            if exact_match:
                return [child for child in children if child.name == name]
            else:
                return [child for child in children if name in child.name]
        except Exception as e:
            self._logger.error(f"Failed to find children by name: {e}")
            return []
    
    def find_child_by_control_type(self, element: "BaseElement", control_type: str) -> Optional["BaseElement"]:
        """
        Find child element by control type.

        Args:
            element (BaseElement): The element to find the child in.
            control_type (str): The control type to find the child by.
        """
        try:
            children = self.get_children(element)
            for child in children:
                if child.control_type == control_type:
                    return child
            return None
        except Exception as e:
            self._logger.error(f"Failed to find child by control type: {e}")
            return None
    
    def find_children_by_control_type(self, element: "BaseElement", control_type: str) -> List["BaseElement"]:
        """
        Find child elements by control type.

        Args:
            element (BaseElement): The element to find the children in.
            control_type (str): The control type to find the children by.
        """
        try:
            children = self.get_children(element)
            return [child for child in children if child.control_type == control_type]
        except Exception as e:
            self._logger.error(f"Failed to find children by control type: {e}")
            return []
    
    def find_child_by_automation_id(self, element: "BaseElement", automation_id: str) -> Optional["BaseElement"]:
        """
        Find child element by automation ID.

        Args:
            element (BaseElement): The element to find the child in.
            automation_id (str): The automation ID to find the child by.
        """
        try:
            children = self.get_children(element)
            for child in children:
                if child.automation_id == automation_id:
                    return child
            return None
        except Exception as e:
            self._logger.error(f"Failed to find child by automation ID: {e}")
            return None
    
    def find_children_by_automation_id(self, element: "BaseElement", automation_id: str) -> List["BaseElement"]:
        """
        Find child elements by automation ID.

        Args:
            element (BaseElement): The element to find the children in.
            automation_id (str): The automation ID to find the children by.
        """
        try:
            children = self.get_children(element)
            return [child for child in children if child.automation_id == automation_id]
        except Exception as e:
            self._logger.error(f"Failed to find children by automation ID: {e}")
            return []
    
    def find_visible_children(self, element: "BaseElement") -> List["BaseElement"]:
        """
        Find visible child elements.

        Args:
            element (BaseElement): The element to find the children in.
        """
        try:
            children = self.get_children(element)
            return [child for child in children if child.is_displayed()]
        except Exception as e:
            self._logger.error(f"Failed to find visible children: {e}")
            return []
    
    def find_enabled_children(self, element: "BaseElement") -> List["BaseElement"]:
        """
        Find enabled child elements.

        Args:
            element (BaseElement): The element to find the children in.
        """
        try:
            children = self.get_children(element)
            return [child for child in children if child.is_enabled()]
        except Exception as e:
            self._logger.error(f"Failed to find enabled children: {e}")
            return []
    
    def find_child_by_predicate(self, element: "BaseElement", predicate: Callable[["BaseElement"], bool]) -> Optional["BaseElement"]:
        """
        Find child element by custom predicate.

        Args:
            element (BaseElement): The element to find the child in.
            predicate (Callable[[BaseElement], bool]): The predicate to find the child by.
        """
        try:
            children = self.get_children(element)
            for child in children:
                if predicate(child):
                    return child
            return None
        except Exception as e:
            self._logger.error(f"Failed to find child by predicate: {e}")
            return None
    
    def find_children_by_predicate(self, element: "BaseElement", predicate: Callable[["BaseElement"], bool]) -> List["BaseElement"]:
        """
        Find child elements by custom predicate.

        Args:
            element (BaseElement): The element to find the children in.
            predicate (Callable[[BaseElement], bool]): The predicate to find the children by.
        """
        try:
            children = self.get_children(element)
            return [child for child in children if predicate(child)]
        except Exception as e:
            self._logger.error(f"Failed to find children by predicate: {e}")
            return [] 