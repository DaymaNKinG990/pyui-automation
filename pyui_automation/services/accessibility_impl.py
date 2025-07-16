from .accessibility import AccessibilityService
from typing import List, Dict

class AccessibilityServiceImpl(AccessibilityService):
    def __init__(self, checker):
        self.checker = checker

    def check_accessibility(self) -> List[Dict[str, str]]:
        return self.checker.check()

    def generate_report(self, output_dir: str) -> None:
        self.checker.generate_report(output_dir) 