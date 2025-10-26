"""
Contacts tools for MCP - Full implementation
"""

from typing import List, Dict, Any
from tools.base_tools import BaseTools
import json


class ContactsTools(BaseTools):
    """Contacts tools"""
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get contacts tools"""
        return [
            {
                "name": "get_workspace_contacts",
                "description": "Retrieve contact information and details from Google Contacts",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "pageSize": {"type": "number", "description": "Number of contacts to return (default: 10)"},
                        "pageToken": {"type": "string", "description": "Token for pagination"},
                        "query": {"type": "string", "description": "Search query to filter contacts"},
                        "sortOrder": {"type": "string", "enum": ["LAST_NAME_ASCENDING", "LAST_NAME_DESCENDING", "FIRST_NAME_ASCENDING", "FIRST_NAME_DESCENDING"], "description": "Sort order for contacts"},
                        "readMask": {"type": "string", "description": "Fields to include in response (comma-separated)"}
                    },
                    "required": ["email"]
                }
            }
        ]
    
    def has_tool(self, name: str) -> bool:
        """Check if this class handles a specific tool"""
        return name == "get_workspace_contacts"
    
    def handle_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution"""
        email = args.get("email")
        if not email:
            return {"content": [{"type": "text", "text": "Error: Email is required"}]}
        
        service = self.auth_manager.get_authenticated_client(email, "people", "v1")
        if not service:
            return {"content": [{"type": "text", "text": "Error: Account not authenticated"}]}
        
        try:
            if name == "get_workspace_contacts":
                return self._get_contacts(service, args)
            else:
                return {"content": [{"type": "text", "text": f"Error: Unknown tool: {name}"}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}
    
    def _get_contacts(self, service, args):
        """Get contacts from Google"""
        params = {
            'resourceName': 'people/me',
            'personFields': args.get('readMask', 'names,emailAddresses,phoneNumbers,addresses,organizations,photos'),
            'pageSize': args.get('pageSize', 10)
        }
        if args.get('pageToken'):
            params['pageToken'] = args['pageToken']
        if args.get('sortOrder'):
            params['sortOrder'] = args['sortOrder']
        
        # If query is provided, use searchContacts
        if args.get('query'):
            response = service.people().searchContacts(
                query=args['query'],
                readMask=params['personFields'],
                pageSize=params['pageSize']
            ).execute()
            contacts = response.get('results', [])
            contacts = [r.get('person', r) for r in contacts]
        else:
            response = service.people().connections().list(**params).execute()
            contacts = response.get('connections', [])
        
        # Process contacts to extract useful information
        processed_contacts = []
        for contact in contacts:
            processed = {'resourceName': contact.get('resourceName', '')}
            
            # Extract names
            if 'names' in contact and len(contact['names']) > 0:
                primary_name = next((n for n in contact['names'] if n.get('metadata', {}).get('primary')), contact['names'][0])
                processed['name'] = {
                    'displayName': primary_name.get('displayName', ''),
                    'givenName': primary_name.get('givenName', ''),
                    'familyName': primary_name.get('familyName', ''),
                    'middleName': primary_name.get('middleName', '')
                }
            
            # Extract email addresses
            if 'emailAddresses' in contact:
                processed['emails'] = [{'value': e.get('value', ''), 'type': e.get('type', ''), 'primary': e.get('metadata', {}).get('primary', False)} for e in contact['emailAddresses']]
            
            # Extract phone numbers
            if 'phoneNumbers' in contact:
                processed['phones'] = [{'value': p.get('value', ''), 'type': p.get('type', ''), 'primary': p.get('metadata', {}).get('primary', False)} for p in contact['phoneNumbers']]
            
            # Extract addresses
            if 'addresses' in contact:
                processed['addresses'] = [{'formattedValue': a.get('formattedValue', ''), 'type': a.get('type', ''), 'primary': a.get('metadata', {}).get('primary', False)} for a in contact['addresses']]
            
            # Extract organizations
            if 'organizations' in contact:
                processed['organizations'] = [{'name': o.get('name', ''), 'title': o.get('title', ''), 'department': o.get('department', ''), 'type': o.get('type', ''), 'primary': o.get('metadata', {}).get('primary', False)} for o in contact['organizations']]
            
            # Extract photos
            if 'photos' in contact and len(contact['photos']) > 0:
                primary_photo = next((p for p in contact['photos'] if p.get('metadata', {}).get('primary')), contact['photos'][0])
                processed['photo'] = {'url': primary_photo.get('url', ''), 'default': primary_photo.get('default', False)}
            
            processed_contacts.append(processed)
        
        return {"content": [{"type": "text", "text": json.dumps({
            "contacts": processed_contacts,
            "total": len(processed_contacts),
            "nextPageToken": response.get('nextPageToken')
        }, indent=2)}]}
