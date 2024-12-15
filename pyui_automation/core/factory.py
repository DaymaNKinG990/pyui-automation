import platform
import os
from pathlib import Path
from typing import Optional, Union

from ..input import Keyboard, Mouse
from ..ocr import OCREngine
from .visual import VisualTester

from ..backends.base import BaseBackend
from ..backends.windows import WindowsBackend
from ..backends.linux import LinuxBackend
from ..backends.macos import MacOSBackend


class BackendFactory:
    """Factory class for creating automation backends"""
    
    @staticmethod
    def create_backend(backend_type: Optional[str] = None) -> BaseBackend:
        """
        Create and return appropriate backend instance

        Args:
            backend_type (str, optional): Type of backend to create. If not specified,
                the current platform will be used

        Returns:
            BaseBackend: The created backend instance

        Raises:
            ValueError: If unsupported platform is specified
        """
        if backend_type is None:
            backend_type = platform.system().lower()

        backend_map = {
            'windows': WindowsBackend,
            'linux': LinuxBackend,
            'darwin': MacOSBackend,
            'macos': MacOSBackend,
        }

        backend_class = backend_map.get(backend_type.lower())
        if not backend_class:
            raise ValueError(f"Unsupported platform: {backend_type}")

        return backend_class()

class ComponentFactory:
    """Factory for creating various automation components"""
    
    @staticmethod
    def create_keyboard(backend: BaseBackend) -> Keyboard:
        """
        Create keyboard controller

        Args:
            backend (BaseBackend): Backend instance to use

        Returns:
            Keyboard: The created keyboard controller
        """
        return Keyboard(backend)

    @staticmethod
    def create_mouse(backend: BaseBackend) -> Mouse:
        """
        Create mouse controller

        Args:
            backend (BaseBackend): Backend instance to use

        Returns:
            Mouse: The created mouse controller
        """
        return Mouse(backend)

    @staticmethod
    def create_ocr_engine() -> OCREngine:
        """
        Create OCR engine

        Returns:
            OCREngine: The created OCR engine
        """
        return OCREngine()

    @staticmethod
    def create_visual_tester(baseline_dir: Optional[Union[str, Path]] = None) -> VisualTester:
        """
        Create and return a VisualTester instance for visual testing.

        Args:
            baseline_dir (Optional[Union[str, Path]]): Directory to store baseline images.
                If not provided, a default directory named 'visual_baseline' will be
                created in the current working directory.

        Returns:
            VisualTester: The created VisualTester instance.
        """
        if baseline_dir is None:
            baseline_dir = os.path.join(os.getcwd(), 'visual_baseline')
            os.makedirs(baseline_dir, exist_ok=True)
        baseline_dir = Path(baseline_dir)
        return VisualTester(baseline_dir)
