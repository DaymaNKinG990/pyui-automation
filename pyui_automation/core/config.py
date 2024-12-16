"""Configuration for UI automation"""

from dataclasses import dataclass
from typing import Optional, Dict, Any, List
from pathlib import Path


@dataclass
class AutomationConfig:
    """Configuration settings for UI automation"""

    # Screenshot settings
    screenshot_format: str = "png"
    screenshot_quality: int = 90
    screenshot_dir: Optional[Path] = None

    # Visual testing settings
    visual_testing_enabled: bool = False
    visual_baseline_dir: Optional[Path] = None
    visual_threshold: float = 0.95
    visual_algorithm: str = "ssim"

    # Performance settings
    performance_enabled: bool = False
    performance_metrics: List[str] = None
    performance_interval: float = 1.0
    performance_output_dir: Optional[Path] = None

    # Wait settings
    default_timeout: float = 10.0
    default_interval: float = 0.5
    implicit_wait: float = 0.0
    polling_interval: float = 0.5

    # OCR settings
    ocr_enabled: bool = False
    ocr_languages: List[str] = None
    ocr_confidence: float = 0.7

    # Accessibility settings
    accessibility_enabled: bool = False
    accessibility_standards: List[str] = None
    accessibility_output_dir: Optional[Path] = None

    # Backend settings
    backend_type: str = "windows"
    backend_options: Dict[str, Any] = None

    def __post_init__(self):
        """Initialize default values for collections"""
        if self.performance_metrics is None:
            self.performance_metrics = ["cpu", "memory", "response_time"]
        if self.ocr_languages is None:
            self.ocr_languages = ["eng"]
        if self.accessibility_standards is None:
            self.accessibility_standards = ["wcag2a", "wcag2aa"]
        if self.backend_options is None:
            self.backend_options = {}

    def validate(self) -> None:
        """Validate configuration settings"""
        if self.screenshot_quality < 0 or self.screenshot_quality > 100:
            raise ValueError("Screenshot quality must be between 0 and 100")

        if self.visual_threshold < 0 or self.visual_threshold > 1:
            raise ValueError("Visual threshold must be between 0 and 1")

        if self.performance_interval <= 0:
            raise ValueError("Performance interval must be positive")

        if self.default_timeout <= 0:
            raise ValueError("Default timeout must be positive")

        if self.default_interval <= 0:
            raise ValueError("Default interval must be positive")

        if self.implicit_wait < 0:
            raise ValueError("Implicit wait must be non-negative")

        if self.ocr_confidence < 0 or self.ocr_confidence > 1:
            raise ValueError("OCR confidence must be between 0 and 1")

        valid_screenshot_formats = ["png", "jpg", "bmp"]
        if self.screenshot_format not in valid_screenshot_formats:
            raise ValueError(f"Invalid screenshot format. Must be one of: {valid_screenshot_formats}")

        valid_visual_algorithms = ["ssim", "mse", "hash"]
        if self.visual_algorithm not in valid_visual_algorithms:
            raise ValueError(f"Invalid visual algorithm. Must be one of: {valid_visual_algorithms}")

        valid_performance_metrics = ["cpu", "memory", "io", "gpu", "network", "response_time"]
        for metric in self.performance_metrics:
            if metric not in valid_performance_metrics:
                raise ValueError(f"Invalid performance metric. Must be one of: {valid_performance_metrics}")

        valid_ocr_languages = ["eng", "fra", "deu", "spa", "ita"]
        for lang in self.ocr_languages:
            if lang not in valid_ocr_languages:
                raise ValueError(f"Invalid OCR language. Must be one of: {valid_ocr_languages}")

        valid_accessibility_standards = ["wcag2.1", "wcag2.2", "section508", "wcag2a", "wcag2aa"]
        for standard in self.accessibility_standards:
            if standard not in valid_accessibility_standards:
                raise ValueError(f"Invalid accessibility standard. Must be one of: {valid_accessibility_standards}")

        valid_backend_types = ["windows", "linux", "macos", "web"]
        if self.backend_type not in valid_backend_types:
            raise ValueError(f"Invalid backend type. Must be one of: {valid_backend_types}")

    def get(self, key: str, default: Any = None) -> Any:
        """
        Get configuration value by key.
        
        Args:
            key: Configuration key
            default: Default value if key doesn't exist
            
        Returns:
            Configuration value
            
        Raises:
            AttributeError: If key doesn't exist and no default provided
        """
        if hasattr(self, key):
            return getattr(self, key)
        if default is not None:
            return default
        raise AttributeError(f"Configuration key '{key}' does not exist")
        
    def set(self, key: str, value: Any) -> None:
        """
        Set configuration value.
        
        Args:
            key: Configuration key
            value: Value to set
            
        Raises:
            AttributeError: If key doesn't exist
        """
        if hasattr(self, key):
            setattr(self, key, value)
        else:
            raise AttributeError(f"Configuration key '{key}' does not exist")
