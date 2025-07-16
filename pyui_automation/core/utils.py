import time
from typing import Callable, Any, Optional
from pathlib import Path
import tempfile
import cv2
import numpy as np
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

def ensure_dir(path: Path) -> Path:
    """
    Ensure directory exists.

    Args:
        path (Path): The directory path to ensure.

    Returns:
        Path: The ensured directory path.
    """
    path.mkdir(parents=True, exist_ok=True)
    return path

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

def save_image(image: np.ndarray, filepath: str) -> None:
    """
    Save image to file.

    Args:
        image (np.ndarray): The image data to save.
        filepath (str): The file path to save the image to.
    """
    cv2.imwrite(str(filepath), image)

def load_image(filepath: str) -> Optional[np.ndarray]:
    """
    Load image from file.

    Args:
        filepath (str): The file path to load the image from.

    Returns:
        Optional[np.ndarray]: The loaded image as a numpy array, or None if loading fails.
    """
    try:
        return cv2.imread(str(filepath))
    except Exception:
        return None

def compare_images(img1: np.ndarray, img2: np.ndarray, threshold: float = 0.95) -> bool:
    """
    Compare two images for similarity.

    Args:
        img1 (np.ndarray): The first image to compare.
        img2 (np.ndarray): The second image to compare.
        threshold (float, optional): The minimum similarity score required for the comparison to return True. Defaults to 0.95.

    Returns:
        bool: True if the images are similar (i.e., the similarity score is greater than or equal to the threshold), False otherwise.
    """
    if img1.shape != img2.shape:
        return False
    # Convert images to grayscale
    if len(img1.shape) == 3:
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    else:
        img1_gray = img1
        img2_gray = img2
    # Calculate normalized mean absolute difference
    diff = img1_gray.astype(float) - img2_gray.astype(float)
    mse = np.mean(np.abs(diff))
    similarity = 1.0 - (mse / 255.0)
    return bool(similarity >= threshold)
