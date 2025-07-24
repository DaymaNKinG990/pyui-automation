"""
Refactored BaseElement - follows SOLID principles.

This is a refactored version of BaseElement that uses specialized services
to handle different responsibilities, following the Single Responsibility Principle.
"""
# Python imports
from typing import Optional, Any, Dict, TYPE_CHECKING, List, Callable
import numpy as np

# Local imports
if TYPE_CHECKING:
    from ..core.session import AutomationSession

from .properties import ELEMENT_PROPERTIES
from .element_finder import ElementFinder
from .interaction_service import ElementInteractionService
from .wait_service import ElementWaitService
from .search_service import ElementSearchService
from .state_service import ElementStateService
from ..core.interfaces import IElement


class BaseElement(IElement):
    """
    Base UI element that follows SOLID principles.
    
    Responsibilities:
    - Element identification and basic properties
    - Delegating interactions to ElementInteractionService
    - Delegating waits to ElementWaitService
    - Delegating searches to ElementSearchService
    - Delegating state management to ElementStateService
    """
    
    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        """
        Initialize a BaseElement instance.

        Args:
            native_element (Any): The native element representation for the current platform.
            session (AutomationSession): The automation session associated with this UI element.
        """
        self._element = native_element
        self._session = session
        self._finder = ElementFinder(native_element)
        
        # Initialize services
        self._interaction_service = ElementInteractionService(session)
        self._wait_service = ElementWaitService(session)
        self._search_service = ElementSearchService(session)
        self._state_service = ElementStateService(session)

    @property
    def native_element(self) -> Any:
        """
        Get native element.

        Returns:
            Any: The native element representation for the current platform.
        """
        return self._element

    @property
    def session(self) -> 'AutomationSession':
        """
        Get the automation session.

        Returns:
            AutomationSession: The automation session associated with this UI element.
        """
        return self._session

    @property
    def control_type(self) -> str:
        """
        Get the control type of this element.

        Returns:
            str: The control type of this element.
        """
        return self.get_property("ControlType") or self.get_attribute("controlType") or "unknown"

    # Basic property access methods
    def get_attribute(self, name: str) -> Optional[str]:
        """
        Get element attribute.

        Args:
            name (str): The name of the attribute to get.

        Returns:
            Optional[str]: The value of the attribute, or None if the attribute is not found.
        """
        try:
            if hasattr(self._element, 'get_attribute'):
                return self._element.get_attribute(name)
            
            # Platform-specific attribute handling
            if hasattr(self._element, 'CurrentName') and name == 'name':
                return self._element.CurrentName
            elif hasattr(self._element, 'CurrentAutomationId') and name == 'automation_id':
                return self._element.CurrentAutomationId
            elif hasattr(self._element, 'CurrentClassName') and name == 'class_name':
                return self._element.CurrentClassName
            elif hasattr(self._element, 'CurrentControlType') and name == 'control_type':
                return str(self._element.CurrentControlType)
            elif hasattr(self._element, 'name') and name == 'name':
                return self._element.name
            elif hasattr(self._element, 'description') and name == 'description':
                return self._element.description
            elif hasattr(self._element, 'getRole') and name == 'role':
                return str(self._element.getRole())
                
            return None
        except Exception:
            return None

    def get_property(self, name: str) -> Any:
        """
        Get element property.

        Args:
            name (str): The name of the property to get.

        Returns:
            Any: The value of the property, or None if the property is not found.
        """
        try:
            if hasattr(self._element, 'GetCurrentPattern'):
                pattern = self._element.GetCurrentPattern(name)
                if pattern:
                    return pattern
            return None
        except Exception:
            return None

    @property
    def text(self) -> str:
        """
        Get element text.

        Returns:
            str: The text of the element.
        """
        return self.get_attribute("name") or ""

    @property
    def location(self) -> Dict[str, int]:
        """
        Get element location.

        Returns:
            Dict[str, int]: The location of the element.
        """
        try:
            if hasattr(self._element, 'CurrentBoundingRectangle'):
                rect = self._element.CurrentBoundingRectangle
                return {'x': rect.left, 'y': rect.top}
            elif hasattr(self._element, 'getBounds'):
                bounds = self._element.getBounds()
                return {'x': bounds.x, 'y': bounds.y}
            return {'x': 0, 'y': 0}
        except Exception:
            return {'x': 0, 'y': 0}

    @property
    def size(self) -> Dict[str, int]:
        """
        Get element size.

        Returns:
            Dict[str, int]: The size of the element.
        """
        try:
            if hasattr(self._element, 'CurrentBoundingRectangle'):
                rect = self._element.CurrentBoundingRectangle
                return {'width': rect.width, 'height': rect.height}
            elif hasattr(self._element, 'getBounds'):
                bounds = self._element.getBounds()
                return {'width': bounds.width, 'height': bounds.height}
            return {'width': 0, 'height': 0}
        except Exception:
            return {'width': 0, 'height': 0}

    @property
    def name(self) -> str:
        """
        Get element name.

        Returns:
            str: The name of the element.
        """
        return self.get_attribute("name") or ""

    @property
    def visible(self) -> bool:
        """
        Check if element is visible.

        Returns:
            bool: True if the element is visible, False otherwise.
        """
        return self.is_displayed()

    def is_displayed(self) -> bool:
        """
        Check if element is displayed.

        Returns:
            bool: True if the element is displayed, False otherwise.
        """
        try:
            if hasattr(self._element, 'CurrentIsOffscreen'):
                return not self._element.CurrentIsOffscreen
            elif hasattr(self._element, 'isVisible'):
                return self._element.isVisible()
            return True
        except Exception:
            return False

    def is_enabled(self) -> bool:
        """
        Check if element is enabled.

        Returns:
            bool: True if the element is enabled, False otherwise.
        """
        try:
            if hasattr(self._element, 'CurrentIsEnabled'):
                return self._element.CurrentIsEnabled
            elif hasattr(self._element, 'isEnabled'):
                return self._element.isEnabled()
            return True
        except Exception:
            return False

    @property
    def rect(self) -> Dict[str, int]:
        """
        Get element rectangle.

        Returns:
            Dict[str, int]: The rectangle of the element.
        """
        location = self.location
        size = self.size
        return {
            'x': location['x'],
            'y': location['y'],
            'width': size['width'],
            'height': size['height']
        }

    @property
    def center(self) -> Dict[str, int]:
        """
        Get element center point.

        Returns:
            Dict[str, int]: The center point of the element.
        """
        rect = self.rect
        return {
            'x': rect['x'] + rect['width'] // 2,
            'y': rect['y'] + rect['height'] // 2
        }

    @property
    def automation_id(self) -> str:
        """
        Get automation ID.

        Returns:
            str: The automation ID of the element.
        """
        return self.get_attribute("automation_id") or ""

    @property
    def class_name(self) -> str:
        """
        Get class name.

        Returns:
            str: The class name of the element.
        """
        return self.get_attribute("class_name") or ""

    @property
    def value(self) -> Optional[str]:
        """
        Get element value.

        Returns:
            Optional[str]: The value of the element, or None if the value is not found.
        """
        return self.get_attribute("value")

    @value.setter
    def value(self, new_value: str) -> None:
        """
        Set element value.

        Args:
            new_value (str): The new value to set.
        """
        self._state_service.set_value(self, new_value)

    @property
    def is_checked(self) -> bool:
        """
        Check if element is checked.

        Returns:
            bool: True if the element is checked, False otherwise.
        """
        try:
            if hasattr(self._element, 'CurrentToggleState'):
                return self._element.CurrentToggleState == 1
            elif hasattr(self._element, 'isChecked'):
                return self._element.isChecked()
            return False
        except Exception:
            return False

    @is_checked.setter
    def is_checked(self, value: bool) -> None:
        """
        Set checked state.

        Args:
            value (bool): The new checked state.
        """
        if value:
            self._state_service.check(self)
        else:
            self._state_service.uncheck(self)

    @property
    def is_expanded(self) -> bool:
        """
        Check if element is expanded.

        Returns:
            bool: True if the element is expanded, False otherwise.
        """
        try:
            if hasattr(self._element, 'CurrentExpandCollapseState'):
                return self._element.CurrentExpandCollapseState == 1
            elif hasattr(self._element, 'isExpanded'):
                return self._element.isExpanded()
            return False
        except Exception:
            return False

    @is_expanded.setter
    def is_expanded(self, value: bool) -> None:
        """
        Set expanded state.

        Args:
            value (bool): The new expanded state.
        """
        if value:
            self._state_service.expand(self)
        else:
            self._state_service.collapse(self)

    @property
    def selected_item(self) -> Optional[str]:
        """
        Get selected item.

        Returns:
            Optional[str]: The selected item, or None if no item is selected.
        """
        try:
            if hasattr(self._element, 'CurrentSelection'):
                return self._element.CurrentSelection[0].CurrentName
            return None
        except Exception:
            return None

    @selected_item.setter
    def selected_item(self, value: str) -> None:
        """
        Set selected item.

        Args:
            value (str): The new selected item.
        """
        self._state_service.select_item(self, value)

    # Delegate to services
    def click(self) -> None:
        """Click element - delegated to interaction service."""
        self._interaction_service.click(self)

    def double_click(self) -> None:
        """Double click element - delegated to interaction service."""
        self._interaction_service.double_click(self)

    def right_click(self) -> None:
        """Right click element - delegated to interaction service. """
        self._interaction_service.right_click(self)

    def hover(self) -> None:
        """Hover over element - delegated to interaction service"""
        self._interaction_service.hover(self)

    def send_keys(self, *keys: str, interval: Optional[float] = None) -> None:
        """
        Send keys to element - delegated to interaction service.

        Args:
            *keys (str): The keys to send.
            interval (Optional[float]): The interval between keys.
        """
        self._interaction_service.send_keys(self, *keys, interval=interval)

    def clear(self) -> None:
        """Clear element - delegated to interaction service"""
        self._interaction_service.clear(self)

    def append(self, text: str) -> None:
        """
        Append text - delegated to interaction service.

        Args:
            text (str): The text to append.
        """
        self._interaction_service.append(self, text)

    def focus(self) -> None:
        """Focus element - delegated to interaction service"""
        self._interaction_service.focus(self)

    def select_all(self) -> None:
        """Select all text - delegated to interaction service"""
        self._interaction_service.select_all(self)

    def copy(self) -> None:
        """Copy text - delegated to interaction service"""
        self._interaction_service.copy(self)

    def paste(self) -> None:
        """Paste text - delegated to interaction service"""
        self._interaction_service.paste(self)

    def drag_and_drop(self, target: 'IElement') -> None:
        """
        Drag and drop - delegated to interaction service.

        Args:
            target (IElement): The target element to drag and drop to.
        """
        # Cast target to BaseElement for the service call
        if isinstance(target, BaseElement):
            self._interaction_service.drag_and_drop(self, target)
        else:
            raise TypeError("Target must be a BaseElement instance")

    # Wait operations - delegated to wait service
    def wait_until_enabled(self, timeout: Optional[float] = None) -> bool:
        """
        Wait until enabled - delegated to wait service.

        Args:
            timeout (Optional[float]): The timeout in seconds.

        Returns:
            bool: True if the element is enabled, False otherwise.
        """
        return self._wait_service.wait_until_enabled(self, timeout)

    def wait_until_clickable(self, timeout: Optional[float] = None) -> bool:
        """
        Wait until clickable - delegated to wait service.

        Args:
            timeout (Optional[float]): The timeout in seconds.

        Returns:
            bool: True if the element is clickable, False otherwise.
        """
        return self._wait_service.wait_until_clickable(self, timeout)

    def wait_until_checked(self, timeout: float = 10) -> bool:
        """
        Wait until checked - delegated to wait service.

        Args:
            timeout (float): The timeout in seconds.

        Returns:
            bool: True if the element is checked, False otherwise.
        """
        return self._wait_service.wait_until_checked(self, timeout)

    def wait_until_unchecked(self, timeout: float = 10) -> bool:
        """
        Wait until unchecked - delegated to wait service.

        Args:
            timeout (float): The timeout in seconds.

        Returns:
            bool: True if the element is unchecked, False otherwise.
        """
        return self._wait_service.wait_until_unchecked(self, timeout)

    def wait_until_expanded(self, timeout: float = 10) -> bool:
        """
        Wait until expanded - delegated to wait service.

        Args:
            timeout (float): The timeout in seconds.

        Returns:
            bool: True if the element is expanded, False otherwise.
        """
        return self._wait_service.wait_until_expanded(self, timeout)

    def wait_until_collapsed(self, timeout: float = 10) -> bool:
        """
        Wait until collapsed - delegated to wait service.

        Args:
            timeout (float): The timeout in seconds.

        Returns:
            bool: True if the element is collapsed, False otherwise.
        """
        return self._wait_service.wait_until_collapsed(self, timeout)

    def wait_until_value_is(self, expected_value: str, timeout: Optional[float] = None) -> bool:
        """
        Wait until value is - delegated to wait service.

        Args:
            expected_value (str): The expected value.
            timeout (Optional[float]): The timeout in seconds.

        Returns:
            bool: True if the element value matches the expected value, False otherwise.
        """
        return self._wait_service.wait_until_value_is(self, expected_value, timeout)

    # Search operations - delegated to search service
    def get_parent(self) -> Optional['IElement']:
        """
        Get parent - delegated to search service.

        Returns:
            Optional[IElement]: The parent element, or None if no parent is found.
        """
        parent = self._search_service.get_parent(self)
        return BaseElement(parent.native_element, self._session) if parent else None

    def get_children(self) -> List['IElement']:
        """
        Get children - delegated to search service.

        Returns:
            List[BaseElement]: The children elements.
        """
        children = self._search_service.get_children(self)
        return [BaseElement(child.native_element, self._session) for child in children]

    def find_child_by_property(self, property_name: str, expected_value: Any) -> Optional['IElement']:
        """
        Find child by property - delegated to search service.

        Args:
            property_name (str): The name of the property to find.
            expected_value (Any): The expected value of the property.

        Returns:
            Optional[IElement]: The child element, or None if no child is found.
        """
        child = self._search_service.find_child_by_property(self, property_name, expected_value)
        return BaseElement(child.native_element, self._session) if child else None

    def find_children_by_property(self, property_name: str, expected_value: Any) -> List['IElement']:
        """
        Find children by property - delegated to search service.

        Args:
            property_name (str): The name of the property to find.
            expected_value (Any): The expected value of the property.

        Returns:
            List[BaseElement]: The children elements.
        """
        children = self._search_service.find_children_by_property(self, property_name, expected_value)
        return [BaseElement(child.native_element, self._session) for child in children]

    def find_child_by_text(self, text: str, exact_match: bool = True) -> Optional['IElement']:
        """
        Find child by text - delegated to search service.

        Args:
            text (str): The text to find.
            exact_match (bool): Whether to use exact match.

        Returns:
            Optional[IElement]: The child element, or None if no child is found.
        """
        child = self._search_service.find_child_by_text(self, text, exact_match)
        return BaseElement(child.native_element, self._session) if child else None

    def find_children_by_text(self, text: str, exact_match: bool = True) -> List['IElement']:
        """
        Find children by text - delegated to search service.

        Args:
            text (str): The text to find.
            exact_match (bool): Whether to use exact match.

        Returns:
            List[BaseElement]: The children elements.
        """
        children = self._search_service.find_children_by_text(self, text, exact_match)
        return [BaseElement(child.native_element, self._session) for child in children]

    def find_child_by_name(self, name: str, exact_match: bool = True) -> Optional['IElement']:
        """
        Find child by name - delegated to search service.

        Args:
            name (str): The name to find.
            exact_match (bool): Whether to use exact match.

        Returns:
            Optional[IElement]: The child element, or None if no child is found.
        """
        child = self._search_service.find_child_by_name(self, name, exact_match)
        return BaseElement(child.native_element, self._session) if child else None

    def find_children_by_name(self, name: str, exact_match: bool = True) -> List['IElement']:
        """
        Find children by name - delegated to search service.

        Args:
            name (str): The name to find.
            exact_match (bool): Whether to use exact match.

        Returns:
            List[BaseElement]: The children elements.
        """
        children = self._search_service.find_children_by_name(self, name, exact_match)
        return [BaseElement(child.native_element, self._session) for child in children]

    def find_child_by_control_type(self, control_type: str) -> Optional['IElement']:
        """
        Find child by control type - delegated to search service.

        Args:
            control_type (str): The control type to find.

        Returns:
            Optional[IElement]: The child element, or None if no child is found.
        """
        child = self._search_service.find_child_by_control_type(self, control_type)
        return BaseElement(child.native_element, self._session) if child else None

    def find_children_by_control_type(self, control_type: str) -> List['IElement']:
        """
        Find children by control type - delegated to search service.

        Args:
            control_type (str): The control type to find.

        Returns:
            List[BaseElement]: The children elements.
        """
        children = self._search_service.find_children_by_control_type(self, control_type)
        return [BaseElement(child.native_element, self._session) for child in children]

    def find_child_by_automation_id(self, automation_id: str) -> Optional['IElement']:
        """
        Find child by automation ID - delegated to search service.

        Args:
            automation_id (str): The automation ID to find.

        Returns:
            Optional[IElement]: The child element, or None if no child is found.
        """
        child = self._search_service.find_child_by_automation_id(self, automation_id)
        return BaseElement(child.native_element, self._session) if child else None

    def find_children_by_automation_id(self, automation_id: str) -> List['IElement']:
        """
        Find children by automation ID - delegated to search service.

        Args:
            automation_id (str): The automation ID to find.

        Returns:
            List[BaseElement]: The children elements.
        """
        children = self._search_service.find_children_by_automation_id(self, automation_id)
        return [BaseElement(child.native_element, self._session) for child in children]

    def find_visible_children(self) -> List['IElement']:
        """
        Find visible children - delegated to search service.

        Returns:
            List[BaseElement]: The visible children elements.
        """
        children = self._search_service.find_visible_children(self)
        return [BaseElement(child.native_element, self._session) for child in children]

    def find_enabled_children(self) -> List['IElement']:
        """
        Find enabled children - delegated to search service.

        Returns:
            List[BaseElement]: The enabled children elements.
        """
        children = self._search_service.find_enabled_children(self)
        return [BaseElement(child.native_element, self._session) for child in children]

    def find_child_by_predicate(self, predicate: Callable) -> Optional['IElement']:
        """
        Find child by predicate - delegated to search service.

        Args:
            predicate (callable): The predicate to find the child.

        Returns:
            Optional[IElement]: The child element, or None if no child is found.
        """
        child = self._search_service.find_child_by_predicate(self, predicate)
        return BaseElement(child.native_element, self._session) if child else None

    def find_children_by_predicate(self, predicate: Callable) -> List['IElement']:
        """
        Find children by predicate - delegated to search service.

        Args:
            predicate (callable): The predicate to find the children.

        Returns:
            List[BaseElement]: The children elements.
        """
        children = self._search_service.find_children_by_predicate(self, predicate)
        return [BaseElement(child.native_element, self._session) for child in children]

    # State operations - delegated to state service
    def check(self) -> None:
        """Check element - delegated to state service"""
        self._state_service.check(self)

    def uncheck(self) -> None:
        """Uncheck element - delegated to state service"""
        self._state_service.uncheck(self)

    def toggle(self) -> None:
        """Toggle element - delegated to state service"""
        self._state_service.toggle(self)

    def expand(self) -> None:
        """Expand element - delegated to state service"""
        self._state_service.expand(self)

    def collapse(self) -> None:
        """Collapse element - delegated to state service"""
        self._state_service.collapse(self)

    def select_item(self, item_text: str) -> None:
        """
        Select item - delegated to state service.

        Args:
            item_text (str): The text of the item to select.
        """
        self._state_service.select_item(self, item_text)

    def is_pressed(self) -> bool:
        """Check if pressed - delegated to state service.

        Returns:
            bool: True if the element is pressed, False otherwise.
        """
        return self._state_service.is_pressed(self)

    def is_selected(self) -> bool:
        """Check if selected - delegated to state service.

        Returns:
            bool: True if the element is selected, False otherwise.
        """
        return self._state_service.is_selected(self)

    def get_state_summary(self) -> Dict[str, Any]:
        """Get state summary - delegated to state service.

        Returns:
            Dict[str, Any]: The state summary of the element.
        """
        return self._state_service.get_state_summary(self)

    # Screenshot operations
    def capture_screenshot(self) -> Optional[np.ndarray]:
        """
        Capture screenshot of this element.

        Returns:
            Optional[np.ndarray]: Screenshot as numpy array, or None if failed.
        """
        try:
            if hasattr(self._element, 'capture_screenshot'):
                return self._element.capture_screenshot()
            
            # Fallback to session screenshot service
            if self._session and hasattr(self._session, 'screenshot_service'):
                return self._session.screenshot_service.capture_element_screenshot(self)
            
            return None
        except Exception:
            return None

    def take_screenshot(self) -> Optional[np.ndarray]:
        """
        Take screenshot of element (alias for capture_screenshot).

        Returns:
            Optional[np.ndarray]: Screenshot as numpy array, or None if failed.
        """
        return self.capture_screenshot()

    def wait_for_enabled(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for element to be enabled.

        Args:
            timeout (Optional[float]): Timeout in seconds.

        Returns:
            bool: True if element is enabled within timeout, False otherwise.
        """
        return self.wait_until_enabled(timeout)

    def wait_for_visible(self, timeout: Optional[float] = None) -> bool:
        """
        Wait for element to be visible.

        Args:
            timeout (Optional[float]): Timeout in seconds.

        Returns:
            bool: True if element is visible within timeout, False otherwise.
        """
        try:
            return self._wait_service.wait_for_condition(
                lambda: self.is_displayed(),
                timeout=timeout or self._session.config.timeout if self._session else 10.0
            )
        except Exception:
            return False

    def wait_for_condition(self, condition: Callable, timeout: Optional[float] = None) -> bool:
        """
        Wait for custom condition.

        Args:
            condition (callable): Condition function to wait for.
            timeout (Optional[float]): Timeout in seconds.

        Returns:
            bool: True if condition is met within timeout, False otherwise.
        """
        try:
            return self._wait_service.wait_for_condition(
                condition,
                timeout=timeout or self._session.config.timeout if self._session else 10.0
            )
        except Exception:
            return False

    # Utility methods
    def get_attributes(self) -> Dict[str, str]:
        """
        Get all attributes.

        Returns:
            Dict[str, str]: The attributes of the element.
        """
        attributes = {}
        for attr_name in ['name', 'automation_id', 'class_name', 'control_type', 'value', 'text']:
            value = self.get_attribute(attr_name)
            if value:
                attributes[attr_name] = value
        return attributes

    def get_properties(self) -> Dict[str, Any]:
        """
        Get all properties.

        Returns:
            Dict[str, Any]: The properties of the element.
        """
        properties = {}
        for prop_name in ELEMENT_PROPERTIES:
            value = self.get_property(prop_name)
            if value is not None:
                properties[prop_name] = value
        return properties

    def scroll_into_view(self) -> None:
        """Scroll element into view"""
        try:
            if hasattr(self._element, 'ScrollIntoView'):
                self._element.ScrollIntoView()
        except Exception as e:
            self._session.logger.error(f"Failed to scroll element into view: {e}")

    def safe_click(self, timeout: Optional[float] = None) -> bool:
        """
        Safely click element with wait.

        Args:
            timeout (Optional[float]): The timeout in seconds.

        Returns:
            bool: True if the element is clicked, False otherwise.
        """
        try:
            if self.wait_until_clickable(timeout):
                self.click()
                return True
            return False
        except Exception as e:
            self._session.logger.error(f"Safe click failed: {e}")
            return False 