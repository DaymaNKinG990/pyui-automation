import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.toggle import Toggle


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
        'toggled': False,
        'enabled': True,
        'label': 'Test Toggle'
    }.get(prop)
    return element

@pytest.fixture
def toggle(mock_native_element, mock_session):
    return Toggle(mock_native_element, mock_session)

def test_init(toggle, mock_native_element, mock_session):
    """Test toggle initialization."""
    assert toggle._element == mock_native_element
    assert toggle._session == mock_session

def test_is_on(toggle, mock_native_element):
    """Test checking if toggle is ON."""
    assert not toggle.is_on
    mock_native_element.get_property.assert_called_with('toggled')

def test_is_enabled(toggle, mock_native_element):
    """Test checking if toggle is enabled."""
    assert toggle.is_enabled
    mock_native_element.get_property.assert_called_with('enabled')

def test_label(toggle, mock_native_element):
    """Test getting toggle label."""
    assert toggle.label == 'Test Toggle'
    mock_native_element.get_property.assert_called_with('label')

def test_toggle_when_enabled(toggle):
    """Test toggling when enabled."""
    toggle.toggle()
    toggle._element.click.assert_called_once()

def test_toggle_when_disabled(toggle, mock_native_element):
    """Test toggling when disabled."""
    mock_native_element.get_property.side_effect = lambda prop: {
        'toggled': False,
        'enabled': False,
        'label': 'Test Toggle'
    }.get(prop)
    
    toggle.toggle()
    toggle._element.click.assert_not_called()

def test_turn_on_when_off(toggle):
    """Test turning ON when OFF."""
    toggle.turn_on()
    toggle._element.click.assert_called_once()

def test_turn_on_when_already_on(toggle, mock_native_element):
    """Test turning ON when already ON."""
    mock_native_element.get_property.side_effect = lambda prop: {
        'toggled': True,
        'enabled': True,
        'label': 'Test Toggle'
    }.get(prop)
    
    toggle.turn_on()
    toggle._element.click.assert_not_called()

def test_turn_on_when_disabled(toggle, mock_native_element):
    """Test turning ON when disabled."""
    mock_native_element.get_property.side_effect = lambda prop: {
        'toggled': False,
        'enabled': False,
        'label': 'Test Toggle'
    }.get(prop)
    
    toggle.turn_on()
    toggle._element.click.assert_not_called()

def test_turn_off_when_on(toggle, mock_native_element):
    """Test turning OFF when ON."""
    mock_native_element.get_property.side_effect = lambda prop: {
        'toggled': True,
        'enabled': True,
        'label': 'Test Toggle'
    }.get(prop)
    
    toggle.turn_off()
    toggle._element.click.assert_called_once()

def test_turn_off_when_already_off(toggle):
    """Test turning OFF when already OFF."""
    toggle.turn_off()
    toggle._element.click.assert_not_called()

def test_turn_off_when_disabled(toggle, mock_native_element):
    """Test turning OFF when disabled."""
    mock_native_element.get_property.side_effect = lambda prop: {
        'toggled': True,
        'enabled': False,
        'label': 'Test Toggle'
    }.get(prop)
    
    toggle.turn_off()
    toggle._element.click.assert_not_called()

def test_wait_until_on(toggle, mock_session):
    """Test waiting for ON state."""
    assert toggle.wait_until_on(timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition function
    with patch.object(toggle, 'is_on', True):
        assert condition_func()
    with patch.object(toggle, 'is_on', False):
        assert not condition_func()

def test_wait_until_off(toggle, mock_session):
    """Test waiting for OFF state."""
    assert toggle.wait_until_off(timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition function
    with patch.object(toggle, 'is_on', True):
        assert not condition_func()
    with patch.object(toggle, 'is_on', False):
        assert condition_func()

def test_wait_until_enabled(toggle, mock_session):
    """Test waiting for enabled state."""
    assert toggle.wait_until_enabled(timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition function
    with patch.object(toggle, 'is_enabled', True):
        assert condition_func()
    with patch.object(toggle, 'is_enabled', False):
        assert not condition_func()
