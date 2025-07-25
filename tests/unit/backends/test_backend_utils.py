"""
Tests for backend utilities
"""
import pytest
import platform

from pyui_automation.backends.backend_utils import get_backend_type, validate_backend_config


class TestValidOcrLanguages:
    """Tests for ValidOcrLanguages dataclass"""
    
    def test_valid_ocr_languages_default(self):
        """Test ValidOcrLanguages with default languages"""
        languages = ValidOcrLanguages()
        assert languages.languages == ("eng", "fra", "deu", "spa")
    
    def test_valid_ocr_languages_custom(self):
        """Test ValidOcrLanguages with custom languages"""
        custom_languages = ("eng", "rus", "chi")
        languages = ValidOcrLanguages(languages=custom_languages)
        assert languages.languages == custom_languages
    
    def test_valid_ocr_languages_immutable(self):
        """Test that ValidOcrLanguages is immutable"""
        languages = ValidOcrLanguages()
        
        # Should not be able to modify the tuple
        with pytest.raises(AttributeError):
            languages.languages = ("new", "lang")
    
    def test_valid_ocr_languages_frozen(self):
        """Test that ValidOcrLanguages is frozen"""
        languages = ValidOcrLanguages()
        
        # Should not be able to add new attributes
        with pytest.raises(AttributeError):
            languages.new_attribute = "value"
    
    def test_valid_ocr_languages_repr(self):
        """Test ValidOcrLanguages string representation"""
        languages = ValidOcrLanguages()
        repr_str = repr(languages)
        assert "ValidOcrLanguages" in repr_str
        assert "eng" in repr_str
        assert "fra" in repr_str
    
    def test_valid_ocr_languages_equality(self):
        """Test ValidOcrLanguages equality"""
        languages1 = ValidOcrLanguages()
        languages2 = ValidOcrLanguages()
        languages3 = ValidOcrLanguages(languages=("eng", "rus"))
        
        assert languages1 == languages2
        assert languages1 != languages3
    
    def test_valid_ocr_languages_hash(self):
        """Test ValidOcrLanguages hashability"""
        languages1 = ValidOcrLanguages()
        languages2 = ValidOcrLanguages()
        
        # Should be hashable since it's frozen
        assert hash(languages1) == hash(languages2)
        
        # Can be used as dictionary key
        test_dict = {languages1: "test"}
        assert test_dict[languages2] == "test" 