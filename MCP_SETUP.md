# MCP Server Setup for Python

## Overview

This project now includes an MCP (Model Context Protocol) server that works with Claude Desktop, just like the TypeScript version.

## Quick Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

Make sure your `.env` file is set up:

```env
GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
GOOGLE_CLIENT_SECRET=your-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8080/oauth/callback
```

### 3. Update Claude Desktop Configuration

Edit your `claude_desktop_config.json`:

**Windows:**
```json
{
  "mcpServers": {
    "google-workspace-mcp": {
      "command": "python",
      "args": ["C:\\Users\\chait\\OneDrive\\Desktop\\Drexel University\\MSAIML Books and Materials\\Future Projects\\Google-Workspace\\mcp_server.py"],
      "cwd": "C:\\Users\\chait\\OneDrive\\Desktop\\Drexel University\\MSAIML Books and Materials\\Future Projects\\Google-Workspace",
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret",
        "GOOGLE_REDIRECT_URI": "http://localhost:8080/oauth/callback",
        "PORT": "8080"
      }
    }
  }
}
```

**macOS/Linux:**
```json
{
  "mcpServers": {
    "google-workspace-mcp": {
      "command": "python",
      "args": ["/path/to/Google-Workspace/mcp_server.py"],
      "cwd": "/path/to/Google-Workspace",
      "env": {
        "GOOGLE_CLIENT_ID": "your-client-id.apps.googleusercontent.com",
        "GOOGLE_CLIENT_SECRET": "your-client-secret",
        "GOOGLE_REDIRECT_URI": "http://localhost:8080/oauth/callback"
      }
    }
  }
}
```

### 4. Test the Server

Run the MCP server directly to test:

```bash
python mcp_server.py
```

You should see it waiting for input on stdin.

### 5. Use with Claude Desktop

1. Restart Claude Desktop after updating the config
2. Ask Claude to "list my workspace accounts"
3. Authenticate your Google account when prompted

## Differences from TypeScript Version

- **Language**: Python instead of TypeScript
- **Same Protocol**: Uses stdin/stdout JSON-RPC
- **Same Functionality**: All Google Workspace features
- **Simpler Setup**: No npm dependencies

## Troubleshooting

### "No module named 'tools'"
- Make sure you're in the correct directory
- Check that all files are in the project directory

### "Environment variables not found"
- Ensure `.env` file exists
- Check environment variables are set correctly

### Server doesn't respond
- Check Python version (3.8+)
- Look for errors in Claude Desktop logs
- Test with: `python mcp_server.py`

## Project Structure

```
Google-Workspace/
├── mcp_server.py          # Main MCP server
├── auth/
│   └── auth_manager.py    # Authentication
├── tools/
│   ├── base_tools.py     # Base class
│   ├── account_tools.py  # Account management
│   ├── gmail_tools.py    # Gmail operations
│   ├── calendar_tools.py # Calendar operations
│   ├── drive_tools.py    # Drive operations
│   ├── contacts_tools.py # Contacts operations
│   └── docs_tools.py     # Docs operations
└── .env                   # Environment variables
```

## Next Steps

The MCP server is set up! It will work with Claude Desktop just like the TypeScript version.

