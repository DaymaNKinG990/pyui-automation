import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.slider import Slider


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session

@pytest.fixture
def mock_native_element():
    element = MagicMock()
    # Set up default property values
    element.get_property.side_effect = lambda prop: {
        'value': 50.0,
        'minimum': 0.0,
        'maximum': 100.0,
        'step': 1.0
    }.get(prop)
    return element

@pytest.fixture
def slider(mock_native_element, mock_session):
    return Slider(mock_native_element, mock_session)

def test_init(slider, mock_native_element, mock_session):
    """Test slider initialization."""
    assert slider._element == mock_native_element
    assert slider._session == mock_session

def test_value(slider, mock_native_element):
    """Test getting slider value."""
    assert slider.value == 50.0
    mock_native_element.get_property.assert_called_with('value')

def test_value_deleter(slider):
    """Test deleting slider value (deleter)."""
    slider._value = 42
    del slider.value
    assert slider._value == 0

def test_minimum(slider, mock_native_element):
    """Test getting slider minimum value."""
    assert slider.minimum == 0.0
    mock_native_element.get_property.assert_called_with('minimum')

def test_maximum(slider, mock_native_element):
    """Test getting slider maximum value."""
    assert slider.maximum == 100.0
    mock_native_element.get_property.assert_called_with('maximum')

def test_step(slider, mock_native_element):
    """Test getting slider step value."""
    assert slider.step == 1.0
    mock_native_element.get_property.assert_called_with('step')

def test_set_value_valid(slider, mock_native_element):
    """Test setting valid slider value."""
    slider.set_value(75.0)
    mock_native_element.set_property.assert_called_once_with('value', 75.0)

def test_set_value_below_minimum(slider):
    """Test setting slider value below minimum."""
    with pytest.raises(ValueError, match=r"Value must be between 0.0 and 100.0"):
        slider.set_value(-1.0)

def test_set_value_above_maximum(slider):
    """Test setting slider value above maximum."""
    with pytest.raises(ValueError, match=r"Value must be between 0.0 and 100.0"):
        slider.set_value(101.0)

def test_increment_normal(slider):
    """Test incrementing slider by one step."""
    slider.increment()
    slider._element.set_property.assert_called_once_with('value', 51.0)

def test_increment_near_maximum(slider, mock_native_element):
    """Test incrementing slider near maximum."""
    mock_native_element.get_property.side_effect = lambda prop: {
        'value': 99.5,
        'minimum': 0.0,
        'maximum': 100.0,
        'step': 1.0
    }.get(prop)
    
    slider.increment()
    slider._element.set_property.assert_called_once_with('value', 100.0)

def test_decrement_normal(slider):
    """Test decrementing slider by one step."""
    slider.decrement()
    slider._element.set_property.assert_called_once_with('value', 49.0)

def test_decrement_near_minimum(slider, mock_native_element):
    """Test decrementing slider near minimum."""
    mock_native_element.get_property.side_effect = lambda prop: {
        'value': 0.5,
        'minimum': 0.0,
        'maximum': 100.0,
        'step': 1.0
    }.get(prop)
    
    slider.decrement()
    slider._element.set_property.assert_called_once_with('value', 0.0)

def test_wait_until_value(slider, mock_session):
    """Test waiting for specific value."""
    # Используем double-класс для подмены value
    class SliderMock(Slider):
        def __init__(self, native_element, session, value=50.0):
            super().__init__(native_element, session)
            self._mock_value = value
        @property
        def value(self):
            return self._mock_value
        @value.setter
        def value(self, v):
            self._mock_value = v
        @property
        def step(self):
            return 1.0
    slider_mock = SliderMock(slider._element, slider._session, value=75.0)
    assert slider_mock.wait_until_value(75.0, timeout=5.0)
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    slider_mock.value = 75.0
    assert condition_func()
    slider_mock.value = 70.0
    assert not condition_func()

def test_wait_until_minimum(slider):
    """Test waiting for minimum value."""
    with patch.object(slider, 'wait_until_value') as mock_wait:
        slider.wait_until_minimum(timeout=5.0)
        mock_wait.assert_called_once_with(0.0, 5.0)

def test_wait_until_maximum(slider):
    """Test waiting for maximum value."""
    with patch.object(slider, 'wait_until_value') as mock_wait:
        slider.wait_until_maximum(timeout=5.0)
        mock_wait.assert_called_once_with(100.0, 5.0)
