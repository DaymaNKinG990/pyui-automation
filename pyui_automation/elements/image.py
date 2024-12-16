from typing import Optional, Any, Tuple
from PIL import Image as PILImage
from .base import UIElement


class Image(UIElement):
    """Represents an image/icon element"""

    def __init__(self, native_element: Any, session: 'AutomationSession') -> None:
        super().__init__(native_element, session)

    @property
    def alt_text(self) -> str:
        """
        Get the alternative text of the image.

        Returns:
            str: Alternative text
        """
        return self._element.get_property("alt_text")

    @property
    def source(self) -> str:
        """
        Get the image source path or URL.

        Returns:
            str: Image source
        """
        return self._element.get_property("source")

    @property
    def size(self) -> Tuple[int, int]:
        """
        Get the image dimensions.

        Returns:
            Tuple[int, int]: Width and height in pixels
        """
        return (
            self._element.get_property("width"),
            self._element.get_property("height")
        )

    @property
    def is_visible(self) -> bool:
        """
        Check if the image is visible.

        Returns:
            bool: True if visible, False otherwise
        """
        return self._element.get_property("visible")

    @is_visible.deleter
    def is_visible(self):
        self._is_visible = False

    def capture(self) -> PILImage.Image:
        """
        Capture the image content as a PIL Image.

        Returns:
            PIL.Image.Image: Captured image
        """
        return self._session.capture_element(self._element)

    def save_as(self, filepath: str) -> None:
        """
        Save the image content to a file.

        Args:
            filepath (str): Path to save the image
        """
        image = self.capture()
        image.save(filepath)

    def compare_to(self, other_image: PILImage.Image, threshold: float = 0.95) -> float:
        """
        Compare this image with another image.

        Args:
            other_image (PIL.Image.Image): Image to compare with
            threshold (float): Similarity threshold (0-1)

        Returns:
            float: Similarity score (0-1)
        """
        return self._session.compare_images(
            self.capture(),
            other_image,
            threshold=threshold
        )

    def wait_until_loaded(self, timeout: float = 10) -> bool:
        """
        Wait until the image is loaded.

        Args:
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if image was loaded within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.is_visible and self.size[0] > 0 and self.size[1] > 0,
            timeout=timeout,
            error_message="Image did not load"
        )

    def wait_until_matches(self, other_image: PILImage.Image, threshold: float = 0.95, timeout: float = 10) -> bool:
        """
        Wait until the image matches another image.

        Args:
            other_image (PIL.Image.Image): Image to match
            threshold (float): Similarity threshold (0-1)
            timeout (float): Maximum time to wait in seconds

        Returns:
            bool: True if images matched within timeout, False otherwise
        """
        return self._session.wait_for_condition(
            lambda: self.compare_to(other_image, threshold) >= threshold,
            timeout=timeout,
            error_message="Images did not match"
        )
