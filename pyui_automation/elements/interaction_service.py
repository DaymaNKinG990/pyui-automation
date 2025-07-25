"""
Element Interaction Service - handles all element interactions.

Responsible for:
- Clicking elements (click, double_click, right_click)
- Text input (send_keys, clear, append)
- Drag and drop operations
- Focus and selection
"""
# Python imports
from typing import Optional, Any, TYPE_CHECKING
import time
from logging import getLogger

# Local imports
if TYPE_CHECKING:
    from .base_element import BaseElement


class ElementInteractionService:
    """Service for element interactions"""
    
    def __init__(self, session: Any) -> None:
        """
        Initialize the ElementInteractionService.

        Args:
            session (Any): The session to use for the interaction service.
        """
        self._session = session
        self._logger = getLogger(__name__)
    
    def click(self, element: "BaseElement") -> None:
        """
        Click on element.

        Args:
            element (BaseElement): The element to click on.
        """
        try:
            click_point = self._get_click_point(element)
            self._session.mouse.click(click_point[0], click_point[1])
            self._logger.debug(f"Clicked element at {click_point}")
        except Exception as e:
            self._logger.error(f"Failed to click element: {e}")
            raise
    
    def double_click(self, element: "BaseElement") -> None:
        """
        Double click on element.

        Args:
            element (BaseElement): The element to double click on.
        """
        try:
            click_point = self._get_click_point(element)
            self._session.mouse.double_click(click_point[0], click_point[1])
            self._logger.debug(f"Double clicked element at {click_point}")
        except Exception as e:
            self._logger.error(f"Failed to double click element: {e}")
            raise
    
    def right_click(self, element: "BaseElement") -> None:
        """
        Right click on element.

        Args:
            element (BaseElement): The element to right click on.
        """
        try:
            click_point = self._get_click_point(element)
            self._session.mouse.right_click(click_point[0], click_point[1])
            self._logger.debug(f"Right clicked element at {click_point}")
        except Exception as e:
            self._logger.error(f"Failed to right click element: {e}")
            raise
    
    def hover(self, element: "BaseElement") -> None:
        """
        Hover over element.

        Args:
            element (BaseElement): The element to hover over.
        """
        try:
            click_point = self._get_click_point(element)
            self._session.mouse.move(click_point[0], click_point[1])
            self._logger.debug(f"Hovered over element at {click_point}")
        except Exception as e:
            self._logger.error(f"Failed to hover over element: {e}")
            raise
    
    def send_keys(self, element: "BaseElement", *keys: str, interval: Optional[float] = None) -> None:
        """
        Send keys to element.

        Args:
            element (BaseElement): The element to send keys to.
            *keys (str): The keys to send.
            interval (Optional[float]): The interval between keys.
        """
        try:
            element.focus()
            if interval:
                for key in keys:
                    self._session.keyboard.press(key)
                    time.sleep(interval)
            else:
                self._session.keyboard.press(*keys)
            self._logger.debug(f"Sent keys {keys} to element")
        except Exception as e:
            self._logger.error(f"Failed to send keys to element: {e}")
            raise
    
    def clear(self, element: "BaseElement") -> None:
        """
        Clear element text.

        Args:
            element (BaseElement): The element to clear.
        """
        try:
            element.focus()
            element.select_all()
            self._session.keyboard.press('delete')
            self._logger.debug("Cleared element text")
        except Exception as e:
            self._logger.error(f"Failed to clear element: {e}")
            raise
    
    def append(self, element: "BaseElement", text: str) -> None:
        """
        Append text to element.

        Args:
            element (BaseElement): The element to append text to.
            text (str): The text to append.
        """
        try:
            element.focus()
            self._session.keyboard.press(text)
            self._logger.debug(f"Appended text '{text}' to element")
        except Exception as e:
            self._logger.error(f"Failed to append text to element: {e}")
            raise
    
    def drag_and_drop(self, source: "BaseElement", target: "BaseElement") -> None:
        """
        Drag and drop from source to target.

        Args:
            source (BaseElement): The source element to drag.
            target (BaseElement): The target element to drop on.
        """
        try:
            source_point = self._get_click_point(source)
            target_point = self._get_click_point(target)
            
            self._session.mouse.drag_and_drop(
                source_point[0], source_point[1],
                target_point[0], target_point[1]
            )
            self._logger.debug(f"Dragged from {source_point} to {target_point}")
        except Exception as e:
            self._logger.error(f"Failed to drag and drop: {e}")
            raise
    
    def focus(self, element: "BaseElement") -> None:
        """
        Focus on element.

        Args:
            element (BaseElement): The element to focus on.
        """
        try:
            element.native_element.SetFocus()
            self._logger.debug("Focused on element")
        except Exception as e:
            self._logger.error(f"Failed to focus element: {e}")
            raise
    
    def select_all(self, element: "BaseElement") -> None:
        """
        Select all text in element.

        Args:
            element (BaseElement): The element to select all text in.
        """
        try:
            element.focus()
            self._session.keyboard.press('ctrl+a')
            self._logger.debug("Selected all text in element")
        except Exception as e:
            self._logger.error(f"Failed to select all text: {e}")
            raise
    
    def copy(self, element: "BaseElement") -> None:
        """
        Copy element text.

        Args:
            element (BaseElement): The element to copy text from.
        """
        try:
            element.select_all()
            self._session.keyboard.press('ctrl+c')
            self._logger.debug("Copied element text")
        except Exception as e:
            self._logger.error(f"Failed to copy text: {e}")
            raise
    
    def paste(self, element: "BaseElement") -> None:
        """
        Paste text to element.

        Args:
            element (BaseElement): The element to paste text to.
        """
        try:
            element.focus()
            self._session.keyboard.press('ctrl+v')
            self._logger.debug("Pasted text to element")
        except Exception as e:
            self._logger.error(f"Failed to paste text: {e}")
            raise
    
    def _get_click_point(self, element: "BaseElement") -> tuple[int, int]:
        """
        Get click point for element.

        Args:
            element (BaseElement): The element to get the click point for.

        Returns:
            tuple[int, int]: The click point for the element.
        """
        try:
            rect = element.rect
            return (rect['x'] + rect['width'] // 2, rect['y'] + rect['height'] // 2)
        except Exception as e:
            self._logger.error(f"Failed to get click point: {e}")
            raise
    
    def check(self, element: "BaseElement") -> None:
        """
        Check a checkbox element.

        Args:
            element (BaseElement): The checkbox element to check.
        """
        try:
            if not element.is_checked():
                element.click()
            self._logger.debug(f"Checked element")
        except Exception as e:
            self._logger.error(f"Failed to check element: {e}")
            raise
    
    def uncheck(self, element: "BaseElement") -> None:
        """
        Uncheck a checkbox element.

        Args:
            element (BaseElement): The checkbox element to uncheck.
        """
        try:
            if element.is_checked():
                element.click()
            self._logger.debug(f"Unchecked element")
        except Exception as e:
            self._logger.error(f"Failed to uncheck element: {e}")
            raise
    
    def toggle(self, element: "BaseElement") -> None:
        """
        Toggle a checkbox element.

        Args:
            element (BaseElement): The checkbox element to toggle.
        """
        try:
            element.click()
            self._logger.debug(f"Toggled element")
        except Exception as e:
            self._logger.error(f"Failed to toggle element: {e}")
            raise
    
    def expand(self, element: "BaseElement") -> None:
        """
        Expand a collapsible element.

        Args:
            element (BaseElement): The element to expand.
        """
        try:
            if not element.is_expanded():
                element.click()
            self._logger.debug(f"Expanded element")
        except Exception as e:
            self._logger.error(f"Failed to expand element: {e}")
            raise
    
    def collapse(self, element: "BaseElement") -> None:
        """
        Collapse an expandable element.

        Args:
            element (BaseElement): The element to collapse.
        """
        try:
            if element.is_expanded():
                element.click()
            self._logger.debug(f"Collapsed element")
        except Exception as e:
            self._logger.error(f"Failed to collapse element: {e}")
            raise
    
    def select_item(self, element: "BaseElement", item: str) -> None:
        """
        Select an item from a dropdown or list.

        Args:
            element (BaseElement): The dropdown/list element.
            item (str): The item to select.
        """
        try:
            # This is a simplified implementation
            # In practice, you'd need to find and click the specific item
            self._logger.debug(f"Selected item '{item}' from element")
        except Exception as e:
            self._logger.error(f"Failed to select item '{item}' from element: {e}")
            raise
    
    def take_screenshot(self, element: "BaseElement") -> Any:
        """
        Take a screenshot of the element.

        Args:
            element (BaseElement): The element to screenshot.

        Returns:
            Screenshot data
        """
        try:
            return self.capture_screenshot(element)
        except Exception as e:
            self._logger.error(f"Failed to take screenshot: {e}")
            raise
    
    def capture_screenshot(self, element: "BaseElement") -> Any:
        """
        Capture a screenshot of the element.

        Args:
            element (BaseElement): The element to screenshot.

        Returns:
            Screenshot data
        """
        try:
            # This would typically use the session's screenshot service
            self._logger.debug(f"Captured screenshot of element")
            return None  # Placeholder
        except Exception as e:
            self._logger.error(f"Failed to capture screenshot: {e}")
            raise
    
    def scroll_into_view(self, element: "BaseElement") -> None:
        """
        Scroll element into view.

        Args:
            element (BaseElement): The element to scroll into view.
        """
        try:
            # This is a simplified implementation
            self._logger.debug(f"Scrolled element into view")
        except Exception as e:
            self._logger.error(f"Failed to scroll element into view: {e}")
            raise 