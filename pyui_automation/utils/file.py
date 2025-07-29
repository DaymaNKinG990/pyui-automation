import shutil
import tempfile
import os
from pathlib import Path
from typing import Optional, List, Union


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

def safe_remove(path: Path) -> bool:
    """
    Safely remove file or directory.

    Args:
        path (Path): The file or directory path to remove.

    Returns:
        bool: True if removal was successful, False otherwise.
    """
    try:
        if not path.exists():
            return False
        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        return True
    except Exception:
        return False


def get_temp_file(suffix: str = "", prefix: str = "tmp") -> Path:
    """
    Get a temporary file path.
    
    Args:
        suffix: File suffix/extension
        prefix: File prefix
        
    Returns:
        Path to temporary file
    """
    fd, path = tempfile.mkstemp(suffix=suffix, prefix=prefix)
    os.close(fd)  # Close the file descriptor
    return Path(path)


def copy_file(src: Union[str, Path], dst: Union[str, Path], overwrite: bool = True) -> bool:
    """
    Copy file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        overwrite: Whether to overwrite existing file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            return False
            
        if dst_path.exists() and not overwrite:
            return False
            
        # Ensure destination directory exists
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.copy2(src_path, dst_path)
        return True
        
    except Exception:
        return False


def move_file(src: Union[str, Path], dst: Union[str, Path], overwrite: bool = True) -> bool:
    """
    Move file from source to destination.
    
    Args:
        src: Source file path
        dst: Destination file path
        overwrite: Whether to overwrite existing file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        src_path = Path(src)
        dst_path = Path(dst)
        
        if not src_path.exists():
            return False
            
        if dst_path.exists() and not overwrite:
            return False
            
        # Ensure destination directory exists
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        
        shutil.move(str(src_path), str(dst_path))
        return True
        
    except Exception:
        return False


def get_file_size(path: Union[str, Path]) -> Optional[int]:
    """
    Get file size in bytes.
    
    Args:
        path: File path
        
    Returns:
        File size in bytes or None if file doesn't exist
    """
    try:
        file_path = Path(path)
        if file_path.exists() and file_path.is_file():
            return file_path.stat().st_size
        return None
    except Exception:
        return None


def is_file_empty(path: Union[str, Path]) -> bool:
    """
    Check if file is empty.
    
    Args:
        path: File path
        
    Returns:
        True if file is empty or doesn't exist, False otherwise
    """
    try:
        file_path = Path(path)
        if not file_path.exists():
            return True
        if file_path.is_file():
            return file_path.stat().st_size == 0
        return True
    except Exception:
        return True


def list_files(directory: Union[str, Path], pattern: str = "*") -> List[Path]:
    """
    List files in directory matching pattern.
    
    Args:
        directory: Directory path
        pattern: Glob pattern to match files
        
    Returns:
        List of file paths
    """
    try:
        dir_path = Path(directory)
        if not dir_path.exists() or not dir_path.is_dir():
            return []
            
        files: List[Path] = []
        for file_path in dir_path.glob(pattern):
            if file_path.is_file():
                files.append(file_path)
                
        return files
        
    except Exception:
        return []
