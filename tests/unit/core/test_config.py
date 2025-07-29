"""
Tests for configuration management
"""

import pytest
from pathlib import Path

from pyui_automation.core.config import AutomationConfig


class TestAutomationConfig:
    """Test AutomationConfig class"""
    
    def test_automation_config_creation(self) -> None:
        """Test basic AutomationConfig creation"""
        config = AutomationConfig()
        assert config.screenshot_format == "png"
        assert config.screenshot_quality == 90
        assert config.visual_testing_enabled is False
        assert config.performance_enabled is False
        assert config.default_timeout == 10.0
        assert config.default_interval == 0.5
        assert config.ocr_enabled is False
        assert config.backend_type == "windows"
    
    def test_automation_config_with_custom_values(self) -> None:
        """Test AutomationConfig with custom values"""
        config = AutomationConfig(
            screenshot_format="jpg",
            screenshot_quality=80,
            visual_testing_enabled=True,
            performance_enabled=True,
            default_timeout=30.0,
            ocr_enabled=True,
            backend_type="linux"
        )
        
        assert config.screenshot_format == "jpg"
        assert config.screenshot_quality == 80
        assert config.visual_testing_enabled is True
        assert config.performance_enabled is True
        assert config.default_timeout == 30.0
        assert config.ocr_enabled is True
        assert config.backend_type == "linux"
    
    def test_automation_config_post_init(self) -> None:
        """Test post-initialization setup"""
        config = AutomationConfig()
        
        assert config.performance_metrics == ["cpu", "memory", "response_time"]
        assert config.ocr_languages == ["eng"]
        assert config.backend_options == {}
    
    def test_automation_config_set_method(self) -> None:
        """Test set method"""
        config = AutomationConfig()
        
        config.set("screenshot_format", "jpg")
        config.set("custom_setting", "custom_value")
        
        assert config.get("screenshot_format") == "jpg"
        assert config.get("custom_setting") == "custom_value"
    
    def test_automation_config_get_method(self) -> None:
        """Test get method"""
        config = AutomationConfig()
        
        assert config.get("screenshot_format") == "png"
        assert config.get("nonexistent_key", "default") == "default"
    
    def test_automation_config_screenshot_dir_property(self) -> None:
        """Test screenshot_dir property"""
        config = AutomationConfig()
        
        # Test setting with string
        config.screenshot_dir = "/tmp/screenshots"
        assert isinstance(config.screenshot_dir, Path)
        assert config.screenshot_dir.name == "screenshots"
        
        # Test setting with Path
        test_path = Path("/test/path")
        config.screenshot_dir = test_path
        assert config.screenshot_dir == test_path
        
        # Test setting None
        config.screenshot_dir = None
        assert config.screenshot_dir is None
    
    def test_automation_config_validation_valid(self) -> None:
        """Test validation with valid values"""
        config = AutomationConfig()
        # Should not raise exception
        config.validate()


class TestAutomationConfigValidation:
    """Test configuration validation with parameterized tests"""
    
    @pytest.mark.parametrize("field,invalid_value,expected_error", [
        ("screenshot_quality", 150, "Screenshot quality must be between 0 and 100"),
        ("screenshot_quality", -10, "Screenshot quality must be between 0 and 100"),
        ("visual_threshold", 1.5, "Visual threshold must be between 0 and 1"),
        ("visual_threshold", -0.1, "Visual threshold must be between 0 and 1"),
        ("performance_interval", 0, "Performance interval must be positive"),
        ("performance_interval", -1.0, "Performance interval must be positive"),
        ("default_timeout", 0, "Default timeout must be positive"),
        ("default_timeout", -5.0, "Default timeout must be positive"),
        ("default_interval", 0, "Default interval must be positive"),
        ("default_interval", -0.1, "Default interval must be positive"),
        ("implicit_wait", -1.0, "Implicit wait must be non-negative"),
        ("ocr_confidence", 1.5, "OCR confidence must be between 0 and 1"),
        ("ocr_confidence", -0.1, "OCR confidence must be between 0 and 1"),
        ("screenshot_format", "invalid", "Invalid screenshot format"),
        ("visual_algorithm", "invalid", "Invalid visual algorithm"),
        ("performance_metrics", ["invalid_metric"], "Invalid performance metric"),
        ("ocr_languages", ["invalid_lang"], "Invalid OCR language"),
        ("backend_type", "invalid", "Invalid backend type"),
    ])
    def test_validation_invalid_values(self, field, invalid_value, expected_error) -> None:
        """Test validation with various invalid values"""
        config = AutomationConfig()
        setattr(config, field, invalid_value)
        with pytest.raises(ValueError, match=expected_error):
            config.validate()


class TestAutomationConfigSet:
    """Test configuration set method"""
    
    def test_set_custom_key(self) -> None:
        """Test setting a custom key"""
        config = AutomationConfig()
        config.set('custom_key', 'custom_value')
        assert config.get('custom_key') == 'custom_value'
    
    def test_set_screenshot_dir_with_string(self) -> None:
        """Test setting screenshot_dir with string value"""
        config = AutomationConfig()
        config.set('screenshot_dir', '/path/to/screenshots')
        assert isinstance(config.screenshot_dir, Path)
        assert config.screenshot_dir.parts[-3:] == ('path', 'to', 'screenshots')
    
    def test_set_screenshot_dir_with_path(self) -> None:
        """Test setting screenshot_dir with Path value"""
        config = AutomationConfig()
        path = Path('/path/to/screenshots')
        config.set('screenshot_dir', path)
        assert config.screenshot_dir == path
    
    def test_set_screenshot_dir_with_none(self) -> None:
        """Test setting screenshot_dir with None value"""
        config = AutomationConfig()
        config.set('screenshot_dir', None)
        assert config.screenshot_dir is None


class TestAutomationConfigGet:
    """Test configuration get method"""
    
    def test_get_existing_key(self) -> None:
        """Test getting existing configuration key"""
        config = AutomationConfig()
        value = config.get('screenshot_format')
        assert value == "png"
    
    def test_get_nonexistent_key_with_default(self) -> None:
        """Test getting nonexistent key with default value"""
        config = AutomationConfig()
        value = config.get('nonexistent_key', 'default_value')
        assert value == 'default_value'
    
    def test_get_nonexistent_key_without_default(self) -> None:
        """Test getting nonexistent key without default value"""
        config = AutomationConfig()
        value = config.get('nonexistent_key')
        assert value is None


class TestAutomationConfigPostInit:
    """Test configuration post-init method"""
    
    @pytest.mark.parametrize("field,expected_default", [
        ("performance_metrics", ["cpu", "memory", "response_time"]),
        ("ocr_languages", ["eng"]),
        ("backend_options", {}),
    ])
    def test_post_init_with_none_values(self, field, expected_default) -> None:
        """Test post-init with None values for various fields"""
        config = AutomationConfig()
        setattr(config, field, None)
        config.__post_init__()
        assert getattr(config, field) == expected_default
    
    def test_post_init_with_string_screenshot_dir(self) -> None:
        """Test post-init with string screenshot directory"""
        config = AutomationConfig()
        config._screenshot_dir = Path("/path/to/screenshots")
        config.__post_init__()
        assert isinstance(config._screenshot_dir, Path)
        assert config._screenshot_dir.parts[-3:] == ('path', 'to', 'screenshots')
    
    def test_post_init_with_string_visual_baseline_dir(self) -> None:
        """Test post-init with string visual baseline directory"""
        config = AutomationConfig()
        config.visual_baseline_dir = Path("/path/to/baseline")
        config.__post_init__()
        assert isinstance(config.visual_baseline_dir, Path)
        assert config.visual_baseline_dir.parts[-3:] == ('path', 'to', 'baseline')
    
    def test_post_init_with_string_performance_output_dir(self) -> None:
        """Test post-init with string performance output directory"""
        config = AutomationConfig()
        config.performance_output_dir = Path("/path/to/output")
        config.__post_init__()
        assert isinstance(config.performance_output_dir, Path)
        assert config.performance_output_dir.parts[-3:] == ('path', 'to', 'output')
    
    def test_post_init_with_path_objects(self) -> None:
        """Test post-init with Path objects"""
        config = AutomationConfig()
        path = Path("/path/to/test")
        config._screenshot_dir = path
        config.visual_baseline_dir = path
        config.performance_output_dir = path
        config.__post_init__()
        assert config._screenshot_dir == path
        assert config.visual_baseline_dir == path
        assert config.performance_output_dir == path


class TestConfigIntegration:
    """Integration tests for configuration - broken down into atomic tests"""
    
    def test_config_creation_and_validation(self) -> None:
        """Test config creation and validation"""
        config = AutomationConfig(
            screenshot_format="jpg",
            screenshot_quality=85,
            visual_testing_enabled=True,
            performance_enabled=True,
            default_timeout=20.0,
            ocr_enabled=True
        )
        config.validate()
        assert config.screenshot_format == "jpg"
        assert config.screenshot_quality == 85
    
    def test_config_modification(self) -> None:
        """Test config modification"""
        config = AutomationConfig()
        config.set("custom_timeout", 15.0)
        config.set("custom_interval", 0.3)
        
        assert config.get("custom_timeout") == 15.0
        assert config.get("custom_interval") == 0.3
    
    def test_config_screenshot_directory_setup(self) -> None:
        """Test screenshot directory setup"""
        config = AutomationConfig()
        config.screenshot_dir = "/custom/screenshots"
        assert config.screenshot_dir is not None
        assert config.screenshot_dir.name == "screenshots"
    
    def test_config_with_all_valid_values(self) -> None:
        """Test config with all valid values"""
        config = AutomationConfig(
            screenshot_format="png",
            screenshot_quality=95,
            visual_testing_enabled=True,
            visual_baseline_dir=Path("/baseline"),
            visual_threshold=0.98,
            visual_algorithm="ssim",
            performance_enabled=True,
            performance_metrics=["cpu", "memory"],
            performance_interval=2.0,
            performance_output_dir=Path("/performance"),
            default_timeout=30.0,
            default_interval=1.0,
            implicit_wait=2.0,
            polling_interval=0.1,
            ocr_enabled=True,
            ocr_languages=["eng", "fra"],
            ocr_confidence=0.8,
            backend_type="linux",
            backend_options={"option1": "value1"}
        )
        
        config.validate()
        assert config.screenshot_format == "png"
        assert config.screenshot_quality == 95
        assert config.visual_testing_enabled is True
        assert config.performance_enabled is True
        assert config.ocr_enabled is True
        assert config.backend_type == "linux"
        assert config.backend_options is not None
        assert config.backend_options["option1"] == "value1" 