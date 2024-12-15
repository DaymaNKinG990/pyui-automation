import pytest
import numpy as np
from pathlib import Path
import tempfile
import os
from pyui_automation.utils.image import (
    load_image, save_image, resize_image, compare_images,
    find_template, highlight_region, crop_image, non_max_suppression
)


@pytest.fixture
def test_image():
    """Create test image"""
    return np.zeros((100, 100, 3), dtype=np.uint8)

@pytest.fixture
def temp_image_path():
    """Create temporary path for image"""
    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as f:
        return Path(f.name)

def test_save_load_image(test_image, temp_image_path):
    """Test saving and loading image"""
    assert save_image(test_image, temp_image_path)
    loaded = load_image(temp_image_path)
    assert loaded is not None, "Failed to load saved image"
    assert np.array_equal(test_image, loaded)
    temp_image_path.unlink()

def test_load_invalid_image():
    """Test loading invalid image"""
    assert load_image(Path('nonexistent.png')) is None

def test_save_image_errors(test_image):
    """Test error handling in save_image"""
    # Test saving to invalid path
    assert not save_image(test_image, Path('/nonexistent/dir/image.png'))
    
    # Test saving with invalid permissions
    with tempfile.TemporaryDirectory() as tmpdir:
        path = Path(tmpdir) / 'test.png'
        # Create the file first
        path.touch()
        # Try to make it read-only
        os.chmod(str(path), 0o444)
        assert not save_image(test_image, path)

def test_resize_image(test_image):
    """Test image resizing"""
    # Test with width only
    resized = resize_image(test_image, width=50)
    assert resized.shape == (50, 50, 3)
    
    # Test with height only
    resized = resize_image(test_image, height=50)
    assert resized.shape == (50, 50, 3)
    
    # Test with both width and height
    resized = resize_image(test_image, width=50, height=75)
    assert resized.shape == (75, 50, 3)
    
    # Test with same dimensions
    resized = resize_image(test_image, width=100)
    assert np.array_equal(test_image, resized)

def test_compare_images():
    """Test image comparison"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    img3 = np.ones((100, 100, 3), dtype=np.uint8)
    
    # Test identical images
    assert compare_images(img1, img2)
    # Test different images
    assert not compare_images(img1, img3)
    # Test different sizes
    assert not compare_images(img1, np.zeros((50, 50, 3)))
    # Test different thresholds
    img4 = img1.copy()
    img4[0:10, 0:10] = 255  # Make small difference
    assert compare_images(img1, img4, threshold=0.9)
    assert not compare_images(img1, img4, threshold=0.99)

def test_find_template():
    """Test template matching"""
    # Create a test image (100x100) with a distinctive pattern
    image = np.zeros((100, 100), dtype=np.uint8)
    image[20:40, 28:32] = 255
    image[28:32, 20:40] = 255
    image[29:31, 29:31] = 0

    # Create template
    template = np.zeros((20, 20), dtype=np.uint8)
    template[4:16, 8:12] = 255
    template[8:12, 4:16] = 255
    template[9:11, 9:11] = 0

    # Test normal matching
    locations = find_template(image, template, threshold=0.6)
    assert len(locations) == 1
    x, y, score = locations[0]
    assert abs(x - 30) <= 2 and abs(y - 30) <= 2
    assert 0 <= score <= 1

    # Test no matches
    locations = find_template(image, template, threshold=0.99)
    assert len(locations) == 0

    # Test multiple matches
    image[60:80, 68:72] = 255  # Add second pattern
    image[68:72, 60:80] = 255
    image[69:71, 69:71] = 0
    locations = find_template(image, template, threshold=0.6)
    assert len(locations) == 2

def test_non_max_suppression():
    """Test non-maximum suppression"""
    # Create overlapping matches
    matches = [(10, 10), (12, 12), (50, 50)]
    template_shape = (20, 20)
    
    # Test with high overlap threshold
    result = non_max_suppression(matches, template_shape, 0.9)
    assert len(result) == 2  # Should keep both close matches
    
    # Test with low overlap threshold
    result = non_max_suppression(matches, template_shape, 0.1)
    assert len(result) == 2  # Should merge close matches
    
    # Test with empty list
    assert len(non_max_suppression([], template_shape, 0.5)) == 0
    
    # Test with single match
    assert len(non_max_suppression([(10, 10)], template_shape, 0.5)) == 1

def test_highlight_region(test_image):
    """Test region highlighting"""
    # Test default green highlight
    highlighted = highlight_region(test_image, 10, 10, 20, 20)
    assert not np.array_equal(test_image, highlighted)
    assert highlighted[10, 10:30, 1].any()
    
    # Test custom color
    red = (0, 0, 255)
    highlighted = highlight_region(test_image, 10, 10, 20, 20, color=red)
    assert highlighted[10, 10:30, 2].any()
    
    # Test custom thickness
    thick = highlight_region(test_image, 10, 10, 20, 20, thickness=5)
    thin = highlight_region(test_image, 10, 10, 20, 20, thickness=1)
    assert not np.array_equal(thick, thin)
    
    # Test boundary cases
    edge = highlight_region(test_image, 0, 0, 99, 99)
    assert edge[0, 0:99, 1].any()

def test_crop_image(test_image):
    """Test image cropping"""
    # Test normal crop
    cropped = crop_image(test_image, 10, 10, 20, 20)
    assert cropped.shape == (20, 20, 3)
    
    # Test edge crop
    edge = crop_image(test_image, 0, 0, 50, 50)
    assert edge.shape == (50, 50, 3)
    
    # Test full image crop
    full = crop_image(test_image, 0, 0, 100, 100)
    assert np.array_equal(test_image, full)
    
    # Test small crop
    small = crop_image(test_image, 50, 50, 1, 1)
    assert small.shape == (1, 1, 3)
