from pathlib import Path
import cv2
import numpy as np
import logging
from typing import List, Union

# Flag to indicate if PaddleOCR is available
try:
    import importlib
    _paddleocr_spec = importlib.util.find_spec('paddleocr')
    HAS_PADDLE = _paddleocr_spec is not None
except Exception:
    HAS_PADDLE = False

from .elements import UIElement


class OCREngine:
    """
    OCR Engine for text recognition in UI screenshots.

    Использует PaddleOCR для распознавания текста на скриншотах UI-элементов или экрана.
    Используется сервисным слоем OCREngineService.

    Example usage:
        ocr = OCREngine()
        text = ocr.recognize_text("screenshot.png")
        # Для UIElement:
        text = ocr.read_text_from_element(element)

    Назначение:
        - Распознавание текста для автоматизации UI
        - Поиск текста и координат в элементах
        - Интеграция с сервисным слоем
    """

    def __init__(self) -> None:
        """Initialize OCR engine
        
        Initialize the OCR engine with the PaddleOCR library if available.
        If PaddleOCR is not available, the engine will not be able to recognize text.
        """
        self._paddle_ocr = None
        self._languages = ['en']
        if HAS_PADDLE:
            try:
                from paddleocr import PaddleOCR
                self._paddle_ocr = PaddleOCR(use_angle_cls=True, lang=self._languages[0], show_log=False)
            except ImportError:
                self._paddle_ocr = None
        else:
            self._paddle_ocr = None

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
            try:
                from paddleocr import PaddleOCR
                self._paddle_ocr = PaddleOCR(use_angle_cls=True, lang=languages[0], show_log=False)
            except ImportError:
                self._paddle_ocr = None

    def recognize_text(self, image_path: Union[Path, str, np.ndarray], preprocess=False) -> str:
        """Recognize text in an image

        Args:
            image_path (Path, str or np.ndarray): Path to the image file, the image itself as a numpy array, or the path to the image file as a string.
            preprocess (bool, optional): Whether to preprocess the image before passing it to the OCR engine. Defaults to False.

        Returns:
            str: The recognized text or an empty string if no text is recognized.
            
        Raises:
            RuntimeError: If PaddleOCR is not available
            FileNotFoundError: If image path does not exist
            ValueError: If image is empty or invalid
        """
        if not HAS_PADDLE or self._paddle_ocr is None:
            raise RuntimeError("PaddleOCR is not available. Please install paddleocr package to use text recognition features.")

        # Convert Path to str
        if isinstance(image_path, Path):
            image_path = str(image_path)

        # Load image from path if string
        if isinstance(image_path, str):
            import os
            if not os.path.exists(image_path):
                raise FileNotFoundError(f"Image file not found: {image_path}")
            image = cv2.imread(image_path)
            if image is None:
                raise ValueError(f"Failed to load image: {image_path}")
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        else:
            image = image_path

        # Ensure image is numpy array and not empty
        if not isinstance(image, np.ndarray) or image.size == 0:
            raise ValueError("Image must be a non-empty numpy array or a valid path to an image file")
            
        if preprocess:
            image = self._preprocess_image(image)

        result = self._paddle_ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return ""
            
        return " ".join(line[1][0] for line in result[0])

    def _preprocess_image(self, image: np.ndarray) -> np.ndarray:
        """Preprocess image for better OCR results
        Always returns 3-channel RGB image for test compatibility.
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

        # Всегда возвращаем 3-канальное изображение (RGB)
        if len(dilation.shape) == 2:
            dilation = cv2.cvtColor(dilation, cv2.COLOR_GRAY2RGB)
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

    def find_text_location(self, element: UIElement, text: str, confidence_threshold: float = .5) -> list:
        """
        Find location(s) of text within element
        Возвращает список кортежей (x, y, width, height) для всех совпадений.
        """
        if not self._paddle_ocr:
            raise RuntimeError("PaddleOCR is not available")

        # If this is a virtual element with a stored screenshot, use that directly
        if hasattr(element, '_screenshot'):
            image = element._screenshot
        elif hasattr(element, 'capture_screenshot'):
            image = element.capture_screenshot()
        elif hasattr(element, 'capture'):
            image = element.capture()
        else:
            raise ValueError("Element does not support screenshot capture")

        result = self._paddle_ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return []

        # location может быть tuple или dict или отсутствовать
        element_x, element_y = 0, 0
        if hasattr(element, 'location'):
            loc = element.location
            if isinstance(loc, dict):
                element_x = loc.get('x', 0)
                element_y = loc.get('y', 0)
            elif isinstance(loc, (tuple, list)) and len(loc) >= 2:
                element_x, element_y = loc[0], loc[1]
        elif hasattr(element, 'get_location'):
            loc = element.get_location()
            if isinstance(loc, dict):
                element_x = loc.get('x', 0)
                element_y = loc.get('y', 0)
            elif isinstance(loc, (tuple, list)) and len(loc) >= 2:
                element_x, element_y = loc[0], loc[1]

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

    def get_all_text(self, element: UIElement, confidence_threshold: float = .5) -> list:
        """Get all text from element with positions (список словарей)"""
        if not self._paddle_ocr:
            raise RuntimeError("PaddleOCR is not available")

        if hasattr(element, 'capture_screenshot'):
            image = element.capture_screenshot()
        elif hasattr(element, 'capture'):
            image = element.capture()
        else:
            raise ValueError("Element does not support screenshot capture")
        result = self._paddle_ocr.ocr(image, cls=True)
        if not result or not result[0]:
            return []

        element_x, element_y = 0, 0
        if hasattr(element, 'location'):
            loc = element.location
            if isinstance(loc, dict):
                element_x = loc.get('x', 0)
                element_y = loc.get('y', 0)
            elif isinstance(loc, (tuple, list)) and len(loc) >= 2:
                element_x, element_y = loc[0], loc[1]
        elif hasattr(element, 'get_location'):
            loc = element.get_location()
            if isinstance(loc, dict):
                element_x = loc.get('x', 0)
                element_y = loc.get('y', 0)
            elif isinstance(loc, (tuple, list)) and len(loc) >= 2:
                element_x, element_y = loc[0], loc[1]
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
