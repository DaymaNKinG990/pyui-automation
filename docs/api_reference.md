# API Reference

Документ содержит актуальное описание публичных API PyUI Automation.

## Основные классы

### AutomationSession
```python
class AutomationSession:
    def __init__(self, backend, config=None): ...
    def find_element_by_object_name(self, name: str) -> UIElement: ...
    def find_elements_by_widget_type(self, widget_type: str) -> list[UIElement]: ...
    def init_visual_testing(self, baseline_dir: str): ...
    def capture_visual_baseline(self, name: str, element: UIElement = None): ...
    def compare_visual(self, name: str, element: UIElement = None) -> dict: ...
    def check_accessibility(self, element: UIElement = None) -> list: ...
    def start_performance_monitoring(self, interval: float = 1.0): ...
    def get_performance_metrics(self) -> dict: ...
    @property
    def ocr(self) -> OCREngine: ...
```

### Application
```python
class Application:
    @classmethod
    def launch(path: Path | str, args: list = None, cwd: str = None, env: dict = None) -> Application: ...
    def wait_for_window(self, title: str, timeout: float = 10.0): ...
    def terminate(self): ...
```

### Backend (WindowsBackend, LinuxBackend, MacOSBackend)
```python
class WindowsBackend:
    def find_element_by_object_name(self, name: str): ...
    def find_elements_by_widget_type(self, widget_type: str): ...
    def get_active_window(self): ...
    def get_window_handle(self, title: str): ...
    def capture_screenshot(self): ...
```

### UIElement
```python
class UIElement:
    def click(self): ...
    def double_click(self): ...
    def right_click(self): ...
    def type_text(self, text: str): ...
    def get_text(self) -> str: ...
    def is_visible(self) -> bool: ...
    def is_enabled(self) -> bool: ...
    def capture_screenshot(self) -> np.ndarray: ...
```

### OCREngine
```python
class OCREngine:
    def read_text_from_element(self, element: UIElement, preprocess: bool = False) -> str: ...
    def recognize_text(self, image: Path | str | np.ndarray, preprocess: bool = False) -> str: ...
    def set_languages(self, languages: list[str]): ...
```

### VisualTester
```python
class VisualTester:
    def capture_baseline(self, name: str, element: UIElement = None): ...
    def compare(self, name: str, element: UIElement = None) -> dict: ...
    def generate_report(self, name: str, differences, output_dir: str): ...
```

### Пример: запуск и взаимодействие с Notepad++
```python
from pyui_automation.core import AutomationSession
from pyui_automation.application import Application
from pyui_automation.core.factory import BackendFactory

backend = BackendFactory.create_backend('windows')
session = AutomationSession(backend)
app = Application.launch(r"D:/Programs/Notepad++/notepad++.exe")
window = app.wait_for_window("Notepad++")
main = session.find_element_by_object_name("Notepad++")
main.type_text("Hello, world!")
```

### Пример: визуальное сравнение
```python
session.init_visual_testing("visual_baseline/")
session.capture_visual_baseline("main_window")
result = session.compare_visual("main_window")
if not result["match"]:
    session.generate_visual_report("main_window", result["differences"], "reports/")
```

### Пример: accessibility
```python
violations = session.check_accessibility()
session.generate_accessibility_report("reports/accessibility.html")
```

### Пример: OCR
```python
text = session.ocr.read_text_from_element(element)
```

### Пример: performance
```python
session.start_performance_monitoring()
# ... действия ...
metrics = session.get_performance_metrics()
```
