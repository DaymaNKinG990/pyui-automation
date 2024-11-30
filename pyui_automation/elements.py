from typing import Optional, Tuple, Dict


class UIElement:
    """Represents a UI element across different platforms"""

    def __init__(self, native_element, automation):
        self._element = native_element
        self._automation = automation

    @property
    def text(self) -> str:
        """Get element text content"""
        return self._element.get_text()

    @property
    def name(self) -> str:
        """Get element name"""
        return self._element.get_name()

    @property
    def location(self) -> Tuple[int, int]:
        """Get element location (x, y coordinates)"""
        return self._element.get_location()

    @property
    def size(self) -> Tuple[int, int]:
        """Get element size (width, height)"""
        return self._element.get_size()

    @property
    def enabled(self) -> bool:
        """Check if element is enabled"""
        return self._element.is_enabled()

    @property
    def visible(self) -> bool:
        """Check if element is visible"""
        return self._element.is_visible()

    def click(self):
        """Click the element"""
        if self.visible and self.enabled:
            x, y = self._get_click_point()
            self._automation.mouse_move(x, y)
            self._automation.mouse_click()

    def double_click(self):
        """Double click the element"""
        if self.visible and self.enabled:
            x, y = self._get_click_point()
            self._automation.mouse_move(x, y)
            self._automation.mouse_click()
            self._automation.mouse_click()

    def right_click(self):
        """Right click the element"""
        if self.visible and self.enabled:
            x, y = self._get_click_point()
            self._automation.mouse_move(x, y)
            self._automation.mouse_click("right")

    def type_text(self, text: str, clear_first: bool = True):
        """Type text into the element"""
        self.click()  # Focus the element
        if clear_first:
            self.clear()
        self._automation.type_text(text)

    def clear(self):
        """Clear element content"""
        self._element.clear()

    def get_attribute(self, name: str) -> Optional[str]:
        """Get element attribute value"""
        return self._element.get_attribute(name)

    def get_property(self, name: str) -> Optional[str]:
        """Get element property value"""
        return self._element.get_property(name)

    def _get_click_point(self) -> Tuple[int, int]:
        """Get the coordinates for clicking the element"""
        x, y = self.location
        width, height = self.size
        return (x + width // 2, y + height // 2)
