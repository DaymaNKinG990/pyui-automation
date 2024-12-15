from typing import Optional, Tuple


class UIElement:
    """Represents a UI element across different platforms"""

    def __init__(self, native_element, automation) -> None:
        """
        Initialize a UIElement instance.

        Args:
            native_element: The native element representation for the current platform.
            automation: The automation session associated with this UI element.
        """
        self._element = native_element
        self._automation = automation

    @property
    def id(self) -> Optional[str]:
        """
        Get element ID.

        Returns:
            Element ID or None if element does not have an ID.
        """
        if hasattr(self._element, 'CurrentAutomationId'):
            return self._element.CurrentAutomationId
        return self._element.get_id() if hasattr(self._element, 'get_id') else None

    @property
    def text(self) -> Optional[str]:
        """
        Retrieve the text content of the UI element.

        This property checks if the underlying native element has a 'CurrentValue'
        attribute or a 'get_text' method to obtain the text content. If neither
        exists, it returns an empty string.

        Returns:
            Optional[str]: The text content of the element, or an empty string
            if the text is not available.
        """
        if hasattr(self._element, 'CurrentValue'):
            return self._element.CurrentValue
        return self._element.get_text() if hasattr(self._element, 'get_text') else ''

    @property
    def name(self) -> str:
        """
        Get element name

        This property retrieves the element name from the underlying native
        element. It first checks if the native element has a 'CurrentName'
        attribute. If not, it checks for a 'get_name' method. If neither exists,
        it returns an empty string.

        Returns:
            str: The element name, or an empty string if the name is not available.
        """
        if hasattr(self._element, 'CurrentName'):
            return self._element.CurrentName
        return self._element.get_name() if hasattr(self._element, 'get_name') else ''

    @property
    def location(self) -> Tuple[int, int]:
        """
        Get element location (x, y coordinates)

        This property retrieves the element location from the underlying native
        element. It first checks if the native element has a 'CurrentBoundingRectangle'
        attribute. If not, it checks for a 'get_location' method. If neither exists,
        it returns (0, 0).

        Returns:
            Tuple[int, int]: The element location as (x, y) coordinates.
        """
        if hasattr(self._element, 'CurrentBoundingRectangle'):
            rect = self._element.CurrentBoundingRectangle
            return (rect[0], rect[1])
        if hasattr(self._element, 'get_location'):
            return self._element.get_location()
        return (0, 0)

    @property
    def size(self) -> Tuple[int, int]:
        """
        Get element size (width, height)

        This property retrieves the size of the element from the underlying native
        element. It first checks if the native element has a 'CurrentBoundingRectangle'
        attribute. If not, it checks for a 'get_size' method. If neither exists,
        it returns (0, 0).

        Returns:
            Tuple[int, int]: The element size as (width, height) coordinates.
        """
        if hasattr(self._element, 'CurrentBoundingRectangle'):
            rect = self._element.CurrentBoundingRectangle
            return (rect[2] - rect[0], rect[3] - rect[1])
        if hasattr(self._element, 'get_size'):
            return self._element.get_size()
        return (0, 0)

    @property
    def enabled(self) -> bool:
        """
        Check if element is enabled.

        This property checks whether the element is currently enabled and can
        be interacted with.

        Returns:
            bool: True if the element is enabled, False otherwise.
        """
        if hasattr(self._element, 'CurrentIsEnabled'):
            return self._element.CurrentIsEnabled
        return self._element.is_enabled() if hasattr(self._element, 'is_enabled') else False

    @property
    def visible(self) -> bool:
        """
        Check if element is visible.

        This property checks whether the element is currently visible on the screen.
        It first checks if the native element has a 'CurrentIsOffscreen' attribute.
        If not, it checks for an 'is_visible' method. If neither exists, it returns False.

        Returns:
            bool: True if the element is visible, False otherwise.
        """
        if hasattr(self._element, 'CurrentIsOffscreen'):
            return not self._element.CurrentIsOffscreen
        return self._element.is_visible() if hasattr(self._element, 'is_visible') else False

    def click(self) -> None:
        """
        Click the element

        This method clicks the element if it is both visible and enabled. It 
        computes the click point, moves the mouse to that location, and 
        performs the click action.
        """
        if self.visible and self.enabled:
            x, y = self._get_click_point()
            self._automation.mouse.move(x, y)
            self._automation.mouse.click()

    def double_click(self) -> None:
        """
        Double click the element

        This method double-clicks the element if it is both visible and enabled.
        It computes the click point, moves the mouse to that location, and
        performs the double-click action.
        """
        if self.visible and self.enabled:
            x, y = self._get_click_point()
            self._automation.mouse.move(x, y)
            self._automation.mouse.double_click()

    def right_click(self) -> None:
        """
        Right click the element

        This method right-clicks the element if it is both visible and enabled.
        It computes the click point, moves the mouse to that location, and
        performs the right-click action.
        """
        if self.visible and self.enabled:
            x, y = self._get_click_point()
            self._automation.mouse.move(x, y)
            self._automation.mouse.right_click()

    def type_text(self, text: str, interval: float = 0.0) -> None:
        """
        Type text into element

        Args:
            text (str): The text to type
            interval (float): The interval in seconds between each keystroke.
                Defaults to 0.0.
        """
        if self.visible and self.enabled:
            self.click()  # Focus element first
            self._automation.keyboard.type_text(text, interval)

    def clear(self) -> None:
        """
        Clear element content

        This method clears the content of the element. If the element supports 
        the 'clear' method, it uses that method. Otherwise, it simulates a 
        clear action by selecting all text and pressing the delete key.
        """
        if hasattr(self._element, 'clear'):
            self._element.clear()
        else:
            self.click()
            self._automation.keyboard.press('ctrl+a')
            self._automation.keyboard.press('delete')

    def get_attribute(self, name: str) -> Optional[str]:
        """
        Get element attribute value

        Args:
            name (str): The name of the attribute to retrieve

        Returns:
            Optional[str]: The value of the attribute, or None if the attribute does not exist
        """
        if hasattr(self._element, 'get_attribute'):
            return self._element.get_attribute(name)
        return None

    def get_property(self, name: str) -> Optional[str]:
        """
        Get element property value

        Args:
            name (str): The name of the property to retrieve

        Returns:
            Optional[str]: The value of the property, or None if the property does not exist
        """
        if hasattr(self._element, 'get_property'):
            return self._element.get_property(name)
        return None

    def _get_click_point(self) -> Tuple[int, int]:
        """
        Get coordinates for clicking element

        Returns the coordinates for clicking the element, which is the center of the element.
        """
        x, y = self.location
        width, height = self.size
        return (x + width // 2, y + height // 2)
