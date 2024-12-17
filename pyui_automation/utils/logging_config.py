"""Конфигурация логирования."""

import logging
import logging.handlers
import os
from pathlib import Path
from typing import Optional

def setup_logging(log_dir: Optional[str] = None, level: int = logging.INFO) -> None:
    """
    Настройка логирования для приложения.
    
    Args:
        log_dir: Директория для файлов логов. Если не указана, используется директория logs в корне проекта.
        level: Уровень логирования.
    """
    if log_dir is None:
        log_dir = Path(__file__).parent.parent.parent / 'logs'
    
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
        Path(log_dir) / 'pyui_automation.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Отдельный файл для ошибок
    error_handler = logging.handlers.RotatingFileHandler(
        Path(log_dir) / 'errors.log',
        maxBytes=10*1024*1024,  # 10MB
        backupCount=5,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    root_logger.addHandler(error_handler)
