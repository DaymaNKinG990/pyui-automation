"""
Tests for OCR engine
"""
import pytest
import numpy as np

from pyui_automation.ocr.engine import OCREngine


class TestOCREngine:
    """Test OCREngine class"""
    
    def test_init(self):
        """Test OCREngine initialization"""
        engine = OCREngine()
        assert engine._languages == ['en']
        assert engine._preprocessor is not None
    
    def test_set_languages(self):
        """Test set_languages method"""
        engine = OCREngine()
        engine.set_languages(['en', 'ru'])
        assert engine._languages == ['en', 'ru']
    
    def test_set_languages_empty(self):
        """Test set_languages with empty list"""
        engine = OCREngine()
        with pytest.raises(ValueError):
            engine.set_languages([])
    
    def test_preprocess_image(self):
        """Test preprocess_image method"""
        engine = OCREngine()
        image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = engine.preprocess_image(image)
        assert result is not None
        assert isinstance(result, np.ndarray)
    
    def test_recognize_text_without_paddleocr(self, mocker):
        """Test recognize_text when PaddleOCR is not available"""
        mocker.patch('importlib.util.find_spec', return_value=None)
        engine = OCREngine()
        
        result = engine.recognize_text(np.zeros((100, 100, 3), dtype=np.uint8))
        assert result == []
    
    def test_recognize_text_invalid_image(self):
        """Test recognize_text with invalid image"""
        engine = OCREngine()
        
        result = engine.recognize_text(None)
        assert result == []
    
    def test_recognize_text_empty_path(self):
        """Test recognize_text with empty path"""
        engine = OCREngine()
        
        result = engine.recognize_text("")
        assert result == []
    
    def test_find_text_location_without_paddleocr(self, mocker):
        """Test find_text_location when PaddleOCR is not available"""
        mocker.patch('importlib.util.find_spec', return_value=None)
        engine = OCREngine()
        mock_element = mocker.Mock()
        
        result = engine.find_text_location(mock_element, "test")
        assert result == []
    
    def test_get_all_text_without_paddleocr(self, mocker):
        """Test get_all_text when PaddleOCR is not available"""
        mocker.patch('importlib.util.find_spec', return_value=None)
        engine = OCREngine()
        mock_element = mocker.Mock()
        
        result = engine.get_all_text(mock_element)
        assert result == ""
    
    def test_verify_text_presence(self, mocker):
        """Test verify_text_presence method"""
        engine = OCREngine()
        mock_element = mocker.Mock()
        
        mocker.patch.object(engine, 'find_text_location', return_value=[(10, 20, 30, 40)])
        result = engine.verify_text_presence(mock_element, "test")
        assert result is True
        
        mocker.patch.object(engine, 'find_text_location', return_value=[])
        result = engine.verify_text_presence(mock_element, "test")
        assert result is False
    
    def test_read_text_without_paddleocr(self, mocker):
        """Test read_text when PaddleOCR is not available"""
        mocker.patch('importlib.util.find_spec', return_value=None)
        engine = OCREngine()
        mock_element = mocker.Mock()
        
        result = engine.read_text(mock_element, "test")
        assert result == ""
    
    def test_get_element_image(self, mocker):
        """Test _get_element_image method"""
        engine = OCREngine()
        mock_element = mocker.Mock()
        mock_image = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.capture_screenshot.return_value = mock_image
        
        result = engine._get_element_image(mock_element)
        assert result is not None
        assert isinstance(result, np.ndarray)
    
    def test_get_element_position(self, mocker):
        """Test _get_element_position method"""
        engine = OCREngine()
        mock_element = mocker.Mock()
        mock_element.location = {'x': 100, 'y': 200}
        
        x, y = engine._get_element_position(mock_element)
        assert x == 100
        assert y == 200
    
    def test_get_element_position_tuple(self, mocker):
        """Test _get_element_position with tuple location"""
        engine = OCREngine()
        mock_element = mocker.Mock()
        mock_element.location = (100, 200)
        
        x, y = engine._get_element_position(mock_element)
        assert x == 100
        assert y == 200 