"""
IConfigurationManager interface - defines contract for configuration manager.

Responsible for:
- Configuration storage
- Configuration retrieval
- Configuration validation
- Configuration persistence
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, Union
from pathlib import Path


class IConfigurationManager(ABC):
    """Interface for configuration manager"""
    
    @abstractmethod
    def set_config(self, key: str, value: Any) -> None:
        """Set configuration value"""
        pass
    
    @abstractmethod
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        pass
    
    @abstractmethod
    def has_config(self, key: str) -> bool:
        """Check if configuration key exists"""
        pass
    
    @abstractmethod
    def remove_config(self, key: str) -> bool:
        """Remove configuration key"""
        pass
    
    @abstractmethod
    def get_all_config(self) -> Dict[str, Any]:
        """Get all configuration values"""
        pass
    
    @abstractmethod
    def update_config(self, config_dict: Dict[str, Any]) -> None:
        """Update configuration with dictionary"""
        pass
    
    @abstractmethod
    def reset_config(self) -> None:
        """Reset configuration to defaults"""
        pass
    
    @abstractmethod
    def load_from_file(self, file_path: Union[str, Path]) -> bool:
        """Load configuration from file"""
        pass
    
    @abstractmethod
    def save_to_file(self, file_path: Optional[Union[str, Path]] = None) -> bool:
        """Save configuration to file"""
        pass
    
    @abstractmethod
    def validate_config(self) -> Dict[str, list[str]]:
        """Validate configuration values"""
        pass
    
    @abstractmethod
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        pass 