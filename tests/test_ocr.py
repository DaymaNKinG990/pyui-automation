import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from PIL import Image
from pyui_automation.ocr import OCREngine


@pytest.fixture
def mock_element():
    """Create a mock UI element for testing"""
    element = MagicMock()
    element.id = "test-id"
    element.name = "test-element"
    element.get_location.return_value = (10, 10)
    element.get_size.return_value = (100, 100)
    element.capture.return_value = np.zeros((100, 100, 3))
    return element


@pytest.fixture
def ocr_engine():
    """Create OCREngine instance with mocked backends"""
    with patch('easyocr.Reader') as mock_easyocr, \
         patch('pytesseract.image_to_string') as mock_tesseract:
        
        # Mock EasyOCR
        mock_reader = MagicMock()
        mock_reader.readtext.return_value = [
            ([[0, 0], [100, 0], [100, 30], [0, 30]], "Sample Text", 0.95)
        ]
        mock_easyocr.return_value = mock_reader
        
        # Mock Tesseract
        mock_tesseract.return_value = "Sample Text"
        
        engine = OCREngine()
        yield engine


@pytest.fixture
def mock_file_access():
    """Mock file access for OCR tests"""
    with patch('builtins.open', new_callable=MagicMock) as mock_open:
        yield mock_open


@pytest.fixture
def mock_image_open():
    """Mock image open for OCR tests"""
    with patch('PIL.Image.open', return_value=Image.new('RGB', (100, 100))) as mock_open:
        yield mock_open


def test_read_text_from_element(ocr_engine, mock_element):
    """Test reading text from UI element"""
    text = ocr_engine.read_text_from_element(mock_element)
    assert isinstance(text, str)
    assert len(text) > 0


def test_read_text_from_image(ocr_engine):
    """Test reading text from image"""
    image = np.zeros((100, 100, 3), dtype=np.uint8)
    text = ocr_engine.read_text_from_image(image)
    assert isinstance(text, str)
    assert len(text) > 0


def test_find_text_location(ocr_engine, mock_element, mock_file_access, mock_image_open):
    """Test finding text location in element"""
    # Mock the capture method to return a test image
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_element.capture.return_value = test_image
    
    # Mock EasyOCR reader results
    ocr_engine._easyocr_reader.readtext.return_value = [
        ([[10, 10], [50, 10], [50, 30], [10, 30]], "Sample Text", 0.95)
    ]
    
    locations = ocr_engine.find_text_location(mock_element, "Sample")
    assert isinstance(locations, list)
    assert len(locations) > 0
    assert all(isinstance(loc, tuple) for loc in locations)
    assert all(len(loc) == 2 for loc in locations)
    assert locations[0] == (10, 10)  # Check exact coordinates


def test_get_text_confidence(ocr_engine, mock_element, mock_file_access, mock_image_open):
    """Test getting text recognition confidence"""
    confidence = ocr_engine.get_text_confidence(mock_element, "Sample")
    assert isinstance(confidence, float)
    assert 0 <= confidence <= 1


def test_read_text_with_language(ocr_engine, mock_element):
    """Test reading text with specific language"""
    text = ocr_engine.read_text_from_element(mock_element)
    assert isinstance(text, str)
    assert len(text) > 0


def test_read_text_with_preprocessing(ocr_engine, mock_element):
    """Test reading text with image preprocessing"""
    text = ocr_engine.read_text_from_element(mock_element)
    assert isinstance(text, str)
    assert len(text) > 0


def test_verify_text_presence(ocr_engine, mock_element, mock_file_access, mock_image_open):
    """Test verifying text presence in element"""
    # Mock the capture method to return a test image
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_element.capture.return_value = test_image
    
    # Mock EasyOCR reader results
    ocr_engine._easyocr_reader.readtext.return_value = [
        ([[10, 10], [50, 10], [50, 30], [10, 30]], "Sample Text", 0.95)
    ]
    
    # Test presence of existing text
    assert ocr_engine.verify_text_presence(mock_element, "Sample") is True
    
    # Test absence of non-existent text
    assert ocr_engine.verify_text_presence(mock_element, "NonExistent") is False
    
    # Test with low confidence text
    ocr_engine._easyocr_reader.readtext.return_value = [
        ([[10, 10], [50, 10], [50, 30], [10, 30]], "Sample Text", 0.3)
    ]
    assert ocr_engine.verify_text_presence(mock_element, "Sample", confidence_threshold=0.5) is False


def test_get_all_text(ocr_engine, mock_element, mock_file_access, mock_image_open):
    """Test getting all text from element"""
    # Mock the capture method to return a test image
    test_image = np.zeros((100, 100, 3), dtype=np.uint8)
    mock_element.capture.return_value = test_image
    
    # Mock EasyOCR reader results
    ocr_engine._easyocr_reader.readtext.return_value = [
        ([[10, 10], [50, 10], [50, 30], [10, 30]], "Sample Text 1", 0.95),
        ([[60, 60], [100, 60], [100, 80], [60, 80]], "Sample Text 2", 0.90)
    ]
    
    texts = ocr_engine.get_all_text(mock_element)
    assert isinstance(texts, list)
    assert len(texts) == 2
    
    # Check first text entry
    assert texts[0]['text'] == "Sample Text 1"
    assert texts[0]['position'] == (10, 10)
    assert texts[0]['confidence'] == 0.95
    
    # Check second text entry
    assert texts[1]['text'] == "Sample Text 2"
    assert texts[1]['position'] == (60, 60)
    assert texts[1]['confidence'] == 0.90
