from abc import ABC, abstractmethod
from typing import Any

class InputService(ABC):
    """Abstract input service interface (keyboard, mouse, game input)."""

    @abstractmethod
    def click(self, element: Any) -> None:
        """Click on the given element"""
        pass

    @abstractmethod
    def double_click(self, element: Any) -> None:
        """Double click on the given element"""
        pass

    @abstractmethod
    def right_click(self, element: Any) -> None:
        """Right click on the given element"""
        pass

    @abstractmethod
    def type_text(self, element: Any, text: str, interval: float = 0.0) -> None:
        """Type text into the given element"""
        pass

    @abstractmethod
    def send_keys(self, element: Any, *keys: str) -> None:
        """Send keys to the given element"""
        pass

    @abstractmethod
    def press_key(self, key: str) -> None:
        pass

    @abstractmethod
    def release_key(self, key: str) -> None:
        pass

    @abstractmethod
    def move_mouse(self, x: int, y: int) -> None:
        pass

    @abstractmethod
    def click_mouse(self, x: int, y: int, button: str = "left") -> None:
        pass 