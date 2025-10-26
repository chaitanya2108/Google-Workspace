"""
Calendar integration routes
"""

from flask import Blueprint, jsonify, request
from auth.auth_manager import AuthManager
from dotenv import load_dotenv
from datetime import datetime, timedelta
from typing import Dict, Any

# Load environment variables
load_dotenv()

bp = Blueprint('calendar', __name__, url_prefix='/api/calendar')
auth_manager = AuthManager()

@bp.route('/list', methods=['POST'])
def list_events():
    """List and search calendar events"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'calendar', 'v3')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        calendar_id = data.get('calendarId', 'primary')
        time_min = data.get('timeMin')
        time_max = data.get('timeMax')
        max_results = data.get('maxResults', 10)
        single_events = data.get('singleEvents', True)
        order_by = data.get('orderBy', 'startTime')
        query = data.get('q', '')
        
        # Build parameters
        params = {
            'calendarId': calendar_id,
            'maxResults': max_results,
            'singleEvents': single_events,
            'orderBy': order_by
        }
        
        if time_min:
            params['timeMin'] = time_min
        if time_max:
            params['timeMax'] = time_max
        if query:
            params['q'] = query
        
        results = service.events().list(**params).execute()
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/event/<event_id>', methods=['GET'])
def get_event(event_id):
    """Get detailed information about a specific calendar event"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'calendar', 'v3')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        calendar_id = data.get('calendarId', 'primary')
        
        result = service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        return jsonify(result), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/event', methods=['POST'])
def create_event():
    """Create a new calendar event"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        summary = data.get('summary')
        start = data.get('start')
        end = data.get('end')
        
        if not all([email, summary, start, end]):
            return jsonify({'error': 'Missing required fields: email, summary, start, end'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'calendar', 'v3')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        calendar_id = data.get('calendarId', 'primary')
        
        event_body = {
            'summary': summary,
            'description': data.get('description', ''),
            'start': start,
            'end': end
        }
        
        if data.get('location'):
            event_body['location'] = data.get('location')
        
        if data.get('attendees'):
            event_body['attendees'] = [
                {'email': attendee} for attendee in data.get('attendees')
            ]
        
        result = service.events().insert(
            calendarId=calendar_id,
            body=event_body
        ).execute()
        
        return jsonify({
            'message': 'Event created successfully',
            'eventId': result.get('id')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/event/<event_id>', methods=['PUT'])
def update_event(event_id):
    """Update an existing calendar event"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'calendar', 'v3')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        calendar_id = data.get('calendarId', 'primary')
        
        # Get existing event
        event = service.events().get(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        # Update fields
        if 'summary' in data:
            event['summary'] = data['summary']
        if 'description' in data:
            event['description'] = data['description']
        if 'start' in data:
            event['start'] = data['start']
        if 'end' in data:
            event['end'] = data['end']
        if 'location' in data:
            event['location'] = data['location']
        if 'attendees' in data:
            event['attendees'] = [
                {'email': attendee} for attendee in data['attendees']
            ]
        
        result = service.events().update(
            calendarId=calendar_id,
            eventId=event_id,
            body=event
        ).execute()
        
        return jsonify({
            'message': 'Event updated successfully',
            'eventId': result.get('id')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/event/<event_id>', methods=['DELETE'])
def delete_event(event_id):
    """Delete a calendar event"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'calendar', 'v3')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        calendar_id = data.get('calendarId', 'primary')
        
        service.events().delete(
            calendarId=calendar_id,
            eventId=event_id
        ).execute()
        
        return jsonify({'message': 'Event deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

