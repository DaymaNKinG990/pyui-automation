from .ocr import OCREngineService
from typing import List

class OCREngineServiceImpl(OCREngineService):
    def __init__(self, ocr_engine):
        self.ocr_engine = ocr_engine

    def set_languages(self, languages: List[str]) -> None:
        self.ocr_engine.set_languages(languages)

    def recognize_text(self, image) -> str:
        return self.ocr_engine.recognize_text(image) 