import pytest
from unittest.mock import MagicMock, patch
from pyui_automation.accessibility import AccessibilityChecker, AccessibilityViolation


@pytest.fixture
def mock_element():
    """Create a mock UI element for testing"""
    element = MagicMock()
    element.id = "test-id"
    element.name = "test-button"
    element.role = "button"
    element.is_enabled.return_value = True
    element.is_keyboard_accessible.return_value = True
    element.get_attribute.return_value = None
    element.get_location.return_value = (0, 0)
    element.get_size.return_value = (100, 30)
    return element


@pytest.fixture
def accessibility_checker():
    """Create AccessibilityChecker instance"""
    checker = AccessibilityChecker()
    checker._is_image_element = MagicMock(return_value=True)
    checker._get_element_color = MagicMock(side_effect=[(0, 0, 0), (255, 255, 255)])
    return checker


def test_check_element_alt_text(accessibility_checker, mock_element):
    """Test checking element for alternative text"""
    mock_element.get_attribute.return_value = None
    
    accessibility_checker.check_element(mock_element)
    violations = accessibility_checker.violations
    
    assert any(v.rule == "missing_alt_text" for v in violations)


def test_check_element_color_contrast(accessibility_checker, mock_element):
    """Test checking element for color contrast"""
    # Setup mock element with text and colors
    mock_element.text = "Test Text"
    mock_element.get_attribute.side_effect = lambda x: {
        "color": "#000000",
        "background-color": "#FFFFFF"
    }.get(x)
    
    # Mock color retrieval to return black text on white background
    accessibility_checker._get_element_color = MagicMock(side_effect=[
        (0, 0, 0),      # Foreground color (black)
        (255, 255, 255) # Background color (white)
    ])
    
    # Check element
    accessibility_checker.check_element(mock_element)
    violations = accessibility_checker.violations
    
    # Black on white should pass contrast check (ratio > 4.5)
    assert not any(v.rule == "insufficient_contrast" for v in violations)

    # Test with low contrast colors
    accessibility_checker.violations.clear()
    accessibility_checker._get_element_color = MagicMock(side_effect=[
        (128, 128, 128),  # Gray text
        (169, 169, 169)   # Light gray background
    ])
    
    accessibility_checker.check_element(mock_element)
    violations = accessibility_checker.violations
    
    # Low contrast should fail
    assert any(v.rule == "insufficient_contrast" for v in violations)


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
    mock_root = MagicMock()
    mock_root.find_elements.return_value = [mock_element]
    
    accessibility_checker.check_application(mock_root)
    violations = accessibility_checker.violations
    
    assert len(violations) > 0


def test_generate_report(accessibility_checker, mock_element, tmp_path):
    """Test generating accessibility report"""
    mock_root = MagicMock()
    mock_root.find_elements.return_value = [mock_element]
    
    accessibility_checker.check_application(mock_root)
    report_path = tmp_path / "accessibility_report.html"
    
    accessibility_checker.generate_report(str(report_path))
    
    assert report_path.exists()
    assert report_path.stat().st_size > 0


def test_color_contrast_calculation(accessibility_checker):
    """Test color contrast ratio calculation"""
    fg_color = (0, 0, 0)  # Black
    bg_color = (255, 255, 255)  # White
    
    ratio = accessibility_checker._calculate_contrast_ratio(fg_color, bg_color)
    assert ratio == 21.0  # Maximum contrast ratio


def test_get_all_elements(accessibility_checker, mock_element):
    """Test getting all elements in application"""
    mock_root = MagicMock()
    mock_root.find_elements.return_value = [mock_element]
    
    elements = accessibility_checker._get_all_elements(mock_root)
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
