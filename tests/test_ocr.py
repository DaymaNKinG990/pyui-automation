import pytest
import numpy as np
from unittest.mock import MagicMock, patch
import cv2
from pathlib import Path
from paddleocr import PaddleOCR


# Mock PIL.Image
pil_mock = MagicMock()
class MockImage:
    @staticmethod
    def fromarray(arr):
        return arr
        
    @staticmethod
    def open(fp):
        # Return a mock image that can be converted to numpy array
        mock_img = MagicMock()
        mock_img.__array__ = lambda: np.zeros((100, 100, 3), dtype=np.uint8)
        return mock_img

# Add the open method directly to the mock module
pil_mock.open = MockImage.open
pil_mock.Image = MockImage

# Mock PaddleOCR
paddle_mock = MagicMock()


class MockPaddleOCR(PaddleOCR):
    def __init__(self, use_angle_cls=True, lang='en', show_log=False):
        pass
        
    def ocr(self, img, det=True, rec=True, cls=True, bin=False, inv=False, alpha_color=(0, 0, 0), slice=None, lang='ch'):
        return [[
            [
                [[10, 10], [50, 10], [50, 30], [10, 30]],  # Bounding box
                ("Sample Text 1", 0.99)  # Text and confidence
            ],
            [
                [[60, 10], [100, 10], [100, 30], [60, 30]],  # Bounding box
                ("Sample Text 2", 0.95)  # Text and confidence
            ]
        ]]


paddle_mock.PaddleOCR = MockPaddleOCR

# Create patch objects
patches = {
    'PIL.Image': patch.dict('sys.modules', {'PIL.Image': pil_mock}),
    'paddleocr': patch.dict('sys.modules', {'paddleocr': paddle_mock})
}


@pytest.fixture
def mock_element():
    """Create a mock UI element for testing"""
    element = MagicMock()
    element.capture.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
    element.get_location.return_value = (0, 0)
    return element

@pytest.fixture
def ocr_engine():
    """Create OCREngine instance with mocked PaddleOCR"""
    with patches['PIL.Image'], patches['paddleocr']:
        from pyui_automation.ocr import OCREngine
        global HAS_PADDLE
        HAS_PADDLE = True  # Force PaddleOCR availability
        engine = OCREngine()
        engine._paddle_ocr = MockPaddleOCR()  # Directly set the mock instance
        yield engine

def test_read_text_from_element(ocr_engine, mock_element):
    """Test reading text from UI element"""
    text = ocr_engine.read_text_from_element(mock_element)
    assert text == "Sample Text 1 Sample Text 2"

def test_find_text_location(ocr_engine, mock_element):
    """Test finding text location"""
    location = ocr_engine.find_text_location(mock_element, "Sample Text 1")
    assert location == (30, 20)  # Center point of first bbox

def test_get_all_text(ocr_engine, mock_element):
    """Test getting all text from element"""
    texts = ocr_engine.get_all_text(mock_element)
    assert len(texts) == 2
    assert texts[0] == {
        'text': 'Sample Text 1',
        'confidence': 0.99,
        'position': (30, 20)  # Center of first bbox
    }
    assert texts[1] == {
        'text': 'Sample Text 2',
        'confidence': 0.95,
        'position': (80, 20)  # Center of second bbox
    }

def test_recognize_text(ocr_engine):
    """Test recognizing text from image array"""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    text = ocr_engine.recognize_text(image)
    assert text == "Sample Text 1 Sample Text 2"

def test_recognize_text_with_preprocessing(ocr_engine):
    """Test text recognition with preprocessing"""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    text = ocr_engine.recognize_text(image, preprocess=True)
    assert text == "Sample Text 1 Sample Text 2"

def test_paddle_ocr_not_available():
    """Test behavior when PaddleOCR is not available"""
    with patches['PIL.Image'], patches['paddleocr']:
        # Import and reload to ensure fresh state
        import pyui_automation.ocr
        import sys
        if 'pyui_automation.ocr' in sys.modules:
            del sys.modules['pyui_automation.ocr']
        import pyui_automation.ocr
        
        # Set PaddleOCR as not available
        pyui_automation.ocr.HAS_PADDLE = False
        
        # Create engine and verify it raises error
        engine = pyui_automation.ocr.OCREngine()
        with pytest.raises(RuntimeError, match="PaddleOCR not available"):
            engine.recognize_text(np.zeros((100, 100, 3), dtype=np.uint8))

def test_set_languages(ocr_engine):
    """Test setting OCR languages"""
    languages = ['en', 'fr', 'de']
    ocr_engine.set_languages(languages)
    assert ocr_engine._languages == languages
    assert ocr_engine._paddle_ocr is not None

def test_set_languages_empty_list(ocr_engine):
    """Test setting empty languages list"""
    with pytest.raises(ValueError, match="Languages list cannot be empty"):
        ocr_engine.set_languages([])

def test_recognize_text_from_path(ocr_engine, tmp_path):
    """Test recognizing text from image path"""
    # Create a test image file
    image_path = tmp_path / "test_image.png"
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(image_path), test_image)
    
    text = ocr_engine.recognize_text(image_path)
    assert isinstance(text, str)
    assert "Sample Text" in text

def test_recognize_text_from_pathlib(ocr_engine, tmp_path):
    """Test recognizing text from pathlib.Path"""
    image_path = tmp_path / "test_image.png"
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    cv2.imwrite(str(image_path), test_image)
    
    text = ocr_engine.recognize_text(Path(image_path))
    assert isinstance(text, str)
    assert "Sample Text" in text

def test_recognize_text_invalid_path(ocr_engine):
    """Test recognizing text from invalid path"""
    with pytest.raises(FileNotFoundError):
        ocr_engine.recognize_text("nonexistent_image.png")

def test_recognize_text_invalid_image(ocr_engine):
    """Test recognizing text from invalid image data"""
    with pytest.raises(ValueError):
        ocr_engine.recognize_text(np.array([]))

def test_find_text_with_confidence(ocr_engine, mock_element):
    """Test finding text with confidence threshold"""
    locations = ocr_engine.find_text_location(mock_element, "Sample Text", confidence_threshold=0.9)
    assert isinstance(locations, list)
    assert len(locations) > 0
    assert all(isinstance(loc, tuple) for loc in locations)

def test_find_text_no_match(ocr_engine, mock_element):
    """Test finding text with no matches"""
    locations = ocr_engine.find_text_location(mock_element, "Nonexistent Text")
    assert isinstance(locations, list)
    assert len(locations) == 0

def test_get_all_text_with_confidence(ocr_engine, mock_element):
    """Test getting all text with confidence threshold"""
    texts = ocr_engine.get_all_text(mock_element, confidence_threshold=0.95)
    assert isinstance(texts, list)
    assert len(texts) == 2  # Both texts have confidence >= 0.95
    assert "Sample Text 1" in texts[0]
    assert "Sample Text 2" in texts[1]

def test_get_all_text_no_results(ocr_engine, mock_element):
    """Test getting all text with no results"""
    # Mock OCR to return empty results
    with patch.object(ocr_engine._paddle_ocr, 'ocr', return_value=[[]]):
        texts = ocr_engine.get_all_text(mock_element)
        assert isinstance(texts, list)
        assert len(texts) == 0

def test_preprocess_image(ocr_engine):
    """Test image preprocessing"""
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    processed = ocr_engine._preprocess_image(test_image)
    assert isinstance(processed, np.ndarray)
    assert processed.shape == test_image.shape

def test_preprocess_image_grayscale(ocr_engine):
    """Test preprocessing grayscale image"""
    test_image = np.zeros((100, 100), dtype=np.uint8)
    processed = ocr_engine._preprocess_image(test_image)
    assert isinstance(processed, np.ndarray)
    assert len(processed.shape) == 3  # Should be converted to RGB

def test_read_text_partial_match(ocr_engine, mock_element):
    """Test reading text with partial match"""
    text = ocr_engine.read_text(mock_element, "Sample")
    assert isinstance(text, str)
    assert "Sample Text" in text

def test_read_text_case_sensitive(ocr_engine, mock_element):
    """Test reading text with case sensitivity"""
    text = ocr_engine.read_text(mock_element, "SAMPLE TEXT", case_sensitive=True)
    assert text == ""  # Should not match due to case sensitivity

def test_read_text_exact_match(ocr_engine, mock_element):
    """Test reading text with exact match"""
    text = ocr_engine.read_text(mock_element, "Sample Text 1", exact_match=True)
    assert text == "Sample Text 1"

def test_multiple_language_recognition(ocr_engine, mock_element):
    """Test recognition with multiple languages"""
    languages = ['en', 'fr']
    ocr_engine.set_languages(languages)
    text = ocr_engine.read_text(mock_element, "Sample")
    assert isinstance(text, str)
    assert "Sample Text" in text

@pytest.mark.parametrize("image_type", [
    np.uint8,
    np.float32,
    np.float64
])
def test_recognize_text_different_dtypes(ocr_engine, image_type):
    """Test recognizing text from images with different dtypes"""
    test_image = np.zeros((100, 100, 3), dtype=image_type)
    text = ocr_engine.recognize_text(test_image)
    assert isinstance(text, str)

def test_concurrent_ocr_operations(ocr_engine, mock_element):
    """Test concurrent OCR operations"""
    import threading
    
    def ocr_operation():
        for _ in range(5):
            ocr_engine.read_text(mock_element, "Sample")
    
    threads = [threading.Thread(target=ocr_operation) for _ in range(3)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

def test_memory_cleanup(ocr_engine):
    """Test memory cleanup after OCR operations"""
    import gc
    initial_objects = len(gc.get_objects())
    
    # Perform multiple OCR operations
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    for _ in range(10):
        ocr_engine.recognize_text(test_image)
    
    # Force garbage collection
    gc.collect()
    final_objects = len(gc.get_objects())
    
    # Check that we don't have a significant memory leak
    assert final_objects - initial_objects < 1000  # Arbitrary threshold
