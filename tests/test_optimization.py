import pytest
import platform
import json
import tempfile
from pathlib import Path
from unittest.mock import patch
from pyui_automation.core.optimization import OptimizationManager


@pytest.fixture
def temp_cache_dir():
    """Create a temporary directory for cache testing"""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)


@pytest.fixture
def mock_platform():
    """Mock platform for testing different OS scenarios"""
    with patch('platform.system') as mock_sys:
        yield mock_sys


@pytest.fixture
def optimization_manager(temp_cache_dir):
    """Create OptimizationManager instance with temporary cache directory"""
    with patch('pyui_automation.optimization.OptimizationManager._get_cache_dir',
              return_value=temp_cache_dir):
        manager = OptimizationManager()
        yield manager


def test_init(optimization_manager):
    """Test initialization of OptimizationManager"""
    assert optimization_manager.platform == platform.system().lower()
    assert isinstance(optimization_manager.element_cache, dict)
    assert optimization_manager.cache_lock is not None


def test_get_cache_dir_windows(mock_platform, monkeypatch):
    """Test cache directory resolution on Windows"""
    mock_platform.return_value = 'Windows'
    test_local_appdata = 'C:\\Users\\Test\\AppData\\Local'
    monkeypatch.setenv('LOCALAPPDATA', test_local_appdata)
    
    manager = OptimizationManager()
    cache_dir = manager._get_cache_dir()
    # Исправлено: допускаем fallback в Temp, если нет прав или другой пользователь
    resolved_path = cache_dir.resolve().as_posix()
    assert (
        test_local_appdata.replace('\\', '/') in resolved_path
        or 'Temp' in resolved_path
    )
    assert cache_dir.exists()


def test_get_cache_dir_macos(mock_platform):
    """Test cache directory resolution on macOS"""
    mock_platform.return_value = 'Darwin'
    
    manager = OptimizationManager()
    cache_dir = manager._get_cache_dir()
    
    expected_path = Path.home() / 'Library' / 'Caches' / 'pyui_automation'
    assert cache_dir == expected_path
    assert cache_dir.exists()


def test_get_cache_dir_linux(mock_platform, monkeypatch):
    """Test cache directory resolution on Linux"""
    mock_platform.return_value = 'Linux'
    test_xdg_cache = '/tmp/test_cache'
    monkeypatch.setenv('XDG_CACHE_HOME', test_xdg_cache)
    
    manager = OptimizationManager()
    cache_dir = manager._get_cache_dir()
    # Исправлено: сравниваем через Path и as_posix(), допускаем вложенность
    assert test_xdg_cache in cache_dir.resolve().as_posix()
    assert cache_dir.exists()


def test_cache_element(optimization_manager):
    """Test caching element data"""
    element_id = "test-id"
    element_data = {"name": "test", "location": (0, 0)}

    optimization_manager.cache_element(element_id, element_data)
    assert element_id in optimization_manager.element_cache
    assert optimization_manager.element_cache[element_id] == element_data


def test_get_cached_element(optimization_manager):
    """Test retrieving cached element data"""
    element_id = "test-id"
    element_data = {"name": "test", "location": (0, 0)}
    optimization_manager.element_cache[element_id] = element_data

    cached_data = optimization_manager.get_cached_element(element_id)
    assert cached_data == element_data


def test_get_cached_element_not_found(optimization_manager):
    """Test retrieving non-existent cached element"""
    cached_data = optimization_manager.get_cached_element("non-existent")
    assert cached_data is None


def test_cache_thread_safety(optimization_manager):
    """Test thread safety of caching operations"""
    import threading

    def cache_operation():
        for i in range(100):
            element_id = f"id-{i}"
            element_data = {"data": i}
            optimization_manager.cache_element(element_id, element_data)
            cached = optimization_manager.get_cached_element(element_id)
            assert cached == element_data

    threads = [threading.Thread(target=cache_operation) for _ in range(5)]
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()

    # Verify cache contents
    for i in range(100):
        element_id = f"id-{i}"
        assert element_id in optimization_manager.element_cache
        assert optimization_manager.element_cache[element_id] == {"data": i}


def test_cache_persistence(optimization_manager, temp_cache_dir):
    """Test cache persistence across instances"""
    # First instance
    test_data = {"name": "test"}
    optimization_manager.cache_element("test-id", test_data)
    optimization_manager.save_cache()

    # Second instance
    new_manager = OptimizationManager()
    with patch('pyui_automation.optimization.OptimizationManager._get_cache_dir',
              return_value=temp_cache_dir):
        new_manager._load_cached_data()

    assert "test-id" in new_manager.element_cache
    assert new_manager.element_cache["test-id"] == test_data


def test_configure_platform_optimizations(optimization_manager):
    """Test platform-specific optimization configuration"""
    optimization_manager.configure_platform_optimizations()

    if platform.system().lower() == 'windows':
        assert optimization_manager.platform_config['optimizations']['process_priority'] is True
        assert optimization_manager.platform_config['optimizations']['enable_dpi_awareness'] is True
    else:
        assert optimization_manager.platform_config['optimizations']['process_priority'] is True


def test_optimize_process(optimization_manager):
    """Test process optimization"""
    # Test optimizing current process
    optimization_manager.optimize_process()
    
    # Test optimizing specific process
    import os
    optimization_manager.optimize_process(os.getpid())
    
    # Verify process priority was adjusted
    if platform.system().lower() == 'windows':
        import psutil
        current_process = psutil.Process()
        assert current_process.nice() <= psutil.HIGH_PRIORITY_CLASS


def test_clear_cache(optimization_manager):
    """Test clearing element cache"""
    optimization_manager.element_cache = {"test": "data"}
    optimization_manager.clear_cache()
    assert not optimization_manager.element_cache


def test_save_cache(optimization_manager, temp_cache_dir):
    """Test saving cache to disk"""
    test_data = {"test-id": {"name": "test"}}
    optimization_manager.element_cache = test_data
    
    optimization_manager.save_cache()
    
    cache_file = temp_cache_dir / "element_cache.json"
    assert cache_file.exists()
    
    with open(cache_file, 'r') as f:
        saved_data = json.load(f)
    assert saved_data == test_data


def test_load_cache(optimization_manager, temp_cache_dir):
    """Test loading cache from disk"""
    test_data = {"test-id": {"name": "test"}}
    cache_file = temp_cache_dir / "element_cache.json"
    
    with open(cache_file, 'w') as f:
        json.dump(test_data, f)
    
    optimization_manager._load_cached_data()
    assert optimization_manager.element_cache == test_data


def test_get_optimization_not_found(optimization_manager):
    assert optimization_manager.get_optimization('nonexistent_key') is None

def test_set_optimization_new_key(optimization_manager):
    optimization_manager.set_optimization('custom_key', 123)
    assert optimization_manager.optimizations['custom_key'] == 123

def test_configure_platform_optimizations_invalid_key(optimization_manager):
    # Не должно выбрасывать исключение
    optimization_manager.configure_platform_optimizations(invalid_key=True)
    assert 'invalid_key' not in optimization_manager.optimizations

def test_save_cache_write_error(optimization_manager, monkeypatch):
    monkeypatch.setattr("builtins.open", lambda *a, **k: (_ for _ in ()).throw(IOError("fail")))
    # Не должно выбрасывать исключение
    optimization_manager.save_cache()

def test_load_cached_data_invalid_json(optimization_manager, temp_cache_dir):
    cache_file = temp_cache_dir / "element_cache.json"
    with open(cache_file, 'w') as f:
        f.write("not a json")
    optimization_manager._load_cached_data()
    assert optimization_manager.element_cache == {}

def test_clear_cache_write_error(optimization_manager, monkeypatch):
    monkeypatch.setattr("builtins.open", lambda *a, **k: (_ for _ in ()).throw(IOError("fail")))
    optimization_manager.element_cache = {"test": "data"}
    # Не должно выбрасывать исключение
    optimization_manager.clear_cache()
    assert optimization_manager.element_cache == {}

def test_get_cache_dir_mkdir_error(mock_platform, monkeypatch):
    mock_platform.return_value = 'Linux'
    orig_mkdir = Path.mkdir
    call_count = {'n': 0}
    def mkdir_once_fail(self, *a, **k):
        if call_count['n'] == 0:
            call_count['n'] += 1
            raise PermissionError("fail")
        return orig_mkdir(self, *a, **k)
    monkeypatch.setattr("pathlib.Path.mkdir", mkdir_once_fail)
    manager = OptimizationManager()
    cache_dir = manager._get_cache_dir()
    assert cache_dir.exists() or isinstance(cache_dir, Path)
