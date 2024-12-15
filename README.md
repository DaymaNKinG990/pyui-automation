# PyUI Automation

A powerful Python library for UI automation and game testing, providing a high-level API for interacting with UI elements across different platforms.

## Features

- Cross-platform support (Windows, Linux, MacOS)
- Game UI automation capabilities
- Rich set of UI element interactions
- Visual element detection and OCR support
- Performance optimization tools
- Extensive test coverage

## Project Structure

```
pyui_automation/
├── docs/                    # Documentation
├── pyui_automation/         # Main package
│   ├── backends/           # Platform-specific implementations
│   ├── core/              # Core functionality
│   ├── elements/          # UI element definitions
│   ├── game_elements/     # Game-specific UI elements
│   ├── input/            # Input device handling
│   └── utils/            # Utility functions
└── tests/                # Test suite
    └── test_game_elements/ # Game UI element tests
```

## Test Coverage

Current test coverage: 42%

Key components coverage:
- Core functionality: 89%
- UI Elements: 72%
- Game Elements: 40%
- Input handling: 72%
- Performance tools: 84%
- OCR functionality: 71%

## Documentation

Detailed documentation is available in the [docs](./docs) directory:

- [Getting Started](./docs/getting_started.md)
- [API Reference](./docs/api_reference.md)
- [Game UI Automation](./docs/game_ui.md)
- [Contributing Guide](./docs/contributing.md)

## Installation

```bash
pip install pyui-automation
```

## Quick Start

```python
from pyui_automation import Session
from pyui_automation.game_elements import HealthBar, SkillBar

# Create automation session
session = Session()

# Interact with game UI elements
health_bar = HealthBar(session)
current_health = health_bar.current_value

skill_bar = SkillBar(session)
skill_bar.use_skill(1)  # Use first skill
```

## Contributing

We welcome contributions! Please see our [Contributing Guide](./docs/contributing.md) for details.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
