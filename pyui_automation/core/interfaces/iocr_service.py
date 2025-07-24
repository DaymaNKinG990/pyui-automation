"""
OCR Service Interfaces for SOLID compliance.

This module defines interfaces for OCR services to ensure
Interface Segregation Principle compliance.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Union
from pathlib import Path
import numpy as np


class ITextRecognition(ABC):
    """Interface for text recognition functionality"""
    
    @abstractmethod
    def recognize_text(self, image: Union[Path, str, np.ndarray], preprocess: bool = False) -> str:
        """Recognize text in an image"""
        pass
    
    @abstractmethod
    def set_languages(self, languages: List[str]) -> None:
        """Set languages for OCR recognition"""
        pass


class ITextLocation(ABC):
    """Interface for text location functionality"""
    
    @abstractmethod
    def find_text_location(self, element: Any, text: str, confidence_threshold: float = 0.5) -> List[tuple]:
        """Find location(s) of text within element"""
        pass
    
    @abstractmethod
    def get_all_text(self, element: Any, confidence_threshold: float = 0.5) -> List[Dict[str, Any]]:
        """Get all text from element with positions"""
        pass


class ITextVerification(ABC):
    """Interface for text verification functionality"""
    
    @abstractmethod
    def verify_text_presence(self, element: Any, text: str, confidence_threshold: float = 0.5) -> bool:
        """Verify presence of text in element"""
        pass
    
    @abstractmethod
    def read_text(self, element: Any, text: str, case_sensitive: bool = False, exact_match: bool = False) -> str:
        """Read text from a UI element and search for a specific pattern"""
        pass


class IImagePreprocessing(ABC):
    """Interface for image preprocessing functionality"""
    
    @abstractmethod
    def preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results"""
        pass


class IOCRService(ITextRecognition, ITextLocation, ITextVerification, IImagePreprocessing):
    """
    Complete OCR service interface.
    
    Combines all OCR functionality while maintaining ISP compliance.
    """
    pass 