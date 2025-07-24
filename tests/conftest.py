"""
Конфигурация и фикстуры для тестирования UI автоматизации.

Этот модуль содержит общие фикстуры и настройки для тестов, включая:
- Мок-объекты для тестирования UI элементов
- Настройку логирования
- Систему отчетности о тестах
- Конфигурацию параллельного запуска
"""

import sys
import pytest
import logging
from unittest.mock import MagicMock
import numpy as np
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

# Mock locator for tests
class MockLocator:
    """Mock locator for tests"""
    def find_element(self, *args, **kwargs):
        return MagicMock()
    
    def find_elements(self, *args, **kwargs):
        return [MagicMock()]

# Добавляем корневую директорию в PYTHONPATH
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pyui_automation.core import Application, AutomationSession
from pyui_automation.core.services.performance_monitor import PerformanceMonitor

from .data.element_data import (
    DEFAULT_ELEMENT_DATA,
    ALTERNATE_ELEMENT_DATA,
    SCREENSHOT_DATA,
    WINDOW_DATA,
    PROCESS_DATA,
    PERFORMANCE_DATA
)

# Типы
ResultDict = Dict[str, Union[str, float, Dict[str, Any]]]
TestSummary = Dict[str, int]

class LoggingSystem:
    """Система управления логированием."""
    
    _log_dir = Path(__file__).parent / 'logs'
    _log_file = _log_dir / 'test_run.log'
    _initialized = False
    
    @classmethod
    def setup(cls):
        """Настройка системы логирования."""
        if cls._initialized:
            return
            
        # Создаем директорию для логов
        cls._log_dir.mkdir(exist_ok=True)
        
        # Настраиваем корневой логгер
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Форматтер для файла (подробный)
        file_formatter = logging.Formatter(
            '%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Форматтер для консоли (краткий)
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # Хендлер для лог-файла
        file_handler = logging.FileHandler(cls._log_file, mode='w', encoding='utf-8')
        file_handler.setFormatter(file_formatter)
        file_handler.setLevel(logging.DEBUG)
        
        # Хендлер для консоли
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(console_formatter)
        console_handler.setLevel(logging.INFO)
        
        # Очищаем все хендлеры
        root_logger.handlers.clear()
        
        # Добавляем хендлеры
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)
        
        cls._initialized = True
        root_logger.info(f"Система логирования инициализирована. Лог-файл: {cls._log_file}")

    @classmethod
    def cleanup(cls):
        """Очистка обработчиков логирования."""
        if cls._initialized:
            root_logger = logging.getLogger()
            root_logger.handlers.clear()
            cls._initialized = False


@pytest.fixture
def mock_automation():
    """Create a mock automation instance"""
    automation = MagicMock()
    automation.mouse = MagicMock()
    automation.keyboard = MagicMock()
    return automation

@pytest.fixture
def mock_element_with_current():
    """Create a mock element with current-style attributes"""
    element = MagicMock()
    # Set default attribute values from test data
    element.text = DEFAULT_ELEMENT_DATA['text']
    element.location = DEFAULT_ELEMENT_DATA['location']
    element.size = DEFAULT_ELEMENT_DATA['size']
    element.is_enabled.return_value = True
    element.is_displayed.return_value = True
    
    # Set up attributes and properties
    def get_attribute(name):
        return DEFAULT_ELEMENT_DATA['attributes'].get(name) if isinstance(DEFAULT_ELEMENT_DATA['attributes'], dict) else None
    def get_property(name):
        return DEFAULT_ELEMENT_DATA['properties'].get(name) if isinstance(DEFAULT_ELEMENT_DATA['properties'], dict) else None
    
    element.get_attribute.side_effect = get_attribute
    element.get_property.side_effect = get_property
    
    return element

@pytest.fixture
def mock_element_with_get():
    """Create a mock element with get-style methods"""
    element = MagicMock()
    # Set up method return values from alternate test data
    element.text = ALTERNATE_ELEMENT_DATA['text']
    element.location = ALTERNATE_ELEMENT_DATA['location']
    element.size = ALTERNATE_ELEMENT_DATA['size']
    element.is_enabled.return_value = True
    element.is_displayed.return_value = True
    
    # Set up attributes and properties
    def get_attribute(name):
        return ALTERNATE_ELEMENT_DATA['attributes'].get(name) if isinstance(ALTERNATE_ELEMENT_DATA['attributes'], dict) else None
    def get_property(name):
        return ALTERNATE_ELEMENT_DATA['properties'].get(name) if isinstance(ALTERNATE_ELEMENT_DATA['properties'], dict) else None
    
    element.get_attribute.side_effect = get_attribute
    element.get_property.side_effect = get_property
    
    return element

@pytest.fixture
def mock_backend(mock_element_with_current):
    """Mock backend for testing"""
    backend = MagicMock()
    backend.find_element.return_value = mock_element_with_current
    backend.find_elements.return_value = [mock_element_with_current]
    backend.get_active_window.return_value = mock_element_with_current
    backend.capture_element.return_value = np.zeros(
        (SCREENSHOT_DATA['height'], SCREENSHOT_DATA['width'], SCREENSHOT_DATA['channels']), 
        dtype=np.uint8
    )
    backend.get_window_handles.return_value = [WINDOW_DATA['handle']]
    backend.get_main_window.return_value = mock_element_with_current
    backend.wait_for_window.return_value = True
    backend.take_screenshot.return_value = "screenshot.png"
    return backend

@pytest.fixture
def ui_automation(mock_backend):
    """Create UIAutomation instance with mocked backend"""
    automation = AutomationSession(backend=mock_backend, locator=MockLocator())
    return automation

@pytest.fixture
def mock_process():
    """Create a mock process for testing"""
    process = MagicMock()
    process.pid = PROCESS_DATA['pid']
    process.name.return_value = PROCESS_DATA['name']
    process.is_running.return_value = True
    process.cpu_percent.return_value = PROCESS_DATA['cpu_percent']
    process.memory_info.return_value = MagicMock(rss=PROCESS_DATA['memory_mb'] * 1024 * 1024)
    process.terminate = MagicMock()
    process.kill = MagicMock()
    process.exe.return_value = PROCESS_DATA['executable']
    return process

@pytest.fixture
def mock_application(mock_process):
    """Create a mock application for testing"""
    app = MagicMock(spec=Application)
    app.process = mock_process
    app.path = Path(str(PROCESS_DATA['executable']))
    return app



@pytest.fixture
def mock_performance_data():
    """Create mock performance data"""
    return {
        'cpu_usage': PERFORMANCE_DATA['cpu_usage'],
        'memory_usage': PERFORMANCE_DATA['memory_usage'],
        'response_time': PERFORMANCE_DATA['response_time'],
        'frame_rate': PERFORMANCE_DATA['frame_rate'],
        'load_time': PERFORMANCE_DATA['load_time']
    }

@pytest.fixture
def performance_monitor(mock_application):
    """Create PerformanceMonitor instance"""
    monitor = PerformanceMonitor(mock_application)
    return monitor

@pytest.fixture
def temp_dir(tmp_path):
    """Create a temporary directory for test files"""
    return tmp_path

@pytest.fixture
def mock_element():
    """Create a base mock element for testing"""
    class MockElement:
        def __init__(self, properties: Optional[Dict[str, Any]] = None):
            self.properties = properties or {}
            self.clicks = 0
            self.right_clicks = 0
            self.enabled = True
            self.checked = False
            self.children = []

        def get_property(self, name: str) -> Any:
            return self.properties.get(name)

        def click(self) -> None:
            self.clicks += 1

        def right_click(self) -> None:
            self.right_clicks += 1

        def is_enabled(self) -> bool:
            return self.enabled

        def is_checked(self) -> bool:
            return self.checked

        def exists(self) -> bool:
            return True

        def find_element(self, **kwargs) -> Optional['MockElement']:
            return self.children[0] if self.children else None

        def find_elements(self, **kwargs) -> List['MockElement']:
            return self.children

        def send_keys(self, text: str) -> None:
            self.properties['text'] = text

        def select_option(self, option: str) -> None:
            self.properties['selected'] = option

        def set_value(self, value: Any) -> None:
            self.properties['value'] = value

        def pan_to(self, x: float, y: float) -> None:
            self.properties['pan_x'] = x
            self.properties['pan_y'] = y

    return MockElement


@pytest.fixture
def mock_session():
    """Create a mock automation session"""
    class MockSession:
        def __init__(self):
            self.wait_results = {}

        def wait_for_condition(self, condition, timeout: float, error_message: str) -> bool:
            return self.wait_results.get(error_message, True)

    return MockSession()


def create_mock_element(properties: Optional[Dict[str, Any]] = None) -> object:
    """Create a mock element with given properties"""
    MockElement = mock_element()
    if properties is None:
        properties = {}
    return MockElement(properties)


# Фикстуры для параллельного запуска
@pytest.fixture(scope='session')
def worker_id(request):
    """Get the worker ID when running in parallel"""
    if hasattr(request.config, 'workerinput'):
        return request.config.workerinput['workerid']
    return 'master'

@pytest.fixture(scope='session')
def worker_tmpdir(worker_id, tmp_path_factory):
    """Create a temporary directory for each worker"""
    if worker_id == 'master':
        return tmp_path_factory.mktemp('master')
    return tmp_path_factory.mktemp(f'worker_{worker_id}')

@pytest.fixture(autouse=True)
def _worker_tmp(request, worker_id, worker_tmpdir):
    """Automatically use worker-specific temp directory"""
    import tempfile
    import os
    # Use the worker_id fixture value, not the function directly
    worker_temp = tempfile.mkdtemp(prefix=f'pytest_worker_{worker_id}_')
    os.environ['PYTEST_WORKER_TEMP'] = worker_temp
    yield
    # Clean up temp directory and environment variable
    if 'PYTEST_WORKER_TEMP' in os.environ:
        try:
            if os.path.exists(worker_temp):
                import shutil
                shutil.rmtree(worker_temp)
        finally:
            del os.environ['PYTEST_WORKER_TEMP']

def pytest_xdist_auto_num_workers(config):
    """Return number of workers to use for parallel testing"""
    import multiprocessing
    # Use number of CPUs minus 1 to leave one core free for system
    return max(multiprocessing.cpu_count() - 1, 1)
