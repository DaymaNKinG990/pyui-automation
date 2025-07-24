# Getting Started

## 🛠️ **Установка**

### Рекомендуемый способ (uv)
```bash
# Установка с помощью uv
uv add pyui-automation

# Или для проекта
uv add pyui-automation --project
```

### Альтернативный способ (pip)
```bash
pip install pyui-automation
```

## 🚀 **Быстрый старт: Автоматизация Qt/Windows приложения**

### Базовый пример
```python
from pyui_automation.core import DIAutomationManager, AutomationSession
from pyui_automation.core.factory import BackendFactory

# Создание менеджера с DI
manager = DIAutomationManager()

# Создание backend для Windows
backend = BackendFactory.create_backend('windows')
session = AutomationSession(backend)

# Поиск и взаимодействие с элементами
login = session.find_element_by_object_name("loginField")
login.type_text("user")

password = session.find_element_by_object_name("passwordField")
password.type_text("pass")

session.find_element_by_object_name("loginButton").click()
```

### Пример с Notepad++
```python
from pyui_automation.core import DIAutomationManager, AutomationSession
from pyui_automation.core.factory import BackendFactory
from pyui_automation.application import Application

# Создание менеджера и сессии
manager = DIAutomationManager()
backend = BackendFactory.create_backend('windows')
session = AutomationSession(backend)

# Запуск Notepad++
app = Application.launch(r"C:\Program Files\Notepad++\notepad++.exe")
window = app.wait_for_window("Notepad++")

# Поиск главного окна и ввод текста
main_editor = session.find_element_by_object_name("Notepad++")
main_editor.type_text("Hello, PyUI Automation!")

# Сохранение файла
save_button = session.find_element_by_object_name("Save")
save_button.click()
```

## 🔍 **Визуальное тестирование**

```python
# Инициализация визуального тестирования
session.init_visual_testing("visual_baseline/")

# Создание baseline
session.capture_visual_baseline("main_window")

# Сравнение с baseline
result = session.compare_visual("main_window")

if not result["match"]:
    # Генерация отчета о различиях
    session.generate_visual_report("main_window", result["differences"], "reports/")
    print(f"Visual test failed! Similarity: {result['similarity']:.2f}")
else:
    print("Visual test passed!")
```

## ♿ **Accessibility проверки**

```python
# Проверка accessibility
violations = session.check_accessibility()

if violations:
    print(f"Found {len(violations)} accessibility violations:")
    for violation in violations:
        print(f"- {violation['type']}: {violation['description']}")
    
    # Генерация отчета
    session.generate_accessibility_report("reports/accessibility.html")
else:
    print("No accessibility violations found!")
```

## 📊 **Мониторинг производительности**

```python
# Запуск мониторинга производительности
session.start_performance_monitoring(interval=1.0)

# Выполнение действий
for i in range(10):
    button = session.find_element_by_object_name(f"button_{i}")
    button.click()

# Остановка мониторинга и получение метрик
metrics = session.stop_performance_monitoring()

print(f"Average CPU usage: {metrics['avg_cpu_usage']:.2f}%")
print(f"Average memory usage: {metrics['avg_memory_usage']:.2f} MB")
print(f"Total operations: {metrics['total_operations']}")
```

## 🔤 **OCR (распознавание текста)**

```python
# Настройка языков для OCR
session.ocr.set_languages(['en', 'ru'])

# Чтение текста из элемента
element = session.find_element_by_object_name("textElement")
text = session.ocr.read_text_from_element(element)
print(f"Extracted text: {text}")

# Распознавание текста из изображения
import numpy as np
image = session.capture_screenshot()
text = session.ocr.recognize_text(image)
print(f"Image text: {text}")
```

## 🎮 **Игровая автоматизация**

```python
from pyui_automation.game_elements import HealthBar, SkillBar

# Создание игровых элементов
health_bar = HealthBar(session)
skill_bar = SkillBar(session)

# Мониторинг здоровья
if health_bar.is_low():
    print("Health is low! Using potion...")
    # Логика использования зелья

# Использование скиллов
if not skill_bar.is_on_cooldown(1):
    skill_bar.use_skill(1)
    print("Skill 1 used!")
```

## 🔧 **DI и расширяемость**

```python
from pyui_automation.core import DIAutomationManager
from pyui_automation.core.interfaces import IBackend

# Создание кастомного backend
class MyCustomBackend(IBackend):
    def find_element_by_object_name(self, name: str):
        # Кастомная реализация
        pass

# Регистрация в DI контейнере
manager = DIAutomationManager()
manager.register_backend('custom', MyCustomBackend)

# Использование кастомного backend
backend = BackendFactory.create_backend('custom')
session = AutomationSession(backend)
```

## 🧪 **Запуск тестов**

```bash
# Установка зависимостей для тестирования
uv add pytest pytest-cov

# Запуск тестов с покрытием
uv run pytest tests/ --cov=pyui_automation --cov-report=html

# Запуск конкретного теста
uv run pytest tests/test_basic.py::test_element_finding
```

## 📍 **Локаторы Qt**

```python
# Поиск по objectName (рекомендуется)
element = session.find_element_by_object_name("submitBtn")

# Поиск по типу виджета
elements = session.find_elements_by_widget_type("QPushButton")

# Поиск по тексту
element = session.find_element_by_text("OK")

# Поиск по свойству
element = session.find_element_by_property("enabled", "true")
```

## ⚙️ **Конфигурация**

```python
from pyui_automation.core.config import AutomationConfig

# Создание конфигурации
config = AutomationConfig(
    timeout=30.0,
    retry_attempts=3,
    retry_delay=1.0,
    screenshot_format='png',
    log_level='INFO'
)

# Создание сессии с конфигурацией
session = AutomationSession(backend, config=config)
```

## 🎯 **Best Practices**

1. **Используйте objectName** для поиска элементов (наиболее надежный способ)
2. **Запускайте тесты с правами администратора** на Windows
3. **Проверяйте пути к .exe** (не используйте .lnk ярлыки)
4. **Используйте DI контейнер** для расширяемости
5. **Создавайте baseline** для визуального тестирования
6. **Мониторьте производительность** для долгих сценариев
7. **Обрабатывайте исключения** для надежности
8. **Используйте uv** для управления зависимостями

## 🚨 **Важные замечания**

- **Windows**: Для UI Automation требуется запуск с правами администратора
- **Linux**: Требуется установка AT-SPI2 (`sudo apt-get install libatspi2.0-dev`)
- **macOS**: Требуется разрешение на Accessibility в System Preferences
- **Qt**: Убедитесь, что приложение использует поддерживаемый backend

## 📚 **Следующие шаги**

1. Изучите [Core Concepts](./core_concepts.md) для понимания архитектуры
2. Ознакомьтесь с [UI Elements](./ui_elements.md) для работы с элементами
3. Изучите [Property System](./property_system.md) для расширенной работы
4. Посмотрите [Examples](./examples.md) для практических примеров
