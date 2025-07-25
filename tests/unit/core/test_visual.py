"""
Tests for visual testing functionality
"""
import pytest
import numpy as np
from pathlib import Path

from pyui_automation.core.visual import VisualTestingService, ImageComparator, BaselineManager


class TestVisualDifference:
    """Test VisualDifference class"""
    
    def test_visual_difference_creation(self, mocker):
        """Test VisualDifference creation"""
        diff = VisualDifference(
            location=(100, 200), size=(50, 30), difference_percentage=0.15, type="changed", element=mocker.Mock()
        )
        assert diff.location == (100, 200)
        assert diff.size == (50, 30)
        assert diff.difference_percentage == 0.15
        assert diff.type == "changed"
        assert diff.element is not None


class TestVisualMatcher:
    """Test VisualMatcher class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_element = mocker.Mock()
        self.matcher = VisualMatcher(self.mock_element)

    def test_find_element_in_image_success(self, mocker):
        """Test successful element finding in image"""
        element_image = np.zeros((20, 20, 3), dtype=np.uint8)
        
        mocker.patch.object(self.mock_element, 'capture_screenshot', return_value=element_image)
        mocker.patch('cv2.matchTemplate')
        mocker.patch('cv2.minMaxLoc')
        
        # Mock template matching result
        mocker.patch('cv2.matchTemplate').return_value = np.zeros((81, 81), dtype=np.float32)
        mocker.patch('cv2.minMaxLoc').return_value = (0.0, 0.98, (0, 0), (0, 0))
        
        result = self.matcher.find_element_in_image(np.zeros((100, 100, 3), dtype=np.uint8))
        assert result is not None
        assert result[0] == 0  # x coordinate
        assert result[1] == 0  # y coordinate

    def test_find_element_in_image_not_found(self, mocker):
        """Test element finding when not found"""
        element_image = np.zeros((20, 20, 3), dtype=np.uint8)
        
        mocker.patch.object(self.mock_element, 'capture_screenshot', return_value=element_image)
        mocker.patch('cv2.matchTemplate')
        mocker.patch('cv2.minMaxLoc')
        
        # Mock template matching result below threshold
        mocker.patch('cv2.matchTemplate').return_value = np.zeros((81, 81), dtype=np.float32)
        mocker.patch('cv2.minMaxLoc').return_value = (0.0, 0.3, (0, 0), (0, 0))
        
        result = self.matcher.find_element_in_image(np.zeros((100, 100, 3), dtype=np.uint8))
        assert result is None

    def test_find_element_in_image_with_threshold(self, mocker):
        """Test element finding with custom threshold"""
        element_image = np.zeros((20, 20, 3), dtype=np.uint8)
        
        mocker.patch.object(self.mock_element, 'capture_screenshot', return_value=element_image)
        mocker.patch('cv2.matchTemplate')
        mocker.patch('cv2.minMaxLoc')
        
        # Mock template matching result with values above threshold
        result_array = np.zeros((81, 81), dtype=np.float32)
        result_array[40, 40] = 0.95  # High similarity at center
        
        mocker.patch('cv2.matchTemplate').return_value = result_array
        mocker.patch('cv2.minMaxLoc').return_value = (0.0, 0.95, (40, 40), (40, 40))
        
        result = self.matcher.find_element_in_image(np.zeros((100, 100, 3), dtype=np.uint8), threshold=0.9)
        assert result is not None
        assert result[0] == 40
        assert result[1] == 40

    def test_compare_images_similar(self, mocker):
        """Test comparing similar images"""
        image1 = np.zeros((50, 50, 3), dtype=np.uint8)
        image2 = np.zeros((50, 50, 3), dtype=np.uint8)
        
        mocker.patch('cv2.matchTemplate')
        mocker.patch('cv2.minMaxLoc')
        mocker.patch('cv2.matchTemplate').return_value = np.zeros((31, 31), dtype=np.float32)
        mocker.patch('cv2.minMaxLoc').return_value = (0.0, 0.98, (0, 0), (0, 0))
        
        result = self.matcher.compare_images(image1, image2)
        assert result > 0.9  # High similarity

    def test_compare_images_different(self, mocker):
        """Test comparing different images"""
        image1 = np.zeros((50, 50, 3), dtype=np.uint8)
        image2 = np.ones((50, 50, 3), dtype=np.uint8) * 255
        
        mocker.patch('cv2.matchTemplate')
        mocker.patch('cv2.minMaxLoc')
        mocker.patch('cv2.matchTemplate').return_value = np.zeros((31, 31), dtype=np.float32)
        mocker.patch('cv2.minMaxLoc').return_value = (0.0, 0.3, (0, 0), (0, 0))
        
        result = self.matcher.compare_images(image1, image2)
        assert result < 0.5  # Low similarity


class TestVisualTester:
    """Test VisualTester class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.baseline_dir = Path("test_baseline")
        self.tester = VisualTester(self.baseline_dir)

    def test_create_baseline(self, mocker):
        """Test create_baseline method"""
        mock_element = mocker.Mock()
        mock_element.capture_screenshot.return_value = np.zeros((50, 50, 3), dtype=np.uint8)
        
        mocker.patch('cv2.imwrite', return_value=True)
        result = self.tester.create_baseline("test_element", mock_element)
        
        assert result is True
        mock_element.capture_screenshot.assert_called_once()

    def test_verify_visual_state_success(self, mocker):
        """Test verify_visual_state with successful verification"""
        mock_element = mocker.Mock()
        mock_element.capture_screenshot.return_value = np.zeros((50, 50, 3), dtype=np.uint8)
        
        mocker.patch.object(self.tester, 'read_baseline', return_value=np.zeros((50, 50, 3), dtype=np.uint8))
        mocker.patch.object(self.tester, 'compare', return_value={'match': True, 'similarity': 0.98})
        
        result = self.tester.verify_visual_state("test_element", mock_element)
        assert result is True

    def test_verify_visual_state_failure(self, mocker):
        """Test verify_visual_state with failed verification"""
        mock_element = mocker.Mock()
        mock_element.capture_screenshot.return_value = np.zeros((50, 50, 3), dtype=np.uint8)
        
        mocker.patch.object(self.tester, 'read_baseline', return_value=np.zeros((50, 50, 3), dtype=np.uint8))
        mocker.patch.object(self.tester, 'compare', return_value={'match': False, 'similarity': 0.5})
        
        result = self.tester.verify_visual_state("test_element", mock_element)
        assert result is False

    def test_verify_visual_state_baseline_not_found(self, mocker):
        """Test verify_visual_state when baseline not found"""
        mock_element = mocker.Mock()
        mock_element.capture_screenshot.return_value = np.zeros((50, 50, 3), dtype=np.uint8)
        
        mocker.patch.object(self.tester, 'read_baseline', side_effect=FileNotFoundError("Baseline not found"))
        result = self.tester.verify_visual_state("test_element", mock_element)
        assert result is False

    def test_wait_for_image_success(self, mocker):
        """Test wait_for_image with successful wait"""
        mock_element = mocker.Mock()
        mock_element.capture_screenshot.return_value = np.zeros((50, 50, 3), dtype=np.uint8)
        
        mocker.patch.object(self.tester, 'verify_visual_state', return_value=True)
        result = self.tester.wait_for_image("test_element", mock_element, 1.0)
        assert result is True

    def test_wait_for_image_timeout(self, mocker):
        """Test wait_for_image with timeout"""
        mock_element = mocker.Mock()
        mock_element.capture_screenshot.return_value = np.zeros((50, 50, 3), dtype=np.uint8)
        
        mocker.patch.object(self.tester, 'verify_visual_state', return_value=False)
        result = self.tester.wait_for_image("test_element", mock_element, 0.1)
        assert result is False

    def test_generate_visual_report(self, mocker):
        """Test generate_visual_report method"""
        mock_element = mocker.Mock()
        mock_element.capture_screenshot.return_value = np.zeros((50, 50, 3), dtype=np.uint8)
        
        mocker.patch.object(self.tester, 'read_baseline', return_value=np.zeros((50, 50, 3), dtype=np.uint8))
        mocker.patch.object(self.tester, 'compare', return_value={'match': True, 'similarity': 0.7, 'differences': []})
        
        report = self.tester.generate_visual_report("test_element", mock_element)
        assert 'element_name' in report
        assert 'match' in report
        assert 'similarity' in report

    def test_find_element_in_baseline(self, mocker):
        """Test find_element_in_baseline method"""
        mock_element = mocker.Mock()
        mock_element.capture_screenshot.return_value = np.zeros((50, 50, 3), dtype=np.uint8)
        
        mocker.patch.object(self.tester, 'read_baseline', return_value=np.zeros((100, 100, 3), dtype=np.uint8))
        mocker.patch('cv2.matchTemplate')
        mocker.patch('cv2.minMaxLoc')
        
        # Mock successful match
        mocker.patch('cv2.matchTemplate').return_value = np.zeros((51, 51), dtype=np.float32)
        mocker.patch('cv2.minMaxLoc').return_value = (0.0, 0.95, (25, 25), (25, 25))
        
        result = self.tester.find_element_in_baseline("test_element", mock_element)
        assert result is not None
        assert result[0] == 25
        assert result[1] == 25

    def test_find_element_in_baseline_not_found(self, mocker):
        """Test find_element_in_baseline when element not found"""
        mock_element = mocker.Mock()
        mock_element.capture_screenshot.return_value = np.zeros((50, 50, 3), dtype=np.uint8)
        
        mocker.patch.object(self.tester, 'read_baseline', return_value=np.zeros((100, 100, 3), dtype=np.uint8))
        mocker.patch('cv2.matchTemplate')
        mocker.patch('cv2.minMaxLoc')
        
        # Mock failed match
        mocker.patch('cv2.matchTemplate').return_value = np.zeros((51, 51), dtype=np.float32)
        mocker.patch('cv2.minMaxLoc').return_value = (0.0, 0.3, (0, 0), (0, 0))
        
        result = self.tester.find_element_in_baseline("test_element", mock_element)
        assert result is None


class TestVisualTesterIntegration:
    """Integration tests for VisualTester"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.baseline_dir = Path("test_baseline")
        self.tester = VisualTester(self.baseline_dir)
        self.mock_element = mocker.Mock()

    def test_complete_visual_testing_workflow(self, mocker):
        """Test complete visual testing workflow"""
        self.mock_element.capture_screenshot.return_value = np.zeros((50, 50, 3), dtype=np.uint8)
        
        mocker.patch('cv2.imwrite', return_value=True)
        mocker.patch.object(self.tester, 'read_baseline', return_value=np.zeros((50, 50, 3), dtype=np.uint8))
        mocker.patch.object(self.tester, 'compare', return_value={'match': True, 'similarity': 0.98, 'differences': []})
        mocker.patch('pathlib.Path.mkdir')
        
        # Create baseline
        self.tester.create_baseline("test_element", self.mock_element)
        
        # Verify visual state
        result = self.tester.verify_visual_state("test_element", self.mock_element)
        assert result is True
        
        # Generate report
        report = self.tester.generate_visual_report("test_element", self.mock_element)
        assert report['match'] is True

    def test_visual_testing_with_different_thresholds(self, mocker):
        """Test visual testing with different thresholds"""
        self.mock_element.capture_screenshot.return_value = np.zeros((50, 50, 3), dtype=np.uint8)
        
        # Test with high threshold
        high_threshold_tester = VisualTester(self.baseline_dir, threshold=0.99)
        
        mocker.patch.object(high_threshold_tester, 'read_baseline', return_value=np.zeros((50, 50, 3), dtype=np.uint8))
        mocker.patch.object(high_threshold_tester, 'compare', return_value={'match': False, 'similarity': 0.98})
        
        result = high_threshold_tester.verify_visual_state("test_element", self.mock_element)
        assert result is False
        
        # Test with low threshold
        low_threshold_tester = VisualTester(self.baseline_dir, threshold=0.5)
        
        mocker.patch.object(low_threshold_tester, 'read_baseline', return_value=np.zeros((50, 50, 3), dtype=np.uint8))
        mocker.patch.object(low_threshold_tester, 'compare', return_value={'match': True, 'similarity': 0.6})
        
        result = low_threshold_tester.verify_visual_state("test_element", self.mock_element)
        assert result is True  # 0.6 > 0.5 