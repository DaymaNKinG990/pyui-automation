"""PyUI Automation package for UI test automation"""

from .core.session import AutomationSession as UIAutomation
from .core.visual import VisualTester, VisualMatcher, VisualDifference as visual
from .elements import UIElement, Button, Window, Input
from .utils import *
from .logging import logger
from .exceptions import *
from .di import container
from .wait import ElementWaits

__version__ = "0.1.0"
__all__ = [
    'UIAutomation',
    'visual',
    'UIElement',
    'Button',
    'Window',
    'Input',
    'logger',
    'container',
    'ElementWaits'
]
