"""
Contacts integration routes
"""

from flask import Blueprint, jsonify, request
from auth.auth_manager import AuthManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

bp = Blueprint('contacts', __name__, url_prefix='/api/contacts')
auth_manager = AuthManager()

@bp.route('/list', methods=['POST'])
def get_contacts():
    """Retrieve contact information and details from Google Contacts"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'people', 'v1')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        page_size = data.get('pageSize', 10)
        page_token = data.get('pageToken')
        query = data.get('query')
        sort_order = data.get('sortOrder')
        
        read_mask = data.get(
            'readMask',
            'names,emailAddresses,phoneNumbers,addresses,organizations,photos'
        )
        
        if query:
            # Use searchContacts if query is provided
            params = {
                'query': query,
                'readMask': read_mask,
                'pageSize': page_size
            }
            
            if page_token:
                params['pageToken'] = page_token
            
            results = service.people().searchContacts(body=params).execute()
            contacts = results.get('results', [])
        else:
            # List all connections
            params = {
                'resourceName': 'people/me',
                'personFields': read_mask,
                'pageSize': page_size
            }
            
            if page_token:
                params['pageToken'] = page_token
            if sort_order:
                params['sortOrder'] = sort_order
            
            results = service.people().connections().list(**params).execute()
            contacts = results.get('connections', [])
        
        # Process contacts to extract useful information
        processed_contacts = []
        for contact in contacts:
            processed = {}
            
            # Handle both connection list and searchContacts format
            contact_data = contact.get('person', contact) if 'person' in contact else contact
            
            if 'names' in contact_data and len(contact_data['names']) > 0:
                primary_name = next((name for name in contact_data['names'] if name.get('metadata', {}).get('primary')), contact_data['names'][0])
                processed['name'] = {
                    'displayName': primary_name.get('displayName'),
                    'givenName': primary_name.get('givenName'),
                    'familyName': primary_name.get('familyName')
                }
            
            if 'emailAddresses' in contact_data:
                processed['emails'] = [email.get('value') for email in contact_data['emailAddresses']]
            
            if 'phoneNumbers' in contact_data:
                processed['phones'] = [phone.get('value') for phone in contact_data['phoneNumbers']]
            
            if 'organizations' in contact_data:
                processed['organizations'] = [
                    {
                        'name': org.get('name'),
                        'title': org.get('title')
                    } for org in contact_data['organizations']
                ]
            
            processed['resourceName'] = contact_data.get('resourceName', '')
            processed_contacts.append(processed)
        
        return jsonify({
            'contacts': processed_contacts,
            'total': len(processed_contacts)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

