"""
Tests for backend utilities
"""

import pytest
import dataclasses
from pyui_automation.backends.backend_utils import ValidOcrLanguages


class TestValidOcrLanguages:
    """Test ValidOcrLanguages dataclass"""
    
    def test_default_languages(self):
        """Test default languages"""
        languages = ValidOcrLanguages()
        assert languages.languages == ("eng", "fra", "deu", "spa")
    
    def test_custom_languages(self):
        """Test custom languages"""
        custom_langs = ("eng", "rus", "spa")
        languages = ValidOcrLanguages(languages=custom_langs)
        assert languages.languages == custom_langs
    
    def test_immutable_tuple(self):
        """Test that languages tuple is immutable"""
        languages = ValidOcrLanguages()
        # Проверяем что tuple действительно неизменяемый
        with pytest.raises(TypeError):
            languages.languages[0] = "invalid"  # type: ignore
    
    def test_frozen_dataclass(self, mocker):
        """Test that dataclass is frozen and cannot be modified"""
        languages = ValidOcrLanguages()
        
        # Проверяем что нельзя изменять атрибуты frozen dataclass
        with pytest.raises(dataclasses.FrozenInstanceError):
            languages.languages = ("new", "langs")  # type: ignore
    
    def test_empty_languages(self):
        """Test with empty languages tuple"""
        empty_langs = ()
        languages = ValidOcrLanguages(languages=empty_langs)
        assert languages.languages == empty_langs
    
    def test_single_language(self):
        """Test with single language"""
        single_lang = ("eng",)
        languages = ValidOcrLanguages(languages=single_lang)
        assert languages.languages == single_lang
    
    def test_languages_immutability_after_creation(self, mocker):
        """Test that languages tuple cannot be modified after creation"""
        original_langs = ("eng", "fra")
        languages = ValidOcrLanguages(languages=original_langs)
        
        # Проверяем что tuple действительно неизменяемый
        # Попытка изменить элемент tuple должна вызвать ошибку
        with pytest.raises(TypeError):
            languages.languages[0] = "deu"  # type: ignore
    
    def test_dataclass_repr(self):
        """Test dataclass string representation"""
        languages = ValidOcrLanguages()
        repr_str = repr(languages)
        assert "ValidOcrLanguages" in repr_str
        assert "languages=" in repr_str
    
    def test_dataclass_equality(self):
        """Test dataclass equality comparison"""
        lang1 = ValidOcrLanguages()
        lang2 = ValidOcrLanguages()
        lang3 = ValidOcrLanguages(languages=("eng", "rus"))
        
        assert lang1 == lang2
        assert lang1 != lang3 