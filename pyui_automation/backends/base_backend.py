# Python imports
from abc import abstractmethod
from typing import Optional, List, Any, Tuple, Union
import numpy as np
from pathlib import Path
from logging import getLogger
from numpy.typing import NDArray

# Local imports
from ..core.interfaces import IBackend
from ..locators.interfaces import IBackendForLocator


class BaseBackend(IBackend, IBackendForLocator):
    """
    Abstract base class for all platform-specific backend implementations.

    Backends implement low-level operations for platform-specific functionality.
    All business logic and service calls must be moved to services, and the backend 
    implements only technical details for platform interaction.

    Purpose:
        - Provide a unified API for the service layer
        - Encapsulate all platform-specific details
        - Contain no business logic
        - Handle only core platform operations
    """

    def __init__(self) -> None:
        """Initialize backend with logger"""
        self._logger = getLogger(self.__class__.__name__)
        self._current_app = None
        self._initialized = False

    @property
    def logger(self) -> Any:
        """Get logger instance"""
        return self._logger

    @property
    def application(self) -> Any:
        """Get current application instance"""
        return self._current_app

    @abstractmethod
    def initialize(self) -> None:
        """Initialize backend"""
        pass

    @abstractmethod
    def is_initialized(self) -> bool:
        """Check if backend is initialized"""
        pass

    @abstractmethod
    def get_screen_size(self) -> Tuple[int, int]:
        """Get screen dimensions"""
        pass

    @abstractmethod
    def get_active_window(self) -> Optional[Any]:
        """Get currently active window"""
        pass

    @abstractmethod
    def get_window_handles(self) -> List[Any]:
        """Get all window handles"""
        pass

    @abstractmethod
    def get_window_handle(self, title: Union[str, int]) -> Optional[int]:
        """Get window handle by title or PID"""
        pass

    @abstractmethod
    def find_window(self, title: str) -> Optional[Any]:
        """Find window by title"""
        pass

    @abstractmethod
    def get_window_title(self, window: Any) -> str:
        """Get window title"""
        pass

    @abstractmethod
    def get_window_bounds(self, window: Any) -> Tuple[int, int, int, int]:
        """Get window position and size"""
        pass

    @abstractmethod
    def maximize_window(self, window: Any) -> None:
        """Maximize window"""
        pass

    @abstractmethod
    def minimize_window(self, window: Any) -> None:
        """Minimize window"""
        pass

    @abstractmethod
    def resize_window(self, window: Any, width: int, height: int) -> None:
        """Resize window"""
        pass

    @abstractmethod
    def set_window_position(self, window: Any, x: int, y: int) -> None:
        """Set window position"""
        pass

    @abstractmethod
    def close_window(self, window: Any) -> None:
        """Close window"""
        pass

    @abstractmethod
    def launch_application(self, path: Union[str, Path], args: List[str]) -> None:
        """Launch application"""
        pass

    @abstractmethod
    def attach_to_application(self, process_id: int) -> Optional[Any]:
        """Attach to existing application"""
        pass

    @abstractmethod
    def close_application(self, application: Any) -> None:
        """Close application"""
        pass

    @abstractmethod
    def get_application(self) -> Optional[Any]:
        """Get current application"""
        pass

    @abstractmethod
    def capture_screen_region(self, x: int, y: int, width: int, height: int) -> Optional[NDArray[np.uint8]]:
        """Capture screenshot of specific screen region"""
        pass

    @abstractmethod
    def capture_screenshot(self) -> Optional[NDArray[np.uint8]]:
        """Capture full screenshot as numpy array"""
        pass

    @abstractmethod
    def cleanup(self) -> None:
        """Cleanup backend resources"""
        pass

    @property
    def root(self) -> Any:
        """Get root element - to be implemented by subclasses"""
        raise NotImplementedError("root property must be implemented by subclasses")

    def _find_element_recursive(self, element: Any, property_name: str, value: str) -> Optional[Any]:
        """Find element recursively by property - to be implemented by subclasses"""
        raise NotImplementedError("_find_element_recursive must be implemented by subclasses")

    def _find_elements_recursive(self, element: Any, property_name: str, value: str, results: List[Any]) -> None:
        """Find elements recursively by property - to be implemented by subclasses"""
        raise NotImplementedError("_find_elements_recursive must be implemented by subclasses")

    def find_element_by_text(self, text: str) -> Optional[Any]:
        """Find element by text - to be implemented by subclasses"""
        raise NotImplementedError("find_element_by_text must be implemented by subclasses")

    def find_elements_by_text(self, text: str) -> List[Any]:
        """Find elements by text - to be implemented by subclasses"""
        raise NotImplementedError("find_elements_by_text must be implemented by subclasses")

    def find_element_by_property(self, property_name: str, value: str) -> Optional[Any]:
        """Find element by property - to be implemented by subclasses"""
        raise NotImplementedError("find_element_by_property must be implemented by subclasses")

    def find_elements_by_property(self, property_name: str, value: str) -> List[Any]:
        """Find elements by property - to be implemented by subclasses"""
        raise NotImplementedError("find_elements_by_property must be implemented by subclasses")

    def find_element_by_object_name(self, name: str) -> Optional[Any]:
        """Find element by object name - to be implemented by subclasses"""
        raise NotImplementedError("find_element_by_object_name must be implemented by subclasses")

    def find_elements_by_object_name(self, name: str) -> List[Any]:
        """Find elements by object name - to be implemented by subclasses"""
        raise NotImplementedError("find_elements_by_object_name must be implemented by subclasses")

    def find_element_by_widget_type(self, widget_type: str) -> Optional[Any]:
        """Find element by widget type - to be implemented by subclasses"""
        raise NotImplementedError("find_element_by_widget_type must be implemented by subclasses")

    def find_elements_by_widget_type(self, widget_type: str) -> List[Any]:
        """Find elements by widget type - to be implemented by subclasses"""
        raise NotImplementedError("find_elements_by_widget_type must be implemented by subclasses")
        
    def double_click_mouse(self) -> bool:
        """Double click mouse (default implementation)"""
        return False
        
    def right_click_mouse(self) -> bool:
        """Right click mouse (default implementation)"""
        return False
        
    def type_text_into_element(self, element: Any, text: str) -> bool:
        """Type text into element (default implementation)"""
        return False

    def __del__(self) -> None:
        """Destructor to ensure cleanup"""
        try:
            self.cleanup()
        except Exception:
            pass
