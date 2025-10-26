"""
Gmail tools for MCP - Full implementation
"""

from typing import List, Dict, Any
from tools.base_tools import BaseTools
from auth.auth_manager import AuthManager
from googleapiclient.discovery import build
import base64
import json


class GmailTools(BaseTools):
    """Gmail tools"""
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get Gmail tools"""
        return [
            {
                "name": "search_workspace_emails",
                "description": "Search emails in Gmail with advanced filtering options",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account to search"},
                        "query": {"type": "string", "description": "Gmail search query (e.g., 'from:example@gmail.com', 'subject:meeting', 'has:attachment')"},
                        "maxResults": {"type": "number", "description": "Maximum number of emails to return (default: 10)"},
                        "includeSpamTrash": {"type": "boolean", "description": "Include emails from spam and trash folders"}
                    },
                    "required": ["email"]
                }
            },
            {
                "name": "send_workspace_email",
                "description": "Send an email through Gmail",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account to send from"},
                        "to": {"type": "string", "description": "Recipient email address"},
                        "subject": {"type": "string", "description": "Email subject"},
                        "body": {"type": "string", "description": "Email body (HTML or plain text)"},
                        "cc": {"type": "string", "description": "CC recipient email addresses (comma-separated)"},
                        "bcc": {"type": "string", "description": "BCC recipient email addresses (comma-separated)"}
                    },
                    "required": ["email", "to", "subject", "body"]
                }
            },
            {
                "name": "manage_workspace_draft",
                "description": "Create, update, or manage email drafts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "action": {"type": "string", "enum": ["create", "update", "list", "get", "delete"], "description": "Action to perform on drafts"},
                        "draftId": {"type": "string", "description": "Draft ID (required for update, get, delete)"},
                        "to": {"type": "string", "description": "Recipient email address (for create/update)"},
                        "subject": {"type": "string", "description": "Email subject (for create/update)"},
                        "body": {"type": "string", "description": "Email body (for create/update)"}
                    },
                    "required": ["email", "action"]
                }
            },
            {
                "name": "manage_workspace_label",
                "description": "Create and manage Gmail labels",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "action": {"type": "string", "enum": ["create", "list", "get", "delete"], "description": "Action to perform on labels"},
                        "labelId": {"type": "string", "description": "Label ID (required for get, delete)"},
                        "name": {"type": "string", "description": "Label name (required for create)"},
                        "labelListVisibility": {"type": "string", "enum": ["labelShow", "labelHide", "labelShowIfUnread"], "description": "Label list visibility"},
                        "messageListVisibility": {"type": "string", "enum": ["show", "hide"], "description": "Message list visibility"}
                    },
                    "required": ["email", "action"]
                }
            },
            {
                "name": "manage_workspace_label_assignment",
                "description": "Apply or remove labels from messages",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "messageId": {"type": "string", "description": "Message ID to modify"},
                        "addLabelIds": {"type": "array", "items": {"type": "string"}, "description": "Label IDs to add to the message"},
                        "removeLabelIds": {"type": "array", "items": {"type": "string"}, "description": "Label IDs to remove from the message"}
                    },
                    "required": ["email", "messageId"]
                }
            },
            {
                "name": "get_workspace_gmail_settings",
                "description": "Get Gmail account settings and configuration",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"}
                    },
                    "required": ["email"]
                }
            }
        ]
    
    def has_tool(self, name: str) -> bool:
        """Check if this class handles a specific tool"""
        return name in [
            "search_workspace_emails",
            "send_workspace_email",
            "manage_workspace_draft",
            "manage_workspace_label",
            "manage_workspace_label_assignment",
            "get_workspace_gmail_settings"
        ]
    
    def handle_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution"""
        email = args.get("email")
        if not email:
            return {"content": [{"type": "text", "text": f"Error: Email is required"}]}
        
        service = self.auth_manager.get_authenticated_client(email, "gmail", "v1")
        if not service:
            return {"content": [{"type": "text", "text": "Error: Account not authenticated"}]}
        
        try:
            if name == "search_workspace_emails":
                return self._search_emails(service, args)
            elif name == "send_workspace_email":
                return self._send_email(service, args)
            elif name == "manage_workspace_draft":
                return self._manage_draft(service, args)
            elif name == "manage_workspace_label":
                return self._manage_label(service, args)
            elif name == "manage_workspace_label_assignment":
                return self._manage_label_assignment(service, args)
            elif name == "get_workspace_gmail_settings":
                return self._get_gmail_settings(service, args)
            else:
                return {"content": [{"type": "text", "text": f"Error: Unknown tool: {name}"}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}
    
    def _search_emails(self, service, args: Dict[str, Any]) -> Dict[str, Any]:
        """Search emails"""
        try:
            params = {
                'userId': 'me',
                'q': args.get('query', ''),
                'maxResults': args.get('maxResults', 10),
                'includeSpamTrash': args.get('includeSpamTrash', False)
            }
            
            response = service.users().messages().list(**params).execute()
            messages = response.get('messages', [])
            
            # Get details for each message
            message_details = []
            for msg in messages[:params['maxResults']]:
                detail = service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='metadata',
                    metadataHeaders=['From', 'To', 'Subject', 'Date']
                ).execute()
                message_details.append(detail)
            
            return {
                "content": [{
                    "type": "text",
                    "text": json.dumps({
                        "messages": message_details,
                        "total": len(messages),
                        "query": args.get('query', '')
                    }, indent=2)
                }]
            }
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}
    
    def _send_email(self, service, args: Dict[str, Any]) -> Dict[str, Any]:
        """Send email"""
        try:
            message_parts = [f"To: {args['to']}"]
            if args.get('cc'):
                message_parts.append(f"Cc: {args['cc']}")
            if args.get('bcc'):
                message_parts.append(f"Bcc: {args['bcc']}")
            message_parts.append(f"Subject: {args['subject']}")
            message_parts.append("")
            message_parts.append(args['body'])
            
            message = '\n'.join(message_parts)
            encoded = base64.urlsafe_b64encode(message.encode()).decode()
            
            result = service.users().messages().send(
                userId='me',
                body={'raw': encoded}
            ).execute()
            
            return {
                "content": [{
                    "type": "text",
                    "text": f"Email sent successfully. Message ID: {result.get('id')}"
                }]
            }
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}
    
    def _manage_draft(self, service, args: Dict[str, Any]) -> Dict[str, Any]:
        """Manage drafts"""
        action = args.get('action')
        if action == 'create':
            return self._create_draft(service, args)
        elif action == 'list':
            return self._list_drafts(service, args)
        elif action == 'get':
            return self._get_draft(service, args)
        elif action == 'update':
            return self._update_draft(service, args)
        elif action == 'delete':
            return self._delete_draft(service, args)
        else:
            return {"content": [{"type": "text", "text": f"Error: Unknown action: {action}"}]}
    
    def _create_draft(self, service, args):
        message = f"To: {args['to']}\nSubject: {args['subject']}\n\n{args['body']}"
        encoded = base64.urlsafe_b64encode(message.encode()).decode()
        
        result = service.users().drafts().create(
            userId='me',
            body={'message': {'raw': encoded}}
        ).execute()
        
        return {"content": [{"type": "text", "text": f"Draft created. ID: {result['id']}"}]}
    
    def _list_drafts(self, service, args):
        result = service.users().drafts().list(userId='me').execute()
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
    
    def _get_draft(self, service, args):
        result = service.users().drafts().get(userId='me', id=args['draftId']).execute()
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
    
    def _update_draft(self, service, args):
        message = f"To: {args['to']}\nSubject: {args['subject']}\n\n{args['body']}"
        encoded = base64.urlsafe_b64encode(message.encode()).decode()
        
        result = service.users().drafts().update(
            userId='me',
            id=args['draftId'],
            body={'message': {'raw': encoded}}
        ).execute()
        
        return {"content": [{"type": "text", "text": f"Draft updated. ID: {result['id']}"}]}
    
    def _delete_draft(self, service, args):
        service.users().drafts().delete(userId='me', id=args['draftId']).execute()
        return {"content": [{"type": "text", "text": "Draft deleted"}]}
    
    def _manage_label(self, service, args):
        action = args.get('action')
        if action == 'create':
            result = service.users().labels().create(
                userId='me',
                body={
                    'name': args['name'],
                    'labelListVisibility': args.get('labelListVisibility', 'labelShow'),
                    'messageListVisibility': args.get('messageListVisibility', 'show')
                }
            ).execute()
            return {"content": [{"type": "text", "text": f"Label created. ID: {result['id']}"}]}
        elif action == 'list':
            result = service.users().labels().list(userId='me').execute()
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        elif action == 'get':
            result = service.users().labels().get(userId='me', id=args['labelId']).execute()
            return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
        elif action == 'delete':
            service.users().labels().delete(userId='me', id=args['labelId']).execute()
            return {"content": [{"type": "text", "text": "Label deleted"}]}
        else:
            return {"content": [{"type": "text", "text": f"Error: Unknown action: {action}"}]}
    
    def _manage_label_assignment(self, service, args):
        result = service.users().messages().modify(
            userId='me',
            id=args['messageId'],
            body={
                'addLabelIds': args.get('addLabelIds', []),
                'removeLabelIds': args.get('removeLabelIds', [])
            }
        ).execute()
        
        return {"content": [{"type": "text", "text": f"Labels updated for message {args['messageId']}"}]}
    
    def _get_gmail_settings(self, service, args):
        import asyncio
        profile = service.users().getProfile(userId='me').execute()
        # Note: settings.get is not always available
        result = {"profile": profile}
        
        return {"content": [{"type": "text", "text": json.dumps(result, indent=2)}]}
