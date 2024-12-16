import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.spinner import Spinner


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session


@pytest.fixture
def mock_spinner_element():
    element = MagicMock()
    
    # Set up default property values
    element.get_property.side_effect = lambda prop: {
        'value': 50,
        'minimum': 0,
        'maximum': 100,
        'step': 1,
        'enabled': True
    }.get(prop)
    
    return element


@pytest.fixture
def spinner(mock_spinner_element, mock_session):
    return Spinner(mock_spinner_element, mock_session)


def test_spinner_init(spinner, mock_spinner_element, mock_session):
    """Test spinner initialization."""
    assert spinner._element == mock_spinner_element
    assert spinner._session == mock_session


def test_spinner_value(spinner, mock_spinner_element):
    """Test getting current value."""
    assert spinner.value == 50
    mock_spinner_element.get_property.assert_called_with('value')


def test_spinner_minimum(spinner, mock_spinner_element):
    """Test getting minimum value."""
    assert spinner.minimum == 0
    mock_spinner_element.get_property.assert_called_with('minimum')


def test_spinner_maximum(spinner, mock_spinner_element):
    """Test getting maximum value."""
    assert spinner.maximum == 100
    mock_spinner_element.get_property.assert_called_with('maximum')


def test_spinner_step(spinner, mock_spinner_element):
    """Test getting step value."""
    assert spinner.step == 1
    mock_spinner_element.get_property.assert_called_with('step')


def test_spinner_is_enabled(spinner, mock_spinner_element):
    """Test checking if spinner is enabled."""
    assert spinner.is_enabled
    mock_spinner_element.get_property.assert_called_with('enabled')


def test_spinner_set_value_valid(spinner, mock_spinner_element):
    """Test setting valid value."""
    spinner.set_value(75)
    mock_spinner_element.set_property.assert_called_once_with('value', 75)


def test_spinner_set_value_below_minimum(spinner):
    """Test setting value below minimum."""
    with pytest.raises(ValueError, match="Value must be between 0 and 100"):
        spinner.set_value(-10)


def test_spinner_set_value_above_maximum(spinner):
    """Test setting value above maximum."""
    with pytest.raises(ValueError, match="Value must be between 0 and 100"):
        spinner.set_value(150)


def test_spinner_increment_normal(spinner):
    """Test incrementing value normally."""
    spinner.increment()
    spinner._element.set_property.assert_called_once_with('value', 51)


def test_spinner_increment_at_maximum(spinner, mock_spinner_element):
    """Test incrementing when at maximum."""
    mock_spinner_element.get_property.side_effect = lambda prop: {
        'value': 100,
        'minimum': 0,
        'maximum': 100,
        'step': 1,
        'enabled': True
    }.get(prop)
    
    spinner.increment()
    spinner._element.set_property.assert_not_called()


def test_spinner_increment_near_maximum(spinner, mock_spinner_element):
    """Test incrementing when near maximum."""
    mock_spinner_element.get_property.side_effect = lambda prop: {
        'value': 99,
        'minimum': 0,
        'maximum': 100,
        'step': 2,
        'enabled': True
    }.get(prop)
    
    spinner.increment()
    spinner._element.set_property.assert_called_once_with('value', 100)


def test_spinner_decrement_normal(spinner):
    """Test decrementing value normally."""
    spinner.decrement()
    spinner._element.set_property.assert_called_once_with('value', 49)


def test_spinner_decrement_at_minimum(spinner, mock_spinner_element):
    """Test decrementing when at minimum."""
    mock_spinner_element.get_property.side_effect = lambda prop: {
        'value': 0,
        'minimum': 0,
        'maximum': 100,
        'step': 1,
        'enabled': True
    }.get(prop)
    
    spinner.decrement()
    spinner._element.set_property.assert_not_called()


def test_spinner_decrement_near_minimum(spinner, mock_spinner_element):
    """Test decrementing when near minimum."""
    mock_spinner_element.get_property.side_effect = lambda prop: {
        'value': 1,
        'minimum': 0,
        'maximum': 100,
        'step': 2,
        'enabled': True
    }.get(prop)
    
    spinner.decrement()
    spinner._element.set_property.assert_called_once_with('value', 0)


def test_spinner_wait_until_value(spinner, mock_session):
    """Test waiting for specific value."""
    assert spinner.wait_until_value(75, timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition with different values
    with patch.object(spinner, 'value', 75):
        assert condition_func()
    with patch.object(spinner, 'value', 50):
        assert not condition_func()
    # Test with value within step size
    with patch.object(spinner, 'value', 75.5):
        assert condition_func()


def test_spinner_wait_until_enabled(spinner, mock_session):
    """Test waiting until enabled."""
    assert spinner.wait_until_enabled(timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition with different enabled states
    with patch.object(spinner, 'is_enabled', True):
        assert condition_func()
    with patch.object(spinner, 'is_enabled', False):
        assert not condition_func()


def test_spinner_float_values(spinner, mock_spinner_element):
    """Test spinner with float values."""
    mock_spinner_element.get_property.side_effect = lambda prop: {
        'value': 50.5,
        'minimum': 0.0,
        'maximum': 100.0,
        'step': 0.5,
        'enabled': True
    }.get(prop)
    
    assert spinner.value == 50.5
    assert spinner.step == 0.5
    
    spinner.set_value(75.5)
    spinner._element.set_property.assert_called_once_with('value', 75.5)
    
    spinner.increment()
    spinner._element.set_property.assert_called_with('value', 76.0)
