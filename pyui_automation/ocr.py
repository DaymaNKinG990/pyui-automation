from pathlib import Path
import cv2
import numpy as np
import logging
from typing import List, Union
from paddleocr import PaddleOCR

from .elements import UIElement

# Flag to indicate if PaddleOCR is available
HAS_PADDLE = True


class OCREngine:
    """OCR Engine"""

    def __init__(self) -> None:
        """Initialize OCR engine
        
        Initialize the OCR engine with the PaddleOCR library if available.
        If PaddleOCR is not available, the engine will not be able to recognize text.
        """
        self._paddle_ocr = None
        self._languages = ['en']
        if HAS_PADDLE:
            self._paddle_ocr = PaddleOCR(use_angle_cls=True, lang=self._languages[0], show_log=False)

    def set_languages(self, languages: List[str]) -> None:
        """Set languages for OCR recognition.
        
        Args:
            languages: List of language codes to use for OCR. The first language in the list
                    will be used as the primary language. Example: ['en', 'fr', 'de']
        """
        if not languages:
            raise ValueError("Languages list cannot be empty")
            
        self._languages = languages
        if HAS_PADDLE:
            self._paddle_ocr = PaddleOCR(use_angle_cls=True, lang=languages[0], show_log=False)

    def recognize_text(self, image_path: Union[Path, str, np.ndarray], preprocess=False) -> str:
        """Recognize text in an image

        Args:
            image_path (Path, str or np.ndarray): Path to the image file, the image itself as a numpy array, or the path to the image file as a string.
            preprocess (bool, optional): Whether to preprocess the image before passing it to the OCR engine. Defaults to False.

        Returns:
            str: The recognized text or an empty string if no text is recognized.
            
        Raises:
            RuntimeError: If PaddleOCR is not available
        """
        if not HAS_PADDLE or self._paddle_ocr is None:
            raise RuntimeError("PaddleOCR is not available. Please install paddleocr package to use text recognition features.")

        # Convert Path to str
        if isinstance(image_path, Path):
            image_path = str(image_path)

        # Load image from path if string
        if isinstance(image_path, str):
            image = cv2.imread(image_path)
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image = image_path

        # Ensure image is numpy array
        if not isinstance(image, np.ndarray):
            raise TypeError("Image must be a numpy array or a path to an image file")
            
        if preprocess:
            image = self._preprocess_image(image)

        result = self._paddle_ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return ""
            
        return " ".join(line[1][0] for line in result[0])

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results
        
        Applies the following preprocessing steps to the image:
        
        1. Convert to grayscale
        2. Apply thresholding using Otsu's thresholding algorithm
        3. Apply dilation with a 3x3 kernel
        
        These steps are intended to improve the OCR results by making the text more legible.
        """
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image

        # Apply thresholding
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]

        # Apply dilation
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3,3))
        dilation = cv2.dilate(thresh, kernel, iterations=1)

        return dilation

    def read_text_from_element(self, element: UIElement, preprocess: bool = False) -> str:
        """
        Read text from a UI element

        Captures the image of the UI element and runs OCR on it to extract the text.

        Args:
            element (UIElement): The UI element to read text from.
            preprocess (bool, optional): Whether to preprocess the image before passing it to the OCR engine. Defaults to False.

        Returns:
            str: The recognized text or an empty string if no text is recognized.
        """
        image = element.capture_screenshot()
        if image is None:
            logging.warning("Failed to capture screenshot of element")
            return ""
        return self.recognize_text(image, preprocess=preprocess)

    def find_text_location(self, element: UIElement, text: str, confidence_threshold: float = .5) -> tuple | None:
        """
        Find location of text within element

        Uses PaddleOCR to find the location of the given text within the given element.
        The location is returned as a tuple of (x, y, width, height) coordinates relative to the element's
        top-left corner, or None if the text is not found.

        Args:
            element (UIElement): The element to search for the text in.
            text (str): The text to search for.
            confidence_threshold (float, optional): The minimum confidence required for a match. Defaults to .5.

        Returns:
            tuple | None: The location of the text or None if not found.
        """
        if not self._paddle_ocr:
            raise RuntimeError("PaddleOCR is not available")

        # If this is a virtual element with a stored screenshot, use that directly
        if hasattr(element, '_screenshot'):
            image = element._screenshot
        else:
            image = element.capture_screenshot()

        result = self._paddle_ocr.ocr(image, cls=True)
        
        if not result or not result[0]:
            return None

        element_x, element_y = element.location
        
        for line in result[0]:
            bbox, (detected_text, confidence) = line
            if detected_text == text and confidence >= confidence_threshold:
                # Calculate bounding box coordinates and dimensions
                x1, y1 = bbox[0]
                x2, y2 = bbox[2]
                width = abs(x2 - x1)
                height = abs(y2 - y1)
                x = x1 + element_x
                y = y1 + element_y
                return (int(x), int(y), int(width), int(height))
        
        return None

    def get_all_text(self, element: UIElement, confidence_threshold: float = .5) -> list:
        """Get all text from element with positions"""
        if not self._paddle_ocr:
            raise RuntimeError("PaddleOCR is not available")

        image = element.capture_screenshot()
        result = self._paddle_ocr.ocr(image, cls=True)
        
        if not result or not result[0]:
            return []

        element_x, element_y = element.location
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

    def verify_text_presence(self, element: UIElement, text: str, confidence_threshold: float = .5) -> bool:
        """
        Verify presence of text in element

        Args:
            element (UIElement): Element to search for text
            text (str): Text to search for
            confidence_threshold (float, optional): Minimum confidence for the OCR result to be considered a match. Defaults to 0.5.

        Returns:
            bool: True if the text is found in the element, False otherwise
        """
        return self.find_text_location(element, text, confidence_threshold) is not None

    def read_text(self, element: UIElement, text: str, case_sensitive: bool = False, exact_match: bool = False) -> str:
        """
        Read text from a UI element and search for a specific pattern

        Args:
            element (UIElement): The UI element to read text from
            text (str): The text pattern to search for
            case_sensitive (bool, optional): Whether to perform case-sensitive matching. Defaults to False.
            exact_match (bool, optional): Whether to require exact matches only. Defaults to False.

        Returns:
            str: The matched text if found, empty string otherwise
        """
        if not HAS_PADDLE or self._paddle_ocr is None:
            raise RuntimeError("PaddleOCR is not available")

        # Get element screenshot
        image = element.capture_screenshot()
        if image is None:
            logging.warning("Failed to capture screenshot of element")
            return ""

        # Get OCR results
        result = self._paddle_ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return ""

        # Process each text result
        for line in result[0]:
            detected_text = line[1][0]  # Get the text part of the result

            # Handle case sensitivity
            search_text = text if case_sensitive else text.lower()
            compare_text = detected_text if case_sensitive else detected_text.lower()

            # Check for match based on exact_match flag
            if exact_match:
                if compare_text == search_text:
                    return detected_text
            else:
                if search_text in compare_text:
                    return detected_text

        return ""
