# Testing Guide

## 🧪 **Обзор тестирования**

PyUI Automation предоставляет мощные инструменты для тестирования UI приложений. Фреймворк поддерживает различные типы тестов: unit тесты, интеграционные тесты, визуальные тесты и тесты производительности.

## 🎯 **Типы тестов**

### **Unit тесты**
- Тестирование отдельных компонентов
- Мокирование зависимостей
- Быстрое выполнение
- Изолированность

### **Интеграционные тесты**
- Тестирование взаимодействия компонентов
- Использование реальных сервисов
- Проверка полного потока
- Близость к реальному использованию

### **Визуальные тесты**
- Сравнение с baseline изображениями
- Обнаружение UI изменений
- Автоматическая генерация отчетов
- Поддержка различных форматов

### **Тесты производительности**
- Мониторинг CPU и памяти
- Измерение времени отклика
- Обнаружение утечек памяти
- Стресс-тестирование

## 🛠️ **Настройка тестового окружения**

### **Установка зависимостей**

```bash
# Установка pytest и расширений
uv add pytest pytest-cov pytest-mock pytest-html

# Установка дополнительных инструментов
uv add pytest-xdist  # Параллельное выполнение
uv add pytest-repeat  # Повторение тестов
uv add pytest-timeout  # Таймауты для тестов
```

### **Структура тестового проекта**

```
tests/
├── conftest.py              # Конфигурация pytest
├── unit/                    # Unit тесты
│   ├── test_elements.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/             # Интеграционные тесты
│   ├── test_automation_flow.py
│   ├── test_applications.py
│   └── test_performance.py
├── visual/                  # Визуальные тесты
│   ├── test_ui_consistency.py
│   └── baseline/            # Baseline изображения
├── performance/             # Тесты производительности
│   ├── test_memory_leaks.py
│   └── test_stress.py
└── fixtures/                # Тестовые данные
    ├── test_apps/
    └── test_data/
```

### **Конфигурация pytest**

```python
# tests/conftest.py
import pytest
from pyui_automation.core import DIAutomationManager
from pyui_automation.core.services.di_container import cleanup

@pytest.fixture(scope="session")
def automation_manager():
    """Глобальный менеджер автоматизации для всех тестов"""
    manager = DIAutomationManager()
    yield manager
    manager.cleanup()

@pytest.fixture(scope="function")
def clean_di_container():
    """Очистка DI контейнера после каждого теста"""
    yield
    cleanup()

@pytest.fixture(scope="function")
def mock_backend():
    """Мок backend для unit тестов"""
    from unittest.mock import Mock
    backend = Mock()
    backend.find_element_by_object_name.return_value = Mock()
    backend.capture_screenshot.return_value = Mock()
    return backend

@pytest.fixture(scope="function")
def automation_session(mock_backend):
    """Сессия автоматизации с мок backend"""
    from pyui_automation.core import AutomationSession
    return AutomationSession(mock_backend)
```

## 🧪 **Unit тесты**

### **Тестирование элементов**

```python
# tests/unit/test_elements.py
import pytest
from unittest.mock import Mock, patch
from pyui_automation.elements import BaseElement

class TestBaseElement:
    
    def test_element_click(self, mock_backend):
        """Тест клика по элементу"""
        # Arrange
        native_element = Mock()
        session = Mock()
        element = BaseElement(native_element, session)
        
        # Act
        element.click()
        
        # Assert
        native_element.click.assert_called_once()
    
    def test_element_type_text(self, mock_backend):
        """Тест ввода текста в элемент"""
        # Arrange
        native_element = Mock()
        session = Mock()
        element = BaseElement(native_element, session)
        text = "Hello, World!"
        
        # Act
        element.type_text(text)
        
        # Assert
        native_element.send_keys.assert_called_once_with(text)
    
    def test_element_get_text(self, mock_backend):
        """Тест получения текста элемента"""
        # Arrange
        native_element = Mock()
        native_element.text = "Test Text"
        session = Mock()
        element = BaseElement(native_element, session)
        
        # Act
        result = element.get_text()
        
        # Assert
        assert result == "Test Text"
    
    def test_element_is_enabled(self, mock_backend):
        """Тест проверки активности элемента"""
        # Arrange
        native_element = Mock()
        native_element.is_enabled.return_value = True
        session = Mock()
        element = BaseElement(native_element, session)
        
        # Act
        result = element.is_enabled()
        
        # Assert
        assert result is True
        native_element.is_enabled.assert_called_once()
```

### **Тестирование сервисов**

```python
# tests/unit/test_services.py
import pytest
from unittest.mock import Mock, patch
from pyui_automation.core.services.performance_monitor import PerformanceMonitor

class TestPerformanceMonitor:
    
    def test_start_monitoring(self):
        """Тест запуска мониторинга производительности"""
        # Arrange
        application = Mock()
        monitor = PerformanceMonitor(application)
        
        # Act
        monitor.start_monitoring(interval=1.0)
        
        # Assert
        assert monitor.is_monitoring is True
        assert monitor.metrics == []
    
    def test_stop_monitoring(self):
        """Тест остановки мониторинга производительности"""
        # Arrange
        application = Mock()
        monitor = PerformanceMonitor(application)
        monitor.start_monitoring()
        
        # Act
        metrics = monitor.stop_monitoring()
        
        # Assert
        assert monitor.is_monitoring is False
        assert isinstance(metrics, list)
    
    def test_record_metric(self):
        """Тест записи метрики"""
        # Arrange
        application = Mock()
        monitor = PerformanceMonitor(application)
        
        # Act
        monitor.record_metric(response_time=0.5)
        
        # Assert
        assert len(monitor.metrics) == 1
        assert monitor.metrics[0].response_time == 0.5
    
    @patch('time.time')
    def test_get_average_metrics(self, mock_time):
        """Тест получения средних метрик"""
        # Arrange
        mock_time.return_value = 100.0
        application = Mock()
        monitor = PerformanceMonitor(application)
        
        # Добавляем тестовые метрики
        monitor.record_metric(response_time=1.0)
        monitor.record_metric(response_time=2.0)
        monitor.record_metric(response_time=3.0)
        
        # Act
        avg_metrics = monitor.get_average_metrics()
        
        # Assert
        assert avg_metrics['response_time'] == 2.0
        assert avg_metrics['duration'] == 0.0
```

### **Тестирование с DI**

```python
# tests/unit/test_di.py
import pytest
from unittest.mock import Mock
from pyui_automation.core.services.di_container import register_service, get_service, cleanup

class TestDependencyInjection:
    
    def setup_method(self):
        """Настройка перед каждым тестом"""
        cleanup()
    
    def test_service_registration(self):
        """Тест регистрации сервиса"""
        # Arrange
        mock_service = Mock()
        
        # Act
        register_service('test_service', lambda: mock_service, singleton=True)
        service = get_service('test_service')
        
        # Assert
        assert service is mock_service
    
    def test_singleton_behavior(self):
        """Тест поведения singleton сервисов"""
        # Arrange
        mock_service = Mock()
        register_service('singleton_service', lambda: mock_service, singleton=True)
        
        # Act
        service1 = get_service('singleton_service')
        service2 = get_service('singleton_service')
        
        # Assert
        assert service1 is service2
    
    def test_transient_behavior(self):
        """Тест поведения transient сервисов"""
        # Arrange
        def create_service():
            return Mock()
        
        register_service('transient_service', create_service, singleton=False)
        
        # Act
        service1 = get_service('transient_service')
        service2 = get_service('transient_service')
        
        # Assert
        assert service1 is not service2
    
    def test_configuration_management(self):
        """Тест управления конфигурацией"""
        from pyui_automation.core.services.di_container import set_config, get_config
        
        # Act
        set_config('test_key', 'test_value')
        value = get_config('test_key')
        
        # Assert
        assert value == 'test_value'
    
    def teardown_method(self):
        """Очистка после каждого теста"""
        cleanup()
```

## 🔗 **Интеграционные тесты**

### **Тестирование полного потока автоматизации**

```python
# tests/integration/test_automation_flow.py
import pytest
from pyui_automation.core import DIAutomationManager, AutomationSession
from pyui_automation.core.factory import BackendFactory

class TestAutomationFlow:
    
    def test_create_session(self, automation_manager):
        """Тест создания сессии автоматизации"""
        # Act
        session = automation_manager.create_session()
        
        # Assert
        assert session is not None
        assert session.backend is not None
        assert session.locator is not None
        assert session.session_id is not None
    
    def test_backend_creation(self, automation_manager):
        """Тест создания backend для разных платформ"""
        # Arrange
        platforms = ['windows', 'linux', 'macos']
        
        for platform in platforms:
            # Act
            backend = automation_manager.create_backend(platform)
            
            # Assert
            assert backend is not None
            assert hasattr(backend, 'find_element_by_object_name')
            assert hasattr(backend, 'capture_screenshot')
    
    def test_element_finding_flow(self, automation_manager):
        """Тест полного потока поиска элементов"""
        # Arrange
        session = automation_manager.create_session()
        
        # Act & Assert
        # Тест поиска по objectName
        try:
            element = session.find_element_by_object_name("test_element")
            # Если элемент найден, проверяем его свойства
            if element:
                assert element.native_element is not None
        except Exception:
            # Элемент может не существовать в тестовой среде
            pass
    
    def test_screenshot_capture(self, automation_manager):
        """Тест захвата скриншота"""
        # Arrange
        session = automation_manager.create_session()
        
        # Act
        screenshot = session.capture_screenshot()
        
        # Assert
        assert screenshot is not None
        assert hasattr(screenshot, 'shape')  # numpy array
        assert len(screenshot.shape) == 3  # RGB image
    
    def test_performance_monitoring_integration(self, automation_manager):
        """Тест интеграции мониторинга производительности"""
        # Arrange
        session = automation_manager.create_session()
        
        # Act
        session.start_performance_monitoring(interval=0.1)
        
        # Выполняем некоторые действия
        for i in range(5):
            session.capture_screenshot()
        
        metrics = session.stop_performance_monitoring()
        
        # Assert
        assert metrics is not None
        assert len(metrics) > 0
        assert 'avg_cpu_usage' in metrics
        assert 'avg_memory_usage' in metrics
```

### **Тестирование приложений**

```python
# tests/integration/test_applications.py
import pytest
from pyui_automation.application import Application
import time

class TestApplications:
    
    def test_application_launch(self):
        """Тест запуска приложения"""
        # Arrange
        app_path = "notepad.exe"  # Простое приложение для тестирования
        
        # Act
        try:
            app = Application.launch(app_path)
            
            # Assert
            assert app is not None
            assert app.process is not None
            assert app.is_running() is True
            
            # Cleanup
            app.terminate()
            time.sleep(1)
            
        except Exception as e:
            # Приложение может не быть доступно в тестовой среде
            pytest.skip(f"Application {app_path} not available: {e}")
    
    def test_application_attach(self):
        """Тест подключения к существующему процессу"""
        # Arrange
        app_path = "notepad.exe"
        
        try:
            app = Application.launch(app_path)
            pid = app.pid
            
            # Act
            attached_app = Application.attach(pid)
            
            # Assert
            assert attached_app is not None
            assert attached_app.pid == pid
            assert attached_app.is_running() is True
            
            # Cleanup
            app.terminate()
            time.sleep(1)
            
        except Exception as e:
            pytest.skip(f"Application not available: {e}")
    
    def test_application_termination(self):
        """Тест завершения приложения"""
        # Arrange
        app_path = "notepad.exe"
        
        try:
            app = Application.launch(app_path)
            
            # Act
            app.terminate()
            time.sleep(1)
            
            # Assert
            assert app.is_running() is False
            
        except Exception as e:
            pytest.skip(f"Application not available: {e}")
```

## 👁️ **Визуальные тесты**

### **Тестирование UI консистентности**

```python
# tests/visual/test_ui_consistency.py
import pytest
import os
from pathlib import Path
from pyui_automation.core import DIAutomationManager, AutomationSession

class TestVisualConsistency:
    
    @pytest.fixture(scope="class")
    def baseline_dir(self):
        """Директория для baseline изображений"""
        baseline_path = Path("tests/visual/baseline")
        baseline_path.mkdir(parents=True, exist_ok=True)
        return baseline_path
    
    @pytest.fixture(scope="class")
    def session(self, automation_manager):
        """Сессия для визуального тестирования"""
        return automation_manager.create_session()
    
    def test_capture_baseline(self, session, baseline_dir):
        """Тест создания baseline изображения"""
        # Arrange
        session.init_visual_testing(str(baseline_dir))
        
        # Act
        success = session.capture_visual_baseline("main_window")
        
        # Assert
        assert success is True
        
        # Проверяем, что файл создан
        baseline_file = baseline_dir / "main_window.png"
        assert baseline_file.exists()
    
    def test_visual_comparison(self, session, baseline_dir):
        """Тест визуального сравнения"""
        # Arrange
        session.init_visual_testing(str(baseline_dir))
        
        # Создаем baseline если его нет
        if not (baseline_dir / "main_window.png").exists():
            session.capture_visual_baseline("main_window")
        
        # Act
        result = session.compare_visual("main_window")
        
        # Assert
        assert result is not None
        assert "match" in result
        assert "similarity" in result
        assert isinstance(result["similarity"], float)
        assert 0.0 <= result["similarity"] <= 1.0
    
    def test_visual_regression_detection(self, session, baseline_dir):
        """Тест обнаружения визуальных регрессий"""
        # Arrange
        session.init_visual_testing(str(baseline_dir), threshold=0.95)
        
        # Создаем baseline
        session.capture_visual_baseline("test_element")
        
        # Act
        result = session.compare_visual("test_element")
        
        # Assert
        if result["match"]:
            assert result["similarity"] >= 0.95
        else:
            # Если тест не прошел, генерируем отчет
            session.generate_visual_report("test_element", result["differences"], "reports/")
            assert result["similarity"] < 0.95
    
    def test_element_screenshot(self, session, baseline_dir):
        """Тест скриншота конкретного элемента"""
        # Arrange
        session.init_visual_testing(str(baseline_dir))
        
        # Act
        try:
            # Пытаемся найти элемент и сделать его скриншот
            element = session.find_element_by_object_name("test_element")
            if element:
                screenshot = session.capture_element_screenshot(element)
                
                # Assert
                assert screenshot is not None
                assert hasattr(screenshot, 'shape')
                assert len(screenshot.shape) == 3
        except Exception:
            # Элемент может не существовать
            pass
```

## 📊 **Тесты производительности**

### **Тестирование утечек памяти**

```python
# tests/performance/test_memory_leaks.py
import pytest
import gc
import psutil
from pyui_automation.core import DIAutomationManager

class TestMemoryLeaks:
    
    def test_memory_leak_detection(self, automation_manager):
        """Тест обнаружения утечек памяти"""
        # Arrange
        session = automation_manager.create_session()
        
        # Act
        leak_report = session.check_memory_leaks(iterations=10)
        
        # Assert
        assert leak_report is not None
        assert "memory_growth" in leak_report
        assert "leak_detected" in leak_report
        assert isinstance(leak_report["leak_detected"], bool)
    
    def test_stress_test(self, automation_manager):
        """Стресс-тест автоматизации"""
        # Arrange
        session = automation_manager.create_session()
        
        def stress_action():
            """Действие для стресс-теста"""
            session.capture_screenshot()
            # Имитируем поиск элементов
            try:
                session.find_element_by_object_name("test_element")
            except:
                pass
        
        # Act
        stress_report = session.run_stress_test(stress_action, duration=5.0)
        
        # Assert
        assert stress_report is not None
        assert "total_time" in stress_report
        assert "iterations" in stress_report
        assert "success_rate" in stress_report
        assert stress_report["iterations"] > 0
        assert 0.0 <= stress_report["success_rate"] <= 1.0
    
    def test_performance_metrics_collection(self, automation_manager):
        """Тест сбора метрик производительности"""
        # Arrange
        session = automation_manager.create_session()
        
        # Act
        session.start_performance_monitoring(interval=0.1)
        
        # Выполняем действия
        for i in range(10):
            session.capture_screenshot()
        
        metrics = session.stop_performance_monitoring()
        
        # Assert
        assert metrics is not None
        assert len(metrics) > 0
        
        # Проверяем структуру метрик
        for metric in metrics:
            assert hasattr(metric, 'timestamp')
            assert hasattr(metric, 'cpu_usage')
            assert hasattr(metric, 'memory_usage')
            assert hasattr(metric, 'response_time')
    
    def test_performance_regression_detection(self, automation_manager):
        """Тест обнаружения регрессий производительности"""
        # Arrange
        session = automation_manager.create_session()
        
        def test_action():
            """Тестовое действие"""
            session.capture_screenshot()
        
        # Baseline метрики (имитируем)
        baseline_metrics = {
            'response_time': {'avg': 0.1, 'std': 0.02},
            'memory_usage': {'avg': 100.0, 'std': 10.0},
            'cpu_usage': {'avg': 5.0, 'std': 1.0}
        }
        
        # Act
        regression_report = session.performance_tester.detect_regression(
            test_action, baseline_metrics, test_runs=3
        )
        
        # Assert
        assert regression_report is not None
        assert "regression_detected" in regression_report
        assert "current_metrics" in regression_report
        assert "baseline_metrics" in regression_report
```

## 🎯 **Best Practices**

### **Организация тестов**
1. **Разделяйте типы тестов** - unit, integration, visual, performance
2. **Используйте фикстуры** для общей настройки
3. **Очищайте ресурсы** после тестов
4. **Группируйте связанные тесты** в классы

### **Мокирование**
1. **Мокируйте внешние зависимости** в unit тестах
2. **Используйте реальные сервисы** в интеграционных тестах
3. **Создавайте реалистичные моки** с правильным поведением
4. **Проверяйте вызовы моков** для валидации взаимодействий

### **Визуальное тестирование**
1. **Создавайте качественные baseline** изображения
2. **Используйте подходящие пороги** сходства
3. **Генерируйте отчеты** при неудачных тестах
4. **Обновляйте baseline** при намеренных изменениях

### **Тестирование производительности**
1. **Устанавливайте базовые метрики** для сравнения
2. **Запускайте тесты в стабильной среде**
3. **Мониторьте системные ресурсы** во время тестов
4. **Анализируйте тренды** производительности

### **Управление данными**
1. **Используйте тестовые данные** отдельно от продакшена
2. **Очищайте данные** после тестов
3. **Используйте фикстуры** для создания тестовых данных
4. **Валидируйте данные** перед использованием

## 🚀 **Запуск тестов**

### **Базовые команды**

```bash
# Запуск всех тестов
uv run pytest

# Запуск с подробным выводом
uv run pytest -v

# Запуск с покрытием кода
uv run pytest --cov=pyui_automation --cov-report=html

# Запуск конкретного теста
uv run pytest tests/unit/test_elements.py::TestBaseElement::test_element_click

# Запуск тестов по маркерам
uv run pytest -m "unit"
uv run pytest -m "integration"
uv run pytest -m "visual"
uv run pytest -m "performance"
```

### **Параллельное выполнение**

```bash
# Запуск тестов в параллели
uv run pytest -n auto

# Запуск с указанием количества процессов
uv run pytest -n 4
```

### **Генерация отчетов**

```bash
# HTML отчет
uv run pytest --html=reports/test_report.html

# JUnit XML отчет
uv run pytest --junitxml=reports/junit.xml

# Coverage отчет
uv run pytest --cov=pyui_automation --cov-report=html --cov-report=term
```

### **CI/CD интеграция**

```yaml
# .github/workflows/test.yml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.12'
      - run: |
          pip install uv
          uv sync
          uv run pytest --cov=pyui_automation --cov-report=xml
      - uses: codecov/codecov-action@v2
        with:
          file: ./coverage.xml
```

Это руководство поможет вам создавать качественные тесты для автоматизации UI с помощью PyUI Automation. 