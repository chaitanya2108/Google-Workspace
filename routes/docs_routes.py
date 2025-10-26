"""
Docs integration routes
"""

from flask import Blueprint, jsonify, request
from auth.auth_manager import AuthManager
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

bp = Blueprint('docs', __name__, url_prefix='/api/docs')
auth_manager = AuthManager()

@bp.route('/create', methods=['POST'])
def create_document():
    """Create a new blank Google Doc document"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        title = data.get('title')
        
        if not all([email, title]):
            return jsonify({'error': 'Email and title are required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'drive', 'v3')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        file_metadata = {
            'name': title,
            'mimeType': 'application/vnd.google-apps.document'
        }
        
        if data.get('parentFolderId'):
            file_metadata['parents'] = [data.get('parentFolderId')]
        
        result = service.files().create(
            body=file_metadata,
            fields='id,name'
        ).execute()
        
        return jsonify({
            'message': 'Document created successfully',
            'documentId': result.get('id'),
            'title': result.get('name')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/list', methods=['POST'])
def list_documents():
    """List all Google Docs documents"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'drive', 'v3')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        page_size = data.get('pageSize', 10)
        page_token = data.get('pageToken')
        query = data.get('q', "mimeType='application/vnd.google-apps.document'")
        
        params = {
            'pageSize': page_size,
            'q': query,
            'fields': 'files(id,name,mimeType,modifiedTime,webViewLink),nextPageToken'
        }
        
        if page_token:
            params['pageToken'] = page_token
        
        results = service.files().list(**params).execute()
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/<document_id>', methods=['GET'])
def get_document(document_id):
    """Get the content and metadata of a Google Doc"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        docs_service = auth_manager.get_authenticated_client(email, 'docs', 'v1')
        drive_service = auth_manager.get_authenticated_client(email, 'drive', 'v3')
        
        if not docs_service or not drive_service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        # Get document metadata from Drive
        file_metadata = drive_service.files().get(
            fileId=document_id,
            fields='id,name,mimeType,modifiedTime,webViewLink'
        ).execute()
        
        # Get document content
        doc = docs_service.documents().get(documentId=document_id).execute()
        
        return jsonify({
            'metadata': file_metadata,
            'content': doc
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

