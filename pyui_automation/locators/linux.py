from typing import Optional, List, Any
from .base import BaseLocator, LocatorStrategy, ByName, ByRole, ByDescription, ByPath, ByState


class LinuxLocator(BaseLocator):
    """
    Linux AT-SPI2 locator implementation.
    Supports element finding strategies using AT-SPI2 accessibility framework.
    """

    def _find_element_impl(self, strategy: LocatorStrategy) -> Optional[Any]:
        """
        Find a single element using the specified strategy.
        
        Args:
            strategy: LocatorStrategy instance defining the search method
            
        Returns:
            AT-SPI2 element if found, None otherwise
        """
        try:
            if isinstance(strategy, ByName):
                return self._find_element_by_name(strategy.value)
            elif isinstance(strategy, ByRole):
                return self._find_element_by_role(strategy.value)
            elif isinstance(strategy, ByDescription):
                return self._find_element_by_description(strategy.value)
            elif isinstance(strategy, ByPath):
                return self._find_element_by_path(strategy.value)
            elif isinstance(strategy, ByState):
                return self._find_element_by_state(strategy.value)
            else:
                if self.logger:
                    self.logger.error(f"Unsupported locator strategy: {type(strategy).__name__}")
                return None
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding element with strategy {type(strategy).__name__}: {str(e)}")
            return None

    def _find_elements_impl(self, strategy: LocatorStrategy) -> List[Any]:
        """
        Find multiple elements using the specified strategy.
        
        Args:
            strategy: LocatorStrategy instance defining the search method
            
        Returns:
            List of AT-SPI2 elements
        """
        try:
            if isinstance(strategy, ByName):
                return self._find_elements_by_name(strategy.value)
            elif isinstance(strategy, ByRole):
                return self._find_elements_by_role(strategy.value)
            elif isinstance(strategy, ByDescription):
                return self._find_elements_by_description(strategy.value)
            elif isinstance(strategy, ByPath):
                return self._find_elements_by_path(strategy.value)
            elif isinstance(strategy, ByState):
                return self._find_elements_by_state(strategy.value)
            else:
                if self.logger:
                    self.logger.error(f"Unsupported locator strategy: {type(strategy).__name__}")
                return []
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements with strategy {type(strategy).__name__}: {str(e)}")
            return []

    def _find_element_by_name(self, name: str) -> Optional[Any]:
        """Find element by name using AT-SPI2"""
        try:
            # Use backend's recursive search method
            return self.backend._find_element_recursive(self.backend.root, "name", name)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding element by name: {str(e)}")
            return None

    def _find_elements_by_name(self, name: str) -> List[Any]:
        """Find elements by name using AT-SPI2"""
        try:
            results: List[Any] = []
            self.backend._find_elements_recursive(self.backend.root, "name", name, results)
            return results
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements by name: {str(e)}")
            return []

    def _find_element_by_role(self, role: str) -> Optional[Any]:
        """Find element by role using AT-SPI2"""
        try:
            return self.backend._find_element_recursive(self.backend.root, "role", role)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding element by role: {str(e)}")
            return None

    def _find_elements_by_role(self, role: str) -> List[Any]:
        """Find elements by role using AT-SPI2"""
        try:
            results: List[Any] = []
            self.backend._find_elements_recursive(self.backend.root, "role", role, results)
            return results
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements by role: {str(e)}")
            return []

    def _find_element_by_description(self, description: str) -> Optional[Any]:
        """Find element by description using AT-SPI2"""
        try:
            return self.backend._find_element_recursive(self.backend.root, "description", description)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding element by description: {str(e)}")
            return None

    def _find_elements_by_description(self, description: str) -> List[Any]:
        """Find elements by description using AT-SPI2"""
        try:
            results: List[Any] = []
            self.backend._find_elements_recursive(self.backend.root, "description", description, results)
            return results
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements by description: {str(e)}")
            return []

    def _find_element_by_path(self, path: str) -> Optional[Any]:
        """Find element by path using AT-SPI2"""
        try:
            # Parse path like "0:1:2" to navigate through children
            path_parts = path.split(":")
            current_element = self.backend.root
            
            for part in path_parts:
                try:
                    index = int(part)
                    children: List[Any] = []
                    if hasattr(current_element, 'getChildren'):
                        get_children_method = getattr(current_element, 'getChildren')
                        if callable(get_children_method):
                            children_result = get_children_method()
                            if isinstance(children_result, (list, tuple)):
                                children = list(children_result)
                    if 0 <= index < len(children):
                        current_element = children[index]
                    else:
                        if self.logger:
                            self.logger.error(f"Invalid path index: {index}")
                        return None
                except (ValueError, IndexError) as e:
                    if self.logger:
                        self.logger.error(f"Error parsing path {path}: {str(e)}")
                    return None
            
            return current_element
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding element by path: {str(e)}")
            return None

    def _find_elements_by_path(self, path: str) -> List[Any]:
        """Find elements by path using AT-SPI2"""
        try:
            element = self._find_element_by_path(path)
            return [element] if element else []
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements by path: {str(e)}")
            return []

    def _find_element_by_state(self, state: str) -> Optional[Any]:
        """Find element by state using AT-SPI2"""
        try:
            return self.backend._find_element_recursive(self.backend.root, "state", state)
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding element by state: {str(e)}")
            return None

    def _find_elements_by_state(self, state: str) -> List[Any]:
        """Find elements by state using AT-SPI2"""
        try:
            results: List[Any] = []
            self.backend._find_elements_recursive(self.backend.root, "state", state, results)
            return results
        except Exception as e:
            if self.logger:
                self.logger.error(f"Error finding elements by state: {str(e)}")
            return [] 