"""Visual testing functionality for UI automation"""

import cv2
import numpy as np
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any, Union
from dataclasses import dataclass
import time

from ..utils import (
    crop_image,
    validate_type
)


@dataclass
class VisualDifference:
    location: Tuple[int, int]
    size: Tuple[int, int]
    difference_percentage: float
    type: str  # 'added', 'removed', 'changed'
    element: Any = None


class VisualMatcher:
    """Handles visual matching and comparison of UI elements"""

    def __init__(self, element: Any, similarity_threshold: float = 0.95):
        """
        Initialize visual matcher with a UI element.

        Args:
            element: UI element to perform visual matching on
            similarity_threshold: Threshold for similarity matching (0-1)
        """
        self.element = element
        self.similarity_threshold = similarity_threshold

    def find_element_in_image(self, screen_image: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Find element in screen image using template matching.

        Args:
            screen_image: Screen image to search in

        Returns:
            Tuple of (x, y) coordinates if found, None otherwise
        """
        element_image = self.element.capture_screenshot()
        if element_image is None:
            return None
            
        result = cv2.matchTemplate(screen_image, element_image, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= self.similarity_threshold:
            return (int(max_loc[0]), int(max_loc[1]))
        return None

    def find_all_elements_in_image(self, screen_image: np.ndarray) -> List[Dict[str, Any]]:
        """
        Find all occurrences of element in screen image.

        Args:
            screen_image: Screen image to search in

        Returns:
            List of dictionaries containing location and confidence of matches
        """
        element_image = self.element.capture_screenshot()
        if element_image is None:
            return []
            
        result = cv2.matchTemplate(screen_image, element_image, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= self.similarity_threshold)
        matches = []
        
        for pt in zip(*locations[::-1]):
            matches.append({
                "location": pt,
                "confidence": float(result[pt[1], pt[0]])
            })
        
        return matches

    def compare_images(self, img1: np.ndarray, img2: np.ndarray, resize: bool = False, roi: Optional[Tuple[int, int, int, int]] = None) -> float:
        """
        Compare two images and calculate similarity.

        Args:
            img1: First image
            img2: Second image
            resize: Whether to resize images if they have different dimensions
            roi: Region of interest as (x, y, width, height)

        Returns:
            Similarity score between 0 and 1
        """
        # Validate inputs
        if not validate_type(img1, np.ndarray) or not validate_type(img2, np.ndarray):
            return 0.0
            
        if resize and img1.shape != img2.shape:
            img2 = cv2.resize(img2, (img1.shape[1], img1.shape[0]))

        if roi:
            x, y, w, h = roi
            img1 = crop_image(img1, x, y, w, h)
            img2 = crop_image(img2, x, y, w, h)

        if img1.shape != img2.shape:
            return 0.0
        
        # Calculate similarity manually for detailed score
        diff = cv2.absdiff(img1, img2)
        similarity = 1 - (np.sum(diff) / (img1.shape[0] * img1.shape[1] * img1.shape[2] * 255))
        
        return float(similarity)

    def find_element(self, template: np.ndarray) -> Optional[Tuple[int, int]]:
        """
        Find element in screen using template matching.

        Args:
            template: Template image to find

        Returns:
            Tuple of (x, y) coordinates if found, None otherwise
        """
        screen = self.element.capture_screenshot()
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
        
        if max_val >= self.similarity_threshold:
            return (int(max_loc[0]), int(max_loc[1]))
        return None

    def find_all_elements(self, template: np.ndarray, threshold: float = 0.8) -> List[Dict[str, Any]]:
        """
        Find all occurrences of a template in the screen.

        Args:
            template: Template image to search for
            threshold: Matching threshold

        Returns:
            List of dictionaries containing location and confidence of matches
        """
        screen = self.element.capture_screenshot()
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        locations = np.where(result >= threshold)
        matches = []
        
        for pt in zip(*locations[::-1]):
            matches.append({
                "location": pt,
                "confidence": result[pt[1], pt[0]]
            })
        
        return matches

    def wait_for_image(self, template: np.ndarray, timeout: float = 10) -> bool:
        """
        Wait for image to appear on screen.

        Args:
            template: Template image to wait for
            timeout: Maximum time to wait in seconds

        Returns:
            True if image was found within timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.find_element(template) is not None:
                return True
            time.sleep(0.1)
        return False

    def verify_visual_state(self, baseline: np.ndarray) -> Dict[str, Any]:
        """
        Verify current visual state against baseline.

        Args:
            baseline: Baseline image to compare against

        Returns:
            Dict containing match status and similarity score
        """
        current = self.element.capture_screenshot()
        return self.compare_images(current, baseline)

    def highlight_differences(self, img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        """
        Create image highlighting differences between two images.

        Args:
            img1: First image
            img2: Second image

        Returns:
            Image with differences highlighted
        """
        if img1.shape != img2.shape:
            raise ValueError("Images must have the same dimensions")
            
        diff = cv2.absdiff(img1, img2)
        _, thresh = cv2.threshold(cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY), 30, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        result = img2.copy()
        cv2.drawContours(result, contours, -1, (0, 0, 255), 2)
        return result

    def generate_diff_report(self, img1: np.ndarray, img2: np.ndarray, output_path: str) -> None:
        """
        Generate a visual difference report between two images.

        Args:
            img1: First image
            img2: Second image
            output_path: Path to save the difference report
        """
        if img1.shape != img2.shape:
            raise ValueError("Images must have the same dimensions")

        diff = cv2.absdiff(img1, img2)
        diff_color = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, diff_binary = cv2.threshold(diff_color, 30, 255, cv2.THRESH_BINARY)
        
        contours, _ = cv2.findContours(diff_binary, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        
        report_img = img1.copy()
        cv2.drawContours(report_img, contours, -1, (0, 0, 255), 2)
        
        cv2.imwrite(output_path, report_img)

    def set_similarity_threshold(self, threshold: float) -> None:
        """
        Set the similarity threshold for image matching.

        Args:
            threshold: Threshold value between 0 and 1
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        self.similarity_threshold = threshold


class VisualTester:
    """Handles visual testing and comparison of UI elements"""

    def __init__(self, baseline_dir: Union[str, Path], threshold: float = 0.95) -> None:
        """
        Initialize visual tester with baseline directory.

        Args:
            baseline_dir: Directory to store baseline images
            threshold: Similarity threshold (0-1)
        """
        self.baseline_dir = Path(baseline_dir)
        self.baseline_dir.mkdir(parents=True, exist_ok=True)
        self._baseline_cache: Dict[str, np.ndarray] = {}
        self.similarity_threshold = threshold
        self.threshold = threshold  # Alias for compatibility

    def capture_baseline(self, name: str, image: np.ndarray) -> bool:
        """
        Capture a baseline image for comparison.

        Args:
            name: Name of the baseline image
            image: Image data as numpy array

        Returns:
            bool: True if baseline was captured successfully

        Raises:
            ValueError: If name is empty or image data is invalid
        """
        if not name:
            raise ValueError("Name cannot be empty")
        if image is None or not isinstance(image, np.ndarray) or image.size == 0:
            raise ValueError("Invalid image data")
        # Гарантируем расширение .png
        if not name.endswith('.png'):
            name = f"{name}.png"
        filepath = self.baseline_dir / name
        cv2.imwrite(str(filepath), image)
        self._baseline_cache[name] = image
        return True

    def read_baseline(self, name: str) -> np.ndarray:
        """
        Read baseline image from the baseline directory.

        Args:
            name: Name of the baseline image to read

        Returns:
            Baseline image as numpy array

        Raises:
            FileNotFoundError: If baseline image does not exist
            ValueError: If baseline image cannot be loaded
        """
        if not name.endswith('.png'):
            name = f"{name}.png"
        baseline_path = self.baseline_dir / name

        if not baseline_path.exists():
            raise FileNotFoundError(f"Baseline image not found: {name}")

        if name in self._baseline_cache:
            return self._baseline_cache[name]

        baseline = cv2.imread(str(baseline_path))
        if baseline is None:
            raise ValueError(f"Failed to load baseline image: {name}")

        self._baseline_cache[name] = baseline
        return baseline

    def _calculate_similarity(self, img1: np.ndarray, img2: np.ndarray) -> float:
        """
        Calculate similarity score between two images.

        Args:
            img1: First image
            img2: Second image

        Returns:
            Similarity score between 0 and 1
        """
        try:
            # Convert to same data type if needed
            if img1.dtype != img2.dtype:
                img1 = img1.astype(np.uint8)
                img2 = img2.astype(np.uint8)

            # Calculate absolute difference
            diff = cv2.absdiff(img1, img2)
            
            # Calculate mean squared error for each channel
            diff_float = diff.astype(np.float64)
            diff_squared = np.power(diff_float, 2).astype(np.float64)
            try:
                # Simple mean calculation
                mse = float(np.sum(diff_squared) / diff_squared.size)
            except Exception:
                mse = 0.0
            
            # Calculate RMSE and normalize to 0-1 range
            rmse = np.sqrt(mse)
            max_rmse = 255.0  # Maximum possible RMSE for 8-bit images
            
            # Convert to similarity score (inverse of normalized RMSE)
            similarity = 1.0 - (rmse / max_rmse)
            
            return float(similarity)

        except Exception as e:
            raise RuntimeError(f"Failed to calculate similarity: {str(e)}")

    def _evaluate_match(self, similarity: float, differences: List[Dict], threshold: float) -> bool:
        """
        Evaluate if images match based on similarity and differences.

        Args:
            similarity: Calculated similarity score
            differences: List of detected differences
            threshold: Similarity threshold to use

        Returns:
            Boolean indicating if images match
        """
        # For high thresholds, require both high similarity and no significant differences
        if threshold >= 0.9:
            return similarity >= threshold and len(differences) == 0
        # For medium thresholds, allow a few small differences
        elif threshold >= 0.7:
            return similarity >= threshold and len(differences) <= 2
        # For low thresholds, только similarity
        else:
            return similarity >= threshold

    def compare_with_baseline(self, name: str, current: np.ndarray) -> Tuple[bool, float]:
        """
        Compare current image with baseline.

        Args:
            name: Name of the baseline image
            current: Current image to compare

        Returns:
            Tuple[bool, float]: Match result and difference score
        """
        try:
            baseline = self.read_baseline(name)
            result = self.compare(current, baseline)
            return result['match'], result['similarity']
        except (FileNotFoundError, ValueError):
            return False, 1.0

    def compare(self, current: np.ndarray, baseline: np.ndarray, resize: bool = False, roi: Optional[tuple] = None) -> Dict[str, Any]:
        """
        Compare two images and return similarity score and match status.

        Args:
            current: Current image to compare
            baseline: Baseline image to compare
            resize: Whether to resize images if they have different dimensions
            roi: Region of interest as (x, y, w, h)

        Returns:
            Dictionary containing match status, similarity score, and differences

        Raises:
            ValueError: If images are invalid or have incompatible sizes when resize=False
        """
        if current is None or baseline is None:
            raise ValueError("Both images must be provided")
            
        if not isinstance(current, np.ndarray) or not isinstance(baseline, np.ndarray):
            raise ValueError("Images must be numpy arrays")

        if not resize and current.shape != baseline.shape:
            raise ValueError("Image sizes do not match and resize=False")

        # Apply ROI if provided
        if roi is not None:
            x, y, w, h = roi
            current = current[y:y+h, x:x+w]
            baseline = baseline[y:y+h, x:x+w]

        try:
            # Convert to same data type if needed
            if current.dtype != baseline.dtype:
                current = current.astype(np.uint8)
                baseline = baseline.astype(np.uint8)

            # Resize if needed and requested
            if resize and current.shape != baseline.shape:
                baseline = cv2.resize(baseline, (current.shape[1], current.shape[0]))

            # Calculate similarity
            similarity = self._calculate_similarity(current, baseline)

            # Find differences
            diff = cv2.absdiff(current, baseline)
            diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
            _, thresh = cv2.threshold(diff_gray, 30, 255, cv2.THRESH_BINARY)
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

            # Create list of differences
            differences = []
            min_diff_area = 25  # Minimum area to consider a difference significant
            for contour in contours:
                area = cv2.contourArea(contour)
                if area >= min_diff_area:
                    x, y, w, h = cv2.boundingRect(contour)
                    differences.append({
                        'location': (x, y),
                        'size': (w, h),
                        'area': area
                    })

            # Create difference visualization
            diff_image = current.copy()
            diff_mask = diff > 30
            red_color = np.array([0, 0, 255], dtype=np.uint8)
            # Use proper boolean indexing
            if len(diff_image.shape) == 3 and diff_image.shape[2] >= 3:
                mask_2d = diff_mask.any(axis=2)
                # Используем более явный способ присваивания
                diff_image = diff_image.astype(np.uint8)
                for i in range(3):  # RGB каналы
                    diff_image[:, :, i] = np.where(mask_2d, red_color[i], diff_image[:, :, i])

            # Determine match
            is_match = self._evaluate_match(similarity, differences, self.similarity_threshold)

            return {
                'match': is_match,
                'similarity': similarity,
                'differences': differences,
                'diff_image': diff_image
            }

        except Exception as e:
            raise RuntimeError(f"Failed to compare images: {str(e)}")

    def verify_hash(self, name: str, current: np.ndarray) -> bool:
        """
        Verify perceptual hash of current image against baseline.

        Args:
            name: Name of the baseline image
            current: Current image to verify

        Returns:
            bool: True if hash matches baseline

        Raises:
            ValueError: If image data is invalid
        """
        if current is None or not isinstance(current, np.ndarray) or current.size == 0:
            raise ValueError("Invalid image data")

        baseline = self.read_baseline(name)
        current_hash = self._calculate_phash(current)
        baseline_hash = self._calculate_phash(baseline)
        return np.array_equal(current_hash, baseline_hash)

    def _calculate_phash(self, image: np.ndarray, hash_size: int = 8) -> np.ndarray:
        """
        Calculate perceptual hash for an image.

        Args:
            image: The input image as a numpy array
            hash_size: Size of the hash (default 8x8)

        Returns:
            numpy array representing the perceptual hash
        """
        if image is None or not isinstance(image, np.ndarray):
            raise ValueError("Invalid image")

        try:
            # Convert to grayscale and resize
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            resized = cv2.resize(gray, (hash_size + 1, hash_size))
            
            # Calculate differences and construct hash
            left_part = resized[:, 1:].astype(np.float64)
            right_part = resized[:, :-1].astype(np.float64)
            diff_array = np.greater(left_part, right_part)
            diff = diff_array.astype(np.uint8)
            return diff

        except Exception as e:
            raise RuntimeError(f"Failed to calculate image hash: {str(e)}")

    def calculate_phash(self, image: np.ndarray, hash_size: int = 8) -> np.ndarray:
        """
        Calculate perceptual hash for an image.

        Args:
            image: The input image as a numpy array
            hash_size: Size of the hash (default 8x8)

        Returns:
            numpy array representing the perceptual hash
        """
        return self._calculate_phash(image, hash_size)

    def set_similarity_threshold(self, threshold: float) -> None:
        """
        Set similarity threshold for image matching.

        Args:
            threshold: New threshold value (between 0 and 1)
        """
        if not 0 <= threshold <= 1:
            raise ValueError("Threshold must be between 0 and 1")
        self.similarity_threshold = threshold

    def generate_report(self, differences: List[VisualDifference], name: str, output_dir: Optional[str] = None) -> None:
        """
        Generate visual comparison report.

        Args:
            differences: List of visual differences
            name: Name of the report
            output_dir: Directory where to save the report. If None, uses baseline directory.
        """
        if output_dir is None:
            output_dir = str(self.baseline_dir)
        else:
            path = Path(output_dir)
            path.mkdir(parents=True, exist_ok=True)
            output_dir = str(path)

        report_path = Path(output_dir) / f"{name}_report.html"
        
        # Generate HTML report
        html_content = ["<html><body>", "<h1>Visual Comparison Report</h1>"]
        
        for i, diff in enumerate(differences):
            html_content.extend([
                f"<h2>Difference {i + 1}</h2>",
                f"<p>Location: {diff.location}</p>",
                f"<p>Size: {diff.size}</p>",
                f"<p>Difference: {diff.difference_percentage:.2f}%</p>",
                f"<p>Type: {diff.type}</p>"
            ])
        
        html_content.append("</body></html>")
        
        report_path.write_text("\n".join(html_content))

    def find_element(self, template: np.ndarray) -> Optional[Tuple[int, int]]:
        """Find element in baseline_dir images using template matching"""
        import glob
        import cv2
        files = list(glob.glob(str(self.baseline_dir / '*.png')))
        if not files:
            return None
        img = cv2.imread(files[0])
        if img is None:
            return None
        # Явное приведение типов для совместимости с cv2
        img_array = np.asarray(img, dtype=np.uint8)
        template_array = np.asarray(template, dtype=np.uint8)
        res = cv2.matchTemplate(img_array, template_array, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
        if max_val > 0.8:
            return (int(max_loc[0]), int(max_loc[1]))
        return None

    def find_all_elements(self, template: np.ndarray, threshold: float = 0.8):
        """Find all elements in baseline_dir images using template matching"""
        import glob
        import cv2
        import numpy as np
        files = list(glob.glob(str(self.baseline_dir / '*.png')))
        if not files:
            return []
        img = cv2.imread(files[0])
        if img is None:
            return []
        # Явное приведение типов для совместимости с cv2
        img_array = np.asarray(img, dtype=np.uint8)
        template_array = np.asarray(template, dtype=np.uint8)
        res = cv2.matchTemplate(img_array, template_array, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= threshold)
        return [{'location': (int(x), int(y)), 'confidence': float(res[y, x])} for y, x in zip(*loc)]

    def generate_diff_report(self, img1, img2, output_path):
        """Сохраняет diff-изображение между img1 и img2 по пути output_path"""
        import cv2
        diff = cv2.absdiff(img1, img2)
        cv2.imwrite(output_path, diff)



    def wait_for_image(self, template: np.ndarray, timeout: float = 10) -> bool:
        """Wait for image to appear in baseline_dir images using template matching"""
        import time
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.find_element(template) is not None:
                return True
            time.sleep(0.1)
        return False

    def highlight_differences(self, img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        """Highlight differences between two images (контуры отличий)"""
        if img1.shape != img2.shape:
            raise ValueError("Images must have the same dimensions")
        import cv2
        diff = cv2.absdiff(img1, img2)
        _, thresh = cv2.threshold(cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY), 30, 255, cv2.THRESH_BINARY)
        contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        result = img2.copy()
        cv2.drawContours(result, contours, -1, (0, 0, 255), 2)
        return result

    def create_baseline(self, name: str, element: Any) -> bool:
        """
        Create a baseline image for an element.

        Args:
            name: Name of the baseline
            element: Element to capture baseline for

        Returns:
            bool: True if baseline was created successfully
        """
        try:
            image = element.capture_screenshot()
            if image is None:
                return False
            return self.capture_baseline(name, image)
        except Exception:
            return False

    def verify_visual_state(self, name: str, element: Any) -> bool:
        """
        Verify visual state of element against baseline.

        Args:
            name: Name of the baseline
            element: Element to verify

        Returns:
            bool: True if visual state matches baseline
        """
        try:
            current_image = element.capture_screenshot()
            if current_image is None:
                return False
                
            baseline = self.read_baseline(name)
            result = self.compare(current_image, baseline)
            return result['match']
        except Exception:
            return False

    def wait_for_image(self, name: str, element: Any, timeout: float = 10) -> bool:
        """
        Wait for element to match baseline image.

        Args:
            name: Name of the baseline
            element: Element to wait for
            timeout: Maximum time to wait in seconds

        Returns:
            bool: True if element matched within timeout
        """
        start_time = time.time()
        while time.time() - start_time < timeout:
            if self.verify_visual_state(name, element):
                return True
            time.sleep(0.1)
        return False

    def generate_visual_report(self, name: str, element: Any) -> Dict[str, Any]:
        """
        Generate visual comparison report.

        Args:
            name: Name of the baseline
            element: Element to compare

        Returns:
            Dict containing comparison results
        """
        try:
            current_image = element.capture_screenshot()
            if current_image is None:
                return {
                    'element_name': name,
                    'similarity': 0.0,
                    'passed': False,
                    'error': 'Failed to capture screenshot'
                }
                
            baseline = self.read_baseline(name)
            result = self.compare(current_image, baseline)
            
            return {
                'element_name': name,
                'similarity': result['similarity'],
                'passed': result['match'],
                'differences': len(result.get('differences', []))
            }
        except Exception as e:
            return {
                'element_name': name,
                'similarity': 0.0,
                'passed': False,
                'error': str(e)
            }

    def find_element_in_baseline(self, name: str, element: Any) -> Optional[Tuple[int, int]]:
        """
        Find element in baseline image.

        Args:
            name: Name of the baseline
            element: Element to find

        Returns:
            Tuple of (x, y) coordinates if found, None otherwise
        """
        try:
            element_image = element.capture_screenshot()
            if element_image is None:
                return None
                
            baseline = self.read_baseline(name)
            result = cv2.matchTemplate(baseline, element_image, cv2.TM_CCOEFF_NORMED)
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
            
            if max_val >= self.similarity_threshold:
                return (int(max_loc[0]), int(max_loc[1]))
            return None
        except Exception:
            return None
