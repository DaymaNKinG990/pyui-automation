from pathlib import Path
import pytest
from unittest.mock import MagicMock, patch
from pyui_automation import Application
import psutil
import comtypes.gen.UIAutomationClient as UIAutomationClient



@pytest.fixture
def mock_uiautomation():
    """Mock the UIAutomation COM interface"""
    mock_uia = MagicMock(spec=UIAutomationClient.IUIAutomation)
    mock_root = MagicMock()
    mock_uia.GetRootElement.return_value = mock_root
    
    mock_element = MagicMock()
    mock_element.CurrentName = "Test Window"
    mock_element.CurrentAutomationId = "test-window"
    mock_element.GetCurrentPropertyValue.return_value = "test-value"
    mock_element.CurrentIsEnabled = True
    mock_element.CurrentIsOffscreen = False
    mock_element.CurrentBoundingRectangle = (0, 0, 800, 600)
    mock_element.CurrentNativeWindowHandle = 12345
    
    mock_condition = MagicMock()
    mock_uia.CreatePropertyCondition.return_value = mock_condition
    mock_root.FindFirst.return_value = mock_element
    mock_root.FindAll.return_value = [mock_element]
    
    return mock_uia

@pytest.fixture
def mock_windows_backend(mock_uiautomation):
    """Create mock Windows backend"""
    with patch('comtypes.client.CreateObject', return_value=mock_uiautomation):
        with patch('pyui_automation.backends.windows.WindowsBackend') as mock_backend:
            instance = mock_backend.return_value
            instance.automation = mock_uiautomation
            instance.root = mock_uiautomation.GetRootElement()
            
            instance.find_window.return_value = instance.root.FindFirst.return_value
            instance.get_window.return_value = instance.root.FindFirst.return_value
            instance.get_window_title.return_value = "Test Window"
            instance.get_active_window.return_value = instance.root.FindFirst.return_value
            instance.get_main_window.return_value = instance.root.FindFirst.return_value
            instance.get_window_handles.return_value = [12345, 12346]
            
            yield instance

@pytest.fixture
def mock_process():
    """Create a mock process"""
    mock = MagicMock(spec=psutil.Process)
    mock.pid = 12345
    mock.name.return_value = "test.exe"
    mock.is_running.return_value = True
    mock.cpu_percent.return_value = 5.0
    mock.memory_info.return_value = MagicMock(rss=1024*1024)
    return mock

@pytest.fixture
def mock_application(mock_process, mock_windows_backend):
    """Create Application instance with mock process"""
    app = Application(Path("test.exe"), mock_process.pid)
    app._process = mock_process
    app._backend = mock_windows_backend
    return app

def test_terminate_application(mock_application):
    """Test terminating application"""
    mock_application.terminate()
    mock_application._process.terminate.assert_called_once()

def test_kill_application(mock_application):
    """Test force killing application"""
    mock_application.kill()
    mock_application._process.kill.assert_called_once()

def test_wait_for_window(mock_application):
    """Test waiting for window"""
    window = mock_application.wait_for_window("Test Window")
    assert window is not None
    assert window.CurrentName == "Test Window"
    
    window = mock_application.wait_for_window("Test Window", timeout=1)
    assert window is not None
    
    mock_application._backend.find_window.return_value = None
    window = mock_application.wait_for_window("Nonexistent Window", timeout=0.1)
    assert window is None

def test_get_window(mock_application):
    """Test getting window by title"""
    window = mock_application.get_window("Test Window")
    assert window is not None
    assert window.CurrentName == "Test Window"
    
    mock_application._backend.find_window.return_value = None
    window = mock_application.get_window("Nonexistent Window")
    assert window is None

def test_get_main_window(mock_application):
    """Test getting main window"""
    window = mock_application.get_main_window()
    assert window is not None
    assert window.CurrentName == "Test Window"
    
    mock_application._backend.get_active_window.return_value = None
    window = mock_application.get_main_window()
    assert window is None

def test_get_window_handles(mock_application):
    """Test getting window handles"""
    handles = mock_application.get_window_handles()
    assert handles == [12345, 12346]

def test_get_active_window(mock_application):
    """Test getting active window"""
    window = mock_application.get_active_window()
    assert window is not None
    assert window.CurrentName == "Test Window"

def test_is_running(mock_application):
    """Test checking if application is running"""
    assert mock_application.is_running()

def test_get_cpu_usage(mock_application):
    """Test getting CPU usage"""
    cpu_usage = mock_application.get_cpu_usage()
    assert cpu_usage == 5.0

def test_get_memory_usage(mock_application):
    mock_application._process.memory_info.return_value = MagicMock(rss=1024)
    memory_usage = mock_application.get_memory_usage()
    assert memory_usage == 1

def test_launch_invalid_path():
    """Test error when launching with invalid path"""
    with pytest.raises(RuntimeError):
        Application.launch(Path("/nonexistent/path.exe"))

def test_launch_process_fails(monkeypatch):
    """Test error when process fails to start"""
    def fake_popen(*a, **k):
        class FakeProc:
            def poll(self): return 1
            pid = 12345
            def communicate(self): return (b'', b'')
        return FakeProc()
    monkeypatch.setattr('subprocess.Popen', fake_popen)
    with pytest.raises(RuntimeError, match="Process failed to start"):
        Application.launch(Path("test.exe"))

def test_attach_invalid_pid():
    """Test error when attaching to non-existent PID"""
    with pytest.raises(ValueError):
        Application.attach("99999999")

def test_attach_invalid_name():
    """Test error when attaching to non-existent process name"""
    with pytest.raises(ValueError):
        Application.attach("definitely_not_a_real_process_name.exe")

def test_terminate_no_process():
    """Test terminate when no process set"""
    with patch('platform.system', return_value='Linux'), \
         patch('pyui_automation.backends.linux.LinuxBackend', MagicMock()):
        app = Application()
        app._process = None
        app.terminate()
        assert app._process is None

def test_kill_no_process():
    """Test kill when no process set"""
    with patch('platform.system', return_value='Linux'), \
         patch('pyui_automation.backends.linux.LinuxBackend', MagicMock()):
        app = Application()
        app._process = None
        app.kill()
        assert app._process is None

def test_is_running_no_process():
    """Test is_running when no process set"""
    with patch('platform.system', return_value='Linux'), \
         patch('pyui_automation.backends.linux.LinuxBackend', MagicMock()):
        app = Application()
        app._process = None
        assert not app.is_running()

def test_get_memory_cpu_usage_no_process():
    """Test get_memory_usage/get_cpu_usage when no process set"""
    with patch('platform.system', return_value='Linux'), \
         patch('pyui_automation.backends.linux.LinuxBackend', MagicMock()):
        app = Application()
        app._process = None
        assert app.get_memory_usage() == 0.0
        assert app.get_cpu_usage() == 0.0

def test_get_child_processes_none():
    """Test get_child_processes when no process set"""
    with patch('platform.system', return_value='Linux'), \
         patch('pyui_automation.backends.linux.LinuxBackend', MagicMock()):
        app = Application()
        app._process = None
        assert app.get_child_processes() == []

def test_get_child_processes_empty(mock_process):
    """Test get_child_processes returns empty if no children"""
    mock_process.children.return_value = []
    with patch('platform.system', return_value='Linux'), \
         patch('pyui_automation.backends.linux.LinuxBackend', MagicMock()):
        app = Application(process=mock_process)
        assert app.get_child_processes() == []

def test_terminate_timeout(monkeypatch, mock_process):
    """Test terminate with timeout expired (should call kill)"""
    def fake_wait(timeout):
        raise psutil.TimeoutExpired(timeout, pid=mock_process.pid)
    mock_process.wait.side_effect = fake_wait
    with patch('platform.system', return_value='Linux'), \
         patch('pyui_automation.backends.linux.LinuxBackend', MagicMock()):
        app = Application(process=mock_process)
        app.terminate(timeout=0)
        mock_process.terminate.assert_called_once()
        mock_process.kill.assert_called_once()
