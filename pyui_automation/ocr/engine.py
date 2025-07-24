"""
OCR Engine - Main OCR implementation using PaddleOCR

This module provides the main OCR engine implementation using PaddleOCR.
Follows SRP by focusing only on text recognition.
"""

import cv2
import numpy as np
import logging
from pathlib import Path
from typing import List, Union, Optional, Dict, Any, Tuple, TYPE_CHECKING

from ..core.interfaces.iocr_service import IOCRService
from ..elements.base_element import BaseElement
from ..utils import (
    load_image, validate_type, validate_not_none, 
    validate_string_not_empty, retry
)
from .preprocessing import ImagePreprocessor

if TYPE_CHECKING:
    from paddleocr import PaddleOCR


class OCREngine(IOCRService):
    """
    Main OCR Engine using PaddleOCR.
    
    Single Responsibility: Text recognition using PaddleOCR.
    """
    
    def __init__(self) -> None:
        """Initialize OCR engine with PaddleOCR"""
        self._paddle_ocr: Optional['PaddleOCR'] = None
        self._languages = ['en']
        self._preprocessor = ImagePreprocessor()
        
        # Check if PaddleOCR is available
        self._init_paddle_ocr()
    
    def _init_paddle_ocr(self) -> None:
        """Initialize PaddleOCR if available"""
        try:
            import importlib
            try:
                import importlib.util
                paddle_spec = importlib.util.find_spec('paddleocr')
            except ImportError:
                paddle_spec = None
            if paddle_spec is not None:
                from paddleocr import PaddleOCR
                self._paddle_ocr = PaddleOCR(
                    use_angle_cls=True, 
                    lang=self._languages[0], 
                    show_log=False
                )
                logging.info("PaddleOCR initialized successfully")
            else:
                logging.warning("PaddleOCR not available. Install with: pip install paddleocr")
        except ImportError as e:
            logging.warning(f"Failed to import PaddleOCR: {e}")
            self._paddle_ocr = None
    
    def set_languages(self, languages: List[str]) -> None:
        """Set languages for OCR recognition"""
        if not languages:
            raise ValueError("Languages list cannot be empty")
        
        self._languages = languages
        
        # Reinitialize PaddleOCR with new language
        if self._paddle_ocr is not None:
            try:
                from paddleocr import PaddleOCR
                self._paddle_ocr = PaddleOCR(
                    use_angle_cls=True, 
                    lang=languages[0], 
                    show_log=False
                )
            except ImportError:
                logging.warning("Failed to reinitialize PaddleOCR with new language")
    
    @retry(attempts=2, delay=0.5)
    def recognize_text(self, image: Union[Path, str, np.ndarray], preprocess: bool = False) -> str:
        """Recognize text in an image"""
        if not self._paddle_ocr:
            raise RuntimeError("PaddleOCR is not available. Install with: pip install paddleocr")
        
        # Validate input
        if not validate_not_none(image):
            raise ValueError("Image cannot be None")
        
        # Load image if path provided
        if isinstance(image, (str, Path)):
            if not validate_string_not_empty(str(image)):
                raise ValueError("Image path cannot be empty")
            
            loaded_image = load_image(Path(image))
            if loaded_image is None:
                raise FileNotFoundError(f"Image file not found: {image}")
            
            image = cv2.cvtColor(loaded_image, cv2.COLOR_BGR2RGB)
        
        # Validate image
        if not validate_type(image, np.ndarray) or image.size == 0:
            raise ValueError("Image must be a non-empty numpy array")
        
        # Preprocess if requested
        if preprocess:
            image = self._preprocessor.preprocess(image)
        
        # Perform OCR
        result = self._paddle_ocr.ocr(image, cls=True)
        
        if not result or not result[0]:
            return ""
        
        # Extract text
        texts = [line[1][0] for line in result[0]]
        return " ".join(texts)
    
    def find_text_location(self, element: BaseElement, text: str, confidence_threshold: float = 0.5) -> List[Tuple[int, int, int, int]]:
        """Find location(s) of text within element"""
        if not self._paddle_ocr:
            raise RuntimeError("PaddleOCR is not available")
        
        # Get element screenshot
        image = self._get_element_image(element)
        if image is None:
            return []
        
        # Get element position
        element_x, element_y = self._get_element_position(element)
        
        # Perform OCR
        result = self._paddle_ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return []
        
        # Find matching text
        locations = []
        for line in result[0]:
            bbox, (detected_text, confidence) = line
            
            if detected_text == text and confidence >= confidence_threshold:
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                width = abs(x2 - x1)
                height = abs(y2 - y1)
                x = x1 + element_x
                y = y1 + element_y
                locations.append((int(x), int(y), int(width), int(height)))
        
        return locations
    
    def get_all_text(self, element: BaseElement, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Get all text from element with positions"""
        if not self._paddle_ocr:
            raise RuntimeError("PaddleOCR is not available")
        
        # Get element screenshot
        image = self._get_element_image(element)
        if image is None:
            return []
        
        # Get element position
        element_x, element_y = self._get_element_position(element)
        
        # Perform OCR
        result = self._paddle_ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return []
        
        # Extract all text with positions
        texts = []
        for line in result[0]:
            bbox, (text, confidence) = line
            
            if confidence >= confidence_threshold:
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                center_x = int((x1 + x2) / 2 + element_x)
                center_y = int((y1 + y2) / 2 + element_y)
                
                texts.append({
                    'text': text,
                    'confidence': confidence,
                    'position': (center_x, center_y)
                })
        
        return texts
    
    def verify_text_presence(self, element: BaseElement, text: str, confidence_threshold: float = 0.5) -> bool:
        """Verify presence of text in element"""
        locations = self.find_text_location(element, text, confidence_threshold)
        return len(locations) > 0
    
    def read_text(self, element: BaseElement, text: str, case_sensitive: bool = False, exact_match: bool = False) -> str:
        """Read text from element and search for specific pattern"""
        if not self._paddle_ocr:
            raise RuntimeError("PaddleOCR is not available")
        
        # Get element screenshot
        image = self._get_element_image(element)
        if image is None:
            return ""
        
        # Perform OCR
        result = self._paddle_ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return ""
        
        # Search for matching text
        for line in result[0]:
            detected_text = line[1][0]
            
            # Handle case sensitivity
            search_text = text if case_sensitive else text.lower()
            compare_text = detected_text if case_sensitive else detected_text.lower()
            
            # Check for match
            if exact_match:
                if compare_text == search_text:
                    return detected_text
            else:
                if search_text in compare_text:
                    return detected_text
        
        return ""
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        return self._preprocessor.preprocess(image)
    
    def _get_element_image(self, element: BaseElement) -> Optional[np.ndarray]:
        """Get image from element"""
        try:
            if hasattr(element, 'capture_screenshot'):
                return element.capture_screenshot()
            elif hasattr(element, 'capture'):
                return element.capture_screenshot() if hasattr(element, 'capture_screenshot') else None
            elif hasattr(element, '_screenshot'):
                return getattr(element, '_screenshot', None) if hasattr(element, '_screenshot') else None
            else:
                logging.warning("Element does not support screenshot capture")
                return None
        except Exception as e:
            logging.warning(f"Failed to capture element screenshot: {e}")
            return None
    
    def _get_element_position(self, element: BaseElement) -> Tuple[int, int]:
        """Get element position"""
        try:
            if hasattr(element, 'location'):
                loc = element.location
                if isinstance(loc, dict):
                    return loc.get('x', 0), loc.get('y', 0)
                elif isinstance(loc, (tuple, list)) and len(loc) >= 2:
                    return loc[0], loc[1]
            elif hasattr(element, 'get_location'):
                loc = element.location if hasattr(element, 'location') else None
                if isinstance(loc, dict):
                    return loc.get('x', 0), loc.get('y', 0)
                elif isinstance(loc, (tuple, list)) and len(loc) >= 2:
                    return loc[0], loc[1]
        except Exception as e:
            logging.warning(f"Failed to get element position: {e}")
        
        return 0, 0 