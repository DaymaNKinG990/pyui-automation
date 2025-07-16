import pytest
from unittest.mock import MagicMock
from pyui_automation.accessibility import AccessibilityChecker
from pyui_automation.services.accessibility_impl import AccessibilityServiceImpl


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
    # Делаем элемент img без alt, чтобы было нарушение
    mock_element.role = "img"
    mock_element.get_attribute = MagicMock(side_effect=lambda x: "img" if x == "role" else None)
    mock_element.find_all = MagicMock(return_value=[mock_element])
    mock_element.find_elements = MagicMock(return_value=[mock_element])
    accessibility_checker.check_application(mock_element)
    assert len(accessibility_checker.violations) > 0

def test_color_contrast_calculation(accessibility_checker):
    """Test color contrast ratio calculation"""
    ratio = accessibility_checker._calculate_contrast_ratio(
        (0, 0, 0),       # Black
        (255, 255, 255)  # White
    )
    assert ratio > 20  # White on black should have very high contrast

def test_get_all_elements(accessibility_checker, mock_element):
    """Test getting all elements in application"""
    # _get_all_elements вызывает find_elements, а не find_all
    mock_element.find_elements = MagicMock(return_value=[mock_element])
    elements = accessibility_checker._get_all_elements(mock_element)
    assert len(elements) == len(mock_element.find_elements.return_value)

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
    assert bg_color == (0, 255, 0)

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

def test_color_parsing_errors(accessibility_checker, mock_element):
    """Test color parsing error handling"""
    # Test invalid hex color
    mock_element.get_attribute.return_value = "#XYZ"
    color = accessibility_checker._get_element_color(mock_element, "color")
    assert color is None  # Теперь ожидаем None
    
    # Test invalid rgb format
    mock_element.get_attribute.return_value = "rgb(invalid)"
    color = accessibility_checker._get_element_color(mock_element, "color")
    assert color is None
    
    # Test invalid color name
    mock_element.get_attribute.return_value = "not_a_color"
    color = accessibility_checker._get_element_color(mock_element, "color")
    assert color is None


def test_get_element_color_no_get_attribute(accessibility_checker):
    """Test color parsing when element has no get_attribute method"""
    class NoAttr:
        pass
    element = NoAttr()
    color = accessibility_checker._get_element_color(element, "color")
    assert color is None


def test_check_element_no_text_or_role(accessibility_checker):
    """Test check_element when element has no text or role attributes"""
    class NoTextRole:
        def get_attribute(self, x):
            return None
        def is_keyboard_accessible(self):
            return True
    element = NoTextRole()
    accessibility_checker.check_element(element)
    # Не должно быть исключений, violations может быть пустым
    assert isinstance(accessibility_checker.violations, list)


def test_check_element_property_exception(accessibility_checker):
    """Test check_element with property raising exception (double-класс)"""
    class PropError:
        def __init__(self):
            self._fail = True
        def get_attribute(self, x):
            return None
        @property
        def text(self):
            if self._fail:
                raise Exception("Property error")
            return "ok"
        def is_keyboard_accessible(self):
            return True
        @property
        def role(self):
            raise Exception("Role error")
    element = PropError()
    accessibility_checker.check_element(element)
    assert isinstance(accessibility_checker.violations, list)


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
        assert isinstance(luminance, float)

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
    mock_automation.get_active_window.return_value = mock_element
    mock_element.role = "img"
    mock_element.get_attribute = MagicMock(side_effect=lambda x: "img" if x == "role" else None)
    mock_element.find_all = MagicMock(return_value=[mock_element])
    mock_element.find_elements = MagicMock(return_value=[mock_element])
    checker = AccessibilityChecker(mock_automation)
    checker.check_application()
    assert len(checker.violations) > 0

def test_accessibility_service_impl_check(monkeypatch):
    """Проверяет делегирование check_accessibility в AccessibilityServiceImpl"""
    called = {}
    class DummyChecker:
        def check(self):
            called['check'] = True
            return [{'rule': 'dummy', 'severity': 'high'}]
    service = AccessibilityServiceImpl(DummyChecker())
    result = service.check_accessibility()
    assert called.get('check')
    assert isinstance(result, list)
    assert result[0]['rule'] == 'dummy'

def test_accessibility_service_impl_generate_report(tmp_path):
    """Проверяет делегирование generate_report в AccessibilityServiceImpl"""
    called = {}
    class DummyChecker:
        def generate_report(self, output_dir):
            called['dir'] = output_dir
    service = AccessibilityServiceImpl(DummyChecker())
    out = tmp_path / "report.html"
    service.generate_report(str(out))
    assert called['dir'] == str(out)
