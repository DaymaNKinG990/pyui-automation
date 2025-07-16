from abc import ABC, abstractmethod
from typing import List

class OCREngineService(ABC):
    """Abstract OCR engine service interface."""

    @abstractmethod
    def set_languages(self, languages: List[str]) -> None:
        pass

    @abstractmethod
    def recognize_text(self, image) -> str:
        pass 