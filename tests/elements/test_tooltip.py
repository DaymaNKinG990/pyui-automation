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
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(tooltip, 'is_visible', True)
        assert condition_func()
        mp.setattr(tooltip, 'is_visible', False)
        assert not condition_func()


def test_tooltip_wait_until_hidden(tooltip, mock_session):
    """Test waiting until tooltip becomes hidden."""
    assert tooltip.wait_until_hidden(timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    
    # Test the condition function
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(tooltip, 'is_visible', False)
        assert condition_func()
        mp.setattr(tooltip, 'is_visible', True)
        assert not condition_func()


def test_tooltip_wait_until_text(tooltip, mock_session):
    """Test waiting until tooltip text matches expected."""
    assert tooltip.wait_until_text('Expected Text', timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    
    # Test the condition function
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    with pytest.MonkeyPatch.context() as mp:
        mp.setattr(tooltip, 'text', 'Expected Text')
        assert condition_func()
        mp.setattr(tooltip, 'text', 'Different Text')
        assert not condition_func()
