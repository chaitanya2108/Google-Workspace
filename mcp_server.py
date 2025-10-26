"""
MCP Server for Google Workspace Integration
Implements Model Context Protocol (MCP) with stdin/stdout communication
"""

import sys
import json
import signal
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

from auth.auth_manager import AuthManager
try:
    from tools.gmail_tools import GmailTools
    from tools.calendar_tools import CalendarTools
    from tools.drive_tools import DriveTools
    from tools.contacts_tools import ContactsTools
    from tools.account_tools import AccountTools
    from tools.docs_tools import DocsTools
    from tools.sheets_tools import SheetsTools
except ImportError:
    # Fallback for when running without full module structure
    GmailTools = CalendarTools = DriveTools = ContactsTools = DocsTools = AccountTools = SheetsTools = None

# Load environment variables
load_dotenv()

class MCPServer:
    """Model Context Protocol Server for Google Workspace"""
    
    def __init__(self):
        """Initialize the MCP server"""
        self.auth_manager = AuthManager()
        
        # Initialize tool handlers
        self.account_tools = AccountTools(self.auth_manager)
        self.gmail_tools = GmailTools(self.auth_manager)
        self.calendar_tools = CalendarTools(self.auth_manager)
        self.drive_tools = DriveTools(self.auth_manager)
        self.contacts_tools = ContactsTools(self.auth_manager)
        self.docs_tools = DocsTools(self.auth_manager)
        self.sheets_tools = SheetsTools(self.auth_manager)
        
        # Combine all tools
        self.all_tools = self._get_all_tools()
    
    def _get_all_tools(self) -> List[Dict[str, Any]]:
        """Get all available tools"""
        tools = []
        
        # Get tools from each handler
        tools.extend(self.account_tools.get_tools())
        tools.extend(self.gmail_tools.get_tools())
        tools.extend(self.calendar_tools.get_tools())
        tools.extend(self.drive_tools.get_tools())
        tools.extend(self.contacts_tools.get_tools())
        tools.extend(self.docs_tools.get_tools())
        tools.extend(self.sheets_tools.get_tools())
        
        return tools
    
    def _handle_list_tools(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/list request"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "tools": self.all_tools
            }
        }
    
    def _handle_call_tool(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tools/call request"""
        params = request.get("params", {})
        tool_name = params.get("name")
        arguments = params.get("arguments", {})
        
        try:
            # Route to appropriate tool handler
                if self.account_tools.has_tool(tool_name):
                    result = self.account_tools.handle_tool(tool_name, arguments)
                elif self.gmail_tools.has_tool(tool_name):
                    result = self.gmail_tools.handle_tool(tool_name, arguments)
                elif self.calendar_tools.has_tool(tool_name):
                    result = self.calendar_tools.handle_tool(tool_name, arguments)
                elif self.drive_tools.has_tool(tool_name):
                    result = self.drive_tools.handle_tool(tool_name, arguments)
                elif self.contacts_tools.has_tool(tool_name):
                    result = self.contacts_tools.handle_tool(tool_name, arguments)
                elif self.docs_tools.has_tool(tool_name):
                    result = self.docs_tools.handle_tool(tool_name, arguments)
                elif self.sheets_tools.has_tool(tool_name):
                    result = self.sheets_tools.handle_tool(tool_name, arguments)
                else:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                return {
                    "jsonrpc": "2.0",
                    "id": request.get("id"),
                    "result": result
                }
        except Exception as e:
            return {
                "jsonrpc": "2.0",
                "id": request.get("id"),
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }
    
    def _handle_initialize(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialize request"""
        return {
            "jsonrpc": "2.0",
            "id": request.get("id"),
            "result": {
                "protocolVersion": "2024-11-05",
                "capabilities": {
                    "tools": {}
                },
                "serverInfo": {
                    "name": "google-workspace-mcp",
                    "version": "1.0.0"
                }
            }
        }
    
    def _handle_notification_initialized(self, request: Dict[str, Any]):
        """Handle notification/initialized"""
        # No response needed for notifications
        pass
    
    def _handle_request(self, message: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle incoming JSON-RPC request"""
        method = message.get("method")
        
        if method == "initialize":
            return self._handle_initialize(message)
        elif method == "tools/list":
            return self._handle_list_tools(message)
        elif method == "tools/call":
            return self._handle_call_tool(message)
        elif method == "notifications/initialized":
            self._handle_notification_initialized(message)
            return None
        else:
            return {
                "jsonrpc": "2.0",
                "id": message.get("id"),
                "error": {
                    "code": -32601,
                    "message": f"Method not found: {method}"
                }
            }
    
    def run(self):
        """Run the MCP server"""
        # Set up signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        # Main loop
        while True:
            try:
                # Read JSON message from stdin
                line = sys.stdin.readline()
                if not line:
                    break
                
                message = json.loads(line.strip())
                
                # Handle the request
                response = self._handle_request(message)
                
                # Send response if there is one
                if response:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                
            except json.JSONDecodeError as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32700,
                        "message": f"Parse error: {str(e)}"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
            
            except Exception as e:
                error_response = {
                    "jsonrpc": "2.0",
                    "id": None,
                    "error": {
                        "code": -32603,
                        "message": f"Internal error: {str(e)}"
                    }
                }
                sys.stdout.write(json.dumps(error_response) + "\n")
                sys.stdout.flush()
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        sys.exit(0)


def main():
    """Main entry point"""
    server = MCPServer()
    server.run()


if __name__ == "__main__":
    main()

