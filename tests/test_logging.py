import pytest
import logging
import sys
from pathlib import Path
import tempfile
from pyui_automation.core.logging import AutomationLogger
from pyui_automation.core.log_manager import get_logger


@pytest.fixture
def logger_instance():
    return AutomationLogger('test_logger')

@pytest.fixture
def temp_log_file(tmp_path):
    log_file = tmp_path / "test.log"
    yield log_file
    # Clean up
    if log_file.exists():
        try:
            log_file.unlink()
        except PermissionError:
            pass

def test_default_initialization():
    """Test logger initialization with default name"""
    logger = AutomationLogger()
    assert logger._logger.name == 'pyui_automation'
    assert logger._logger.level == logging.DEBUG
    assert len(logger._logger.handlers) == 1
    assert isinstance(logger._logger.handlers[0], logging.StreamHandler)
    assert logger._logger.handlers[0].stream == sys.stdout

def test_custom_initialization():
    """Test logger initialization with custom name"""
    logger = AutomationLogger('custom_logger')
    assert logger._logger.name == 'custom_logger'
    assert logger._logger.level == logging.DEBUG

def test_default_level(logger_instance):
    """Test default logging level"""
    assert logger_instance._logger.level == logging.DEBUG
    assert logger_instance._logger.handlers[0].level == logging.DEBUG

def test_set_level(logger_instance):
    """Test setting logging level"""
    logger_instance.set_level(logging.INFO)
    assert logger_instance._logger.level == logging.INFO
    assert all(h.level == logging.INFO for h in logger_instance._logger.handlers)

def test_logging_methods(logger_instance, caplog):
    """Test all logging methods"""
    with caplog.at_level(logging.DEBUG):
        logger_instance.debug("Debug message")
        logger_instance.info("Info message")
        logger_instance.warning("Warning message")
        logger_instance.error("Error message")
        logger_instance.critical("Critical message")

        assert "Debug message" in caplog.text
        assert "Info message" in caplog.text
        assert "Warning message" in caplog.text
        assert "Error message" in caplog.text
        assert "Critical message" in caplog.text

def test_add_file_handler(logger_instance, temp_log_file):
    """Test adding file handler"""
    initial_handlers = len(logger_instance._logger.handlers)
    logger_instance.add_file_handler(temp_log_file)
    
    # Verify handler was added
    assert len(logger_instance._logger.handlers) == initial_handlers + 1
    assert isinstance(logger_instance._logger.handlers[-1], logging.FileHandler)
    assert logger_instance._logger.handlers[-1].baseFilename == str(temp_log_file)
    
    # Test logging to file
    test_message = "Test file logging"
    logger_instance.info(test_message)
    
    # Verify message was written to file
    with open(temp_log_file, 'r') as f:
        log_content = f.read()
        assert test_message in log_content

def test_multiple_handlers(logger_instance, temp_log_file, caplog):
    """Test logging to multiple handlers"""
    # Add file handler
    logger_instance.add_file_handler(temp_log_file)
    
    # Log message
    test_message = "Test multiple handlers"
    with caplog.at_level(logging.INFO):
        logger_instance.info(test_message)
    
    # Check console output
    assert test_message in caplog.text
    
    # Check file output
    with open(temp_log_file, 'r') as f:
        log_content = f.read()
        assert test_message in log_content

def test_exception_logging(logger_instance, caplog):
    """Test logging exceptions"""
    with caplog.at_level(logging.ERROR):
        try:
            raise ValueError("Test exception")
        except Exception as e:
            logger_instance.error(f"Caught error: {str(e)}")
    
    assert "Caught error: Test exception" in caplog.text

def test_duplicate_handler_prevention(logger_instance):
    """Test prevention of duplicate handlers"""
    initial_handlers = len(logger_instance._logger.handlers)
    
    # Try to set up console handler again
    logger_instance._setup_console_handler()
    
    # Should still have same number of handlers
    assert len(logger_instance._logger.handlers) == initial_handlers

def test_global_logger_instance():
    """Test global logger instance"""
    logger = get_logger('test')
    assert isinstance(logger, AutomationLogger)
    assert logger._logger.name == 'test'
    assert logger._logger.level == logging.DEBUG

def test_handler_formatter(logger_instance):
    """Test handler formatters"""
    # Check console handler formatter
    console_handler = logger_instance._logger.handlers[0]
    assert isinstance(console_handler.formatter, logging.Formatter)
    assert console_handler.formatter._fmt == '%(levelname)-8s %(name)s:%(filename)s:%(lineno)d %(message)s'
    
    # Check file handler formatter
    with tempfile.NamedTemporaryFile(suffix='.log', delete=False) as tf:
        logger_instance.add_file_handler(Path(tf.name))
        file_handler = logger_instance._logger.handlers[-1]
        assert isinstance(file_handler.formatter, logging.Formatter)
        assert file_handler.formatter._fmt == '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
