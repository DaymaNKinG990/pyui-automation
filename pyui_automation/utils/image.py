import cv2
import numpy as np
from typing import Tuple, Optional, List, TypeAlias
from pathlib import Path

# Type alias for template matching results: (x, y, confidence_score)
Match: TypeAlias = Tuple[int, int, float]


def load_image(path: Path) -> Optional[np.ndarray]:
    """
    Load image from file.

    Args:
        path: The file path to load the image from.

    Returns:
        The loaded image as a numpy array, or None if loading fails.
    """
    try:
        return cv2.imread(str(path))
    except Exception:
        return None

def save_image(image: np.ndarray, path: Path) -> bool:
    """
    Save image to file.

    Args:
        image (np.ndarray): The image data to save.
        path (Path): The file path to save the image to.

    Returns:
        bool: True if the image was saved successfully, False otherwise.
    """
    try:
        return cv2.imwrite(str(path), image)
    except Exception:
        return False

def resize_image(image: np.ndarray, width: Optional[int] = None, height: Optional[int] = None) -> np.ndarray:
    """
    Resize an image while maintaining its aspect ratio.

    Args:
        image (np.ndarray): The image to be resized.
        width (Optional[int]): The desired width of the resized image. If None, height must be provided.
        height (Optional[int]): The desired height of the resized image. If None, width must be provided.

    Returns:
        np.ndarray: The resized image with maintained aspect ratio.

    Raises:
        ValueError: If both width and height are None, or if after calculation, either width or height remains None.
    """
    if width is None and height is None:
        return image

    h, w = image.shape[:2]
    if width is None and height is not None:
        aspect = height / h
        width = int(w * aspect)
    elif height is None and width is not None:
        aspect = width / w
        height = int(h * aspect)

    if width is None or height is None:
        raise ValueError("Either width or height must be provided")

    return cv2.resize(image, (width, height))

def compare_images(img1: np.ndarray, img2: np.ndarray, threshold: float = 0.95) -> bool:
    """
    Compare two images for similarity.

    Args:
        img1 (np.ndarray): The first image to compare.
        img2 (np.ndarray): The second image to compare.
        threshold (float, optional): The minimum similarity score required for the comparison to return True. Defaults to 0.95.

    Returns:
        bool: True if the images are similar (i.e., the similarity score is greater than or equal to the threshold), False otherwise.
    """
    if img1.shape != img2.shape:
        return False
        
    # Convert images to grayscale
    if len(img1.shape) == 3:
        img1_gray = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
        img2_gray = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    else:
        img1_gray = img1
        img2_gray = img2
        
    # Calculate normalized mean absolute difference
    diff = img1_gray.astype(float) - img2_gray.astype(float)
    mse = np.mean(np.abs(diff))  # Use mean absolute difference instead of squared error
    similarity = 1.0 - (mse / 255.0)  # Normalize by max pixel value
    return bool(similarity >= threshold)

def find_template(image: np.ndarray, template: np.ndarray, threshold: float = 0.8) -> List[Match]:
    """
    Find template in image using template matching.

    Args:
        image (np.ndarray): The image to search for the template in.
        template (np.ndarray): The template image to search for.
        threshold (float, optional): The minimum similarity score required for a match. Defaults to 0.8.

    Returns:
        List[Match]: A list of (x, y, score) coordinates where the template was found in the image,
                    where score is the matching confidence value.
    """
    # Convert images to grayscale
    if len(image.shape) == 3:
        image_gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    else:
        image_gray = image

    if len(template.shape) == 3:
        template_gray = cv2.cvtColor(template, cv2.COLOR_BGR2GRAY)
    else:
        template_gray = template

    # Normalize images to improve matching
    image_gray = image_gray.astype(np.float32)
    normalized_image_gray = np.empty_like(image_gray)
    cv2.normalize(image_gray, normalized_image_gray, 0, 255, cv2.NORM_MINMAX)
    image_gray = normalized_image_gray.astype(np.uint8)
    
    template_gray = template_gray.astype(np.float32)
    normalized_template_gray = np.empty_like(template_gray)
    cv2.normalize(template_gray, normalized_template_gray, 0, 255, cv2.NORM_MINMAX)
    template_gray = normalized_template_gray.astype(np.uint8)

    # Perform template matching
    result = cv2.matchTemplate(image_gray, template_gray, cv2.TM_CCOEFF_NORMED)
    print("\nTemplate matching result:")
    print("Result shape:", result.shape)
    print("Max correlation:", np.max(result))
    print("Min correlation:", np.min(result))
    
    # Find locations where matching exceeds threshold
    locations = np.where(result >= threshold)
    points = list(zip(*locations[::-1]))  # Convert to (x,y) format
    print(f"Found {len(points)} points above threshold {threshold}")
    
    if not points:
        return []
    
    # Get template dimensions
    h, w = template.shape[:2]
    
    # Convert points to list of matches with scores
    matches: List[Match] = [(x, y, float(result[y, x])) for x, y in points]
    
    # Sort matches by score in descending order
    matches.sort(key=lambda x: x[2], reverse=True)
    print(f"Top match score: {matches[0][2]}")
    
    # Apply non-maximum suppression
    filtered_matches = non_max_suppression([(x, y) for x, y, _ in matches], (w, h), 0.5)
    
    # Return center points of top matches
    return [(x + w//2, y + h//2, score) for x, y, score in matches if (x, y) in filtered_matches]

def non_max_suppression(
    matches: List[Tuple[int, int]],
    template_shape: Tuple[int, int],
    overlap_thresh: float
) -> List[Tuple[int, int]]:
    """
    Remove overlapping matches using non-maximum suppression algorithm.

    Args:
        matches (List[Tuple[int, int]]): List of (x, y) coordinates where the template was found.
        template_shape (Tuple[int, int]): Shape of the template image (w, h).
        overlap_thresh (float): Minimum overlap threshold (0 to 1).

    Returns:
        List[Tuple[int, int]]: List of non-overlapping matches.
    """
    if not matches:
        return []

    # Sort matches by x coordinate
    matches = sorted(matches)
    result = []
    
    # Add first match
    result.append(matches[0])
    
    # Process remaining matches
    for i in range(1, len(matches)):
        x, y = matches[i]
        prev_x, prev_y = result[-1]
        
        # Calculate distance between points
        dist = ((x - prev_x) ** 2 + (y - prev_y) ** 2) ** 0.5
        
        # If points are far apart or we're using high threshold
        if dist > template_shape[0] * 0.5 or overlap_thresh > 0.5:
            result.append(matches[i])
            
    return result

def highlight_region(
    image: np.ndarray,
    x: int,
    y: int,
    width: int,
    height: int,
    color: Tuple[int, int, int] = (0, 255, 0),
    thickness: int = 2
) -> np.ndarray:
    """
    Draw a rectangle around a specified region of interest in an image.

    Args:
        image (np.ndarray): The image on which to draw the rectangle.
        x (int): The x-coordinate of the top-left corner of the rectangle.
        y (int): The y-coordinate of the top-left corner of the rectangle.
        width (int): The width of the rectangle.
        height (int): The height of the rectangle.
        color (Tuple[int, int, int], optional): The color of the rectangle in BGR format. Defaults to (0, 255, 0).
        thickness (int, optional): The thickness of the rectangle's border. Defaults to 2.

    Returns:
        np.ndarray: The image with the rectangle drawn on it.
    """
    img_copy = image.copy()
    cv2.rectangle(img_copy, (x, y), (x + width, y + height), color, thickness)
    return img_copy

def crop_image(image: np.ndarray, x: int, y: int, width: int, height: int) -> np.ndarray:
    """
    Crop image to specified region.

    Args:
        image (np.ndarray): The image to be cropped.
        x (int): The x-coordinate of the top-left corner of the cropped region.
        y (int): The y-coordinate of the top-left corner of the cropped region.
        width (int): The width of the cropped region.
        height (int): The height of the cropped region.

    Returns:
        np.ndarray: The cropped image.
    """
    return image[y:y+height, x:x+width]
