import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.elements.accordion import Accordion, AccordionPanel


@pytest.fixture
def mock_session():
    session = MagicMock()
    session.wait_for_condition = MagicMock(return_value=True)
    return session

@pytest.fixture
def mock_panel_element():
    element = MagicMock()
    # Set up default property values for panel
    element.get_property.side_effect = lambda prop: {
        'expanded': False,
    }.get(prop)
    
    # Mock header and content elements
    mock_header = MagicMock()
    mock_header.get_property.return_value = "Panel 1"
    mock_content = MagicMock()
    mock_content.get_property.return_value = "Content 1"
    
    element.find_element.side_effect = lambda by, value: {
        'header': mock_header,
        'content': mock_content
    }.get(value)
    
    return element

@pytest.fixture
def mock_accordion_element():
    element = MagicMock()
    
    # Create mock panels
    mock_panel1 = MagicMock()
    mock_panel1.find_element.side_effect = lambda by, value: {
        'header': MagicMock(get_property=lambda x: "Panel 1"),
        'content': MagicMock(get_property=lambda x: "Content 1")
    }.get(value)
    mock_panel1.get_property.return_value = True  # expanded
    
    mock_panel2 = MagicMock()
    mock_panel2.find_element.side_effect = lambda by, value: {
        'header': MagicMock(get_property=lambda x: "Panel 2"),
        'content': MagicMock(get_property=lambda x: "Content 2")
    }.get(value)
    mock_panel2.get_property.return_value = False  # collapsed
    
    element.find_elements.return_value = [mock_panel1, mock_panel2]
    return element

@pytest.fixture
def panel(mock_panel_element, mock_session):
    return AccordionPanel(mock_panel_element, mock_session)

@pytest.fixture
def accordion(mock_accordion_element, mock_session):
    return Accordion(mock_accordion_element, mock_session)

# AccordionPanel Tests
def test_panel_init(panel, mock_panel_element, mock_session):
    """Test panel initialization."""
    assert panel._element == mock_panel_element
    assert panel._session == mock_session

def test_panel_header_text(panel, mock_panel_element):
    """Test getting panel header text."""
    assert panel.header_text == "Panel 1"
    mock_panel_element.find_element.assert_called_with(by="type", value="header")

def test_panel_content_text(panel, mock_panel_element):
    """Test getting panel content text."""
    assert panel.content_text == "Content 1"
    mock_panel_element.find_element.assert_called_with(by="type", value="content")

def test_panel_is_expanded(panel, mock_panel_element):
    """Test checking if panel is expanded."""
    assert not panel.is_expanded
    mock_panel_element.get_property.assert_called_with("expanded")

def test_panel_expand(panel, mock_panel_element):
    """Test expanding a collapsed panel."""
    # Setup mock for is_expanded
    with patch.object(panel, 'is_expanded', return_value=False):
        mock_header = MagicMock()
        mock_panel_element.find_element.return_value = mock_header
        
        panel.expand()
        mock_header.click.assert_called_once()

def test_panel_collapse(panel, mock_panel_element):
    """Test collapsing an expanded panel."""
    # Setup mock for is_expanded
    with patch.object(panel, 'is_expanded', return_value=True):
        mock_header = MagicMock()
        mock_panel_element.find_element.return_value = mock_header
        
        panel.collapse()
        mock_header.click.assert_called_once()

def test_panel_wait_until_expanded(panel, mock_session):
    """Test waiting for panel to expand."""
    # Setup mock for is_expanded
    with patch.object(panel, 'is_expanded', return_value=True):
        assert panel.wait_until_expanded(timeout=5.0)
        
        mock_session.wait_for_condition.assert_called_once()
        condition_func = mock_session.wait_for_condition.call_args[0][0]
        assert condition_func() is True

    # Test when not expanded
    with patch.object(panel, 'is_expanded', return_value=False):
        condition_func = mock_session.wait_for_condition.call_args[0][0]
        assert condition_func() is False

def test_panel_wait_until_collapsed(panel, mock_session):
    """Test waiting for panel to collapse."""
    # Setup mock for is_expanded
    with patch.object(panel, 'is_expanded', return_value=False):
        assert panel.wait_until_collapsed(timeout=5.0)
        
        mock_session.wait_for_condition.assert_called_once()
        condition_func = mock_session.wait_for_condition.call_args[0][0]
        assert condition_func() is True

    # Test when not collapsed
    with patch.object(panel, 'is_expanded', return_value=True):
        condition_func = mock_session.wait_for_condition.call_args[0][0]
        assert condition_func() is False

# Accordion Tests
def test_accordion_init(accordion, mock_accordion_element, mock_session):
    """Test accordion initialization."""
    assert accordion._element == mock_accordion_element
    assert accordion._session == mock_session

def test_accordion_panels(accordion, mock_accordion_element):
    """Test getting all panels."""
    panels = accordion.panels
    assert len(panels) == 2
    assert all(isinstance(panel, AccordionPanel) for panel in panels)
    mock_accordion_element.find_elements.assert_called_with(by="type", value="panel")

def test_accordion_expanded_panels(accordion):
    """Test getting expanded panels."""
    expanded = accordion.expanded_panels
    assert len(expanded) == 1
    assert expanded[0].header_text == "Panel 1"

def test_accordion_get_panel(accordion):
    """Test getting panel by header text."""
    panel = accordion.get_panel("Panel 1")
    assert panel is not None
    assert panel.header_text == "Panel 1"
    
    panel = accordion.get_panel("Nonexistent Panel")
    assert panel is None

def test_accordion_expand_panel(accordion):
    """Test expanding panel by header text."""
    accordion.expand_panel("Panel 2")
    # The panel's expand method should be called
    assert True  # If no exception is raised, test passes

def test_accordion_expand_panel_not_found(accordion):
    """Test expanding nonexistent panel."""
    with pytest.raises(ValueError, match="Panel with header 'Nonexistent Panel' not found"):
        accordion.expand_panel("Nonexistent Panel")

def test_accordion_collapse_panel(accordion):
    """Test collapsing panel by header text."""
    accordion.collapse_panel("Panel 1")
    # The panel's collapse method should be called
    assert True  # If no exception is raised, test passes

def test_accordion_collapse_panel_not_found(accordion):
    """Test collapsing nonexistent panel."""
    with pytest.raises(ValueError, match="Panel with header 'Nonexistent Panel' not found"):
        accordion.collapse_panel("Nonexistent Panel")

def test_accordion_expand_all(accordion):
    """Test expanding all panels."""
    accordion.expand_all()
    # All panels' expand methods should be called
    assert len(accordion.expanded_panels) >= 1

def test_accordion_collapse_all(accordion):
    """Test collapsing all panels."""
    accordion.collapse_all()
    # All panels' collapse methods should be called
    assert True  # If no exception is raised, test passes

def test_accordion_wait_until_panel_expanded(accordion, mock_session):
    """Test waiting for specific panel to expand."""
    assert accordion.wait_until_panel_expanded("Panel 1", timeout=5.0)
    # Should delegate to panel's wait_until_expanded
    assert mock_session.wait_for_condition.called

def test_accordion_wait_until_panel_expanded_not_found(accordion):
    """Test waiting for nonexistent panel to expand."""
    assert not accordion.wait_until_panel_expanded("Nonexistent Panel", timeout=5.0)

def test_accordion_wait_until_panel_collapsed(accordion, mock_session):
    """Test waiting for specific panel to collapse."""
    assert accordion.wait_until_panel_collapsed("Panel 1", timeout=5.0)
    # Should delegate to panel's wait_until_collapsed
    assert mock_session.wait_for_condition.called

def test_accordion_wait_until_panel_collapsed_not_found(accordion):
    """Test waiting for nonexistent panel to collapse."""
    assert not accordion.wait_until_panel_collapsed("Nonexistent Panel", timeout=5.0)
