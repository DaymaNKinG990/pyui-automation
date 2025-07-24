# Property System and Element Finding

## Overview

The new property system provides a flexible and type-safe way to access element properties and find child elements dynamically. This system replaces the hardcoded properties in `BaseElement` with a more extensible and maintainable approach.

## Key Components

### 1. Property Classes

#### Base Property Class
```python
from pyui_automation.elements import Property

# Base class for all properties
class Property(ABC):
    def __init__(self, name: str, element: Any)
    def get_value(self) -> Any
```

#### Specialized Property Classes

- **StringProperty**: For text-based attributes
- **IntProperty**: For numeric attributes  
- **BoolProperty**: For boolean attributes
- **DictProperty**: For complex attributes (location, size)
- **OptionalStringProperty**: For optional string attributes

### 2. Element Finder

The `ElementFinder` class provides methods to find child elements based on various criteria:

```python
from pyui_automation.elements import ElementFinder

finder = ElementFinder(native_element)
```

## Usage Examples

### Basic Property Access

```python
from pyui_automation import AutomationManager, ByName

# Create session and find element
manager = AutomationManager()
session = manager.create_session()
button = session.find_element(ByName("Submit Button"))

# Get properties dynamically
text = button.get_property_dynamic('text')
name = button.get_property_dynamic('name')
visible = button.get_property_dynamic('visible')
location = button.get_property_dynamic('location')
size = button.get_property_dynamic('size')

# Get property object for advanced operations
text_prop = button.get_property_object('text')
text_value = text_prop.get_value()

# Check if property exists
has_text = button.has_property('text')
```

### Element Finding Methods

#### Find by Property
```python
# Find child by specific property value
child = element.find_child_by_property('name', 'Submit')
children = element.find_children_by_property('control_type', 'button')
```

#### Find by Text
```python
# Find by text content (exact or partial match)
child = element.find_child_by_text("Click me", exact_match=True)
children = element.find_children_by_text("button", exact_match=False)
```

#### Find by Name
```python
# Find by element name
child = element.find_child_by_name("username_field")
children = element.find_children_by_name("input", exact_match=False)
```

#### Find by Control Type
```python
# Find by control type
buttons = element.find_children_by_control_type("button")
inputs = element.find_children_by_control_type("edit")
```

#### Find by Automation ID
```python
# Find by automation ID
child = element.find_child_by_automation_id("unique_id")
children = element.find_children_by_automation_id("input_group")
```

#### Find by State
```python
# Find visible/enabled elements
visible_children = element.find_visible_children()
enabled_children = element.find_enabled_children()
```

#### Find by Custom Predicate
```python
# Find using custom logic
def custom_predicate(element):
    text = element.get_property_dynamic('text')
    visible = element.get_property_dynamic('visible')
    return "important" in text.lower() and visible

important_elements = element.find_children_by_predicate(custom_predicate)
```

### Advanced Usage

#### Chaining Operations
```python
# Find form and then find specific inputs
form = session.find_element(ByName("Login Form"))
username_input = form.find_child_by_name("username")
password_input = form.find_child_by_name("password")
```

#### Complex Predicates
```python
def complex_predicate(element):
    """Find elements matching multiple criteria."""
    text = element.get_property_dynamic('text')
    visible = element.get_property_dynamic('visible')
    enabled = element.get_property_dynamic('enabled')
    control_type = element.get_property_dynamic('control_type')
    
    return (
        visible and 
        enabled and 
        control_type in ['button', 'edit'] and
        len(text) > 0
    )

complex_elements = form.find_children_by_predicate(complex_predicate)
```

## Available Properties

The system includes predefined properties for common element attributes:

### String Properties
- `text`: Element text content
- `name`: Element name
- `automation_id`: Element automation ID
- `class_name`: Element class name
- `control_type`: Element control type

### Optional String Properties
- `value`: Element value
- `selected_item`: Selected item text

### Boolean Properties
- `visible`: Element visibility
- `is_checked`: Element checked state
- `is_expanded`: Element expanded state
- `is_selected`: Element selected state

### Dictionary Properties
- `location`: Element location coordinates
- `size`: Element size dimensions
- `rect`: Element rectangle bounds
- `center`: Element center coordinates

## Creating Custom Properties

You can create custom properties by extending the base `Property` class:

```python
from pyui_automation.elements import StringProperty, PropertyDefinition

class CustomIntProperty(StringProperty):
    """Custom property that converts string to integer."""
    
    def get_value(self) -> int:
        try:
            string_value = super().get_value()
            return int(string_value) if string_value.isdigit() else 0
        except (ValueError, AttributeError):
            return 0

# Add to ELEMENT_PROPERTIES
ELEMENT_PROPERTIES['custom_number'] = PropertyDefinition(
    name="custom_number",
    property_class=CustomIntProperty,
    description="Custom numeric property"
)
```

## Benefits

1. **Type Safety**: Properties return appropriate types
2. **Extensibility**: Easy to add new property types
3. **Flexibility**: Dynamic property access
4. **Maintainability**: Centralized property definitions
5. **Performance**: Efficient property access patterns
6. **Error Handling**: Graceful fallbacks for missing properties

## Migration from Old Properties

The old property access methods are still available for backward compatibility:

```python
# Old way (still works)
text = element.text
name = element.name
visible = element.visible

# New way (recommended)
text = element.get_property_dynamic('text')
name = element.get_property_dynamic('name')
visible = element.get_property_dynamic('visible')
```

## Best Practices

1. **Use `get_property_dynamic()`** for most property access
2. **Use `get_property_object()`** when you need the property object
3. **Use `has_property()`** to check property existence
4. **Chain element finding** for complex scenarios
5. **Use predicates** for complex search criteria
6. **Handle None returns** from finding methods
7. **Cache frequently accessed properties** if performance is critical 