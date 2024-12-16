"""
Конфигурация и фикстуры для тестирования UI автоматизации.

Этот модуль содержит общие фикстуры и настройки для тестов, включая:
- Мок-объекты для тестирования UI элементов
- Настройку логирования
- Систему отчетности о тестах
- Конфигурацию параллельного запуска
"""

import os
import sys
import pytest
import logging
import threading
import xml.etree.ElementTree as ET
from queue import Queue, Empty
import atexit
from unittest.mock import MagicMock
import numpy as np
from types import ModuleType
from pathlib import Path
import time
import webbrowser
from typing import Any, Dict, List, Optional, Union
import psutil
from http.server import HTTPServer
from datetime import datetime
import asyncio
import aiofiles
import aiofiles.os as async_os

from pyui_automation.elements import UIElement
from pyui_automation.accessibility import AccessibilityChecker
from pyui_automation.application import Application
from pyui_automation.performance import PerformanceMonitor
from pyui_automation.core import AutomationSession
from pyui_automation.server import TestReportServer, run_server
from pyui_automation.server.server import ws_handler

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

# Глобальные переменные для управления отчетностью
_results_queue: Queue = Queue()
_writer_thread: Optional[threading.Thread] = None
_stop_writer: threading.Event = threading.Event()
_file_lock: threading.Lock = threading.Lock()
_log_file_handler: Optional[logging.FileHandler] = None
_console_handler: Optional[logging.StreamHandler] = None
_is_master = False  # Флаг мастер-процесса
_event_loop_lock = threading.Lock()  # Блокировка для event loop

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

class TestReportingSystem:
    """Система отчетности о тестах через WebSocket."""
    
    _instance = None
    _results_queue = None
    _event_loop = None
    _writer_thread = None
    _stop_event = None
    _is_master = False
    _logger = logging.getLogger('test_reporting')
    _initialized = False
    _lock = threading.Lock()

    @classmethod
    def initialize(cls, is_master=False):
        """Инициализация системы отчетности."""
        with cls._lock:
            if cls._initialized:
                cls._logger.debug("Система отчетности уже инициализирована")
                return
                
            cls._is_master = is_master
            cls._logger.info(f"Инициализация системы отчетности (master={is_master})")
            
            if cls._instance is None:
                cls._instance = cls()
                cls._results_queue = Queue()
                cls._stop_event = threading.Event()
                
                if is_master:
                    cls._logger.info("Запуск writer thread в мастер-процессе")
                    try:
                        # Инициализация event loop для WebSocket
                        cls._event_loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(cls._event_loop)
                        cls._logger.info("Event loop инициализирован успешно")
                        
                        # Запуск writer thread только после успешной инициализации event loop
                        cls._writer_thread = threading.Thread(target=cls._process_results_queue, daemon=True)
                        cls._writer_thread.start()
                        cls._logger.info("Writer thread запущен успешно")
                    except Exception as e:
                        cls._logger.error(f"Ошибка инициализации мастер-процесса: {e}", exc_info=True)
                        raise
                        
            cls._initialized = True
            cls._logger.info("Инициализация завершена успешно")

    @classmethod
    def _process_results_queue(cls):
        """Обработка очереди результатов в фоновом потоке."""
        cls._logger.info("Запущена обработка очереди результатов")
        
        while not cls._stop_event.is_set():
            try:
                # Проверяем очередь каждые 0.1 секунды
                try:
                    result = cls._results_queue.get(timeout=0.1)
                except Empty:
                    continue
                    
                if not cls._is_master:
                    cls._logger.warning("Попытка обработки результатов в не-мастер процессе")
                    continue
                    
                cls._logger.debug(f"Получен результат из очереди: {result.get('name', 'Unknown')}")
                
                # Отправляем результат через WebSocket
                if cls._event_loop and not cls._event_loop.is_closed():
                    try:
                        future = asyncio.run_coroutine_threadsafe(
                            cls.send_test_result(result),
                            cls._event_loop
                        )
                        future.result(timeout=5)  # Ждем отправки не более 5 секунд
                        cls._logger.debug(f"Результат успешно отправлен: {result.get('name', 'Unknown')}")
                    except Exception as e:
                        cls._logger.error(f"Ошибка отправки результата: {e}", exc_info=True)
                else:
                    cls._logger.error("Event loop не доступен для отправки результата")
                    
            except Exception as e:
                cls._logger.error(f"Ошибка обработки результата: {e}", exc_info=True)
                
        cls._logger.info("Обработка очереди результатов остановлена")

    @classmethod
    async def send_test_result(cls, result):
        """Отправка результата теста через WebSocket."""
        if not cls._initialized:
            cls._logger.warning("Система отчетности не инициализирована")
            return

        try:
            test_name = result.get('name', 'Unknown')
            test_status = result.get('status', 'Unknown')
            cls._logger.info(f"Начало отправки результата теста '{test_name}' (статус: {test_status}) на сервер")
            
            from pyui_automation.server.server import WebSocketHandler
            await WebSocketHandler.broadcast(json.dumps(result))
            
            cls._logger.info(f"Результат теста '{test_name}' успешно отправлен на сервер")
            cls._logger.debug(f"Детали отправленного результата: {result}")
        except Exception as e:
            cls._logger.error(f"Ошибка при отправке результата теста '{test_name}' на сервер: {e}", exc_info=True)
            raise

    @classmethod
    def stop_writer_thread(cls):
        """Остановка потока обработки результатов."""
        if not cls._initialized:
            return
            
        cls._logger.info("Остановка writer thread")
        
        if cls._stop_event:
            cls._stop_event.set()
            
            if cls._writer_thread and cls._writer_thread.is_alive():
                try:
                    cls._writer_thread.join(timeout=5)
                    cls._logger.info("Writer thread успешно остановлен")
                except Exception as e:
                    cls._logger.error(f"Ошибка при остановке writer thread: {e}", exc_info=True)
                
            if cls._event_loop and not cls._event_loop.is_closed():
                try:
                    cls._event_loop.close()
                    cls._logger.info("Event loop закрыт")
                except Exception as e:
                    cls._logger.error(f"Ошибка при закрытии event loop: {e}", exc_info=True)

class BrowserManager:
    """Управление браузером для отображения отчетов."""
    
    _browser_opened = False
    
    @classmethod
    def open_report(cls, port: int = 8000) -> None:
        """
        Открытие отчета в браузере.
        
        Args:
            port: Порт, на котором запущен сервер отчетов
        """
        if not cls._browser_opened:
            url = f'http://localhost:{port}/'
            webbrowser.open(url)
            cls._browser_opened = True

# Create a mock module for os
class MockOS(ModuleType):
    def __init__(self, name='os'):
        super().__init__(name)
        """
        Initialize the mock os module by copying all attributes
        from the real os module and adding a mock getuid.
        """
        # Copy all attributes from the real os module
        for attr in dir(os):
            if not attr.startswith('__'):
                setattr(self, attr, getattr(os, attr))
        # Add mock getuid
        self.getuid = MagicMock(return_value=1000)

# Replace os module with our mock for tests
@pytest.fixture(autouse=True)
def mock_os_module():
    real_os = sys.modules['os']
    mock_os = MockOS()
    sys.modules['os'] = mock_os
    yield
    sys.modules['os'] = real_os

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
        return DEFAULT_ELEMENT_DATA['attributes'].get(name)
    def get_property(name):
        return DEFAULT_ELEMENT_DATA['properties'].get(name)
    
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
        return ALTERNATE_ELEMENT_DATA['attributes'].get(name)
    def get_property(name):
        return ALTERNATE_ELEMENT_DATA['properties'].get(name)
    
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
        dtype=SCREENSHOT_DATA['dtype']
    )
    backend.get_window_handles.return_value = [WINDOW_DATA['handle']]
    backend.get_main_window.return_value = mock_element_with_current
    backend.wait_for_window.return_value = True
    backend.take_screenshot.return_value = "screenshot.png"
    return backend

@pytest.fixture
def ui_automation(mock_backend):
    """Create UIAutomation instance with mocked backend"""
    automation = AutomationSession()
    automation._backend = mock_backend
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
    app.path = Path(PROCESS_DATA['executable'])
    return app

@pytest.fixture
def accessibility_checker(ui_automation):
    """Create AccessibilityChecker instance"""
    return AccessibilityChecker(ui_automation)

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
        def __init__(self, properties: Dict[str, Any] = None):
            self.properties = properties or {}
            self.clicks = 0
            self.right_clicks = 0
            self.enabled = True
            self.checked = False
            self.exists = True
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
            return self.exists

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

    return MockElement()


@pytest.fixture
def mock_session():
    """Create a mock automation session"""
    class MockSession:
        def __init__(self):
            self.wait_results = {}

        def wait_for_condition(self, condition, timeout: float, error_message: str) -> bool:
            return self.wait_results.get(error_message, True)

    return MockSession()


def create_mock_element(properties: Dict[str, Any] = None) -> 'MockElement':
    """Create a mock element with given properties"""
    return mock_element()(properties)


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

# Хуки pytest
@pytest.fixture(scope="session")
def is_master(request):
    """Определяет, является ли текущий процесс мастером."""
    try:
        return not hasattr(request.config, 'workerinput')
    except Exception as e:
        logging.getLogger('test_system').error(f"Ошибка при определении мастер-процесса: {e}")
        return False

@pytest.fixture(scope='session', autouse=True)
def setup_reporting(is_master):
    """Инициализация системы отчетности."""
    try:
        TestReportingSystem.initialize(is_master=is_master)
        yield
        TestReportingSystem.stop_writer_thread()
    except Exception as e:
        logging.getLogger('test_system').error(f"Ошибка при инициализации системы отчетности: {e}")

def pytest_configure(config):
    """Configure pytest settings"""
    global _is_master
    _is_master = not hasattr(config, "workerinput")

def pytest_sessionfinish(session):
    """Called after whole test run finished."""
    if _is_master:
        TestReportingSystem.stop_writer_thread()

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Перехватываем результаты тестов для отправки через WebSocket."""
    logger = logging.getLogger('test_reporting')
    
    outcome = yield
    report = outcome.get_result()
    
    if call.when == "call":
        try:
            # Создаем результат теста
            result = {
                'name': item.name,
                'nodeid': item.nodeid,
                'outcome': report.outcome,
                'duration': report.duration,
                'timestamp': datetime.now().isoformat(),
                'longrepr': str(report.longrepr) if report.longrepr else None,
                'worker_id': getattr(item.config, "workerinput", {}).get("workerid", "master")
            }
            
            logger.debug(f"Создан результат теста: {result['name']} ({result['worker_id']})")
            
            # В воркерах только добавляем результат в очередь
            if not _is_master:
                TestReportingSystem._results_queue.put(result)
                logger.debug(f"Результат добавлен в очередь воркером: {result['worker_id']}")
                return
                
            # В мастер-процессе отправляем через WebSocket
            loop = TestReportingSystem._event_loop
            if loop is None:
                logger.error("Event loop не инициализирован в мастер-процессе")
                return
                
            try:
                if loop.is_running():
                    loop.call_soon_threadsafe(
                        lambda: asyncio.create_task(
                            TestReportingSystem.send_test_result(result)
                        )
                    )
                    logger.debug(f"Результат отправлен асинхронно: {result['name']}")
                else:
                    loop.run_until_complete(TestReportingSystem.send_test_result(result))
                    logger.debug(f"Результат отправлен синхронно: {result['name']}")
            except Exception as e:
                logger.error(f"Ошибка отправки результата: {e}", exc_info=True)
            
        except Exception as e:
            logger.error(f"Ошибка обработки результата теста: {e}", exc_info=True)

def _serve_results():
    """Запуск HTTP сервера для отдачи результатов тестов."""
    try:
        port = 8000
        host = 'localhost'
        
        # Создаем и запускаем event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        # Запускаем сервер асинхронно
        loop.run_until_complete(run_server(host, port))
        
    except Exception as e:
        logging.error(f"Ошибка запуска сервера отчетов: {e}", exc_info=True)
    finally:
        loop.close()
