"""
Tests for visual testing functionality
"""
import pytest
import numpy as np

from pyui_automation.core.visual import VisualMatcher, VisualTester, VisualDifference


class TestVisualMatcher:
    """Test VisualMatcher class"""
    
    def test_init(self, mocker):
        """Test VisualMatcher initialization"""
        mock_element = mocker.Mock()
        matcher = VisualMatcher(mock_element, similarity_threshold=0.9)
        assert matcher.element == mock_element
        assert matcher.similarity_threshold == 0.9
    
    def test_set_similarity_threshold(self, mocker):
        """Test set_similarity_threshold method"""
        mock_element = mocker.Mock()
        matcher = VisualMatcher(mock_element)
        matcher.set_similarity_threshold(0.8)
        assert matcher.similarity_threshold == 0.8
    
    def test_set_similarity_threshold_invalid(self, mocker):
        """Test set_similarity_threshold with invalid value"""
        mock_element = mocker.Mock()
        matcher = VisualMatcher(mock_element)
        with pytest.raises(ValueError):
            matcher.set_similarity_threshold(1.5)
    
    def test_compare_images(self, mocker):
        """Test compare_images method"""
        mock_element = mocker.Mock()
        matcher = VisualMatcher(mock_element)
        
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((100, 100, 3), dtype=np.uint8)
        
        similarity = matcher.compare_images(img1, img2)
        assert similarity == 1.0
    
    def test_compare_images_different_sizes(self, mocker):
        """Test compare_images with different sizes"""
        mock_element = mocker.Mock()
        matcher = VisualMatcher(mock_element)
        
        img1 = np.zeros((100, 100, 3), dtype=np.uint8)
        img2 = np.zeros((200, 200, 3), dtype=np.uint8)
        
        similarity = matcher.compare_images(img1, img2)
        assert similarity == 0.0


class TestVisualTester:
    """Test VisualTester class"""
    
    def test_init(self, tmp_path):
        """Test VisualTester initialization"""
        tester = VisualTester(tmp_path, threshold=0.9)
        assert tester.baseline_dir == tmp_path
        assert tester.similarity_threshold == 0.9
        assert tester.threshold == 0.9
    
    def test_capture_baseline(self, tmp_path):
        """Test capture_baseline method"""
        tester = VisualTester(tmp_path)
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = tester.capture_baseline("test", image)
        assert result is True
        assert (tmp_path / "test.png").exists()
    
    def test_capture_baseline_empty_name(self, tmp_path):
        """Test capture_baseline with empty name"""
        tester = VisualTester(tmp_path)
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with pytest.raises(ValueError):
            tester.capture_baseline("", image)
    
    def test_capture_baseline_invalid_image(self, tmp_path):
        """Test capture_baseline with invalid image"""
        tester = VisualTester(tmp_path)
        
        with pytest.raises(ValueError):
            tester.capture_baseline("test", np.array([]))
    
    def test_read_baseline(self, tmp_path):
        """Test read_baseline method"""
        tester = VisualTester(tmp_path)
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        tester.capture_baseline("test", image)
        
        result = tester.read_baseline("test")
        assert result is not None
        assert result.shape == (100, 100, 3)
    
    def test_read_baseline_not_found(self, tmp_path):
        """Test read_baseline with non-existent baseline"""
        tester = VisualTester(tmp_path)
        
        with pytest.raises(FileNotFoundError):
            tester.read_baseline("nonexistent")
    
    def test_compare_with_baseline(self, tmp_path):
        """Test compare_with_baseline method"""
        tester = VisualTester(tmp_path)
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        tester.capture_baseline("test", image)
        
        match, similarity = tester.compare_with_baseline("test", image)
        assert match is True
        assert similarity == 1.0
    
    def test_set_similarity_threshold(self, tmp_path):
        """Test set_similarity_threshold method"""
        tester = VisualTester(tmp_path)
        tester.set_similarity_threshold(0.8)
        assert tester.similarity_threshold == 0.8
    
    def test_set_similarity_threshold_invalid(self, tmp_path):
        """Test set_similarity_threshold with invalid value"""
        tester = VisualTester(tmp_path)
        with pytest.raises(ValueError):
            tester.set_similarity_threshold(1.5)


class TestVisualDifference:
    """Test VisualDifference dataclass"""
    
    def test_visual_difference_creation(self):
        """Test VisualDifference creation"""
        diff = VisualDifference(
            location=(10, 20),
            size=(30, 40),
            difference_percentage=15.5,
            type="changed"
        )
        assert diff.location == (10, 20)
        assert diff.size == (30, 40)
        assert diff.difference_percentage == 15.5
        assert diff.type == "changed" 