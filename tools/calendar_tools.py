"""
Calendar tools for MCP - Full implementation
"""

from typing import List, Dict, Any
from tools.base_tools import BaseTools
from auth.auth_manager import AuthManager
import json


class CalendarTools(BaseTools):
    """Calendar tools"""
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get calendar tools"""
        return [
            {
                "name": "list_workspace_calendar_events",
                "description": "List and search calendar events",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "calendarId": {"type": "string", "description": "Calendar ID (default: primary)"},
                        "timeMin": {"type": "string", "description": "Lower bound for event start times (RFC3339 timestamp)"},
                        "timeMax": {"type": "string", "description": "Upper bound for event start times (RFC3339 timestamp)"},
                        "maxResults": {"type": "number", "description": "Maximum number of events to return (default: 10)"},
                        "singleEvents": {"type": "boolean", "description": "Whether to expand recurring events into instances"},
                        "orderBy": {"type": "string", "enum": ["startTime", "updated"], "description": "Order of events returned"},
                        "q": {"type": "string", "description": "Free text search terms"}
                    },
                    "required": ["email"]
                }
            },
            {
                "name": "get_workspace_calendar_event",
                "description": "Get detailed information about a specific calendar event",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "calendarId": {"type": "string", "description": "Calendar ID (default: primary)"},
                        "eventId": {"type": "string", "description": "Event ID"}
                    },
                    "required": ["email", "eventId"]
                }
            },
            {
                "name": "create_workspace_calendar_event",
                "description": "Create a new calendar event",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "calendarId": {"type": "string", "description": "Calendar ID (default: primary)"},
                        "summary": {"type": "string", "description": "Event title/summary"},
                        "description": {"type": "string", "description": "Event description"},
                        "start": {"type": "object", "description": "Start time with dateTime and timeZone"},
                        "end": {"type": "object", "description": "End time with dateTime and timeZone"},
                        "attendees": {"type": "array", "description": "List of attendees"},
                        "location": {"type": "string", "description": "Event location"},
                        "reminders": {"type": "object", "description": "Event reminders"}
                    },
                    "required": ["email", "summary", "start", "end"]
                }
            },
            {
                "name": "manage_workspace_calendar_event",
                "description": "Update calendar events and respond to invitations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "calendarId": {"type": "string"},
                        "eventId": {"type": "string"},
                        "action": {"type": "string", "enum": ["update", "respond"], "description": "Action to perform"},
                        "responseStatus": {"type": "string", "enum": ["accepted", "declined", "tentative"], "description": "Response status (for respond action)"},
                        "summary": {"type": "string"},
                        "description": {"type": "string"},
                        "start": {"type": "object"},
                        "end": {"type": "object"},
                        "attendees": {"type": "array"},
                        "location": {"type": "string"}
                    },
                    "required": ["email", "eventId", "action"]
                }
            },
            {
                "name": "delete_workspace_calendar_event",
                "description": "Delete calendar events",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string"},
                        "calendarId": {"type": "string"},
                        "eventId": {"type": "string"},
                        "sendUpdates": {"type": "string", "enum": ["all", "externalOnly", "none"], "description": "Whether to send notifications"}
                    },
                    "required": ["email", "eventId"]
                }
            }
        ]
    
    def has_tool(self, name: str) -> bool:
        """Check if this class handles a specific tool"""
        return name in [
            "list_workspace_calendar_events",
            "get_workspace_calendar_event",
            "create_workspace_calendar_event",
            "manage_workspace_calendar_event",
            "delete_workspace_calendar_event"
        ]
    
    def handle_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution"""
        email = args.get("email")
        if not email:
            return {"content": [{"type": "text", "text": "Error: Email is required"}]}
        
        service = self.auth_manager.get_authenticated_client(email, "calendar", "v3")
        if not service:
            return {"content": [{"type": "text", "text": "Error: Account not authenticated"}]}
        
        try:
            if name == "list_workspace_calendar_events":
                return self._list_events(service, args)
            elif name == "get_workspace_calendar_event":
                return self._get_event(service, args)
            elif name == "create_workspace_calendar_event":
                return self._create_event(service, args)
            elif name == "manage_workspace_calendar_event":
                return self._manage_event(service, args)
            elif name == "delete_workspace_calendar_event":
                return self._delete_event(service, args)
            else:
                return {"content": [{"type": "text", "text": f"Error: Unknown tool: {name}"}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}
    
    def _list_events(self, service, args):
        params = {
            'calendarId': args.get('calendarId', 'primary'),
            'maxResults': args.get('maxResults', 10),
            'singleEvents': args.get('singleEvents', True),
            'orderBy': args.get('orderBy', 'startTime')
        }
        if args.get('timeMin'):
            params['timeMin'] = args['timeMin']
        if args.get('timeMax'):
            params['timeMax'] = args['timeMax']
        if args.get('q'):
            params['q'] = args['q']
        
        response = service.events().list(**params).execute()
        events = response.get('items', [])
        
        return {"content": [{"type": "text", "text": json.dumps({"events": events, "total": len(events), "calendarId": params['calendarId']}, indent=2)}]}
    
    def _get_event(self, service, args):
        response = service.events().get(calendarId=args.get('calendarId', 'primary'), eventId=args['eventId']).execute()
        return {"content": [{"type": "text", "text": json.dumps(response, indent=2)}]}
    
    def _create_event(self, service, args):
        event = {
            'summary': args['summary'],
            'description': args.get('description', ''),
            'start': args['start'],
            'end': args['end']
        }
        if args.get('location'):
            event['location'] = args['location']
        if args.get('attendees'):
            event['attendees'] = args['attendees']
        if args.get('reminders'):
            event['reminders'] = args['reminders']
        
        response = service.events().insert(calendarId=args.get('calendarId', 'primary'), body=event).execute()
        return {"content": [{"type": "text", "text": f"Event created. ID: {response['id']}"}]}
    
    def _manage_event(self, service, args):
        if args['action'] == 'respond':
            return self._respond_to_event(service, args)
        elif args['action'] == 'update':
            return self._update_event(service, args)
        else:
            return {"content": [{"type": "text", "text": f"Error: Unknown action: {args['action']}"}]}
    
    def _respond_to_event(self, service, args):
        event = service.events().get(calendarId=args.get('calendarId', 'primary'), eventId=args['eventId']).execute()
        attendees = event.get('attendees', [])
        updated = [{'email': att['email'], 'responseStatus': args['responseStatus']} if att['email'] == args['email'] else att for att in attendees]
        
        response = service.events().update(
            calendarId=args.get('calendarId', 'primary'),
            eventId=args['eventId'],
            body={'attendees': updated}
        ).execute()
        return {"content": [{"type": "text", "text": f"Responded: {args['responseStatus']}"}]}
    
    def _update_event(self, service, args):
        event = service.events().get(calendarId=args.get('calendarId', 'primary'), eventId=args['eventId']).execute()
        updated = dict(event)
        if args.get('summary'): updated['summary'] = args['summary']
        if args.get('description'): updated['description'] = args['description']
        if args.get('start'): updated['start'] = args['start']
        if args.get('end'): updated['end'] = args['end']
        if args.get('location'): updated['location'] = args['location']
        if args.get('attendees'): updated['attendees'] = args['attendees']
        
        response = service.events().update(calendarId=args.get('calendarId', 'primary'), eventId=args['eventId'], body=updated).execute()
        return {"content": [{"type": "text", "text": f"Event updated. ID: {response['id']}"}]}
    
    def _delete_event(self, service, args):
        params = {'calendarId': args.get('calendarId', 'primary'), 'eventId': args['eventId']}
        if args.get('sendUpdates'):
            params['sendUpdates'] = args['sendUpdates']
        service.events().delete(**params).execute()
        return {"content": [{"type": "text", "text": "Event deleted"}]}
