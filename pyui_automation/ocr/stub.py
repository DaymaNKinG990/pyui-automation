"""
Stub OCR Engine - Test implementation

This module provides a stub OCR engine for testing purposes.
Follows SRP by providing test data without real OCR processing.
"""

import numpy as np
from typing import List, Union, Dict, Any, Tuple
from pathlib import Path

from ..core.interfaces.iocr_service import IOCRService
from ..elements.base_element import BaseElement
from .models import OCRResult, TextLocation


class StubOCREngine(IOCRService):
    """
    Stub OCR engine for testing purposes.
    
    Single Responsibility: Provide test data for OCR functionality.
    """
    
    def __init__(self):
        """Initialize stub OCR engine"""
        self._languages = ["en"]
        self._test_data = {
            "sample text": OCRResult("sample text", 0.95, (10, 10, 100, 30)),
            "test button": OCRResult("test button", 0.90, (50, 50, 80, 25)),
            "login": OCRResult("login", 0.88, (100, 100, 60, 20)),
            "username": OCRResult("username", 0.92, (150, 150, 70, 25)),
            "password": OCRResult("password", 0.91, (200, 200, 70, 25)),
        }
    
    def set_languages(self, languages: List[str]) -> None:
        """Set OCR languages (stub)"""
        if not languages:
            raise ValueError("Languages list cannot be empty")
        self._languages = languages
    
    def recognize_text(self, image: Union[Path, str, np.ndarray], preprocess: bool = False) -> str:
        """Recognize text in image (stub)"""
        # Return sample text for any input
        return "sample text"
    
    def find_text_location(self, element: BaseElement, text: str, confidence_threshold: float = 0.5) -> List[Tuple[int, int, int, int]]:
        """Find location(s) of text within element (stub)"""
        # Return sample location for any text
        return [(10, 10, 100, 30)]
    
    def get_all_text(self, element: BaseElement, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Get all text from element with positions (stub)"""
        # Return sample text data
        return [
            {
                "text": "sample text",
                "confidence": 0.95,
                "position": (50, 20)
            },
            {
                "text": "test button",
                "confidence": 0.90,
                "position": (100, 50)
            }
        ]
    
    def verify_text_presence(self, element: BaseElement, text: str, confidence_threshold: float = 0.5) -> bool:
        """Verify presence of text in element (stub)"""
        # Always return True for testing
        return True
    
    def read_text(self, element: BaseElement, text: str, case_sensitive: bool = False, exact_match: bool = False) -> str:
        """Read text from element and search for specific pattern (stub)"""
        # Return the searched text if it exists in test data
        if text in self._test_data:
            return self._test_data[text].text
        return "sample text"
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results (stub)"""
        # Return the same image
        return image
    
    def get_supported_languages(self) -> List[str]:
        """Get supported languages (stub)"""
        return ["en", "ru", "de", "fr", "es", "it", "pt", "zh", "ja", "ko"]
    
    def is_language_supported(self, language: str) -> bool:
        """Check if language is supported (stub)"""
        return language in self.get_supported_languages()
    
    def add_test_data(self, text: str, result: OCRResult) -> None:
        """Add test data for specific text"""
        self._test_data[text] = result
    
    def clear_test_data(self) -> None:
        """Clear all test data"""
        self._test_data.clear() 