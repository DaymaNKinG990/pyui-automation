"""
OCR Module - Unified text recognition functionality

This module provides a unified interface for OCR functionality,
supporting both real implementations and test stubs.
"""

# Import models
from .models import OCRResult, TextLocation

# Import engines
from .engine import OCREngine
from .stub import StubOCREngine
from .unified import UnifiedOCREngine

# Import preprocessing
from .preprocessing import ImagePreprocessor

# Default engine instance
default_engine = UnifiedOCREngine()


# Convenience functions
def recognize_text(image, preprocess: bool = False) -> str:
    """Recognize text using default engine"""
    return default_engine.recognize_text(image, preprocess)


def set_languages(languages: list) -> None:
    """Set languages for default engine"""
    default_engine.set_languages(languages)


def get_implementation_info() -> dict:
    """Get information about current OCR implementation"""
    return default_engine.get_implementation_info()


# Export main classes and functions
__all__ = [
    # Models
    'OCRResult',
    'TextLocation',
    
    # Engines
    'OCREngine',
    'StubOCREngine', 
    'UnifiedOCREngine',
    
    # Preprocessing
    'ImagePreprocessor',
    
    # Default instance
    'default_engine',
    
    # Convenience functions
    'recognize_text',
    'set_languages',
    'get_implementation_info',
]
