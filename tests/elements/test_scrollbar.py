import pytest
from unittest.mock import MagicMock
from pyui_automation.elements.scrollbar import ScrollBar


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session


@pytest.fixture
def mock_viewport():
    viewport = MagicMock()
    viewport.get_property.side_effect = lambda prop: {
        'width': 800,
        'height': 600
    }.get(prop)
    return viewport


@pytest.fixture
def mock_scrollbar_element(mock_viewport):
    element = MagicMock()
    
    # Set up default property values
    element.get_property.side_effect = lambda prop: {
        'orientation': 'vertical',
        'value': 50.0,
        'min': 0.0,
        'max': 100.0,
        'step': 1.0,
        'page': 10.0,
        'enabled': True
    }.get(prop)
    
    # Set up viewport finding
    element.find_element.return_value = mock_viewport
    
    return element


@pytest.fixture
def scrollbar(mock_scrollbar_element, mock_session):
    return ScrollBar(mock_scrollbar_element, mock_session)


def test_scrollbar_init(scrollbar, mock_scrollbar_element, mock_session):
    """Test scrollbar initialization."""
    assert scrollbar._element == mock_scrollbar_element
    assert scrollbar._session == mock_session


def test_scrollbar_orientation(scrollbar, mock_scrollbar_element):
    """Test getting scrollbar orientation."""
    assert scrollbar.orientation == 'vertical'
    mock_scrollbar_element.get_property.assert_called_with('orientation')


def test_scrollbar_value(scrollbar, mock_scrollbar_element):
    """Test getting current scroll position."""
    assert scrollbar.value == 50.0
    mock_scrollbar_element.get_property.assert_called_with('value')


def test_scrollbar_min_value(scrollbar, mock_scrollbar_element):
    """Test getting minimum scroll value."""
    assert scrollbar.min_value == 0.0
    mock_scrollbar_element.get_property.assert_called_with('min')


def test_scrollbar_max_value(scrollbar, mock_scrollbar_element):
    """Test getting maximum scroll value."""
    assert scrollbar.max_value == 100.0
    mock_scrollbar_element.get_property.assert_called_with('max')


def test_scrollbar_step_size(scrollbar, mock_scrollbar_element):
    """Test getting step size."""
    assert scrollbar.step_size == 1.0
    mock_scrollbar_element.get_property.assert_called_with('step')


def test_scrollbar_page_size(scrollbar, mock_scrollbar_element):
    """Test getting page size."""
    assert scrollbar.page_size == 10.0
    mock_scrollbar_element.get_property.assert_called_with('page')


def test_scrollbar_is_enabled(scrollbar, mock_scrollbar_element):
    """Test checking if scrollbar is enabled."""
    assert scrollbar.is_enabled
    mock_scrollbar_element.get_property.assert_called_with('enabled')


def test_scrollbar_viewport_size(scrollbar, mock_scrollbar_element, mock_viewport):
    """Test getting viewport size."""
    width, height = scrollbar.viewport_size
    assert width == 800
    assert height == 600
    mock_scrollbar_element.find_element.assert_called_with(by='type', value='viewport')


def test_scrollbar_viewport_size_not_found(scrollbar, mock_scrollbar_element):
    """Test getting viewport size when viewport not found."""
    mock_scrollbar_element.find_element.return_value = None
    width, height = scrollbar.viewport_size
    assert width == 0
    assert height == 0


def test_scrollbar_scroll_to_valid(scrollbar, mock_scrollbar_element):
    """Test scrolling to valid position."""
    scrollbar.scroll_to(75.0)
    mock_scrollbar_element.set_property.assert_called_once_with('value', 75.0)


def test_scrollbar_scroll_to_invalid(scrollbar):
    """Test scrolling to invalid position."""
    with pytest.raises(ValueError, match="Value -10.0 out of range"):
        scrollbar.scroll_to(-10.0)
    
    with pytest.raises(ValueError, match="Value 150.0 out of range"):
        scrollbar.scroll_to(150.0)


def test_scrollbar_scroll_to_start(scrollbar):
    """Test scrolling to start position."""
    scrollbar.scroll_to_start()
    scrollbar._element.set_property.assert_called_once_with('value', 0.0)


def test_scrollbar_scroll_to_end(scrollbar):
    """Test scrolling to end position."""
    scrollbar.scroll_to_end()
    scrollbar._element.set_property.assert_called_once_with('value', 100.0)


def test_scrollbar_scroll_by(scrollbar):
    """Test scrolling by relative amount."""
    scrollbar.scroll_by(25.0)
    scrollbar._element.set_property.assert_called_once_with('value', 75.0)


def test_scrollbar_scroll_by_clamped(scrollbar):
    """Test scrolling by amount that would exceed limits."""
    # Test exceeding maximum
    scrollbar.scroll_by(60.0)  # From 50.0 would be 110.0, should clamp to 100.0
    scrollbar._element.set_property.assert_called_with('value', 100.0)
    
    # Test exceeding minimum
    scrollbar.scroll_by(-60.0)  # From 50.0 would be -10.0, should clamp to 0.0
    scrollbar._element.set_property.assert_called_with('value', 0.0)


def test_scrollbar_scroll_step_forward(scrollbar):
    """Test scrolling forward by one step."""
    scrollbar.scroll_step_forward()
    scrollbar._element.set_property.assert_called_once_with('value', 51.0)


def test_scrollbar_scroll_step_backward(scrollbar):
    """Test scrolling backward by one step."""
    scrollbar.scroll_step_backward()
    scrollbar._element.set_property.assert_called_once_with('value', 49.0)


def test_scrollbar_scroll_page_forward(scrollbar):
    """Test scrolling forward by one page."""
    scrollbar.scroll_page_forward()
    scrollbar._element.set_property.assert_called_once_with('value', 60.0)


def test_scrollbar_scroll_page_backward(scrollbar):
    """Test scrolling backward by one page."""
    scrollbar.scroll_page_backward()
    scrollbar._element.set_property.assert_called_once_with('value', 40.0)


def test_scrollbar_is_at_start(scrollbar, mock_scrollbar_element):
    """Test checking if scrolled to start."""
    mock_scrollbar_element.get_property.side_effect = lambda prop: {
        'value': 0.0,
        'min': 0.0,
        'max': 100.0
    }.get(prop)
    
    assert scrollbar.is_at_start()


def test_scrollbar_is_at_end(scrollbar, mock_scrollbar_element):
    """Test checking if scrolled to end."""
    mock_scrollbar_element.get_property.side_effect = lambda prop: {
        'value': 100.0,
        'min': 0.0,
        'max': 100.0
    }.get(prop)
    
    assert scrollbar.is_at_end()


class ScrollBarMock(ScrollBar):
    def __init__(self, native_element, session, value=50.0):
        super().__init__(native_element, session)
        self._mock_value = value
    @property
    def value(self):
        return self._mock_value

def test_scrollbar_wait_until_value(mock_scrollbar_element, mock_session):
    """Test waiting for specific scroll value (без patch.object, через double)."""
    scrollbar = ScrollBarMock(mock_scrollbar_element, mock_session, value=75.0)
    assert scrollbar.wait_until_value(75.0, timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    scrollbar._mock_value = 75.0
    assert condition_func()
    scrollbar._mock_value = 50.0
    assert not condition_func()
    scrollbar._mock_value = 75.0005
    assert condition_func()

def test_scrollbar_wait_until_at_start(mock_scrollbar_element, mock_session):
    """Test waiting until scrolled to start (без patch.object, через double)."""
    scrollbar = ScrollBarMock(mock_scrollbar_element, mock_session, value=0.0)
    assert scrollbar.wait_until_at_start(timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    scrollbar._mock_value = 0.0
    assert condition_func()
    scrollbar._mock_value = 50.0
    assert not condition_func()

def test_scrollbar_wait_until_at_end(mock_scrollbar_element, mock_session):
    """Test waiting until scrolled to end (без patch.object, через double)."""
    scrollbar = ScrollBarMock(mock_scrollbar_element, mock_session, value=100.0)
    assert scrollbar.wait_until_at_end(timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    scrollbar._mock_value = 100.0
    assert condition_func()
    scrollbar._mock_value = 50.0
    assert not condition_func()
