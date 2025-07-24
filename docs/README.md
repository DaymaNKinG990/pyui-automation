# PyUI Automation Documentation

PyUI Automation - мощная кроссплатформенная Python библиотека для автоматизации и тестирования пользовательских интерфейсов настольных приложений (Windows, Linux, macOS, Qt, игры). Поддерживает визуальное тестирование, accessibility, мониторинг производительности, OCR и современную архитектуру с Dependency Injection.

## 🚀 **Основные возможности**

- **Кроссплатформенность**: Windows, Linux, macOS
- **Поиск и взаимодействие с UI элементами** (objectName, widget type, text, property)
- **Визуальное сравнение и baseline тестирование**
- **Accessibility проверки**
- **Мониторинг производительности** (CPU, память, время отклика)
- **OCR (распознавание текста)** с поддержкой множественных языков
- **Современная архитектура** с Dependency Injection
- **Специализированные сервисы** для каждой области ответственности
- **Расширяемая система локаторов**
- **Система свойств элементов** с типизацией
- **Поддержка игровых UI элементов**
- **Высокоуровневый API** для упрощения работы QA Automation инженеров

## 🏗️ **Архитектура**

Фреймворк построен на принципах SOLID и Clean Architecture:

- **DIAutomationManager** - главный менеджер с DI
- **AutomationSession** - сессия автоматизации
- **PyUIAutomation** - высокоуровневый API для QA инженеров
- **Специализированные сервисы** - каждый сервис имеет одну ответственность
- **Интерфейсы** - для loose coupling
- **Платформо-зависимые backends** - Windows, Linux, macOS
- **Система локаторов** - для поиска элементов

## 📋 **Содержание документации**

### **Основы**
1. [Getting Started](./getting_started.md) - Быстрый старт
2. [High-Level API](./high_level_api.md) - Высокоуровневый API для QA Automation
3. [Core Concepts](./core_concepts.md) - Основные концепции
4. [Framework Architecture](./framework_architecture.md) - Архитектура фреймворка

### **Работа с элементами**
5. [UI Elements](./ui_elements.md) - UI элементы и их свойства
6. [Property System](./property_system.md) - Система свойств элементов
7. [Locators Guide](./locators_guide.md) - Руководство по локаторам

### **Возможности автоматизации**
8. [Automation Features](./automation_features.md) - Основные возможности
9. [Visual Testing](./visual_testing.md) - Визуальное тестирование
10. [OCR Guide](./ocr_guide.md) - Распознавание текста
11. [Performance Monitoring](./performance_monitoring.md) - Мониторинг производительности
12. [Game Automation](./game_automation.md) - Автоматизация игр

### **Архитектура и расширяемость**
13. [Dependency Injection](./dependency_injection.md) - Руководство по DI
14. [Configuration](./configuration.md) - Конфигурация фреймворка
15. [Error Handling](./error_handling.md) - Обработка ошибок

### **Тестирование и разработка**
16. [Testing Guide](./testing_guide.md) - Руководство по тестированию
17. [Advanced Topics](./advanced_topics.md) - Продвинутые темы
18. [Examples](./examples.md) - Примеры использования

### **Справочники**
19. [API Reference](./api_reference.md) - Справочник API
20. [Utils Guide](./utils_guide.md) - Руководство по утилитам
21. [Troubleshooting](./troubleshooting.md) - Решение проблем

## 🛠️ **Установка**

```bash
# Используя uv (рекомендуется)
uv add pyui-automation

# Или pip
pip install pyui-automation
```

## 🚀 **Быстрый старт**

### **Высокоуровневый API (рекомендуется для QA Automation)**

```python
from pyui_automation import PyUIAutomation, app_session

# Простое использование
with app_session("notepad++.exe", "Notepad++") as app:
    app.click("loginButton")
    app.type_text("username", "admin")
    app.type_text("password", "123456")
    app.click("submitButton")
    
    # Визуальное тестирование
    app.capture_baseline("main_window")
    app.assert_visual_match("main_window")
    
    # OCR
    text = app.get_ocr_text("elementName")
    
    # Мониторинг производительности
    app.start_performance_monitoring()
    # ... действия ...
    metrics = app.stop_performance_monitoring()
```

### **Низкоуровневый API (для разработчиков)**

```python
from pyui_automation.core import DIAutomationManager, AutomationSession
from pyui_automation.core.factory import BackendFactory

# Создание менеджера с DI
manager = DIAutomationManager()

# Создание сессии
backend = BackendFactory.create_backend('windows')
session = AutomationSession(backend)

# Поиск и взаимодействие с элементами
button = session.find_element_by_object_name("submitBtn")
button.click()

# Визуальное тестирование
session.init_visual_testing("baseline/")
session.capture_visual_baseline("main_window")
result = session.compare_visual("main_window")

# OCR
text = session.ocr.read_text_from_element(element)

# Мониторинг производительности
session.start_performance_monitoring()
# ... действия ...
metrics = session.get_performance_metrics()
```

## 🎯 **Особенности**

- **SOLID принципы** - каждый компонент имеет одну ответственность
- **Dependency Injection** - loose coupling между компонентами
- **Интерфейсы** - для тестируемости и расширяемости
- **Специализированные сервисы** - PerformanceMonitor, PerformanceAnalyzer, PerformanceTester, MemoryLeakDetector
- **Унифицированный OCR** - автоматический выбор реализации
- **Современная архитектура** - готова к продакшену
- **Высокоуровневый API** - упрощенная работа для QA Automation инженеров

## 📖 **Документация**

Полная документация доступна в папке `docs/`. Начните с [Getting Started](./getting_started.md) для быстрого старта или [High-Level API](./high_level_api.md) для упрощенного использования.

## 🤝 **Поддержка**

- **Issues**: Создавайте issues для багов и feature requests
- **Discussions**: Обсуждения и вопросы
- **Wiki**: Дополнительная информация

## 📄 **Лицензия**

MIT License - см. файл LICENSE для деталей.
