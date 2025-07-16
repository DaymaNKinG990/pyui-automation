import pytest
from unittest.mock import MagicMock
from pyui_automation.elements.splitter import Splitter, SplitterPanel


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session


@pytest.fixture
def mock_panel_element():
    element = MagicMock()
    element.get_property.side_effect = lambda prop: {
        'width': 100,
        'height': 200,
        'min_width': 50,
        'min_height': 50,
        'max_width': 500,
        'max_height': 500,
        'collapsed': False
    }.get(prop)
    return element


@pytest.fixture
def mock_splitter_element():
    element = MagicMock()
    element.get_property.return_value = 'horizontal'
    
    panel1 = MagicMock()
    panel2 = MagicMock()
    element.find_elements.return_value = [panel1, panel2]
    
    return element


@pytest.fixture
def splitter_panel(mock_panel_element, mock_session):
    return SplitterPanel(mock_panel_element, mock_session)


@pytest.fixture
def splitter(mock_splitter_element, mock_session):
    return Splitter(mock_splitter_element, mock_session)


def test_panel_size(splitter_panel, mock_panel_element):
    """Test getting panel size."""
    assert splitter_panel.size == (100, 200)
    mock_panel_element.get_property.assert_any_call('width')
    mock_panel_element.get_property.assert_any_call('height')


def test_panel_min_size(splitter_panel, mock_panel_element):
    """Test getting panel minimum size."""
    assert splitter_panel.min_size == (50, 50)
    mock_panel_element.get_property.assert_any_call('min_width')
    mock_panel_element.get_property.assert_any_call('min_height')


def test_panel_max_size(splitter_panel, mock_panel_element):
    """Test getting panel maximum size."""
    assert splitter_panel.max_size == (500, 500)
    mock_panel_element.get_property.assert_any_call('max_width')
    mock_panel_element.get_property.assert_any_call('max_height')


def test_panel_is_collapsed(splitter_panel, mock_panel_element):
    """Test checking if panel is collapsed."""
    assert not splitter_panel.is_collapsed
    mock_panel_element.get_property.assert_called_with('collapsed')


def test_splitter_orientation(splitter, mock_splitter_element):
    """Test getting splitter orientation."""
    assert splitter.orientation == 'horizontal'
    mock_splitter_element.get_property.assert_called_with('orientation')


def test_splitter_panels(splitter, mock_splitter_element):
    """Test getting splitter panels."""
    panels = splitter.panels
    assert len(panels) == 2
    assert all(isinstance(panel, SplitterPanel) for panel in panels)
    mock_splitter_element.find_elements.assert_called_with(by='type', value='panel')


def test_splitter_panel_count(splitter):
    """Test getting panel count."""
    assert splitter.panel_count == 2


def test_get_panel_at_valid_index(splitter):
    """Test getting panel at valid index."""
    panel = splitter.get_panel_at(0)
    assert isinstance(panel, SplitterPanel)


def test_get_panel_at_invalid_index(splitter):
    """Test getting panel at invalid index."""
    panel = splitter.get_panel_at(5)
    assert panel is None


def test_resize_panel_invalid_index(splitter):
    with pytest.raises(ValueError):
        splitter.resize_panel(10, 100)

def test_resize_panel_size_out_of_range(splitter, mock_splitter_element, mock_session):
    panel = splitter.get_panel_at(0)
    # Мокаем get_property для min_size/max_size
    panel._element.get_property.side_effect = lambda prop: {
        'min_width': 50, 'min_height': 50, 'max_width': 500, 'max_height': 500, 'width': 100, 'height': 200, 'collapsed': False
    }[prop]
    splitter._element.get_property.return_value = 'vertical'
    with pytest.raises(ValueError):
        splitter.resize_panel(0, 10)
    with pytest.raises(ValueError):
        splitter.resize_panel(0, 1000)

def test_resize_panel_handle_not_found(splitter, mock_splitter_element):
    splitter._element.find_element.return_value = None
    panel = splitter.get_panel_at(0)
    panel._element.get_property.side_effect = lambda prop: {
        'min_width': 50, 'min_height': 50, 'max_width': 500, 'max_height': 500, 'width': 100, 'height': 200, 'collapsed': False
    }[prop]
    splitter._element.get_property.return_value = 'horizontal'
    splitter.resize_panel(0, 100)

def test_resize_panel_drag_by_called(splitter, mock_splitter_element):
    # Мокаем handle с drag_by
    handle = MagicMock()
    splitter._element.find_element.return_value = handle
    splitter._element.get_property.return_value = 'vertical'
    panel = splitter.get_panel_at(0)
    # Текущий размер = 100, хотим 150
    panel._element.get_property.side_effect = lambda prop: {
        'width': 100, 'height': 200, 'min_width': 50, 'min_height': 50, 'max_width': 500, 'max_height': 500, 'collapsed': False
    }[prop]
    splitter.resize_panel(0, 150)
    handle.drag_by.assert_called_with(50, 0)

def test_collapse_panel_invalid_index(splitter):
    with pytest.raises(ValueError):
        splitter.collapse_panel(10)

def test_collapse_panel_button_not_found(splitter, mock_splitter_element):
    panel = splitter.get_panel_at(0)
    panel._element.find_element.return_value = None
    # Не должно быть исключения, просто ничего не происходит
    splitter.collapse_panel(0)

def test_collapse_panel_click_called(splitter, mock_splitter_element):
    panel = splitter.get_panel_at(0)
    button = MagicMock()
    panel._element.find_element.return_value = button
    panel._element.get_property.side_effect = lambda prop: {
        'width': 100, 'height': 200, 'min_width': 50, 'min_height': 50, 'max_width': 500, 'max_height': 500, 'collapsed': False
    }[prop]
    splitter.collapse_panel(0)
    button.click.assert_called_once()

def test_expand_panel_invalid_index(splitter):
    with pytest.raises(ValueError):
        splitter.expand_panel(10)

def test_expand_panel_button_not_found(splitter, mock_splitter_element):
    panel = splitter.get_panel_at(0)
    # panel.is_collapsed = True
    panel._element.get_property.side_effect = lambda prop: {
        'width': 100, 'height': 200, 'min_width': 50, 'min_height': 50, 'max_width': 500, 'max_height': 500, 'collapsed': True
    }[prop]
    panel._element.find_element.return_value = None
    splitter.expand_panel(0)

def test_expand_panel_click_called(splitter, mock_splitter_element):
    panel = splitter.get_panel_at(0)
    button = MagicMock()
    panel._element.get_property.side_effect = lambda prop: {
        'width': 100, 'height': 200, 'min_width': 50, 'min_height': 50, 'max_width': 500, 'max_height': 500, 'collapsed': True
    }[prop]
    panel._element.find_element.return_value = button
    splitter.expand_panel(0)
    button.click.assert_called_once()
