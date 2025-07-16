import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.text import Text


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
        'text': 'Sample Text',
        'editable': True,
        'font_name': 'Arial',
        'font_size': 12.0,
        'font_weight': 'normal',
        'color': '#000000'
    }.get(prop)
    return element

@pytest.fixture
def text_element(mock_native_element, mock_session):
    return Text(mock_native_element, mock_session)

def test_init(text_element, mock_native_element, mock_session):
    """Test text element initialization."""
    assert text_element._element == mock_native_element
    assert text_element._session == mock_session

def test_text_property(text_element, mock_native_element):
    """Test getting text content."""
    assert text_element.text == 'Sample Text'
    mock_native_element.get_property.assert_called_with('text')

def test_is_editable(text_element, mock_native_element):
    """Test checking if text is editable."""
    assert text_element.is_editable
    mock_native_element.get_property.assert_called_with('editable')

def test_font_name(text_element, mock_native_element):
    """Test getting font name."""
    assert text_element.font_name == 'Arial'
    mock_native_element.get_property.assert_called_with('font_name')

def test_font_size(text_element, mock_native_element):
    """Test getting font size."""
    assert text_element.font_size == 12.0
    mock_native_element.get_property.assert_called_with('font_size')

def test_font_weight(text_element, mock_native_element):
    """Test getting font weight."""
    assert text_element.font_weight == 'normal'
    mock_native_element.get_property.assert_called_with('font_weight')

def test_text_color(text_element, mock_native_element):
    """Test getting text color."""
    assert text_element.text_color == '#000000'
    mock_native_element.get_property.assert_called_with('color')

def test_set_text_when_editable(text_element, mock_native_element):
    """Test setting text when editable."""
    text_element.set_text('New Text')
    mock_native_element.set_property.assert_called_once_with('text', 'New Text')

def test_set_text_when_not_editable(text_element, mock_native_element):
    """Test setting text when not editable."""
    mock_native_element.get_property.side_effect = lambda prop: {
        'text': 'Sample Text',
        'editable': False,
        'font_name': 'Arial',
        'font_size': 12.0,
        'font_weight': 'normal',
        'color': '#000000'
    }.get(prop)
    
    with pytest.raises(ValueError, match="Text element is not editable"):
        text_element.set_text('New Text')
    mock_native_element.set_property.assert_not_called()

def test_append_text_when_editable(text_element, mock_native_element):
    """Test appending text when editable."""
    text_element.append_text(' Additional')
    mock_native_element.set_property.assert_called_once_with('text', 'Sample Text Additional')

def test_append_text_when_not_editable(text_element, mock_native_element):
    """Test appending text when not editable."""
    mock_native_element.get_property.side_effect = lambda prop: {
        'text': 'Sample Text',
        'editable': False,
        'font_name': 'Arial',
        'font_size': 12.0,
        'font_weight': 'normal',
        'color': '#000000'
    }.get(prop)
    
    with pytest.raises(ValueError, match="Text element is not editable"):
        text_element.append_text(' Additional')
    mock_native_element.set_property.assert_not_called()

def test_clear_when_editable(text_element, mock_native_element):
    """Test clearing text when editable."""
    text_element.clear()
    mock_native_element.set_property.assert_called_once_with('text', '')

def test_clear_when_not_editable(text_element, mock_native_element):
    """Test clearing text when not editable."""
    mock_native_element.get_property.side_effect = lambda prop: {
        'text': 'Sample Text',
        'editable': False,
        'font_name': 'Arial',
        'font_size': 12.0,
        'font_weight': 'normal',
        'color': '#000000'
    }.get(prop)
    
    with pytest.raises(ValueError, match="Text element is not editable"):
        text_element.clear()
    mock_native_element.set_property.assert_not_called()

def test_wait_until_text(text_element, mock_session):
    """Test waiting for specific text."""
    assert text_element.wait_until_text('Expected Text', timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition function
    with patch.object(text_element, 'text', 'Expected Text'):
        assert condition_func()
    with patch.object(text_element, 'text', 'Different Text'):
        assert not condition_func()

def test_wait_until_contains(text_element, mock_session):
    """Test waiting for text to contain substring."""
    assert text_element.wait_until_contains('Expected', timeout=5.0)
    
    mock_session.wait_for_condition.assert_called_once()
    condition_func = mock_session.wait_for_condition.call_args[0][0]
    
    # Test condition function
    with patch.object(text_element, 'text', 'Contains Expected Text'):
        assert condition_func()
    with patch.object(text_element, 'text', 'Different Text'):
        assert not condition_func()

def test_text_setter(text_element):
    """Test setting text property directly (setter)."""
    text_element.text = 'Setter Text'
    assert text_element.text == 'Setter Text'

def test_text_deleter(text_element):
    """Test deleting text property (deleter)."""
    text_element.text = 'To be deleted'
    del text_element.text
    assert text_element.text == ''
