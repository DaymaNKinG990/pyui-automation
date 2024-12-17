import os
import sys
import json
import time
import asyncio
import logging
import threading
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler, ThreadingHTTPServer, BaseHTTPRequestHandler
from queue import Queue, Empty
from threading import Thread, Event
from dataclasses import dataclass, field
from typing import Dict, Optional
from collections import deque
from statistics import mean
import uuid
import websockets
from pyui_automation.utils.metrics import metrics
from pyui_automation.utils.logging_config import setup_logging
import base64
import hashlib

# Настройка логирования
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

# Очищаем все существующие обработчики
logging.getLogger().handlers.clear()

# Настраиваем корневой логгер
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'server.log', mode='a', encoding='utf-8'),
        logging.StreamHandler(sys.stdout)
    ]
)

# Получаем логгер для текущего модуля
logger = logging.getLogger(__name__)

# Проверяем существование и права доступа к файлу логов
log_file = log_dir / 'server.log'
try:
    if not log_file.exists():
        log_file.touch()
    if not os.access(log_file, os.W_OK):
        logger.error(f"Нет прав на запись в файл логов: {log_file}")
        sys.exit(1)
except Exception as e:
    logger.error(f"Ошибка при работе с файлом логов: {e}")
    sys.exit(1)

logger.info("Логирование инициализировано успешно")

"""
Модуль реализации HTTP сервера для отображения результатов тестов.

Этот модуль предоставляет HTTP сервер для отображения результатов тестов pytest в веб-интерфейсе.
Он поддерживает кэширование результатов, CORS, и отдачу статических файлов.
"""

# Константы для настройки сервера
MAX_QUEUE_SIZE = 10000  # Максимальный размер очереди
RECONNECT_TIMEOUT = 5  # Таймаут для переподключения в секундах
SOCKET_TIMEOUT = 30  # Таймаут для сокет-операций в секундах
MAX_RETRIES = 3  # Максимальное количество попыток переподключения

@dataclass
class ConnectionMetrics:
    """Метрики соединения."""
    messages_sent: int = 0
    messages_received: int = 0
    errors: int = 0
    latency_history: deque = field(default_factory=lambda: deque(maxlen=100))
    last_activity: float = 0.0
    reconnect_attempts: int = 0
    
    @property
    def average_latency(self) -> float:
        """Средняя задержка за последние 100 сообщений."""
        return mean(self.latency_history) if self.latency_history else 0.0

class PerformanceMonitor:
    """Монитор производительности WebSocket сервера."""
    
    def __init__(self):
        self._metrics: Dict[int, ConnectionMetrics] = {}
        self._global_metrics = ConnectionMetrics()
        self._start_time = time.time()
        self._logger = logging.getLogger('performance')
        
    def register_connection(self, connection_id: int) -> None:
        """Регистрация нового соединения."""
        self._metrics[connection_id] = ConnectionMetrics()
        self._logger.info(f"Зарегистрировано новое соединение {connection_id}")
        
    def unregister_connection(self, connection_id: int) -> None:
        """Удаление соединения из мониторинга."""
        if connection_id in self._metrics:
            metrics = self._metrics.pop(connection_id)
            self._logger.info(
                f"Соединение {connection_id} закрыто. "
                f"Отправлено: {metrics.messages_sent}, "
                f"Получено: {metrics.messages_received}, "
                f"Ошибок: {metrics.errors}, "
                f"Средняя задержка: {metrics.average_latency:.2f}ms"
            )
            
    def record_message_sent(self, connection_id: int, size: int) -> None:
        """Запись метрики отправленного сообщения."""
        if connection_id in self._metrics:
            self._metrics[connection_id].messages_sent += 1
            self._metrics[connection_id].last_activity = time.time()
            self._global_metrics.messages_sent += 1
            
    def record_message_received(self, connection_id: int, size: int) -> None:
        """Запись метрики полученного сообщения."""
        if connection_id in self._metrics:
            self._metrics[connection_id].messages_received += 1
            self._metrics[connection_id].last_activity = time.time()
            self._global_metrics.messages_received += 1
            
    def record_error(self, connection_id: int) -> None:
        """Запись ошибки соединения."""
        if connection_id in self._metrics:
            self._metrics[connection_id].errors += 1
            self._global_metrics.errors += 1
            
    def record_latency(self, connection_id: int, latency: float) -> None:
        """Запись задержки сообщения."""
        if connection_id in self._metrics:
            self._metrics[connection_id].latency_history.append(latency)
            self._global_metrics.latency_history.append(latency)
            
    def record_reconnect(self, connection_id: int) -> None:
        """Запись попытки переподключения."""
        if connection_id in self._metrics:
            self._metrics[connection_id].reconnect_attempts += 1
            
    def get_connection_stats(self, connection_id: int) -> Optional[Dict]:
        """Получение статистики по соединению."""
        if connection_id not in self._metrics:
            return None
            
        metrics = self._metrics[connection_id]
        return {
            'messages_sent': metrics.messages_sent,
            'messages_received': metrics.messages_received,
            'errors': metrics.errors,
            'average_latency': metrics.average_latency,
            'last_activity': metrics.last_activity,
            'reconnect_attempts': metrics.reconnect_attempts
        }
        
    def get_global_stats(self) -> Dict:
        """Получение глобальной статистики."""
        uptime = time.time() - self._start_time
        active_connections = len(self._metrics)
        
        return {
            'uptime': uptime,
            'active_connections': active_connections,
            'total_messages_sent': self._global_metrics.messages_sent,
            'total_messages_received': self._global_metrics.messages_received,
            'total_errors': self._global_metrics.errors,
            'average_latency': self._global_metrics.average_latency
        }
        
    def log_stats(self) -> None:
        """Логирование текущей статистики."""
        stats = self.get_global_stats()
        self._logger.info(
            f"Статистика сервера:\n"
            f"Время работы: {stats['uptime']:.2f}s\n"
            f"Активных соединений: {stats['active_connections']}\n"
            f"Всего отправлено: {stats['total_messages_sent']}\n"
            f"Всего получено: {stats['total_messages_received']}\n"
            f"Всего ошибок: {stats['total_errors']}\n"
            f"Средняя задержка: {stats['average_latency']:.2f}ms"
        )

# Создаем глобальный монитор производительности
performance_monitor = PerformanceMonitor()

class WebSocketProtocol:
    """Протокол для обработки WebSocket соединений."""
    
    def __init__(self, handler):
        self.handler = handler
        self.transport = None
        self.buffer = bytearray()
        self.header_parsed = False
        self.frame_length = 0
        self.mask = None
        self._logger = logging.getLogger('websocket')
        self.connection_id = id(self)
        self.last_activity = time.time()
        self.retry_count = 0
        self.is_connected = False
        self._message_timestamps = {}

    def connection_made(self, transport):
        """Установка соединения."""
        self.transport = transport
        self.is_connected = True
        self.last_activity = time.time()
        self._logger.info(f"Соединение установлено (id: {self.connection_id})")
        performance_monitor.register_connection(self.connection_id)

    def connection_lost(self, exc):
        """Потеря соединения."""
        self.is_connected = False
        self._logger.info(f"Соединение потеряно (id: {self.connection_id})")
        if exc:
            self._logger.error(f"Причина: {str(exc)}")
            performance_monitor.record_error(self.connection_id)
        self.handler.unregister(self)
        performance_monitor.unregister_connection(self.connection_id)

    def send_message(self, message):
        """Отправка сообщения клиенту."""
        try:
            if not self.is_connected:
                self._logger.warning("Попытка отправить сообщение через закрытое соединение")
                return False

            if isinstance(message, dict):
                message = json.dumps(message)
            if isinstance(message, str):
                message = message.encode('utf-8')

            # Формируем WebSocket фрейм
            frame = bytearray()
            frame.append(0x81)  # FIN + Opcode для текстового сообщения

            # Длина сообщения
            length = len(message)
            if length <= 125:
                frame.append(length)
            elif length <= 65535:
                frame.append(126)
                frame.extend(length.to_bytes(2, 'big'))
            else:
                frame.append(127)
                frame.extend(length.to_bytes(8, 'big'))

            # Добавляем сообщение
            frame.extend(message)

            # Отправляем фрейм
            self.transport.wfile.write(frame)
            self.transport.wfile.flush()

            self.last_activity = time.time()
            performance_monitor.record_message_sent(self.connection_id, len(message))
            return True

        except Exception as e:
            self._logger.error(f"Ошибка при отправке сообщения: {str(e)}", exc_info=True)
            performance_monitor.record_error(self.connection_id)
            return False

    def data_received(self, data):
        """Получение данных."""
        try:
            self.buffer.extend(data)
            self.last_activity = time.time()
            self._process_buffer()
        except Exception as e:
            self._logger.error(f"Ошибка при получении данных: {str(e)}", exc_info=True)
            performance_monitor.record_error(self.connection_id)

    def _process_buffer(self):
        """Обработка буфера данных."""
        while len(self.buffer) >= 2:
            if not self.header_parsed:
                # Разбор заголовка фрейма
                header1, header2 = self.buffer[0], self.buffer[1]
                fin = (header1 & 0x80) != 0
                opcode = header1 & 0x0F
                masked = (header2 & 0x80) != 0
                payload_length = header2 & 0x7F

                if opcode == 0x8:  # Close frame
                    self.connection_lost(None)
                    return

                header_length = 2
                if payload_length == 126:
                    if len(self.buffer) < 4:
                        return
                    payload_length = int.from_bytes(self.buffer[2:4], 'big')
                    header_length = 4
                elif payload_length == 127:
                    if len(self.buffer) < 10:
                        return
                    payload_length = int.from_bytes(self.buffer[2:10], 'big')
                    header_length = 10

                if masked:
                    if len(self.buffer) < header_length + 4:
                        return
                    self.mask = self.buffer[header_length:header_length+4]
                    header_length += 4

                self.frame_length = header_length + payload_length
                self.header_parsed = True

            if len(self.buffer) < self.frame_length:
                return

            # Извлекаем и обрабатываем сообщение
            payload = self.buffer[header_length:self.frame_length]
            if self.mask:
                payload = bytearray(b ^ m for b, m in zip(payload, self.mask * (len(payload) // 4 + 1)))

            message = payload.decode('utf-8')
            self._handle_message(message)

            # Очищаем буфер
            self.buffer = self.buffer[self.frame_length:]
            self.header_parsed = False
            self.frame_length = 0
            self.mask = None

    def _handle_message(self, message):
        """Обработка полученного сообщения."""
        try:
            data = json.loads(message)
            performance_monitor.record_message_received(self.connection_id, len(message))
            
            if isinstance(data, dict):
                if data.get('type') == 'ping':
                    self.send_message({'type': 'pong'})
                elif data.get('type') == 'ack':
                    self.handle_message_ack(data.get('message_id'))
                else:
                    self.handler.broadcast(data)
        except json.JSONDecodeError:
            self._logger.error("Получено некорректное JSON сообщение")
            performance_monitor.record_error(self.connection_id)
        except Exception as e:
            self._logger.error(f"Ошибка при обработке сообщения: {str(e)}", exc_info=True)
            performance_monitor.record_error(self.connection_id)

class WebSocketHandler:
    """Обработчик WebSocket соединений."""
    
    def __init__(self):
        self.connections = set()
        self.lock = threading.Lock()
        self._connected = False
        self._connection_url = None
        self.loop = None
        self._logger = logging.getLogger('websocket')
        self.message_queue = asyncio.Queue(maxsize=MAX_QUEUE_SIZE)
        
    async def start(self, reporting_system):
        """Запуск обработчика."""
        self.test_reporting_system = reporting_system
        self.loop = asyncio.get_event_loop()
        asyncio.create_task(self._process_queue())
        
    async def stop(self):
        """Остановка обработчика."""
        for conn in list(self.connections):
            await self.unregister(conn)
            
    async def register(self, connection):
        """Регистрация нового соединения."""
        try:
            async with self.lock:
                self.connections.add(connection)
                self._logger.info(f"Зарегистрировано новое соединение. Всего соединений: {len(self.connections)}")
        except Exception as e:
            self._logger.error(f"Ошибка при регистрации соединения: {e}", exc_info=True)
            
    async def unregister(self, connection):
        """Удаление соединения."""
        try:
            async with self.lock:
                self.connections.discard(connection)
                self._logger.info(f"Соединение удалено. Всего соединений: {len(self.connections)}")
        except Exception as e:
            self._logger.error(f"Ошибка при удалении соединения: {e}", exc_info=True)
    
    async def broadcast(self, message):
        """Отправка сообщения всем подключенным клиентам."""
        self._logger.debug(f"Начало широковещательной рассылки сообщения всем клиентам")
        if not self.connections:
            self._logger.warning("Нет подключенных клиентов для отправки сообщения")
            return
            
        try:
            await self.message_queue.put(message)
        except Exception as e:
            self._logger.error(f"Ошибка при широковещательной рассылке: {e}", exc_info=True)
            raise
    
    async def send_test_update(self, test_data: dict):
        """Отправка обновления о результате теста."""
        try:
            self._logger.debug(f"Подготовка к отправке результата теста через WebSocket: {test_data.get('name', 'Unknown')}")
            message = {
                'type': 'test_update',
                'data': test_data
            }
            await self.broadcast(json.dumps(message))
            self._logger.info(f"Результат теста успешно отправлен через WebSocket: {test_data.get('name', 'Unknown')}")
        except Exception as e:
            self._logger.error(f"Ошибка отправки через WebSocket: {e}", exc_info=True)
            raise
    
    async def send_suite_complete(self, summary: dict):
        """Отправка информации о завершении набора тестов."""
        message = {
            'type': 'suite_complete',
            'data': summary
        }
        await self.broadcast(message)
    
    async def _process_queue(self):
        """Обработка очереди сообщений."""
        while True:
            try:
                message = await self.message_queue.get()
                if self.message_queue.qsize() > MAX_QUEUE_SIZE * 0.8:
                    self._logger.warning(f"Очередь сообщений заполнена на {self.message_queue.qsize()}/{MAX_QUEUE_SIZE}")
                
                await self._broadcast_message(message)
                self.message_queue.task_done()
            except asyncio.CancelledError:
                break
            except Exception as e:
                self._logger.error(f"Ошибка при обработке очереди сообщений: {e}", exc_info=True)
                
    async def _broadcast_message(self, message):
        """Рассылка сообщения всем подключенным клиентам."""
        disconnected = set()
        
        for connection in self.connections:
            try:
                if not connection.is_connected:
                    disconnected.add(connection)
                    continue
                    
                connection.send_message(message)
            except Exception as e:
                self._logger.error(f"Ошибка при отправке сообщения клиенту {id(connection)}: {e}", exc_info=True)
                disconnected.add(connection)
                
        # Удаляем отключенные соединения
        if disconnected:
            async with self.lock:
                self.connections -= disconnected
                
# Глобальный экземпляр WebSocketHandler
ws_handler = WebSocketHandler()

# Определяем пути к директориям
CURRENT_DIR = Path(__file__).resolve().parent
TEMPLATES_DIR = CURRENT_DIR / 'templates'
STATIC_DIR = CURRENT_DIR / 'static'
RESULTS_DIR = CURRENT_DIR.parent / 'results'

# Создаем директории, если они не существуют
TEMPLATES_DIR.mkdir(exist_ok=True)
RESULTS_DIR.mkdir(exist_ok=True)

logger.info(f"Текущая директория: {CURRENT_DIR}")
logger.info(f"Директория шаблонов: {TEMPLATES_DIR}")
logger.info(f"Директория статических файлов: {STATIC_DIR}")
logger.info(f"Директория результатов: {RESULTS_DIR}")

class TestReportServer(BaseHTTPRequestHandler):
    """HTTP сервер для отображения результатов тестов."""
    
    def __init__(self, request, client_address, server):
        """Инициализация сервера."""
        self.results_dir = RESULTS_DIR
        self.template_dir = TEMPLATES_DIR
        self.static_dir = STATIC_DIR
        self.cache = {}
        super().__init__(request, client_address, server)

    def do_GET(self):
        """Обработка GET запросов."""
        try:
            # Получаем информацию о клиенте
            client_address = self.client_address[0]
            user_agent = self.headers.get('User-Agent', 'Unknown')
            referer = self.headers.get('Referer', 'Direct access')
            
            logger.info(f"Получен GET запрос: {self.path}")
            logger.info(f"Клиент: {client_address}")
            logger.info(f"User-Agent: {user_agent}")
            logger.info(f"Referer: {referer}")
            
            # Обработка корневого пути
            if self.path == '/':
                logger.info("Обработка корневого пути")
                self._serve_report()
                return
                
            # Обработка метрик
            if self.path == '/metrics':
                logger.info("Обработка запроса метрик")
                self._serve_metrics()
                return
                
            # Обработка WebSocket
            if self.path == '/ws':
                logger.info("Обработка WebSocket соединения")
                self._handle_websocket()
                return
                
            # Обработка манифеста
            if self.path == '/manifest.json':
                logger.info("Обработка запроса манифеста")
                self._serve_manifest()
                return
                
            # Обработка статических файлов
            if self.path.startswith('/static/'):
                logger.info(f"Обработка статического файла: {self.path}")
                file_path = Path(self.path)
                self._serve_static_file(file_path)
                return
                
            # Если путь не найден
            logger.warning(f"Путь не найден: {self.path}")
            self.send_error(404)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке GET запроса: {str(e)}", exc_info=True)
            self.send_error(500)

    def _serve_report(self):
        """Отдача основного шаблона."""
        try:
            logger.info("Запрошен основной шаблон")
            template_path = self.template_dir / 'report.html'
            logger.info(f"Путь к шаблону: {template_path}")
            logger.info(f"Существование шаблона: {template_path.exists()}")
            
            if not template_path.exists():
                logger.error("Шаблон не найден")
                self.send_error(404, "Template not found")
                return
                
            logger.info("Читаем содержимое шаблона")
            try:
                with open(template_path, 'rb') as f:
                    content = f.read()
                logger.info(f"Размер шаблона: {len(content)} байт")
            except Exception as e:
                logger.error(f"Ошибка при чтении шаблона: {str(e)}", exc_info=True)
                self.send_error(500)
                return
                
            logger.info("Отправляем заголовки")
            try:
                self.send_response(200)
                self.send_header('Content-Type', 'text/html; charset=utf-8')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                logger.info("Заголовки успешно отправлены")
            except Exception as e:
                logger.error(f"Ошибка при отправке заголовков: {str(e)}", exc_info=True)
                self.send_error(500)
                return
            
            logger.info("Отправляем содержимое")
            try:
                self.wfile.write(content)
                logger.info("Шаблон успешно отправлен")
            except Exception as e:
                logger.error(f"Ошибка при отправке содержимого: {str(e)}", exc_info=True)
                raise
            
        except Exception as e:
            logger.error(f"Общая ошибка при отдаче шаблона: {str(e)}", exc_info=True)
            self.send_error(500)

    def _serve_static_file(self, file_path):
        """Отдача статического файла."""
        try:
            logger.info(f"Начало обработки статического файла: {file_path}")
            logger.info(f"Текущая директория: {os.getcwd()}")
            logger.info(f"Директория static_dir: {STATIC_DIR}")
            
            # Получаем путь относительно /static/
            relative_path = str(file_path).replace('\\', '/')
            if relative_path.startswith('/'):
                relative_path = relative_path[1:]  # Убираем начальный слеш
            if relative_path.startswith('static/'):
                relative_path = relative_path[7:]  # Убираем 'static/'
            
            # Преобразуем путь в абсолютный
            abs_path = (STATIC_DIR / relative_path).resolve()
            
            logger.info(f"Относительный путь: {relative_path}")
            logger.info(f"Запрошен статический файл: {abs_path}")
            logger.info(f"Существование файла: {abs_path.exists()}")
            logger.info(f"Абсолютный путь: {abs_path.absolute()}")
            
            if not abs_path.exists():
                logger.error(f"Файл не найден: {abs_path}")
                self.send_error(404)
                return

            # Проверяем, что файл находится в разрешенной директории
            try:
                abs_path.relative_to(STATIC_DIR)
            except ValueError:
                logger.error(f"Попытка доступа к файлу вне разрешенной директории: {abs_path}")
                logger.error(f"Разрешенная директория: {STATIC_DIR}")
                self.send_error(403)
                return

            # Получаем MIME тип файла
            content_type = self._get_content_type(abs_path)
            logger.info(f"MIME тип файла: {content_type}")

            # Читаем файл
            try:
                with open(abs_path, 'rb') as f:
                    content = f.read()
                logger.info(f"Файл успешно прочитан, размер: {len(content)} байт")
            except Exception as e:
                logger.error(f"Ошибка при чтении файла: {str(e)}", exc_info=True)
                self.send_error(500)
                return

            # Отправляем заголовки
            try:
                self.send_response(200)
                self.send_header('Content-Type', content_type)
                self.send_header('Content-Length', str(len(content)))
                self.send_header('Cache-Control', 'public, max-age=31536000')  # Кэширование на 1 год
                self.end_headers()
                logger.info("Заголовки успешно отправлены")
            except Exception as e:
                logger.error(f"Ошибка при отправке заголовков: {str(e)}", exc_info=True)
                self.send_error(500)
                return

            # Отправляем содержимое
            try:
                self.wfile.write(content)
                logger.info("Содержимое файла успешно отправлено")
            except Exception as e:
                logger.error(f"Ошибка при отправке содержимого: {str(e)}", exc_info=True)
                raise

        except Exception as e:
            logger.error(f"Общая ошибка при отдаче статического файла: {str(e)}", exc_info=True)
            self.send_error(500)

    def _serve_metrics(self):
        """Отдача метрик в формате JSON."""
        try:
            metrics_data = {
                'performance': performance_monitor.get_global_stats(),
                'websocket': {
                    'connections': len(ws_handler.connections),
                    'queue_size': ws_handler.message_queue.qsize()
                }
            }
            
            content = json.dumps(metrics_data).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)
            
        except Exception as e:
            logger.error(f"Ошибка при отдаче метрик: {e}", exc_info=True)
            self.send_error(500)

    def _serve_manifest(self):
        """Отдача манифеста."""
        try:
            manifest = {
                "name": "Test Results Dashboard",
                "short_name": "Tests",
                "description": "Dashboard for viewing test results",
                "start_url": "/",
                "display": "standalone",
                "background_color": "#ffffff",
                "theme_color": "#2196F3",
                "icons": [
                    {
                        "src": "static/icons/favicon-32x32.png",
                        "sizes": "32x32",
                        "type": "image/png",
                        "purpose": "any"
                    }
                ]
            }
            
            content = json.dumps(manifest, indent=2).encode('utf-8')
            
            self.send_response(200)
            self.send_header('Content-Type', 'application/manifest+json')
            self.send_header('Content-Length', str(len(content)))
            self.send_header('Cache-Control', 'public, max-age=86400')  # кэшировать на 24 часа
            self.send_header('Access-Control-Allow-Origin', '*')
            self.end_headers()
            
            logger.debug(f"Отправка манифеста: {manifest}")
            self.wfile.write(content)
            
        except Exception as e:
            logger.error(f"Ошибка при отдаче манифеста: {str(e)}", exc_info=True)
            self.send_error(500)

    def _get_content_type(self, path):
        """Определение MIME типа файла."""
        mime_types = {
            '.html': 'text/html',
            '.css': 'text/css',
            '.js': 'application/javascript',
            '.json': 'application/json',
            '.png': 'image/png',
            '.jpg': 'image/jpeg',
            '.jpeg': 'image/jpeg',
            '.gif': 'image/gif',
            '.svg': 'image/svg+xml',
            '.ico': 'image/x-icon',
            '.woff': 'font/woff',
            '.woff2': 'font/woff2',
            '.ttf': 'font/ttf',
            '.eot': 'application/vnd.ms-fontobject'
        }
        ext = Path(path).suffix.lower()
        return mime_types.get(ext, 'application/octet-stream')

    def _handle_websocket(self):
        """Обработка WebSocket соединения."""
        try:
            # Проверяем, что это WebSocket запрос
            if 'Upgrade' not in self.headers or self.headers['Upgrade'].lower() != 'websocket':
                logger.error("Не WebSocket запрос")
                self.send_error(400, "Expected WebSocket request")
                return

            # Проверяем наличие ключа
            if 'Sec-WebSocket-Key' not in self.headers:
                logger.error("Отсутствует WebSocket ключ")
                self.send_error(400, "No WebSocket key")
                return

            # Отправляем заголовки для апгрейда соединения
            ws_key = self.headers['Sec-WebSocket-Key'].encode('utf-8')
            ws_accept = base64.b64encode(
                hashlib.sha1(ws_key + b"258EAFA5-E914-47DA-95CA-C5AB0DC85B11").digest()
            ).decode('utf-8')

            self.send_response(101)
            self.send_header('Upgrade', 'websocket')
            self.send_header('Connection', 'Upgrade')
            self.send_header('Sec-WebSocket-Accept', ws_accept)
            self.end_headers()

            # Создаем и регистрируем WebSocket соединение
            protocol = WebSocketProtocol(ws_handler)
            protocol.connection_made(self)
            ws_handler.register(protocol)

            logger.info("WebSocket соединение установлено")

        except Exception as e:
            logger.error(f"Ошибка при установке WebSocket соединения: {str(e)}", exc_info=True)
            self.send_error(500)

class WebSocketServer:
    """Сервер для обработки WebSocket соединений."""
    
    def __init__(self, handler, host='localhost', port=8001):
        self.handler = handler
        self.host = host
        self.port = port
        self.server = None
        self._loop = None

    async def start(self):
        """Запуск WebSocket сервера."""
        try:
            self._loop = asyncio.get_event_loop()
            self.server = await self._loop.create_server(
                lambda: WebSocketProtocol(ws_handler=self.handler),
                self.host,
                self.port
            )
            logger.info(f"WebSocket сервер запущен на ws://{self.host}:{self.port}")
        except Exception as e:
            logger.error(f"Ошибка запуска WebSocket сервера: {e}", exc_info=True)
            raise

    async def stop(self):
        """Остановка WebSocket сервера."""
        if self.server:
            self.server.close()
            await self.server.wait_closed()
            logger.info("WebSocket сервер остановлен")

async def run_http_server(server):
    """Запуск HTTP сервера в асинхронном режиме."""
    loop = asyncio.get_event_loop()
    return await loop.run_in_executor(None, server.serve_forever)

async def run_server_async(host: str, port: int):
    """
    Асинхронный запуск сервера.
    
    Args:
        host: Хост для запуска сервера
        port: Порт для запуска сервера
    """
    try:
        # Создаем и запускаем HTTP сервер
        httpd = HTTPServer((host, port), TestReportServer)
        server_thread = threading.Thread(target=httpd.serve_forever)
        server_thread.daemon = True
        server_thread.start()
        logger.info(f"HTTP сервер запущен на http://{host}:{port}")
        
        # Создаем и запускаем WebSocket сервер
        ws_server = WebSocketServer(ws_handler, host, port + 1)
        await ws_server.start()
        logger.info(f"WebSocket сервер запущен на ws://{host}:{port + 1}")
        
        # Ждем завершения
        try:
            while True:
                await asyncio.sleep(1)
        except asyncio.CancelledError:
            logger.info("Получен сигнал остановки")
            httpd.shutdown()
            await ws_server.stop()
            
    except Exception as e:
        logger.error(f"Ошибка запуска сервера: {e}", exc_info=True)
        raise

def run_server(host: str = 'localhost', port: int = 8000):
    """Запуск сервера."""
    logger = logging.getLogger(__name__)
    setup_logging()
    
    try:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        
        try:
            loop.run_until_complete(run_server_async(host, port))
        except KeyboardInterrupt:
            logger.info("Сервер остановлен пользователем")
        except Exception as e:
            logger.error(f"Ошибка в работе сервера: {e}", exc_info=True)
        finally:
            loop.close()
            
    except Exception as e:
        logger.error(f"Ошибка запуска сервера: {e}", exc_info=True)
        raise

def cleanup_reports() -> None:
    """Очистка старых отчетов при завершении работы."""
    try:
        report_dir = Path(__file__).parent / 'report'
        if report_dir.exists():
            shutil.rmtree(report_dir)
            logger.info(f"Очищена директория отчетов: {report_dir}")
    except Exception as e:
        logger.error(f"Ошибка очистки отчетов: {e}", exc_info=True)

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Test Report Server')
    parser.add_argument('--host', default='localhost', help='Server host')
    parser.add_argument('--port', type=int, default=8000, help='Server port')
    
    args = parser.parse_args()
    run_server(args.host, args.port)
