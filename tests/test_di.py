import pytest
from typing import Protocol
from pyui_automation.di import Container


class IService(Protocol):
    def do_something(self) -> str:
        ...


class ServiceA:
    def do_something(self) -> str:
        return "Service A"


class ServiceB:
    def do_something(self) -> str:
        return "Service B"


@pytest.fixture
def container():
    return Container()


def test_register_resolve(container):
    """Test registering and resolving service"""
    container.register(IService, ServiceA)
    service = container.resolve(IService)
    assert isinstance(service, ServiceA)
    assert service.do_something() == "Service A"

def test_register_singleton(container):
    """Test singleton registration"""
    container.register_singleton(IService, ServiceA)
    
    service1 = container.resolve(IService)
    service2 = container.resolve(IService)
    
    assert service1 is service2
    assert isinstance(service1, ServiceA)

def test_register_factory(container):
    """Test factory registration"""
    def factory():
        return ServiceB()
    
    container.register_factory(IService, factory)
    service = container.resolve(IService)
    
    assert isinstance(service, ServiceB)
    assert service.do_something() == "Service B"

def test_resolve_unregistered(container):
    """Test resolving unregistered service"""
    with pytest.raises(KeyError):
        container.resolve(IService)

def test_multiple_registrations(container):
    """Test multiple service registrations"""
    container.register(IService, ServiceA)
    container.register(IService, ServiceB)
    
    service = container.resolve(IService)
    assert isinstance(service, ServiceB)
    assert service.do_something() == "Service B"

def test_singleton_vs_transient(container):
    """Test difference between singleton and transient registration"""
    # Singleton
    container.register_singleton(IService, ServiceA)
    singleton1 = container.resolve(IService)
    singleton2 = container.resolve(IService)
    assert singleton1 is singleton2
    
    # Transient
    container = Container()  # Reset container
    container.register(IService, ServiceA)
    transient1 = container.resolve(IService)
    transient2 = container.resolve(IService)
    assert transient1 is not transient2

def test_register_invalid_types(container):
    with pytest.raises(Exception):
        container.register(None, None)
    with pytest.raises(Exception):
        container.register(str, None)
    with pytest.raises(Exception):
        container.register(None, str)

def test_register_singleton_invalid_types(container):
    with pytest.raises(Exception):
        container.register_singleton(None, None)
    with pytest.raises(Exception):
        container.register_singleton(str, None)
    with pytest.raises(Exception):
        container.register_singleton(None, str)

def test_register_factory_invalid_types(container):
    with pytest.raises(Exception):
        container.register_factory(None, None)
    with pytest.raises(Exception):
        container.register_factory(str, None)
    with pytest.raises(Exception):
        container.register_factory(None, lambda: 1)
    with pytest.raises(Exception):
        container.register_factory(str, 123)

def test_resolve_invalid_type(container):
    with pytest.raises(Exception):
        container.resolve(None)
    with pytest.raises(Exception):
        container.resolve(123)

def test_factory_returns_none(container):
    class IFoo: pass
    container.register_factory(IFoo, lambda: None)
    assert container.resolve(IFoo) is None

def test_factory_raises(container):
    class IBar: pass
    def bad_factory():
        raise RuntimeError('fail')
    container.register_factory(IBar, bad_factory)
    with pytest.raises(RuntimeError):
        container.resolve(IBar)

def test_singleton_constructor_error(container):
    class IBad: pass
    class BadImpl:
        def __init__(self):
            raise RuntimeError('fail')
    container.register_singleton(IBad, BadImpl)
    with pytest.raises(RuntimeError):
        container.resolve(IBad)

def test_re_registration_types(container):
    class IFoo: pass
    class ImplA:
        pass
    class ImplB:
        pass
    container.register(IFoo, ImplA)
    container.register_singleton(IFoo, ImplB)
    s1 = container.resolve(IFoo)
    s2 = container.resolve(IFoo)
    assert s1 is s2
    container.register(IFoo, ImplA)
    t1 = container.resolve(IFoo)
    t2 = container.resolve(IFoo)
    assert t1 is not t2
