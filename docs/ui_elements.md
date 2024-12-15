# UI Elements

This guide covers all UI elements supported by PyUI Automation and their usage.

## Element Types

### Basic Elements

#### Button
```python
from pyui_automation import Application

app = Application()
app.connect(title="Application")

# Find button by text
button = app.find_element(type="button", text="Submit")
button.click()

# Find button by ID
button = app.find_element(type="button", id="submit-btn")
button.click()

# Check button state
if button.is_enabled():
    button.click()
```

#### Input Field
```python
# Find input field
input_field = app.find_element(type="input", name="username")

# Type text
input_field.type_text("user123")

# Clear text
input_field.clear()

# Get current value
value = input_field.get_text()
```

#### Checkbox
```python
checkbox = app.find_element(type="checkbox", name="agree")

# Check state
if not checkbox.is_checked():
    checkbox.click()

# Toggle state
checkbox.toggle()
```

#### Radio Button
```python
radio = app.find_element(type="radio", value="option1")

# Select option
radio.select()

# Check if selected
is_selected = radio.is_selected()
```

#### Dropdown/Combobox
```python
dropdown = app.find_element(type="combobox", name="country")

# Select by text
dropdown.select_option("United States")

# Select by index
dropdown.select_index(0)

# Get all options
options = dropdown.get_options()

# Get selected option
selected = dropdown.get_selected_option()
```

### Container Elements

#### Window
```python
window = app.find_element(type="window", title="Main Window")

# Window operations
window.maximize()
window.minimize()
window.restore()
window.close()

# Window properties
size = window.get_size()
position = window.get_position()
is_visible = window.is_visible()
```

#### Tab
```python
tab_control = app.find_element(type="tab", name="Settings")

# Switch tabs
tab_control.select_tab("General")

# Get active tab
active_tab = tab_control.get_active_tab()

# Get all tabs
tabs = tab_control.get_tabs()
```

#### Menu
```python
# Click menu item
app.click_menu("File", "Open")

# Complex menu navigation
app.click_menu("Edit", "Advanced", "Settings")

# Check menu item state
is_enabled = app.is_menu_enabled("Edit", "Undo")
```

#### TreeView
```python
tree = app.find_element(type="tree", id="file-tree")

# Expand node
tree.expand_node("Documents")

# Select node
tree.select_node("Documents/Reports")

# Get selected node
selected = tree.get_selected_node()

# Get node properties
node_text = tree.get_node_text("Documents/Reports")
has_children = tree.node_has_children("Documents")
```

### Custom Elements

#### Game UI Element
```python
from pyui_automation import GameElement

class GameButton(GameElement):
    def __init__(self, image_template):
        super().__init__()
        self.template = image_template
    
    def wait_and_click(self, timeout=10):
        """Wait for button to appear and click it"""
        if self.wait_until_visible(timeout):
            self.click()
            return True
        return False
```

## Element Properties

### Common Properties
```python
element = app.find_element(type="button", name="Submit")

# Basic properties
name = element.name
id = element.id
class_name = element.class_name

# State
enabled = element.is_enabled()
visible = element.is_visible()
focused = element.is_focused()

# Location and size
bounds = element.get_bounds()
center = element.get_center()
width, height = element.get_size()
x, y = element.get_position()
```

### Accessibility Properties
```python
# Get accessibility properties
role = element.get_role()
description = element.get_description()
value = element.get_value()

# Check states
is_required = element.is_required()
is_readonly = element.is_readonly()
can_focus = element.can_receive_focus()
```

## Element Actions

### Mouse Actions
```python
# Click types
element.click()
element.double_click()
element.right_click()
element.middle_click()

# Hover
element.hover()

# Drag and drop
element.drag_to(target_element)
element.drag_by(dx=100, dy=0)
```

### Keyboard Actions
```python
# Text input
element.type_text("Hello World")
element.send_keys("Hello{ENTER}")

# Special keys
element.send_key("F5")
element.send_keys(["ctrl", "c"])
```

## Element Finding

### Finding Strategies
```python
# By basic properties
element = app.find_element(type="button", name="Submit")
element = app.find_element(type="input", id="username")
element = app.find_element(type="checkbox", class_name="form-check")

# By text content
element = app.find_element(text="Click me")
element = app.find_element(text_contains="Click")

# By relative location
element = app.find_element(to_right_of=reference_element)
element = app.find_element(below=reference_element)

# Multiple elements
elements = app.find_elements(type="button")
```

### Wait Conditions
```python
# Wait for element
element = app.wait_for_element(
    type="button",
    name="Submit",
    timeout=10,
    interval=0.5
)

# Custom wait condition
app.wait_until(lambda: element.is_visible() and element.is_enabled())

# Wait for multiple conditions
app.wait_for_any([
    lambda: button1.is_visible(),
    lambda: button2.is_visible()
])
```

## Element Patterns

### Form Filling
```python
def fill_form(app, data):
    """Fill form with provided data"""
    for field_name, value in data.items():
        element = app.find_element(type="input", name=field_name)
        element.type_text(value)
```

### Element Verification
```python
def verify_element_state(element):
    """Verify element is in correct state"""
    assert element.is_visible(), "Element should be visible"
    assert element.is_enabled(), "Element should be enabled"
    assert not element.is_readonly(), "Element should not be readonly"
```

### Element Retry
```python
def retry_click(element, max_attempts=3):
    """Retry clicking element with error handling"""
    for attempt in range(max_attempts):
        try:
            element.click()
            return True
        except Exception as e:
            if attempt == max_attempts - 1:
                raise
            time.sleep(1)
    return False
```

## Best Practices

1. **Always use waits instead of sleep**
```python
# Bad
time.sleep(2)
button.click()

# Good
app.wait_for_element(type="button", timeout=2).click()
```

2. **Cache elements when possible**
```python
# Bad
for _ in range(10):
    app.find_element(type="button").click()

# Good
button = app.find_element(type="button")
for _ in range(10):
    button.click()
```

3. **Use appropriate finding strategies**
```python
# Bad - fragile
element = app.find_element(type="button", position=(100, 200))

# Good - robust
element = app.find_element(type="button", name="Submit")
```

4. **Handle dynamic content**
```python
def wait_for_content_update(element, old_value):
    """Wait for element content to update"""
    def content_updated():
        return element.get_text() != old_value
    app.wait_until(content_updated, timeout=10)
```

## Next Steps

- Learn about [Game Automation](./game_automation.md)
- Explore [Advanced Topics](./advanced_topics.md)
- Check out the [API Reference](./api_reference.md)
