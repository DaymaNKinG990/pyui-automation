"""
Visual Testing Service - handles all visual testing operations.

Responsible for:
- Visual baseline management
- Visual comparison
- Visual difference detection
- Visual testing reports
"""

from typing import Optional, Union, Tuple, Any
from pathlib import Path
import numpy as np
from logging import getLogger
import time

from ...elements.base_element import BaseElement
from ...utils.image import load_image, save_image, compare_images
from ...utils.file import ensure_dir
from ..interfaces.ivisual_testing_service import IVisualTestingService


class VisualTestingService(IVisualTestingService):
    """Service for visual testing operations"""
    
    def __init__(self, session: Any):
        self._session = session
        self._logger = getLogger(__name__)
        self._visual_tester = None
        self._baseline_dir: Optional[Path] = None
        self._threshold = 0.95
    
    def init_visual_testing(self, baseline_dir: Union[str, Path], threshold: float = 0.95) -> None:
        """Initialize visual testing"""
        try:
            from .visual import VisualTester
            self._baseline_dir = Path(baseline_dir)
            self._threshold = threshold
            self._visual_tester = VisualTester(self._session)
            if self._visual_tester:
                self._visual_tester.init_visual_testing(baseline_dir, threshold)
            self._logger.info(f"Visual testing initialized with baseline dir: {baseline_dir}")
        except Exception as e:
            self._logger.error(f"Failed to initialize visual testing: {e}")
            raise
    
    def configure_visual_testing(self, baseline_dir: Union[str, Path], threshold: float = 0.95) -> None:
        """Configure visual testing (alias for init_visual_testing)"""
        self.init_visual_testing(baseline_dir, threshold)
    
    def capture_baseline(self, name: str, element: Optional[BaseElement] = None) -> bool:
        """Capture visual baseline"""
        try:
            if self._visual_tester:
                return self._visual_tester.capture_baseline(name, element)
            
            # Fallback implementation
            if element:
                screenshot = element.capture_screenshot()
            else:
                screenshot = self._session.screenshot_service.take_screenshot()
            
            if screenshot is not None and self._baseline_dir is not None:
                baseline_path = self._baseline_dir / f"{name}.png"
                ensure_dir(baseline_path.parent)
                save_image(screenshot, baseline_path)
                self._logger.info(f"Baseline captured: {name}")
                return True
            
            return False
        except Exception as e:
            self._logger.error(f"Failed to capture baseline: {e}")
            return False
    
    def verify_visual(self, name: str, element: Optional[BaseElement] = None) -> Tuple[bool, float]:
        """Verify visual state against baseline"""
        try:
            if self._visual_tester:
                return self._visual_tester.verify_visual(name, element)
            
            # Fallback implementation
            if self._baseline_dir is None:
                self._logger.warning("Baseline directory not initialized")
                return False, 0.0
                
            baseline_path = self._baseline_dir / f"{name}.png"
            if not baseline_path.exists():
                self._logger.warning(f"Baseline not found: {name}")
                return False, 0.0
            
            baseline_image = load_image(baseline_path)
            if element:
                current_image = element.capture_screenshot()
            else:
                current_image = self._session.screenshot_service.take_screenshot()
            
            if current_image is None:
                return False, 0.0
            
            similarity = compare_images(baseline_image, current_image) if baseline_image is not None and current_image is not None else 0.0
            is_match = similarity >= self._threshold
            
            self._logger.info(f"Visual verification {name}: similarity={similarity:.3f}, match={is_match}")
            return is_match, similarity
        except Exception as e:
            self._logger.error(f"Failed to verify visual: {e}")
            return False, 0.0
    
    def compare_visual(self, name: str, element: Optional[BaseElement] = None) -> Tuple[bool, float]:
        """Compare visual state (alias for verify_visual)"""
        return self.verify_visual(name, element)
    
    def verify_visual_state(self, name: str, element: Optional[BaseElement] = None, threshold: Optional[float] = None) -> bool:
        """Verify visual state and return boolean result"""
        try:
            is_match, similarity = self.verify_visual(name, element)
            if threshold is not None:
                is_match = similarity >= threshold
            return is_match
        except Exception as e:
            self._logger.error(f"Failed to verify visual state: {e}")
            return False
    
    def capture_visual_baseline(self, name: str, element: Optional[BaseElement] = None) -> bool:
        """Capture visual baseline (alias for capture_baseline)"""
        return self.capture_baseline(name, element)
    
    def generate_visual_report(self, differences: list, name: str, output_dir: Optional[Union[str, Path]] = None) -> None:
        """Generate visual testing report"""
        try:
            if self._visual_tester:
                self._visual_tester.generate_visual_report(differences, name, output_dir)
            else:
                # Fallback implementation
                if output_dir is None and self._baseline_dir is not None:
                    output_dir = self._baseline_dir / "reports"
                elif output_dir is None:
                    self._logger.error("No output directory specified and baseline directory not initialized")
                    return
                
                output_path = Path(output_dir) / f"{name}_report.txt"
                ensure_dir(output_path.parent)
                
                with open(output_path, 'w') as f:
                    f.write(f"Visual Testing Report: {name}\n")
                    f.write(f"Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
                    f.write(f"Differences found: {len(differences)}\n")
                    for diff in differences:
                        f.write(f"- {diff}\n")
                
                self._logger.info(f"Visual report generated: {output_path}")
        except Exception as e:
            self._logger.error(f"Failed to generate visual report: {e}")
    
    def generate_diff_report(self, img1: np.ndarray, img2: np.ndarray, output_path: Union[str, Path]) -> None:
        """Generate difference report between two images"""
        try:
            # This is a simplified implementation
            # In a real scenario, you might want to highlight differences
            diff_image = np.abs(img1.astype(np.float64) - img2.astype(np.float64))
            save_image(diff_image.astype(np.uint8), output_path)
            self._logger.info(f"Diff report generated: {output_path}")
        except Exception as e:
            self._logger.error(f"Failed to generate diff report: {e}")
    
    def find_all_elements(self, template: np.ndarray, threshold: float = 0.8) -> list:
        """Find all elements matching template"""
        try:
            # This is a placeholder implementation
            # In a real scenario, you would use template matching
            self._logger.warning("find_all_elements not implemented")
            return []
        except Exception as e:
            self._logger.error(f"Failed to find elements: {e}")
            return []
    
    def wait_for_image(self, template: np.ndarray, timeout: float = 10) -> bool:
        """Wait for image to appear"""
        try:
            # This is a placeholder implementation
            # In a real scenario, you would use template matching with timeout
            self._logger.warning("wait_for_image not implemented")
            return False
        except Exception as e:
            self._logger.error(f"Failed to wait for image: {e}")
            return False
    
    def highlight_differences(self, img1: np.ndarray, img2: np.ndarray) -> np.ndarray:
        """Highlight differences between two images"""
        try:
            # Simple difference highlighting
            # Ensure both arrays have the same shape and dtype for subtraction
            img1_float = img1.astype(np.float64)
            img2_float = img2.astype(np.float64)
            
            if img1_float.shape != img2_float.shape:
                img2_float = np.resize(img2_float, img1_float.shape)
            
            diff = np.abs(img1_float - img2_float)
            highlighted = img1.copy()
            # Use boolean indexing for setting values
            diff_mask = diff > 30
            if len(highlighted.shape) == 3 and highlighted.shape[2] >= 3:
                highlighted[diff_mask] = [255, 0, 0]  # Red for differences
            return highlighted
        except Exception as e:
            self._logger.error(f"Failed to highlight differences: {e}")
            return img1 