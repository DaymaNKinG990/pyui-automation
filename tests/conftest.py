"""Common test fixtures and configuration"""

import os
import sys
import pytest
from unittest.mock import MagicMock, patch
import numpy as np
from types import ModuleType
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from pyui_automation.elements import UIElement
from pyui_automation.accessibility import AccessibilityChecker
from pyui_automation.application import Application
from pyui_automation.performance import PerformanceMonitor
from pyui_automation.core import AutomationSession

from .data.element_data import (
    DEFAULT_ELEMENT_DATA,
    ALTERNATE_ELEMENT_DATA,
    SCREENSHOT_DATA,
    WINDOW_DATA,
    PROCESS_DATA,
    PERFORMANCE_DATA
)

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
