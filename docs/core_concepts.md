# Core Concepts

## Архитектура (актуально)
- Вся логика вынесена в сервисы (Backend, Input, Visual, Performance, Accessibility, OCR, Application).
- AutomationSession — основной фасад для управления сессией автоматизации и доступом ко всем возможностям.
- Для поиска элементов используются Qt-локаторы (objectName, widget, text, property).
- Взаимодействие с платформой — только через backend.
- Для Windows UI Automation требуется запуск с правами администратора.

## AutomationSession (фасад)
```python
from pyui_automation.core import AutomationSession
from pyui_automation.core.factory import BackendFactory

backend = BackendFactory.create_backend('windows')
session = AutomationSession(backend)
```

## Поиск и взаимодействие с элементами
```python
el = session.find_element_by_object_name("mainButton")
el.click()
el.type_text("Hello!")
```

## Визуальное тестирование
```python
session.init_visual_testing("visual_baseline/")
session.capture_visual_baseline("main_window")
result = session.compare_visual("main_window")
if not result["match"]:
    session.generate_visual_report("main_window", result["differences"], "reports/")
```

## Accessibility
```python
violations = session.check_accessibility()
session.generate_accessibility_report("reports/accessibility.html")
```

## Performance
```python
session.start_performance_monitoring()
# ... действия ...
metrics = session.get_performance_metrics()
```

## OCR
```python
text = session.ocr.read_text_from_element(element)
```

## DI и расширяемость
```python
from pyui_automation.di import container
class MyCustomBackend:
    ...
container.register('BackendService', MyCustomBackend)
backend = container.resolve('BackendService')
```

## Особенности Windows
- Для работы с Windows UI Automation требуется запускать тесты/скрипты с правами администратора.
- Указывайте путь к .exe, а не к .lnk (ярлыку).

## Best Practices
- Всегда запускайте тесты с admin-правами на Windows.
- Используйте только поддерживаемые локаторы (objectName, widget, text, property).
- Для визуального тестирования храните baseline-изображения в отдельной папке.
- Для интеграции с CI/CD используйте uv и pytest.
- Для мокирования сервисов используйте DI-контейнер.
- Для Notepad++ и других приложений всегда проверяйте путь к .exe.
