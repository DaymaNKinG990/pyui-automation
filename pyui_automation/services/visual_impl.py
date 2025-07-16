from typing import Any, Optional
from pathlib import Path
import cv2
import numpy as np
from .visual import VisualTestingService

class VisualTestingServiceImpl(VisualTestingService):
    """Implementation of VisualTestingService for baseline and smart screenshot comparison."""
    def __init__(self, baseline_dir: Optional[str] = None):
        """Initialize visual testing service implementation."""
        self._baseline_dir = Path(baseline_dir) if baseline_dir else Path.cwd() / 'visual_baseline'
        self._baseline_dir.mkdir(parents=True, exist_ok=True)

    def init_baseline(self, baseline_dir: Optional[str] = None) -> None:
        if baseline_dir:
            self._baseline_dir = Path(baseline_dir)
            self._baseline_dir.mkdir(parents=True, exist_ok=True)

    def capture_baseline(self, name: str, element: Optional[Any] = None) -> None:
        img = element.capture_screenshot() if element else self._capture_screen()
        path = self._baseline_dir / f"{name}.png"
        cv2.imwrite(str(path), cv2.cvtColor(img, cv2.COLOR_RGB2BGR))

    def compare_visual(self, name: str, element: Optional[Any] = None, threshold: float = 0.01, ignore_mask: Optional[np.ndarray] = None, ignore_regions: Optional[list] = None) -> dict:
        baseline_path = self._baseline_dir / f"{name}.png"
        if not baseline_path.exists():
            return {"error": "Baseline not found"}
        baseline = cv2.imread(str(baseline_path))
        img = element.capture_screenshot() if element else self._capture_screen()
        if baseline.shape != img.shape:
            img = cv2.resize(img, (baseline.shape[1], baseline.shape[0]))
        diff = cv2.absdiff(baseline, img)
        diff_gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)
        _, diff_mask = cv2.threshold(diff_gray, 25, 255, cv2.THRESH_BINARY)
        # Применяем ignore_mask
        if ignore_mask is not None:
            diff_mask = cv2.bitwise_and(diff_mask, cv2.bitwise_not(ignore_mask))
        # Применяем ignore_regions
        if ignore_regions:
            for (x, y, w, h) in ignore_regions:
                diff_mask[y:y+h, x:x+w] = 0
        diff_pixels = cv2.countNonZero(diff_mask)
        total_pixels = diff_mask.size
        percent_diff = diff_pixels / total_pixels
        passed = percent_diff <= threshold
        highlight = img.copy()
        highlight[diff_mask > 0] = [0, 0, 255]
        return {
            "percent_diff": percent_diff,
            "passed": passed,
            "diff_mask": diff_mask,
            "highlight": highlight,
            "threshold": threshold
        }

    def generate_report(self, name: str, differences: list, output_dir: str) -> None:
        report_path = Path(output_dir) / f"visual_report_{name}.txt"
        with open(report_path, "w") as f:
            for diff in differences:
                f.write(str(diff) + "\n")

    def _capture_screen(self):
        # Заглушка: здесь должен быть вызов backend.capture_screenshot()
        # Для интеграции потребуется DI backend
        raise NotImplementedError("_capture_screen должен быть реализован через backend") 