import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional


class AutomationLogger:
    """
    Logger for UI Automation.

    Унифицированный логгер для всей библиотеки. Поддерживает вывод в консоль и файл, настройку уровня логирования.
    Используется во всех сервисах и компонентах.

    Example usage:
        from pyui_automation.core.logging import logger
        logger.info("Start automation")
        logger.error("Something went wrong")
        logger.add_file_handler("automation.log")

    Назначение:
        - Централизованный лог
        - Гибкая настройка вывода
        - Использование во всех слоях
    """
    
    def __init__(self, name: str = 'pyui_automation') -> None:
        """
        Initialize the AutomationLogger.
        
        Args:
            name: The name of the logger. Defaults to 'pyui_automation'.
        """
        self._logger = logging.getLogger(name)
        self._logger.setLevel(logging.DEBUG)  # Set to DEBUG by default
        self._setup_console_handler()

    def _setup_console_handler(self) -> None:
        """
        Setup console handler
        
        This method sets up the console handler for the logger. The handler is
        configured to write to sys.stdout and logs messages at the DEBUG level.
        The format of the logs is:
        
        %(levelname)-8s %(name)s:%(filename)s:%(lineno)d %(message)s
        
        This method also removes any existing handlers to avoid duplicates.
        """
        handler = logging.StreamHandler(sys.stdout)
        handler.setLevel(logging.DEBUG)  # Set handler to DEBUG
        formatter = logging.Formatter(
            '%(levelname)-8s %(name)s:%(filename)s:%(lineno)d %(message)s'
        )
        handler.setFormatter(formatter)
        # Remove existing handlers to avoid duplicates
        self._logger.handlers.clear()
        self._logger.addHandler(handler)

    def add_file_handler(self, filepath: Path) -> None:
        """
        Add file handler
        
        This method adds a file handler to the logger. The handler will write
        log messages to the specified file. The format of the logs will be:
        
        %(asctime)s - %(name)s - %(levelname)s - %(message)s
        
        The level of the handler is set to DEBUG, and the formatter is set to
        include the timestamp, logger name, log level, and message.
        
        Args:
            filepath: The path to the file where the logs will be written.
        """
        handler = logging.FileHandler(str(filepath))
        handler.setLevel(logging.DEBUG)  # Set handler to DEBUG
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        handler.setFormatter(formatter)
        self._logger.addHandler(handler)

    def set_level(self, level: int) -> None:
        """
        Set the logging level for the logger and all its handlers.

        Args:
            level: The logging level to set. This should be one of the standard
                   logging levels like logging.DEBUG, logging.INFO, etc.
        """
        self._logger.setLevel(level)
        for handler in self._logger.handlers:
            handler.setLevel(level)

    def debug(self, msg: str) -> None:
        """
        Log debug message

        Args:
            msg: The message to log
        """
        self._logger.debug(msg)

    def info(self, msg: str) -> None:
        """
        Log info message

        Args:
            msg: The message to log
        """
        self._logger.info(msg)

    def warning(self, msg: str) -> None:
        """
        Log warning message

        Args:
            msg: The message to log
        """
        self._logger.warning(msg)

    def error(self, msg: str) -> None:
        """
        Log error message

        Args:
            msg: The message to log
        """
        self._logger.error(msg)

    def critical(self, msg: str) -> None:
        """
        Log critical message

        Args:
            msg: The message to log
        """
        self._logger.critical(msg)

    def exception(self, msg: str) -> None:
        """
        Log exception message

        Args:
            msg: The message to log
        """
        self._logger.exception(msg)


def setup_logging(log_dir: Optional[str] = None, level: int = logging.INFO) -> None:
    """
    Setup logging configuration for the application.
    
    Args:
        log_dir: Directory for log files. If None, uses logs directory in project root.
        level: Logging level.
    """
    if log_dir is None:
        log_dir = str(Path(__file__).parent.parent.parent / 'logs')
    
    os.makedirs(log_dir, exist_ok=True)
    
    # Основной форматтер для логов
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Настройка корневого логгера
    root_logger = logging.getLogger()
    root_logger.setLevel(level)
    
    # Хендлер для консоли
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Хендлер для файла
    file_handler = logging.handlers.RotatingFileHandler(
        str(Path(log_dir) / 'pyui_automation.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Отдельный файл для ошибок
    error_handler = logging.handlers.RotatingFileHandler(
        str(Path(log_dir) / 'errors.log'),
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)


# Global logger instance
logger = AutomationLogger() 