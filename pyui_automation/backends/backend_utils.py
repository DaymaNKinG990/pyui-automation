from dataclasses import dataclass, field
from typing import Tuple

@dataclass(frozen=True)
class ValidOcrLanguages:
    """
    Dataclass for storing valid OCR language codes.
    """
    languages: Tuple[str, ...] = field(default=("eng", "fra", "deu", "spa")) 