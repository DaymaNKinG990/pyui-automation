# Examples Guide

Этот гайд содержит практические примеры использования PyUI Automation для различных сценариев автоматизации и тестирования.

## Базовые примеры

### Простой поиск и взаимодействие с элементами
```python
from pyui_automation.core import AutomationSession
from pyui_automation.core.factory import BackendFactory
from pyui_automation.locators import ByName, ByClassName

# Создание сессии
backend = BackendFactory.create_backend('windows')
session = AutomationSession(backend)

# Поиск и клик по кнопке
submit_button = session.find_element(ByName("submitButton"))
submit_button.click()

# Ввод текста в поле
username_field = session.find_element(ByName("username"))
username_field.type_text("testuser")

# Поиск всех кнопок
all_buttons = session.find_elements(ByClassName("QPushButton"))
for button in all_buttons:
    if button.get_text() == "OK":
        button.click()
        break
```

### Работа с формами
```python
def fill_login_form(session, username, password):
    """Заполнение формы входа"""
    # Поиск полей
    username_field = session.find_element(ByName("username"))
    password_field = session.find_element(ByName("password"))
    login_button = session.find_element(ByName("loginButton"))
    
    # Очистка и заполнение
    username_field.clear()
    username_field.type_text(username)
    
    password_field.clear()
    password_field.type_text(password)
    
    # Отправка формы
    login_button.click()

# Использование
fill_login_form(session, "admin", "password123")
```

### Ожидание элементов
```python
from pyui_automation.core.wait import wait_for_element, wait_for_condition

# Ожидание появления элемента
dynamic_element = wait_for_element(
    session, 
    ByName("dynamicElement"), 
    timeout=10.0
)

# Ожидание условия
def element_is_visible():
    try:
        element = session.find_element(ByName("loadingIndicator"))
        return not element.is_visible()
    except:
        return True

wait_for_condition(element_is_visible, timeout=30.0)
```

## Примеры визуального тестирования

### Baseline тестирование
```python
def test_main_window_appearance():
    """Тест внешнего вида главного окна"""
    # Инициализация визуального тестирования
    session.init_visual_testing("visual_baseline/")
    
    # Создание baseline (выполняется один раз)
    session.capture_visual_baseline("main_window")
    
    # Сравнение с baseline
    result = session.compare_visual("main_window")
    
    if result["match"]:
        print("Visual test passed!")
    else:
        print(f"Visual test failed! Similarity: {result['similarity']}")
        # Генерация отчета о различиях
        session.generate_visual_report(
            "main_window",
            result["differences"],
            "reports/visual_differences/"
        )

# Запуск теста
test_main_window_appearance()
```

### Тестирование состояний элементов
```python
def test_button_states():
    """Тест различных состояний кнопки"""
    session.init_visual_testing("button_baseline/")
    
    button = session.find_element(ByName("testButton"))
    
    # Тест нормального состояния
    session.capture_visual_baseline("button_normal", element=button)
    result = session.compare_visual("button_normal", element=button)
    assert result["match"], "Button normal state changed"
    
    # Тест состояния при наведении
    button.hover()
    session.capture_visual_baseline("button_hover", element=button)
    result = session.compare_visual("button_hover", element=button)
    assert result["match"], "Button hover state changed"
    
    # Тест состояния при нажатии
    button.click()
    session.capture_visual_baseline("button_pressed", element=button)
    result = session.compare_visual("button_pressed", element=button)
    assert result["match"], "Button pressed state changed"
```

### Игнорирование динамических областей
```python
def test_dashboard_with_ignored_regions():
    """Тест дашборда с игнорированием динамических областей"""
    session.init_visual_testing("dashboard_baseline/")
    
    # Области для игнорирования (время, счетчики, etc.)
    ignore_regions = [
        {"x": 100, "y": 50, "width": 150, "height": 30},   # Время
        {"x": 800, "y": 100, "width": 100, "height": 25},  # Счетчик
        {"x": 1200, "y": 200, "width": 80, "height": 20}   # Статус
    ]
    
    # Создание baseline
    session.capture_visual_baseline("dashboard")
    
    # Сравнение с игнорированием областей
    result = session.compare_visual("dashboard", ignore_regions=ignore_regions)
    
    if not result["match"]:
        print(f"Dashboard changed! Similarity: {result['similarity']}")
        for diff in result["differences"]:
            print(f"  Difference at {diff['position']}")
```

## Примеры OCR

### Распознавание текста из элементов
```python
def extract_text_from_elements():
    """Извлечение текста из различных элементов"""
    # Распознавание текста из элемента
    status_element = session.find_element(ByName("statusLabel"))
    status_text = session.ocr.read_text_from_element(status_element)
    print(f"Status: {status_text}")
    
    # Распознавание текста из области экрана
    screenshot = session.backend.capture_screenshot()
    text = session.ocr.recognize_text(screenshot)
    print(f"Screen text: {text}")
    
    # Распознавание с предобработкой
    error_element = session.find_element(ByName("errorMessage"))
    error_text = session.ocr.read_text_from_element(
        error_element, 
        preprocess=True
    )
    print(f"Error: {error_text}")

# Использование
extract_text_from_elements()
```

### Многоязычное распознавание
```python
def multilingual_ocr():
    """Многоязычное распознавание текста"""
    # Настройка языков
    session.ocr.set_languages(['en', 'ru', 'es'])
    
    # Распознавание текста на разных языках
    elements = [
        session.find_element(ByName("englishText")),
        session.find_element(ByName("russianText")),
        session.find_element(ByName("spanishText"))
    ]
    
    for element in elements:
        text = session.ocr.read_text_from_element(element)
        confidence = session.ocr.get_last_confidence()
        print(f"Text: {text} (confidence: {confidence:.2f})")

# Использование
multilingual_ocr()
```

### Валидация текста через OCR
```python
def validate_text_content():
    """Валидация содержимого текста через OCR"""
    # Ожидание появления текста
    text_element = wait_for_element(session, ByName("dynamicText"), timeout=10.0)
    
    # Получение текста через OCR
    ocr_text = session.ocr.read_text_from_element(text_element)
    
    # Сравнение с ожидаемым текстом
    expected_text = "Expected content"
    if ocr_text.lower() == expected_text.lower():
        print("Text validation passed")
    else:
        print(f"Text validation failed. Expected: {expected_text}, Got: {ocr_text}")
        
        # Сохранение скриншота для анализа
        screenshot = text_element.capture_screenshot()
        session.utils.save_image(screenshot, "text_validation_failed.png")

# Использование
validate_text_content()
```

## Примеры мониторинга производительности

### Базовый мониторинг
```python
def monitor_performance():
    """Базовый мониторинг производительности"""
    # Запуск мониторинга
    session.start_performance_monitoring(interval=1.0)
    
    # Выполнение операций
    for i in range(10):
        button = session.find_element(ByName(f"button{i}"))
        button.click()
        time.sleep(0.5)
    
    # Получение метрик
    metrics = session.get_performance_metrics()
    
    # Анализ результатов
    print(f"CPU usage: {metrics['cpu_usage']:.2f}%")
    print(f"Memory usage: {metrics['memory_usage']:.2f}%")
    print(f"Response time: {metrics['response_time']:.3f}s")
    
    # Проверка порогов
    if metrics['cpu_usage'] > 80:
        print("Warning: High CPU usage detected")
    
    if metrics['memory_usage'] > 85:
        print("Warning: High memory usage detected")

# Использование
monitor_performance()
```

### Детальный анализ производительности
```python
def detailed_performance_analysis():
    """Детальный анализ производительности"""
    # Запуск мониторинга
    session.start_performance_monitoring(interval=0.5)
    
    # Выполнение критических операций
    operations = [
        lambda: session.find_element(ByName("criticalButton")).click(),
        lambda: session.ocr.read_text_from_element(session.find_element(ByName("text"))),
        lambda: session.compare_visual("main_window"),
        lambda: session.backend.capture_screenshot()
    ]
    
    results = {}
    for i, operation in enumerate(operations):
        start_time = time.time()
        try:
            operation()
            results[f"operation_{i}"] = {
                "status": "success",
                "duration": time.time() - start_time
            }
        except Exception as e:
            results[f"operation_{i}"] = {
                "status": "failed",
                "error": str(e),
                "duration": time.time() - start_time
            }
    
    # Получение детальных метрик
    metrics = session.get_performance_metrics()
    
    # Анализ результатов
    print("Performance Analysis:")
    print(f"  Total operations: {len(operations)}")
    print(f"  Successful: {sum(1 for r in results.values() if r['status'] == 'success')}")
    print(f"  Failed: {sum(1 for r in results.values() if r['status'] == 'failed')}")
    print(f"  Average duration: {sum(r['duration'] for r in results.values()) / len(results):.3f}s")
    print(f"  Peak CPU: {max(metrics['cpu_history']):.2f}%")
    print(f"  Peak memory: {max(metrics['memory_history']):.2f}%")

# Использование
detailed_performance_analysis()
```

### Обнаружение утечек памяти
```python
def detect_memory_leaks():
    """Обнаружение утечек памяти"""
    # Запуск мониторинга с детекцией утечек
    session.start_performance_monitoring(interval=1.0)
    session.performance_monitor.enable_memory_leak_detection()
    
    # Выполнение операций, которые могут вызвать утечки
    for cycle in range(5):
        print(f"Cycle {cycle + 1}")
        
        # Создание и удаление элементов
        for i in range(100):
            element = session.find_element(ByName("testElement"))
            element.click()
        
        # Проверка на утечки
        leak_report = session.performance_monitor.get_memory_leak_report()
        if leak_report['leaks_detected']:
            print(f"Memory leaks detected in cycle {cycle + 1}")
            print(f"  Leak size: {leak_report['leak_size']} bytes")
            print(f"  Leak rate: {leak_report['leak_rate']} bytes/s")
    
    # Финальный отчет
    final_report = session.performance_monitor.get_memory_leak_report()
    if final_report['leaks_detected']:
        print("CRITICAL: Memory leaks detected!")
        print(f"Total leak size: {final_report['total_leak_size']} bytes")
    else:
        print("No memory leaks detected")

# Использование
detect_memory_leaks()
```

## Примеры игровой автоматизации

### Мониторинг здоровья персонажа
```python
def monitor_character_health():
    """Мониторинг здоровья персонажа"""
    from pyui_automation.game_elements import HealthBar
    
    # Создание объекта здоровья
    health_bar = HealthBar(session)
    
    # Мониторинг в цикле
    while True:
        current_health = health_bar.current_value
        max_health = health_bar.max_value
        health_percentage = (current_health / max_health) * 100
        
        print(f"Health: {current_health}/{max_health} ({health_percentage:.1f}%)")
        
        # Проверка критического состояния
        if health_bar.is_low():
            print("WARNING: Low health detected!")
            # Использование зелья здоровья
            health_potion = session.find_element(ByName("healthPotion"))
            health_potion.click()
        
        # Проверка смерти
        if health_bar.is_dead():
            print("Character is dead!")
            break
        
        time.sleep(1.0)

# Использование
monitor_character_health()
```

### Автоматизация боевых действий
```python
def automate_combat():
    """Автоматизация боевых действий"""
    from pyui_automation.game_elements import SkillBar, HealthBar
    
    health_bar = HealthBar(session)
    skill_bar = SkillBar(session)
    
    # Основной боевой цикл
    while not health_bar.is_dead():
        # Проверка здоровья
        if health_bar.is_low():
            # Использование защитных способностей
            if not skill_bar.is_on_cooldown("shield"):
                skill_bar.use_skill("shield")
        
        # Атака
        if not skill_bar.is_on_cooldown("attack"):
            skill_bar.use_skill("attack")
        
        # Проверка наличия врагов
        enemy = session.find_element(ByName("enemy"))
        if not enemy.is_visible():
            print("No enemies found, combat ended")
            break
        
        time.sleep(0.5)

# Использование
automate_combat()
```

### Работа с инвентарем
```python
def manage_inventory():
    """Управление инвентарем"""
    from pyui_automation.game_elements import InventorySlot
    
    inventory = InventorySlot(session)
    
    # Проверка всех слотов
    for row in range(5):
        for col in range(8):
            slot = inventory.get_slot(row, col)
            
            if not slot.is_empty():
                item = slot.get_item()
                print(f"Slot ({row}, {col}): {item.name}")
                
                # Автоматическая сортировка
                if item.type == "consumable":
                    # Перемещение в специальный слот
                    target_slot = inventory.get_slot(0, 0)
                    slot.move_item_to(target_slot)
    
    # Проверка веса
    current_weight = inventory.get_current_weight()
    max_weight = inventory.get_max_weight()
    
    if current_weight > max_weight * 0.9:
        print("WARNING: Inventory almost full!")
        # Автоматическое использование предметов
        for item in inventory.get_consumables():
            if item.can_use():
                item.use()

# Использование
manage_inventory()
```

## Примеры интеграции с тестированием

### Pytest тесты
```python
import pytest
from pyui_automation.core import AutomationSession
from pyui_automation.core.factory import BackendFactory

@pytest.fixture(scope="session")
def automation_session():
    """Фикстура для создания сессии автоматизации"""
    backend = BackendFactory.create_backend('windows')
    session = AutomationSession(backend)
    session.init_visual_testing("tests/visual_baseline/")
    yield session
    session.terminate()

@pytest.fixture
def login_session(automation_session):
    """Фикстура для авторизованной сессии"""
    # Авторизация
    username_field = automation_session.find_element(ByName("username"))
    password_field = automation_session.find_element(ByName("password"))
    login_button = automation_session.find_element(ByName("loginButton"))
    
    username_field.type_text("testuser")
    password_field.type_text("testpass")
    login_button.click()
    
    yield automation_session

def test_main_page_loads(automation_session):
    """Тест загрузки главной страницы"""
    # Проверка наличия основных элементов
    assert automation_session.find_element(ByName("mainContent"))
    assert automation_session.find_element(ByName("navigationMenu"))
    
    # Визуальная проверка
    result = automation_session.compare_visual("main_page")
    assert result["match"], f"Visual test failed: {result['similarity']}"

def test_login_functionality(automation_session):
    """Тест функциональности входа"""
    # Заполнение формы
    username_field = automation_session.find_element(ByName("username"))
    password_field = automation_session.find_element(ByName("password"))
    login_button = automation_session.find_element(ByName("loginButton"))
    
    username_field.type_text("testuser")
    password_field.type_text("testpass")
    login_button.click()
    
    # Проверка успешного входа
    welcome_message = automation_session.find_element(ByName("welcomeMessage"))
    assert "Welcome" in welcome_message.get_text()

def test_performance_under_load(automation_session):
    """Тест производительности под нагрузкой"""
    # Запуск мониторинга
    automation_session.start_performance_monitoring()
    
    # Выполнение операций
    for i in range(50):
        button = automation_session.find_element(ByName(f"testButton{i % 5}"))
        button.click()
    
    # Проверка метрик
    metrics = automation_session.get_performance_metrics()
    assert metrics['cpu_usage'] < 80, "CPU usage too high"
    assert metrics['memory_usage'] < 85, "Memory usage too high"
    assert metrics['response_time'] < 2.0, "Response time too high"
```

### Page Object Model
```python
class LoginPage:
    """Page Object для страницы входа"""
    
    def __init__(self, session):
        self.session = session
    
    @property
    def username_field(self):
        return self.session.find_element(ByName("username"))
    
    @property
    def password_field(self):
        return self.session.find_element(ByName("password"))
    
    @property
    def login_button(self):
        return self.session.find_element(ByName("loginButton"))
    
    @property
    def error_message(self):
        return self.session.find_element(ByName("errorMessage"))
    
    def login(self, username: str, password: str):
        """Выполнение входа"""
        self.username_field.clear()
        self.username_field.type_text(username)
        
        self.password_field.clear()
        self.password_field.type_text(password)
        
        self.login_button.click()
    
    def get_error_text(self) -> str:
        """Получение текста ошибки"""
        return self.session.ocr.read_text_from_element(self.error_message)

class DashboardPage:
    """Page Object для дашборда"""
    
    def __init__(self, session):
        self.session = session
    
    @property
    def welcome_message(self):
        return self.session.find_element(ByName("welcomeMessage"))
    
    @property
    def navigation_menu(self):
        return self.session.find_element(ByName("navigationMenu"))
    
    def navigate_to(self, section: str):
        """Навигация к разделу"""
        menu_item = self.session.find_element(ByName(f"menu_{section}"))
        menu_item.click()
    
    def verify_page_loaded(self):
        """Проверка загрузки страницы"""
        assert self.welcome_message.is_visible()
        assert self.navigation_menu.is_visible()

# Использование в тестах
def test_login_workflow(automation_session):
    """Тест полного workflow входа"""
    login_page = LoginPage(automation_session)
    dashboard_page = DashboardPage(automation_session)
    
    # Выполнение входа
    login_page.login("testuser", "testpass")
    
    # Проверка успешного входа
    dashboard_page.verify_page_loaded()
    
    # Навигация
    dashboard_page.navigate_to("settings")
    
    # Визуальная проверка
    result = automation_session.compare_visual("dashboard")
    assert result["match"]
```

## Примеры CI/CD интеграции

### GitHub Actions workflow
```yaml
name: UI Automation Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: windows-latest
    
    steps:
    - uses: actions/checkout@v3
    
    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install uv
        uv sync
    
    - name: Run UI automation tests
      run: |
        python -m pytest tests/ -v --html=reports/report.html --self-contained-html
    
    - name: Upload test results
      uses: actions/upload-artifact@v3
      if: always()
      with:
        name: test-results
        path: |
          reports/
          error_screenshots/
          visual_baseline/
```

### Локальный CI скрипт
```python
#!/usr/bin/env python3
"""Локальный CI скрипт для запуска тестов"""

import subprocess
import sys
import os
from datetime import datetime

def run_command(command, description):
    """Выполнение команды с логированием"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print(f"{'='*50}")
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    
    if result.stdout:
        print("STDOUT:")
        print(result.stdout)
    
    if result.stderr:
        print("STDERR:")
        print(result.stderr)
    
    if result.returncode != 0:
        print(f"ERROR: Command failed with return code {result.returncode}")
        return False
    
    return True

def main():
    """Основная функция CI"""
    print(f"Starting CI run at {datetime.now()}")
    
    # Создание директорий
    os.makedirs("reports", exist_ok=True)
    os.makedirs("error_screenshots", exist_ok=True)
    
    # Установка зависимостей
    if not run_command("uv sync", "Installing dependencies"):
        sys.exit(1)
    
    # Запуск линтера
    if not run_command("uv run ruff check .", "Running linter"):
        sys.exit(1)
    
    # Запуск тестов
    if not run_command(
        "uv run pytest tests/ -v --html=reports/report.html --self-contained-html",
        "Running tests"
    ):
        sys.exit(1)
    
    # Генерация отчета о покрытии
    if not run_command(
        "uv run pytest tests/ --cov=pyui_automation --cov-report=html:reports/coverage",
        "Generating coverage report"
    ):
        sys.exit(1)
    
    print(f"\nCI run completed successfully at {datetime.now()}")

if __name__ == "__main__":
    main()
```

## Примеры расширения функциональности

### Кастомный элемент
```python
from pyui_automation.elements.base import UIElement

class CustomButton(UIElement):
    """Кастомная кнопка с дополнительной функциональностью"""
    
    def flash(self, times=3, color="yellow"):
        """Мигание кнопки"""
        original_color = self.get_property("background")
        
        for _ in range(times):
            self.set_property("background", color)
            time.sleep(0.2)
            self.set_property("background", original_color)
            time.sleep(0.2)
    
    def is_loading(self) -> bool:
        """Проверка состояния загрузки"""
        return "loading" in self.get_property("class").lower()
    
    def wait_for_ready(self, timeout=10.0):
        """Ожидание готовности кнопки"""
        start_time = time.time()
        while time.time() - start_time < timeout:
            if not self.is_loading():
                return True
            time.sleep(0.1)
        raise TimeoutError("Button not ready")

# Использование
custom_button = CustomButton(session.find_element(ByName("customButton")))
custom_button.flash(5, "red")
custom_button.wait_for_ready()
custom_button.click()
```

### Кастомный локатор
```python
from pyui_automation.locators import BaseLocator, LocatorStrategy

class ByCustomAttribute(LocatorStrategy):
    """Кастомная стратегия поиска по атрибуту"""
    
    def __init__(self, attribute_name: str, attribute_value: str):
        self.attribute_name = attribute_name
        self.attribute_value = attribute_value
        super().__init__()

class CustomLocator(BaseLocator):
    """Кастомный локатор с дополнительными стратегиями"""
    
    def _find_element_impl(self, strategy: LocatorStrategy):
        if isinstance(strategy, ByCustomAttribute):
            return self.backend.find_element_by_custom_attribute(
                strategy.attribute_name,
                strategy.attribute_value
            )
        return super()._find_element_impl(strategy)

# Использование
custom_locator = CustomLocator(backend)
element = custom_locator.find_element(ByCustomAttribute("data-testid", "submit-button"))
```

Эти примеры демонстрируют различные способы использования PyUI Automation для автоматизации и тестирования UI приложений. Каждый пример можно адаптировать под конкретные потребности проекта. 