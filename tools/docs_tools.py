"""
Docs tools for MCP - Full implementation
"""

from typing import List, Dict, Any
from tools.base_tools import BaseTools
import json


class DocsTools(BaseTools):
    """Docs tools"""
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get docs tools"""
        return [
            {
                "name": "create_workspace_document",
                "description": "Create a new blank Google Doc document",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "title": {"type": "string", "description": "Title of the document"},
                        "parentFolderId": {"type": "string", "description": "Parent folder ID in Google Drive (optional)"}
                    },
                    "required": ["email", "title"]
                }
            },
            {
                "name": "copy_workspace_document",
                "description": "Copy an existing Google Doc to create a new document",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "documentId": {"type": "string", "description": "ID of the document to copy"},
                        "newTitle": {"type": "string", "description": "Title for the copied document"}
                    },
                    "required": ["email", "documentId", "newTitle"]
                }
            },
            {
                "name": "get_workspace_document",
                "description": "Get the content and metadata of a Google Doc",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "documentId": {"type": "string", "description": "ID of the document"},
                        "suggestionsViewMode": {"type": "string", "enum": ["DEFAULT_FOR_CURRENT_ACCESS", "SUGGESTIONS_INLINE", "SUGGESTIONS_IN_DIALOG", "PREVIEW_WITHOUT_SUGGESTIONS"], "description": "Controls whether suggestions in the document are shown"}
                    },
                    "required": ["email", "documentId"]
                }
            },
            {
                "name": "list_workspace_documents",
                "description": "List all Google Docs documents",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "pageSize": {"type": "number", "description": "Number of documents to return (default: 10)"},
                        "pageToken": {"type": "string", "description": "Token for pagination"},
                        "q": {"type": "string", "description": "Query string for filtering documents"}
                    },
                    "required": ["email"]
                }
            },
            {
                "name": "insert_text_into_document",
                "description": "Insert text into a Google Doc at a specific index location",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "documentId": {"type": "string", "description": "ID of the document"},
                        "text": {"type": "string", "description": "Text to insert"},
                        "index": {"type": "number", "description": "Index location to insert text (UTF-16 code units)"},
                        "tabId": {"type": "string", "description": "Tab ID (optional, defaults to body)"}
                    },
                    "required": ["email", "documentId", "text", "index"]
                }
            },
            {
                "name": "delete_text_from_document",
                "description": "Delete text from a Google Doc between two index locations",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "documentId": {"type": "string", "description": "ID of the document"},
                        "startIndex": {"type": "number", "description": "Start index of text to delete"},
                        "endIndex": {"type": "number", "description": "End index of text to delete"},
                        "tabId": {"type": "string", "description": "Tab ID (optional, defaults to body)"}
                    },
                    "required": ["email", "documentId", "startIndex", "endIndex"]
                }
            },
            {
                "name": "batch_update_document",
                "description": "Perform multiple document edits in a single batch operation",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "documentId": {"type": "string", "description": "ID of the document"},
                        "requests": {"type": "array", "description": "Array of edit requests to perform"}
                    },
                    "required": ["email", "documentId", "requests"]
                }
            }
        ]
    
    def has_tool(self, name: str) -> bool:
        """Check if this class handles a specific tool"""
        return name in [
            "create_workspace_document",
            "copy_workspace_document",
            "get_workspace_document",
            "list_workspace_documents",
            "insert_text_into_document",
            "delete_text_from_document",
            "batch_update_document"
        ]
    
    def handle_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution"""
        email = args.get("email")
        if not email:
            return {"content": [{"type": "text", "text": "Error: Email is required"}]}
        
        docs_service = self.auth_manager.get_authenticated_client(email, "docs", "v1")
        drive_service = self.auth_manager.get_authenticated_client(email, "drive", "v3")
        
        if not docs_service or not drive_service:
            return {"content": [{"type": "text", "text": "Error: Account not authenticated"}]}
        
        try:
            if name == "create_workspace_document":
                return self._create_document(docs_service, drive_service, args)
            elif name == "copy_workspace_document":
                return self._copy_document(drive_service, args)
            elif name == "get_workspace_document":
                return self._get_document(docs_service, args)
            elif name == "list_workspace_documents":
                return self._list_documents(drive_service, args)
            elif name == "insert_text_into_document":
                return self._insert_text(docs_service, args)
            elif name == "delete_text_from_document":
                return self._delete_text(docs_service, args)
            elif name == "batch_update_document":
                return self._batch_update(docs_service, args)
            else:
                return {"content": [{"type": "text", "text": f"Error: Unknown tool: {name}"}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}
    
    def _create_document(self, docs_service, drive_service, args):
        """Create a new Google Doc"""
        document = {'title': args['title']}
        
        response = docs_service.documents().create(body=document).execute()
        document_id = response['documentId']
        
        # If a parent folder is specified, move the document there
        if args.get('parentFolderId'):
            drive_service.files().update(
                fileId=document_id,
                addParents=args['parentFolderId'],
                removeParents='root',
                fields='id, parents'
            ).execute()
        
        return {"content": [{"type": "text", "text": f"Document created successfully!\n\nDocument ID: {document_id}\nTitle: {args['title']}\nURL: https://docs.google.com/document/d/{document_id}/edit"}]}
    
    def _copy_document(self, drive_service, args):
        """Copy an existing Google Doc"""
        copy_metadata = {'name': args['newTitle']}
        
        response = drive_service.files().copy(fileId=args['documentId'], body=copy_metadata).execute()
        new_document_id = response['id']
        
        return {"content": [{"type": "text", "text": f"Document copied successfully!\n\nOriginal Document ID: {args['documentId']}\nNew Document ID: {new_document_id}\nTitle: {args['newTitle']}\nURL: https://docs.google.com/document/d/{new_document_id}/edit"}]}
    
    def _get_document(self, docs_service, args):
        """Get a Google Doc"""
        params = {'documentId': args['documentId']}
        if args.get('suggestionsViewMode'):
            params['suggestionsViewMode'] = args['suggestionsViewMode']
        
        response = docs_service.documents().get(**params).execute()
        
        # Extract text content from the document
        content = []
        if 'body' in response and 'content' in response['body']:
            for element in response['body']['content']:
                if 'paragraph' in element:
                    text = ''
                    if 'elements' in element['paragraph']:
                        for el in element['paragraph']['elements']:
                            if 'textRun' in el and 'content' in el['textRun']:
                                text += el['textRun']['content']
                    if text.strip():
                        content.append(text)
        
        return {"content": [{"type": "text", "text": json.dumps({
            "title": response.get('title', ''),
            "documentId": response.get('documentId', ''),
            "content": '\n'.join(content),
            "fullMetadata": response
        }, indent=2)}]}
    
    def _list_documents(self, drive_service, args):
        """List all Google Docs"""
        params = {
            'q': args.get('q', "mimeType='application/vnd.google-apps.document'"),
            'pageSize': args.get('pageSize', 10),
            'fields': 'nextPageToken, files(id, name, createdTime, modifiedTime, parents, webViewLink)'
        }
        if args.get('pageToken'):
            params['pageToken'] = args['pageToken']
        
        response = drive_service.files().list(**params).execute()
        files = response.get('files', [])
        
        return {"content": [{"type": "text", "text": json.dumps({
            "documents": [{'id': f['id'], 'name': f['name'], 'createdTime': f.get('createdTime', ''), 'modifiedTime': f.get('modifiedTime', ''), 'url': f.get('webViewLink', '')} for f in files],
            "nextPageToken": response.get('nextPageToken'),
            "total": len(files)
        }, indent=2)}]}
    
    def _insert_text(self, docs_service, args):
        """Insert text into a Google Doc"""
        location = {'index': args['index']}
        if args.get('tabId'):
            location['tabId'] = args['tabId']
        
        requests = [{
            'insertText': {
                'location': location,
                'text': args['text']
            }
        }]
        
        response = docs_service.documents().batchUpdate(
            documentId=args['documentId'],
            body={'requests': requests}
        ).execute()
        
        return {"content": [{"type": "text", "text": f"Text inserted successfully at index {args['index']}"}]}
    
    def _delete_text(self, docs_service, args):
        """Delete text from a Google Doc"""
        range_obj = {
            'startIndex': args['startIndex'],
            'endIndex': args['endIndex']
        }
        if args.get('tabId'):
            range_obj['tabId'] = args['tabId']
        
        requests = [{
            'deleteContentRange': {
                'range': range_obj
            }
        }]
        
        response = docs_service.documents().batchUpdate(
            documentId=args['documentId'],
            body={'requests': requests}
        ).execute()
        
        return {"content": [{"type": "text", "text": f"Text deleted successfully from index {args['startIndex']} to {args['endIndex']}"}]}
    
    def _batch_update(self, docs_service, args):
        """Perform batch update with multiple edit requests"""
        response = docs_service.documents().batchUpdate(
            documentId=args['documentId'],
            body={'requests': args['requests']}
        ).execute()
        
        return {"content": [{"type": "text", "text": f"Batch update completed successfully. {len(args['requests'])} requests processed."}]}
