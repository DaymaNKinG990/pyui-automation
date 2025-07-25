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
    
    def test_immutable(self):
        """Test that languages tuple is immutable"""
        languages = ValidOcrLanguages()
        with pytest.raises(AttributeError):
            languages.languages = ("eng",)
    
    def test_frozen_dataclass(self):
        """Test that dataclass is frozen"""
        languages = ValidOcrLanguages()
        with pytest.raises(dataclasses.FrozenInstanceError):
            languages.languages = ("eng",) 