"""
Account management tools for MCP
"""

from typing import List, Dict, Any
from tools.base_tools import BaseTools
from auth.auth_manager import AuthManager


class AccountTools(BaseTools):
    """Account management tools"""
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get account management tools"""
        return [
            {
                "name": "list_workspace_accounts",
                "description": "List all configured Google Workspace accounts and their authentication status",
                "inputSchema": {
                    "type": "object",
                    "properties": {}
                }
            },
            {
                "name": "authenticate_workspace_account",
                "description": "Add and authenticate a new Google Workspace account",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email address of the account to authenticate (optional, will be determined from OAuth)"
                        }
                    }
                }
            },
            {
                "name": "remove_workspace_account",
                "description": "Remove a Google Workspace account and its associated tokens",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {
                            "type": "string",
                            "description": "Email address of the account to remove"
                        }
                    },
                    "required": ["email"]
                }
            }
        ]
    
    def has_tool(self, name: str) -> bool:
        """Check if this class handles a specific tool"""
        return name in [
            "list_workspace_accounts",
            "authenticate_workspace_account",
            "remove_workspace_account"
        ]
    
    def handle_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution"""
        if name == "list_workspace_accounts":
            return self._list_accounts()
        elif name == "authenticate_workspace_account":
            return self._authenticate_account(args)
        elif name == "remove_workspace_account":
            return self._remove_account(args)
        else:
            raise ValueError(f"Unknown tool: {name}")
    
    def _list_accounts(self) -> Dict[str, Any]:
        """List all accounts"""
        try:
            accounts = self.auth_manager.list_accounts()
            return {
                "content": [
                    {
                        "type": "text",
                        "text": str(accounts)
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ]
            }
    
    def _authenticate_account(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Authenticate an account"""
        try:
            email = args.get("email")
            result = self.auth_manager.get_auth_url(email)
            
            if not result["success"]:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Failed to generate auth URL: {result.get('error')}"
                        }
                    ]
                }
            
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Please visit this URL to authenticate:\n\n{result['authUrl']}\n\nAfter clicking 'Allow' on the Google authorization page, the authentication will complete automatically."
                    }
                ]
            }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ]
            }
    
    def _remove_account(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Remove an account"""
        try:
            email = args.get("email")
            if not email:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": "Error: email is required"
                        }
                    ]
                }
            
            success = self.auth_manager.remove_account(email)
            
            if success:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Successfully removed account: {email}"
                        }
                    ]
                }
            else:
                return {
                    "content": [
                        {
                            "type": "text",
                            "text": f"Failed to remove account: {email}"
                        }
                    ]
                }
        except Exception as e:
            return {
                "content": [
                    {
                        "type": "text",
                        "text": f"Error: {str(e)}"
                    }
                ]
            }

