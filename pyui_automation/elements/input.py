from typing import Optional
from .base import UIElement


class Input(UIElement):
    """Input element class"""

    @property
    def value(self) -> str:
        """Get input value"""
        return self.get_property('value')

    @value.setter
    def value(self, text: str) -> None:
        """
        Set input value

        This method sets the value of the input element. The old value is cleared
        before setting the new value.

        Args:
            text (str): New value for the input element.

        Returns:
            None
        """
        self.clear()
        self.send_keys(text)

    @value.deleter
    def value(self):
        self._value = ""

    def clear(self) -> None:
        """
        Clear input value

        This method clears the current value of the input element.

        Returns:
            None
        """
        self._element.clear()

    def append(self, text: str) -> None:
        """
        Append text to current value

        This method appends the given text to the current value of the input element.
        
        Args:
            text (str): The text to append to the current value.
        """
        self.send_keys(text)

    def focus(self) -> None:
        """
        Set focus to input

        This method sets the focus to the input element.
        """
        self.click()

    def select_all(self) -> None:
        """
        Select all text in input

        This method selects all text in the input element.
        """
        self.focus()
        self._session.keyboard.select_all()

    def copy(self) -> None:
        """
        Copy selected text

        This method copies the selected text from the input element to the
        system clipboard.
        """
        self._session.keyboard.copy()

    def paste(self) -> None:
        """Paste text from the clipboard into the input field."""
        self._session.keyboard.paste()

    def wait_until_value_is(self, expected_value: str, timeout: Optional[float] = None) -> bool:
        """
        Wait until input has expected value

        Args:
            expected_value (str): Expected input value
            timeout (Optional[float]): Maximum time to wait in seconds

        Returns:
            bool: True if expected value is found, raises WaitTimeout otherwise
        """
        return self._session.waits.wait_until(
            lambda: self.value == expected_value,
            timeout=timeout if timeout is not None else 10.0,
            error_message=f"Input value not equal to '{expected_value}'"
        )
