from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass
from enum import Enum, auto
import logging


class AccessibilitySeverity(Enum):
    """Severity levels for accessibility violations."""
    LOW = auto()
    MEDIUM = auto()
    HIGH = auto()


@dataclass
class AccessibilityViolation:
    """Represents an accessibility violation found during checking."""
    element: Any
    rule: str
    severity: AccessibilitySeverity
    description: str
    recommendation: str


class AccessibilityChecker:
    """
    Check application accessibility compliance according to WCAG guidelines.

    Проверяет элементы UI на соответствие стандартам доступности (WCAG): alt-текст, контрастность, доступность с клавиатуры, валидные ARIA-ролли и др.
    Используется сервисным слоем AccessibilityService.

    Example usage:
        checker = AccessibilityChecker(automation)
        violations = checker.check_application()
        checker.generate_report("reports/accessibility.html")

    Назначение:
        - Автоматизированный аудит доступности UI
        - Генерация HTML-отчёта по найденным нарушениям
        - Интеграция с сервисным слоем
    """
    
    # Valid ARIA roles from WAI-ARIA specification
    VALID_ROLES: Set[str] = {
        "alert", "alertdialog", "application", "article", "banner", "button", 
        "checkbox", "columnheader", "combobox", "complementary", "contentinfo", 
        "dialog", "directory", "document", "form", "grid", "gridcell", "group", 
        "heading", "img", "link", "list", "listbox", "listitem", "main", "menu", 
        "menubar", "menuitem", "menuitemcheckbox", "menuitemradio", "navigation", 
        "note", "option", "presentation", "progressbar", "radio", "radiogroup", 
        "region", "row", "rowgroup", "rowheader", "scrollbar", "search", 
        "searchbox", "separator", "slider", "spinbutton", "status", "tab", 
        "tablist", "tabpanel", "textbox", "timer", "toolbar", "tooltip", "tree", 
        "treegrid", "treeitem"
    }
    
    # Interactive roles that should be keyboard accessible
    INTERACTIVE_ROLES: Set[str] = {
        "button", "checkbox", "combobox", "link", "menuitem", "menuitemcheckbox",
        "menuitemradio", "option", "radio", "slider", "spinbutton", "tab", 
        "textbox", "treeitem"
    }

    # Common named colors mapping
    NAMED_COLORS: Dict[str, Tuple[int, int, int]] = {
        'black': (0, 0, 0),
        'white': (255, 255, 255),
        'red': (255, 0, 0),
        'green': (0, 255, 0),
        'blue': (0, 0, 255),
        'gray': (128, 128, 128),
        'silver': (192, 192, 192),
        'maroon': (128, 0, 0),
        'purple': (128, 0, 128),
        'navy': (0, 0, 128),
    }

    def __init__(self, automation: Optional[Any] = None, logger: Optional[logging.Logger] = None) -> None:
        """
        Initialize accessibility checker.
        
        Args:
            automation: Optional UIAutomation instance for automation-specific checks
            logger: Optional logger instance for logging errors and warnings
        """
        self.automation = automation
        self.logger = logger or logging.getLogger(__name__)
        self.violations: List[AccessibilityViolation] = []

    def check_element(self, element: Any) -> None:
        """
        Check single element for accessibility issues.
        
        Args:
            element: UI element to check for accessibility issues
        """
        try:
            self._check_alt_text(element)
            self._check_color_contrast(element)
            self._check_keyboard_accessibility(element)
            self._check_aria_role(element)
        except Exception as e:
            self.logger.error(f"Error checking element {element}: {str(e)}")

    def check_application(self, root_element: Optional[Any] = None) -> List[AccessibilityViolation]:
        """
        Check entire application for accessibility issues.
        
        Args:
            root_element: Optional root element to start checking from. If None,
                        uses the active window from automation.
        
        Returns:
            List of accessibility violations found
        """
        self.violations.clear()
        try:
            if root_element is None and self.automation:
                root_element = self.automation.get_active_window()
            if root_element:
                elements = self._get_all_elements(root_element)
                for element in elements:
                    self.check_element(element)
        except Exception as e:
            self.logger.error(f"Error checking application: {str(e)}")
        return self.violations

    def _check_alt_text(self, element: Any) -> None:
        """Check if image elements have alternative text."""
        if self._is_image_element(element) and not element.get_attribute("alt"):
            self.violations.append(AccessibilityViolation(
                element=element,
                rule="missing_alt_text",
                severity=AccessibilitySeverity.HIGH,
                description="Image element missing alternative text",
                recommendation="Add descriptive alt text to the image"
            ))

    def _check_color_contrast(self, element: Any) -> None:
        """Check if text elements have sufficient color contrast."""
        if self._has_text(element):
            try:
                fg_color = self._get_element_color(element, "color") or (0, 0, 0)
                bg_color = self._get_element_color(element, "background-color") or (255, 255, 255)
                
                contrast = self._calculate_contrast_ratio(fg_color, bg_color)
                if contrast < 4.5:  # WCAG AA standard
                    self.violations.append(AccessibilityViolation(
                        element=element,
                        rule="insufficient_contrast",
                        severity=AccessibilitySeverity.HIGH,
                        description=f"Insufficient color contrast ratio: {contrast:.1f}:1",
                        recommendation="Increase the color contrast to at least 4.5:1"
                    ))
            except Exception as e:
                self.logger.warning(f"Error checking color contrast: {str(e)}")

    def _check_keyboard_accessibility(self, element: Any) -> None:
        """Check if interactive elements are keyboard accessible."""
        if self._is_interactive(element) and not element.is_keyboard_accessible():
            self.violations.append(AccessibilityViolation(
                element=element,
                rule="not_keyboard_accessible",
                severity=AccessibilitySeverity.HIGH,
                description="Interactive element not keyboard accessible",
                recommendation="Ensure the element can be focused and activated with keyboard"
            ))

    def _check_aria_role(self, element: Any) -> None:
        """Check if element has valid ARIA role."""
        if not self._has_valid_role(element):
            self.violations.append(AccessibilityViolation(
                element=element,
                rule="invalid_aria_role",
                severity=AccessibilitySeverity.MEDIUM,
                description=f"Invalid ARIA role: {element.role}",
                recommendation="Use a valid ARIA role from the WAI-ARIA specification"
            ))

    @staticmethod
    def _is_image_element(element: Any) -> bool:
        """
        Check if element is an image.
        
        Args:
            element: Element to check
            
        Returns:
            True if element is an image, False otherwise
        """
        return element.role == "img" or element.get_attribute("role") == "img"

    @staticmethod
    def _has_text(element: Any) -> bool:
        """
        Check if element contains text.
        
        Args:
            element: Element to check
            
        Returns:
            True if element contains text, False otherwise
        """
        try:
            if not hasattr(element, "text"):
                return False
            text = element.text
            if not isinstance(text, str):
                return False
            return bool(text.strip())
        except Exception:
            return False

    def _get_element_color(self, element: Any, property: str) -> Optional[Tuple[int, int, int]]:
        """
        Get element's color as RGB tuple.
        
        Args:
            element: Element to get color from
            property: CSS property name ("color" or "background-color")
            
        Returns:
            RGB color tuple or None if color cannot be determined
        """
        try:
            color_str = element.get_attribute(property)
            if not color_str:
                return None
                
            color_str = color_str.strip().lower()
            
            # Handle hex colors
            if color_str.startswith('#'):
                return self._parse_hex_color(color_str)
            
            # Handle rgb/rgba colors
            if color_str.startswith('rgb'):
                return self._parse_rgb_color(color_str)
            
            # Handle named colors
            return self.NAMED_COLORS.get(color_str)
            
        except Exception as e:
            self.logger.warning(f"Error parsing color {property}: {str(e)}")
            return None

    @staticmethod
    def _parse_hex_color(color_str: str) -> Optional[Tuple[int, int, int]]:
        """Parse hex color string to RGB tuple."""
        if len(color_str) == 4:  # Short form #RGB
            r = int(color_str[1] + color_str[1], 16)
            g = int(color_str[2] + color_str[2], 16)
            b = int(color_str[3] + color_str[3], 16)
            return (r, g, b)
        elif len(color_str) == 7:  # Full form #RRGGBB
            r = int(color_str[1:3], 16)
            g = int(color_str[3:5], 16)
            b = int(color_str[5:7], 16)
            return (r, g, b)
        return None

    @staticmethod
    def _parse_rgb_color(color_str: str) -> Optional[Tuple[int, int, int]]:
        """Parse rgb/rgba color string to RGB tuple."""
        values = color_str.split('(')[1].split(')')[0].split(',')
        if len(values) >= 3:
            r = int(values[0].strip())
            g = int(values[1].strip())
            b = int(values[2].strip())
            return (r, g, b)
        return None

    def _calculate_contrast_ratio(self, fg_color: Tuple[int, int, int], 
                                bg_color: Tuple[int, int, int]) -> float:
        """
        Calculate color contrast ratio using WCAG algorithm.
        
        Args:
            fg_color: Foreground color as RGB tuple
            bg_color: Background color as RGB tuple
            
        Returns:
            Contrast ratio as float
        """
        try:
            fg_luminance = self._get_luminance(fg_color)
            bg_luminance = self._get_luminance(bg_color)
            
            lighter = max(fg_luminance, bg_luminance)
            darker = min(fg_luminance, bg_luminance)
            
            return (lighter + 0.05) / (darker + 0.05)
            
        except Exception as e:
            self.logger.error(f"Error calculating contrast ratio: {str(e)}")
            return 0.0

    def _get_luminance(self, color: Tuple[int, int, int]) -> float:
        """
        Calculate relative luminance using WCAG formula.
        
        Args:
            color: RGB color tuple
            
        Returns:
            Relative luminance as float
        """
        try:
            r, g, b = [x / 255.0 for x in color]
            
            r = self._to_srgb(r)
            g = self._to_srgb(g)
            b = self._to_srgb(b)
            
            return 0.2126 * r + 0.7152 * g + 0.0722 * b
            
        except Exception as e:
            self.logger.error(f"Error calculating luminance: {str(e)}")
            return 0.0

    @staticmethod
    def _to_srgb(c: float) -> float:
        """Convert linear RGB to sRGB."""
        return c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4

    @classmethod
    def _is_interactive(cls, element: Any) -> bool:
        """
        Check if element is interactive.
        
        Args:
            element: Element to check
            
        Returns:
            True if element is interactive, False otherwise
        """
        return element.role in cls.INTERACTIVE_ROLES

    @classmethod
    def _has_valid_role(cls, element: Any) -> bool:
        """
        Check if element has valid ARIA role.
        
        Args:
            element: Element to check
            
        Returns:
            True if element has valid role, False otherwise
        """
        return element.role in cls.VALID_ROLES

    def _get_all_elements(self, root_element: Any) -> List[Any]:
        """
        Get all elements in application.
        
        Args:
            root_element: Root element to start search from
            
        Returns:
            List of all child elements
        """
        return root_element.find_elements("*")
