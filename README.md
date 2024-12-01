# PyUI Automation

A powerful, cross-platform Python library for desktop UI testing and automation with advanced features including visual testing, performance monitoring, and accessibility checking.

## Features

- 🖥️ Cross-Platform Support (Windows, Linux, macOS)
- 🔍 Multiple Element Finding Strategies
- 🖱️ Advanced Input Simulation
- 📸 Visual Testing and Comparison
- ⚡ Performance Monitoring and Testing
- ♿ Accessibility Testing
- 🔄 Application Management
- 📊 Comprehensive Reporting

## Code Coverage

```
---------- coverage: platform win32, python 3.12.0-final-0 -----------
Name                                   Stmts   Miss  Cover
----------------------------------------------------------
pyui_automation/__init__.py                5      0   100%
pyui_automation/accessibility.py         136     43    68%
pyui_automation/application.py           138     62    55%
pyui_automation/backends/__init__.py      15      8    47%
pyui_automation/backends/base.py          38     15    61%
pyui_automation/backends/linux.py         77     60    22%
pyui_automation/backends/macos.py         95     77    19%
pyui_automation/backends/windows.py      212    179    16%
pyui_automation/core.py                  246     99    60%
pyui_automation/elements.py               77     46    40%
pyui_automation/input.py                 204    134    34%
pyui_automation/ocr.py                   143     77    46%
pyui_automation/optimization.py           77     35    55%
pyui_automation/performance.py           142     45    68%
pyui_automation/visual.py                168     26    85%
pyui_automation/wait.py                   45     23    49%
----------------------------------------------------------
TOTAL                                   1818    929    49%
```

### Coverage Highlights
- 🟢 High Coverage (>80%): Visual Testing, Core Initialization
- 🟡 Medium Coverage (50-80%): Accessibility, Performance, Core Functions
- 🔴 Low Coverage (<50%): Platform-specific Backends, Input Handling

## Installation

```bash
# Install required dependencies
pip install -r requirements.txt

# Install development dependencies
pip install -r requirements-dev.txt
```

## Testing

### Running Tests

```bash
# Run all tests
pytest

# Run specific test module
pytest tests/test_visual.py

# Run with coverage
pytest --cov=pyui_automation

# Generate HTML coverage report
pytest --cov=pyui_automation --cov-report=html
```

### Test Structure

```
tests/
├── conftest.py           # Shared fixtures
├── test_accessibility.py # Accessibility testing
├── test_core.py         # Core functionality
├── test_input.py        # Input simulation
├── test_performance.py  # Performance monitoring
├── test_visual.py       # Visual comparison
└── test_wait.py         # Wait conditions
```

## Quick Start

```python
from pyui_automation import UIAutomation

# Initialize automation
ui = UIAutomation()

# Launch application
app = ui.launch_application("path/to/app.exe")

# Find and interact with elements
button = ui.find_element(by="name", value="Submit")
button.click()

# Visual testing
ui.init_visual_testing()
ui.capture_visual_baseline("login_screen")
assert ui.compare_visual("login_screen")

# Accessibility testing
checker = ui.create_accessibility_checker()
violations = checker.check_element(button)
```

## Core Features

### Element Interaction

```python
# Find element with different strategies
element = ui.find_element(by="id", value="username")
element = ui.find_element(by="xpath", value="//button[@name='submit']")
element = ui.find_element(by="css", value="#submit-button")

# Element actions
element.click()
element.type_text("Hello World")
element.get_screenshot()
```

### Visual Testing

```python
# Initialize visual testing
ui.init_visual_testing("baseline_dir")

# Capture baseline
ui.capture_visual_baseline("main_screen")

# Compare with baseline
result = ui.compare_visual("main_screen")
assert result["match"], f"Visual mismatch: {result['differences']}"

# Hash-based comparison
assert ui.verify_visual_hash("main_screen")
```

### Accessibility Testing

```python
# Create checker
checker = ui.create_accessibility_checker()

# Check single element
violations = checker.check_element(button)

# Check entire application
app_violations = checker.check_application()

# Generate report
checker.generate_report("accessibility_report.html")
```

### Performance Monitoring

```python
# Start monitoring
ui.start_performance_monitoring()

# Perform actions
button.click()
ui.wait_for_element("result")

# Get metrics
metrics = ui.get_performance_metrics()
print(f"Response time: {metrics['response_time']}ms")
```

## Best Practices

1. **Element Location**
   - Use unique identifiers when possible
   - Prefer ID and name over XPath
   - Create robust element locators

2. **Visual Testing**
   - Keep baseline images in version control
   - Update baselines when UI changes are approved
   - Use element-specific comparisons for dynamic content

3. **Performance Testing**
   - Set realistic thresholds
   - Account for system variations
   - Monitor trends over time

4. **Cross-Platform Testing**
   - Test on all target platforms
   - Use platform-agnostic locators
   - Handle platform-specific differences

## Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
