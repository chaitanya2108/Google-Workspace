"""
Account management routes
"""

from flask import Blueprint, jsonify, request
from auth.auth_manager import AuthManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

bp = Blueprint('accounts', __name__)
auth_manager = AuthManager()

@bp.route('/api/accounts', methods=['GET'])
def list_accounts():
    """List all configured Google Workspace accounts"""
    try:
        accounts = auth_manager.list_accounts()
        return jsonify({
            'accounts': accounts,
            'total': len(accounts)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/accounts/authenticate', methods=['POST'])
def authenticate_account():
    """Generate OAuth URL for authentication"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        
        result = auth_manager.get_auth_url(email)
        
        if not result['success']:
            return jsonify({'error': result.get('error', 'Failed to generate auth URL')}), 400
        
        return jsonify({
            'authUrl': result['authUrl'],
            'state': result['state'],
            'message': 'Please visit the authorization URL to complete authentication'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/api/accounts/<email>', methods=['DELETE'])
def remove_account(email):
    """Remove a Google Workspace account"""
    try:
        success = auth_manager.remove_account(email)
        
        if not success:
            return jsonify({'error': 'Failed to remove account'}), 400
        
        return jsonify({
            'message': f'Successfully removed account: {email}'
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

