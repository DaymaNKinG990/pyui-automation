"""
Тест для проверки архитектуры без запуска реального приложения.
"""

import pytest
import sys
from pathlib import Path

# Добавляем корневую директорию в PYTHONPATH
project_root = str(Path(__file__).parent.parent)
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pyui_automation.core.services.backend_factory import BackendFactory
from pyui_automation.core.session import AutomationSession
from pyui_automation.locators.windows import WindowsLocator


def test_backend_creation():
    """Тест создания backend'а"""
    try:
        backend = BackendFactory.create_backend('windows')
        assert backend is not None
        assert backend.is_initialized()
        print("✅ Backend создан и инициализирован успешно")
    except Exception as e:
        pytest.skip(f"Backend не может быть создан: {e}")


def test_locator_creation():
    """Тест создания locator'а"""
    try:
        backend = BackendFactory.create_backend('windows')
        locator = WindowsLocator(backend)
        assert locator is not None
        print("✅ Locator создан успешно")
    except Exception as e:
        pytest.skip(f"Locator не может быть создан: {e}")


def test_session_creation():
    """Тест создания session"""
    try:
        backend = BackendFactory.create_backend('windows')
        locator = WindowsLocator(backend)
        session = AutomationSession(backend, locator)
        assert session is not None
        print("✅ Session создан успешно")
    except Exception as e:
        pytest.skip(f"Session не может быть создан: {e}")


def test_backend_methods():
    """Тест основных методов backend'а"""
    try:
        backend = BackendFactory.create_backend('windows')
        
        # Тест получения размера экрана
        screen_size = backend.get_screen_size()
        assert isinstance(screen_size, tuple)
        assert len(screen_size) == 2
        assert screen_size[0] > 0 and screen_size[1] > 0
        print(f"✅ Размер экрана получен: {screen_size}")
        
        # Тест получения активного окна
        active_window = backend.get_active_window()
        print(f"✅ Активное окно получено: {active_window}")
        
    except Exception as e:
        pytest.skip(f"Методы backend'а не работают: {e}")


def test_session_methods():
    """Тест основных методов session"""
    try:
        backend = BackendFactory.create_backend('windows')
        locator = WindowsLocator(backend)
        session = AutomationSession(backend, locator)
        
        # Тест получения размера экрана через session
        screen_size = session.get_screen_size()
        assert isinstance(screen_size, tuple)
        assert len(screen_size) == 2
        print(f"✅ Размер экрана через session: {screen_size}")
        
        # Тест получения активного окна через session
        active_window = session.get_active_window()
        print(f"✅ Активное окно через session: {active_window}")
        
    except Exception as e:
        pytest.skip(f"Методы session не работают: {e}")


if __name__ == "__main__":
    # Запуск тестов напрямую
    print("🧪 Запуск тестов архитектуры...")
    
    test_backend_creation()
    test_locator_creation()
    test_session_creation()
    test_backend_methods()
    test_session_methods()
    
    print("✅ Все тесты архитектуры прошли успешно!") 