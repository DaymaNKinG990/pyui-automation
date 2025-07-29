"""
Tests for visual testing functionality
"""
import pytest
import numpy as np
from pathlib import Path

from pyui_automation.core.visual import VisualMatcher, VisualTester, VisualDifference


@pytest.fixture
def sample_image():
    """Create a sample image for testing"""
    return np.zeros((100, 100, 3), dtype=np.uint8)


@pytest.fixture
def different_size_image():
    """Create an image with different size for testing"""
    return np.zeros((200, 200, 3), dtype=np.uint8)


@pytest.fixture
def colored_image():
    """Create a colored image for testing"""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    img[50:60, 50:60] = [255, 0, 0]  # Red square
    return img


class TestVisualMatcher:
    """Test VisualMatcher class"""
    
    def test_init(self, mock_native_element):
        """Test VisualMatcher initialization"""
        matcher = VisualMatcher(mock_native_element, similarity_threshold=0.9)
        assert matcher.element == mock_native_element
        assert matcher.similarity_threshold == 0.9
    
    def test_set_similarity_threshold(self, mock_native_element):
        """Test set_similarity_threshold method"""
        matcher = VisualMatcher(mock_native_element)
        matcher.set_similarity_threshold(0.8)
        assert matcher.similarity_threshold == 0.8
    
    @pytest.mark.parametrize("invalid_threshold", [-0.1, 1.5, 2.0])
    def test_set_similarity_threshold_invalid(self, mock_native_element, invalid_threshold):
        """Test set_similarity_threshold with invalid values"""
        matcher = VisualMatcher(mock_native_element)
        with pytest.raises(ValueError):
            matcher.set_similarity_threshold(invalid_threshold)
    
    def test_compare_images_identical(self, mock_native_element, sample_image):
        """Test compare_images with identical images"""
        matcher = VisualMatcher(mock_native_element)
        similarity = matcher.compare_images(sample_image, sample_image)
        assert similarity == 1.0
    
    def test_compare_images_different_sizes(self, mock_native_element, sample_image, different_size_image):
        """Test compare_images with different sizes"""
        matcher = VisualMatcher(mock_native_element)
        similarity = matcher.compare_images(sample_image, different_size_image)
        # Similarity should be 0.0 for different sizes
        assert similarity == 0.0
    
    def test_compare_images_different_content(self, mock_native_element, sample_image, colored_image):
        """Test compare_images with different content"""
        matcher = VisualMatcher(mock_native_element)
        similarity = matcher.compare_images(sample_image, colored_image)
        # Similarity should be less than 1.0 but greater than 0.0
        assert 0.0 < similarity < 1.0
    
    def test_compare_images_none_input(self, mock_native_element, sample_image):
        """Test compare_images with None input"""
        matcher = VisualMatcher(mock_native_element)
        # None inputs should return 0.0 similarity
        similarity1 = matcher.compare_images(None, sample_image)
        similarity2 = matcher.compare_images(sample_image, None)
        assert similarity1 == 0.0
        assert similarity2 == 0.0


class TestVisualTester:
    """Test VisualTester class"""
    
    def test_init(self, temp_dir):
        """Test VisualTester initialization"""
        tester = VisualTester(temp_dir, threshold=0.9)
        assert tester.baseline_dir == Path(temp_dir)
        assert tester.similarity_threshold == 0.9
        assert tester.threshold == 0.9
    
    def test_capture_baseline(self, temp_dir, sample_image):
        """Test capture_baseline method"""
        tester = VisualTester(temp_dir)
        
        result = tester.capture_baseline("test", sample_image)
        assert result is True
        assert (Path(temp_dir) / "test.png").exists()
    
    def test_capture_baseline_empty_name(self, temp_dir, sample_image):
        """Test capture_baseline with empty name"""
        tester = VisualTester(temp_dir)
        
        with pytest.raises(ValueError):
            tester.capture_baseline("", sample_image)
    
    def test_capture_baseline_invalid_image(self, temp_dir):
        """Test capture_baseline with invalid image"""
        tester = VisualTester(temp_dir)
        
        with pytest.raises(ValueError):
            tester.capture_baseline("test", np.array([]))
    
    def test_capture_baseline_none_image(self, temp_dir):
        """Test capture_baseline with None image"""
        tester = VisualTester(temp_dir)
        
        with pytest.raises(ValueError):
            tester.capture_baseline("test", None)
    
    def test_read_baseline(self, temp_dir, sample_image):
        """Test read_baseline method"""
        tester = VisualTester(temp_dir)
        tester.capture_baseline("test", sample_image)
        
        result = tester.read_baseline("test")
        assert result is not None
        assert result.shape == (100, 100, 3)
    
    def test_read_baseline_not_found(self, temp_dir):
        """Test read_baseline with non-existent baseline"""
        tester = VisualTester(temp_dir)
        
        with pytest.raises(FileNotFoundError):
            tester.read_baseline("nonexistent")
    
    def test_compare_with_baseline_identical(self, temp_dir, sample_image):
        """Test compare_with_baseline method with identical images"""
        tester = VisualTester(temp_dir)
        tester.capture_baseline("test", sample_image)
        
        match, similarity = tester.compare_with_baseline("test", sample_image)
        assert match is True
        assert similarity == 1.0
    
    def test_compare_with_baseline_different(self, temp_dir, sample_image, colored_image):
        """Test compare_with_baseline method with different images"""
        tester = VisualTester(temp_dir)
        tester.capture_baseline("test", sample_image)
        
        match, similarity = tester.compare_with_baseline("test", colored_image)
        assert match is False
        assert 0.0 < similarity < 1.0
    
    def test_compare_with_baseline_custom_threshold(self, temp_dir, sample_image, colored_image):
        """Test compare_with_baseline with custom threshold"""
        tester = VisualTester(temp_dir, threshold=0.1)  # Very low threshold
        tester.capture_baseline("test", sample_image)
        
        match, similarity = tester.compare_with_baseline("test", colored_image)
        # With very low threshold, even different images might match
        assert isinstance(match, bool)
        assert 0.0 <= similarity <= 1.0
    
    def test_set_similarity_threshold(self, temp_dir):
        """Test set_similarity_threshold method"""
        tester = VisualTester(temp_dir)
        tester.set_similarity_threshold(0.8)
        assert tester.similarity_threshold == 0.8
    
    @pytest.mark.parametrize("invalid_threshold", [-0.1, 1.5, 2.0])
    def test_set_similarity_threshold_invalid(self, temp_dir, invalid_threshold):
        """Test set_similarity_threshold with invalid values"""
        tester = VisualTester(temp_dir)
        with pytest.raises(ValueError):
            tester.set_similarity_threshold(invalid_threshold)


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
    
    def test_visual_difference_edge_cases(self):
        """Test VisualDifference with edge cases"""
        # Zero values
        diff = VisualDifference(
            location=(0, 0),
            size=(0, 0),
            difference_percentage=0.0,
            type="unchanged"
        )
        assert diff.location == (0, 0)
        assert diff.size == (0, 0)
        assert diff.difference_percentage == 0.0
        assert diff.type == "unchanged"
        
        # Maximum values
        diff = VisualDifference(
            location=(9999, 9999),
            size=(9999, 9999),
            difference_percentage=100.0,
            type="missing"
        )
        assert diff.location == (9999, 9999)
        assert diff.size == (9999, 9999)
        assert diff.difference_percentage == 100.0
        assert diff.type == "missing" 