"""
Tests for OCR engine functionality
"""
import pytest
import numpy as np
from pathlib import Path

from pyui_automation.ocr.engine import OCREngine, OCRResult, OCRConfig
from pyui_automation.elements.base_element import BaseElement


class TestOCREngineInitialization:
    """Test OCREngine initialization"""
    
    def test_init_paddle_ocr_when_available(self, mocker):
        """Test initialization when PaddleOCR is available"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        with mocker.patch('builtins.__import__') as mock_import:
            mock_paddle_ocr = mocker.Mock()
            mock_import.return_value = mock_paddle_ocr
            
            engine = OCREngine()
            assert engine._paddle_ocr is not None
    
    def test_init_paddle_ocr_when_not_available(self, mocker):
        """Test initialization when PaddleOCR is not available"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = None
        
        engine = OCREngine()
        assert engine._paddle_ocr is None
    
    def test_init_paddle_ocr_import_error(self, mocker):
        """Test initialization with import error"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.side_effect = ImportError("PaddleOCR not found")
        
        engine = OCREngine()
        assert engine._paddle_ocr is None


class TestOCREngineSetLanguages:
    """Test language setting"""
    
    def test_set_languages_with_valid_languages(self, mocker):
        """Test setting valid languages"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        engine = OCREngine()
        engine.set_languages(['en', 'ru'])
        assert engine._languages == ['en', 'ru']
    
    def test_set_languages_with_empty_list(self, mocker):
        """Test setting empty languages list"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        engine = OCREngine()
        with pytest.raises(ValueError, match="Languages list cannot be empty"):
            engine.set_languages([])


class TestOCREngineRecognizeText:
    """Test text recognition"""
    
    def test_recognize_text_with_file_path(self, mocker):
        """Test recognizing text from file path"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        with mocker.patch('pyui_automation.ocr.engine.load_image') as mock_load_image:
            # Create a proper image array for OpenCV (uint8, 3 channels)
            mock_load_image.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
            
            engine = OCREngine()
            # Mock the OCR result
            engine._paddle_ocr = mocker.Mock()
            engine._paddle_ocr.ocr.return_value = [[
                ([[0, 0], [10, 0], [10, 10], [0, 10]], ('Hello World', 0.9))
            ]]
            
            result = engine.recognize_text('test.png')
            assert result == "Hello World"
    
    def test_recognize_text_with_numpy_array(self, mocker):
        """Test recognizing text from numpy array"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        engine = OCREngine()
        # Mock the OCR result
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = [[
            ([[0, 0], [10, 0], [10, 10], [0, 10]], ('Hello World', 0.9))
        ]]
        
        # Create a proper image array for OpenCV (uint8, 3 channels)
        test_image = np.zeros((100, 100, 3), dtype=np.uint8)
        result = engine.recognize_text(test_image)
        assert result == "Hello World"
    
    def test_recognize_text_with_file_not_found(self, mocker):
        """Test recognizing text with file not found"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()

        with mocker.patch('pyui_automation.ocr.engine.load_image', return_value=None):
            engine = OCREngine()
            with pytest.raises(FileNotFoundError, match="Image file not found: nonexistent.png"):
                result = engine.recognize_text('nonexistent.png')
    
    def test_recognize_text_with_none_image(self, mocker):
        """Test recognizing text with None image"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()

        engine = OCREngine()
        with pytest.raises(ValueError, match="Image cannot be None"):
            result = engine.recognize_text(None)
    
    def test_recognize_text_with_empty_path(self, mocker):
        """Test recognizing text with empty path"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        engine = OCREngine()
        with pytest.raises(ValueError, match="Image path cannot be empty"):
            engine.recognize_text("")
    
    def test_recognize_text_with_paddle_ocr_not_available(self, mocker):
        """Test recognizing text when PaddleOCR is not available"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = None
        
        engine = OCREngine()
        with pytest.raises(RuntimeError, match="PaddleOCR is not available"):
            # Create a proper image array for OpenCV (uint8, 3 channels)
            engine.recognize_text(np.zeros((100, 100, 3), dtype=np.uint8))


class TestOCREngineFindTextLocation:
    """Test finding text location"""
    
    def test_find_text_location_with_found_text(self, mocker):
        """Test finding text location when text is found"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        engine = OCREngine()
        # Mock the OCR result
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = [[
            ([[0, 0], [10, 0], [10, 10], [0, 10]], ('Hello', 0.9))
        ]]
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        locations = engine.find_text_location(mock_element, 'Hello')
        assert len(locations) == 1
        assert locations[0][0] == 100  # x + element_x
        assert locations[0][1] == 200  # y + element_y
    
    def test_find_text_location_with_text_not_found(self, mocker):
        """Test finding text location when text is not found"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        engine = OCREngine()
        # Mock the OCR result - no matches
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = []
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        locations = engine.find_text_location(mock_element, 'Nonexistent')
        assert len(locations) == 0
    
    def test_find_text_location_with_low_confidence(self, mocker):
        """Test finding text location with low confidence"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        engine = OCREngine()
        # Mock the OCR result with low confidence
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = [[
            ([[0, 0], [10, 0], [10, 10], [0, 10]], ('Hello', 0.3))  # Low confidence
        ]]
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        locations = engine.find_text_location(mock_element, 'Hello', confidence_threshold=0.5)
        assert len(locations) == 0


class TestOCREngineGetAllText:
    """Test getting all text"""
    
    def test_get_all_text_with_multiple_texts(self, mocker):
        """Test getting all text with multiple texts"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        engine = OCREngine()
        # Mock the OCR result
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = [[
            ([[0, 0], [10, 0], [10, 10], [0, 10]], ('Hello', 0.9)),
            ([[20, 0], [30, 0], [30, 10], [20, 10]], ('World', 0.8))
        ]]
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        texts = engine.get_all_text(mock_element)
        assert len(texts) == 2
        assert any(text['text'] == 'Hello' for text in texts)
        assert any(text['text'] == 'World' for text in texts)


class TestOCREngineVerifyTextPresence:
    """Test text presence verification"""
    
    def test_verify_text_presence_with_text_found(self, mocker):
        """Test verifying text presence when text is found"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        engine = OCREngine()
        # Mock the OCR result
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = [[
            ([[0, 0], [10, 0], [10, 10], [0, 10]], ('Hello', 0.9))
        ]]
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        result = engine.verify_text_presence(mock_element, 'Hello')
        assert result is True
    
    def test_verify_text_presence_with_text_not_found(self, mocker):
        """Test verifying text presence when text is not found"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        engine = OCREngine()
        # Mock the OCR result - no matches
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = []
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        result = engine.verify_text_presence(mock_element, 'Nonexistent')
        assert result is False


class TestOCREngineReadText:
    """Test reading text"""
    
    def test_read_text_with_exact_match(self, mocker):
        """Test reading text with exact match"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = [[
            ([[0, 0], [10, 0], [10, 10], [0, 10]], ('Hello World', 0.9))
        ]]
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = engine.read_text(mock_element, 'Hello World', exact_match=True)
        assert result == 'Hello World'
    
    def test_read_text_with_case_insensitive(self, mocker):
        """Test reading text with case insensitive match"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = [[
            ([[0, 0], [10, 0], [10, 10], [0, 10]], ('hello world', 0.9))
        ]]
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = engine.read_text(mock_element, 'Hello World', exact_match=False)
        assert result == 'hello world'
    
    def test_read_text_with_text_not_found(self, mocker):
        """Test reading text when not found"""
        mock_find_spec = mocker.patch('importlib.util.find_spec')
        mock_find_spec.return_value = mocker.Mock()
        
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = []
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = engine.read_text(mock_element, 'NotFound', exact_match=True)
        assert result == ''


class TestOCREnginePreprocessImage:
    """Tests for preprocess_image method"""
    
    def test_preprocess_image(self, mocker, sample_image):
        """Test preprocess_image method"""
        engine = OCREngine()
        result = engine.preprocess_image(sample_image)
        
        assert isinstance(result, np.ndarray)
        assert result.shape == sample_image.shape


class TestOCREngineHelperMethods:
    """Test helper methods"""
    
    def test_get_element_image_with_valid_element(self, mocker):
        """Test getting element image with valid element"""
        engine = OCREngine()
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = engine._get_element_image(mock_element)
        assert result is not None
        assert isinstance(result, np.ndarray)
    
    def test_get_element_position_with_valid_element(self, mocker):
        """Test getting element position with valid element"""
        engine = OCREngine()
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.location = {'x': 100, 'y': 200}
        
        x, y = engine._get_element_position(mock_element)
        assert x == 100
        assert y == 200
    
    def test_get_element_position_with_exception(self, mocker):
        """Test getting element position with exception"""
        engine = OCREngine()
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.location = None
        
        result = engine._get_element_position(mock_element)
        assert result == (0, 0)


class TestOCREngineErrorHandling:
    """Test error handling in OCREngine"""
    
    def test_recognize_text_with_paddle_ocr_not_available(self, mocker):
        """Test recognizing text when PaddleOCR is not available"""
        engine = OCREngine()
        engine._paddle_ocr = None
        
        with pytest.raises(RuntimeError, match="PaddleOCR is not available"):
            engine.recognize_text('test.png')
    
    def test_find_text_location_with_paddle_ocr_not_available(self, mocker):
        """Test finding text location when PaddleOCR is not available"""
        engine = OCREngine()
        engine._paddle_ocr = None
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with pytest.raises(RuntimeError, match="PaddleOCR is not available"):
            engine.find_text_location(mock_element, 'Hello')
    
    def test_get_all_text_with_paddle_ocr_not_available(self, mocker):
        """Test getting all text when PaddleOCR is not available"""
        engine = OCREngine()
        engine._paddle_ocr = None
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with pytest.raises(RuntimeError, match="PaddleOCR is not available"):
            engine.get_all_text(mock_element)
    
    def test_read_text_with_paddle_ocr_not_available(self, mocker):
        """Test reading text when PaddleOCR is not available"""
        engine = OCREngine()
        engine._paddle_ocr = None
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        with pytest.raises(RuntimeError, match="PaddleOCR is not available"):
            engine.read_text(mock_element, 'Hello')
    
    def test_find_text_location_with_no_element_image(self, mocker):
        """Test finding text location with no element image"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = None
        
        locations = engine.find_text_location(mock_element, 'Hello')
        assert len(locations) == 0
    
    def test_get_all_text_with_no_element_image(self, mocker):
        """Test getting all text with no element image"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = None
        
        texts = engine.get_all_text(mock_element)
        assert len(texts) == 0
    
    def test_read_text_with_no_element_image(self, mocker):
        """Test reading text with no element image"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = None
        
        result = engine.read_text(mock_element, 'Hello')
        assert result == ""
    
    def test_find_text_location_with_ocr_exception(self, mocker):
        """Test find_text_location when OCR raises an exception"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.side_effect = Exception("OCR failed")
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        # Exception should propagate since there's no error handling
        with pytest.raises(Exception, match="OCR failed"):
            engine.find_text_location(mock_element, 'Hello')

    def test_get_all_text_with_ocr_exception(self, mocker):
        """Test get_all_text when OCR raises an exception"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.side_effect = Exception("OCR failed")
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        # Exception should propagate since there's no error handling
        with pytest.raises(Exception, match="OCR failed"):
            engine.get_all_text(mock_element)

    def test_read_text_with_ocr_exception(self, mocker):
        """Test read_text when OCR raises an exception"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.side_effect = Exception("OCR failed")
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        # Exception should propagate since there's no error handling
        with pytest.raises(Exception, match="OCR failed"):
            engine.read_text(mock_element, 'Hello')


class TestOCREngineEdgeCases:
    """Test edge cases in OCREngine"""
    
    def test_find_text_location_with_empty_ocr_result(self, mocker):
        """Test finding text location with empty OCR result"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = []
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        locations = engine.find_text_location(mock_element, 'Hello')
        assert len(locations) == 0
    
    def test_get_all_text_with_empty_ocr_result(self, mocker):
        """Test getting all text with empty OCR result"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = []
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        texts = engine.get_all_text(mock_element)
        assert len(texts) == 0
    
    def test_read_text_with_empty_ocr_result(self, mocker):
        """Test reading text with empty OCR result"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = []
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = engine.read_text(mock_element, 'Hello')
        assert result == ""
    
    def test_find_text_location_with_none_ocr_result(self, mocker):
        """Test finding text location with None OCR result"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = None
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        locations = engine.find_text_location(mock_element, 'Hello')
        assert len(locations) == 0
    
    def test_get_all_text_with_none_ocr_result(self, mocker):
        """Test getting all text with None OCR result"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = None
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        texts = engine.get_all_text(mock_element)
        assert len(texts) == 0
    
    def test_read_text_with_none_ocr_result(self, mocker):
        """Test reading text with None OCR result"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = None
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = engine.read_text(mock_element, 'Hello')
        assert result == ""
    
    def test_find_text_location_with_empty_first_line(self, mocker):
        """Test finding text location with empty first line in OCR result"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = [[]]
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        locations = engine.find_text_location(mock_element, 'Hello')
        assert len(locations) == 0
    
    def test_get_all_text_with_empty_first_line(self, mocker):
        """Test getting all text with empty first line in OCR result"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = [[]]
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        mock_element.location = {'x': 100, 'y': 200}
        
        texts = engine.get_all_text(mock_element)
        assert len(texts) == 0
    
    def test_read_text_with_empty_first_line(self, mocker):
        """Test reading text with empty first line in OCR result"""
        engine = OCREngine()
        engine._paddle_ocr = mocker.Mock()
        engine._paddle_ocr.ocr.return_value = [[]]
        
        mock_element = mocker.Mock(spec=BaseElement)
        mock_element.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
        
        result = engine.read_text(mock_element, 'Hello')
        assert result == "" 