"""PyUI Automation package for UI test automation"""

from .core.session import AutomationSession
from .core.visual import VisualTester, VisualMatcher, VisualDifference
from .elements import UIElement, Button, Window, Input
from .utils import (
    load_image, save_image, resize_image, compare_images, find_template, highlight_region, crop_image,
    ensure_dir, get_temp_dir, get_temp_file, safe_remove, list_files, copy_file, move_file, get_file_size, is_file_empty,
    validate_type, validate_not_none, validate_string_not_empty, validate_number_range, validate_regex, validate_callable,
    validate_iterable, validate_all, validate_any
)
from .logging import logger
from .exceptions import (
    AutomationError, ElementNotFoundError, ElementStateError, TimeoutError, BackendError, ConfigurationError,
    ValidationError, OCRError, VisualError, InputError, WindowError, WaitTimeout
)
from .di import container
from .wait import ElementWaits
from . import services

__version__ = "0.1.0"
__all__ = [
    'AutomationSession',
    'VisualTester',
    'VisualMatcher',
    'VisualDifference',
    'UIElement',
    'Button',
    'Window',
    'Input',
    'logger',
    'container',
    'ElementWaits',
    'services',
    'load_image', 'save_image', 'resize_image', 'compare_images', 'find_template', 'highlight_region', 'crop_image',
    'ensure_dir', 'get_temp_dir', 'get_temp_file', 'safe_remove', 'list_files', 'copy_file', 'move_file', 'get_file_size', 'is_file_empty',
    'validate_type', 'validate_not_none', 'validate_string_not_empty', 'validate_number_range', 'validate_regex', 'validate_callable',
    'validate_iterable', 'validate_all', 'validate_any',
    'AutomationError', 'ElementNotFoundError', 'ElementStateError', 'TimeoutError', 'BackendError', 'ConfigurationError',
    'ValidationError', 'OCRError', 'VisualError', 'InputError', 'WindowError', 'WaitTimeout'
]
