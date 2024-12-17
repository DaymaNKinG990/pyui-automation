import pytest
from pathlib import Path
from unittest.mock import MagicMock
from pyui_automation.core.config import AutomationConfig
from pyui_automation.core.automation_session import AutomationSession


@pytest.fixture
def config():
    return AutomationConfig()

@pytest.fixture
def mock_backend():
    """Создаем мок для бэкенда"""
    backend = MagicMock()
    return backend

@pytest.fixture
def ui_automation(mock_backend):
    """Создаем экземпляр AutomationSession с мок бэкендом"""
    return AutomationSession(backend=mock_backend)

def test_default_values(ui_automation):
    """Test default configuration values"""
    config = ui_automation.config
    
    # Проверяем наличие базовых настроек
    assert config.get('implicit_wait') is not None
    assert config.get('explicit_wait') is not None
    assert config.get('polling_interval') is not None
    
    # Проверяем значения по умолчанию
    assert isinstance(config.get('implicit_wait'), (int, float))
    assert isinstance(config.get('explicit_wait'), (int, float))
    assert isinstance(config.get('polling_interval'), (int, float))

def test_set_get_values(ui_automation):
    """Test setting and getting configuration values"""
    config = ui_automation.config
    
    # Устанавливаем новые значения
    config.set('custom_timeout', 10)
    config.set('custom_interval', 0.5)
    
    # Проверяем установленные значения
    assert config.get('custom_timeout') == 10
    assert config.get('custom_interval') == 0.5
    
    # Проверяем несуществующий ключ
    assert config.get('non_existent_key', default=None) is None

def test_screenshot_dir(config):
    """Test screenshot directory property"""
    test_path = str(Path('/test/path'))  # Convert to proper path for platform
    config.screenshot_dir = test_path
    assert isinstance(config.screenshot_dir, Path)
    assert str(config.screenshot_dir) == test_path

def test_timeout(config):
    """Test timeout property"""
    config.timeout = 20.5
    assert config.timeout == 20.5
    assert isinstance(config.timeout, float)

def test_retry_interval(config):
    """Test retry interval property"""
    config.retry_interval = 1.5
    assert config.retry_interval == 1.5
    assert isinstance(config.retry_interval, float)
