"""
Модуль для запуска сервера с автоматической перезагрузкой при изменении файлов.
"""

import sys
import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess
import psutil

logger = logging.getLogger(__name__)

class ServerReloader(FileSystemEventHandler):
    def __init__(self):
        self.process = None
        self.start_server()

    def start_server(self):
        """Запуск сервера."""
        if self.process:
            self.stop_server()
        
        logger.info("Starting server...")
        server_script = Path(__file__).parent / 'server.py'
        
        # Запускаем сервер в отдельном процессе
        self.process = subprocess.Popen(
            [sys.executable, str(server_script)],
            cwd=str(Path(__file__).parent.parent.parent)
        )
        logger.info(f"Server started with PID: {self.process.pid}")

    def stop_server(self):
        """Остановка сервера и всех дочерних процессов."""
        if self.process:
            logger.info(f"Stopping server (PID: {self.process.pid})...")
            try:
                parent = psutil.Process(self.process.pid)
                children = parent.children(recursive=True)
                
                # Останавливаем дочерние процессы
                for child in children:
                    child.terminate()
                psutil.wait_procs(children, timeout=3)
                
                # Останавливаем родительский процесс
                self.process.terminate()
                self.process.wait(timeout=3)
                
            except psutil.NoSuchProcess:
                pass
            except Exception as e:
                logger.error(f"Error stopping server: {e}")
            finally:
                self.process = None

    def on_modified(self, event):
        """Обработчик изменения файлов."""
        if event.src_path.endswith('.py'):
            logger.info(f"Detected change in {event.src_path}")
            self.start_server()

def run_server_with_reload():
    """Запуск сервера с автоперезагрузкой."""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )

    server_dir = Path(__file__).parent
    reloader = ServerReloader()
    
    # Настраиваем наблюдателя за изменениями файлов
    observer = Observer()
    observer.schedule(reloader, str(server_dir), recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping server...")
        reloader.stop_server()
        observer.stop()
        observer.join()

if __name__ == '__main__':
    run_server_with_reload()
