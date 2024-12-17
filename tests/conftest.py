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
from queue import Queue, Empty, Full
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
import uuid
import json

# Добавляем корневую директорию в PYTHONPATH
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pyui_automation.elements import UIElement
from pyui_automation.accessibility import AccessibilityChecker
from pyui_automation.application import Application
from pyui_automation.performance import PerformanceMonitor
from pyui_automation.core import AutomationSession
from pyui_automation.server import TestReportServer, run_server
from pyui_automation.server.server import ws_handler

from pyui_automation.utils.types import (
    TestStatus, MessageType, TestResult, TestSuite,
    WebSocketMessage, MAX_QUEUE_SIZE, CLEANUP_INTERVAL,
    MAX_RESULT_AGE, MAX_RETRY_ATTEMPTS, RETRY_DELAY,
    ACK_TIMEOUT, PING_INTERVAL
)

from pyui_automation.utils.storage import TestResultStorage
from pyui_automation.utils.notifications import NotificationManager, NotificationConfig

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
    
    def __init__(self, notification_config: Optional[NotificationConfig] = None):
        self.results_queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
        self.test_suites: Dict[str, TestSuite] = {}
        self.current_suite: Optional[TestSuite] = None
        self.subscribers = set()
        self._processing_task = None
        self._cleanup_task = None
        self._ping_task = None
        self._retry_queue = asyncio.Queue()
        self.logger = logging.getLogger(__name__)
        self.metrics = {
            'processed_results': 0,
            'failed_sends': 0,
            'retried_sends': 0,
            'active_subscribers': 0,
            'stored_results': 0,
            'notifications_sent': 0,
            'notification_errors': 0
        }
        self.storage = TestResultStorage()
        self.notification_manager = (NotificationManager(notification_config) 
                                   if notification_config else None)

    async def start(self):
        """Запуск системы обработки результатов."""
        await self.storage.initialize()
        
        if self.notification_manager:
            await self.notification_manager.start()
        
        # Загружаем последние результаты из хранилища
        recent_suites = await self.storage.get_recent_suites()
        for suite in recent_suites:
            self.test_suites[suite.id] = suite
            suite.results = await self.storage.get_suite_results(suite.id)
        
        self._processing_task = asyncio.create_task(self._process_results_queue())
        self._cleanup_task = asyncio.create_task(self._cleanup_old_results())
        self._ping_task = asyncio.create_task(self._ping_subscribers())
        self.logger.info("Система обработки результатов запущена")

    async def stop(self):
        """Остановка системы обработки результатов."""
        tasks = [
            self._processing_task,
            self._cleanup_task,
            self._ping_task
        ]
        for task in tasks:
            if task:
                task.cancel()
                try:
                    await task
                except asyncio.CancelledError:
                    pass
        
        if self.notification_manager:
            await self.notification_manager.stop()
        
        # Закрываем все WebSocket соединения
        for websocket in self.subscribers.copy():
            try:
                await websocket.close()
            except Exception as e:
                self.logger.error(f"Ошибка закрытия WebSocket: {e}")
                
        self.logger.info("Система обработки результатов остановлена")

    async def end_suite(self, suite_id: str) -> bool:
        """
        Завершение набора тестов.
        
        Args:
            suite_id: ID набора тестов
            
        Returns:
            bool: True если набор тестов успешно завершен
        """
        suite = self.test_suites.get(suite_id)
        if not suite:
            self.logger.error(f"Набор тестов {suite_id} не найден")
            return False
            
        suite.end_time = datetime.now()
        suite.duration = (suite.end_time - suite.start_time).total_seconds()
        
        # Сохраняем результаты
        try:
            await self.storage.save_suite(suite)
            await self.storage.save_results(suite_id, suite.results)
            self.metrics['stored_results'] += len(suite.results)
            
            # Отправляем уведомление
            if self.notification_manager:
                try:
                    await self.notification_manager.notify_suite_completion(suite)
                    self.metrics['notifications_sent'] += 1
                except Exception as e:
                    self.logger.error(f"Ошибка отправки уведомления: {e}")
                    self.metrics['notification_errors'] += 1
            
            return True
        except Exception as e:
            self.logger.error(f"Ошибка сохранения результатов: {e}")
            return False

    async def start_suite(self, name: str) -> str:
        """
        Начало нового набора тестов.
        
        Args:
            name: Имя набора тестов
            
        Returns:
            ID набора тестов
        """
        suite = TestSuite(id=str(uuid.uuid4()), name=name)
        self.test_suites[suite.id] = suite
        self.current_suite = suite
        
        # Сохраняем в хранилище
        await self.storage.save_suite(suite)
        
        await self._broadcast_message(MessageType.TEST_RESULT, {
            'type': 'suite_started',
            'suite': asdict(suite)
        })
        return suite.id

    async def add_result(self, result_dict: dict):
        """
        Добавление результата теста в очередь.
        
        Args:
            result_dict: Словарь с результатами теста
        """
        try:
            # Преобразуем словарь в TestResult
            result = TestResult(
                id=result_dict.get('id', str(uuid.uuid4())),
                name=result_dict['name'],
                status=TestStatus[result_dict['status'].upper()],
                duration=result_dict.get('duration', 0.0),
                error_message=result_dict.get('error_message'),
                traceback=result_dict.get('traceback'),
                metadata=result_dict.get('metadata', {})
            )
            
            # Добавляем результат в текущий набор тестов
            if self.current_suite:
                self.current_suite.results.append(result)
                # Сохраняем в хранилище
                await self.storage.save_result(result, self.current_suite.id)
                self.metrics['stored_results'] += 1
            
            await self.results_queue.put(result)
            
        except Exception as e:
            self.logger.error(f"Ошибка добавления результата: {e}", exc_info=True)

    async def subscribe(self, websocket):
        """
        Подписка на обновления результатов.
        
        Args:
            websocket: WebSocket соединение
        """
        self.subscribers.add(websocket)
        self.metrics['active_subscribers'] = len(self.subscribers)
        
        # Отправляем текущие результаты
        if self.test_suites:
            await websocket.send(json.dumps({
                'type': MessageType.INITIAL_RESULTS.value,
                'suites': [asdict(suite) for suite in self.test_suites.values()]
            }))

    async def unsubscribe(self, websocket):
        """
        Отписка от обновлений результатов.
        
        Args:
            websocket: WebSocket соединение
        """
        self.subscribers.remove(websocket)
        self.metrics['active_subscribers'] = len(self.subscribers)
        try:
            await websocket.close()
        except Exception as e:
            self.logger.error(f"Ошибка закрытия WebSocket: {e}")

    async def _process_results_queue(self):
        """Обработка очереди результатов."""
        while True:
            try:
                result = await self.results_queue.get()
                
                message = WebSocketMessage(
                    type=MessageType.TEST_RESULT,
                    data={'result': asdict(result)}
                )
                
                await self._broadcast_message_with_retry(message)
                self.metrics['processed_results'] += 1
                self.results_queue.task_done()
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Ошибка обработки результата: {e}", exc_info=True)

    async def _broadcast_message_with_retry(self, message: WebSocketMessage, attempts: int = 0):
        """
        Отправка сообщения всем подписчикам с повторными попытками.
        
        Args:
            message: Сообщение для отправки
            attempts: Текущее количество попыток
        """
        failed_subscribers = []
        
        for websocket in self.subscribers.copy():
            try:
                await websocket.send(json.dumps({
                    'type': message.type.value,
                    'id': message.id,
                    'data': message.data,
                    'timestamp': message.timestamp.isoformat()
                }))
            except Exception as e:
                self.logger.error(f"Ошибка отправки сообщения: {e}")
                failed_subscribers.append(websocket)
                self.metrics['failed_sends'] += 1

        # Отписываем неактивных подписчиков
        for websocket in failed_subscribers:
            await self.unsubscribe(websocket)

        # Повторяем попытку для неотправленных сообщений
        if failed_subscribers and attempts < MAX_RETRY_ATTEMPTS:
            self.metrics['retried_sends'] += 1
            await asyncio.sleep(RETRY_DELAY)
            await self._broadcast_message_with_retry(message, attempts + 1)

    async def _broadcast_message(self, message_type: MessageType, data: dict):
        """
        Отправка сообщения всем подписчикам.
        
        Args:
            message_type: Тип сообщения
            data: Данные сообщения
        """
        message = WebSocketMessage(type=message_type, data=data)
        await self._broadcast_message_with_retry(message)

    async def _cleanup_old_results(self):
        """Очистка старых результатов."""
        while True:
            try:
                # Очищаем кэш
                now = datetime.now()
                old_suites = [
                    suite_id for suite_id, suite in self.test_suites.items()
                    if (now - suite.start_time).total_seconds() > MAX_RESULT_AGE
                ]
                
                for suite_id in old_suites:
                    del self.test_suites[suite_id]
                
                if old_suites:
                    self.logger.info(f"Удалено {len(old_suites)} старых наборов тестов из кэша")
                
                # Очищаем хранилище
                await self.storage.cleanup_old_data()
                
                await asyncio.sleep(CLEANUP_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Ошибка очистки старых результатов: {e}", exc_info=True)

    async def _ping_subscribers(self):
        """Отправка ping-сообщений подписчикам."""
        while True:
            try:
                if self.subscribers:
                    await self._broadcast_message(
                        MessageType.PING,
                        {'timestamp': datetime.now().isoformat()}
                    )
                await asyncio.sleep(PING_INTERVAL)
                
            except asyncio.CancelledError:
                break
            except Exception as e:
                self.logger.error(f"Ошибка отправки ping: {e}", exc_info=True)

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
    worker_id = getattr(request.config, 'workerinput', {}).get('workerid', None)
    return worker_id is None

@pytest.fixture(scope='session')
def setup_reporting(request, is_master):
    """Инициализация системы отчетности."""
    global _is_master
    _is_master = is_master
    
    if is_master:
        # Настраиваем конфигурацию уведомлений
        notification_config = NotificationConfig(
            email_enabled=os.getenv('TEST_EMAIL_ENABLED', 'false').lower() == 'true',
            email_from=os.getenv('TEST_EMAIL_FROM'),
            email_to=os.getenv('TEST_EMAIL_TO', '').split(','),
            email_server=os.getenv('TEST_EMAIL_SERVER', 'smtp.gmail.com'),
            email_port=int(os.getenv('TEST_EMAIL_PORT', '587')),
            email_username=os.getenv('TEST_EMAIL_USERNAME'),
            email_password=os.getenv('TEST_EMAIL_PASSWORD'),
            
            slack_enabled=os.getenv('TEST_SLACK_ENABLED', 'false').lower() == 'true',
            slack_webhook_url=os.getenv('TEST_SLACK_WEBHOOK_URL'),
            
            telegram_enabled=os.getenv('TEST_TELEGRAM_ENABLED', 'false').lower() == 'true',
            telegram_bot_token=os.getenv('TEST_TELEGRAM_BOT_TOKEN'),
            telegram_chat_ids=os.getenv('TEST_TELEGRAM_CHAT_IDS', '').split(','),
            
            notification_threshold=float(os.getenv('TEST_NOTIFICATION_THRESHOLD', '80.0'))
        )
        
        # Создаем экземпляр системы отчетности
        reporting_system = TestReportingSystem(notification_config)
        
        # Запускаем сервер в отдельном потоке
        def run_server():
            asyncio.run(run_server('localhost', 8000))
            
        server_thread = threading.Thread(target=run_server)
        server_thread.daemon = True
        server_thread.start()
        
        # Регистрируем функцию очистки
        def cleanup():
            global _is_master
            _is_master = False
            LoggingSystem.cleanup()
            
        request.addfinalizer(cleanup)
        
        return reporting_system
    return None

@pytest.fixture(autouse=True)
def test_reporting_system(setup_reporting):
    """Фикстура для доступа к системе отчетности."""
    return setup_reporting

def pytest_sessionfinish(session):
    """Called after whole test run finished."""
    reporting = session.config.pluginmanager.get_plugin("setup_reporting")
    if reporting:
        reporting.stop()

def pytest_configure(config):
    """Configure pytest settings"""
    global _is_master
    _is_master = not hasattr(config, "workerinput")

@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Перехватываем результаты тестов для отправки через WebSocket."""
    logger = logging.getLogger('test_reporting')
    
    outcome = yield
    report = outcome.get_result()
    
    if call.when == "call":
        try:
            # Создаем результат теста
            worker_id = getattr(item.config, "workerinput", {}).get("workerid", "master")
            result = {
                'name': item.name,
                'nodeid': item.nodeid,
                'outcome': report.outcome,
                'duration': report.duration,
                'timestamp': datetime.now().isoformat(),
                'longrepr': str(report.longrepr) if report.longrepr else None,
                'worker_id': worker_id
            }
            
            logger.debug(f"Создан результат теста: {result['name']} ({worker_id})")
            
            # В воркере просто добавляем результат в очередь
            if worker_id != "master":
                try:
                    test_reporting_system.add_result(result)
                    logger.debug(f"Результат добавлен в очередь: {result['name']} ({worker_id})")
                except Full:
                    logger.error("Очередь результатов переполнена")
                    test_reporting_system._metrics['queue_overflow_count'] += 1
            else:
                # В мастер-процессе сразу отправляем результат
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        test_reporting_system.add_result(result),
                        test_reporting_system._event_loop
                    )
                    future.result(timeout=5)
                    logger.debug(f"Результат отправлен напрямую: {result['name']} (master)")
                except Exception as e:
                    logger.error(f"Ошибка отправки результата в мастер-процессе: {e}", exc_info=True)
                    # Добавляем в очередь при ошибке отправки
                    try:
                        test_reporting_system.add_result(result)
                        logger.debug(f"Результат добавлен в очередь после ошибки: {result['name']} (master)")
                    except Full:
                        logger.error("Очередь результатов переполнена")
                        test_reporting_system._metrics['queue_overflow_count'] += 1
            
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
