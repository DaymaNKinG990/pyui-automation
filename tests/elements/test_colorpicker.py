import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.colorpicker import ColorPicker


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session

@pytest.fixture
def mock_colorpicker_element():
    element = MagicMock()
    # Set up default property values
    element.get_property.side_effect = lambda prop: {
        'color': '#FF0000',
        'rgb': (255, 0, 0),
        'alpha': 1.0,
        'expanded': False
    }.get(prop)
    
    # Mock preset color element
    mock_preset = MagicMock()
    element.find_element.side_effect = lambda by, value: mock_preset if value == 'Red' else None
    
    return element

@pytest.fixture
def colorpicker(mock_colorpicker_element, mock_session):
    return ColorPicker(mock_colorpicker_element, mock_session)

def test_init(colorpicker, mock_colorpicker_element, mock_session):
    """Test color picker initialization."""
    assert colorpicker._element == mock_colorpicker_element
    assert colorpicker._session == mock_session

def test_color(colorpicker, mock_colorpicker_element):
    """Test getting color in hex format."""
    assert colorpicker.color == '#FF0000'
    mock_colorpicker_element.get_property.assert_called_with('color')

def test_rgb(colorpicker, mock_colorpicker_element):
    """Test getting color in RGB format."""
    assert colorpicker.rgb == (255, 0, 0)
    mock_colorpicker_element.get_property.assert_called_with('rgb')

def test_alpha(colorpicker, mock_colorpicker_element):
    """Test getting alpha value."""
    assert colorpicker.alpha == 1.0
    mock_colorpicker_element.get_property.assert_called_with('alpha')

def test_is_expanded(colorpicker, mock_colorpicker_element):
    """Test checking if color picker is expanded."""
    assert not colorpicker.is_expanded
    mock_colorpicker_element.get_property.assert_called_with('expanded')

def test_set_color_hex(colorpicker, mock_colorpicker_element):
    """Test setting color with hex value."""
    colorpicker.set_color('#00FF00')
    mock_colorpicker_element.set_property.assert_called_once_with('color', '#00FF00')

def test_set_color_rgb(colorpicker, mock_colorpicker_element):
    """Test setting color with RGB tuple."""
    colorpicker.set_color((0, 255, 0))
    mock_colorpicker_element.set_property.assert_called_once_with('rgb', (0, 255, 0))

def test_set_alpha_valid(colorpicker, mock_colorpicker_element):
    """Test setting valid alpha value."""
    colorpicker.set_alpha(0.5)
    mock_colorpicker_element.set_property.assert_called_once_with('alpha', 0.5)

def test_set_alpha_invalid_low(colorpicker):
    """Test setting alpha value below 0."""
    with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
        colorpicker.set_alpha(-0.1)

def test_set_alpha_invalid_high(colorpicker):
    """Test setting alpha value above 1."""
    with pytest.raises(ValueError, match="Alpha must be between 0 and 1"):
        colorpicker.set_alpha(1.1)

def test_expand_when_collapsed(colorpicker):
    """Test expanding when collapsed."""
    colorpicker.expand()
    colorpicker._element.click.assert_called_once()

def test_expand_when_expanded(colorpicker, mock_colorpicker_element):
    """Test expanding when already expanded."""
    mock_colorpicker_element.get_property.side_effect = lambda prop: {
        'color': '#FF0000',
        'rgb': (255, 0, 0),
        'alpha': 1.0,
        'expanded': True
    }.get(prop)
    
    colorpicker.expand()
    colorpicker._element.click.assert_not_called()

def test_collapse_when_expanded(colorpicker, mock_colorpicker_element):
    """Test collapsing when expanded."""
    mock_colorpicker_element.get_property.side_effect = lambda prop: {
        'color': '#FF0000',
        'rgb': (255, 0, 0),
        'alpha': 1.0,
        'expanded': True
    }.get(prop)
    
    colorpicker.collapse()
    colorpicker._element.click.assert_called_once()

def test_collapse_when_collapsed(colorpicker):
    """Test collapsing when already collapsed."""
    colorpicker.collapse()
    colorpicker._element.click.assert_not_called()

def test_select_preset_found(colorpicker, mock_colorpicker_element):
    """Test selecting existing preset color."""
    colorpicker.select_preset('Red')
    mock_colorpicker_element.find_element.assert_called_with(by="name", value="Red")

def test_select_preset_not_found(colorpicker):
    """Test selecting nonexistent preset color."""
    with pytest.raises(ValueError, match="Preset color 'NonexistentColor' not found"):
        colorpicker.select_preset('NonexistentColor')

def test_wait_until_color_hex(colorpicker, mock_session):
    """Test waiting for specific hex color."""
    assert colorpicker.wait_until_color('#FF0000', timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    with patch.object(colorpicker, 'color', '#FF0000'):
        assert condition_func()
    with patch.object(colorpicker, 'color', '#00FF00'):
        assert not condition_func()

def test_wait_until_color_rgb(colorpicker, mock_session):
    """Test waiting for specific RGB color."""
    assert colorpicker.wait_until_color((255, 0, 0), timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    with patch.object(colorpicker, 'rgb', (255, 0, 0)):
        assert condition_func()
    with patch.object(colorpicker, 'rgb', (0, 255, 0)):
        assert not condition_func()

def test_wait_until_expanded(colorpicker, mock_session):
    """Test waiting for color picker to expand."""
    assert colorpicker.wait_until_expanded(timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    with patch.object(colorpicker, 'is_expanded', True):
        assert condition_func()
    with patch.object(colorpicker, 'is_expanded', False):
        assert not condition_func()

def test_wait_until_collapsed(colorpicker, mock_session):
    """Test waiting for color picker to collapse."""
    assert colorpicker.wait_until_collapsed(timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    with patch.object(colorpicker, 'is_expanded', True):
        assert not condition_func()
    with patch.object(colorpicker, 'is_expanded', False):
        assert condition_func()
