# Getting Started with PyUI Automation

## Installation

Install PyUI Automation using pip:

```bash
pip install pyui-automation
```

For game automation features, install additional dependencies:

```bash
pip install pyui-automation[game]
```

## Basic Setup

### Windows
```python
from pyui_automation import Application, GameBackend

# For desktop applications
app = Application()
app.connect(title="Notepad")

# For games
game = GameBackend()
game.connect(title="Game Window")
```

### Linux
```python
from pyui_automation import Application, GameBackend

# For desktop applications
app = Application()
app.connect(title="gedit")

# For games (requires X11)
game = GameBackend()
game.connect(title="Game Window")
```

### macOS
```python
from pyui_automation import Application, GameBackend

# For desktop applications
app = Application()
app.connect(title="TextEdit")

# For games
game = GameBackend()
game.connect(title="Game Window")
```

## First Automation Script

Here's a simple example that demonstrates basic automation:

```python
from pyui_automation import Application, GameInput
import time

def simple_automation():
    # Connect to application
    app = Application()
    app.connect(title="Notepad")
    
    # Type some text
    app.type_text("Hello, PyUI Automation!")
    
    # Click a button
    app.click(text="File")
    app.click(text="Save")
    
    # Close application
    app.close()

def simple_game_automation():
    # Connect to game
    game = GameBackend()
    game.connect(title="Game Window")
    
    # Create input handler
    input = GameInput()
    
    # Perform some actions
    input.move_mouse(100, 100)
    input.click(100, 100)
    input.send_key('space')

if __name__ == '__main__':
    simple_automation()
    simple_game_automation()
```

## Configuration

Create a `config.yaml` file for custom settings:

```yaml
application:
  timeout: 10
  retry_interval: 0.5
  
game:
  failsafe: true
  pause: 0.1
  
input:
  move_duration: 0.2
  click_delay: 0.1
```

## Error Handling

Always use try-except blocks for robust automation:

```python
try:
    app = Application()
    app.connect(title="Window Title")
    # Your automation code
except ConnectionError:
    print("Failed to connect to application")
except TimeoutError:
    print("Operation timed out")
except Exception as e:
    print(f"Unexpected error: {e}")
finally:
    # Cleanup code
    if 'app' in locals():
        app.close()
```

## Logging

Enable detailed logging for debugging:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    filename='automation.log'
)

logger = logging.getLogger('pyui_automation')
```

## Next Steps

- Read the [Core Concepts](./core_concepts.md) guide
- Explore [UI Elements](./ui_elements.md)
- Check out [Game Automation](./game_automation.md)
- Learn about [Advanced Topics](./advanced_topics.md)
