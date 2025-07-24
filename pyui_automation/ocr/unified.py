"""
Unified OCR Engine - Factory for OCR implementations

This module provides a unified interface for OCR functionality,
automatically selecting the appropriate implementation.
Follows SRP by managing OCR engine selection.
"""

from typing import List, Union, Optional, Dict, Any, Tuple
import numpy as np
from pathlib import Path

from ..core.interfaces.iocr_service import IOCRService
from ..elements.base_element import BaseElement
from .models import OCRResult


class UnifiedOCREngine(IOCRService):
    """
    Unified OCR Engine that automatically selects the best available implementation.
    
    Single Responsibility: Manage OCR engine selection and delegation.
    """
    
    def __init__(self, implementation: Optional[IOCRService] = None):
        """
        Initialize unified OCR engine
        
        Args:
            implementation: Optional OCR implementation. If None, will auto-select.
        """
        self._implementation = implementation
        self._languages = ["en"]
        
        # Auto-select implementation if none provided
        if self._implementation is None:
            self._implementation = self._select_implementation()
    
    def _select_implementation(self) -> IOCRService:
        """Select the best available OCR implementation"""
        # Try to use real OCR engine first
        try:
            from .engine import OCREngine
            return OCREngine()
        except (ImportError, RuntimeError) as e:
            # Fall back to stub implementation
            from .stub import StubOCREngine
            return StubOCREngine()
    
    def set_implementation(self, implementation: IOCRService) -> None:
        """Set specific OCR implementation"""
        if not isinstance(implementation, IOCRService):
            raise ValueError("Implementation must implement IOCRService")
        self._implementation = implementation
    
    def get_implementation(self) -> Optional[IOCRService]:
        """Get current OCR implementation"""
        return self._implementation
    
    def set_languages(self, languages: List[str]) -> None:
        """Set languages for OCR recognition"""
        if not languages:
            raise ValueError("Languages list cannot be empty")
        self._languages = languages
        if self._implementation:
            self._implementation.set_languages(languages)
    
    def recognize_text(self, image: Union[Path, str, np.ndarray], preprocess: bool = False) -> str:
        """Recognize text in an image"""
        return self._implementation.recognize_text(image, preprocess) if self._implementation else ""
    
    def find_text_location(self, element: BaseElement, text: str, confidence_threshold: float = 0.5) -> List[Tuple[int, int, int, int]]:
        """Find location(s) of text within element"""
        return self._implementation.find_text_location(element, text, confidence_threshold) if self._implementation else []
    
    def get_all_text(self, element: BaseElement, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Get all text from element with positions"""
        return self._implementation.get_all_text(element, confidence_threshold) if self._implementation else []
    
    def verify_text_presence(self, element: BaseElement, text: str, confidence_threshold: float = 0.5) -> bool:
        """Verify presence of text in element"""
        return self._implementation.verify_text_presence(element, text, confidence_threshold) if self._implementation else False
    
    def read_text(self, element: BaseElement, text: str, case_sensitive: bool = False, exact_match: bool = False) -> str:
        """Read text from element and search for specific pattern"""
        return self._implementation.read_text(element, text, case_sensitive, exact_match) if self._implementation else ""
    
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        return self._implementation.preprocess_image(image) if self._implementation else image
    
    def get_implementation_info(self) -> Dict[str, Any]:
        """Get information about current implementation"""
        impl_type = type(self._implementation).__name__
        return {
            "type": impl_type,
            "languages": self._languages,
            "is_real_engine": "OCREngine" in impl_type
        } 