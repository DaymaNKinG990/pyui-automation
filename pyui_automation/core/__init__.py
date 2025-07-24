"""
Core module for pyui-automation.

Provides central management components and session handling.
"""

from .di_manager import (
    DIAutomationManager,
    create_session,
    cleanup as cleanup_manager,
)

from .log_manager import (
    LogManager,
    get_log_manager,
    get_logger,
    configure_logging,
    disable_logging,
    enable_logging,
)

from .session import AutomationSession
from .application import Application
from .exceptions import (
    AutomationError, ElementNotFoundError, ElementStateError, TimeoutError,
    BackendError, ConfigurationError, ValidationError, OCRError, VisualError,
    InputError, WindowError, WaitTimeout
)
from .optimization import OptimizationManager
from .wait import wait_until
from .logging import AutomationLogger, setup_logging, logger


__all__ = [
    # Manager
    "DIAutomationManager",
    "create_session",
    "cleanup_manager",
    
    # Logging
    "LogManager",
    "get_log_manager", 
    "get_logger",
    "configure_logging",
    "disable_logging",
    "enable_logging",
    
    # Session
    "AutomationSession",
    
    # Application
    "Application",
    
    # Exceptions
    "AutomationError",
    "ElementNotFoundError", 
    "ElementStateError",
    "TimeoutError",
    "BackendError",
    "ConfigurationError",
    "ValidationError",
    "OCRError",
    "VisualError",
    "InputError",
    "WindowError",
    "WaitTimeout",
    
    # Optimization
    "OptimizationManager",
    
    # Wait
    "wait_until",
    
    # Logging
    "AutomationLogger",
    "setup_logging",
    "logger"
]
