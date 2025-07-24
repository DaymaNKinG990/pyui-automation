"""
Dependency Injection Container - manages dependencies and their lifecycle.

Responsible for:
- Service registration
- Dependency resolution
- Lifecycle management
- Configuration injection
"""

from typing import Dict, Any, Type, Optional, Callable, Union
from logging import getLogger


class DIContainer:
    """Simple dependency injection container"""
    
    def __init__(self):
        self._logger = getLogger(__name__)
        self._services: Dict[str, Any] = {}
        self._factories: Dict[str, Callable] = {}
        self._singletons: Dict[str, Any] = {}
        self._config: Dict[str, Any] = {}
    
    def register(self, service_name: str, service_class: Type, singleton: bool = True) -> None:
        """Register a service class"""
        try:
            self._services[service_name] = service_class
            if singleton:
                self._singletons[service_name] = None
            self._logger.debug(f"Registered service: {service_name} ({service_class.__name__})")
        except Exception as e:
            self._logger.error(f"Failed to register service {service_name}: {e}")
            raise
    
    def register_factory(self, service_name: str, factory_func: Callable) -> None:
        """Register a factory function for service creation"""
        try:
            self._factories[service_name] = factory_func
            self._logger.debug(f"Registered factory: {service_name}")
        except Exception as e:
            self._logger.error(f"Failed to register factory {service_name}: {e}")
            raise
    
    def register_instance(self, service_name: str, instance: Any) -> None:
        """Register an existing instance"""
        try:
            self._services[service_name] = instance
            self._singletons[service_name] = instance
            self._logger.debug(f"Registered instance: {service_name}")
        except Exception as e:
            self._logger.error(f"Failed to register instance {service_name}: {e}")
            raise
    
    def get(self, service_name: str) -> Any:
        """Get service instance"""
        try:
            # Check if singleton instance exists
            if service_name in self._singletons and self._singletons[service_name] is not None:
                return self._singletons[service_name]
            
            # Check if factory exists
            if service_name in self._factories:
                instance = self._factories[service_name](self)
                if service_name in self._singletons:
                    self._singletons[service_name] = instance
                return instance
            
            # Check if service class exists
            if service_name in self._services:
                service_class = self._services[service_name]
                if isinstance(service_class, type):
                    # Create new instance
                    instance = service_class()
                    if service_name in self._singletons:
                        self._singletons[service_name] = instance
                    return instance
                else:
                    # Return existing instance
                    return service_class
            
            raise KeyError(f"Service not found: {service_name}")
            
        except Exception as e:
            self._logger.error(f"Failed to get service {service_name}: {e}")
            raise
    
    def has(self, service_name: str) -> bool:
        """Check if service is registered"""
        return service_name in self._services or service_name in self._factories
    
    def unregister(self, service_name: str) -> bool:
        """Unregister a service"""
        try:
            removed = False
            if service_name in self._services:
                del self._services[service_name]
                removed = True
            
            if service_name in self._factories:
                del self._factories[service_name]
                removed = True
            
            if service_name in self._singletons:
                del self._singletons[service_name]
                removed = True
            
            if removed:
                self._logger.debug(f"Unregistered service: {service_name}")
            
            return removed
        except Exception as e:
            self._logger.error(f"Failed to unregister service {service_name}: {e}")
            return False
    
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        try:
            self._config[key] = value
            self._logger.debug(f"Set config: {key} = {value}")
        except Exception as e:
            self._logger.error(f"Failed to set config {key}: {e}")
            raise
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self._config.get(key, default)
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration"""
        return self._config.copy()
    
    def update_config(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration with dictionary"""
        try:
            self._config.update(config_dict)
            self._logger.info(f"Updated config with {len(config_dict)} values")
        except Exception as e:
            self._logger.error(f"Failed to update config: {e}")
            raise
    
    def get_registered_services(self) -> list[str]:
        """Get list of registered service names"""
        services = set(self._services.keys()) | set(self._factories.keys())
        return list(services)
    
    def get_singleton_services(self) -> list[str]:
        """Get list of singleton service names"""
        return list(self._singletons.keys())
    
    def clear(self) -> None:
        """Clear all services and configuration"""
        try:
            self._services.clear()
            self._factories.clear()
            self._singletons.clear()
            self._config.clear()
            self._logger.info("DI container cleared")
        except Exception as e:
            self._logger.error(f"Failed to clear DI container: {e}")
    
    def cleanup(self) -> None:
        """Cleanup all services"""
        try:
            for service_name in self._singletons:
                instance = self._singletons[service_name]
                if instance and hasattr(instance, 'cleanup'):
                    try:
                        instance.cleanup()
                        self._logger.debug(f"Cleaned up service: {service_name}")
                    except Exception as e:
                        self._logger.warning(f"Failed to cleanup service {service_name}: {e}")
            
            self._logger.info("DI container cleanup completed")
        except Exception as e:
            self._logger.error(f"Error during DI container cleanup: {e}")


# Global DI container instance
_container = None


def get_container() -> DIContainer:
    """Get global DI container instance"""
    global _container
    if _container is None:
        _container = DIContainer()
    return _container


def register_service(service_name: str, service_class: Type, singleton: bool = True) -> None:
    """Register a service in global container"""
    get_container().register(service_name, service_class, singleton)


def register_factory(service_name: str, factory_func: Callable) -> None:
    """Register a factory in global container"""
    get_container().register_factory(service_name, factory_func)


def register_instance(service_name: str, instance: Any) -> None:
    """Register an instance in global container"""
    get_container().register_instance(service_name, instance)


def get_service(service_name: str) -> Any:
    """Get service from global container"""
    return get_container().get(service_name)


def has_service(service_name: str) -> bool:
    """Check if service exists in global container"""
    return get_container().has(service_name)


def set_config(key: str, value: Any) -> None:
    """Set configuration in global container"""
    get_container().set_config(key, value)


def get_config(key: str, default: Any = None) -> Any:
    """Get configuration from global container"""
    return get_container().get_config(key, default)


def cleanup() -> None:
    """Cleanup global container"""
    if _container:
        _container.cleanup() 