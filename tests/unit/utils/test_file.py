"""
Tests for file utilities
"""
import pytest
import tempfile
import shutil
from pathlib import Path

from pyui_automation.utils.file import (
    ensure_dir,
    get_temp_dir,
    safe_remove,
    get_temp_file,
    copy_file,
    move_file,
    get_file_size,
    is_file_empty,
    list_files
)


class TestFileUtils:
    """Test file utility functions"""
    
    def test_ensure_dir(self, tmp_path):
        """Test ensure_dir function"""
        new_dir = tmp_path / "test_dir"
        result = ensure_dir(new_dir)
        assert result == new_dir
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_ensure_dir_nested(self, tmp_path):
        """Test ensure_dir with nested directories"""
        nested_dir = tmp_path / "parent" / "child" / "grandchild"
        result = ensure_dir(nested_dir)
        assert result == nested_dir
        assert nested_dir.exists()
        assert nested_dir.is_dir()
    
    def test_get_temp_dir(self):
        """Test get_temp_dir function"""
        temp_dir = get_temp_dir()
        assert isinstance(temp_dir, Path)
        assert temp_dir.exists()
        assert temp_dir.is_dir()
    
    def test_safe_remove_file(self, tmp_path):
        """Test safe_remove with file"""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")
        
        result = safe_remove(test_file)
        assert result is True
        assert not test_file.exists()
    
    def test_safe_remove_directory(self, tmp_path):
        """Test safe_remove with directory"""
        test_dir = tmp_path / "test_dir"
        test_dir.mkdir()
        (test_dir / "test_file.txt").write_text("test content")
        
        result = safe_remove(test_dir)
        assert result is True
        assert not test_dir.exists()
    
    def test_safe_remove_nonexistent(self, tmp_path):
        """Test safe_remove with nonexistent path"""
        nonexistent = tmp_path / "nonexistent"
        result = safe_remove(nonexistent)
        assert result is False
    
    def test_get_temp_file(self):
        """Test get_temp_file function"""
        temp_file = get_temp_file(suffix=".txt", prefix="test")
        assert isinstance(temp_file, Path)
        assert temp_file.suffix == ".txt"
        assert temp_file.name.startswith("test")
    
    def test_copy_file(self, tmp_path):
        """Test copy_file function"""
        source = tmp_path / "source.txt"
        source.write_text("test content")
        destination = tmp_path / "destination.txt"
        
        result = copy_file(source, destination)
        assert result is True
        assert destination.exists()
        assert destination.read_text() == "test content"
    
    def test_copy_file_nonexistent_source(self, tmp_path):
        """Test copy_file with nonexistent source"""
        source = tmp_path / "nonexistent.txt"
        destination = tmp_path / "destination.txt"
        
        result = copy_file(source, destination)
        assert result is False
    
    def test_copy_file_overwrite(self, tmp_path):
        """Test copy_file with overwrite"""
        source = tmp_path / "source.txt"
        source.write_text("new content")
        destination = tmp_path / "destination.txt"
        destination.write_text("old content")
        
        result = copy_file(source, destination, overwrite=True)
        assert result is True
        assert destination.read_text() == "new content"
    
    def test_copy_file_no_overwrite(self, tmp_path):
        """Test copy_file without overwrite"""
        source = tmp_path / "source.txt"
        source.write_text("new content")
        destination = tmp_path / "destination.txt"
        destination.write_text("old content")
        
        result = copy_file(source, destination, overwrite=False)
        assert result is False
        assert destination.read_text() == "old content"
    
    def test_move_file(self, tmp_path):
        """Test move_file function"""
        source = tmp_path / "source.txt"
        source.write_text("test content")
        destination = tmp_path / "destination.txt"
        
        result = move_file(source, destination)
        assert result is True
        assert not source.exists()
        assert destination.exists()
        assert destination.read_text() == "test content"
    
    def test_move_file_nonexistent_source(self, tmp_path):
        """Test move_file with nonexistent source"""
        source = tmp_path / "nonexistent.txt"
        destination = tmp_path / "destination.txt"
        
        result = move_file(source, destination)
        assert result is False
    
    def test_get_file_size(self, tmp_path):
        """Test get_file_size function"""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")
        
        size = get_file_size(test_file)
        assert size == len("test content")
    
    def test_get_file_size_nonexistent(self, tmp_path):
        """Test get_file_size with nonexistent file"""
        nonexistent = tmp_path / "nonexistent.txt"
        size = get_file_size(nonexistent)
        assert size is None
    
    def test_is_file_empty(self, tmp_path):
        """Test is_file_empty function"""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")
        
        non_empty_file = tmp_path / "non_empty.txt"
        non_empty_file.write_text("content")
        
        assert is_file_empty(empty_file) is True
        assert is_file_empty(non_empty_file) is False
    
    def test_is_file_empty_nonexistent(self, tmp_path):
        """Test is_file_empty with nonexistent file"""
        nonexistent = tmp_path / "nonexistent.txt"
        assert is_file_empty(nonexistent) is True
    
    def test_list_files(self, tmp_path):
        """Test list_files function"""
        # Create test files
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "file3.py").write_text("content3")
        (tmp_path / "subdir").mkdir()
        
        # Test listing all files
        files = list_files(tmp_path)
        assert len(files) == 3
        assert any(f.name == "file1.txt" for f in files)
        assert any(f.name == "file2.txt" for f in files)
        assert any(f.name == "file3.py" for f in files)
        
        # Test listing with pattern
        txt_files = list_files(tmp_path, "*.txt")
        assert len(txt_files) == 2
        assert all(f.suffix == ".txt" for f in txt_files)
    
    def test_list_files_nonexistent_directory(self, tmp_path):
        """Test list_files with nonexistent directory"""
        nonexistent = tmp_path / "nonexistent"
        files = list_files(nonexistent)
        assert files == [] 