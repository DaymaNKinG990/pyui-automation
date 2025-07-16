# Automation Features

Этот гайд описывает расширенные возможности автоматизации в PyUI Automation.

## Скриншоты и визуальный анализ

### Снятие скриншота
```python
from pyui_automation.core import AutomationSession
from pyui_automation.core.factory import BackendFactory

backend = BackendFactory.create_backend('windows')
session = AutomationSession(backend)

# Снимок экрана через backend
screenshot = session.backend.capture_screenshot()
```

### Визуальное сравнение
```python
session.init_visual_testing("visual_baseline/")
session.capture_visual_baseline("main_window")
result = session.compare_visual("main_window")
if not result["match"]:
    session.generate_visual_report("main_window", result["differences"], "reports/")
```

### OCR (распознавание текста)
```python
text = session.ocr.read_text_from_element(element)
```

### Сравнение изображений
```python
from pyui_automation.core.utils.image import compare_images
similarity = compare_images(image1, image2)
```

## Управление вводом

### Управление мышью
```python
mouse = session.mouse
mouse.move(100, 200)
mouse.click(100, 200)
mouse.double_click(100, 200)
mouse.right_click(100, 200)
mouse.drag(100, 100, 200, 200)
mouse.scroll(10)
```

### Управление клавиатурой
```python
keyboard = session.keyboard
keyboard.type_text("Hello World")
keyboard.press_key("enter")
keyboard.press_keys("ctrl", "c")
keyboard.release_key("ctrl")
```

## Управление окнами
```python
app = Application.launch(r"D:/Programs/Notepad++/notepad++.exe")
window = app.wait_for_window("Notepad++")
window_handle = session.backend.get_window_handle("Notepad++")
```

## Performance monitoring
```python
session.start_performance_monitoring()
# ... действия ...
metrics = session.get_performance_metrics()
```

## Accessibility
```python
violations = session.check_accessibility()
session.generate_accessibility_report("reports/accessibility.html")
```

## Best Practices
- Для Windows UI Automation всегда запускайте тесты с правами администратора.
- Для визуального тестирования храните baseline-изображения отдельно.
- Используйте только поддерживаемые методы поиска элементов.
- Для интеграции с CI/CD используйте uv и pytest.
- Проверяйте путь к .exe для приложений (не используйте .lnk).
