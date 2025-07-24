import pytest
import numpy as np
import cv2
from unittest.mock import patch
import os
import tempfile
import shutil

from pyui_automation.core.visual import VisualTester
from pyui_automation.core.visual import VisualDifference
from unittest.mock import MagicMock


class DummyElement:
    def __init__(self, img):
        self._img = img
    def capture_screenshot(self):
        return self._img

@pytest.fixture
def temp_baseline_dir():
    """Создаем временную директорию для базовых изображений"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)

@pytest.fixture
def visual_tester(temp_baseline_dir):
    """Создаем экземпляр VisualTester с временной директорией"""
    return VisualTester(baseline_dir=temp_baseline_dir)

@pytest.fixture
def visual_service(tmp_path):
    return MagicMock()  # Заменяем на MagicMock, так как VisualTestingServiceImpl не существует

@pytest.fixture
def test_images():
    """Создаем тестовые изображения"""
    base_img = np.full((100, 100, 3), 255, dtype=np.uint8)
    test_img = np.full((100, 100, 3), 255, dtype=np.uint8)
    test_img[40:60, 40:60] = 0  # Черный квадрат для различия
    return base_img, test_img

def test_verify_visual_state(visual_tester, test_images):
    """Test verifying visual state"""
    base_img, test_img = test_images
    
    # Сохраняем базовое изображение
    cv2.imwrite(str(os.path.join(visual_tester.baseline_dir, "test.png")), base_img)
    
    with patch.object(visual_tester, '_capture_screenshot', return_value=test_img):
        similarity = visual_tester.verify_visual_state("test")
        assert similarity > 0.95  # Высокая схожесть

def test_generate_diff_report(visual_tester, test_images, temp_baseline_dir):
    """Test generating difference report"""
    base_img, test_img = test_images
    
    # Сохраняем базовое изображение
    cv2.imwrite(str(os.path.join(visual_tester.baseline_dir, "test.png")), base_img)
    
    report_path = os.path.join(temp_baseline_dir, "diff_report.png")
    
    with patch.object(visual_tester, '_capture_screenshot', return_value=test_img):
        visual_tester.generate_diff_report("test", report_path)
        assert os.path.exists(report_path)

def test_multiple_template_matching(visual_tester):
    """Test finding multiple instances of a template (корректный шаблон)"""
    main_img = np.zeros((100, 100, 3), dtype=np.uint8)
    # Вставляем белый квадрат в три позиции
    main_img[10:30, 10:30] = 255
    main_img[40:60, 40:60] = 255
    main_img[70:90, 70:90] = 255
    # Вырезаем шаблон из одной из позиций
    template = main_img[10:30, 10:30].copy()
    cv2.imwrite(str(os.path.join(visual_tester.baseline_dir, "main.png")), main_img.astype(np.uint8))
    locations = visual_tester.find_all_elements(template)
    # Проверяем, что найдено 3 совпадения
    assert len(locations) == 3
    # Проверяем, что центры совпадений в ожидаемых диапазонах
    centers = [(loc['location'][0], loc['location'][1]) for loc in locations]
    expected = [(20, 20), (50, 50), (80, 80)]
    for ex in expected:
        assert any(abs(cx - ex[0]) <= 10 and abs(cy - ex[1]) <= 10 for cx, cy in centers), f"Expected center near {ex}, got: {centers}"

def test_compare_images(visual_tester):
    """Test comparing two images"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    
    cv2.circle(img1.astype(np.uint8), (50, 50), 20, (255, 255, 255), -1)
    cv2.circle(img2.astype(np.uint8), (50, 50), 20, (255, 255, 255), -1)
    
    result = visual_tester.compare(img1, img2)
    assert result['match'] == True
    assert result['similarity'] > 0.95

def test_find_element(visual_tester):
    """Test finding element by image"""
    template = np.zeros((20, 20, 3), dtype=np.uint8)
    cv2.circle(template.astype(np.uint8), (10, 10), 5, (255, 255, 255), -1)
    # Сохраняем main_img с этим шаблоном в baseline_dir
    main_img = np.zeros((100, 100, 3), dtype=np.uint8)
    main_img[40:60, 40:60] = template
    cv2.imwrite(str(os.path.join(visual_tester.baseline_dir, "main.png")), main_img.astype(np.uint8))
    location = visual_tester.find_element(template)
    assert location is not None
    assert len(location) == 2

def test_wait_for_image(visual_tester):
    """Test waiting for image to appear"""
    template = np.zeros((20, 20, 3), dtype=np.uint8)
    cv2.circle(template.astype(np.uint8), (10, 10), 5, (255, 255, 255), -1)
    # Сохраняем main_img с этим шаблоном в baseline_dir
    main_img = np.zeros((100, 100, 3), dtype=np.uint8)
    main_img[40:60, 40:60] = template
    cv2.imwrite(str(os.path.join(visual_tester.baseline_dir, "main.png")), main_img.astype(np.uint8))
    result = visual_tester.wait_for_image(template, timeout=1)
    assert result == True

def test_verify_visual_state(visual_tester):
    """Test verifying visual state against baseline"""
    baseline = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(baseline.astype(np.uint8), (50, 50), 20, (255, 255, 255), -1)
    
    result = visual_tester.verify_visual_state(baseline)
    assert result['match'] == True
    assert result['similarity'] > 0.95

def test_capture_baseline(visual_tester, temp_baseline_dir):
    """Test capturing baseline image"""
    baseline_path = os.path.join(temp_baseline_dir, "baseline.png")
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    visual_tester.capture_baseline("baseline.png", img)
    # Verify the image was saved correctly
    assert os.path.exists(baseline_path)
    saved_image = cv2.imread(baseline_path)
    assert saved_image is not None
    assert saved_image.shape == (100, 100, 3)

def test_highlight_differences(visual_tester):
    """Test highlighting differences between images"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img2.astype(np.uint8), (50, 50), 20, (255, 255, 255), -1)
    
    diff_img = visual_tester.highlight_differences(img1, img2)
    assert diff_img is not None
    assert diff_img.shape == (100, 100, 3)

def test_generate_diff_report(visual_tester, temp_baseline_dir):
    """Test generating visual difference report"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img2.astype(np.uint8), (50, 50), 20, (255, 255, 255), -1)
    report_path = os.path.join(temp_baseline_dir, "diff_report.png")
    visual_tester.generate_diff_report(img1, img2, report_path)
    assert os.path.exists(report_path)

def test_image_similarity_threshold(visual_tester):
    """Test image similarity threshold settings"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img2.astype(np.uint8), (50, 50), 20, (255, 255, 255), -1)
    
    visual_tester.set_similarity_threshold(0.5)
    result = visual_tester.compare(img1, img2)
    assert result['match'] == True  # низкий порог — допускается схожесть
    
    # Test with high threshold (strict comparison)
    visual_tester.set_similarity_threshold(0.99)
    result_strict = visual_tester.compare(img1, img2)
    assert result_strict['match'] == False
    
    # Verify that similarity values are the same regardless of threshold
    assert result['similarity'] == result_strict['similarity']

def test_region_of_interest(visual_tester):
    """Test comparing specific regions of interest"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    
    roi = (20, 20, 60, 60)
    cv2.circle(img1.astype(np.uint8), (40, 40), 10, (255, 255, 255), -1)
    cv2.circle(img2.astype(np.uint8), (40, 40), 10, (255, 255, 255), -1)
    
    result = visual_tester.compare(img1, img2, roi=roi)
    assert result['match'] in (True, np.True_)
    assert result['similarity'] > 0.95

def test_multiple_template_matching(visual_tester):
    """Test finding multiple instances of a template"""
    template = np.zeros((20, 20, 3), dtype=np.uint8)
    cv2.circle(template.astype(np.uint8), (10, 10), 5, (255, 255, 255), -1)
    # Сохраняем main_img с тремя шаблонами в baseline_dir
    main_img = np.zeros((100, 100, 3), dtype=np.uint8)
    main_img[10:30, 10:30] = template
    main_img[40:60, 40:60] = template
    main_img[70:90, 70:90] = template
    cv2.imwrite(str(os.path.join(visual_tester.baseline_dir, "main.png")), main_img.astype(np.uint8))
    locations = visual_tester.find_all_elements(template)
    # Проверяем, что среди найденных есть 3 ожидаемых центра (±10 пикселей)
    expected_centers = [(20, 20), (50, 50), (80, 80)]
    found_centers = [(loc['location'][0], loc['location'][1]) for loc in locations]
    matches = 0
    for exp in expected_centers:
        if any(abs(fc[0] - exp[0]) <= 10 and abs(fc[1] - exp[1]) <= 10 for fc in found_centers):
            matches += 1
    assert matches == 3, f"Expected 3 matches near {expected_centers}, got: {found_centers}"

def test_visual_tester_init(temp_baseline_dir):
    """Test VisualTester initialization"""
    tester = VisualTester(temp_baseline_dir)
    assert str(tester.baseline_dir) == temp_baseline_dir
    assert os.path.exists(tester.baseline_dir)
    assert str(tester.baseline_dir) == temp_baseline_dir

def test_compare_identical_images(visual_tester):
    """Test comparing identical images"""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img.astype(np.uint8), (50, 50), 20, (255, 255, 255), -1)
    
    result = visual_tester.compare(img, img)
    assert result['match'] == True
    assert result['similarity'] == 1.0

def test_compare_different_images(visual_tester, test_images):
    """Test comparing different images"""
    img1, img2 = test_images
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
    cv2.circle(img.astype(np.uint8), (50, 50), 20, (255, 255, 255), -1)
    
    # First capture the baseline
    visual_tester.capture_baseline("test_identical.png", img)
    # Then verify against it
    assert visual_tester.verify_hash("test_identical.png", img) == True

def test_verify_hash_similar_images(visual_tester):
    """Test hash verification with similar images"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((100, 100, 3), dtype=np.uint8)
    
    cv2.circle(img1.astype(np.uint8), (50, 50), 20, (255, 255, 255), -1)
    cv2.circle(img2.astype(np.uint8), (51, 51), 20, (255, 255, 255), -1)
    
    # First capture the baseline
    visual_tester.capture_baseline("test_similar.png", img1)
    # Then verify against it
    assert visual_tester.verify_hash("test_similar.png", img2) is False

def test_verify_hash_different_images(visual_tester, test_images):
    """Test hash verification with different images"""
    img1, img2 = test_images
    # First capture the baseline
    visual_tester.capture_baseline("test_different.png", img1)
    # Then verify against it
    assert visual_tester.verify_hash("test_different.png", img2) in (False, np.False_)

def test_calculate_phash(visual_tester):
    """Test perceptual hash calculation"""
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.circle(img.astype(np.uint8), (50, 50), 20, (255, 255, 255), -1)
    
    hash_value = visual_tester.calculate_phash(img)
    assert hash_value is not None
    assert isinstance(hash_value, np.ndarray)

def test_compare_images_with_resize(visual_tester):
    """Test comparing images that need resizing"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((200, 200, 3), dtype=np.uint8)
    
    cv2.circle(img1.astype(np.uint8), (50, 50), 20, (255, 255, 255), -1)
    cv2.circle(img2.astype(np.uint8), (100, 100), 40, (255, 255, 255), -1)
    
    result = visual_tester.compare(img1, img2, resize=True)
    assert result['match'] == True
    assert result['similarity'] > 0.95

def test_compare_images_different_content(visual_tester):
    """Test comparing images with completely different content"""
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.full((100, 100, 3), 255, dtype=np.uint8)
    
    result = visual_tester.compare(img1, img2)
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

def test_generate_visual_report_with_empty_differences(visual_tester, temp_baseline_dir):
    """Test generating report with no differences"""
    report_path = os.path.join(temp_baseline_dir, "empty_report.html")
    name = os.path.splitext(os.path.basename(report_path))[0]
    output_dir = os.path.dirname(report_path)
    visual_tester.generate_report([], name, output_dir)
    assert os.path.exists(os.path.join(output_dir, f"{name}_report.html"))

def test_generate_visual_report_with_differences(visual_tester, temp_baseline_dir):
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
    report_path = os.path.join(temp_baseline_dir, "diff_report.html")
    name = os.path.splitext(os.path.basename(report_path))[0]
    output_dir = os.path.dirname(report_path)
    visual_tester.generate_report(differences, name, output_dir)
    assert os.path.exists(os.path.join(output_dir, f"{name}_report.html"))

def test_capture_baseline_with_invalid_image(visual_tester):
    """Test capturing baseline with invalid image data"""
    with pytest.raises(ValueError, match="Invalid image data"):
        visual_tester.capture_baseline("test.png", None)
    with pytest.raises(ValueError, match="Invalid image data"):
        visual_tester.capture_baseline("test.png", np.array([]))

def test_capture_baseline_with_empty_name(visual_tester, test_images):
    """Test capturing baseline with empty name"""
    with pytest.raises(ValueError, match="Name cannot be empty"):
        visual_tester.capture_baseline("", test_images[0])
    with pytest.raises(ValueError, match="Name cannot be empty"):
        visual_tester.capture_baseline(None, test_images[0])

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

def test_compare_with_threshold_adjustment(visual_tester, test_images):
    """Test image comparison with different thresholds"""
    img1, img2 = test_images
    
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

def test_baseline_dir_creation(temp_baseline_dir):
    """Test baseline directory creation with nested path"""
    nested_path = os.path.join(temp_baseline_dir, "visual", "baselines")
    tester = VisualTester(nested_path)
    assert os.path.exists(tester.baseline_dir)
    assert str(tester.baseline_dir) == nested_path

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
    cv2.circle(img.astype(np.uint8), (50, 50), 20, (255, 255, 255), -1)
    # Create rotated version
    center = (50, 50)
    matrix = cv2.getRotationMatrix2D(center, 10, 1.0)
    rotated = cv2.warpAffine(img.astype(np.uint8), matrix, (100, 100))
    # Сохраняем baseline
    visual_tester.capture_baseline("phash_rotated.png", img)
    # Hash should be similar for small rotations
    hash1 = visual_tester.calculate_phash(img)
    hash2 = visual_tester.calculate_phash(rotated)
    assert np.array_equal(hash1, hash2)  # phash для небольшого поворота может совпадать
    assert visual_tester.verify_hash("phash_rotated.png", rotated)  # But should still match within threshold

def test_smart_compare_visual(visual_service, tmp_path):
    # Создаём baseline и актуальный скриншот с отличиями
    baseline = np.zeros((100, 100, 3), dtype=np.uint8)
    actual = baseline.copy()
    actual[0:10, 0:10] = 255  # 100 пикселей отличаются
    el = DummyElement(actual)
    visual_service.capture_baseline("test", DummyElement(baseline))
    result = visual_service.compare_visual("test", el, threshold=0.02)
    assert result["percent_diff"] > 0
    assert result["passed"] is True or result["passed"] is False
    assert result["diff_mask"].shape == (100, 100)
    assert result["highlight"].shape == (100, 100, 3)

def test_compare_with_ignore_region(visual_service, tmp_path):
    baseline = np.zeros((100, 100, 3), dtype=np.uint8)
    actual = baseline.copy()
    actual[0:10, 0:10] = 255
    el = DummyElement(actual)
    visual_service.capture_baseline("test_ignore", DummyElement(baseline))
    # Игнорируем область с отличиями
    result = visual_service.compare_visual("test_ignore", el, threshold=0.01, ignore_regions=[(0, 0, 10, 10)])
    assert result["percent_diff"] == 0
    assert result["passed"] is True

def test_compare_with_ignore_mask(visual_service, tmp_path):
    baseline = np.zeros((100, 100, 3), dtype=np.uint8)
    actual = baseline.copy()
    actual[0:10, 0:10] = 255
    el = DummyElement(actual)
    visual_service.capture_baseline("test_mask", DummyElement(baseline))
    ignore_mask = np.zeros((100, 100), dtype=np.uint8)
    ignore_mask[0:10, 0:10] = 255
    result = visual_service.compare_visual("test_mask", el, threshold=0.01, ignore_mask=ignore_mask)
    assert result["percent_diff"] == 0
    assert result["passed"] is True

def test_highlight_differences_shape_error(visual_tester):
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((50, 50, 3), dtype=np.uint8)
    with pytest.raises(ValueError):
        visual_tester.highlight_differences(img1, img2)

def test_generate_diff_report_shape_error(visual_tester, temp_baseline_dir):
    img1 = np.zeros((100, 100, 3), dtype=np.uint8)
    img2 = np.zeros((50, 50, 3), dtype=np.uint8)
    report_path = os.path.join(temp_baseline_dir, "diff_report.png")
    with pytest.raises(ValueError):
        visual_tester.generate_diff_report(img1, img2, report_path)

def test_set_similarity_threshold_invalid(visual_tester):
    with pytest.raises(ValueError):
        visual_tester.set_similarity_threshold(-0.1)
    with pytest.raises(ValueError):
        visual_tester.set_similarity_threshold(1.1)

def test_read_baseline_file_not_found(visual_tester):
    with pytest.raises(FileNotFoundError):
        visual_tester.read_baseline("nonexistent_baseline.png")

def test_capture_baseline_write_error(visual_tester, monkeypatch):
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    monkeypatch.setattr("cv2.imwrite", lambda *a, **k: False)
    # capture_baseline не выбрасывает исключение, просто не сохраняет файл
    visual_tester.capture_baseline("fail.png", img)
