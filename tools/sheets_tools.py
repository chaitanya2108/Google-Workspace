"""
Sheets tools for MCP - Full implementation
"""

from typing import List, Dict, Any
from tools.base_tools import BaseTools
import json


class SheetsTools(BaseTools):
    """Google Sheets tools"""
    
    def get_tools(self) -> List[Dict[str, Any]]:
        """Get sheets tools"""
        return [
            {
                "name": "create_workspace_spreadsheet",
                "description": "Create a new blank Google Spreadsheet",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "title": {"type": "string", "description": "Title of the spreadsheet"},
                        "parentFolderId": {"type": "string", "description": "Parent folder ID in Google Drive (optional)"}
                    },
                    "required": ["email", "title"]
                }
            },
            {
                "name": "get_sheet_values",
                "description": "Get cell values from a spreadsheet range",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "spreadsheetId": {"type": "string", "description": "ID of the spreadsheet"},
                        "range": {"type": "string", "description": "Range in A1 notation (e.g., 'Sheet1!A1:C2')"},
                        "majorDimension": {"type": "string", "enum": ["ROWS", "COLUMNS"], "description": "How to return the values"},
                        "valueRenderOption": {"type": "string", "enum": ["FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA"], "description": "How values should be rendered"}
                    },
                    "required": ["email", "spreadsheetId", "range"]
                }
            },
            {
                "name": "batch_get_sheet_values",
                "description": "Get cell values from multiple spreadsheet ranges",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "spreadsheetId": {"type": "string", "description": "ID of the spreadsheet"},
                        "ranges": {"type": "array", "items": {"type": "string"}, "description": "Array of ranges in A1 notation"},
                        "majorDimension": {"type": "string", "enum": ["ROWS", "COLUMNS"], "description": "How to return the values"},
                        "valueRenderOption": {"type": "string", "enum": ["FORMATTED_VALUE", "UNFORMATTED_VALUE", "FORMULA"], "description": "How values should be rendered"}
                    },
                    "required": ["email", "spreadsheetId", "ranges"]
                }
            },
            {
                "name": "update_sheet_values",
                "description": "Update cell values in a spreadsheet range",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "spreadsheetId": {"type": "string", "description": "ID of the spreadsheet"},
                        "range": {"type": "string", "description": "Range in A1 notation"},
                        "values": {"type": "array", "description": "2D array of values to write"},
                        "valueInputOption": {"type": "string", "enum": ["RAW", "USER_ENTERED"], "description": "How input data should be interpreted"},
                        "majorDimension": {"type": "string", "enum": ["ROWS", "COLUMNS"], "description": "The dimension along which data is written"}
                    },
                    "required": ["email", "spreadsheetId", "range", "values"]
                }
            },
            {
                "name": "batch_update_sheet_values",
                "description": "Update cell values in multiple spreadsheet ranges at once",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "spreadsheetId": {"type": "string", "description": "ID of the spreadsheet"},
                        "data": {"type": "array", "items": {"type": "object"}, "description": "Array of range and values objects"},
                        "valueInputOption": {"type": "string", "enum": ["RAW", "USER_ENTERED"], "description": "How input data should be interpreted"}
                    },
                    "required": ["email", "spreadsheetId", "data"]
                }
            },
            {
                "name": "append_sheet_values",
                "description": "Append cell values to the end of a table in a spreadsheet",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "email": {"type": "string", "description": "Email address of the account"},
                        "spreadsheetId": {"type": "string", "description": "ID of the spreadsheet"},
                        "range": {"type": "string", "description": "Range in A1 notation (used to find the table)"},
                        "values": {"type": "array", "description": "2D array of values to append"},
                        "valueInputOption": {"type": "string", "enum": ["RAW", "USER_ENTERED"], "description": "How input data should be interpreted"},
                        "insertDataOption": {"type": "string", "enum": ["OVERWRITE", "INSERT_ROWS"], "description": "Whether to overwrite or insert rows"}
                    },
                    "required": ["email", "spreadsheetId", "range", "values"]
                }
            }
        ]
    
    def has_tool(self, name: str) -> bool:
        """Check if this class handles a specific tool"""
        return name in [
            "create_workspace_spreadsheet",
            "get_sheet_values",
            "batch_get_sheet_values",
            "update_sheet_values",
            "batch_update_sheet_values",
            "append_sheet_values"
        ]
    
    def handle_tool(self, name: str, args: Dict[str, Any]) -> Dict[str, Any]:
        """Handle tool execution"""
        email = args.get("email")
        if not email:
            return {"content": [{"type": "text", "text": "Error: Email is required"}]}
        
        sheets_service = self.auth_manager.get_authenticated_client(email, "sheets", "v4")
        drive_service = self.auth_manager.get_authenticated_client(email, "drive", "v3")
        
        if not sheets_service or not drive_service:
            return {"content": [{"type": "text", "text": "Error: Account not authenticated"}]}
        
        try:
            if name == "create_workspace_spreadsheet":
                return self._create_spreadsheet(sheets_service, drive_service, args)
            elif name == "get_sheet_values":
                return self._get_values(sheets_service, args)
            elif name == "batch_get_sheet_values":
                return self._batch_get_values(sheets_service, args)
            elif name == "update_sheet_values":
                return self._update_values(sheets_service, args)
            elif name == "batch_update_sheet_values":
                return self._batch_update_values(sheets_service, args)
            elif name == "append_sheet_values":
                return self._append_values(sheets_service, args)
            else:
                return {"content": [{"type": "text", "text": f"Error: Unknown tool: {name}"}]}
        except Exception as e:
            return {"content": [{"type": "text", "text": f"Error: {str(e)}"}]}
    
    def _create_spreadsheet(self, sheets_service, drive_service, args):
        """Create a new Google Spreadsheet"""
        spreadsheet = {
            'properties': {
                'title': args['title']
            }
        }
        
        response = sheets_service.spreadsheets().create(body=spreadsheet, fields='spreadsheetId').execute()
        spreadsheet_id = response['spreadsheetId']
        
        # If a parent folder is specified, move the spreadsheet there
        if args.get('parentFolderId'):
            drive_service.files().update(
                fileId=spreadsheet_id,
                addParents=args['parentFolderId'],
                removeParents='root',
                fields='id, parents'
            ).execute()
        
        return {"content": [{"type": "text", "text": f"Spreadsheet created successfully!\n\nSpreadsheet ID: {spreadsheet_id}\nTitle: {args['title']}\nURL: https://docs.google.com/spreadsheets/d/{spreadsheet_id}/edit"}]}
    
    def _get_values(self, sheets_service, args):
        """Get values from a single range"""
        params = {
            'spreadsheetId': args['spreadsheetId'],
            'range': args['range']
        }
        if args.get('majorDimension'):
            params['majorDimension'] = args['majorDimension']
        if args.get('valueRenderOption'):
            params['valueRenderOption'] = args['valueRenderOption']
        
        result = sheets_service.spreadsheets().values().get(**params).execute()
        num_rows = len(result.get('values', []))
        
        return {"content": [{"type": "text", "text": json.dumps({
            "values": result.get('values', []),
            "range": result.get('range', ''),
            "numRows": num_rows
        }, indent=2)}]}
    
    def _batch_get_values(self, sheets_service, args):
        """Get values from multiple ranges"""
        params = {
            'spreadsheetId': args['spreadsheetId'],
            'ranges': args['ranges']
        }
        if args.get('majorDimension'):
            params['majorDimension'] = args['majorDimension']
        if args.get('valueRenderOption'):
            params['valueRenderOption'] = args['valueRenderOption']
        
        result = sheets_service.spreadsheets().values().batchGet(**params).execute()
        ranges = result.get('valueRanges', [])
        
        return {"content": [{"type": "text", "text": json.dumps({
            "valueRanges": [{'range': v['range'], 'values': v.get('values', [])} for v in ranges],
            "spreadsheetId": result.get('spreadsheetId', '')
        }, indent=2)}]}
    
    def _update_values(self, sheets_service, args):
        """Update values in a single range"""
        body = {
            'values': args['values']
        }
        if args.get('majorDimension'):
            body['majorDimension'] = args['majorDimension']
        
        params = {
            'spreadsheetId': args['spreadsheetId'],
            'range': args['range'],
            'valueInputOption': args.get('valueInputOption', 'RAW'),
            'body': body
        }
        
        result = sheets_service.spreadsheets().values().update(**params).execute()
        
        return {"content": [{"type": "text", "text": f"Successfully updated {result.get('updatedCells', 0)} cells"}]}
    
    def _batch_update_values(self, sheets_service, args):
        """Update values in multiple ranges"""
        body = {
            'valueInputOption': args.get('valueInputOption', 'RAW'),
            'data': args['data']
        }
        
        result = sheets_service.spreadsheets().values().batchUpdate(
            spreadsheetId=args['spreadsheetId'],
            body=body
        ).execute()
        
        return {"content": [{"type": "text", "text": f"Successfully updated {result.get('totalUpdatedCells', 0)} cells across {len(args['data'])} ranges"}]}
    
    def _append_values(self, sheets_service, args):
        """Append values to a table"""
        body = {
            'values': args['values']
        }
        
        params = {
            'spreadsheetId': args['spreadsheetId'],
            'range': args['range'],
            'valueInputOption': args.get('valueInputOption', 'RAW'),
            'body': body
        }
        
        if args.get('insertDataOption'):
            params['insertDataOption'] = args['insertDataOption']
        
        result = sheets_service.spreadsheets().values().append(**params).execute()
        updates = result.get('updates', {})
        
        return {"content": [{"type": "text", "text": f"Successfully appended {updates.get('updatedCells', 0)} cells. Updated range: {updates.get('updatedRange', '')}"}]}

