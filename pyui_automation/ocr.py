import cv2
import numpy as np
import pytesseract
import easyocr
from PIL import Image
from typing import List, Tuple, Optional


class OCREngine:
    """OCR engine that combines multiple OCR backends for better accuracy"""

    def __init__(self):
        self.easyocr_reader = None  # Lazy initialization
        self.languages = ['en']  # Default to English

    def set_languages(self, languages: List[str]):
        """Set OCR languages"""
        self.languages = languages
        # Reset EasyOCR reader to use new languages
        self.easyocr_reader = None

    def read_text(self, image_path: str, backend: str = 'auto') -> str:
        """
        Read text from image using specified backend
        
        Args:
            image_path: Path to image file
            backend: OCR backend to use ('tesseract', 'easyocr', or 'auto')
        """
        if backend == 'auto':
            # Try both backends and return the one with more confidence
            tesseract_result = self._read_with_tesseract(image_path)
            easyocr_result = self._read_with_easyocr(image_path)
            
            # Simple heuristic: choose the longer text
            if len(tesseract_result) > len(easyocr_result):
                return tesseract_result
            return easyocr_result
        
        elif backend == 'tesseract':
            return self._read_with_tesseract(image_path)
        
        elif backend == 'easyocr':
            return self._read_with_easyocr(image_path)
        
        raise ValueError(f"Unknown backend: {backend}")

    def find_text_location(self, image_path: str, text: str) -> Optional[Tuple[int, int, int, int]]:
        """
        Find location of text in image
        Returns bounding box (x, y, width, height) if found, None otherwise
        """
        # Use EasyOCR for better bounding box detection
        if not self.easyocr_reader:
            self.easyocr_reader = easyocr.Reader(self.languages)

        image = cv2.imread(image_path)
        results = self.easyocr_reader.readtext(image)

        text = text.lower()
        for (bbox, detected_text, conf) in results:
            if text in detected_text.lower():
                # Convert bbox to (x, y, width, height)
                x1, y1 = map(int, bbox[0])
                x2, y2 = map(int, bbox[2])
                return (x1, y1, x2 - x1, y2 - y1)

        return None

    def _read_with_tesseract(self, image_path: str) -> str:
        """Read text using Tesseract OCR"""
        try:
            image = Image.open(image_path)
            return pytesseract.image_to_string(image, lang='+'.join(self.languages))
        except Exception as e:
            print(f"Tesseract OCR error: {e}")
            return ""

    def _read_with_easyocr(self, image_path: str) -> str:
        """Read text using EasyOCR"""
        try:
            if not self.easyocr_reader:
                self.easyocr_reader = easyocr.Reader(self.languages)
            
            results = self.easyocr_reader.readtext(image_path)
            return ' '.join(text for _, text, _ in results)
        except Exception as e:
            print(f"EasyOCR error: {e}")
            return ""
