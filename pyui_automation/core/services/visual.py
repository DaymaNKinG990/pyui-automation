"""
Visual testing utilities.
"""

from typing import Optional, Tuple, Any
import numpy as np
from pathlib import Path

from ...utils.image import compare_images, save_image, load_image


class VisualTester:
    """Handles visual testing operations."""
    
    def __init__(self, baseline_dir: Optional[Path] = None):
        self.baseline_dir = baseline_dir
        
    def compare_with_baseline(self, current_image: np.ndarray, baseline_name: str, 
                            threshold: float = 0.95) -> Tuple[bool, float]:
        """Compare current image with baseline."""
        if self.baseline_dir is None:
            return False, 0.0
            
        baseline_path = self.baseline_dir / f"{baseline_name}.png"
        if not baseline_path.exists():
            return False, 0.0
            
        baseline_image = load_image(baseline_path)
        if baseline_image is None:
            return False, 0.0
            
        similarity = compare_images(baseline_image, current_image)
        return similarity >= threshold, similarity
        
    def save_baseline(self, image: np.ndarray, name: str) -> bool:
        """Save image as baseline."""
        if self.baseline_dir is None:
            return False
            
        baseline_path = self.baseline_dir / f"{name}.png"
        try:
            save_image(image, baseline_path)
            return True
        except Exception:
            return False 