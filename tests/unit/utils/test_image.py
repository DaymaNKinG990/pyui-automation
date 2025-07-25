"""
Tests for image utilities
"""
import pytest
import numpy as np
import cv2
from pathlib import Path

from pyui_automation.utils.image import (
    load_image, save_image, resize_image, compare_images,
    find_template, non_max_suppression, highlight_region,
    crop_image, preprocess_image, create_mask, enhance_image
)


class TestImageFunctions:
    """Tests for image utility functions"""
    
    def test_load_image_success(self, tmp_path):
        """Test load_image with valid image"""
        # Create a simple test image
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[50, 50] = [255, 255, 255]  # White pixel in center
        
        image_path = tmp_path / "test_image.png"
        cv2.imwrite(str(image_path), test_image)
        
        loaded_image = load_image(image_path)
        
        assert loaded_image is not None
        assert isinstance(loaded_image, np.ndarray)
        assert loaded_image.shape == (100, 100, 3)
    
    def test_load_image_not_exists(self, tmp_path):
        """Test load_image with non-existent file"""
        non_existent_path = tmp_path / "non_existent.png"
        
        loaded_image = load_image(non_existent_path)
        
        assert loaded_image is None
    
    def test_save_image_success(self, tmp_path):
        """Test save_image with valid image"""
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        test_image[50, 50] = [255, 255, 255]
        
        image_path = tmp_path / "test_image.png"
        
        result = save_image(test_image, image_path)
        
        assert result is True
        assert image_path.exists()
    
    def test_save_image_failure(self, tmp_path):
        """Test save_image with invalid image"""
        invalid_image = None
        image_path = tmp_path / "test_image.png"
        
        result = save_image(invalid_image, image_path)
        
        assert result is False
    
    def test_resize_image_with_width(self):
        """Test resize_image with width parameter"""
        original_image = np.zeros((100, 200, 3), dtype=np.uint8)
        
        resized_image = resize_image(original_image, width=150)
        
        assert resized_image.shape[1] == 150  # width
        assert resized_image.shape[0] == 75   # height (maintained aspect ratio)
    
    def test_resize_image_with_height(self):
        """Test resize_image with height parameter"""
        original_image = np.zeros((100, 200, 3), dtype=np.uint8)
        
        resized_image = resize_image(original_image, height=150)
        
        assert resized_image.shape[0] == 150  # height
        assert resized_image.shape[1] == 300  # width (maintained aspect ratio)
    
    def test_resize_image_no_params(self):
        """Test resize_image with no parameters"""
        original_image = np.zeros((100, 200, 3), dtype=np.uint8)
        
        resized_image = resize_image(original_image)
        
        assert resized_image.shape == original_image.shape
    
    def test_compare_images_identical(self):
        """Test compare_images with identical images"""
        image1 = np.zeros((100, 100, 3), dtype=np.uint8)
        image2 = np.zeros((100, 100, 3), dtype=np.uint8)
        
        similarity = compare_images(image1, image2)
        
        assert similarity == 1.0
    
    def test_compare_images_different(self):
        """Test compare_images with different images"""
        image1 = np.zeros((100, 100, 3), dtype=np.uint8)
        image2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
        
        similarity = compare_images(image1, image2)
        
        assert similarity < 1.0
        assert similarity >= 0.0
    
    def test_compare_images_different_shapes(self):
        """Test compare_images with different shapes"""
        image1 = np.zeros((100, 100, 3), dtype=np.uint8)
        image2 = np.zeros((200, 200, 3), dtype=np.uint8)
        
        similarity = compare_images(image1, image2)
        
        assert similarity == 0.0
    
    def test_find_template(self):
        """Test find_template function"""
        # Create a larger image
        image = np.zeros((200, 200, 3), dtype=np.uint8)
        # Create a template (smaller image)
        template = np.ones((50, 50, 3), dtype=np.uint8) * 255
        
        # Place template in the image
        image[75:125, 75:125] = template
        
        matches = find_template(image, template, threshold=0.8)
        
        assert len(matches) > 0
        assert all(isinstance(match, tuple) and len(match) == 3 for match in matches)
    
    def test_crop_image(self):
        """Test crop_image function"""
        original_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        cropped_image = crop_image(original_image, 10, 10, 50, 50)
        
        assert cropped_image.shape == (50, 50, 3)
    
    def test_preprocess_image(self):
        """Test preprocess_image function"""
        original_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        processed_image = preprocess_image(original_image)
        
        assert isinstance(processed_image, np.ndarray)
        assert processed_image.shape == original_image.shape
    
    def test_create_mask(self):
        """Test create_mask function"""
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        image[25:75, 25:75] = [255, 255, 255]  # White region
        
        mask = create_mask(image, lower=(200, 200, 200), upper=(255, 255, 255))
        
        assert isinstance(mask, np.ndarray)
        assert mask.shape == (100, 100)
        assert mask.dtype == np.uint8
    
    def test_enhance_image(self):
        """Test enhance_image function"""
        original_image = np.zeros((100, 100, 3), dtype=np.uint8)
        
        enhanced_image = enhance_image(original_image, method="contrast")
        
        assert isinstance(enhanced_image, np.ndarray)
        assert enhanced_image.shape == original_image.shape 