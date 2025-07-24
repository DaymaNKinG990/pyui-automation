# Dependency Injection Guide

## 🏗️ **Обзор DI архитектуры**

PyUI Automation использует современную архитектуру с Dependency Injection для обеспечения loose coupling, тестируемости и расширяемости. DI контейнер управляет всеми зависимостями и сервисами фреймворка.

## 🎯 **Основные принципы**

### **SOLID принципы**
- **Single Responsibility Principle (SRP)** - каждый сервис имеет одну ответственность
- **Open/Closed Principle (OCP)** - открыт для расширения, закрыт для модификации
- **Liskov Substitution Principle (LSP)** - подтипы могут заменять базовые типы
- **Interface Segregation Principle (ISP)** - клиенты не зависят от неиспользуемых интерфейсов
- **Dependency Inversion Principle (DIP)** - зависимости от абстракций, а не от конкретных классов

### **Преимущества DI**
- **Loose Coupling** - компоненты слабо связаны
- **Testability** - легко мокировать зависимости
- **Extensibility** - простое добавление новых реализаций
- **Maintainability** - централизованное управление зависимостями
- **Reusability** - компоненты можно переиспользовать

## 🏢 **DIAutomationManager**

### **Основной менеджер с DI**

```python
from pyui_automation.core import DIAutomationManager

# Создание менеджера (Singleton)
manager = DIAutomationManager()

# Получение сервисов через DI
backend_factory = manager.backend_factory
locator_factory = manager.locator_factory
session_manager = manager.session_manager
```

### **Структура DI контейнера**

```python
class DIAutomationManager:
    """Главный менеджер с Dependency Injection"""
    
    def __init__(self):
        self._initialize_services()
        self._set_default_config()
    
    def _initialize_services(self):
        """Инициализация всех сервисов в DI контейнере"""
        # Регистрация сервисов
        register_service('backend_factory', BackendFactory, singleton=True)
        register_service('locator_factory', LocatorFactory, singleton=True)
        register_service('session_manager', SessionManager, singleton=True)
        register_service('configuration_manager', ConfigurationManager, singleton=True)
        register_service('element_discovery_service', ElementDiscoveryService, singleton=True)
        register_service('screenshot_service', ScreenshotService, singleton=True)
        register_service('performance_monitor', PerformanceMonitor, singleton=True)
        register_service('performance_analyzer', PerformanceAnalyzer, singleton=True)
        register_service('performance_tester', PerformanceTester, singleton=True)
        register_service('memory_leak_detector', MemoryLeakDetector, singleton=True)
        register_service('visual_testing_service', VisualTestingService, singleton=True)
        register_service('input_service', InputService, singleton=True)
```

## 🔧 **Регистрация сервисов**

### **Регистрация существующих сервисов**

```python
from pyui_automation.core.services.di_container import register_service, get_service

# Регистрация сервиса как singleton
register_service('my_service', MyService, singleton=True)

# Регистрация сервиса как transient (новый экземпляр каждый раз)
register_service('my_service', MyService, singleton=False)

# Получение сервиса
service = get_service('my_service')
```

### **Регистрация кастомных сервисов**

```python
from pyui_automation.core.interfaces import IBackend, IPerformanceService

class MyCustomBackend(IBackend):
    """Кастомная реализация backend"""
    
    def find_element_by_object_name(self, name: str):
        # Кастомная логика поиска
        pass

class MyCustomPerformanceService(IPerformanceService):
    """Кастомная реализация performance сервиса"""
    
    def start_monitoring(self, interval: float = 1.0):
        # Кастомная логика мониторинга
        pass

# Регистрация кастомных сервисов
register_service('custom_backend', MyCustomBackend, singleton=True)
register_service('custom_performance', MyCustomPerformanceService, singleton=True)
```

### **Регистрация с фабрикой**

```python
def create_custom_service(config):
    """Фабрика для создания кастомного сервиса"""
    return MyCustomService(config)

# Регистрация с фабрикой
register_service('custom_service', create_custom_service, singleton=True)
```

## 🎛️ **Управление конфигурацией**

### **Установка конфигурации**

```python
from pyui_automation.core.services.di_container import set_config, get_config

# Установка конфигурации
set_config('timeout', 30.0)
set_config('retry_attempts', 3)
set_config('log_level', 'INFO')
set_config('performance_monitoring', True)

# Получение конфигурации
timeout = get_config('timeout', default=10.0)
log_level = get_config('log_level', default='WARNING')
```

### **Массовая установка конфигурации**

```python
# Установка нескольких параметров
config = {
    'timeout': 30.0,
    'retry_attempts': 3,
    'retry_delay': 1.0,
    'screenshot_format': 'png',
    'log_level': 'INFO',
    'performance_monitoring': True,
    'visual_testing': True,
    'ocr_enabled': True
}

for key, value in config.items():
    set_config(key, value)
```

## 🔄 **Жизненный цикл сервисов**

### **Singleton сервисы**

```python
# Singleton сервисы создаются один раз и переиспользуются
backend_factory = get_service('backend_factory')  # Создается при первом вызове
backend_factory2 = get_service('backend_factory')  # Возвращается тот же экземпляр

assert backend_factory is backend_factory2  # True
```

### **Transient сервисы**

```python
# Transient сервисы создаются каждый раз заново
register_service('transient_service', MyService, singleton=False)

service1 = get_service('transient_service')  # Новый экземпляр
service2 = get_service('transient_service')  # Новый экземпляр

assert service1 is not service2  # True
```

## 🧪 **Тестирование с DI**

### **Мокирование сервисов**

```python
import pytest
from unittest.mock import Mock
from pyui_automation.core.services.di_container import register_service, get_service

class TestAutomation:
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        # Создание моков
        self.mock_backend = Mock()
        self.mock_locator = Mock()
        
        # Регистрация моков
        register_service('backend_factory', lambda: self.mock_backend, singleton=True)
        register_service('locator_factory', lambda: self.mock_locator, singleton=True)
    
    def test_element_finding(self):
        """Тест поиска элементов с моками"""
        # Настройка мока
        self.mock_backend.find_element_by_object_name.return_value = Mock()
        
        # Тестирование
        backend = get_service('backend_factory')
        element = backend.find_element_by_object_name("test_button")
        
        # Проверки
        assert element is not None
        self.mock_backend.find_element_by_object_name.assert_called_once_with("test_button")
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        # Очистка DI контейнера
        from pyui_automation.core.services.di_container import cleanup
        cleanup()
```

### **Интеграционные тесты**

```python
class TestIntegration:
    
    def test_full_automation_flow(self):
        """Интеграционный тест полного потока автоматизации"""
        # Использование реальных сервисов
        manager = DIAutomationManager()
        
        # Создание сессии
        session = manager.create_session()
        
        # Тестирование функциональности
        assert session is not None
        assert session.backend is not None
        assert session.locator is not None
```

## 🔌 **Расширение функциональности**

### **Создание кастомного сервиса**

```python
from abc import ABC, abstractmethod
from typing import Any, Dict

class ICustomService(ABC):
    """Интерфейс для кастомного сервиса"""
    
    @abstractmethod
    def process_data(self, data: Dict[str, Any]) -> bool:
        """Обработка данных"""
        pass

class MyCustomService(ICustomService):
    """Реализация кастомного сервиса"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    def process_data(self, data: Dict[str, Any]) -> bool:
        """Обработка данных"""
        # Кастомная логика обработки
        return True

# Регистрация в DI контейнере
register_service('custom_service', MyCustomService, singleton=True)
```

### **Расширение существующих сервисов**

```python
from pyui_automation.core.services.performance_monitor import PerformanceMonitor

class ExtendedPerformanceMonitor(PerformanceMonitor):
    """Расширенный мониторинг производительности"""
    
    def __init__(self, application):
        super().__init__(application)
        self.custom_metrics = []
    
    def record_custom_metric(self, metric_name: str, value: float):
        """Запись кастомной метрики"""
        self.custom_metrics.append({
            'name': metric_name,
            'value': value,
            'timestamp': time.time()
        })
    
    def get_custom_metrics(self):
        """Получение кастомных метрик"""
        return self.custom_metrics.copy()

# Регистрация расширенного сервиса
register_service('performance_monitor', ExtendedPerformanceMonitor, singleton=True)
```

## 🎛️ **Управление зависимостями**

### **Автоматическое разрешение зависимостей**

```python
class ServiceWithDependencies:
    """Сервис с зависимостями"""
    
    def __init__(self, backend_factory, locator_factory):
        self.backend_factory = backend_factory
        self.locator_factory = locator_factory
    
    def create_session(self):
        """Создание сессии с зависимостями"""
        backend = self.backend_factory.create_backend('windows')
        locator = self.locator_factory.create_locator('windows', backend)
        return AutomationSession(backend, locator)

# DI контейнер автоматически разрешит зависимости
register_service('service_with_deps', ServiceWithDependencies, singleton=True)
service = get_service('service_with_deps')  # Зависимости будут автоматически внедрены
```

### **Ручное разрешение зависимостей**

```python
from pyui_automation.core.services.di_container import resolve_dependencies

def create_service_manually():
    """Ручное создание сервиса с зависимостями"""
    backend_factory = get_service('backend_factory')
    locator_factory = get_service('locator_factory')
    
    return ServiceWithDependencies(backend_factory, locator_factory)

# Регистрация с ручным созданием
register_service('manual_service', create_service_manually, singleton=True)
```

## 🔍 **Отладка DI контейнера**

### **Получение информации о сервисах**

```python
from pyui_automation.core.services.di_container import get_container

# Получение информации о зарегистрированных сервисах
container = get_container()
registered_services = container.get_registered_services()
singleton_services = container.get_singleton_services()
all_config = container.get_all_config()

print(f"Registered services: {registered_services}")
print(f"Singleton services: {singleton_services}")
print(f"Configuration: {all_config}")
```

### **Проверка состояния контейнера**

```python
def check_container_health():
    """Проверка состояния DI контейнера"""
    container = get_container()
    
    # Проверка зарегистрированных сервисов
    services = container.get_registered_services()
    print(f"Total registered services: {len(services)}")
    
    # Проверка синглтонов
    singletons = container.get_singleton_services()
    print(f"Singleton services: {len(singletons)}")
    
    # Проверка конфигурации
    config = container.get_all_config()
    print(f"Configuration items: {len(config)}")
    
    return {
        'services_count': len(services),
        'singletons_count': len(singletons),
        'config_count': len(config)
    }
```

## 🧹 **Очистка ресурсов**

### **Очистка DI контейнера**

```python
from pyui_automation.core.services.di_container import cleanup

# Очистка всех сервисов и конфигурации
cleanup()

# После очистки все сервисы нужно регистрировать заново
```

### **Очистка менеджера**

```python
# Очистка DIAutomationManager
manager = DIAutomationManager()
manager.cleanup()

# Сброс синглтона
DIAutomationManager._instance = None
DIAutomationManager._initialized = False
```

## 🎯 **Best Practices**

### **Регистрация сервисов**
1. **Регистрируйте сервисы как singleton** для состояния и ресурсов
2. **Используйте интерфейсы** для loose coupling
3. **Группируйте связанные сервисы** в модули
4. **Документируйте зависимости** сервисов

### **Управление конфигурацией**
1. **Устанавливайте значения по умолчанию** для всех параметров
2. **Валидируйте конфигурацию** при установке
3. **Используйте типизированные значения** где возможно
4. **Группируйте связанные параметры** в словари

### **Тестирование**
1. **Мокируйте внешние зависимости** в unit тестах
2. **Используйте реальные сервисы** в интеграционных тестах
3. **Очищайте контейнер** после каждого теста
4. **Тестируйте граничные случаи** конфигурации

### **Расширяемость**
1. **Следуйте принципам SOLID** при создании сервисов
2. **Используйте композицию** вместо наследования
3. **Создавайте интерфейсы** для новых сервисов
4. **Документируйте API** новых сервисов

## 📚 **Примеры использования**

### **Полный пример с кастомным сервисом**

```python
from pyui_automation.core import DIAutomationManager
from pyui_automation.core.services.di_container import register_service, get_service, set_config

# Настройка конфигурации
set_config('custom_timeout', 60.0)
set_config('custom_retries', 5)

# Создание кастомного сервиса
class CustomElementFinder:
    def __init__(self, timeout: float, retries: int):
        self.timeout = timeout
        self.retries = retries
    
    def find_element_custom(self, name: str):
        # Кастомная логика поиска
        return f"Found element: {name}"

# Регистрация кастомного сервиса
register_service('custom_finder', CustomElementFinder, singleton=True)

# Создание менеджера
manager = DIAutomationManager()

# Использование кастомного сервиса
finder = get_service('custom_finder')
element = finder.find_element_custom("test_button")

print(element)  # "Found element: test_button"
```

Это руководство поможет вам эффективно использовать Dependency Injection в PyUI Automation для создания тестируемых, расширяемых и поддерживаемых автоматизационных решений. 