from typing import Optional, Any, Dict, TYPE_CHECKING, List
import numpy as np
import time

if TYPE_CHECKING:
    from ..core.session import AutomationSession


class UIElement:
    """Base class for UI elements"""
    
    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        """
        Initialize a UIElement instance.

        Args:
            native_element (Any): The native element representation for the current platform.
            session (AutomationSession): The automation session associated with this UI element.
        """
        self._element = native_element
        self._session = session

    @property
    def native_element(self) -> Any:
        """
        Get native element

        Returns native element representation for the current platform.
        """
        return self._element

    @property
    def session(self) -> 'AutomationSession':
        """
        Get the automation session associated with this UI element.

        Returns:
            AutomationSession: The current automation session.
        """
        return self._session

    def get_attribute(self, name: str) -> Optional[str]:
        """
        Get element attribute

        Returns the value of the given attribute for the element, or None
        if the attribute does not exist.
        """
        return self._element.get_attribute(name)

    def get_property(self, name: str) -> Any:
        """
        Get element property

        Returns the value of the given property for the element.

        Args:
            name (str): The name of the property to retrieve.

        Returns:
            Any: The value of the property, or None if the property does not exist.
        """
        return self._element.get_property(name)

    @property
    def text(self) -> str:
        """
        Get element text

        This property retrieves the text content of the UI element, if available.
        
        Returns:
            str: The text content of the element.
        """
        return self._element.text

    @property
    def location(self) -> Dict[str, int]:
        """
        Get element location

        This property retrieves the (x, y) coordinates of the UI element's
        top-left corner.

        Returns:
            Dict[str, int]: A dictionary containing the x and y coordinates
                of the element's location.
        """
        return self._element.location

    @property
    def size(self) -> Dict[str, int]:
        """
        Get element size

        This property retrieves the size (width and height) of the UI element.

        Returns:
            Dict[str, int]: A dictionary containing the width and height of the element.
        """
        return self._element.size

    @property
    def name(self) -> str:
        """
        Get element name

        This property retrieves the name of the UI element. It first tries to get
        the CurrentName attribute, and if that's not available, falls back to the
        get_name method.

        Returns:
            str: The name of the element.
        """
        if hasattr(self._element, 'CurrentName'):
            return self._element.CurrentName
        elif hasattr(self._element, 'get_name'):
            return self._element.get_name()
        return ""

    @property
    def visible(self) -> bool:
        """
        Check if element is visible

        This property checks whether the element is visible on the screen
        by checking if it is not offscreen.

        Returns:
            bool: True if the element is visible (not offscreen), False otherwise.
        """
        if hasattr(self._element, 'CurrentIsOffscreen'):
            return not self._element.CurrentIsOffscreen
        return self.is_displayed()

    def is_displayed(self) -> bool:
        """
        Check if element is displayed

        This property checks whether the element is visible on the screen.

        Returns:
            bool: True if the element is visible, False otherwise.
        """
        return self._element.is_displayed()

    def is_enabled(self) -> bool:
        """
        Check if element is enabled

        This property checks whether the element is currently enabled and
        can be interacted with.

        Returns:
            bool: True if the element is enabled, False otherwise.
        """
        return self._element.is_enabled()

    def _get_click_point(self) -> tuple[int, int]:
        """
        Get the point where the element should be clicked.
        By default, this is the center of the element's bounding rectangle.

        Returns:
            tuple[int, int]: The (x, y) coordinates where the element should be clicked
        """
        loc = self.location
        size = self.size
        if not loc or not size:
            raise ValueError("Cannot determine click point - element has no location or size")
            
        # Calculate center point
        x = loc['x'] + size['width'] // 2
        y = loc['y'] + size['height'] // 2
        return x, y

    def click(self) -> None:
        """
        Click element

        This method clicks the element. The element should be visible and enabled.
        """
        self._element.click()

    def double_click(self) -> None:
        """
        Double click element

        This method double-clicks the element. The element should be visible and enabled.
        """
        self._session.mouse.double_click(self.location['x'], self.location['y'])

    def right_click(self) -> None:
        """
        Right click element

        This method performs a right-click action on the element. The element
        should be visible and enabled.

        """
        self._session.mouse.right_click(self.location['x'], self.location['y'])

    def hover(self) -> None:
        """
        Hover over element

        This method moves the mouse over the element. This can be useful for
        triggering hover events.

        """
        self._session.mouse.move(self.location['x'], self.location['y'])

    def send_keys(self, *keys: str, interval: Optional[float] = None) -> None:
        """
        Send keys to element

        This method sends the specified keys to the element. The element should
        be visible and enabled.

        Args:
            *keys (str): The keys to send to the element. The keys can be
                         specified as a single string or as separate arguments.
            interval (float, optional): The interval between keystrokes in seconds.
                                      If None, keys are sent without delay.

        """
        if interval is not None:
            self._session.keyboard.type_text(*keys, interval=interval)
        else:
            self._element.send_keys(*keys)

    def clear(self) -> None:
        """
        Clear the element's content.

        This method clears any input or editable content in the element.
        The element should be visible and enabled.
        """
        if hasattr(self._element, 'clear') and callable(self._element.clear):
            self._element.clear()
        else:
            # Fallback: send backspaces
            text = self.text or ""
            if text:
                self.send_keys("\b" * len(text))

    def capture_screenshot(self) -> Optional[np.ndarray]:
        """Capture screenshot of this element
        
        Returns:
            Screenshot as numpy array if successful, None otherwise
        """
        if hasattr(self._element, 'capture_screenshot'):
            result = self._element.capture_screenshot()
            import numpy as np
            if isinstance(result, np.ndarray):
                return result
            print('DEBUG: return None (native result not ndarray)')
            return None
        # Fallback to capturing region from full screenshot
        screenshot = self._session.take_screenshot()
        import numpy as np
        print('DEBUG: screenshot type:', type(screenshot))
        if isinstance(screenshot, np.ndarray):
            # Get element bounds
            loc = self.location
            size = self.size
            print('DEBUG: location:', loc, type(loc), 'size:', size, type(size))
            if not loc or not size:
                print('DEBUG: loc or size is None, return None')
                return None
            # Crop to element bounds
            x, y = loc['x'], loc['y']
            width, height = size['width'], size['height']
            crop = screenshot[y:y+height, x:x+width]
            print('DEBUG: crop shape:', crop.shape if isinstance(crop, np.ndarray) else None)
            return crop
        print('DEBUG: screenshot is not np.ndarray, return None')
        return None

    def drag_and_drop(self, target: 'UIElement') -> None:
        """
        Drag this element and drop it onto the target element.

        Args:
            target (UIElement): The target element to drop onto
        """
        # Get source and target coordinates
        source_x, source_y = self._get_click_point()
        target_x, target_y = target._get_click_point()

        # Perform drag and drop operation
        self._session.mouse.drag_and_drop(source_x, source_y, target_x, target_y)

    def scroll_into_view(self) -> None:
        """
        Scroll the element into view if it's not currently visible.
        """
        if hasattr(self._element, 'scroll_into_view'):
            self._element.scroll_into_view()
        else:
            # Fallback implementation using JavaScript if available
            self._session.execute_script('arguments[0].scrollIntoView(true);', self._element)

    def wait_for_enabled(self, timeout: float = 10) -> bool:
        """
        Wait for the element to become enabled.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if element became enabled within timeout, False otherwise
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_enabled():
                return True
            time.sleep(0.1)
        return False

    def wait_for_visible(self, timeout: float = 10) -> bool:
        """
        Wait for the element to become visible.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if element became visible within timeout, False otherwise
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.is_displayed():
                return True
            time.sleep(0.1)
        return False

    def get_parent(self) -> Optional['UIElement']:
        """
        Get the parent element of this element.

        Returns:
            Optional[UIElement]: The parent element, or None if no parent exists
        """
        if hasattr(self._element, 'get_parent'):
            parent = self._element.get_parent()
            return UIElement(parent, self._session) if parent else None
        return None

    def get_children(self) -> List['UIElement']:
        """
        Get all child elements of this element.

        Returns:
            List[UIElement]: List of child elements
        """
        if hasattr(self._element, 'get_children'):
            children = self._element.get_children()
            return [UIElement(child, self._session) for child in children]
        return []

    # Удалены устаревшие методы поиска find_element и find_elements

    def take_screenshot(self) -> Optional[np.ndarray]:
        """
        Capture a screenshot of this element.

        Returns:
            Optional[np.ndarray]: Screenshot as numpy array if successful, None otherwise
        """
        return self.capture_screenshot()

    def get_attributes(self) -> Dict[str, str]:
        """
        Get all attributes of the element.

        Returns:
            Dict[str, str]: Dictionary of attribute names and values
        """
        if hasattr(self._element, 'get_attributes'):
            return self._element.get_attributes()
        
        # Fallback: Try to get common attributes
        attrs = {}
        common_attrs = ['id', 'class', 'name', 'title', 'type', 'value']
        for attr in common_attrs:
            value = self.get_attribute(attr)
            if value is not None:
                attrs[attr] = value
        return attrs

    def get_properties(self) -> Dict[str, Any]:
        """
        Get all properties of the element.

        Returns:
            Dict[str, Any]: Dictionary of property names and values
        """
        if hasattr(self._element, 'get_properties'):
            return self._element.get_properties()
            
        # Fallback: Try to get common properties
        props = {}
        common_props = ['tagName', 'textContent', 'innerText', 'innerHTML', 'outerHTML']
        for prop in common_props:
            value = self.get_property(prop)
            if value is not None:
                props[prop] = value
        return props

    @property
    def rect(self) -> Dict[str, int]:
        """
        Get the element's bounding rectangle.

        Returns:
            Dict[str, int]: Dictionary with x, y, width, and height
        """
        loc = self.location
        size = self.size
        return {
            'x': loc['x'],
            'y': loc['y'],
            'width': size['width'],
            'height': size['height']
        }

    @property
    def center(self) -> Dict[str, int]:
        """
        Get the center point of the element.

        Returns:
            Dict[str, int]: Dictionary with x and y coordinates of the center point
        """
        x, y = self._get_click_point()
        return {'x': x, 'y': y}

    @property
    def value(self) -> Optional[str]:
        """
        Get or set the value of the element.

        Returns:
            Optional[str]: The element's value
        """
        if hasattr(self._element, 'value'):
            return self._element.value
        return self.get_attribute('value')

    @value.setter
    def value(self, new_value: str) -> None:
        """
        Set the value of the element.

        Args:
            new_value (str): The value to set
        """
        if hasattr(self._element, 'value'):
            self._element.value = new_value
        else:
            self.clear()
            self.send_keys(new_value)

    @property
    def is_selected(self) -> bool:
        """
        Check if the element is selected.

        Returns:
            bool: True if the element is selected, False otherwise.
        """
        return bool(self.get_property('selected'))

    @property
    def automation_id(self) -> str:
        """Returns the AutomationId of the element (Windows UIA)."""
        return getattr(self._element, 'CurrentAutomationId', None)

    @property
    def class_name(self) -> str:
        """Returns the ClassName of the element (Windows UIA)."""
        return getattr(self._element, 'CurrentClassName', None)
