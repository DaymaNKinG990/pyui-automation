# Getting Started

## Installation

```bash
uv add pyui-automation
```

## Quick Start: Automating a Qt/Windows Application

```python
from pyui_automation.core import AutomationSession
from pyui_automation.core.factory import BackendFactory

# Create a backend for Windows
backend = BackendFactory.create_backend('windows')
session = AutomationSession(backend)

# Find and interact with elements
login = session.find_element_by_object_name("loginField")
login.type_text("user")
password = session.find_element_by_object_name("passwordField")
password.type_text("pass")
session.find_element_by_object_name("loginButton").click()
```

## Visual Testing

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
# ... actions ...
metrics = session.get_performance_metrics()
```

## OCR

```python
text = session.ocr.read_text_from_element(element)
```

## DI and Extensibility

```python
from pyui_automation.di import container
class MyCustomBackend:
    ...
container.register('BackendService', MyCustomBackend)
backend = container.resolve('BackendService')
```

## Qt Locators

```python
element = session.find_element_by_object_name("submitBtn")
elements = session.find_elements_by_widget_type("QPushButton")
```

## Running Tests

```bash
uv run pytest tests --cov=.
```
