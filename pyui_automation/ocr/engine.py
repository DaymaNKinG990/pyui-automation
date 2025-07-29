"""
OCR Engine - Real OCR implementation using PaddleOCR

This module provides real OCR functionality using PaddleOCR.
Follows SRP by handling OCR text recognition and processing.
"""

import logging
import cv2
from numpy.typing import NDArray
from typing import List, Union, Optional, Dict, Any, Tuple
from pathlib import Path

from ..core.interfaces.iocr_service import IOCRService
from ..elements.base_element import BaseElement
from ..utils.core import retry
from .preprocessing import ImagePreprocessor


class OCREngine(IOCRService):
    """
    Real OCR engine using PaddleOCR.
    
    Single Responsibility: Perform OCR text recognition using PaddleOCR.
    """
    
    def __init__(self) -> None:
        """Initialize OCR engine"""
        self._paddle_ocr: Optional[Any] = None
        self._preprocessor = ImagePreprocessor()
        self._languages = ["en"]
        self._init_paddle_ocr()
    
    def _init_paddle_ocr(self) -> None:
        """Initialize PaddleOCR"""
        try:
            from paddleocr import PaddleOCR
            self._paddle_ocr = PaddleOCR(
                use_angle_cls=True,
                lang='en',
                show_log=False
            )
            logging.info("PaddleOCR initialized successfully")
        except ImportError:
            logging.warning("PaddleOCR not available. Install with: pip install paddlepaddle paddleocr")
            self._paddle_ocr = None
        except Exception as e:
            logging.error(f"Failed to initialize PaddleOCR: {e}")
            self._paddle_ocr = None
    
    def set_languages(self, languages: List[str]) -> None:
        """Set OCR languages"""
        if not languages:
            raise ValueError("Languages list cannot be empty")
        
        # PaddleOCR supports multiple languages
        supported_langs = ["en", "ch", "french", "german", "korean", "japan"]
        valid_langs = [lang for lang in languages if lang in supported_langs]
        
        if not valid_langs:
            logging.warning(f"No supported languages found in {languages}. Using 'en'")
            self._languages = ["en"]
        else:
            self._languages = valid_langs
            
        # Reinitialize with new language if PaddleOCR is available
        if self._paddle_ocr:
            self._init_paddle_ocr()
    
    @retry(attempts=2, delay=0.5)
    def recognize_text(self, image: Union[Path, str, NDArray[Any]], preprocess: bool = False) -> str:
        """Recognize text in an image"""
        if not self._paddle_ocr:
            raise RuntimeError("PaddleOCR is not available")
        
        # Load image if path provided
        if isinstance(image, (str, Path)):
            image_path = str(image)
            if not Path(image_path).exists():
                raise FileNotFoundError(f"Image file not found: {image_path}")
            loaded_image: Optional[NDArray[Any]] = cv2.imread(image_path)
            if loaded_image is None:
                raise ValueError(f"Failed to load image: {image_path}")
            image = loaded_image
        
        # Preprocess if requested
        if preprocess:
            image = self._preprocessor.preprocess(image)
        
        # Perform OCR
        result: List[Any] = self._paddle_ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return ""
        
        # Extract text
        texts: List[str] = []
        for line in result[0]:
            _, (text, confidence) = line
            if confidence >= 0.5:  # Minimum confidence threshold
                texts.append(text)
        
        return " ".join(texts)
    
    def find_text_location(self, element: BaseElement, text: str, confidence_threshold: float = 0.5) -> List[Tuple[int, int, int, int]]:
        """Find location(s) of text within element"""
        if not self._paddle_ocr:
            raise RuntimeError("PaddleOCR is not available")
        
        # Get element screenshot
        image = self._get_element_image(element)
        if image is None:
            return []
        
        # Get element position for coordinate adjustment
        element_x, element_y = self._get_element_position(element)
        
        # Perform OCR
        result: List[Any] = self._paddle_ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return []
        
        # Extract all text with positions
        locations: List[Tuple[int, int, int, int]] = []
        for line in result[0]:
            bbox, (detected_text, confidence) = line
            
            if confidence >= confidence_threshold and detected_text == text:
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                width = int(x2 - x1)
                height = int(y2 - y1)
                x = int(x1 + element_x)
                y = int(y1 + element_y)
                
                locations.append((x, y, width, height))
        
        return locations
    
    def get_all_text(self, element: BaseElement, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Get all text from element with positions"""
        if not self._paddle_ocr:
            raise RuntimeError("PaddleOCR is not available")
        
        # Get element screenshot
        image = self._get_element_image(element)
        if image is None:
            return []
        
        # Get element position for coordinate adjustment
        element_x, element_y = self._get_element_position(element)
        
        # Perform OCR
        result: List[Any] = self._paddle_ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return []
        
        # Extract all text with positions
        texts: List[Dict[str, Any]] = []
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
        result: List[Any] = self._paddle_ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return ""
        
        # Search for matching text
        for line in result[0]:
            detected_text: str = line[1][0]
            
            # Handle case sensitivity
            search_text = text if case_sensitive else text.lower()
            compare_text: str = detected_text if case_sensitive else detected_text.lower()
            
            # Check for match
            if exact_match:
                if compare_text == search_text:
                    return detected_text
            else:
                if search_text in compare_text:
                    return detected_text
        
        return ""
    
    def preprocess_image(self, image: Any) -> NDArray:
        """Preprocess image for better OCR results"""
        return self._preprocessor.preprocess(image)
    
    def _get_element_image(self, element: BaseElement) -> Optional[NDArray]:
        """Get image from element"""
        try:
            if hasattr(element, 'capture_screenshot'):
                screenshot = element.capture_screenshot()
                return screenshot
            elif hasattr(element, 'capture'):
                screenshot = element.capture_screenshot() if hasattr(element, 'capture_screenshot') else None
                return screenshot
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
                elif hasattr(loc, '__len__') and len(loc) >= 2:
                    return loc[0], loc[1]
        except Exception as e:
            logging.warning(f"Failed to get element position: {e}")
        
        return 0, 0 