"""Keyboard input handling"""

from typing import Optional
from ..backends.base import BaseBackend


class Keyboard:
    """Keyboard input handler"""
    
    def __init__(self, backend: BaseBackend) -> None:
        """
        Initialize keyboard input handler
        
        Args:
            backend: Platform-specific backend to use for keyboard input
        """
        self._backend = backend

    def type_text(self, text: str, interval: float = 0.0) -> bool:
        """
        Type text with optional interval between keystrokes

        Args:
            text: The text to type.
            interval: The interval in seconds between each keystroke. Defaults to 0.0.

        Returns:
            bool: True if the text was typed successfully, False otherwise.

        Raises:
            ValueError: If the text is not a string.
        """
        if not isinstance(text, str):
            raise ValueError("Text must be a string")
        if not text:
            return True
        return self._backend.type_text(text, interval)

    def press_key(self, key: str) -> bool:
        """
        Press a single key

        Args:
            key: The key to press.

        Returns:
            bool: True if the key was pressed successfully, False otherwise.

        Raises:
            ValueError: If the key is not a string.
        """
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        if not key:
            return True
        return self._backend.press_key(key)

    def release_key(self, key: str) -> bool:
        """
        Release a single key

        Args:
            key: The key to release.

        Returns:
            bool: True if the key was released successfully, False otherwise.

        Raises:
            ValueError: If the key is not a string.
        """
        if not isinstance(key, str):
            raise ValueError("Key must be a string")
        if not key:
            return True
        return self._backend.release_key(key)

    def press_keys(self, *keys: str) -> bool:
        """
        Press multiple keys simultaneously

        Args:
            *keys: The keys to press simultaneously.

        Returns:
            bool: True if all keys were pressed successfully, False otherwise.

        Raises:
            ValueError: If any of the keys are not strings.
        """
        if not all(isinstance(key, str) for key in keys):
            raise ValueError("All keys must be strings")
        if not keys:
            return True
        return self._backend.press_keys(*keys)

    def release_keys(self, *keys: str) -> bool:
        """
        Release multiple keys simultaneously

        Args:
            *keys: The keys to release simultaneously.

        Returns:
            bool: True if all keys were released successfully, False otherwise.

        Raises:
            ValueError: If any of the keys are not strings.
        """
        if not all(isinstance(key, str) for key in keys):
            raise ValueError("All keys must be strings")
        if not keys:
            return True
        return self._backend.release_keys(*keys)

    def send_keys(self, keys: str) -> bool:
        """
        Send a sequence of keys with special key support

        Sends a sequence of keys to the currently active window. This method
        supports special keys, such as modifier keys (e.g. Ctrl, Shift, Alt) and
        function keys (e.g. F1-F12).

        Args:
            keys: The sequence of keys to send.

        Returns:
            bool: True if the keys were sent successfully, False otherwise.

        Raises:
            ValueError: If the keys are not a string.
        """
        if not isinstance(keys, str):
            raise ValueError("Keys must be a string")
        if not keys:
            return True
        return self._backend.send_keys(keys)
