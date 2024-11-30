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

## Installation

```bash
pip install -r requirements.txt
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

# Take screenshot
ui.take_screenshot("main_screen.png")
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
element.clear()
element.is_visible()
element.wait_until_visible(timeout=10)
```

### Visual Testing

```python
# Initialize visual testing
ui.init_visual_testing("baseline_images")

# Capture baseline
ui.capture_visual_baseline("login_screen")

# Compare with baseline
differences = ui.compare_visual("login_screen")
if differences:
    print(f"Found {len(differences)} visual differences")
    
# Quick hash-based comparison
result = ui.verify_visual_hash("login_screen")
if result['match']:
    print(f"Images match with {result['similarity']*100}% similarity")

# Generate visual report
ui.generate_visual_report("login_screen", differences, "reports")
```

### Performance Testing

```python
# Start monitoring
ui.start_performance_monitoring(interval=1.0)

# Measure specific action
def login_action():
    ui.find_element(by="id", value="username").type_text("user")
    ui.find_element(by="id", value="password").type_text("pass")
    ui.find_element(by="id", value="submit").click()

metrics = ui.measure_action_performance(
    action=login_action,
    name="login",
    test_runs=5
)

# Run stress test
stress_results = ui.run_stress_test(
    action=login_action,
    duration=60,
    interval=0.1
)

# Check for memory leaks
leak_results = ui.check_memory_leaks(
    action=login_action,
    iterations=100,
    threshold_mb=10.0
)

# Generate performance report
ui.generate_performance_report("performance_reports")
```

### Accessibility Testing

```python
# Run accessibility checks
violations = ui.check_accessibility()
for violation in violations:
    print(f"Rule: {violation['rule']}")
    print(f"Severity: {violation['severity']}")
    print(f"Description: {violation['description']}")
    print(f"Recommendation: {violation['recommendation']}")

# Generate accessibility report
ui.generate_accessibility_report("accessibility_reports")
```

### Application Management

```python
# Launch application
app = ui.launch_application(
    path="path/to/app.exe",
    args=["--debug"],
    env={"DEBUG": "1"}
)

# Attach to existing application
app = ui.attach_to_application("notepad.exe")

# Get current application
current_app = ui.get_current_application()

# Application properties
print(f"Process ID: {current_app.pid}")
print(f"Memory Usage: {current_app.memory_usage} MB")
print(f"CPU Usage: {current_app.cpu_usage}%")
```

## Advanced Usage

### Custom Wait Conditions

```python
# Wait for custom condition
ui.wait_until(lambda: ui.find_element(by="id", value="status").text == "Ready")

# Wait with timeout
ui.wait_until(
    condition=lambda: ui.find_element(by="id", value="progress").value == 100,
    timeout=30
)
```

### Element Collections

```python
# Find multiple elements
buttons = ui.find_elements(by="class", value="btn")

# Iterate and interact
for button in buttons:
    if button.is_visible() and button.is_enabled():
        button.click()
```

### OCR and Text Recognition

```python
# Find element by text content
element = ui.find_element(by="text", value="Click me")

# Use OCR to find text
text = ui.ocr.find_text("Submit")
if text:
    print(f"Found text at coordinates: {text.location}")
```

### Performance Optimization

```python
# Enable optimization features
ui.optimization.enable_caching()
ui.optimization.set_process_priority("high")
ui.optimization.enable_multi_threading()
```

## Best Practices

1. **Element Finding**
   - Use IDs when possible for fastest and most reliable element finding
   - Avoid complex XPath expressions
   - Use appropriate timeouts for dynamic elements

2. **Visual Testing**
   - Keep baseline images in version control
   - Update baselines when UI changes are approved
   - Use element-specific comparisons for dynamic content

3. **Performance Testing**
   - Run performance tests in a controlled environment
   - Include warm-up runs before measuring
   - Set appropriate thresholds for your application

4. **Accessibility Testing**
   - Run accessibility checks early in development
   - Address high-severity violations first
   - Include accessibility testing in CI/CD pipeline

## Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
