"""
Image Preprocessing for OCR - follows SRP

This module is responsible only for image preprocessing to improve OCR accuracy.
"""

import cv2
import numpy as np
from ..utils import validate_type


class ImagePreprocessor:
    """
    Image preprocessor for OCR optimization.
    
    Single Responsibility: Preprocess images for better OCR results.
    """
    
    def __init__(self):
        """Initialize image preprocessor"""
        pass
    
    def preprocess(self, image: np.ndarray) -> np.ndarray:
        """
        Preprocess image for better OCR results
        
        Args:
            image: Input image as numpy array
            
        Returns:
            Preprocessed image as numpy array (always 3-channel RGB)
            
        Raises:
            ValueError: If image is invalid
        """
        if not validate_type(image, np.ndarray):
            raise ValueError("Image must be a numpy array")
        
        if image.size == 0:
            raise ValueError("Image cannot be empty")
        
        # Convert to grayscale if needed
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply thresholding
        thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        
        # Apply dilation to connect text components
        kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (3, 3))
        dilated = cv2.dilate(thresh, kernel, iterations=1)
        
        # Always return 3-channel RGB image for compatibility
        if len(dilated.shape) == 2:
            dilated = cv2.cvtColor(dilated, cv2.COLOR_GRAY2RGB)
        
        return dilated
    
    def enhance_contrast(self, image: np.ndarray) -> np.ndarray:
        """
        Enhance image contrast
        
        Args:
            image: Input image
            
        Returns:
            Enhanced image
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply CLAHE (Contrast Limited Adaptive Histogram Equalization)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        # Convert back to RGB
        if len(image.shape) == 3:
            enhanced = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2RGB)
        
        return enhanced
    
    def remove_noise(self, image: np.ndarray) -> np.ndarray:
        """
        Remove noise from image
        
        Args:
            image: Input image
            
        Returns:
            Denoised image
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        # Apply Gaussian blur to reduce noise
        denoised = cv2.GaussianBlur(gray, (3, 3), 0)
        
        # Convert back to RGB
        if len(image.shape) == 3:
            denoised = cv2.cvtColor(denoised, cv2.COLOR_GRAY2RGB)
        
        return denoised
    
    def resize_for_ocr(self, image: np.ndarray, min_width: int = 800) -> np.ndarray:
        """
        Resize image for optimal OCR performance
        
        Args:
            image: Input image
            min_width: Minimum width for OCR
            
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        
        if width < min_width:
            scale = min_width / width
            new_width = int(width * scale)
            new_height = int(height * scale)
            resized = cv2.resize(image, (new_width, new_height), interpolation=cv2.INTER_CUBIC)
            return resized
        
        return image 