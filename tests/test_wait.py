import pytest
from unittest.mock import MagicMock
from pyui_automation.wait import wait_until, ElementWaits
from pyui_automation.exceptions import WaitTimeout


def test_wait_until_success():
    """Test wait_until with successful condition"""
    condition = MagicMock(side_effect=[False, False, True])
    assert wait_until(condition, timeout=1, poll_frequency=0.1) is True
    assert condition.call_count == 3


def test_wait_until_timeout():
    """Test wait_until with timeout"""
    condition = MagicMock(return_value=False)
    with pytest.raises(WaitTimeout) as exc_info:
        wait_until(condition, timeout=0.2, poll_frequency=0.1)
    assert "Timed out after 0.2 seconds" in str(exc_info.value)


def test_wait_until_custom_error():
    """Test wait_until with custom error message"""
    condition = MagicMock(return_value=False)
    error_message = "Custom error message"
    with pytest.raises(WaitTimeout) as exc_info:
        wait_until(condition, timeout=0.2, poll_frequency=0.1, error_message=error_message)
    assert error_message in str(exc_info.value)


def test_wait_until_invalid_params():
    with pytest.raises(Exception):
        wait_until(None)
    with pytest.raises(Exception):
        wait_until(lambda: True, timeout=-1)
    with pytest.raises(Exception):
        wait_until(lambda: True, poll_frequency=-1)
    with pytest.raises(WaitTimeout):
        wait_until(lambda: False, timeout=0)


@pytest.fixture
def mock_automation():
    """Create mock automation session"""
    automation = MagicMock()
    automation.find_element = MagicMock()
    return automation


@pytest.fixture
def element_waits(mock_automation):
    """Create ElementWaits instance with mock automation"""
    return ElementWaits(mock_automation)


def test_wait_until_element_success(element_waits):
    """Test ElementWaits.wait_until with successful condition"""
    condition = MagicMock(side_effect=[False, True])
    assert element_waits.wait_until(condition, timeout=1) is True
    assert condition.call_count == 2


def test_wait_until_element_timeout(element_waits):
    """Test ElementWaits.wait_until with timeout"""
    condition = MagicMock(return_value=False)
    with pytest.raises(WaitTimeout):
        element_waits.wait_until(condition, timeout=0.2)


def test_element_waits_invalid_params(element_waits):
    with pytest.raises(Exception):
        element_waits.for_element_by_object_name(None)
    with pytest.raises(Exception):
        element_waits.for_element_by_widget_type(None)
    with pytest.raises(Exception):
        element_waits.for_element_by_text(None)
    with pytest.raises(Exception):
        element_waits.for_element_by_property(None, None)
    with pytest.raises(Exception):
        element_waits.for_element_by_object_name("")
    with pytest.raises(Exception):
        element_waits.for_element_by_widget_type("")
    with pytest.raises(Exception):
        element_waits.for_element_by_text("")
    with pytest.raises(Exception):
        element_waits.for_element_by_property("", "")


def test_for_element_pattern_invalid(element_waits):
    class Dummy:
        pass
    dummy = Dummy()
    with pytest.raises(Exception):
        element_waits.for_element_pattern(dummy, "pattern")
    class Dummy2:
        def has_pattern(self, name):
            return False
    dummy2 = Dummy2()
    with pytest.raises(WaitTimeout):
        element_waits.for_element_pattern(dummy2, "pattern", timeout=0.1)
    with pytest.raises(Exception):
        element_waits.for_element_pattern(dummy2, None)
    with pytest.raises(Exception):
        element_waits.for_element_pattern(dummy2, 123)
    with pytest.raises(WaitTimeout):
        element_waits.for_element_pattern(dummy2, "pattern", timeout=0)


def test_for_element_by_object_name_success(element_waits, mock_automation):
    mock_element = MagicMock()
    mock_automation.backend.find_element_by_object_name.side_effect = [None, None, mock_element]
    element = element_waits.for_element_by_object_name("test-object", timeout=1)
    assert element == mock_element
    assert mock_automation.backend.find_element_by_object_name.call_count == 3

def test_for_element_by_widget_type_success(element_waits, mock_automation):
    mock_element = MagicMock()
    mock_automation.backend.find_element_by_widget_type.side_effect = [None, mock_element]
    element = element_waits.for_element_by_widget_type("Button", timeout=0.5)
    assert element == mock_element
    assert mock_automation.backend.find_element_by_widget_type.call_count == 2

def test_for_element_by_text_success(element_waits, mock_automation):
    mock_element = MagicMock()
    mock_automation.backend.find_element_by_text.side_effect = [None, None, mock_element]
    element = element_waits.for_element_by_text("OK", timeout=1)
    assert element == mock_element
    assert mock_automation.backend.find_element_by_text.call_count == 3

def test_for_element_by_property_success(element_waits, mock_automation):
    mock_element = MagicMock()
    mock_automation.backend.find_element_by_property.side_effect = [None, mock_element]
    element = element_waits.for_element_by_property("role", "button", timeout=0.5)
    assert element == mock_element
    assert mock_automation.backend.find_element_by_property.call_count == 2
