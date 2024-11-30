from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import json
from pathlib import Path
import time
import cv2
import numpy as np
from PIL import Image
import colour


@dataclass
class AccessibilityViolation:
    element: Any
    rule: str
    severity: str
    description: str
    recommendation: str


class AccessibilityChecker:
    """Check application accessibility compliance"""

    def __init__(self, automation):
        self.automation = automation
        self.violations: List[AccessibilityViolation] = []

    def check_element(self, element) -> List[AccessibilityViolation]:
        """Check single element for accessibility issues"""
        violations = []
        
        # Check for missing alternative text
        if self._is_image_element(element) and not self._has_alt_text(element):
            violations.append(AccessibilityViolation(
                element=element,
                rule="alt-text",
                severity="error",
                description="Image element missing alternative text",
                recommendation="Add descriptive alternative text for the image"
            ))

        # Check for sufficient color contrast
        if self._has_text(element):
            contrast_ratio = self._check_color_contrast(element)
            if contrast_ratio < 4.5:  # WCAG AA standard
                violations.append(AccessibilityViolation(
                    element=element,
                    rule="color-contrast",
                    severity="error",
                    description=f"Insufficient color contrast ratio: {contrast_ratio:.2f}",
                    recommendation="Increase color contrast to meet WCAG AA standards (minimum 4.5:1)"
                ))

        # Check for keyboard accessibility
        if self._is_interactive(element) and not self._is_keyboard_accessible(element):
            violations.append(AccessibilityViolation(
                element=element,
                rule="keyboard-accessible",
                severity="error",
                description="Interactive element not keyboard accessible",
                recommendation="Ensure element can be focused and activated using keyboard"
            ))

        # Check for appropriate element role
        if not self._has_valid_role(element):
            violations.append(AccessibilityViolation(
                element=element,
                rule="valid-role",
                severity="warning",
                description="Element missing or has invalid ARIA role",
                recommendation="Add appropriate ARIA role for the element"
            ))

        return violations

    def check_application(self) -> List[AccessibilityViolation]:
        """Check entire application for accessibility issues"""
        self.violations.clear()
        
        # Get all elements
        elements = self._get_all_elements()
        
        # Check each element
        for element in elements:
            self.violations.extend(self.check_element(element))
        
        return self.violations

    def generate_report(self, output_dir: str):
        """Generate accessibility report"""
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)

        # Group violations by severity
        violations_by_severity = {}
        for violation in self.violations:
            if violation.severity not in violations_by_severity:
                violations_by_severity[violation.severity] = []
            violations_by_severity[violation.severity].append(violation)

        # Generate HTML report
        html_report = f"""
        <html>
        <head>
            <title>Accessibility Report</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .violation {{ margin: 20px 0; padding: 10px; border: 1px solid #ccc; }}
                .error {{ border-left: 5px solid #ff0000; }}
                .warning {{ border-left: 5px solid #ffa500; }}
                .info {{ border-left: 5px solid #0000ff; }}
            </style>
        </head>
        <body>
            <h1>Accessibility Report</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <ul>
        """
        
        for severity in violations_by_severity:
            html_report += f"""
                    <li>{severity.title()}: {len(violations_by_severity[severity])} violations</li>
            """

        html_report += """
                </ul>
            </div>
        """

        for severity in violations_by_severity:
            html_report += f"""
            <div class="violations">
                <h2>{severity.title()} Violations</h2>
            """
            
            for violation in violations_by_severity[severity]:
                html_report += f"""
                <div class="violation {severity}">
                    <h3>{violation.rule}</h3>
                    <p><strong>Description:</strong> {violation.description}</p>
                    <p><strong>Recommendation:</strong> {violation.recommendation}</p>
                </div>
                """

            html_report += """
            </div>
            """

        html_report += """
        </body>
        </html>
        """

        with open(output_path / 'accessibility_report.html', 'w') as f:
            f.write(html_report)

        # Save raw violations data
        with open(output_path / 'violations.json', 'w') as f:
            json.dump([{
                'rule': v.rule,
                'severity': v.severity,
                'description': v.description,
                'recommendation': v.recommendation
            } for v in self.violations], f, indent=2)

    def _is_image_element(self, element) -> bool:
        """Check if element is an image"""
        try:
            return element.get_attribute("role") in ["img", "image"]
        except Exception:
            return False

    def _has_alt_text(self, element) -> bool:
        """Check if element has alternative text"""
        try:
            return bool(element.get_attribute("alt"))
        except Exception:
            return False

    def _has_text(self, element) -> bool:
        """Check if element has visible text"""
        try:
            return bool(element.text.strip())
        except Exception:
            return False

    def _check_color_contrast(self, element) -> float:
        """Calculate color contrast ratio"""
        try:
            # Get element colors
            fg_color = self._get_element_color(element, "color")
            bg_color = self._get_element_color(element, "background-color")
            
            if fg_color and bg_color:
                # Convert colors to luminance
                fg_luminance = self._get_relative_luminance(fg_color)
                bg_luminance = self._get_relative_luminance(bg_color)
                
                # Calculate contrast ratio
                lighter = max(fg_luminance, bg_luminance)
                darker = min(fg_luminance, bg_luminance)
                return (lighter + 0.05) / (darker + 0.05)
        except Exception:
            pass
        return 0.0

    def _is_interactive(self, element) -> bool:
        """Check if element is interactive"""
        try:
            return element.get_attribute("role") in [
                "button", "link", "checkbox", "radio",
                "combobox", "listbox", "menu", "menuitem",
                "tab", "textbox", "switch"
            ]
        except Exception:
            return False

    def _is_keyboard_accessible(self, element) -> bool:
        """Check if element is keyboard accessible"""
        try:
            return element.get_attribute("tabindex") is not None
        except Exception:
            return False

    def _has_valid_role(self, element) -> bool:
        """Check if element has valid ARIA role"""
        try:
            role = element.get_attribute("role")
            return role is not None and role in [
                "alert", "application", "article", "banner",
                "button", "cell", "checkbox", "columnheader",
                "combobox", "complementary", "contentinfo",
                "definition", "dialog", "directory", "document",
                "feed", "figure", "form", "grid", "gridcell",
                "group", "heading", "img", "link", "list",
                "listbox", "listitem", "log", "main", "marquee",
                "math", "menu", "menubar", "menuitem", "menuitemcheckbox",
                "menuitemradio", "navigation", "note", "option",
                "presentation", "progressbar", "radio", "radiogroup",
                "region", "row", "rowgroup", "rowheader", "scrollbar",
                "search", "searchbox", "separator", "slider", "spinbutton",
                "status", "switch", "tab", "table", "tablist", "tabpanel",
                "term", "textbox", "timer", "toolbar", "tooltip", "tree",
                "treegrid", "treeitem"
            ]
        except Exception:
            return False

    def _get_all_elements(self) -> List[Any]:
        """Get all elements in the application"""
        # This is a simplified version. In practice, you would need to
        # implement a proper tree traversal of the application's UI
        return self.automation.find_elements("*", "")

    def _get_element_color(self, element, property_name: str) -> Optional[tuple]:
        """Get element color as RGB tuple"""
        try:
            color = element.get_attribute(property_name)
            if color.startswith('rgb'):
                return tuple(map(int, color.strip('rgb()').split(',')))
            elif color.startswith('#'):
                return tuple(int(color.lstrip('#')[i:i+2], 16) for i in (0, 2, 4))
        except Exception:
            pass
        return None

    def _get_relative_luminance(self, rgb: tuple) -> float:
        """Calculate relative luminance of a color"""
        r, g, b = [x / 255 for x in rgb]
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        return 0.2126 * r + 0.7152 * g + 0.0722 * b
