"""
OCR Models - Data structures for OCR functionality
"""

from typing import Tuple, Dict, Any


class OCRResult:
    """OCR result data structure"""
    
    def __init__(self, text: str = "", confidence: float = 0.0, bbox: Tuple[int, int, int, int] = (0, 0, 0, 0)):
        """
        Initialize OCR result
        
        Args:
            text: Recognized text
            confidence: Confidence score (0.0-1.0)
            bbox: Bounding box (x, y, width, height)
        """
        self.text = text
        self.confidence = confidence
        self.bbox = bbox
    
    def __str__(self) -> str:
        return f"OCRResult(text='{self.text}', confidence={self.confidence:.2f}, bbox={self.bbox})"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'text': self.text,
            'confidence': self.confidence,
            'bbox': self.bbox
        }


class TextLocation:
    """Text location data structure"""
    
    def __init__(self, x: int, y: int, width: int, height: int, text: str = "", confidence: float = 0.0):
        """
        Initialize text location
        
        Args:
            x: X coordinate
            y: Y coordinate
            width: Width of text region
            height: Height of text region
            text: Text content
            confidence: Confidence score
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.confidence = confidence
    
    def __str__(self) -> str:
        return f"TextLocation(x={self.x}, y={self.y}, w={self.width}, h={self.height}, text='{self.text}')"
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        """Convert to tuple format (x, y, width, height)"""
        return (self.x, self.y, self.width, self.height)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'x': self.x,
            'y': self.y,
            'width': self.width,
            'height': self.height,
            'text': self.text,
            'confidence': self.confidence
        } 