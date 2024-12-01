import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.core import UIAutomation, Mouse, Keyboard
import time
import numpy as np
from PIL import Image
import platform
import comtypes.client
import comtypes.gen.UIAutomationClient as UIAutomationClient
import unittest
from pathlib import Path
import tempfile
import psutil


@pytest.fixture
def mock_uiautomation():
    """Mock the UIAutomation COM interface"""
    mock_uia = MagicMock(spec=UIAutomationClient.IUIAutomation)
    mock_root = MagicMock()
    mock_uia.GetRootElement.return_value = mock_root
    
    # Mock element
    mock_element = MagicMock()
    mock_element.CurrentName = "test-button"
    mock_element.CurrentAutomationId = "test-id"
    mock_element.GetCurrentPropertyValue.return_value = "test-value"
    mock_element.CurrentIsEnabled = True
    mock_element.CurrentIsOffscreen = False
    mock_element.CurrentBoundingRectangle = (0, 0, 100, 30)
    
    # Set up search conditions
    mock_condition = MagicMock()
    mock_uia.CreatePropertyCondition.return_value = mock_condition
    mock_root.FindFirst.return_value = mock_element
    mock_root.FindAll.return_value = [mock_element]
    
    return mock_uia


@pytest.fixture
def mock_windows_backend(mock_uiautomation):
    """Create mock Windows backend"""
    with patch('comtypes.client.CreateObject', return_value=mock_uiautomation) as mock_create:
        with patch('pyui_automation.backends.windows.WindowsBackend') as mock_backend:
            instance = mock_backend.return_value
            instance.automation = mock_uiautomation
            instance.root = mock_uiautomation.GetRootElement()
            
            # Set up backend methods
            instance.find_element.return_value = instance.root.FindFirst.return_value
            instance.find_elements.return_value = instance.root.FindAll.return_value
            instance.capture_screenshot.return_value = np.zeros((100, 100, 3), dtype=np.uint8)
            instance.type_text.return_value = True
            instance.click.return_value = True
            instance.get_active_window.return_value = instance.root.FindFirst.return_value
            
            yield instance


@pytest.fixture
def ui_automation(mock_windows_backend):
    """Create UIAutomation instance with mock backend"""
    with patch('platform.system', return_value='Windows'):
        automation = UIAutomation()
        automation._backend = mock_windows_backend
        return automation


@pytest.fixture
def temp_dir(tmp_path):
    """Create temporary directory for testing"""
    return tmp_path


def test_find_element(ui_automation):
    """Test finding an element"""
    element = ui_automation.find_element(by="id", value="test-id")
    assert element is not None
    assert element.id == "test-id"
    assert element.name == "test-button"
    ui_automation._backend.find_element.assert_called_once_with("id", "test-id", 0)


def test_find_element_with_timeout(ui_automation):
    """Test finding an element with timeout"""
    element = ui_automation.find_element(by="name", value="test-button", timeout=5)
    assert element is not None
    ui_automation._backend.find_element.assert_called_once_with("name", "test-button", 5)


def test_take_screenshot(ui_automation, temp_dir):
    """Test taking a screenshot"""
    screenshot = ui_automation.take_screenshot()
    assert screenshot is not None
    assert isinstance(screenshot, np.ndarray)
    assert screenshot.shape == (100, 100, 3)


def test_keyboard_input(ui_automation):
    """Test keyboard input"""
    # Test type_text
    assert ui_automation.keyboard.type_text("test") is True
    ui_automation._backend.type_text.assert_called_once_with("test", 0.0)
    
    # Test press_key
    ui_automation._backend.press_key.return_value = True
    assert ui_automation.keyboard.press_key("a") is True
    ui_automation._backend.press_key.assert_called_once_with("a")
    
    # Test release_key
    ui_automation._backend.release_key.return_value = True
    assert ui_automation.keyboard.release_key("a") is True
    ui_automation._backend.release_key.assert_called_once_with("a")
    
    # Test press_keys
    ui_automation._backend.press_keys.return_value = True
    assert ui_automation.keyboard.press_keys("ctrl", "c") is True
    ui_automation._backend.press_keys.assert_called_once_with("ctrl", "c")


def test_mouse_click(ui_automation):
    """Test mouse click"""
    # Test basic click
    ui_automation._backend.click.return_value = True
    assert ui_automation.mouse.click(100, 200) is True
    ui_automation._backend.click.assert_called_once_with(100, 200, "left")
    
    # Test right click
    ui_automation._backend.click.reset_mock()
    ui_automation._backend.click.return_value = True
    assert ui_automation.mouse.click(100, 200, "right") is True
    ui_automation._backend.click.assert_called_once_with(100, 200, "right")
    
    # Test double click
    ui_automation._backend.click.reset_mock()
    ui_automation._backend.click.return_value = True
    assert ui_automation.mouse.double_click(100, 200) is True
    assert ui_automation._backend.click.call_count == 2
    ui_automation._backend.click.assert_has_calls([
        unittest.mock.call(100, 200, "left"),
        unittest.mock.call(100, 200, "left")
    ])
    
    # Test drag
    ui_automation._backend.move_mouse.return_value = True
    ui_automation._backend.mouse_down.return_value = True
    ui_automation._backend.mouse_up.return_value = True
    assert ui_automation.mouse.drag(100, 200, 300, 400) is True
    ui_automation._backend.move_mouse.assert_has_calls([
        unittest.mock.call(100, 200),
        unittest.mock.call(300, 400)
    ])
    ui_automation._backend.mouse_down.assert_called_once_with("left")
    ui_automation._backend.mouse_up.assert_called_once_with("left")


def test_wait_until(ui_automation):
    """Test wait until condition"""
    condition = lambda: True
    result = ui_automation.waits.wait_until(condition, timeout=1)
    assert result is True


def test_init_visual_testing(ui_automation, temp_dir):
    """Test initializing visual testing"""
    # Test with explicit directory
    ui_automation.init_visual_testing(str(temp_dir))
    assert ui_automation._visual_tester is not None
    assert ui_automation._baseline_dir == temp_dir
    
    # Test with default directory
    ui_automation._visual_tester = None
    ui_automation._baseline_dir = None
    ui_automation.init_visual_testing()
    assert ui_automation._visual_tester is not None
    assert ui_automation._baseline_dir.exists()


def test_capture_visual_baseline(ui_automation, temp_dir):
    """Test capturing visual baseline"""
    # Setup mock screenshot
    screenshot = np.zeros((100, 100, 3), dtype=np.uint8)
    ui_automation._backend.capture_screenshot.return_value = screenshot
    
    # Initialize visual testing
    ui_automation.init_visual_testing(str(temp_dir))
    
    # Test capturing baseline
    ui_automation.capture_visual_baseline("test_screen")
    baseline_path = temp_dir / "test_screen.png"
    assert baseline_path.exists()
    
    # Test error when not initialized
    ui_automation._visual_tester = None
    with pytest.raises(ValueError, match="Visual testing not initialized"):
        ui_automation.capture_visual_baseline("test_screen")


def test_compare_visual(ui_automation, temp_dir):
    """Test visual comparison"""
    # Setup mock screenshot
    screenshot = np.zeros((100, 100, 3), dtype=np.uint8)
    ui_automation._backend.capture_screenshot.return_value = screenshot
    
    # Initialize visual testing and capture baseline
    ui_automation.init_visual_testing(str(temp_dir))
    ui_automation.capture_visual_baseline("test_screen")
    
    # Test successful comparison
    result = ui_automation.compare_visual("test_screen")
    assert result is not None
    
    # Test error when not initialized
    ui_automation._visual_tester = None
    with pytest.raises(ValueError, match="Visual testing not initialized"):
        ui_automation.compare_visual("test_screen")


def test_verify_visual_hash(ui_automation, temp_dir):
    """Test visual hash verification"""
    # Setup mock screenshot
    screenshot = np.zeros((100, 100, 3), dtype=np.uint8)
    ui_automation._backend.capture_screenshot.return_value = screenshot
    
    # Initialize visual testing and capture baseline
    ui_automation.init_visual_testing(str(temp_dir))
    ui_automation.capture_visual_baseline("test_screen")
    
    # Test successful hash verification
    result = ui_automation.verify_visual_hash("test_screen")
    assert result is True
    
    # Test error when not initialized
    ui_automation._visual_tester = None
    with pytest.raises(ValueError, match="Visual testing not initialized"):
        ui_automation.verify_visual_hash("test_screen")


@patch('subprocess.Popen')
@patch('psutil.Process')
def test_launch_application(mock_process, mock_popen, ui_automation):
    """Test application launch"""
    # Setup mock process
    mock_proc = MagicMock()
    mock_proc.pid = 12345
    mock_proc.poll.return_value = None  # Process is running
    mock_popen.return_value = mock_proc
    
    # Setup psutil mock
    mock_process_instance = MagicMock()
    mock_process_instance.is_running.return_value = True
    mock_process.return_value = mock_process_instance
    
    # Test successful launch
    app = ui_automation.launch_application("notepad.exe")
    assert app is not None
    assert app.is_running()
    
    # Test launch failure - process terminates immediately
    mock_proc.poll.return_value = 1
    with pytest.raises(RuntimeError, match="Process terminated immediately"):
        ui_automation.launch_application("notepad.exe")
    
    # Test launch failure - process not running
    mock_proc.poll.return_value = None
    mock_process_instance.is_running.return_value = False
    with pytest.raises(RuntimeError, match="Process not running"):
        ui_automation.launch_application("notepad.exe")
    
    # Test launch failure - process not found
    mock_process.side_effect = psutil.NoSuchProcess(12345)
    with pytest.raises(RuntimeError, match="Process PID not found"):
        ui_automation.launch_application("notepad.exe")


@patch('psutil.Process')
def test_attach_to_application(mock_process, ui_automation):
    """Test attaching to application"""
    # Setup mock process
    mock_process_instance = MagicMock()
    mock_process_instance.pid = 12345
    mock_process_instance.is_running.return_value = True
    mock_process.return_value = mock_process_instance
    
    # Test successful attach
    app = ui_automation.attach_to_application(12345)
    assert app is not None
    assert app.is_running()
    
    # Test attach failure - process not running
    mock_process_instance.is_running.return_value = False
    with pytest.raises(RuntimeError, match="Process not running"):
        ui_automation.attach_to_application(12345)
    
    # Test attach failure - process not found
    mock_process.side_effect = psutil.NoSuchProcess(12345)
    with pytest.raises(RuntimeError, match="Process not found"):
        ui_automation.attach_to_application(12345)
