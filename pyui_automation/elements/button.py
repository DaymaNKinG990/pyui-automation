from .base import UIElement
from typing import Optional


class Button(UIElement):
    """Button element class"""
    
    def is_pressed(self) -> bool:
        """
        Check if button is pressed

        Returns:
            True if button is pressed, False otherwise
        """
        return self.get_property('pressed')

    def wait_until_enabled(self, timeout: Optional[float] = None) -> bool:
        """
        Wait until the button is enabled.

        Args:
            timeout (Optional[float]): Maximum time to wait in seconds. Defaults to 10 seconds if not provided.

        Returns:
            bool: True if the button becomes enabled within the timeout period, otherwise raises WaitTimeout.
        """
        return self._session.waits.wait_until(
            lambda: self.is_enabled(),
            timeout=timeout if timeout is not None else 10.0,
            error_message="Button not enabled"
        )

    def wait_until_clickable(self, timeout: Optional[float] = None) -> bool:
        """
        Wait until button is clickable

        This method will wait until the button is both displayed and enabled.
        If the button becomes clickable within the given timeout period, the method will return True.
        Otherwise, a WaitTimeout exception will be raised.

        Args:
            timeout (Optional[float]): Maximum time to wait in seconds. Defaults to 10 seconds if not provided.

        Returns:
            bool: True if the button becomes clickable within the timeout period, otherwise raises WaitTimeout.
        """
        return self._session.waits.wait_until(
            lambda: self.is_displayed() and self.is_enabled(),
            timeout=timeout if timeout is not None else 10.0,
            error_message="Button not clickable"
        )

    def safe_click(self, timeout: Optional[float] = None) -> bool:
        """
        Safely click button after waiting for it to be clickable

        This method will wait until the button is both displayed and enabled.
        If the button becomes clickable within the given timeout period, the method will click the button
        and return True. Otherwise, the method will return False without attempting to click the button.

        Args:
            timeout (Optional[float]): Maximum time to wait in seconds. Defaults to 10 seconds if not provided.

        Returns:
            bool: True if the button becomes clickable within the timeout period and the click was successful,
                  otherwise False.
        """
        if self.wait_until_clickable(timeout if timeout is not None else 10.0):
            self.click()
            return True
        return False
