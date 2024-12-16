import pytest
from unittest.mock import MagicMock
import numpy as np
import cv2
from pyui_automation.core.visual import VisualMatcher, VisualDifference, VisualTester


@pytest.fixture
def mock_element():
    """Create a mock UI element for testing"""
    element = MagicMock()
    # Create a test screen with multiple white circles that match our template
    screen = np.zeros((100, 100, 3), dtype=np.uint8)
    # Add three circles at different locations
    cv2.circle(screen, (30, 30), 5, (255, 255, 255), -1)
    cv2.circle(screen, (50, 50), 5, (255, 255, 255), -1)
    cv2.circle(screen, (70, 70), 5, (255, 255, 255), -1)
    # Return the actual numpy array instead of wrapping in MagicMock
    element.capture_screenshot = lambda: screen
    return element

@pytest.fixture
def visual_matcher(mock_element):
    """Create VisualMatcher instance with mock element"""
    matcher = VisualMatcher(mock_element)
    matcher.similarity_threshold = 0.8  # Set a reasonable threshold for testing
    return matcher

@pytest.fixture
def visual_tester(tmp_path):
    """Create VisualTester instance with temporary directory"""
    return VisualTester(tmp_path)

@pytest.fixture
def sample_images():
    """Create sample images for testing"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    
    cv2.circle(img1, (50, 50), 20, (255, 255, 255), -1)
    cv2.circle(img2, (50, 50), 20, (255, 255, 255), -1)
    cv2.rectangle(img2, (70, 70), (90, 90), (255, 255, 255), -1)
    
    return img1, img2

def test_compare_images(visual_matcher):
    """Test comparing two images"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    
    cv2.circle(img1, (50, 50), 20, (255, 255, 255), -1)
    cv2.circle(img2, (50, 50), 20, (255, 255, 255), -1)
    
    result = visual_matcher.compare_images(img1, img2)
    assert result['match'] == True
    assert result['similarity'] > 0.95

def test_find_element(visual_matcher):
    """Test finding element by image"""
    template = np.zeros((20, 20, 3), dtype=np.uint8)
    cv2.circle(template, (10, 10), 5, (255, 255, 255), -1)
    
    location = visual_matcher.find_element(template)
    assert location is not None
    assert len(location) == 2

def test_wait_for_image(visual_matcher):
    """Test waiting for image to appear"""
    template = np.zeros((20, 20, 3), dtype=np.uint8)
    cv2.circle(template, (10, 10), 5, (255, 255, 255), -1)
    
    result = visual_matcher.wait_for_image(template, timeout=1)
    assert result == True

def test_verify_visual_state(visual_matcher):
    """Test verifying visual state against baseline"""
    baseline = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(baseline, (50, 50), 20, (255, 255, 255), -1)
    
    result = visual_matcher.verify_visual_state(baseline)
    assert result['match'] == True
    assert result['similarity'] > 0.95

def test_capture_baseline(visual_matcher, tmp_path):
    """Test capturing baseline image"""
    baseline_path = tmp_path / "baseline.png"
    visual_matcher.capture_baseline(baseline_path)
    
    # Verify the image was saved correctly
    assert baseline_path.exists()
    saved_image = cv2.imread(str(baseline_path))
    assert saved_image is not None
    assert saved_image.shape == (100, 100, 3)

def test_highlight_differences(visual_matcher):
    """Test highlighting differences between images"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img2, (50, 50), 20, (255, 255, 255), -1)
    
    diff_img = visual_matcher.highlight_differences(img1, img2)
    assert diff_img is not None
    assert diff_img.shape == (100, 100, 3)

def test_generate_diff_report(visual_matcher, tmp_path):
    """Test generating visual difference report"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img2, (50, 50), 20, (255, 255, 255), -1)
    
    report_path = tmp_path / "diff_report.html"
    visual_matcher.generate_diff_report(img1, img2, report_path)
    assert report_path.exists()

def test_image_similarity_threshold(visual_matcher):
    """Test image similarity threshold settings"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img2, (50, 50), 20, (255, 255, 255), -1)
    
    visual_matcher.set_similarity_threshold(0.5)
    result = visual_matcher.compare_images(img1, img2)
    assert result['match'] == False

def test_region_of_interest(visual_matcher):
    """Test comparing specific regions of interest"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    
    roi = (20, 20, 60, 60)
    cv2.circle(img1, (40, 40), 10, (255, 255, 255), -1)
    cv2.circle(img2, (40, 40), 10, (255, 255, 255), -1)
    
    result = visual_matcher.compare_images(img1, img2, roi=roi)
    assert result['match'] == True
    assert result['similarity'] > 0.95

def test_multiple_template_matching(visual_matcher):
    """Test finding multiple instances of a template"""
    template = np.zeros((20, 20, 3), dtype=np.uint8)
    cv2.circle(template, (10, 10), 5, (255, 255, 255), -1)
    
    locations = visual_matcher.find_all_elements(template)
    assert len(locations) == 3  # Should find all three circles
    
    # Verify the locations match our expected circle positions
    expected_centers = [(30, 30), (50, 50), (70, 70)]
    found_centers = [(loc['location'][0] + 10, loc['location'][1] + 10) for loc in locations]  # Add template center offset
    assert all(any(abs(found[0] - exp[0]) <= 2 and abs(found[1] - exp[1]) <= 2 
              for exp in expected_centers) for found in found_centers)

def test_visual_tester_init(tmp_path):
    """Test VisualTester initialization"""
    tester = VisualTester(tmp_path)
    assert tester.baseline_dir == tmp_path
    assert tester.baseline_dir.exists()

def test_compare_identical_images(visual_tester):
    """Test comparing identical images"""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img, (50, 50), 20, (255, 255, 255), -1)
    
    result = visual_tester.compare(img, img)
    assert result['match'] == True
    assert result['similarity'] == 1.0

def test_compare_different_images(visual_tester, sample_images):
    """Test comparing different images"""
    img1, img2 = sample_images
    result = visual_tester.compare(img1, img2)
    assert result['match'] == False
    assert result['similarity'] < 1.0

def test_compare_different_sizes(visual_tester):
    """Test comparing images of different sizes"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((50, 50, 3), dtype=np.uint8)
    
    with pytest.raises(ValueError):
        visual_tester.compare(img1, img2)

def test_verify_hash_identical_images(visual_tester):
    """Test hash verification with identical images"""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img, (50, 50), 20, (255, 255, 255), -1)
    
    # First capture the baseline
    visual_tester.capture_baseline("test_identical.png", img)
    # Then verify against it
    assert visual_tester.verify_hash("test_identical.png", img) == True

def test_verify_hash_similar_images(visual_tester):
    """Test hash verification with similar images"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    
    cv2.circle(img1, (50, 50), 20, (255, 255, 255), -1)
    cv2.circle(img2, (51, 51), 20, (255, 255, 255), -1)
    
    # First capture the baseline
    visual_tester.capture_baseline("test_similar.png", img1)
    # Then verify against it
    assert visual_tester.verify_hash("test_similar.png", img2) == True

def test_verify_hash_different_images(visual_tester, sample_images):
    """Test hash verification with different images"""
    img1, img2 = sample_images
    # First capture the baseline
    visual_tester.capture_baseline("test_different.png", img1)
    # Then verify against it
    assert visual_tester.verify_hash("test_different.png", img2) == False

def test_calculate_phash(visual_tester):
    """Test perceptual hash calculation"""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img, (50, 50), 20, (255, 255, 255), -1)
    
    hash_value = visual_tester.calculate_phash(img)
    assert hash_value is not None
    assert isinstance(hash_value, str)

def test_compare_images_with_resize(visual_matcher):
    """Test comparing images that need resizing"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((200, 200, 3), dtype=np.uint8)
    
    cv2.circle(img1, (50, 50), 20, (255, 255, 255), -1)
    cv2.circle(img2, (100, 100), 40, (255, 255, 255), -1)
    
    result = visual_matcher.compare_images(img1, img2, resize=True)
    assert result['match'] == True
    assert result['similarity'] > 0.95

def test_compare_images_different_content(visual_matcher):
    """Test comparing images with completely different content"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.ones((100, 100, 3), dtype=np.uint8) * 255
    
    result = visual_matcher.compare_images(img1, img2)
    assert result['match'] == False
    assert result['similarity'] < 0.1

def test_visual_difference_dataclass():
    """Test VisualDifference dataclass functionality"""
    diff = VisualDifference(
        location=(10, 20),
        size=(30, 40),
        difference_percentage=0.02,  # 2% difference (98% similarity)
        type="pixel"
    )
    
    assert diff.location == (10, 20)
    assert diff.size == (30, 40)
    assert diff.difference_percentage == 0.02
    assert diff.type == "pixel"

def test_generate_visual_report_with_empty_differences(visual_tester, tmp_path):
    """Test generating report with no differences"""
    report_path = tmp_path / "empty_report.html"
    visual_tester.generate_report([], report_path)
    assert report_path.exists()

def test_generate_visual_report_with_differences(visual_tester, tmp_path):
    """Test generating report with differences"""
    differences = [
        VisualDifference(
            location=(10, 20),
            size=(30, 40),
            difference_percentage=0.02,  # 2% difference (98% similarity)
            type="pixel"
        ),
        VisualDifference(
            location=(50, 60),
            size=(70, 80),
            difference_percentage=0.03,  # 3% difference (97% similarity)
            type="structural"
        )
    ]
    
    report_path = tmp_path / "diff_report.html"
    visual_tester.generate_report(differences, report_path)
    assert report_path.exists()

def test_capture_baseline_with_invalid_image(visual_tester):
    """Test capturing baseline with invalid image data"""
    with pytest.raises(ValueError, match="Invalid image data"):
        visual_tester.capture_baseline("test.png", None)
    with pytest.raises(ValueError, match="Invalid image data"):
        visual_tester.capture_baseline("test.png", np.array([]))

def test_capture_baseline_with_empty_name(visual_tester, sample_images):
    """Test capturing baseline with empty name"""
    with pytest.raises(ValueError, match="Name cannot be empty"):
        visual_tester.capture_baseline("", sample_images[0])
    with pytest.raises(ValueError, match="Name cannot be empty"):
        visual_tester.capture_baseline(None, sample_images[0])

def test_verify_hash_with_invalid_images(visual_tester):
    """Test hash verification with invalid image data"""
    with pytest.raises(ValueError, match="Invalid image data"):
        visual_tester.verify_hash("test.png", None)
    with pytest.raises(ValueError, match="Invalid image data"):
        visual_tester.verify_hash("test.png", np.array([]))

def test_compare_with_invalid_images(visual_tester):
    """Test comparing invalid image data"""
    with pytest.raises(ValueError):
        visual_tester.compare(None, None)

def test_calculate_phash_with_invalid_image(visual_tester):
    """Test calculating perceptual hash with invalid image"""
    with pytest.raises(ValueError):
        visual_tester.calculate_phash(None)

def test_compare_with_threshold_adjustment(visual_tester, sample_images):
    """Test image comparison with different thresholds"""
    img1, img2 = sample_images
    
    # Test with high threshold (strict comparison)
    visual_tester.set_similarity_threshold(0.95)
    result_strict = visual_tester.compare(img1, img2)
    assert result_strict['match'] == False
    
    # Test with low threshold (lenient comparison)
    visual_tester.set_similarity_threshold(0.5)
    result_lenient = visual_tester.compare(img1, img2)
    assert result_lenient['match'] == True
    
    # Verify that similarity values are the same regardless of threshold
    assert result_strict['similarity'] == result_lenient['similarity']

def test_baseline_dir_creation(tmp_path):
    """Test baseline directory creation with nested path"""
    nested_path = tmp_path / "visual" / "baselines"
    tester = VisualTester(nested_path)
    assert tester.baseline_dir.exists()
    assert tester.baseline_dir == nested_path

def test_compare_with_color_images(visual_tester):
    """Test comparing images with different color patterns"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    
    # Create different color patterns
    img1[20:40, 20:40] = [255, 0, 0]   # Red square
    img2[20:40, 20:40] = [0, 255, 0]   # Green square
    
    result = visual_tester.compare(img1, img2)
    assert result['match'] == False
    assert result['similarity'] < 0.9
    assert result['diff_image'] is not None

def test_phash_with_rotated_image(visual_tester):
    """Test perceptual hash with rotated image"""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img, (50, 50), 20, (255, 255, 255), -1)
    
    # Create rotated version
    center = (50, 50)
    matrix = cv2.getRotationMatrix2D(center, 10, 1.0)
    rotated = cv2.warpAffine(img, matrix, (100, 100))
    
    # Hash should be similar for small rotations
    hash1 = visual_tester.calculate_phash(img)
    hash2 = visual_tester.calculate_phash(rotated)
    
    assert not np.array_equal(hash1, hash2)  # Hashes should be different for rotated image
    assert visual_tester.verify_hash(img, rotated)  # But should still match within threshold
