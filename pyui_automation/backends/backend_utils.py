# Python imports
from dataclasses import dataclass, field
from enum import Enum
from typing import Tuple


class OcrLanguage(Enum):
    """
    Enum for supported OCR languages.
    Contains the most commonly used languages for text recognition.
    """
    ENGLISH = "eng"
    FRENCH = "fra"
    GERMAN = "deu"
    SPANISH = "spa"
    RUSSIAN = "rus"
    CHINESE_SIMPLIFIED = "chi_sim"
    CHINESE_TRADITIONAL = "chi_tra"
    JAPANESE = "jpn"
    KOREAN = "kor"
    ITALIAN = "ita"
    PORTUGUESE = "por"
    DUTCH = "nld"
    POLISH = "pol"
    TURKISH = "tur"
    ARABIC = "ara"
    HINDI = "hin"
    THAI = "tha"
    VIETNAMESE = "vie"
    GREEK = "ell"
    HEBREW = "heb"


@dataclass(frozen=True)
class ValidOcrLanguages:
    """
    Dataclass for storing valid OCR language codes.
    """
    languages: Tuple[str, ...] = field(default_factory=lambda: tuple(lang.value for lang in OcrLanguage.__members__.values()))


def get_supported_languages() -> Tuple[str, ...]:
    """
    Get tuple of all supported language codes.
    
    Returns:
        Tuple of language codes supported by OCR engine.
    """
    return tuple(lang.value for lang in OcrLanguage.__members__.values())


def is_language_supported(language_code: str) -> bool:
    """
    Check if a language code is supported.
    
    Args:
        language_code: Language code to check (e.g., "eng", "fra")
        
    Returns:
        True if language is supported, False otherwise.
    """
    return language_code in get_supported_languages()


def get_language_name(language_code: str) -> str:
    """
    Get the display name of a language code.
    
    Args:
        language_code: Language code to get name for
        
    Returns:
        Display name of the language or the original code if not found.
    """
    for lang in OcrLanguage.__members__.values():
        if lang.value == language_code:
            return lang.name.replace("_", " ").title()
    return language_code 