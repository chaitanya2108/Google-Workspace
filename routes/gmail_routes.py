"""
Gmail integration routes
"""

from flask import Blueprint, jsonify, request
from auth.auth_manager import AuthManager
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from dotenv import load_dotenv
import base64
from typing import Dict, Any

# Load environment variables
load_dotenv()

bp = Blueprint('gmail', __name__, url_prefix='/api/gmail')
auth_manager = AuthManager()

@bp.route('/search', methods=['POST'])
def search_emails():
    """Search emails in Gmail"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'gmail', 'v1')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        query = data.get('query', '')
        max_results = data.get('maxResults', 10)
        include_spam_trash = data.get('includeSpamTrash', False)
        
        results = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results,
            includeSpamTrash=include_spam_trash
        ).execute()
        
        messages = results.get('messages', [])
        
        # Get details for each message
        message_details = []
        for msg in messages:
            detail = service.users().messages().get(
                userId='me',
                id=msg['id'],
                format='metadata',
                metadataHeaders=['From', 'To', 'Subject', 'Date']
            ).execute()
            message_details.append(detail)
        
        return jsonify({
            'messages': message_details,
            'total': len(messages),
            'query': query
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/send', methods=['POST'])
def send_email():
    """Send an email through Gmail"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        to = data.get('to')
        subject = data.get('subject')
        body = data.get('body')
        
        if not all([email, to, subject, body]):
            return jsonify({'error': 'Missing required fields: email, to, subject, body'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'gmail', 'v1')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        # Create message
        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        
        # Add CC and BCC if provided
        if data.get('cc'):
            message['Cc'] = data.get('cc')
        if data.get('bcc'):
            message['Bcc'] = data.get('bcc')
        
        # Encode message
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
        
        # Send message
        result = service.users().messages().send(
            userId='me',
            body={'raw': raw_message}
        ).execute()
        
        return jsonify({
            'message': 'Email sent successfully',
            'messageId': result.get('id')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/draft', methods=['POST'])
def manage_draft():
    """Create, update, or manage email drafts"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        action = data.get('action')
        
        if not all([email, action]):
            return jsonify({'error': 'Email and action are required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'gmail', 'v1')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        if action == 'create':
            to = data.get('to')
            subject = data.get('subject')
            body = data.get('body')
            
            if not all([to, subject, body]):
                return jsonify({'error': 'Missing required fields for create: to, subject, body'}), 400
            
            message = MIMEText(body)
            message['to'] = to
            message['subject'] = subject
            raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')
            
            result = service.users().drafts().create(
                userId='me',
                body={
                    'message': {
                        'raw': raw_message
                    }
                }
            ).execute()
            
            return jsonify({
                'message': 'Draft created successfully',
                'draftId': result.get('id')
            }), 200
            
        elif action == 'list':
            results = service.users().drafts().list(userId='me').execute()
            return jsonify(results), 200
            
        elif action == 'get':
            draft_id = data.get('draftId')
            if not draft_id:
                return jsonify({'error': 'draftId is required'}), 400
            
            result = service.users().drafts().get(
                userId='me',
                id=draft_id
            ).execute()
            
            return jsonify(result), 200
        else:
            return jsonify({'error': f'Unknown action: {action}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/label', methods=['POST'])
def manage_label():
    """Create and manage Gmail labels"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        action = data.get('action')
        
        if not all([email, action]):
            return jsonify({'error': 'Email and action are required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'gmail', 'v1')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        if action == 'create':
            name = data.get('name')
            if not name:
                return jsonify({'error': 'name is required for create'}), 400
            
            result = service.users().labels().create(
                userId='me',
                body={
                    'name': name,
                    'labelListVisibility': data.get('labelListVisibility', 'labelShow'),
                    'messageListVisibility': data.get('messageListVisibility', 'show')
                }
            ).execute()
            
            return jsonify({
                'message': 'Label created successfully',
                'labelId': result.get('id')
            }), 200
            
        elif action == 'list':
            results = service.users().labels().list(userId='me').execute()
            return jsonify(results), 200
        else:
            return jsonify({'error': f'Unknown action: {action}'}), 400
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

