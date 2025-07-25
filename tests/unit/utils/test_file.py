"""
Tests for file utilities
"""
import pytest
import tempfile
import json
import yaml
from pathlib import Path

from pyui_automation.utils.file import (
    FileUtils, PathUtils, FileManager
)


class TestFileFunctions:
    """Tests for file utility functions"""
    
    def test_ensure_dir(self, tmp_path):
        """Test ensure_dir function"""
        new_dir = tmp_path / "test_directory"
        
        result = FileUtils.ensure_dir(new_dir)
        
        assert result == new_dir
        assert new_dir.exists()
        assert new_dir.is_dir()
    
    def test_ensure_dir_already_exists(self, tmp_path):
        """Test ensure_dir when directory already exists"""
        existing_dir = tmp_path / "existing_directory"
        existing_dir.mkdir()
        
        result = FileUtils.ensure_dir(existing_dir)
        
        assert result == existing_dir
        assert existing_dir.exists()
    
    def test_get_temp_dir(self):
        """Test get_temp_dir function"""
        temp_dir = FileUtils.get_temp_dir()
        
        assert isinstance(temp_dir, Path)
        assert temp_dir.exists()
        assert temp_dir.is_dir()
    
    def test_safe_remove_file(self, tmp_path):
        """Test safe_remove with file"""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")
        
        result = FileUtils.safe_remove(test_file)
        
        assert result is True
        assert not test_file.exists()
    
    def test_safe_remove_directory(self, tmp_path):
        """Test safe_remove with directory"""
        test_dir = tmp_path / "test_directory"
        test_dir.mkdir()
        (test_dir / "test_file.txt").write_text("test content")
        
        result = FileUtils.safe_remove(test_dir)
        
        assert result is True
        assert not test_dir.exists()
    
    def test_safe_remove_not_exists(self, tmp_path):
        """Test safe_remove with non-existent path"""
        non_existent = tmp_path / "non_existent.txt"
        
        result = FileUtils.safe_remove(non_existent)
        
        assert result is False
    
    def test_get_temp_file(self):
        """Test get_temp_file function"""
        temp_file = FileUtils.get_temp_file(suffix=".txt", prefix="test_")
        
        assert isinstance(temp_file, Path)
        assert temp_file.name.startswith("test_")
        assert temp_file.name.endswith(".txt")
    
    def test_copy_file(self, tmp_path):
        """Test copy_file function"""
        source_file = tmp_path / "source.txt"
        target_file = tmp_path / "target.txt"
        source_file.write_text("test content")
        
        result = FileUtils.copy_file(source_file, target_file)
        
        assert result is True
        assert target_file.exists()
        assert target_file.read_text() == "test content"
    
    def test_copy_file_not_exists(self, tmp_path):
        """Test copy_file with non-existent source"""
        source_file = tmp_path / "source.txt"
        target_file = tmp_path / "target.txt"
        
        result = FileUtils.copy_file(source_file, target_file)
        
        assert result is False
        assert not target_file.exists()
    
    def test_move_file(self, tmp_path):
        """Test move_file function"""
        source_file = tmp_path / "source.txt"
        target_file = tmp_path / "target.txt"
        source_file.write_text("test content")
        
        result = FileUtils.move_file(source_file, target_file)
        
        assert result is True
        assert not source_file.exists()
        assert target_file.exists()
        assert target_file.read_text() == "test content"
    
    def test_get_file_size(self, tmp_path):
        """Test get_file_size function"""
        test_file = tmp_path / "test_file.txt"
        test_file.write_text("test content")
        
        size = FileUtils.get_file_size(test_file)
        
        assert size is not None
        assert size > 0
    
    def test_get_file_size_not_exists(self, tmp_path):
        """Test get_file_size with non-existent file"""
        non_existent = tmp_path / "non_existent.txt"
        
        size = FileUtils.get_file_size(non_existent)
        
        assert size is None
    
    def test_is_file_empty(self, tmp_path):
        """Test is_file_empty function"""
        empty_file = tmp_path / "empty.txt"
        empty_file.write_text("")
        
        non_empty_file = tmp_path / "non_empty.txt"
        non_empty_file.write_text("content")
        
        assert FileUtils.is_file_empty(empty_file) is True
        assert FileUtils.is_file_empty(non_empty_file) is False
    
    def test_list_files(self, tmp_path):
        """Test list_files function"""
        # Create test files
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "file3.py").write_text("content3")
        
        files = FileUtils.list_files(tmp_path)
        
        assert len(files) == 3
        assert all(f.name in ["file1.txt", "file2.txt", "file3.py"] for f in files)
    
    def test_list_files_with_pattern(self, tmp_path):
        """Test list_files with pattern"""
        # Create test files
        (tmp_path / "file1.txt").write_text("content1")
        (tmp_path / "file2.txt").write_text("content2")
        (tmp_path / "file3.py").write_text("content3")
        
        txt_files = FileUtils.list_files(tmp_path, "*.txt")
        
        assert len(txt_files) == 2
        assert all(f.name.endswith(".txt") for f in txt_files) 