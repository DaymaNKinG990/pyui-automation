import cv2
import numpy as np
from PIL import Image
import imagehash
from typing import Dict, List, Tuple, Optional
import json
from pathlib import Path
import time
from dataclasses import dataclass


@dataclass
class VisualDifference:
    location: Tuple[int, int]
    size: Tuple[int, int]
    difference_percentage: float
    type: str  # 'added', 'removed', 'changed'


class VisualTester:
    """Class for visual testing and comparison"""

    def __init__(self, automation):
        self.automation = automation
        self.baseline_dir = None
        self.threshold = 0.95  # Similarity threshold

    def set_baseline_directory(self, directory: str):
        """Set directory for baseline images"""
        self.baseline_dir = Path(directory)
        self.baseline_dir.mkdir(parents=True, exist_ok=True)

    def capture_baseline(self, name: str, element=None):
        """Capture baseline screenshot"""
        if not self.baseline_dir:
            raise ValueError("Baseline directory not set")

        screenshot = self._take_screenshot(element)
        if screenshot:
            screenshot.save(self.baseline_dir / f"{name}.png")

    def compare_with_baseline(self, name: str, element=None) -> Optional[List[VisualDifference]]:
        """Compare current state with baseline"""
        if not self.baseline_dir:
            raise ValueError("Baseline directory not set")

        baseline_path = self.baseline_dir / f"{name}.png"
        if not baseline_path.exists():
            raise FileNotFoundError(f"Baseline image not found: {name}")

        # Take current screenshot
        current = self._take_screenshot(element)
        if not current:
            return None

        # Load baseline
        baseline = Image.open(baseline_path)

        # Convert to same size if different
        if current.size != baseline.size:
            current = current.resize(baseline.size)

        # Convert to OpenCV format
        current_cv = cv2.cvtColor(np.array(current), cv2.COLOR_RGB2BGR)
        baseline_cv = cv2.cvtColor(np.array(baseline), cv2.COLOR_RGB2BGR)

        return self._find_differences(baseline_cv, current_cv)

    def verify_visual_hash(self, name: str, element=None) -> Dict[str, float]:
        """Compare images using perceptual hashing"""
        if not self.baseline_dir:
            raise ValueError("Baseline directory not set")

        baseline_path = self.baseline_dir / f"{name}.png"
        if not baseline_path.exists():
            raise FileNotFoundError(f"Baseline image not found: {name}")

        # Take current screenshot
        current = self._take_screenshot(element)
        if not current:
            return {'similarity': 0.0}

        # Load baseline
        baseline = Image.open(baseline_path)

        # Calculate image hashes
        current_hash = imagehash.average_hash(current)
        baseline_hash = imagehash.average_hash(baseline)

        # Compare hashes
        similarity = 1 - (current_hash - baseline_hash) / 64.0  # 64 bits in the hash
        return {
            'similarity': similarity,
            'match': similarity >= self.threshold
        }

    def generate_visual_report(self, differences: List[VisualDifference],
                             name: str, output_dir: str):
        """Generate visual comparison report"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Create visualization of differences
        baseline_path = self.baseline_dir / f"{name}.png"
        current = self._take_screenshot()
        baseline = Image.open(baseline_path)

        # Convert to same size if different
        if current.size != baseline.size:
            current = current.resize(baseline.size)

        # Create diff visualization
        diff_image = self._create_diff_visualization(
            np.array(baseline),
            np.array(current),
            differences
        )

        # Save diff image
        cv2.imwrite(str(output_path / f"{name}_diff.png"), diff_image)

        # Generate HTML report
        html_report = f"""
        <html>
        <head>
            <title>Visual Comparison Report - {name}</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .image-container {{ display: flex; margin: 20px 0; }}
                .image-box {{ margin-right: 20px; }}
                .diff-list {{ margin: 20px 0; }}
                .diff-item {{ margin: 10px 0; padding: 10px; border: 1px solid #ccc; }}
            </style>
        </head>
        <body>
            <h1>Visual Comparison Report - {name}</h1>
            
            <div class="image-container">
                <div class="image-box">
                    <h3>Baseline</h3>
                    <img src="{baseline_path.name}" alt="Baseline">
                </div>
                <div class="image-box">
                    <h3>Current</h3>
                    <img src="{name}.png" alt="Current">
                </div>
                <div class="image-box">
                    <h3>Differences</h3>
                    <img src="{name}_diff.png" alt="Differences">
                </div>
            </div>

            <div class="diff-list">
                <h2>Detected Differences</h2>
        """

        for diff in differences:
            html_report += f"""
                <div class="diff-item">
                    <p><strong>Type:</strong> {diff.type}</p>
                    <p><strong>Location:</strong> ({diff.location[0]}, {diff.location[1]})</p>
                    <p><strong>Size:</strong> {diff.size[0]}x{diff.size[1]}</p>
                    <p><strong>Difference:</strong> {diff.difference_percentage:.2f}%</p>
                </div>
            """

        html_report += """
            </div>
        </body>
        </html>
        """

        with open(output_path / f"{name}_report.html", 'w') as f:
            f.write(html_report)

    def _take_screenshot(self, element=None) -> Optional[Image.Image]:
        """Take screenshot of full screen or specific element"""
        if element:
            # Get element bounds
            location = element.location
            size = element.size
            
            # Take full screenshot
            screenshot_path = self.automation.take_screenshot()
            if not screenshot_path:
                return None
            
            # Load and crop image
            image = Image.open(screenshot_path)
            return image.crop((
                location[0],
                location[1],
                location[0] + size[0],
                location[1] + size[1]
            ))
        else:
            # Take full screenshot
            screenshot_path = self.automation.take_screenshot()
            if screenshot_path:
                return Image.open(screenshot_path)
        return None

    def _find_differences(self, baseline: np.ndarray,
                         current: np.ndarray) -> List[VisualDifference]:
        """Find visual differences between images"""
        differences = []

        # Calculate absolute difference
        diff = cv2.absdiff(baseline, current)
        gray_diff = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        
        # Threshold the difference
        _, thresholded = cv2.threshold(gray_diff, 30, 255, cv2.THRESH_BINARY)
        
        # Find contours of differences
        contours, _ = cv2.findContours(
            thresholded,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )

        for contour in contours:
            x, y, w, h = cv2.boundingRect(contour)
            area = cv2.contourArea(contour)
            if area > 100:  # Filter out small differences
                # Calculate difference percentage for this region
                region_baseline = baseline[y:y+h, x:x+w]
                region_current = current[y:y+h, x:x+w]
                diff_percentage = np.sum(cv2.absdiff(
                    region_baseline, region_current)) / (w * h * 255 * 3) * 100

                # Determine type of difference
                if np.mean(region_current) > np.mean(region_baseline):
                    diff_type = 'added'
                elif np.mean(region_current) < np.mean(region_baseline):
                    diff_type = 'removed'
                else:
                    diff_type = 'changed'

                differences.append(VisualDifference(
                    location=(x, y),
                    size=(w, h),
                    difference_percentage=diff_percentage,
                    type=diff_type
                ))

        return differences

    def _create_diff_visualization(self, baseline: np.ndarray,
                                 current: np.ndarray,
                                 differences: List[VisualDifference]) -> np.ndarray:
        """Create visualization of differences"""
        # Create copy of current image
        visualization = current.copy()

        # Draw rectangles around differences
        for diff in differences:
            color = {
                'added': (0, 255, 0),    # Green
                'removed': (0, 0, 255),  # Red
                'changed': (255, 0, 0)   # Blue
            }[diff.type]

            cv2.rectangle(
                visualization,
                (diff.location[0], diff.location[1]),
                (diff.location[0] + diff.size[0],
                 diff.location[1] + diff.size[1]),
                color,
                2
            )

        return visualization
