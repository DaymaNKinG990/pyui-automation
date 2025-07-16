import pytest
from pathlib import Path
from unittest.mock import MagicMock
from pyui_automation.core.config import AutomationConfig
from pyui_automation.core.session import AutomationSession


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

def test_validate_invalid_values(config):
    config.screenshot_quality = 200
    with pytest.raises(ValueError):
        config.validate()
    config.screenshot_quality = 90
    config.visual_threshold = -0.1
    with pytest.raises(ValueError):
        config.validate()
    config.visual_threshold = 0.95
    config.performance_interval = 0
    with pytest.raises(ValueError):
        config.validate()
    config.performance_interval = 1.0
    config.default_timeout = 0
    with pytest.raises(ValueError):
        config.validate()
    config.default_timeout = 10.0
    config.default_interval = 0
    with pytest.raises(ValueError):
        config.validate()
    config.default_interval = 0.5
    config.implicit_wait = -1
    with pytest.raises(ValueError):
        config.validate()
    config.implicit_wait = 0
    config.ocr_confidence = 2
    with pytest.raises(ValueError):
        config.validate()
    config.ocr_confidence = 0.7
    config.screenshot_format = 'tiff'
    with pytest.raises(ValueError):
        config.validate()
    config.screenshot_format = 'png'
    config.visual_algorithm = 'unknown'
    with pytest.raises(ValueError):
        config.validate()
    config.visual_algorithm = 'ssim'
    config.performance_metrics = ['cpu', 'invalid']
    with pytest.raises(ValueError):
        config.validate()
    config.performance_metrics = ['cpu']
    config.ocr_languages = ['invalid']
    with pytest.raises(ValueError):
        config.validate()
    config.ocr_languages = ['eng']
    config.accessibility_standards = ['invalid']
    with pytest.raises(ValueError):
        config.validate()
    config.accessibility_standards = ['wcag2a']
    config.backend_type = 'invalid'
    with pytest.raises(ValueError):
        config.validate()
    config.backend_type = 'windows'

def test_set_invalid_key_type(config):
    with pytest.raises(Exception):
        config.set(123, 1)

def test_screenshot_dir_invalid_type(config):
    with pytest.raises(Exception):
        config.screenshot_dir = 123

def test_get_nonexistent_key_no_default(config):
    assert config.get('definitely_not_exist') is None
