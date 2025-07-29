"""
Configuration Manager - handles configuration management.

Responsible for:
- Configuration storage
- Configuration retrieval
- Configuration validation
- Configuration persistence
"""

from typing import Dict, Any, Optional, Union, List
from pathlib import Path
import json
import yaml
from logging import getLogger

from ..interfaces.iconfiguration_manager import IConfigurationManager


class ConfigurationManager(IConfigurationManager):
    """Manager for automation configuration"""
    
    def __init__(self, config_file: Optional[Union[str, Path]] = None):
        self._logger = getLogger(__name__)
        self._config: Dict[str, Any] = {}
        self._config_file = Path(config_file) if config_file else None
        
        # Load default configuration
        self._load_defaults()
        
        # Load from file if specified
        if self._config_file and self._config_file.exists():
            self.load_from_file(self._config_file)
    
    def _load_defaults(self) -> None:
        """Load default configuration values"""
        self._config = {
            'default_timeout': 10.0,
            'default_interval': 0.5,
            'screenshot_dir': 'screenshots',
            'log_level': 'INFO',
            'log_file': 'automation.log',
            'visual_threshold': 0.95,
            'ocr_languages': ['eng'],
            'performance_monitoring': False,
            'performance_interval': 1.0,
            'memory_leak_check': False,
            'stress_test_duration': 60.0,
            'max_sessions': 10,
            'auto_cleanup': True,
            'debug_mode': False,
            'retry_attempts': 3,
            'retry_delay': 1.0,
        }
    
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        try:
            self._config[key] = value
            self._logger.debug(f"Set config: {key} = {value}")
        except Exception as e:
            self._logger.error(f"Failed to set config {key}: {e}")
            raise
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        try:
            return self._config.get(key, default)
        except Exception as e:
            self._logger.error(f"Failed to get config {key}: {e}")
            return default
    
    def has_config(self, key: str) -> bool:
        """Check if configuration key exists"""
        try:
            return key in self._config
        except Exception as e:
            self._logger.error(f"Failed to check config {key}: {e}")
            return False
    
    def remove_config(self, key: str) -> bool:
        """Remove configuration key"""
        try:
            if key in self._config:
                del self._config[key]
                self._logger.debug(f"Removed config: {key}")
                return True
            return False
        except Exception as e:
            self._logger.error(f"Failed to remove config {key}: {e}")
            return False
    
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration values"""
        try:
            return self._config.copy()
        except Exception as e:
            self._logger.error(f"Failed to get all config: {e}")
            return {}
    
    def update_config(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration with dictionary"""
        try:
            self._config.update(config_dict)
            self._logger.info(f"Updated config with {len(config_dict)} values")
        except Exception as e:
            self._logger.error(f"Failed to update config: {e}")
            raise
    
    def reset_config(self) -> None:
        """Reset configuration to defaults"""
        try:
            self._load_defaults()
            self._logger.info("Configuration reset to defaults")
        except Exception as e:
            self._logger.error(f"Failed to reset config: {e}")
            raise
    
    def load_from_file(self, file_path: Union[str, Path]) -> bool:
        """Load configuration from file"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                self._logger.warning(f"Config file not found: {file_path}")
                return False
            
            with open(file_path, 'r', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    config_data = json.load(f)
                elif file_path.suffix.lower() in ['.yml', '.yaml']:
                    config_data = yaml.safe_load(f)
                else:
                    self._logger.error(f"Unsupported config file format: {file_path.suffix}")
                    return False
            
            if isinstance(config_data, dict):
                self._config.update(config_data)
            self._logger.info(f"Loaded config from: {file_path}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to load config from {file_path}: {e}")
            return False
    
    def save_to_file(self, file_path: Optional[Union[str, Path]] = None) -> bool:
        """Save configuration to file"""
        try:
            if file_path is None:
                file_path = self._config_file
            
            if file_path is None:
                self._logger.error("No file path specified for saving config")
                return False
            
            file_path = Path(file_path)
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                if file_path.suffix.lower() == '.json':
                    json.dump(self._config, f, indent=2, ensure_ascii=False)
                elif file_path.suffix.lower() in ['.yml', '.yaml']:
                    yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
                else:
                    self._logger.error(f"Unsupported config file format: {file_path.suffix}")
                    return False
            
            self._logger.info(f"Saved config to: {file_path}")
            return True
            
        except Exception as e:
            self._logger.error(f"Failed to save config to {file_path}: {e}")
            return False
    
    def validate_config(self) -> Dict[str, List[str]]:
        """Validate configuration values"""
        try:
            errors = []
            warnings = []
            
            # Validate timeout
            timeout = self.get_config('default_timeout')
            if not isinstance(timeout, (int, float)) or timeout <= 0:
                errors.append("default_timeout must be a positive number")
            
            # Validate interval
            interval = self.get_config('default_interval')
            if not isinstance(interval, (int, float)) or interval <= 0:
                errors.append("default_interval must be a positive number")
            
            # Validate visual threshold
            threshold = self.get_config('visual_threshold')
            if not isinstance(threshold, (int, float)) or not (0 <= threshold <= 1):
                errors.append("visual_threshold must be between 0 and 1")
            
            # Validate OCR languages
            languages = self.get_config('ocr_languages')
            if not isinstance(languages, list) or not all(isinstance(lang, str) for lang in languages):
                errors.append("ocr_languages must be a list of strings")
            
            # Validate max sessions
            max_sessions = self.get_config('max_sessions')
            if not isinstance(max_sessions, int) or max_sessions <= 0:
                errors.append("max_sessions must be a positive integer")
            
            # Warnings
            if timeout > 60:
                warnings.append("default_timeout is very high (>60s)")
            
            if interval > 5:
                warnings.append("default_interval is very high (>5s)")
            
            return {"errors": errors, "warnings": warnings}
            
        except Exception as e:
            self._logger.error(f"Failed to validate config: {e}")
            return {"errors": [f"Validation failed: {e}"], "warnings": []}
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        try:
            validation = self.validate_config()
            return {
                "total_keys": len(self._config),
                "validation": validation,
                "file_path": str(self._config_file) if self._config_file else None,
                "file_exists": self._config_file.exists() if self._config_file else False
            }
        except Exception as e:
            self._logger.error(f"Failed to get config summary: {e}")
            return {"error": str(e)} 