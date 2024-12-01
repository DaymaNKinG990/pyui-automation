import cv2
import numpy as np
import pytesseract
import easyocr
from PIL import Image


class OCREngine:
    def __init__(self):
        self._tesseract_available = True
        try:
            import pytesseract
        except ImportError:
            self._tesseract_available = False
        
        self._easyocr_reader = None
        try:
            self._easyocr_reader = easyocr.Reader(['en'])
        except ImportError:
            pass

    def recognize_text(self, image_path, engine="tesseract", preprocess=False):
        """Recognize text in an image using specified OCR engine"""
        if isinstance(image_path, str):
            image = Image.open(image_path)
            image = np.array(image)
        else:
            image = image_path
            
        if preprocess:
            image = self._preprocess_image(image)
            
        if engine == "tesseract":
            if not self._tesseract_available:
                raise RuntimeError("Tesseract not available")
            return pytesseract.image_to_string(image)
            
        elif engine == "easyocr":
            if self._easyocr_reader is None:
                raise RuntimeError("EasyOCR not available")
            results = self._easyocr_reader.readtext(image)
            return " ".join(text for _, text, _ in results)
            
        else:
            raise ValueError(f"Unsupported OCR engine: {engine}")

    def find_text(self, text, image_path, confidence_threshold=0.5):
        """Find location of specific text in image"""
        if self._easyocr_reader is None:
            raise RuntimeError("EasyOCR not available")
            
        if isinstance(image_path, str):
            image = Image.open(image_path)
            image = np.array(image)
        else:
            image = image_path
            
        results = self._easyocr_reader.readtext(image)
        
        for bbox, detected_text, confidence in results:
            if detected_text == text and confidence >= confidence_threshold:
                # Return center point of bounding box
                x = sum(point[0] for point in bbox) / 4
                y = sum(point[1] for point in bbox) / 4
                return (int(x), int(y))
        return None

    def find_all_text(self, text, image_path, confidence_threshold=0.5):
        """Find all occurrences of text in image"""
        if self._easyocr_reader is None:
            raise RuntimeError("EasyOCR not available")
            
        if isinstance(image_path, str):
            image = Image.open(image_path)
            image = np.array(image)
        else:
            image = image_path
            
        results = self._easyocr_reader.readtext(image)
        locations = []
        
        for bbox, detected_text, confidence in results:
            if detected_text == text and confidence >= confidence_threshold:
                x = sum(point[0] for point in bbox) / 4
                y = sum(point[1] for point in bbox) / 4
                locations.append((int(x), int(y)))
                
        return locations

    def _preprocess_image(self, image):
        """Preprocess image for better OCR results"""
        # Convert to grayscale
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
            
        # Apply thresholding to get black and white image
        _, binary = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        # Noise removal
        denoised = cv2.fastNlMeansDenoising(binary)
        
        return denoised

    def read_text_from_element(self, element, engine="tesseract", preprocess=False):
        """Read text from a UI element"""
        screenshot = element.capture_screenshot()
        return self.recognize_text(screenshot, engine=engine, preprocess=preprocess)

    def read_text_from_image(self, image_path, engine="tesseract", preprocess=False):
        """Read text from an image file"""
        return self.recognize_text(image_path, engine=engine, preprocess=preprocess)

    def find_text_location(self, element, text, confidence_threshold=0.5):
        """Find location of text within element"""
        image = element.capture()
        if image is None:
            return []
            
        if self._easyocr_reader is None:
            raise RuntimeError("EasyOCR not available")
            
        results = self._easyocr_reader.readtext(image)
        locations = []
        
        for bbox, detected_text, confidence in results:
            if text.lower() in detected_text.lower() and confidence >= confidence_threshold:
                # Convert bbox points to x,y coordinates
                x = min(point[0] for point in bbox)
                y = min(point[1] for point in bbox)
                locations.append((int(x), int(y)))
                
        return locations

    def get_all_text(self, element, engine="easyocr", confidence_threshold=0.5):
        """Get all text from element with positions"""
        image = element.capture()
        if image is None:
            return []
            
        if engine == "easyocr":
            if self._easyocr_reader is None:
                raise RuntimeError("EasyOCR not available")
                
            results = self._easyocr_reader.readtext(image)
            texts = []
            
            for bbox, text, confidence in results:
                if confidence >= confidence_threshold:
                    x = min(point[0] for point in bbox)
                    y = min(point[1] for point in bbox)
                    texts.append({
                        'text': text,
                        'position': (int(x), int(y)),
                        'confidence': confidence
                    })
                    
            return texts
            
        elif engine == "tesseract":
            if not self._tesseract_available:
                raise RuntimeError("Tesseract not available")
                
            # Get text and bounding boxes using Tesseract
            data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DICT)
            texts = []
            
            for i in range(len(data['text'])):
                if float(data['conf'][i]) >= confidence_threshold * 100:  # Tesseract confidence is 0-100
                    texts.append({
                        'text': data['text'][i],
                        'position': (data['left'][i], data['top'][i]),
                        'confidence': float(data['conf'][i]) / 100
                    })
                    
            return texts
            
        else:
            raise ValueError(f"Unsupported OCR engine: {engine}")

    def get_text_confidence(self, text, image_path):
        """Get confidence score for detected text"""
        if self._easyocr_reader is None:
            raise RuntimeError("EasyOCR not available")
        
        if isinstance(image_path, str):
            image = Image.open(image_path)
            image = np.array(image)
        else:
            image = image_path
        
        results = self._easyocr_reader.readtext(image)
        for bbox, detected_text, confidence in results:
            if detected_text == text:
                return confidence
        return 0.0

    def verify_text_presence(self, element, text, confidence_threshold=0.5):
        """Verify presence of text in element"""
        locations = self.find_text_location(element, text, confidence_threshold)
        return len(locations) > 0

    def find_text(self, text, image_path, confidence_threshold=0.5):
        """Find location of specific text in image"""
        if self._easyocr_reader is None:
            raise RuntimeError("EasyOCR not available")
            
        if isinstance(image_path, str):
            image = Image.open(image_path)
            image = np.array(image)
        else:
            image = image_path
            
        results = self._easyocr_reader.readtext(image)
        
        for bbox, detected_text, confidence in results:
            if detected_text == text and confidence >= confidence_threshold:
                # Return center point of bounding box
                x = sum(point[0] for point in bbox) / 4
                y = sum(point[1] for point in bbox) / 4
                return (int(x), int(y))
        return None
