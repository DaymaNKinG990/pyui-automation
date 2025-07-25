"""
Tests for configuration management
"""

import pytest
from pathlib import Path

from pyui_automation.core.config import AutomationConfig


class TestAutomationConfig:
    """Test AutomationConfig class"""
    
    def test_automation_config_creation(self):
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
    
    def test_automation_config_with_custom_values(self):
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
    
    def test_automation_config_post_init(self):
        """Test post-initialization setup"""
        config = AutomationConfig()
        
        assert config.performance_metrics == ["cpu", "memory", "response_time"]
        assert config.ocr_languages == ["eng"]
        assert config.backend_options == {}
    
    def test_automation_config_set_method(self):
        """Test set method"""
        config = AutomationConfig()
        
        config.set("screenshot_format", "jpg")
        config.set("custom_setting", "custom_value")
        
        assert config.screenshot_format == "jpg"
        assert config.custom_setting == "custom_value"
    
    def test_automation_config_get_method(self):
        """Test get method"""
        config = AutomationConfig()
        
        assert config.get("screenshot_format") == "png"
        assert config.get("nonexistent_key", "default") == "default"
    
    def test_automation_config_screenshot_dir_property(self):
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
    
    def test_automation_config_validation_valid(self):
        """Test validation with valid values"""
        config = AutomationConfig()
        # Should not raise exception
        config.validate()
    
    def test_automation_config_validation_invalid_screenshot_quality(self):
        """Test validation with invalid screenshot quality"""
        config = AutomationConfig(screenshot_quality=150)
        with pytest.raises(ValueError, match="Screenshot quality must be between 0 and 100"):
            config.validate()
    
    def test_automation_config_validation_invalid_visual_threshold(self):
        """Test validation with invalid visual threshold"""
        config = AutomationConfig(visual_threshold=1.5)
        with pytest.raises(ValueError, match="Visual threshold must be between 0 and 1"):
            config.validate()
    
    def test_automation_config_validation_invalid_performance_interval(self):
        """Test validation with invalid performance interval"""
        config = AutomationConfig(performance_interval=0)
        with pytest.raises(ValueError, match="Performance interval must be positive"):
            config.validate()
    
    def test_automation_config_validation_invalid_timeout(self):
        """Test validation with invalid timeout"""
        config = AutomationConfig(default_timeout=0)
        with pytest.raises(ValueError, match="Default timeout must be positive"):
            config.validate()
    
    def test_automation_config_validation_invalid_interval(self):
        """Test validation with invalid interval"""
        config = AutomationConfig(default_interval=0)
        with pytest.raises(ValueError, match="Default interval must be positive"):
            config.validate()
    
    def test_automation_config_validation_invalid_implicit_wait(self):
        """Test validation with invalid implicit wait"""
        config = AutomationConfig(implicit_wait=-1)
        with pytest.raises(ValueError, match="Implicit wait must be non-negative"):
            config.validate()
    
    def test_automation_config_validation_invalid_ocr_confidence(self):
        """Test validation with invalid OCR confidence"""
        config = AutomationConfig(ocr_confidence=1.5)
        with pytest.raises(ValueError, match="OCR confidence must be between 0 and 1"):
            config.validate()
    
    def test_automation_config_validation_invalid_screenshot_format(self):
        """Test validation with invalid screenshot format"""
        config = AutomationConfig(screenshot_format="invalid")
        with pytest.raises(ValueError, match="Invalid screenshot format"):
            config.validate()
    
    def test_automation_config_validation_invalid_visual_algorithm(self):
        """Test validation with invalid visual algorithm"""
        config = AutomationConfig(visual_algorithm="invalid")
        with pytest.raises(ValueError, match="Invalid visual algorithm"):
            config.validate()
    
    def test_automation_config_validation_invalid_performance_metrics(self):
        """Test validation with invalid performance metrics"""
        config = AutomationConfig(performance_metrics=["invalid_metric"])
        with pytest.raises(ValueError, match="Invalid performance metric"):
            config.validate()
    
    def test_automation_config_validation_invalid_ocr_languages(self):
        """Test validation with invalid OCR languages"""
        config = AutomationConfig(ocr_languages=["invalid_lang"])
        with pytest.raises(ValueError, match="Invalid OCR language"):
            config.validate()
    
    def test_automation_config_validation_invalid_backend_type(self):
        """Test validation with invalid backend type"""
        config = AutomationConfig(backend_type="invalid")
        with pytest.raises(ValueError, match="Invalid backend type"):
            config.validate()


class TestConfigIntegration:
    """Integration tests for configuration"""
    
    def test_config_complete_workflow(self):
        """Test complete configuration workflow"""
        # Create config
        config = AutomationConfig(
            screenshot_format="jpg",
            screenshot_quality=85,
            visual_testing_enabled=True,
            performance_enabled=True,
            default_timeout=20.0,
            ocr_enabled=True
        )
        
        # Validate
        config.validate()
        
        # Modify settings
        config.set("custom_timeout", 15.0)
        config.set("custom_interval", 0.3)
        
        # Verify settings
        assert config.get("screenshot_format") == "jpg"
        assert config.get("custom_timeout") == 15.0
        assert config.get("custom_interval") == 0.3
        
        # Test screenshot directory
        config.screenshot_dir = "/custom/screenshots"
        assert config.screenshot_dir.name == "screenshots"
    
    def test_config_with_all_valid_values(self):
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
        
        # Should not raise exception
        config.validate()
        
        # Verify all values
        assert config.screenshot_format == "png"
        assert config.screenshot_quality == 95
        assert config.visual_testing_enabled is True
        assert config.performance_enabled is True
        assert config.ocr_enabled is True
        assert config.backend_type == "linux"
        assert config.backend_options is not None
        assert config.backend_options["option1"] == "value1" 


class TestAutomationConfigSet:
    """Test configuration set method"""
    
    def test_set_custom_key(self):
        """Test setting a custom key"""
        config = AutomationConfig()
        config.set('custom_key', 'custom_value')
        assert config.custom_key == 'custom_value'
    
    def test_set_screenshot_dir_with_string(self):
        """Test setting screenshot_dir with string value"""
        config = AutomationConfig()
        config.set('screenshot_dir', '/path/to/screenshots')
        assert isinstance(config.screenshot_dir, Path)
        # Use Path.parts to compare path components instead of string comparison
        assert config.screenshot_dir.parts[-3:] == ('path', 'to', 'screenshots')
    
    def test_set_screenshot_dir_with_path(self):
        """Test setting screenshot_dir with Path value"""
        config = AutomationConfig()
        path = Path('/path/to/screenshots')
        config.set('screenshot_dir', path)
        assert config.screenshot_dir == path
    
    def test_set_screenshot_dir_with_none(self):
        """Test setting screenshot_dir with None value"""
        config = AutomationConfig()
        config.set('screenshot_dir', None)
        assert config.screenshot_dir is None


class TestAutomationConfigValidation:
    """Test configuration validation"""
    
    def test_validate_with_invalid_screenshot_quality(self):
        """Test validation with invalid screenshot quality"""
        config = AutomationConfig()
        config.screenshot_quality = 150
        with pytest.raises(ValueError, match="Screenshot quality must be between 0 and 100"):
            config.validate()
    
    def test_validate_with_invalid_screenshot_quality_negative(self):
        """Test validation with negative screenshot quality"""
        config = AutomationConfig()
        config.screenshot_quality = -10
        with pytest.raises(ValueError, match="Screenshot quality must be between 0 and 100"):
            config.validate()
    
    def test_validate_with_invalid_visual_threshold(self):
        """Test validation with invalid visual threshold"""
        config = AutomationConfig()
        config.visual_threshold = 1.5
        with pytest.raises(ValueError, match="Visual threshold must be between 0 and 1"):
            config.validate()
    
    def test_validate_with_invalid_visual_threshold_negative(self):
        """Test validation with negative visual threshold"""
        config = AutomationConfig()
        config.visual_threshold = -0.1
        with pytest.raises(ValueError, match="Visual threshold must be between 0 and 1"):
            config.validate()
    
    def test_validate_with_invalid_performance_interval(self):
        """Test validation with invalid performance interval"""
        config = AutomationConfig()
        config.performance_interval = 0
        with pytest.raises(ValueError, match="Performance interval must be positive"):
            config.validate()
    
    def test_validate_with_invalid_performance_interval_negative(self):
        """Test validation with negative performance interval"""
        config = AutomationConfig()
        config.performance_interval = -1.0
        with pytest.raises(ValueError, match="Performance interval must be positive"):
            config.validate()
    
    def test_validate_with_invalid_default_timeout(self):
        """Test validation with invalid default timeout"""
        config = AutomationConfig()
        config.default_timeout = 0
        with pytest.raises(ValueError, match="Default timeout must be positive"):
            config.validate()
    
    def test_validate_with_invalid_default_timeout_negative(self):
        """Test validation with negative default timeout"""
        config = AutomationConfig()
        config.default_timeout = -5.0
        with pytest.raises(ValueError, match="Default timeout must be positive"):
            config.validate()
    
    def test_validate_with_invalid_default_interval(self):
        """Test validation with invalid default interval"""
        config = AutomationConfig()
        config.default_interval = 0
        with pytest.raises(ValueError, match="Default interval must be positive"):
            config.validate()
    
    def test_validate_with_invalid_default_interval_negative(self):
        """Test validation with negative default interval"""
        config = AutomationConfig()
        config.default_interval = -0.1
        with pytest.raises(ValueError, match="Default interval must be positive"):
            config.validate()
    
    def test_validate_with_invalid_implicit_wait(self):
        """Test validation with invalid implicit wait"""
        config = AutomationConfig()
        config.implicit_wait = -1.0
        with pytest.raises(ValueError, match="Implicit wait must be non-negative"):
            config.validate()
    
    def test_validate_with_invalid_ocr_confidence(self):
        """Test validation with invalid OCR confidence"""
        config = AutomationConfig()
        config.ocr_confidence = 1.5
        with pytest.raises(ValueError, match="OCR confidence must be between 0 and 1"):
            config.validate()
    
    def test_validate_with_invalid_ocr_confidence_negative(self):
        """Test validation with negative OCR confidence"""
        config = AutomationConfig()
        config.ocr_confidence = -0.1
        with pytest.raises(ValueError, match="OCR confidence must be between 0 and 1"):
            config.validate()
    
    def test_validate_with_invalid_screenshot_format(self):
        """Test validation with invalid screenshot format"""
        config = AutomationConfig()
        config.screenshot_format = "invalid"
        with pytest.raises(ValueError, match="Invalid screenshot format"):
            config.validate()
    
    def test_validate_with_invalid_visual_algorithm(self):
        """Test validation with invalid visual algorithm"""
        config = AutomationConfig()
        config.visual_algorithm = "invalid"
        with pytest.raises(ValueError, match="Invalid visual algorithm"):
            config.validate()
    
    def test_validate_with_invalid_performance_metrics(self):
        """Test validation with invalid performance metrics"""
        config = AutomationConfig()
        config.performance_metrics = ["invalid_metric"]
        with pytest.raises(ValueError, match="Invalid performance metric"):
            config.validate()
    
    def test_validate_with_invalid_ocr_languages(self):
        """Test validation with invalid OCR languages"""
        config = AutomationConfig()
        config.ocr_languages = ["invalid_lang"]
        with pytest.raises(ValueError, match="Invalid OCR language"):
            config.validate()
    
    def test_validate_with_invalid_backend_type(self):
        """Test validation with invalid backend type"""
        config = AutomationConfig()
        config.backend_type = "invalid"
        with pytest.raises(ValueError, match="Invalid backend type"):
            config.validate()


class TestAutomationConfigGet:
    """Test configuration get method"""
    
    def test_get_existing_key(self):
        """Test getting existing configuration key"""
        config = AutomationConfig()
        value = config.get('screenshot_format')
        assert value == "png"
    
    def test_get_nonexistent_key_with_default(self):
        """Test getting nonexistent key with default value"""
        config = AutomationConfig()
        value = config.get('nonexistent_key', 'default_value')
        assert value == 'default_value'
    
    def test_get_nonexistent_key_without_default(self):
        """Test getting nonexistent key without default value"""
        config = AutomationConfig()
        value = config.get('nonexistent_key')
        assert value is None


class TestAutomationConfigPostInit:
    """Test configuration post-init method"""
    
    def test_post_init_with_none_performance_metrics(self):
        """Test post-init with None performance metrics"""
        config = AutomationConfig()
        config.performance_metrics = None
        config.__post_init__()
        assert config.performance_metrics == ["cpu", "memory", "response_time"]
    
    def test_post_init_with_none_ocr_languages(self):
        """Test post-init with None OCR languages"""
        config = AutomationConfig()
        config.ocr_languages = None
        config.__post_init__()
        assert config.ocr_languages == ["eng"]
    
    def test_post_init_with_none_backend_options(self):
        """Test post-init with None backend options"""
        config = AutomationConfig()
        config.backend_options = None
        config.__post_init__()
        assert config.backend_options == {}
    
    def test_post_init_with_string_screenshot_dir(self):
        """Test post-init with string screenshot directory"""
        config = AutomationConfig()
        config._screenshot_dir = "/path/to/screenshots"
        config.__post_init__()
        assert isinstance(config._screenshot_dir, Path)
        # Use Path.parts to compare path components instead of string comparison
        assert config._screenshot_dir.parts[-3:] == ('path', 'to', 'screenshots')
    
    def test_post_init_with_string_visual_baseline_dir(self):
        """Test post-init with string visual baseline directory"""
        config = AutomationConfig()
        config.visual_baseline_dir = "/path/to/baseline"
        config.__post_init__()
        assert isinstance(config.visual_baseline_dir, Path)
        # Use Path.parts to compare path components instead of string comparison
        assert config.visual_baseline_dir.parts[-3:] == ('path', 'to', 'baseline')
    
    def test_post_init_with_string_performance_output_dir(self):
        """Test post-init with string performance output directory"""
        config = AutomationConfig()
        config.performance_output_dir = "/path/to/output"
        config.__post_init__()
        assert isinstance(config.performance_output_dir, Path)
        # Use Path.parts to compare path components instead of string comparison
        assert config.performance_output_dir.parts[-3:] == ('path', 'to', 'output')
    
    def test_post_init_with_path_objects(self):
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