# pyui-automation

A cross-platform library for desktop/Qt UI automation with a service architecture, support for Qt-locators, visual testing, accessibility, performance, and OCR. Supports automation of Notepad++ and other Windows applications.

## Quick Start
```python
from pyui_automation.core import AutomationSession
from pyui_automation.core.factory import BackendFactory

# Create an automation session for Windows
backend = BackendFactory.create_backend('windows')
session = AutomationSession(backend)

# Find and interact with an element
el = session.find_element_by_object_name("loginButton")
el.click()
el.type_text("admin")
```

## Example: Notepad++ Automation
```python
from pyui_automation.core import AutomationSession
from pyui_automation.application import Application
from pyui_automation.core.factory import BackendFactory

backend = BackendFactory.create_backend('windows')
session = AutomationSession(backend)

# Launch Notepad++
app = Application.launch(r"D:/Programs/Notepad++/notepad++.exe")
window = app.wait_for_window("Notepad++")

# Interact with the main window
main = session.find_element_by_object_name("Notepad++")
main.type_text("Hello, world!")
```

## Visual Testing
```python
session.init_visual_testing(baseline_dir="visual_baseline/")
session.capture_visual_baseline("main_window")
result = session.compare_visual("main_window")
if not result["match"]:
    session.generate_visual_report("main_window", result["differences"], "reports/")
```

## Performance
```python
session.start_performance_monitoring(interval=1.0)
# ... actions ...
metrics = session.get_performance_metrics()
```

## Accessibility
```python
violations = session.check_accessibility()
session.generate_accessibility_report("reports/accessibility.html")
```

## OCR
```python
text = session.ocr.read_text_from_element(element)
```

## Windows Launch Notes
- For Windows UI Automation, tests and scripts must be run with administrator rights.
- Make sure the path to the application executable is correct (use .exe, not a .lnk shortcut).

## Architecture
- AutomationSession (facade) → services (Backend, Input, Visual, Performance, Accessibility, OCR, Application).
- Each service implements only its own responsibility.
- All platform interactions go through the backend.

## DI and Extensibility
```python
from pyui_automation.di import container
class MyCustomBackend:
    ...
container.register('BackendService', MyCustomBackend)
backend = container.resolve('BackendService')
```

## Testing
- All services are easy to mock.
- Test coverage: unit, integration, edge-case for visual and accessibility.
- To run tests use:
```
uv run pytest tests --cov=.
```

## Documentation
- [docs/getting_started.md](docs/getting_started.md)
- [docs/api_reference.md](docs/api_reference.md)
- [docs/advanced_topics.md](docs/advanced_topics.md)
- [docs/core_concepts.md](docs/core_concepts.md)
- [docs/ui_elements.md](docs/ui_elements.md)
- [docs/automation_features.md](docs/automation_features.md)
- [docs/game_automation.md](docs/game_automation.md)
