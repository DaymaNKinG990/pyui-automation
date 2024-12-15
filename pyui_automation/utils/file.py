import os
import shutil
import tempfile
from pathlib import Path
from typing import Optional, List


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

def get_temp_dir() -> Path:
    """Get temporary directory"""
    return Path(tempfile.gettempdir())

def get_temp_file(suffix: str = '') -> Path:
    """
    Get temporary file path

    Args:
        suffix (str): Optional suffix for the file name

    Returns:
        Path: A Path object representing the temporary file path
    """
    return Path(tempfile.mktemp(suffix=suffix))

def safe_remove(path: Path) -> bool:
    """
    Safely remove file or directory.

    Args:
        path (Path): The file or directory path to remove.

    Returns:
        bool: True if removal was successful, False otherwise.
    """
    try:
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        return True
    except Exception:
        return False

def list_files(directory: Path, pattern: str = '*') -> List[Path]:
    """
    List files in directory matching pattern.

    Args:
        directory (Path): The directory to list files from.
        pattern (str): The glob pattern to use for matching files.

    Returns:
        List[Path]: A list of Path objects representing the matching files.
    """
    return list(directory.glob(pattern))

def copy_file(src: Path, dst: Path, overwrite: bool = False) -> bool:
    """
    Copy file from source to destination with optional overwrite.

    Args:
        src (Path): The path to the source file.
        dst (Path): The path to the destination file.
        overwrite (bool): Whether to overwrite the destination file if it exists. Defaults to False.

    Returns:
        bool: True if the file was copied successfully, False otherwise.
    """
    try:
        if dst.exists() and not overwrite:
            return False
        shutil.copy2(src, dst)
        return True
    except Exception:
        return False

def move_file(src: Path, dst: Path, overwrite: bool = False) -> bool:
    """
    Move file from source to destination with optional overwrite.

    Args:
        src (Path): The path to the source file.
        dst (Path): The path to the destination file.
        overwrite (bool): Whether to overwrite the destination file if it exists. Defaults to False.

    Returns:
        bool: True if the file was moved successfully, False otherwise.
    """
    try:
        if dst.exists() and not overwrite:
            return False
        shutil.move(src, dst)
        return True
    except Exception:
        return False

def get_file_size(path: Path) -> Optional[int]:
    """
    Get file size in bytes.

    Args:
        path (Path): The path to the file.

    Returns:
        Optional[int]: The size of the file in bytes, or None if the file does not exist.
    """
    try:
        return path.stat().st_size
    except Exception:
        return None

def is_file_empty(path: Path) -> bool:
    """
    Check if file is empty.

    Args:
        path (Path): The path to the file to check.

    Returns:
        bool: True if the file is empty, False otherwise.
    """
    size = get_file_size(path)
    return size == 0 if size is not None else True
