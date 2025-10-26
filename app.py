"""
MCP Server for Google Workspace Integration
When run directly, starts the MCP server for Claude Desktop
"""

import sys
import os

# Check if running in MCP mode (Claude Desktop)
# This is detected by checking if stdin is not a TTY (interactive terminal)
def is_mcp_mode():
    """Check if running in MCP mode"""
    return not sys.stdin.isatty()

if is_mcp_mode():
    # Import and run MCP server
    from mcp_server import MCPServer
    
    server = MCPServer()
    server.run()
else:
    # Import and run Flask API for HTTP access
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    from dotenv import load_dotenv
    from auth.auth_manager import AuthManager
    from routes import gmail_routes, calendar_routes, drive_routes, contacts_routes, account_routes, docs_routes
    
    # Load environment variables
    load_dotenv()
    
    # Initialize Flask app
    app = Flask(__name__)
    CORS(app)
    
    # Initialize auth manager
    auth_manager = AuthManager()
    
    # Register blueprints
    app.register_blueprint(account_routes.bp)
    app.register_blueprint(gmail_routes.bp)
    app.register_blueprint(calendar_routes.bp)
    app.register_blueprint(drive_routes.bp)
    app.register_blueprint(contacts_routes.bp)
    app.register_blueprint(docs_routes.bp)
    
    # Health check endpoint
    @app.route('/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify({
            'status': 'ok',
            'timestamp': __import__('datetime').datetime.now().isoformat()
        })
    
    # OAuth callback endpoint
    @app.route('/oauth/callback', methods=['GET'])
    def oauth_callback():
        """Handle OAuth callback from Google"""
        try:
            code = request.args.get('code')
            state = request.args.get('state')
            
            if not code or not state:
                return jsonify({'error': 'Missing authorization code or state'}), 400
            
            result = auth_manager.handle_oauth_callback(code, state)
            
            if result['success']:
                return """
                    <html>
                        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 50px auto; padding: 20px;">
                            <h1 style="color: #4CAF50;">✅ Authentication Successful!</h1>
                            <p>Your Google account has been successfully authenticated.</p>
                            <p><strong>Authorization code:</strong> <code style="background: #f0f0f0; padding: 5px; border-radius: 3px;">{}</code></p>
                            <p>You can now close this window and return to your API client.</p>
                            <script>
                                setTimeout(function() {{
                                    window.close();
                                }}, 3000);
                            </script>
                        </body>
                    </html>
                """.format(code), 200
            else:
                return jsonify({'error': f'Authentication failed: {result.get("error")}'}), 400
        except Exception as e:
            return jsonify({'error': f'Internal server error: {str(e)}'}), 500
    
    @app.route('/')
    def index():
        """API information page"""
        return """
        <html>
            <head><title>Google Workspace API</title></head>
            <body style="font-family: Arial, sans-serif; max-width: 800px; margin: 50px auto; padding: 20px;">
                <h1>Google Workspace API</h1>
                <p>This API provides access to Google Workspace services including Gmail, Calendar, Drive, and Contacts.</p>
                <h2>Available Endpoints:</h2>
                <ul>
                    <li><strong>Account Management</strong>:
                        <ul>
                            <li>GET /api/accounts - List all accounts</li>
                            <li>POST /api/accounts/authenticate - Start authentication</li>
                            <li>DELETE /api/accounts/<email> - Remove account</li>
                        </ul>
                    </li>
                    <li><strong>Gmail Operations</strong>:
                        <ul>
                            <li>POST /api/gmail/search - Search emails</li>
                            <li>POST /api/gmail/send - Send email</li>
                            <li>POST /api/gmail/draft - Manage drafts</li>
                            <li>POST /api/gmail/label - Manage labels</li>
                        </ul>
                    </li>
                    <li><strong>Calendar Operations</strong>:
                        <ul>
                            <li>POST /api/calendar/list - List events</li>
                            <li>GET /api/calendar/event/<event_id> - Get event</li>
                            <li>POST /api/calendar/event - Create event</li>
                            <li>PUT /api/calendar/event/<event_id> - Update event</li>
                            <li>DELETE /api/calendar/event/<event_id> - Delete event</li>
                        </ul>
                    </li>
                    <li><strong>Drive Operations</strong>:
                        <ul>
                            <li>POST /api/drive/list - List files</li>
                            <li>POST /api/drive/search - Search files</li>
                            <li>POST /api/drive/upload - Upload file</li>
                            <li>GET /api/drive/download/<file_id> - Download file</li>
                            <li>DELETE /api/drive/file/<file_id> - Delete file</li>
                        </ul>
                    </li>
                    <li><strong>Contacts Operations</strong>:
                        <ul>
                            <li>POST /api/contacts/list - Get contacts</li>
                        </ul>
                    </li>
                </ul>
                <h2>Health Check:</h2>
                <p>Visit <a href="/health">/health</a> to check if the API is running.</p>
            </body>
        </html>
        """, 200
    
    if __name__ == '__main__':
        port = int(os.getenv('PORT', 8080))
        print(f"Flask API server running on http://localhost:{port}")
        app.run(host='0.0.0.0', port=port, debug=True)

