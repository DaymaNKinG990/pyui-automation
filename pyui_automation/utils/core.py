import time
from typing import Callable, Any
from pathlib import Path
import tempfile
import uuid


def retry(attempts: int = 3, delay: float = 1.0, exceptions: tuple = (Exception,)) -> Callable:
    """
    Retry decorator for functions that may fail.

    Args:
        attempts (int): Number of attempts to retry the function. Defaults to 3.
        delay (float): Delay between retries in seconds. Defaults to 1.0.
        exceptions (tuple): Exception types to catch and retry. Defaults to (Exception,).

    Returns:
        Callable: A decorator that applies the retry logic to the function.
    """
    if attempts <= 0:
        raise ValueError("attempts must be > 0")
    def decorator(func: Callable) -> Callable:
        def wrapper(*args, **kwargs) -> Any:
            for attempt in range(attempts):
                try:
                    return func(*args, **kwargs)
                except exceptions:
                    if attempt == attempts - 1:
                        raise
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

def get_temp_path(suffix: str = '') -> Path:
    """
    Get a unique temporary file path.

    Args:
        suffix (str): Optional suffix for the file name. Defaults to an empty string.

    Returns:
        Path: A Path object representing the temporary file path, with a unique name.
    """
    if not isinstance(suffix, str):
        raise TypeError("suffix must be a string")
    temp_dir = Path(tempfile.gettempdir())
    unique = uuid.uuid4().hex
    return temp_dir / f"pyui_automation_{time.time()}_{unique}{suffix}" 