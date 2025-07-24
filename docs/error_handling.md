# Error Handling Guide

Этот гайд описывает систему обработки ошибок в PyUI Automation, включая типы исключений, стратегии обработки и best practices.

## Основы обработки ошибок

PyUI Automation использует иерархическую систему исключений для различных типов ошибок:
- **BaseAutomationException** - базовое исключение для всех ошибок автоматизации
- **ElementNotFoundError** - элемент не найден
- **TimeoutError** - превышение времени ожидания
- **PlatformNotSupportedError** - платформа не поддерживается
- **ConfigurationError** - ошибка конфигурации
- **BackendError** - ошибка backend
- **OCRException** - ошибка OCR
- **VisualTestError** - ошибка визуального тестирования

## Типы исключений

### BaseAutomationException
```python
from pyui_automation.core.exceptions import BaseAutomationException

try:
    element = session.find_element(ByName("nonExistentElement"))
except BaseAutomationException as e:
    print(f"Automation error: {e}")
    print(f"Error type: {type(e).__name__}")
    print(f"Error details: {e.details}")
```

### ElementNotFoundError
```python
from pyui_automation.core.exceptions import ElementNotFoundError

try:
    button = session.find_element(ByName("submitButton"))
except ElementNotFoundError as e:
    print(f"Element not found: {e.element_name}")
    print(f"Strategy used: {e.strategy}")
    print(f"Available elements: {e.available_elements}")
    
    # Fallback стратегия
    try:
        button = session.find_element(ByClassName("QPushButton"))
    except ElementNotFoundError:
        print("No buttons found at all")
```

### TimeoutError
```python
from pyui_automation.core.exceptions import TimeoutError

try:
    element = session.wait_for_element(ByName("dynamicElement"), timeout=5.0)
except TimeoutError as e:
    print(f"Timeout waiting for element: {e.element_name}")
    print(f"Timeout duration: {e.timeout}")
    print(f"Last attempt result: {e.last_attempt_result}")
```

### PlatformNotSupportedError
```python
from pyui_automation.core.exceptions import PlatformNotSupportedError

try:
    backend = BackendFactory.create_backend('unsupported_platform')
except PlatformNotSupportedError as e:
    print(f"Platform not supported: {e.platform}")
    print(f"Supported platforms: {e.supported_platforms}")
    
    # Fallback на поддерживаемую платформу
    backend = BackendFactory.create_backend('windows')
```

### ConfigurationError
```python
from pyui_automation.core.exceptions import ConfigurationError

try:
    config = Config.from_file("invalid_config.yaml")
except ConfigurationError as e:
    print(f"Configuration error: {e.message}")
    print(f"Invalid field: {e.field}")
    print(f"Expected value: {e.expected_value}")
    print(f"Actual value: {e.actual_value}")
```

### BackendError
```python
from pyui_automation.core.exceptions import BackendError

try:
    screenshot = session.backend.capture_screenshot()
except BackendError as e:
    print(f"Backend error: {e.message}")
    print(f"Backend type: {e.backend_type}")
    print(f"Operation: {e.operation}")
    
    # Попытка восстановления
    session.backend.reinitialize()
    screenshot = session.backend.capture_screenshot()
```

### OCRException
```python
from pyui_automation.core.exceptions import OCRException

try:
    text = session.ocr.read_text_from_element(element)
except OCRException as e:
    print(f"OCR error: {e.message}")
    print(f"OCR engine: {e.engine}")
    print(f"Confidence: {e.confidence}")
    
    # Fallback на другой OCR engine
    session.ocr.set_engine("tesseract")
    text = session.ocr.read_text_from_element(element)
```

### VisualTestError
```python
from pyui_automation.core.exceptions import VisualTestError

try:
    result = session.compare_visual("main_window")
except VisualTestError as e:
    print(f"Visual test error: {e.message}")
    print(f"Baseline path: {e.baseline_path}")
    print(f"Current image path: {e.current_image_path}")
    
    # Создание нового baseline
    session.capture_visual_baseline("main_window")
```

## Стратегии обработки ошибок

### Retry Pattern
```python
from pyui_automation.core.exceptions import ElementNotFoundError, TimeoutError
import time

def retry_operation(operation, max_retries=3, delay=1.0):
    """Повторение операции с задержкой"""
    for attempt in range(max_retries):
        try:
            return operation()
        except (ElementNotFoundError, TimeoutError) as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Attempt {attempt + 1} failed: {e}")
            time.sleep(delay)
            delay *= 2  # Экспоненциальная задержка

# Использование
def find_element_with_retry():
    return retry_operation(
        lambda: session.find_element(ByName("dynamicElement")),
        max_retries=5,
        delay=0.5
    )
```

### Fallback Strategy
```python
def find_element_with_fallback(element_name):
    """Поиск элемента с fallback стратегиями"""
    strategies = [
        lambda: session.find_element(ByName(element_name)),
        lambda: session.find_element(ByClassName("QPushButton")),
        lambda: session.find_element(ByText("Submit")),
        lambda: session.find_element(ByXPath(f"//*[@text='{element_name}']"))
    ]
    
    for strategy in strategies:
        try:
            return strategy()
        except ElementNotFoundError:
            continue
    
    raise ElementNotFoundError(f"Element '{element_name}' not found with any strategy")
```

### Circuit Breaker Pattern
```python
class CircuitBreaker:
    def __init__(self, failure_threshold=5, recovery_timeout=60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    def call(self, operation):
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
            else:
                raise Exception("Circuit breaker is OPEN")
        
        try:
            result = operation()
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
            return result
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
            
            raise e

# Использование
circuit_breaker = CircuitBreaker()

def safe_operation():
    return circuit_breaker.call(
        lambda: session.find_element(ByName("unstableElement"))
    )
```

### Graceful Degradation
```python
def perform_automation_with_graceful_degradation():
    """Выполнение автоматизации с graceful degradation"""
    results = {}
    
    # Основная функциональность
    try:
        button = session.find_element(ByName("submitButton"))
        button.click()
        results["button_click"] = "success"
    except ElementNotFoundError:
        results["button_click"] = "degraded"
        # Fallback: поиск по координатам
        session.mouse.click(500, 300)
    
    # Визуальное тестирование
    try:
        result = session.compare_visual("main_window")
        results["visual_test"] = "success" if result["match"] else "failed"
    except VisualTestError:
        results["visual_test"] = "skipped"
    
    # OCR
    try:
        text = session.ocr.read_text_from_element(element)
        results["ocr"] = "success"
    except OCRException:
        results["ocr"] = "degraded"
        # Fallback: получение текста через accessibility
        text = element.get_text()
    
    return results
```

## Обработка специфичных ошибок

### Обработка ошибок Windows UI Automation
```python
def handle_windows_automation_errors():
    try:
        element = session.find_element(ByName("windowsElement"))
    except BackendError as e:
        if "access denied" in str(e).lower():
            print("Run as administrator required")
            # Попытка запуска с elevated privileges
            session.backend.request_elevation()
        elif "element not found" in str(e).lower():
            print("Element not accessible via UI Automation")
            # Fallback на accessibility API
            element = session.find_element(ByAccessibilityId("elementId"))
        else:
            raise e
```

### Обработка ошибок OCR
```python
def handle_ocr_errors():
    try:
        text = session.ocr.read_text_from_element(element)
    except OCRException as e:
        if e.confidence < 0.5:
            print("Low OCR confidence, trying preprocessing")
            # Попытка с предобработкой
            text = session.ocr.read_text_from_element(
                element, 
                preprocess=True
            )
        elif "language not supported" in str(e).lower():
            print("Language not supported, switching engine")
            # Переключение на другой OCR engine
            session.ocr.set_engine("tesseract")
            text = session.ocr.read_text_from_element(element)
        else:
            raise e
```

### Обработка ошибок визуального тестирования
```python
def handle_visual_test_errors():
    try:
        result = session.compare_visual("main_window")
    except VisualTestError as e:
        if "baseline not found" in str(e).lower():
            print("Creating new baseline")
            session.capture_visual_baseline("main_window")
        elif "image format not supported" in str(e).lower():
            print("Converting image format")
            # Конвертация изображения
            session.utils.convert_image_format(
                e.current_image_path, 
                "png"
            )
        else:
            raise e
```

## Логирование ошибок

### Структурированное логирование
```python
import logging
from pyui_automation.core.exceptions import BaseAutomationException

# Настройка логгера
logger = logging.getLogger("pyui_automation.errors")
logger.setLevel(logging.ERROR)

def log_automation_error(error: BaseAutomationException, context: dict = None):
    """Структурированное логирование ошибок автоматизации"""
    error_data = {
        "error_type": type(error).__name__,
        "message": str(error),
        "details": getattr(error, 'details', {}),
        "context": context or {},
        "timestamp": time.time()
    }
    
    logger.error(f"Automation error: {error_data}")
    
    # Сохранение в файл для анализа
    with open("automation_errors.log", "a") as f:
        f.write(f"{error_data}\n")

# Использование
try:
    element = session.find_element(ByName("testElement"))
except BaseAutomationException as e:
    log_automation_error(e, {
        "test_name": "test_button_click",
        "step": "find_element",
        "element_name": "testElement"
    })
```

### Обработчик исключений для тестов
```python
import pytest
from pyui_automation.core.exceptions import BaseAutomationException

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Обработчик для создания отчетов об ошибках"""
    outcome = yield
    report = outcome.get_result()
    
    if report.when == "call" and report.failed:
        # Получение информации об ошибке
        if hasattr(call.excinfo, 'value') and isinstance(call.excinfo.value, BaseAutomationException):
            error = call.excinfo.value
            
            # Сохранение скриншота при ошибке
            try:
                session = item.funcargs.get('session')
                if session:
                    screenshot = session.backend.capture_screenshot()
                    screenshot_path = f"error_screenshots/{item.name}_{int(time.time())}.png"
                    session.utils.save_image(screenshot, screenshot_path)
                    report.sections.append(("Screenshot", screenshot_path))
            except Exception as e:
                report.sections.append(("Screenshot Error", str(e)))
            
            # Добавление информации об ошибке в отчет
            report.sections.append(("Error Type", type(error).__name__))
            report.sections.append(("Error Details", str(error)))
```

## Восстановление после ошибок

### Восстановление сессии
```python
def recover_session(session):
    """Восстановление сессии после критических ошибок"""
    try:
        # Проверка состояния backend
        session.backend.validate_state()
    except BackendError:
        print("Backend state invalid, reinitializing...")
        session.backend.reinitialize()
    
    try:
        # Проверка OCR сервиса
        session.ocr.validate_state()
    except OCRException:
        print("OCR service invalid, reinitializing...")
        session.ocr.reinitialize()
    
    try:
        # Проверка визуального тестирования
        session.visual.validate_state()
    except VisualTestError:
        print("Visual testing invalid, reinitializing...")
        session.init_visual_testing("visual_baseline/")
```

### Автоматическое восстановление
```python
class AutoRecoverySession:
    def __init__(self, session):
        self.session = session
        self.recovery_attempts = 0
        self.max_recovery_attempts = 3
    
    def execute_with_recovery(self, operation):
        """Выполнение операции с автоматическим восстановлением"""
        for attempt in range(self.max_recovery_attempts):
            try:
                return operation()
            except (BackendError, OCRException, VisualTestError) as e:
                if attempt < self.max_recovery_attempts - 1:
                    print(f"Recovery attempt {attempt + 1}")
                    recover_session(self.session)
                    time.sleep(1.0)
                else:
                    raise e

# Использование
auto_session = AutoRecoverySession(session)

def safe_automation():
    return auto_session.execute_with_recovery(
        lambda: session.find_element(ByName("criticalElement")).click()
    )
```

## Best Practices

### Общие принципы
- **Fail Fast** - быстрое обнаружение ошибок
- **Graceful Degradation** - постепенная деградация функциональности
- **Retry with Exponential Backoff** - повторные попытки с экспоненциальной задержкой
- **Circuit Breaker** - защита от каскадных сбоев
- **Structured Logging** - структурированное логирование ошибок

### Специфичные для автоматизации
- **Element State Validation** - проверка состояния элементов перед взаимодействием
- **Platform-Specific Error Handling** - обработка ошибок специфичных для платформы
- **OCR Confidence Thresholds** - использование порогов уверенности для OCR
- **Visual Test Fallbacks** - fallback стратегии для визуального тестирования
- **Performance Monitoring** - мониторинг производительности для выявления проблем

### Отладка и диагностика
- **Screenshot on Error** - автоматическое создание скриншотов при ошибках
- **Error Context Collection** - сбор контекста ошибок
- **Error Classification** - классификация ошибок по типам
- **Error Reporting** - создание отчетов об ошибках
- **Error Analytics** - анализ паттернов ошибок

### Производительность
- **Error Caching** - кэширование результатов обработки ошибок
- **Lazy Error Handling** - отложенная обработка некритичных ошибок
- **Error Rate Limiting** - ограничение частоты обработки ошибок
- **Error Prioritization** - приоритизация ошибок по важности 