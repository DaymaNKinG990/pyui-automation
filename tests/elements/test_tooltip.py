import pytest
from unittest.mock import MagicMock
from pyui_automation.elements.tooltip import Tooltip


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session


@pytest.fixture
def mock_tooltip_element():
    element = MagicMock()
    element.get_property.side_effect = lambda prop: {
        'text': 'Tooltip Text',
        'visible': True,
        'x': 100,
        'y': 200,
        'width': 150,
        'height': 50
    }.get(prop)
    return element


@pytest.fixture
def tooltip(mock_tooltip_element, mock_session):
    return Tooltip(mock_tooltip_element, mock_session)


def test_tooltip_text(tooltip, mock_tooltip_element):
    """Test getting tooltip text."""
    assert tooltip.text == 'Tooltip Text'
    mock_tooltip_element.get_property.assert_called_with('text')


def test_tooltip_is_visible(tooltip, mock_tooltip_element):
    """Test checking if tooltip is visible."""
    assert tooltip.is_visible
    mock_tooltip_element.get_property.assert_called_with('visible')


def test_tooltip_position(tooltip, mock_tooltip_element):
    """Test getting tooltip position."""
    assert tooltip.position == (100, 200)
    mock_tooltip_element.get_property.assert_any_call('x')
    mock_tooltip_element.get_property.assert_any_call('y')


def test_tooltip_size(tooltip, mock_tooltip_element):
    """Test getting tooltip size."""
    assert tooltip.size == (150, 50)
    mock_tooltip_element.get_property.assert_any_call('width')
    mock_tooltip_element.get_property.assert_any_call('height')


def test_tooltip_wait_until_visible(tooltip, mock_session):
    """Test waiting until tooltip becomes visible."""
    assert tooltip.wait_until_visible(timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    # Test the condition function
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    tooltip._element.get_property.side_effect = lambda prop: True if prop == 'visible' else None
    assert condition_func()
    tooltip._element.get_property.side_effect = lambda prop: False if prop == 'visible' else None
    assert not condition_func()


def test_tooltip_wait_until_hidden(tooltip, mock_session):
    """Test waiting until tooltip becomes hidden."""
    assert tooltip.wait_until_hidden(timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    # Test the condition function
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    tooltip._element.get_property.side_effect = lambda prop: False if prop == 'visible' else None
    assert condition_func()
    tooltip._element.get_property.side_effect = lambda prop: True if prop == 'visible' else None
    assert not condition_func()


def test_tooltip_wait_until_text(tooltip, mock_session):
    """Test waiting until tooltip text matches expected."""
    assert tooltip.wait_until_text('Expected Text', timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    # Test the condition function
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    tooltip._element.get_property.side_effect = lambda prop: 'Expected Text' if prop == 'text' else None
    assert condition_func()
    tooltip._element.get_property.side_effect = lambda prop: 'Different Text' if prop == 'text' else None
    assert not condition_func()


def test_text_setter():
    tooltip = Tooltip(MagicMock(), MagicMock())
    tooltip.text = 'Setter Text'
    tooltip._element.set_property.assert_called_once_with('text', 'Setter Text')

def test_is_visible_setter():
    tooltip = Tooltip(MagicMock(), MagicMock())
    tooltip.show = MagicMock()
    tooltip.hide = MagicMock()
    # Сначала невидим, делаем видимым
    tooltip._is_visible = False
    setattr(tooltip, '_is_visible', False)
    tooltip.is_visible = True
    tooltip.show.assert_called_once()
    # Теперь видим, делаем невидимым
    tooltip._is_visible = True
    setattr(tooltip, '_is_visible', True)
    tooltip.is_visible = False
    tooltip.hide.assert_called_once()

def test_position_setter():
    tooltip = Tooltip(MagicMock(), MagicMock())
    tooltip.position = (10, 20)
    tooltip._element.set_property.assert_any_call('x', 10)
    tooltip._element.set_property.assert_any_call('y', 20)

def test_size_setter():
    tooltip = Tooltip(MagicMock(), MagicMock())
    tooltip.size = (123, 456)
    tooltip._element.set_property.assert_any_call('width', 123)
    tooltip._element.set_property.assert_any_call('height', 456)

def test_show_when_already_visible():
    tooltip = Tooltip(MagicMock(), MagicMock())
    tooltip._element.get_property.return_value = True
    tooltip._element.set_property.reset_mock()
    tooltip.show()
    tooltip._element.set_property.assert_not_called()

def test_hide_when_already_hidden():
    tooltip = Tooltip(MagicMock(), MagicMock())
    tooltip._element.get_property.return_value = False
    tooltip._element.set_property.reset_mock()
    tooltip.hide()
    tooltip._element.set_property.assert_not_called()

def test_wait_until_visible_error(monkeypatch):
    session = MagicMock()
    session.wait_for_condition.side_effect = RuntimeError("fail")
    tooltip = Tooltip(MagicMock(), session)
    with pytest.raises(RuntimeError):
        tooltip.wait_until_visible()

def test_wait_until_hidden_error(monkeypatch):
    session = MagicMock()
    session.wait_for_condition.side_effect = RuntimeError("fail")
    tooltip = Tooltip(MagicMock(), session)
    with pytest.raises(RuntimeError):
        tooltip.wait_until_hidden()

def test_wait_until_text_error(monkeypatch):
    session = MagicMock()
    session.wait_for_condition.side_effect = RuntimeError("fail")
    tooltip = Tooltip(MagicMock(), session)
    with pytest.raises(RuntimeError):
        tooltip.wait_until_text("text")

def test_position_property_invalid():
    element = MagicMock()
    element.get_property.side_effect = lambda prop: None
    tooltip = Tooltip(element, MagicMock())
    assert tooltip.position == (None, None)

def test_size_property_invalid():
    element = MagicMock()
    element.get_property.side_effect = lambda prop: None
    tooltip = Tooltip(element, MagicMock())
    assert tooltip.size == (None, None)
