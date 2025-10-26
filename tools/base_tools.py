"""
Base class for all tool handlers
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from auth.auth_manager import AuthManager


class BaseTools(ABC):
    """Base class for all Google Workspace tools"""
    
    def __init__(self, auth_manager: AuthManager):
        """
        Initialize base tools
        
        Args:
            auth_manager: Authentication manager instance
        """
        self.auth_manager = auth_manager
    
    @abstractmethod
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get list of available tools"""
        pass
    
    @abstractmethod
    def has_tool(self, name: str) -> bool:
        """Check if this class handles a specific tool"""
        pass
    
    @abstractmethod
    def handle_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution"""
        pass

