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


def test_for_element_success(element_waits, mock_automation):
    """Test waiting for element to be present"""
    mock_element = MagicMock()
    mock_automation.find_element.side_effect = [None, None, mock_element]
    
    element = element_waits.for_element("id", "test-id", timeout=1)
    assert element == mock_element
    assert mock_automation.find_element.call_count == 3


def test_for_element_timeout(element_waits, mock_automation):
    """Test waiting for element with timeout"""
    mock_automation.find_element.return_value = None
    
    with pytest.raises(WaitTimeout) as exc_info:
        element_waits.for_element("id", "test-id", timeout=0.2)
    assert "Element not found" in str(exc_info.value)


def test_for_element_visible_success(element_waits):
    """Test waiting for element to be visible"""
    mock_element = MagicMock()
    mock_element.is_offscreen = False
    
    assert element_waits.for_element_visible(mock_element, timeout=0.2) is True


def test_for_element_visible_timeout(element_waits):
    """Test waiting for element visibility with timeout"""
    mock_element = MagicMock()
    mock_element.is_offscreen = True
    
    with pytest.raises(WaitTimeout) as exc_info:
        element_waits.for_element_visible(mock_element, timeout=0.2)
    assert "Element not visible" in str(exc_info.value)


def test_for_element_enabled_success(element_waits):
    """Test waiting for element to be enabled"""
    mock_element = MagicMock()
    mock_element.is_enabled = True
    
    assert element_waits.for_element_enabled(mock_element, timeout=0.2) is True


def test_for_element_enabled_timeout(element_waits):
    """Test waiting for element to be enabled with timeout"""
    mock_element = MagicMock()
    mock_element.is_enabled = False
    
    with pytest.raises(WaitTimeout) as exc_info:
        element_waits.for_element_enabled(mock_element, timeout=0.2)
    assert "Element not enabled" in str(exc_info.value)


def test_for_element_property_success(element_waits):
    """Test waiting for element property"""
    mock_element = MagicMock()
    mock_element.get_property.side_effect = ["old-value", "old-value", "new-value"]
    
    assert element_waits.for_element_property(
        mock_element, "test-prop", "new-value", timeout=0.2
    ) is True
    assert mock_element.get_property.call_count == 3


def test_for_element_property_timeout(element_waits):
    """Test waiting for element property with timeout"""
    mock_element = MagicMock()
    mock_element.get_property.return_value = "old-value"
    
    with pytest.raises(WaitTimeout) as exc_info:
        element_waits.for_element_property(
            mock_element, "test-prop", "new-value", timeout=0.2
        )
    assert "Property mismatch" in str(exc_info.value)


def test_for_element_pattern_success(element_waits):
    """Test waiting for element pattern"""
    mock_element = MagicMock()
    mock_element.has_pattern.side_effect = [False, True]
    
    assert element_waits.for_element_pattern(
        mock_element, "test-pattern", timeout=0.2
    ) is True
    assert mock_element.has_pattern.call_count == 2


def test_for_element_pattern_timeout(element_waits):
    """Test waiting for element pattern with timeout"""
    mock_element = MagicMock()
    mock_element.has_pattern.return_value = False
    
    with pytest.raises(WaitTimeout) as exc_info:
        element_waits.for_element_pattern(
            mock_element, "test-pattern", timeout=0.2
        )
    assert "Pattern not supported" in str(exc_info.value)


def test_for_element_text_success(element_waits, mock_automation):
    """Test waiting for element with specific text"""
    mock_element = MagicMock()
    mock_element.text = "test-text"
    mock_automation.find_element.return_value = mock_element
    
    element = element_waits.for_element_text("id", "test-id", "test-text", timeout=0.2)
    assert element == mock_element


def test_for_element_text_timeout(element_waits, mock_automation):
    """Test waiting for element text with timeout"""
    mock_element = MagicMock()
    mock_element.text = "wrong-text"
    mock_automation.find_element.return_value = mock_element
    
    with pytest.raises(WaitTimeout) as exc_info:
        element_waits.for_element_text("id", "test-id", "test-text", timeout=0.2)
    assert "Element text mismatch" in str(exc_info.value)


def test_for_element_contains_text_success(element_waits, mock_automation):
    """Test waiting for element containing text"""
    mock_element = MagicMock()
    mock_element.text = "some test-text here"
    mock_automation.find_element.return_value = mock_element
    
    element = element_waits.for_element_contains_text(
        "id", "test-id", "test-text", timeout=0.2
    )
    assert element == mock_element


def test_for_element_contains_text_timeout(element_waits, mock_automation):
    """Test waiting for element containing text with timeout"""
    mock_element = MagicMock()
    mock_element.text = "wrong content"
    mock_automation.find_element.return_value = mock_element
    
    with pytest.raises(WaitTimeout) as exc_info:
        element_waits.for_element_contains_text(
            "id", "test-id", "test-text", timeout=0.2
        )
    assert "Element text does not contain" in str(exc_info.value)
