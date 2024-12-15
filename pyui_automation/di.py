from typing import Dict, Any, Type, Optional, TypeVar

T = TypeVar('T')


class Container:
    """Dependency injection container"""
    
    def __init__(self) -> None:
        """
        Initialize dependency injection container.
        
        :var _services: Mapping of service interface names to implementations
        :var _factories: Mapping of service interface names to factories
        :var _singletons: Mapping of service interface names to singleton instances
        """
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Any] = {}
        self._singletons: Dict[str, Any] = {}

    def register(self, interface: Type[T], implementation: Type[T]) -> None:
        """
        Register a transient service.

        Args:
            interface (Type[T]): The interface type to register.
            implementation (Type[T]): The implementation type to associate with the interface.
        """
        self._services[interface.__name__] = implementation

    def register_singleton(self, interface: Type[T], implementation: Type[T]) -> None:
        """
        Register a singleton service.

        Args:
            interface (Type[T]): The interface type to register.
            implementation (Type[T]): The implementation type to associate with the interface.
        """
        self._services[interface.__name__] = implementation
        self._singletons[interface.__name__] = None

    def register_factory(self, interface: Type[T], factory: Any) -> None:
        """
        Register factory.

        Args:
            interface (Type[T]): The interface type to register.
            factory (Any): The factory function to associate with the interface.
        """
        self._factories[interface.__name__] = factory

    def resolve(self, interface: Type[T]) -> Optional[T]:
        """
        Resolve service.

        Args:
            interface: The type of the service to resolve.

        Returns:
            The resolved service instance, or None if no registration was found.
        """
        name = interface.__name__

        # Check if singleton instance exists
        if name in self._singletons:
            if self._singletons[name] is None:
                self._singletons[name] = self._create_instance(name)
            return self._singletons[name]

        # Check if factory exists
        if name in self._factories:
            return self._factories[name]()

        # Create new instance
        return self._create_instance(name)

    def _create_instance(self, name: str) -> Any:
        """
        Create instance of service.

        Args:
            name (str): The name of the service to create.

        Returns:
            Any: The created instance.

        Raises:
            KeyError: If no registration is found for the given name.
        """
        if name not in self._services:
            raise KeyError(f"No registration found for {name}")

        implementation = self._services[name]
        return implementation()

# Global container instance
container = Container()
