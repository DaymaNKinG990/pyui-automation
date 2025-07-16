import logging
from pyui_automation.utils.logging_config import setup_logging

def test_setup_logging_creates_files_and_handlers(tmp_path, caplog):
    log_dir = tmp_path / 'logs'
    setup_logging(log_dir=log_dir, level=logging.INFO)
    logger = logging.getLogger()
    logger.info('test info')
    logger.error('test error')
    # Проверяем, что файлы созданы
    assert (log_dir / 'pyui_automation.log').exists()
    assert (log_dir / 'errors.log').exists()
    # Проверяем, что в логах есть записи
    with open(log_dir / 'pyui_automation.log', encoding='utf-8') as f:
        content = f.read()
    assert 'test info' in content or 'test error' in content
    with open(log_dir / 'errors.log', encoding='utf-8') as f:
        err_content = f.read()
    assert 'test error' in err_content
    # Проверяем, что хендлеры добавлены
    handlers = [h for h in logger.handlers if isinstance(h, logging.StreamHandler) or isinstance(h, logging.handlers.RotatingFileHandler)]
    assert len(handlers) >= 3 