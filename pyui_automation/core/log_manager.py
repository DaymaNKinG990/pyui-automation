"""
LogManager - Internal logging management for pyui-automation.

Provides controlled logging that can be disabled for library users.
"""

# Python libraries
import os
import logging
from typing import Optional, Dict, Any
from pathlib import Path


class LogManager:
    """
    Internal logging manager for pyui-automation.
    
    Features:
    - Controlled logging levels
    - Environment-based configuration
    - File and console logging
    - Disable logging for library users
    """
    
    _instance = None
    
    def __new__(cls) -> "LogManager":
        """Singleton pattern implementation"""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def __init__(self) -> None:
        """Initialize LogManager"""
        if hasattr(self, '_initialized'):
            return
            
        self._initialized = True
        self._loggers: Dict[str, logging.Logger] = {}
        self._log_level = self._get_log_level()
        self._log_file = self._get_log_file()
        self._console_enabled = self._get_console_enabled()
        
        # Configure root logger
        self._configure_root_logger()
    
    def _get_log_level(self) -> int:
        """Get log level from environment or default"""
        level_str = os.environ.get('PYUI_AUTOMATION_LOG_LEVEL', 'INFO').upper()
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL,
        }
        return level_map.get(level_str, logging.INFO)
    
    def _get_log_file(self) -> Optional[Path]:
        """Get log file path from environment"""
        log_file = os.environ.get('PYUI_AUTOMATION_LOG_FILE')
        if log_file:
            return Path(log_file)
        return None
    
    def _get_console_enabled(self) -> bool:
        """Check if console logging is enabled"""
        return os.environ.get('PYUI_AUTOMATION_CONSOLE_LOG', 'false').lower() == 'true'
    
    def _configure_root_logger(self) -> None:
        """Configure root logger with handlers"""
        root_logger = logging.getLogger('pyui_automation')
        root_logger.setLevel(self._log_level)
        
        # Clear existing handlers
        root_logger.handlers.clear()
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Add console handler if enabled
        if self._console_enabled:
            console_handler = logging.StreamHandler()
            console_handler.setLevel(self._log_level)
            console_handler.setFormatter(formatter)
            root_logger.addHandler(console_handler)
        
        # Add file handler if log file specified
        if self._log_file:
            try:
                # Ensure log directory exists
                self._log_file.parent.mkdir(parents=True, exist_ok=True)
                
                file_handler = logging.FileHandler(self._log_file)
                file_handler.setLevel(self._log_level)
                file_handler.setFormatter(formatter)
                root_logger.addHandler(file_handler)
            except Exception as e:
                # Fallback to console if file logging fails
                console_handler = logging.StreamHandler()
                console_handler.setLevel(logging.ERROR)
                console_handler.setFormatter(formatter)
                root_logger.addHandler(console_handler)
                root_logger.error(f"Failed to configure file logging: {e}")
    
    def get_logger(self, name: str) -> logging.Logger:
        """
        Get logger instance for specified name.
        
        Args:
            name: Logger name (usually module name)
            
        Returns:
            Configured logger instance
        """
        if name not in self._loggers:
            logger = logging.getLogger(f'pyui_automation.{name}')
            self._loggers[name] = logger
        
        return self._loggers[name]
    
    def set_log_level(self, level: int) -> None:
        """
        Set log level for all loggers.
        
        Args:
            level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        """
        self._log_level = level
        
        # Update root logger
        root_logger = logging.getLogger('pyui_automation')
        root_logger.setLevel(level)
        
        # Update all handlers
        for handler in root_logger.handlers:
            handler.setLevel(level)
        
        # Update cached loggers
        for logger in self._loggers.values():
            logger.setLevel(level)
    
    def enable_console_logging(self) -> None:
        """Enable console logging"""
        if not self._console_enabled:
            self._console_enabled = True
            self._configure_root_logger()
    
    def disable_console_logging(self) -> None:
        """Disable console logging"""
        if self._console_enabled:
            self._console_enabled = False
            self._configure_root_logger()
    
    def set_log_file(self, filepath: Path) -> None:
        """
        Set log file path.
        
        Args:
            filepath: Path to log file
        """
        self._log_file = filepath
        self._configure_root_logger()
    
    def clear_log_file(self) -> None:
        """Clear log file if it exists"""
        if self._log_file and self._log_file.exists():
            try:
                self._log_file.unlink()
            except Exception as e:
                root_logger = logging.getLogger('pyui_automation')
                root_logger.error(f"Failed to clear log file: {e}")
    
    def get_log_stats(self) -> Dict[str, Any]:
        """
        Get logging statistics.
        
        Returns:
            Dictionary with logging statistics
        """
        root_logger = logging.getLogger('pyui_automation')
        
        stats = {
            'log_level': self._log_level,
            'console_enabled': self._console_enabled,
            'log_file': str(self._log_file) if self._log_file else None,
            'handlers_count': len(root_logger.handlers),
            'loggers_count': len(self._loggers),
        }
        
        return stats


# Global instance
_log_manager = None


def get_log_manager() -> LogManager:
    """
    Get global LogManager instance.
    
    Returns:
        LogManager: Global log manager instance
    """
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager


def get_logger(name: str) -> logging.Logger:
    """
    Get logger instance using global LogManager.
    
    Args:
        name: Logger name
        
    Returns:
        Configured logger instance
    """
    return get_log_manager().get_logger(name)


def configure_logging(
    level: Optional[int] = None,
    console: Optional[bool] = None,
    filepath: Optional[Path] = None
) -> None:
    """
    Configure logging globally.
    
    Args:
        level: Logging level
        console: Enable/disable console logging
        filepath: Log file path
    """
    manager = get_log_manager()
    
    if level is not None:
        manager.set_log_level(level)
    
    if console is not None:
        if console:
            manager.enable_console_logging()
        else:
            manager.disable_console_logging()
    
    if filepath is not None:
        manager.set_log_file(filepath)


def disable_logging() -> None:
    """Disable all logging for library users"""
    manager = get_log_manager()
    manager.set_log_level(logging.CRITICAL)  # Only critical errors
    manager.disable_console_logging()


def enable_logging() -> None:
    """Enable logging for development"""
    manager = get_log_manager()
    manager.set_log_level(logging.DEBUG)
    manager.enable_console_logging() 