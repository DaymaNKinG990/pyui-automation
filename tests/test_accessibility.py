import pytest
from unittest.mock import MagicMock
from pyui_automation.accessibility import AccessibilityChecker


@pytest.fixture
def mock_element():
    """Create a mock UI element for testing"""
    element = MagicMock()
    element.id = "test-id"
    element.name = "test-button"
    element.role = "button"
    element.is_enabled.return_value = True
    element.is_keyboard_accessible.return_value = True
    element.get_attribute = MagicMock(return_value=None)
    element.get_location.return_value = (0, 0)
    element.get_size.return_value = (100, 30)
    return element

@pytest.fixture
def accessibility_checker():
    """Create AccessibilityChecker instance"""
    checker = AccessibilityChecker()
    checker._is_image_element = MagicMock(return_value=True)
    return checker

def test_check_element_alt_text(accessibility_checker, mock_element):
    """Test checking element for alternative text"""
    mock_element.get_attribute.return_value = None
    accessibility_checker.check_element(mock_element)
    violations = accessibility_checker.violations
    assert any(v.rule == "missing_alt_text" for v in violations)

def test_check_element_color_contrast(accessibility_checker, mock_element):
    """Test checking element for color contrast"""
    mock_element.text = "Test Text"
    mock_element.get_attribute.side_effect = lambda x: {
        "color": "#000000",
        "background-color": "#FFFFFF"
    }.get(x)
    
    accessibility_checker._get_element_color = MagicMock(side_effect=[
        (0, 0, 0),      # Foreground color (black)
        (255, 255, 255) # Background color (white)
    ])
    
    accessibility_checker.check_element(mock_element)
    violations = accessibility_checker.violations
    assert not any(v.rule == "insufficient_contrast" for v in violations)

def test_check_element_keyboard_accessibility(accessibility_checker, mock_element):
    """Test checking element for keyboard accessibility"""
    mock_element.is_keyboard_accessible.return_value = False
    accessibility_checker.check_element(mock_element)
    violations = accessibility_checker.violations
    assert any(v.rule == "not_keyboard_accessible" for v in violations)

def test_check_element_aria_role(accessibility_checker, mock_element):
    """Test checking element for valid ARIA role"""
    mock_element.role = "invalid_role"
    accessibility_checker.check_element(mock_element)
    violations = accessibility_checker.violations
    assert any(v.rule == "invalid_aria_role" for v in violations)

def test_check_application(accessibility_checker, mock_element):
    """Test checking entire application"""
    mock_element.find_all = MagicMock(return_value=[mock_element])
    accessibility_checker.check_application(mock_element)
    assert len(accessibility_checker.violations) > 0

def test_generate_report(accessibility_checker, mock_element, tmp_path):
    """Test generating accessibility report"""
    report_path = tmp_path / "report.html"
    mock_element.get_attribute.return_value = None
    accessibility_checker.check_element(mock_element)
    accessibility_checker.generate_report(report_path)
    assert report_path.exists()
    assert report_path.stat().st_size > 0

def test_color_contrast_calculation(accessibility_checker):
    """Test color contrast ratio calculation"""
    ratio = accessibility_checker._calculate_contrast_ratio(
        (0, 0, 0),       # Black
        (255, 255, 255)  # White
    )
    assert ratio > 20  # White on black should have very high contrast

def test_get_all_elements(accessibility_checker, mock_element):
    """Test getting all elements in application"""
    mock_element.find_all = MagicMock(return_value=[mock_element])
    elements = accessibility_checker._get_all_elements(mock_element)
    assert len(elements) == 1
    assert elements[0] == mock_element

def test_is_interactive(mock_element):
    """Test detecting interactive elements"""
    mock_element.role = "button"
    assert AccessibilityChecker._is_interactive(mock_element)
    mock_element.role = "text"
    assert not AccessibilityChecker._is_interactive(mock_element)

def test_has_valid_role(mock_element):
    """Test validating ARIA roles"""
    mock_element.role = "button"
    assert AccessibilityChecker._has_valid_role(mock_element)
    mock_element.role = "invalid_role"
    assert not AccessibilityChecker._has_valid_role(mock_element)

def test_get_element_color_hex(accessibility_checker, mock_element):
    """Test parsing hex color values"""
    mock_element.get_attribute.side_effect = lambda x: {
        "color": "#FF0000",
        "background-color": "#00FF00"
    }.get(x)
    
    color = accessibility_checker._get_element_color(mock_element, "color")
    assert color == (255, 0, 0)
    
    bg_color = accessibility_checker._get_element_color(mock_element, "background-color")
    assert bg_color == (0, 255, 0)

def test_get_element_color_rgb(accessibility_checker, mock_element):
    """Test parsing RGB color values"""
    mock_element.get_attribute.side_effect = lambda x: {
        "color": "rgb(255, 0, 0)",
        "background-color": "rgb(0, 255, 0)"
    }.get(x)
    
    color = accessibility_checker._get_element_color(mock_element, "color")
    assert color == (255, 0, 0)
    
    bg_color = accessibility_checker._get_element_color(mock_element, "background-color")
    assert bg_color == (0, 255, 0)

def test_get_element_color_named(accessibility_checker, mock_element):
    """Test parsing named colors"""
    mock_element.get_attribute.side_effect = lambda x: {
        "color": "red",
        "background-color": "green"
    }.get(x)
    
    color = accessibility_checker._get_element_color(mock_element, "color")
    assert color == (255, 0, 0)
    
    bg_color = accessibility_checker._get_element_color(mock_element, "background-color")
    assert bg_color == (0, 128, 0)

def test_get_luminance(accessibility_checker):
    """Test luminance calculation"""
    test_colors = [
        ((0, 0, 0), 0.0),       # Black
        ((255, 255, 255), 1.0), # White
        ((255, 0, 0), 0.2126),  # Red
        ((0, 255, 0), 0.7152),  # Green
        ((0, 0, 255), 0.0722)   # Blue
    ]
    
    for color, expected in test_colors:
        luminance = accessibility_checker._get_luminance(color)
        assert abs(luminance - expected) < 0.01

def test_check_element_edge_cases(accessibility_checker, mock_element):
    """Test element checking with edge cases"""
    # Test with empty text
    mock_element.text = ""
    mock_element.get_attribute.return_value = None
    accessibility_checker.check_element(mock_element)
    
    # Test with None values
    mock_element.text = None
    mock_element.role = None
    accessibility_checker.check_element(mock_element)
    
    # Test with special characters
    mock_element.text = "Test\nText\t"
    accessibility_checker.check_element(mock_element)

def test_check_application_empty(accessibility_checker):
    """Test checking application with no elements"""
    mock_root = MagicMock()
    mock_root.find_all = MagicMock(return_value=[])
    accessibility_checker.check_application(mock_root)
    assert len(accessibility_checker.violations) == 0

def test_check_application_no_root(accessibility_checker):
    """Test checking application with no root element"""
    accessibility_checker.check_application(None)
    assert len(accessibility_checker.violations) == 0

def test_generate_report_no_violations(accessibility_checker, tmp_path):
    """Test generating report with no violations"""
    report_path = tmp_path / "report.html"
    accessibility_checker.generate_report(report_path)
    assert report_path.exists()
    assert report_path.stat().st_size > 0

def test_color_parsing_errors(accessibility_checker, mock_element):
    """Test color parsing error handling"""
    # Test invalid hex color
    mock_element.get_attribute.return_value = "#XYZ"
    color = accessibility_checker._get_element_color(mock_element, "color")
    assert color == (0, 0, 0)  # Default to black
    
    # Test invalid rgb format
    mock_element.get_attribute.return_value = "rgb(invalid)"
    color = accessibility_checker._get_element_color(mock_element, "color")
    assert color == (0, 0, 0)
    
    # Test invalid color name
    mock_element.get_attribute.return_value = "not_a_color"
    color = accessibility_checker._get_element_color(mock_element, "color")
    assert color == (0, 0, 0)

def test_contrast_ratio_edge_cases(accessibility_checker):
    """Test contrast ratio calculation edge cases"""
    # Same color (no contrast)
    ratio = accessibility_checker._calculate_contrast_ratio(
        (128, 128, 128),
        (128, 128, 128)
    )
    assert ratio == 1.0
    
    # Maximum contrast
    ratio = accessibility_checker._calculate_contrast_ratio(
        (0, 0, 0),
        (255, 255, 255)
    )
    assert ratio > 20
    
    # Edge case with very similar colors
    ratio = accessibility_checker._calculate_contrast_ratio(
        (200, 200, 200),
        (201, 201, 201)
    )
    assert ratio > 0

def test_luminance_calculation_errors(accessibility_checker):
    """Test luminance calculation error handling"""
    # Test with invalid color values
    invalid_colors = [
        (-1, 0, 0),
        (0, -1, 0),
        (0, 0, -1),
        (256, 0, 0),
        (0, 256, 0),
        (0, 0, 256)
    ]
    
    for color in invalid_colors:
        luminance = accessibility_checker._get_luminance(color)
        assert 0 <= luminance <= 1

def test_check_element_exception_handling(accessibility_checker, mock_element):
    """Test exception handling in check_element"""
    # Test with attribute access error
    mock_element.get_attribute.side_effect = Exception("Attribute error")
    accessibility_checker.check_element(mock_element)
    
    # Test with property access error
    mock_element.text = property(lambda _: (_ for _ in ()).throw(Exception("Property error")))
    accessibility_checker.check_element(mock_element)
    
    # Test with method call error
    mock_element.is_enabled.side_effect = Exception("Method error")
    accessibility_checker.check_element(mock_element)
    
    # Verify that checker continues despite errors
    assert isinstance(accessibility_checker.violations, list)

def test_check_application_with_automation(mock_element):
    """Test check_application with automation instance"""
    mock_automation = MagicMock()
    mock_automation.root = mock_element
    mock_element.find_all = MagicMock(return_value=[mock_element])
    
    checker = AccessibilityChecker()
    checker.check_application(mock_automation)
    assert len(checker.violations) > 0

def test_generate_report_element_attributes(accessibility_checker, mock_element, tmp_path):
    """Test report generation with different element attributes"""
    report_path = tmp_path / "report.html"
    
    # Test with various element attributes
    mock_element.id = "test-id"
    mock_element.name = "Test Element"
    mock_element.role = "button"
    mock_element.text = "Click me"
    mock_element.get_attribute.side_effect = lambda x: {
        "aria-label": "Test button",
        "title": "Test title",
        "class": "test-class",
        "style": "color: red"
    }.get(x)
    
    accessibility_checker.check_element(mock_element)
    accessibility_checker.generate_report(report_path)
    
    # Verify report content
    assert report_path.exists()
    content = report_path.read_text()
    assert "test-id" in content
    assert "Test Element" in content
    assert "button" in content
    assert "Click me" in content
