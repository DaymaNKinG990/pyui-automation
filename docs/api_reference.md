# API Reference

This document provides a comprehensive reference for all public APIs in PyUI Automation.

## Core Classes

### Application
```python
class Application:
    def __init__(self):
        """Initialize application automation"""
        pass
        
    def connect(self, title: str = None, process_id: int = None):
        """Connect to an application window"""
        pass
        
    def find_element(self, **kwargs):
        """Find a UI element"""
        pass
        
    def find_elements(self, **kwargs):
        """Find multiple UI elements"""
        pass
        
    def wait_for_element(self, **kwargs):
        """Wait for element to appear"""
        pass
        
    def close(self):
        """Close the application"""
        pass
```

### GameBackend
```python
class GameBackend:
    def __init__(self):
        """Initialize game automation backend"""
        pass
        
    def connect(self, title: str):
        """Connect to game window"""
        pass
        
    def capture_screen(self, region: tuple = None):
        """Capture screen or region"""
        pass
        
    def find_element(self, template: Image.Image):
        """Find element using template matching"""
        pass
```

### UIElement
```python
class UIElement:
    def click(self):
        """Click the element"""
        pass
        
    def double_click(self):
        """Double click the element"""
        pass
        
    def right_click(self):
        """Right click the element"""
        pass
        
    def hover(self):
        """Move mouse to element"""
        pass
        
    def type_text(self, text: str):
        """Type text into element"""
        pass
        
    def get_text(self) -> str:
        """Get element text"""
        pass
        
    def is_visible(self) -> bool:
        """Check if element is visible"""
        pass
        
    def is_enabled(self) -> bool:
        """Check if element is enabled"""
        pass
        
    def get_property(self, name: str):
        """Get element property"""
        pass
        
    def set_property(self, name: str, value: Any):
        """Set element property"""
        pass
```

### GameElement
```python
class GameElement:
    def __init__(self, backend, template):
        """Initialize game element"""
        pass
        
    def find(self) -> tuple:
        """Find element position"""
        pass
        
    def click(self):
        """Click the element"""
        pass
        
    def wait_until_visible(self, timeout: float = 10):
        """Wait until element is visible"""
        pass
```

## Input Classes

### Mouse
```python
class Mouse:
    @staticmethod
    def move(x: int, y: int, duration: float = 0):
        """Move mouse to position"""
        pass
        
    @staticmethod
    def click(x: int = None, y: int = None, button: str = 'left'):
        """Click at position"""
        pass
        
    @staticmethod
    def double_click(x: int = None, y: int = None):
        """Double click at position"""
        pass
        
    @staticmethod
    def right_click(x: int = None, y: int = None):
        """Right click at position"""
        pass
        
    @staticmethod
    def drag(start_x: int, start_y: int, end_x: int, end_y: int):
        """Drag from start to end"""
        pass
        
    @staticmethod
    def scroll(amount: int):
        """Scroll wheel"""
        pass
```

### Keyboard
```python
class Keyboard:
    @staticmethod
    def type_text(text: str, interval: float = 0):
        """Type text with optional interval"""
        pass
        
    @staticmethod
    def press_key(key: str):
        """Press a key"""
        pass
        
    @staticmethod
    def press_keys(*keys: str):
        """Press multiple keys"""
        pass
        
    @staticmethod
    def hold_key(key: str):
        """Hold a key down"""
        pass
        
    @staticmethod
    def release_key(key: str):
        """Release a held key"""
        pass
```

### GameInput
```python
class GameInput:
    def __init__(self):
        """Initialize game input handler"""
        pass
        
    def press_key(self, key: str):
        """Press a key"""
        pass
        
    def hold_key(self, key: str, duration: float):
        """Hold key for duration"""
        pass
        
    def click(self, x: int, y: int):
        """Click at position"""
        pass
        
    def move_mouse(self, x: int, y: int):
        """Move mouse to position"""
        pass
```

## Image Processing

### ImageUtils
```python
class ImageUtils:
    @staticmethod
    def load_image(path: str) -> Image.Image:
        """Load image from file"""
        pass
        
    @staticmethod
    def save_image(image: Image.Image, path: str):
        """Save image to file"""
        pass
        
    @staticmethod
    def compare_images(image1: Image.Image, image2: Image.Image) -> float:
        """Compare two images"""
        pass
        
    @staticmethod
    def find_template(image: Image.Image, template: Image.Image) -> tuple:
        """Find template in image"""
        pass
```

### OCR
```python
class OCR:
    def __init__(self):
        """Initialize OCR engine"""
        pass
        
    def recognize(self, image: Image.Image) -> str:
        """Recognize text in image"""
        pass
        
    def find_text(self, text: str, image: Image.Image) -> list:
        """Find text locations in image"""
        pass
```

## Configuration

### Config
```python
class Config:
    def __init__(self):
        """Initialize configuration"""
        self.timeout = 10
        self.retry_interval = 0.5
        self.screenshot_format = 'png'
        self.log_level = 'INFO'
        
    def load_from_file(self, path: str):
        """Load config from file"""
        pass
        
    def save_to_file(self, path: str):
        """Save config to file"""
        pass
```

### Logger
```python
class Logger:
    def __init__(self):
        """Initialize logger"""
        pass
        
    def setup(self, level: str = 'INFO'):
        """Setup logging configuration"""
        pass
        
    def debug(self, message: str, **kwargs):
        """Log debug message"""
        pass
        
    def info(self, message: str, **kwargs):
        """Log info message"""
        pass
        
    def warning(self, message: str, **kwargs):
        """Log warning message"""
        pass
        
    def error(self, message: str, **kwargs):
        """Log error message"""
        pass
```

## Performance

### PerformanceMonitor
```python
class PerformanceMonitor:
    def __init__(self):
        """Initialize performance monitor"""
        pass
        
    def start_metric(self, name: str):
        """Start measuring metric"""
        pass
        
    def end_metric(self, name: str):
        """End measuring metric"""
        pass
        
    def get_metric(self, name: str) -> float:
        """Get metric value"""
        pass
        
    def reset(self):
        """Reset all metrics"""
        pass
```

## Exceptions

### AutomationError
```python
class AutomationError(Exception):
    """Base class for automation errors"""
    pass
```

### ElementNotFoundError
```python
class ElementNotFoundError(AutomationError):
    """Element not found within timeout"""
    pass
```

### TimeoutError
```python
class TimeoutError(AutomationError):
    """Operation timed out"""
    pass
```

### ConnectionError
```python
class ConnectionError(AutomationError):
    """Failed to connect to application"""
    pass
```

## Constants

### Mouse Buttons
```python
MOUSE_BUTTON_LEFT = 'left'
MOUSE_BUTTON_RIGHT = 'right'
MOUSE_BUTTON_MIDDLE = 'middle'
```

### Special Keys
```python
KEY_ENTER = 'enter'
KEY_TAB = 'tab'
KEY_SPACE = 'space'
KEY_BACKSPACE = 'backspace'
KEY_DELETE = 'delete'
KEY_ESCAPE = 'escape'
KEY_UP = 'up'
KEY_DOWN = 'down'
KEY_LEFT = 'left'
KEY_RIGHT = 'right'
```

### Image Formats
```python
IMAGE_FORMAT_PNG = 'png'
IMAGE_FORMAT_JPEG = 'jpeg'
IMAGE_FORMAT_BMP = 'bmp'
```

## Type Hints

### Common Types
```python
from typing import TypeVar, Union, Optional, List, Tuple, Dict, Any

# Element types
Element = TypeVar('Element', UIElement, GameElement)
ElementList = List[Element]

# Position types
Position = Tuple[int, int]
Region = Tuple[int, int, int, int]  # x, y, width, height

# Image types
from PIL import Image
ImageType = Union[str, Image.Image]

# Property types
PropertyValue = Union[str, int, float, bool]
PropertyDict = Dict[str, PropertyValue]
```

## Usage Examples

### Basic Automation
```python
from pyui_automation import Application

# Connect to application
app = Application()
app.connect(title="Notepad")

# Find and interact with elements
button = app.find_element(type="button", name="OK")
button.click()

# Type text
input_field = app.find_element(type="input")
input_field.type_text("Hello World")
```

### Game Automation
```python
from pyui_automation import GameBackend, GameInput

# Connect to game
game = GameBackend()
game.connect(title="Game Window")

# Create input handler
input_handler = GameInput()

# Perform game actions
input_handler.press_key('space')
input_handler.move_mouse(100, 100)
input_handler.click(100, 100)
```

### Image Processing
```python
from pyui_automation import ImageUtils, OCR

# Load and compare images
image1 = ImageUtils.load_image("screenshot1.png")
image2 = ImageUtils.load_image("screenshot2.png")
similarity = ImageUtils.compare_images(image1, image2)

# OCR
ocr = OCR()
text = ocr.recognize(image1)
```

### Error Handling
```python
from pyui_automation import AutomationError

try:
    element = app.find_element(type="button", timeout=5)
    element.click()
except ElementNotFoundError:
    print("Button not found")
except TimeoutError:
    print("Operation timed out")
except AutomationError as e:
    print(f"Automation error: {e}")
