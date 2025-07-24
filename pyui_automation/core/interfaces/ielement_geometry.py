"""
IElementGeometry interface - defines contract for element geometry.

Responsible for:
- Element location
- Element size
- Element bounds
- Element center
"""

from abc import ABC, abstractmethod
from typing import Dict


class IElementGeometry(ABC):
    """Interface for element geometry"""
    
    @property
    @abstractmethod
    def location(self) -> Dict[str, int]:
        """Get element location"""
        pass
    
    @property
    @abstractmethod
    def size(self) -> Dict[str, int]:
        """Get element size"""
        pass
    
    @property
    @abstractmethod
    def rect(self) -> Dict[str, int]:
        """Get element rectangle (x, y, width, height)"""
        pass
    
    @property
    @abstractmethod
    def center(self) -> Dict[str, int]:
        """Get element center coordinates"""
        pass 