"""
Drive integration routes
"""

from flask import Blueprint, jsonify, request, send_file
from auth.auth_manager import AuthManager
from dotenv import load_dotenv
from pathlib import Path
import os

# Load environment variables
load_dotenv()

bp = Blueprint('drive', __name__, url_prefix='/api/drive')
auth_manager = AuthManager()

def ensure_workspace_dir(email: str):
    """Ensure workspace directory exists for the email"""
    workspace_dir = Path('workspace') / email
    workspace_dir.mkdir(parents=True, exist_ok=True)
    return workspace_dir

@bp.route('/list', methods=['POST'])
def list_files():
    """List files in Google Drive with filtering and pagination"""
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
        query = data.get('q')
        order_by = data.get('orderBy', 'modifiedTime desc')
        fields = data.get('fields', 'files(id,name,mimeType,modifiedTime,size)')
        
        params = {
            'pageSize': page_size,
            'fields': f'files({fields}),nextPageToken'
        }
        
        if page_token:
            params['pageToken'] = page_token
        if query:
            params['q'] = query
        if order_by:
            params['orderBy'] = order_by
        
        results = service.files().list(**params).execute()
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/search', methods=['POST'])
def search_files():
    """Full-text search across Drive content"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        query_text = data.get('query')
        
        if not all([email, query_text]):
            return jsonify({'error': 'Email and query are required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'drive', 'v3')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        page_size = data.get('pageSize', 10)
        page_token = data.get('pageToken')
        
        params = {
            'q': f"fullText contains '{query_text}'",
            'pageSize': page_size,
            'fields': 'files(id,name,mimeType,modifiedTime,size),nextPageToken'
        }
        
        if page_token:
            params['pageToken'] = page_token
        
        results = service.files().list(**params).execute()
        
        return jsonify(results), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/upload', methods=['POST'])
def upload_file():
    """Upload files to Google Drive with metadata and permissions"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        file_path = data.get('filePath')
        name = data.get('name')
        
        if not all([email, file_path]):
            return jsonify({'error': 'Email and filePath are required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'drive', 'v3')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        # Check if file exists
        if not Path(file_path).exists():
            return jsonify({'error': 'File not found'}), 404
        
        # Prepare file metadata
        file_metadata = {
            'name': name or Path(file_path).name
        }
        
        if data.get('parents'):
            file_metadata['parents'] = [data.get('parents')]
        
        # Upload file
        media_body = file_path
        
        result = service.files().create(
            body=file_metadata,
            media_body=media_body,
            fields='id,name,mimeType,size'
        ).execute()
        
        return jsonify({
            'message': 'File uploaded successfully',
            'fileId': result.get('id'),
            'name': result.get('name')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/download/<file_id>', methods=['POST'])
def download_file(file_id):
    """Download files from Google Drive"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'drive', 'v3')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        # Get file metadata
        file_metadata = service.files().get(
            fileId=file_id,
            fields='name,mimeType'
        ).execute()
        
        # Check if it's a Google Doc/Sheets
        mime_type = file_metadata.get('mimeType', '')
        download_mime = data.get('mimeType', 'application/pdf')
        
        if 'google-apps' in mime_type:
            # Export Google Docs
            request_obj = service.files().export_media(
                fileId=file_id,
                mimeType=download_mime
            )
        else:
            # Download regular file
            request_obj = service.files().get_media(fileId=file_id)
        
        # Save to workspace
        workspace_dir = ensure_workspace_dir(email)
        download_dir = workspace_dir / 'downloads'
        download_dir.mkdir(parents=True, exist_ok=True)
        
        file_name = file_metadata.get('name', 'downloaded_file')
        local_path = download_dir / file_name
        
        with open(local_path, 'wb') as f:
            import io
            downloader = io.BytesIO()
            downloader.write(request_obj.execute().content)
            f.write(downloader.getvalue())
        
        return jsonify({
            'message': 'File downloaded successfully',
            'localPath': str(local_path)
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/file/<file_id>', methods=['DELETE'])
def delete_file(file_id):
    """Delete files and folders from Google Drive"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        
        if not email:
            return jsonify({'error': 'Email is required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'drive', 'v3')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        service.files().delete(fileId=file_id).execute()
        
        return jsonify({'message': 'File deleted successfully'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@bp.route('/folder', methods=['POST'])
def create_folder():
    """Create organized folder structures in Google Drive"""
    try:
        data = request.get_json() or {}
        email = data.get('email')
        name = data.get('name')
        
        if not all([email, name]):
            return jsonify({'error': 'Email and name are required'}), 400
        
        service = auth_manager.get_authenticated_client(email, 'drive', 'v3')
        if not service:
            return jsonify({'error': 'Account not authenticated'}), 401
        
        file_metadata = {
            'name': name,
            'mimeType': 'application/vnd.google-apps.folder'
        }
        
        if data.get('parents'):
            file_metadata['parents'] = [data.get('parents')]
        
        result = service.files().create(
            body=file_metadata,
            fields='id,name'
        ).execute()
        
        return jsonify({
            'message': 'Folder created successfully',
            'folderId': result.get('id'),
            'name': result.get('name')
        }), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500

