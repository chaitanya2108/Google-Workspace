"""
Drive tools for MCP - Full implementation
"""

from typing import List, Dict, Any
from tools.base_tools import BaseTools
from pathlib import Path
import json
import os


class DriveTools(BaseTools):
    """Drive tools"""
    
    def __init__(self, auth_manager):
        """Initialize Drive tools with workspace directory"""
        super().__init__(auth_manager)
        self.workspace_dir = Path('workspace')
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get drive tools"""
        return [
            {
                "name": "list_drive_files",
                "description": "List files in Google Drive with filtering and pagination",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "pageSize": {"type": "number", "description": "Number of files to return (default: 10)"},
                        "pageToken": {"type": "string", "description": "Token for pagination"},
                        "q": {"type": "string", "description": "Query string for filtering files"},
                        "orderBy": {"type": "string", "description": "Order by field (e.g., 'name', 'modifiedTime', 'createdTime')"},
                        "fields": {"type": "string", "description": "Fields to include in response"}
                    },
                    "required": ["email"]
                }
            },
            {
                "name": "search_drive_files",
                "description": "Full-text search across Drive content",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "query": {"type": "string", "description": "Search query"},
                        "pageSize": {"type": "number", "description": "Number of results to return (default: 10)"},
                        "pageToken": {"type": "string", "description": "Token for pagination"}
                    },
                    "required": ["email", "query"]
                }
            },
            {
                "name": "upload_drive_file",
                "description": "Upload files to Google Drive with metadata and permissions",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "filePath": {"type": "string", "description": "Local file path to upload"},
                        "name": {"type": "string", "description": "Name for the file in Drive (optional)"},
                        "parents": {"type": "array", "items": {"type": "string"}, "description": "Parent folder IDs"},
                        "description": {"type": "string", "description": "File description"},
                        "mimeType": {"type": "string", "description": "MIME type of the file"}
                    },
                    "required": ["email", "filePath"]
                }
            },
            {
                "name": "download_drive_file",
                "description": "Download files from Google Drive with format conversion",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "fileId": {"type": "string", "description": "Google Drive file ID"},
                        "mimeType": {"type": "string", "description": "MIME type for export (for Google Docs/Sheets/Slides)"},
                        "localPath": {"type": "string", "description": "Local path to save the file (optional)"}
                    },
                    "required": ["email", "fileId"]
                }
            },
            {
                "name": "delete_drive_file",
                "description": "Delete files and folders from Google Drive",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "fileId": {"type": "string", "description": "Google Drive file ID"}
                    },
                    "required": ["email", "fileId"]
                }
            },
            {
                "name": "create_drive_folder",
                "description": "Create organized folder structures in Google Drive",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "name": {"type": "string", "description": "Folder name"},
                        "parents": {"type": "array", "items": {"type": "string"}, "description": "Parent folder IDs"},
                        "description": {"type": "string", "description": "Folder description"}
                    },
                    "required": ["email", "name"]
                }
            },
            {
                "name": "update_drive_permissions",
                "description": "Manage file sharing and permissions in Google Drive",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "fileId": {"type": "string", "description": "Google Drive file ID"},
                        "action": {"type": "string", "enum": ["add", "remove", "update", "list"], "description": "Action to perform on permissions"},
                        "permissionId": {"type": "string", "description": "Permission ID (for remove/update actions)"},
                        "role": {"type": "string", "enum": ["owner", "organizer", "fileOrganizer", "writer", "commenter", "reader"], "description": "Permission role"},
                        "type": {"type": "string", "enum": ["user", "group", "domain", "anyone"], "description": "Permission type"},
                        "emailAddress": {"type": "string", "description": "Email address for user/group permissions"},
                        "domain": {"type": "string", "description": "Domain for domain permissions"},
                        "allowFileDiscovery": {"type": "boolean", "description": "Whether to allow file discovery"}
                    },
                    "required": ["email", "fileId", "action"]
                }
            }
        ]
    
    def has_tool(self, name: str) -> bool:
        """Check if this class handles a specific tool"""
        return name in [
            "list_drive_files",
            "search_drive_files",
            "upload_drive_file",
            "download_drive_file",
            "delete_drive_file",
            "create_drive_folder",
            "update_drive_permissions"
        ]
    
    def handle_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution"""
        email = args.get("email")
        if not email:
            return {"content": [{"type": "text", "text": "Error: Email is required"}]}
        
        service = self.auth_manager.get_authenticated_client(email, "drive", "v3")
        if not service:
            return {"content": [{"type": "text", "text": "Error: Account not authenticated"}]}
        
        try:
            if name == "list_drive_files":
                return self._list_files(service, args)
            elif name == "search_drive_files":
                return self._search_files(service, args)
            elif name == "upload_drive_file":
                return self._upload_file(service, args)
            elif name == "download_drive_file":
                return self._download_file(service, args)
            elif name == "delete_drive_file":
                return self._delete_file(service, args)
            elif name == "create_drive_folder":
                return self._create_folder(service, args)
            elif name == "update_drive_permissions":
                return self._update_permissions(service, args)
            else:
                return {"content": [{"type": "text", "text": f"Error: Unknown tool: {name}"}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}
    
    def _list_files(self, service, args):
        """List files in Google Drive"""
        params = {
            'pageSize': args.get('pageSize', 10),
            'fields': args.get('fields', 'nextPageToken, files(id, name, mimeType, size, modifiedTime, createdTime, parents)')
        }
        if args.get('pageToken'):
            params['pageToken'] = args['pageToken']
        if args.get('q'):
            params['q'] = args['q']
        if args.get('orderBy'):
            params['orderBy'] = args['orderBy']
        
        response = service.files().list(**params).execute()
        files = response.get('files', [])
        
        return {"content": [{"type": "text", "text": json.dumps({
            "files": files,
            "nextPageToken": response.get('nextPageToken'),
            "total": len(files)
        }, indent=2)}]}
    
    def _search_files(self, service, args):
        """Search files in Google Drive"""
        params = {
            'q': f"fullText contains '{args['query']}'",
            'pageSize': args.get('pageSize', 10),
            'fields': 'nextPageToken, files(id, name, mimeType, size, modifiedTime, createdTime, parents)'
        }
        if args.get('pageToken'):
            params['pageToken'] = args['pageToken']
        
        response = service.files().list(**params).execute()
        files = response.get('files', [])
        
        return {"content": [{"type": "text", "text": json.dumps({
            "files": files,
            "nextPageToken": response.get('nextPageToken'),
            "total": len(files),
            "query": args['query']
        }, indent=2)}]}
    
    def _upload_file(self, service, args):
        """Upload file to Google Drive"""
        file_path = args['filePath']
        file_name = args.get('name') or Path(file_path).name
        
        metadata = {'name': file_name}
        if args.get('description'):
            metadata['description'] = args['description']
        if args.get('parents'):
            metadata['parents'] = args['parents']
        
        from googleapiclient.http import MediaFileUpload
        media = MediaFileUpload(file_path, mimetype=args.get('mimeType', 'application/octet-stream'), resumable=True)
        
        file = service.files().create(body=metadata, media_body=media, fields='id, name, mimeType, size, parents').execute()
        
        return {"content": [{"type": "text", "text": f"File uploaded successfully. File ID: {file.get('id')}, Name: {file.get('name')}"}]}
    
    def _download_file(self, service, args):
        """Download file from Google Drive"""
        # Get file metadata
        file_metadata = service.files().get(fileId=args['fileId'], fields='name, mimeType').execute()
        file_name = file_metadata.get('name')
        mime_type = file_metadata.get('mimeType')
        
        # Determine if we need to export (for Google Docs/Sheets/Slides)
        is_google_doc = 'google-apps' in mime_type
        download_mime_type = args.get('mimeType') or ('application/pdf' if is_google_doc else mime_type)
        
        # Download file
        user_dir = self.workspace_dir / args['email'] / 'downloads'
        user_dir.mkdir(parents=True, exist_ok=True)
        local_path = args.get('localPath') or str(user_dir / file_name)
        
        from googleapiclient.http import MediaIoBaseDownload
        import io
        
        if is_google_doc:
            # Export the file
            request = service.files().export_media(fileId=args['fileId'], mimeType=download_mime_type)
        else:
            # Download the file
            request = service.files().get_media(fileId=args['fileId'])
        
        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
        
        # Save to file
        with open(local_path, 'wb') as f:
            f.write(fh.getvalue())
        
        return {"content": [{"type": "text", "text": f"File downloaded successfully to: {local_path}"}]}
    
    def _delete_file(self, service, args):
        """Delete file from Google Drive"""
        service.files().delete(fileId=args['fileId']).execute()
        return {"content": [{"type": "text", "text": f"File deleted successfully. File ID: {args['fileId']}"}]}
    
    def _create_folder(self, service, args):
        """Create folder in Google Drive"""
        metadata = {
            'name': args['name'],
            'mimeType': 'application/vnd.google-apps.folder'
        }
        if args.get('description'):
            metadata['description'] = args['description']
        if args.get('parents'):
            metadata['parents'] = args['parents']
        
        file = service.files().create(body=metadata, fields='id, name, parents').execute()
        return {"content": [{"type": "text", "text": f"Folder created successfully. Folder ID: {file.get('id')}, Name: {file.get('name')}"}]}
    
    def _update_permissions(self, service, args):
        """Update file permissions"""
        action = args['action']
        if action == 'list':
            response = service.permissions().list(fileId=args['fileId'], fields='permissions(id, type, role, emailAddress, domain, allowFileDiscovery)').execute()
            return {"content": [{"type": "text", "text": json.dumps(response, indent=2)}]}
        elif action == 'add':
            permission = {'role': args['role'], 'type': args['type']}
            if args.get('emailAddress'):
                permission['emailAddress'] = args['emailAddress']
            if args.get('domain'):
                permission['domain'] = args['domain']
            if args.get('allowFileDiscovery') is not None:
                permission['allowFileDiscovery'] = args['allowFileDiscovery']
            
            response = service.permissions().create(fileId=args['fileId'], body=permission).execute()
            return {"content": [{"type": "text", "text": f"Permission added successfully. Permission ID: {response.get('id')}"}]}
        elif action == 'remove':
            service.permissions().delete(fileId=args['fileId'], permissionId=args['permissionId']).execute()
            return {"content": [{"type": "text", "text": "Permission removed successfully."}]}
        elif action == 'update':
            permission = {'role': args['role']}
            if args.get('allowFileDiscovery') is not None:
                permission['allowFileDiscovery'] = args['allowFileDiscovery']
            response = service.permissions().update(fileId=args['fileId'], permissionId=args['permissionId'], body=permission).execute()
            return {"content": [{"type": "text", "text": f"Permission updated successfully. Permission ID: {response.get('id')}"}]}
        else:
            return {"content": [{"type": "text", "text": f"Error: Unknown permission action: {action}"}]}
