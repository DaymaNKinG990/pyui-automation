# Advanced Topics

Этот гайд охватывает продвинутые техники и best practices для PyUI Automation.

## Кастомные элементы

### Создание кастомных элементов
```python
from pyui_automation.elements.base import UIElement

class CustomButton(UIElement):
    def flash(self, times=3):
        for _ in range(times):
            self.set_property('background', 'yellow')
            time.sleep(0.2)
            self.set_property('background', 'white')
            time.sleep(0.2)
```

## Расширение игровых элементов
```python
from pyui_automation.game_elements import HealthBar

class MyHealthBar(HealthBar):
    def is_critical(self):
        return self.current_value < 0.2 * self.max_value
```

## Расширение backend
```python
from pyui_automation.backends.base import BaseBackend

class MyBackend(BaseBackend):
    def find_element_by_custom(self, custom_param):
        # Реализация поиска
        ...
```

## Кастомные сценарии визуального тестирования
```python
session.init_visual_testing("visual_baseline/")
session.capture_visual_baseline("custom_element")
result = session.compare_visual("custom_element")
if not result["match"]:
    session.generate_visual_report("custom_element", result["differences"], "reports/")
```

## Расширенное OCR
```python
from pyui_automation.services.ocr import UnifiedOCREngine

ocr = UnifiedOCREngine()
ocr.set_languages(['en', 'ru'])
text = ocr.recognize_text(image)
```

## Кастомные паттерны ввода
```python
keyboard = session.keyboard
for char in "Hello, world!":
    keyboard.type_text(char)
    time.sleep(0.1)
```

## Performance optimization
```python
session.start_performance_monitoring()
# ... действия ...
metrics = session.get_performance_metrics()
```

## Memory management
- Используйте session.terminate() и Application.terminate() для корректного завершения процессов.
- Для долгих сценариев следите за утечками памяти через performance-мониторинг.

## Best Practices
- Для сложных сценариев расширяйте UIElement и backend через наследование.
- Для визуального тестирования используйте baseline и отчёты различий.
- Для интеграции с CI/CD используйте uv, pytest, coverage.
- Для кастомных сценариев OCR и image processing используйте numpy, cv2, PIL.
- Для сложных игровых сценариев комбинируйте визуальное сравнение, OCR и работу с координатами.
