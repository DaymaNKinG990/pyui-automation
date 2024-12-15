from typing import Dict, Any, Optional
from pathlib import Path


class AutomationConfig:
    """
    Configuration class for UI Automation

    This class provides a way to customize the behavior of UI Automation.
    The following configuration options are available:

    - `screenshot_dir`: Directory to save screenshots (default: None)
    - `timeout`: Default timeout for waiting (default: 10)
    - `retry_interval`: Interval between retries (default: 0.5)
    - `screenshot_on_error`: Capture screenshot on error (default: True)
    - `log_level`: Log level (default: 'INFO')
    - `poll_frequency`: Frequency of polling for element state changes (default: 0.1)

    Example:
        config = AutomationConfig()
        config.timeout = 20  # Set default timeout to 20 seconds
        config.screenshot_dir = '/path/to/screenshots'  # Set screenshot directory
    """

    def __init__(self) -> None:
        """
        Initialize configuration with default values
        
        - `screenshot_dir`: Directory to save screenshots (default: None)
        - `timeout`: Default timeout for waiting (default: 10)
        - `retry_interval`: Interval between retries (default: 0.5)
        - `screenshot_on_error`: Capture screenshot on error (default: True)
        - `log_level`: Log level (default: 'INFO')
        - `poll_frequency`: Frequency of polling for element state changes (default: 0.1)
        """
        self._config: Dict[str, Any] = {
            'screenshot_dir': None,
            'timeout': 10,
            'retry_interval': 0.5,
            'screenshot_on_error': True,
            'log_level': 'INFO',
            'poll_frequency': 0.1,
        }

    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value

        Args:
            key (str): Configuration key
            value (Any): Configuration value
        """
        self._config[key] = value

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value

        Args:
            key (str): Configuration key
            default (Any): Default value if key not found

        Returns:
            Any: Configuration value
        """
        return self._config.get(key, default)

    @property
    def screenshot_dir(self) -> Optional[Path]:
        """Get screenshot directory"""
        dir_path = self._config.get('screenshot_dir')
        return Path(dir_path) if dir_path else None

    @screenshot_dir.setter
    def screenshot_dir(self, path: str) -> None:
        """
        Set the screenshot directory path

        Args:
            path (str): The path to the directory where screenshots will be saved
        """
        self._config['screenshot_dir'] = path

    @property
    def timeout(self) -> float:
        """Get default timeout"""
        return float(self._config.get('timeout', 10))

    @timeout.setter
    def timeout(self, value: float) -> None:
        """
        Set default timeout

        Set the default timeout in seconds for all wait operations.
        """
        self._config['timeout'] = float(value)

    @property
    def retry_interval(self) -> float:
        """Get retry interval"""
        return float(self._config.get('retry_interval', 0.5))

    @retry_interval.setter
    def retry_interval(self, value: float) -> None:
        """Set retry interval"""
        self._config['retry_interval'] = float(value)

    @property
    def poll_frequency(self) -> float:
        """Get polling frequency"""
        return self._config['poll_frequency']

    @poll_frequency.setter
    def poll_frequency(self, value: float) -> None:
        """Set polling frequency"""
        self._config['poll_frequency'] = value
