import os
import sys
import json
import time
import asyncio
import logging
import threading
from pathlib import Path
from datetime import datetime
from http.server import HTTPServer, SimpleHTTPRequestHandler, ThreadingHTTPServer
from queue import Queue, Empty
from threading import Thread, Event

logger = logging.getLogger(__name__)

"""
Модуль реализации HTTP сервера для отображения результатов тестов.

Этот модуль предоставляет HTTP сервер для отображения результатов тестов pytest в веб-интерфейсе.
Он поддерживает кэширование результатов, CORS, и отдачу статических файлов.
"""

# Настройка логирования
log_dir = Path(__file__).parent.parent / 'logs'
log_dir.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_dir / 'server.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)

class WebSocketProtocol(asyncio.Protocol):
    """Протокол для обработки WebSocket соединений."""
    
    def __init__(self, handler):
        self.handler = handler
        self.transport = None
        self.buffer = bytearray()
        self.header_parsed = False
        self.frame_length = 0
        self.mask = None
        self._logger = logging.getLogger('websocket')
        
    def connection_made(self, transport):
        """Установка соединения."""
        self.transport = transport
        self._logger.info(f"Установлено новое соединение: {transport.get_extra_info('peername')}")
        asyncio.create_task(self.handler.register(self))
        
    def connection_lost(self, exc):
        """Потеря соединения."""
        self._logger.info(f"Соединение закрыто: {exc if exc else 'нормальное завершение'}")
        asyncio.create_task(self.handler.unregister(self))
        
    def data_received(self, data):
        """Получение данных."""
        try:
            self.buffer.extend(data)
            self._process_buffer()
        except Exception as e:
            self._logger.error(f"Ошибка обработки данных: {e}", exc_info=True)
            
    def _process_buffer(self):
        """Обработка буфера данных."""
        while self.buffer:
            if not self.header_parsed:
                if len(self.buffer) < 2:
                    return
                    
                # Парсим заголовок WebSocket фрейма
                first_byte = self.buffer[0]
                second_byte = self.buffer[1]
                
                fin = (first_byte & 0b10000000) != 0
                opcode = first_byte & 0b00001111
                is_masked = (second_byte & 0b10000000) != 0
                payload_length = second_byte & 0b01111111
                
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
                    
                if is_masked:
                    if len(self.buffer) < header_length + 4:
                        return
                    self.mask = self.buffer[header_length:header_length + 4]
                    header_length += 4
                    
                self.frame_length = payload_length
                self.header_parsed = True
                self.buffer = self.buffer[header_length:]
                
            if len(self.buffer) < self.frame_length:
                return
                
            # Получаем и обрабатываем payload
            payload = self.buffer[:self.frame_length]
            self.buffer = self.buffer[self.frame_length:]
            
            if self.mask:
                unmasked = bytearray(len(payload))
                for i in range(len(payload)):
                    unmasked[i] = payload[i] ^ self.mask[i % 4]
                payload = unmasked
                
            try:
                message = json.loads(payload.decode())
                self._handle_message(message)
            except json.JSONDecodeError:
                self._logger.warning(f"Получено некорректное JSON сообщение: {payload}")
            except Exception as e:
                self._logger.error(f"Ошибка обработки сообщения: {e}", exc_info=True)
                
            self.header_parsed = False
            self.frame_length = 0
            self.mask = None
            
    def _handle_message(self, message):
        """Обработка полученного сообщения."""
        try:
            message_type = message.get('type')
            
            if message_type == 'reload':
                self._logger.info("Получена команда перезагрузки")
                # Отправляем подтверждение
                self.send_message(json.dumps({
                    'type': 'reload_ack',
                    'status': 'success'
                }))
            elif message_type == 'ping':
                self._logger.debug("Получен ping")
                self.send_message(json.dumps({
                    'type': 'pong',
                    'timestamp': datetime.now().isoformat()
                }))
            else:
                self._logger.warning(f"Получено неизвестное сообщение: {message}")
                
        except Exception as e:
            self._logger.error(f"Ошибка при обработке сообщения {message}: {e}", exc_info=True)
            
    def send_message(self, message):
        """Отправка сообщения клиенту."""
        if not isinstance(message, str):
            message = json.dumps(message)
            
        data = message.encode()
        length = len(data)
        header = bytearray()
        
        # Первый байт: FIN + опкод
        header.append(0x80 | 0x1)  # FIN=1, RSV=000, опкод=0x1 (text)
        
        # Второй байт: MASK + длина полезной нагрузки
        if length < 126:
            header.append(length)
        elif length < 65536:
            header.append(126)
            header.extend(length.to_bytes(2, 'big'))
        else:
            header.append(127)
            header.extend(length.to_bytes(8, 'big'))
            
        # Отправляем фрейм
        try:
            self.transport.write(header + data)
            self._logger.debug(f"Отправлено сообщение длиной {length} байт")
        except Exception as e:
            self._logger.error(f"Ошибка отправки сообщения: {e}", exc_info=True)

class WebSocketHandler:
    """Обработчик WebSocket соединений."""
    
    def __init__(self):
        self.connections = set()
        self.lock = threading.Lock()
        self._connected = False
        self._connection_url = None
        self.loop = None
        self._logger = logging.getLogger('websocket')
        
    @classmethod
    def get_instance(cls):
        """Получение глобального экземпляра WebSocketHandler."""
        if not hasattr(cls, '_instance'):
            cls._instance = cls()
            cls._instance._logger.info("Создан новый экземпляр WebSocketHandler")
        return cls._instance
    
    def is_connected(self) -> bool:
        """Проверка состояния соединения."""
        is_connected = self._connected and bool(self.connections)
        self._logger.debug(f"Проверка соединения: connected={is_connected}, connections={len(self.connections)}")
        return is_connected
    
    async def connect(self, url: str = None) -> bool:
        """
        Установка WebSocket соединения.
        
        Args:
            url: URL для подключения. Если не указан, используется последний успешный URL.
            
        Returns:
            bool: True если соединение успешно установлено, иначе False
        """
        self._logger.info(f"Попытка подключения к {url or self._connection_url}")
        
        if url:
            self._connection_url = url
        elif not self._connection_url:
            self._logger.error("URL для подключения не указан")
            return False
            
        try:
            if not self.loop:
                self.loop = asyncio.get_event_loop()
                self._logger.debug("Получен event loop")
                
            # Создаем новое соединение
            transport, protocol = await self.loop.create_connection(
                lambda: WebSocketProtocol(self),
                self._connection_url,
                8001  # WebSocket порт
            )
            self._connected = True
            self._logger.info(f"Успешное подключение к {self._connection_url}")
            return True
            
        except Exception as e:
            self._logger.error(f"Ошибка при подключении к {self._connection_url}: {e}", exc_info=True)
            self._connected = False
            return False
    
    async def disconnect(self):
        """Закрытие всех WebSocket соединений."""
        with self.lock:
            for ws in self.connections:
                try:
                    ws.transport.close()
                except Exception as e:
                    logger.error(f"Ошибка при закрытии соединения: {e}")
            self.connections.clear()
            self._connected = False
    
    async def register(self, websocket):
        """Регистрация нового WebSocket соединения."""
        with self.lock:
            self.connections.add(websocket)
            self._logger.info(f"Новое WebSocket соединение. Всего соединений: {len(self.connections)}")
    
    async def unregister(self, websocket):
        """Удаление WebSocket соединения."""
        with self.lock:
            self.connections.remove(websocket)
            self._logger.info(f"WebSocket соединение закрыто. Осталось соединений: {len(self.connections)}")
    
    async def broadcast(self, message):
        """Отправка сообщения всем подключенным клиентам."""
        self._logger.debug(f"Начало широковещательной рассылки сообщения всем клиентам")
        if not self.connections:
            self._logger.warning("Нет подключенных клиентов для отправки сообщения")
            return
            
        try:
            for ws in self.connections:
                ws.send_message(message)
            self._logger.info(f"Сообщение успешно отправлено {len(self.connections)} клиентам")
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
    
    async def __call__(self, websocket):
        """Обработка WebSocket соединения."""
        await self.register(websocket)
        try:
            async for message in websocket:
                try:
                    data = json.loads(message)
                    if data.get('type') == 'ping':
                        await websocket.send(json.dumps({'type': 'pong'}))
                except json.JSONDecodeError:
                    logger.warning(f"Получено некорректное сообщение: {message}")
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            logger.error(f"Ошибка в WebSocket соединении: {e}", exc_info=True)
        finally:
            await self.unregister(websocket)

# Глобальный экземпляр WebSocketHandler
ws_handler = WebSocketHandler.get_instance()

# Определяем пути к директориям
CURRENT_DIR = Path(__file__).parent
TEMPLATES_DIR = CURRENT_DIR / 'templates'
RESULTS_DIR = CURRENT_DIR.parent / 'results'

class TestReportServer(SimpleHTTPRequestHandler):
    """HTTP сервер для отображения результатов тестов."""
    
    def __init__(self, *args, results_dir=None, template_dir=None, **kwargs):
        """Инициализация сервера."""
        self.results_dir = Path(results_dir) if results_dir else RESULTS_DIR
        self.template_dir = Path(template_dir) if template_dir else TEMPLATES_DIR
        self.cache = {}
        super().__init__(*args, **kwargs)

    def do_GET(self):
        """Обработка GET запросов."""
        try:
            # Проверяем WebSocket запрос
            if self.headers.get('Upgrade', '').lower() == 'websocket':
                self._handle_websocket()
                return

            # Получаем путь запроса без параметров
            path = self.path.split('?')[0].strip('/')
            
            # Для корневого пути отдаем report.html
            if not path:
                path = 'report.html'
                file_path = TEMPLATES_DIR / path
            # Для статических файлов
            elif path.startswith('assets/'):
                file_path = TEMPLATES_DIR / path
            # Для остальных файлов ищем в assets
            else:
                file_path = TEMPLATES_DIR / 'assets' / path

            logger.info(f"Запрошен файл: {file_path}")

            # Проверяем существование файла
            if not os.path.exists(file_path):
                logger.warning(f"Файл не найден: {file_path}")
                self.send_error(404, f"File not found: {path}")
                return

            # Отправляем файл
            with open(file_path, 'rb') as f:
                content = f.read()

            self.send_response(200)
            self.send_header('Content-Type', self._get_content_type(str(file_path)))
            self.send_header('Content-Length', str(len(content)))
            self.end_headers()
            self.wfile.write(content)

        except Exception as e:
            logger.error(f"Ошибка при обработке GET запроса: {e}")
            self.send_error(500, str(e))

    def _serve_report(self):
        """Отдача основного шаблона."""
        try:
            logger.info("Запрос основного шаблона")
            template_path = self.template_dir / 'report.html'
            logger.debug(f"Путь к шаблону: {template_path}")
            
            if not template_path.exists():
                logger.error(f"Шаблон не найден: {template_path}")
                self.send_error(404)
                return
                
            with open(template_path, 'r', encoding='utf-8') as f:
                template_content = f.read()
                
            # Отправляем заголовки
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            # Отправляем контент
            self.wfile.write(template_content.encode('utf-8'))
            logger.info("Шаблон успешно отправлен")
            
        except Exception as e:
            logger.error(f"Ошибка при отдаче шаблона: {e}", exc_info=True)
            self.send_error(500, str(e))

    def _serve_static_file(self, file_path):
        """Отдача статического файла."""
        try:
            # Получаем MIME тип
            content_type = self._get_content_type(file_path)
            
            # Читаем файл
            with open(file_path, 'rb') as f:
                content = f.read()
            
            # Отправляем заголовки
            self.send_response(200)
            self.send_header('Content-type', content_type)
            if content_type == 'application/javascript':
                self.send_header('Cache-Control', 'no-cache')
            self.end_headers()
            
            # Отправляем контент
            self.wfile.write(content)
            logger.debug(f"Отправлен статический файл: {file_path}")
            
        except Exception as e:
            logger.error(f"Ошибка при отдаче статического файла {file_path}: {e}", exc_info=True)
            self.send_error(500, str(e))

    def _serve_manifest(self):
        """Отдача манифеста."""
        try:
            logger.info("Запрос манифеста")
            manifest_path = self.results_dir / 'manifest.json'
            
            if not manifest_path.exists():
                logger.warning("Манифест не найден")
                self.send_error(404)
                return
                
            # Читаем манифест
            with open(manifest_path, 'r', encoding='utf-8') as f:
                manifest_data = json.load(f)
                logger.debug(f"Прочитан манифест: {manifest_data}")
            
            # Отправляем заголовки
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
            self.end_headers()
            
            # Отправляем данные
            manifest_json = json.dumps(manifest_data)
            self.wfile.write(manifest_json.encode('utf-8'))
            logger.info("Манифест успешно отправлен")
            
        except Exception as e:
            logger.error(f"Ошибка при отдаче манифеста: {e}", exc_info=True)
            self.send_error(500, str(e))

    def _handle_websocket(self):
        """Обработка WebSocket соединения."""
        try:
            logger.info("Начало обработки WebSocket соединения")
            
            # Проверяем заголовки
            headers = {k.lower(): v for k, v in self.headers.items()}
            if 'upgrade' not in headers or headers['upgrade'].lower() != 'websocket':
                logger.error("Отсутствует заголовок Upgrade: websocket")
                self.send_error(400, "Expected Upgrade: websocket")
                return
                
            if 'sec-websocket-key' not in headers:
                logger.error("Отсутствует заголовок Sec-WebSocket-Key")
                self.send_error(400, "Sec-WebSocket-Key header is missing")
                return
                
            # Вычисляем ключ для ответа
            ws_key = headers['sec-websocket-key']
            ws_accept = self._calculate_websocket_accept(ws_key)
            
            # Отправляем ответ на handshake
            logger.debug("Отправка WebSocket handshake")
            self.send_response(101, "Switching Protocols")
            self.send_header('Upgrade', 'websocket')
            self.send_header('Connection', 'Upgrade')
            self.send_header('Sec-WebSocket-Accept', ws_accept)
            self.end_headers()
            
            logger.info("WebSocket соединение установлено")
            
            # Отправляем приветственное сообщение
            hello_message = json.dumps({
                'type': 'hello',
                'content': {
                    'message': 'Соединение установлено',
                    'timestamp': time.time()
                }
            })
            self._send_websocket_frame(hello_message.encode('utf-8'))
            
            # Основной цикл обработки сообщений
            while True:
                message = self._read_websocket_frame()
                if message is None:
                    break
                    
                try:
                    data = json.loads(message)
                    if data.get('type') == 'hello':
                        # Отвечаем на приветствие
                        response = json.dumps({
                            'type': 'hello',
                            'content': {
                                'status': 'connected',
                                'timestamp': time.time()
                            }
                        })
                        self._send_websocket_frame(response.encode('utf-8'))
                    else:
                        logger.warning(f"Получено неизвестное сообщение: {data}")
                except json.JSONDecodeError:
                    logger.error("Получено некорректное JSON сообщение")
                except Exception as e:
                    logger.error(f"Ошибка при обработке сообщения: {e}")
                    
        except Exception as e:
            logger.error(f"Ошибка WebSocket соединения: {e}")
            return

    def _read_websocket_frame(self):
        """Чтение WebSocket фрейма."""
        try:
            # Читаем первые два байта
            header = self.rfile.read(2)
            if not header or len(header) < 2:
                return None
                
            # Разбираем заголовок
            fin = (header[0] & 0x80) >> 7
            opcode = header[0] & 0x0F
            mask = (header[1] & 0x80) >> 7
            payload_len = header[1] & 0x7F
            
            # Проверяем опкод
            if opcode == 0x8:  # Close frame
                return None
                
            # Получаем длину данных
            if payload_len == 126:
                payload_len = int.from_bytes(self.rfile.read(2), 'big')
            elif payload_len == 127:
                payload_len = int.from_bytes(self.rfile.read(8), 'big')
                
            # Читаем маску
            if mask:
                masking_key = self.rfile.read(4)
            
            # Читаем данные
            payload = self.rfile.read(payload_len)
            
            # Демаскируем данные если нужно
            if mask:
                unmasked = bytearray(payload_len)
                for i in range(payload_len):
                    unmasked[i] = payload[i] ^ masking_key[i % 4]
                payload = unmasked
                
            return payload
            
        except Exception as e:
            logger.error(f"Ошибка при чтении WebSocket фрейма: {e}")
            return None

    def _send_websocket_frame(self, data, opcode=0x01):
        """Отправка WebSocket фрейма."""
        try:
            length = len(data)
            header = bytearray()
            
            # Первый байт: FIN + опкод
            header.append(0x80 | opcode)  # FIN=1, RSV=000, опкод
            
            # Второй байт: MASK + длина полезной нагрузки
            if length < 126:
                header.append(length)
            elif length < 65536:
                header.append(126)
                header.extend(length.to_bytes(2, 'big'))
            else:
                header.append(127)
                header.extend(length.to_bytes(8, 'big'))
                
            # Отправляем заголовок и данные
            self.wfile.write(header)
            self.wfile.write(data)
            self.wfile.flush()
            
        except Exception as e:
            logger.error(f"Ошибка при отправке WebSocket фрейма: {e}")
            raise

    def _calculate_websocket_accept(self, key):
        """Вычисление Sec-WebSocket-Accept."""
        import base64
        import hashlib
        
        GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
        sha1 = hashlib.sha1((key + GUID).encode()).digest()
        return base64.b64encode(sha1).decode()

    def _get_content_type(self, path):
        """Определение MIME типа файла."""
        ext = path.split('.')[-1].lower()
        return {
            'html': 'text/html',
            'js': 'application/javascript',
            'css': 'text/css',
            'json': 'application/json',
            'png': 'image/png',
            'jpg': 'image/jpeg',
            'gif': 'image/gif',
            'svg': 'image/svg+xml',
        }.get(ext, 'application/octet-stream')

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

async def run_server_async(host: str = 'localhost', port: int = 8000) -> None:
    """
    Асинхронный запуск сервера.
    
    Args:
        host: хост для запуска сервера
        port: порт для запуска сервера
    """
    try:
        # Создаем HTTP сервер
        http_server = HTTPServer((host, port), TestReportServer)
        logger.info(f"Запуск HTTP сервера на http://{host}:{port}")
        
        # Создаем WebSocket сервер
        ws_port = port + 1
        ws_server = WebSocketServer(ws_handler, host, ws_port)
        await ws_server.start()
        
        # Запускаем HTTP сервер
        await run_http_server(http_server)
            
    except Exception as e:
        logger.error(f"Ошибка запуска сервера: {e}", exc_info=True)
        raise

def run_server(host='localhost', port=8000):
    """Запуск сервера."""
    try:
        # Определяем пути
        base_dir = Path(__file__).resolve().parent
        template_dir = base_dir / 'templates'
        results_dir = base_dir.parent / 'results'
        
        logger.info(f"Базовая директория: {base_dir}")
        logger.info(f"Директория шаблонов: {template_dir}")
        logger.info(f"Директория результатов: {results_dir}")
        
        # Проверяем существование директорий
        if not template_dir.exists():
            logger.error(f"Директория шаблонов не найдена: {template_dir}")
            raise FileNotFoundError(f"Директория шаблонов не найдена: {template_dir}")
            
        # Проверяем наличие шаблона
        report_template = template_dir / 'report.html'
        if not report_template.exists():
            logger.error(f"Файл шаблона не найден: {report_template}")
            raise FileNotFoundError(f"Файл шаблона не найден: {report_template}")
            
        # Создаем директорию для результатов
        results_dir.mkdir(parents=True, exist_ok=True)
        
        # Создаем и запускаем сервер
        server = ThreadingHTTPServer(
            (host, port),
            lambda *args, **kwargs: TestReportServer(
                *args,
                template_dir=template_dir,
                results_dir=results_dir,
                **kwargs
            )
        )
        
        logger.info(f"Сервер запущен на http://{host}:{port}")
        server.serve_forever()
        
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
