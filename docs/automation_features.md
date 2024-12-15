# Automation Features

This guide covers the advanced automation features available in PyUI Automation.

## Screen Capture and Analysis

### Screenshot Capture
```python
from pyui_automation import Application, ImageUtils

app = Application()

# Capture full screen
screenshot = app.capture_screen()

# Capture specific region
region = (100, 100, 500, 500)  # x, y, width, height
region_shot = app.capture_screen(region=region)

# Capture specific window
window_shot = app.capture_window("Window Title")

# Save screenshot
screenshot.save("screenshot.png")
```

### Image Recognition
```python
# Template matching
template = ImageUtils.load_image("button_template.png")
location = app.find_image(template, confidence=0.9)

# OCR (Optical Character Recognition)
text = app.get_text_from_image(region=(100, 100, 300, 50))
text_locations = app.find_text("Click me", confidence=0.8)

# Image comparison
diff = ImageUtils.compare_images("baseline.png", "current.png")
similarity = ImageUtils.get_similarity(image1, image2)
```

### Color Analysis
```python
# Get pixel color
color = app.get_pixel_color(x=100, y=100)

# Find color in region
red_pixels = app.find_color((255, 0, 0), region=(0, 0, 100, 100))

# Color matching
is_match = ImageUtils.colors_match(color1, color2, tolerance=5)
```

## Input Automation

### Mouse Control
```python
from pyui_automation import Mouse

# Basic movements
Mouse.move(100, 200)
Mouse.move_smooth(100, 200)  # Human-like movement

# Click operations
Mouse.click()
Mouse.double_click()
Mouse.right_click()

# Drag operations
Mouse.drag(start_x=100, start_y=100, end_x=200, end_y=200)
Mouse.drag_smooth(start_x=100, start_y=100, end_x=200, end_y=200)

# Scroll
Mouse.scroll(10)  # Scroll up
Mouse.scroll(-10)  # Scroll down
```

### Keyboard Control
```python
from pyui_automation import Keyboard

# Text input
Keyboard.type("Hello World")
Keyboard.type_with_delay("Hello World", delay=0.1)

# Special keys
Keyboard.press('enter')
Keyboard.press('ctrl+c')
Keyboard.press(['ctrl', 'shift', 'esc'])

# Key combinations
with Keyboard.held_keys('ctrl'):
    Keyboard.press('c')
```

### Game Input
```python
from pyui_automation import GameInput

# Initialize game input
game_input = GameInput()

# Basic actions
game_input.press_key('space')
game_input.hold_key('w', duration=2.0)
game_input.click(x=100, y=100)

# Complex actions
game_input.perform_combo(['w', 'w', 's', 'space'])
game_input.move_mouse_smooth(100, 100, duration=0.5)
```

## Window Management

### Window Control
```python
# Find window
window = app.find_window(title="Application")

# Window operations
window.maximize()
window.minimize()
window.restore()
window.close()

# Window properties
size = window.get_size()
position = window.get_position()
is_visible = window.is_visible()

# Window manipulation
window.move(x=100, y=100)
window.resize(width=800, height=600)
window.set_foreground()
```

### Multi-Window Handling
```python
# Get all windows
windows = app.get_windows()

# Switch between windows
for window in windows:
    window.activate()
    # Perform operations
    
# Work with multiple windows
def handle_multiple_windows():
    main_window = app.find_window(title="Main")
    dialog = app.find_window(title="Dialog")
    
    with main_window.as_active():
        # Operations in main window
        pass
        
    with dialog.as_active():
        # Operations in dialog
        pass
```

## Process Management

### Process Control
```python
from pyui_automation import Process

# Start process
process = Process.start("notepad.exe")

# Find existing process
process = Process.find_by_name("notepad.exe")
process = Process.find_by_window("Notepad")

# Process operations
process.terminate()
process.kill()
process.is_running()

# Process information
pid = process.pid
name = process.name
memory = process.memory_usage()
cpu = process.cpu_usage()
```

### Process Monitoring
```python
class ProcessMonitor:
    def __init__(self, process_name):
        self.process = Process.find_by_name(process_name)
        
    def monitor(self, interval=1.0):
        while True:
            cpu = self.process.cpu_usage()
            memory = self.process.memory_usage()
            print(f"CPU: {cpu}%, Memory: {memory}MB")
            time.sleep(interval)
```

## Performance Optimization

### Caching
```python
class CachedAutomation:
    def __init__(self):
        self._cache = {}
        
    def find_element(self, **kwargs):
        cache_key = str(kwargs)
        if cache_key not in self._cache:
            self._cache[cache_key] = app.find_element(**kwargs)
        return self._cache[cache_key]
        
    def clear_cache(self):
        self._cache.clear()
```

### Batch Operations
```python
def batch_click_elements(elements):
    """Perform batch operations efficiently"""
    with app.batch_mode():
        for element in elements:
            element.click()
```

### Performance Monitoring
```python
class PerformanceTracker:
    def __init__(self):
        self.start_time = time.time()
        self.operations = []
        
    def record_operation(self, operation):
        duration = time.time() - self.start_time
        self.operations.append({
            'operation': operation,
            'time': duration
        })
        
    def get_statistics(self):
        total_ops = len(self.operations)
        total_time = self.operations[-1]['time']
        ops_per_second = total_ops / total_time
        return {
            'total_operations': total_ops,
            'total_time': total_time,
            'operations_per_second': ops_per_second
        }
```

## Error Handling

### Retry Mechanism
```python
def retry_operation(func, max_attempts=3, delay=1):
    """Retry an operation with exponential backoff"""
    for attempt in range(max_attempts):
        try:
            return func()
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(delay * (2 ** attempt))
```

### Error Recovery
```python
class AutomationRecovery:
    def __init__(self):
        self.recovery_actions = {}
        
    def register_recovery(self, error_type, action):
        self.recovery_actions[error_type] = action
        
    def handle_error(self, error):
        error_type = type(error)
        if error_type in self.recovery_actions:
            self.recovery_actions[error_type]()
            return True
        return False
```

## Logging and Debugging

### Advanced Logging
```python
class AutomationLogger:
    def __init__(self):
        self.logger = logging.getLogger('automation')
        self.setup_logging()
        
    def setup_logging(self):
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # File handler
        fh = logging.FileHandler('automation.log')
        fh.setFormatter(formatter)
        self.logger.addHandler(fh)
        
        # Console handler
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)
        
    def log_action(self, action, **kwargs):
        self.logger.info(f"Action: {action}, Parameters: {kwargs}")
        
    def log_error(self, error, context=None):
        self.logger.error(f"Error: {error}, Context: {context}")
```

### Debugging Tools
```python
class AutomationDebugger:
    def __init__(self):
        self.breakpoints = set()
        
    def add_breakpoint(self, condition):
        self.breakpoints.add(condition)
        
    def check_breakpoint(self, condition):
        if condition in self.breakpoints:
            import pdb; pdb.set_trace()
            
    def capture_state(self):
        """Capture current automation state for debugging"""
        return {
            'mouse_position': Mouse.get_position(),
            'active_window': app.get_active_window(),
            'screenshot': app.capture_screen(),
            'time': time.time()
        }
```

## Best Practices

1. **Always use explicit waits**
```python
# Bad
time.sleep(2)
element.click()

# Good
app.wait_for_element(timeout=2).click()
```

2. **Handle resources properly**
```python
# Bad
process = Process.start("app.exe")
# ... operations ...

# Good
with Process.start("app.exe") as process:
    # ... operations ...
    # Process automatically terminated after block
```

3. **Use appropriate logging levels**
```python
# Debug information
logger.debug("Attempting to find element")

# Normal operations
logger.info("Element found and clicked")

# Warnings
logger.warning("Element took longer than expected to appear")

# Errors
logger.error("Failed to find element", exc_info=True)
```

4. **Implement proper cleanup**
```python
try:
    # Automation code
    pass
except Exception:
    # Error handling
    pass
finally:
    # Cleanup
    app.cleanup()
    mouse.reset_position()
    keyboard.release_all_keys()
```

## Next Steps

- Explore [Game Automation](./game_automation.md)
- Learn about [Advanced Topics](./advanced_topics.md)
- Check out the [API Reference](./api_reference.md)
