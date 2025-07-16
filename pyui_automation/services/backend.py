from abc import ABC, abstractmethod
from typing import Any

class BackendService(ABC):
    """Abstract backend service interface."""

    # Удалены методы find_element и find_elements (универсальные by/value)

    @abstractmethod
    def capture_screenshot(self) -> Any:
        pass

    @abstractmethod
    def get_active_window(self) -> Any:
        pass

    @abstractmethod
    def get_screen_size(self) -> tuple:
        pass

    @abstractmethod
    def find_element_by_object_name(self, object_name: str) -> Any:
        pass

    @abstractmethod
    def find_elements_by_object_name(self, object_name: str) -> list[Any]:
        pass

    @abstractmethod
    def find_element_by_widget_type(self, widget_type: str) -> Any:
        pass

    @abstractmethod
    def find_elements_by_widget_type(self, widget_type: str) -> list[Any]:
        pass

    @abstractmethod
    def find_element_by_text(self, text: str) -> Any:
        pass

    @abstractmethod
    def find_elements_by_text(self, text: str) -> list[Any]:
        pass

    @abstractmethod
    def find_element_by_property(self, property_name: str, value: str) -> Any:
        pass

    @abstractmethod
    def find_elements_by_property(self, property_name: str, value: str) -> list[Any]:
        pass 