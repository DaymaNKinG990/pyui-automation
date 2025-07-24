"""
IElement interface - composite interface for complete element functionality.

This interface combines all element capabilities through composition
of specialized interfaces, following Interface Segregation Principle.
"""

from typing import Any

from .ielement_properties import IElementProperties
from .ielement_geometry import IElementGeometry
from .ielement_state import IElementState
from .ielement_interaction import IElementInteraction
from .ielement_wait import IElementWait
from .ielement_search import IElementSearch
from .ielement_screenshot import IElementScreenshot


class IElement(IElementProperties, IElementGeometry, IElementState, 
              IElementInteraction, IElementWait, IElementSearch, IElementScreenshot):
    """
    Complete element interface that combines all capabilities.
    
    This interface inherits from all specialized interfaces to provide
    a complete element contract while maintaining interface segregation.
    """
    
    @property
    def native_element(self) -> Any:
        """Get native element"""
        pass
    
    @property
    def session(self) -> Any:
        """Get the automation session"""
        pass 