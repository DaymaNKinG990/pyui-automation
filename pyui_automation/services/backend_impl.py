from .backend import BackendService
from typing import Any

class BackendServiceImpl(BackendService):
    def __init__(self, backend):
        self.backend = backend

    def find_element(self, by: str, value: str, timeout: float = 0) -> Any:
        return self.backend.find_element(by, value, timeout)

    def find_elements(self, by: str, value: str) -> list[Any]:
        return self.backend.find_elements(by, value)

    def capture_screenshot(self) -> Any:
        return self.backend.capture_screenshot()

    def get_active_window(self) -> Any:
        return self.backend.get_active_window()

    def get_screen_size(self) -> tuple:
        return self.backend.get_screen_size()

    def find_element_by_object_name(self, object_name: str) -> Any:
        return self.backend.find_element_by_object_name(object_name)

    def find_elements_by_object_name(self, object_name: str) -> list[Any]:
        return self.backend.find_elements_by_object_name(object_name)

    def find_element_by_widget_type(self, widget_type: str) -> Any:
        return self.backend.find_element_by_widget_type(widget_type)

    def find_elements_by_widget_type(self, widget_type: str) -> list[Any]:
        return self.backend.find_elements_by_widget_type(widget_type)

    def find_element_by_text(self, text: str) -> Any:
        return self.backend.find_element_by_text(text)

    def find_elements_by_text(self, text: str) -> list[Any]:
        return self.backend.find_elements_by_text(text)

    def find_element_by_property(self, property_name: str, value: str) -> Any:
        return self.backend.find_element_by_property(property_name, value)

    def find_elements_by_property(self, property_name: str, value: str) -> list[Any]:
        return self.backend.find_elements_by_property(property_name, value) 