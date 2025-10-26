# How the Dual-Mode Server Works

## Overview

`app.py` is a **smart application** that automatically detects whether it's being run by Claude Desktop or manually, and starts the appropriate server.

## Two Modes

### 1. **MCP Mode** (Claude Desktop)
When Claude Desktop runs the app, it connects via **stdin/stdout** (non-interactive terminal)
- Detects: `sys.stdin.isatty() == False`
- Runs: MCP server for JSON-RPC communication
- Purpose: Works with Claude Desktop's AI assistant

### 2. **Flask API Mode** (Manual Run)
When you run `python app.py` manually, it starts a **Flask HTTP server**
- Detects: `sys.stdin.isatty() == True`
- Runs: Flask REST API on http://localhost:8080
- Purpose: For web apps, scripts, testing

## How It Works

```python
def is_mcp_mode():
    """Check if running in MCP mode"""
    return not sys.stdin.isatty()

if is_mcp_mode():
    # Claude Desktop is calling - run MCP server
    from mcp_server import MCPServer
    server = MCPServer()
    server.run()
else:
    # Manual run - start Flask API
    from flask import Flask
    app = Flask(__name__)
    # ... set up Flask routes ...
    app.run(host='0.0.0.0', port=8080)
```

## Using Each Mode

### MCP Mode (Claude Desktop)

**Setup:**
1. Update `claude_desktop_config.json`:
```json
{
  "mcpServers": {
    "google-workspace-mcp": {
      "command": "C:\\Users\\chait\\OneDrive\\Desktop\\Drexel University\\MSAIML Books and Materials\\Future Projects\\Google-Workspace\\.venv\\Scripts\\python.exe",
      "args": ["app.py"],
      "cwd": "C:\\Users\\chait\\OneDrive\\Desktop\\Drexel University\\MSAIML Books and Materials\\Future Projects\\Google-Workspace"
    }
  }
}
```

2. Restart Claude Desktop
3. Ask Claude: "list my workspace accounts"

**What Happens:**
- Claude Desktop spawns the Python process with stdin/stdout pipes
- `app.py` detects it's not a TTY (terminal)
- Automatically starts MCP server
- Claude can now call tools like `list_workspace_accounts`, `search_workspace_emails`, etc.

### Flask API Mode (Manual)

**Setup:**
```bash
python app.py
```

**Output:**
```
Flask API server running on http://localhost:8080
 * Running on http://0.0.0.0:8080
```

**What Happens:**
- You run the app manually from terminal
- `app.py` detects it IS a TTY (terminal)
- Starts Flask HTTP server
- Access via browser: http://localhost:8080

## API Endpoints (Flask Mode)

When running in Flask mode, you get REST API endpoints:

- `GET /health` - Health check
- `GET /` - API documentation
- `POST /api/accounts/authenticate` - Start OAuth
- `POST /api/gmail/search` - Search emails
- `POST /api/calendar/list` - List events
- etc.

## Tools (MCP Mode)

When running in MCP mode, Claude can call these tools:

- `list_workspace_accounts` - List accounts
- `authenticate_workspace_account` - Add account
- `search_workspace_emails` - Search Gmail
- `send_workspace_email` - Send email
- `list_workspace_calendar_events` - List events
- etc.

## Benefits

✅ **One codebase** - Same app works both ways  
✅ **No duplication** - Same auth manager and tools  
✅ **Easy testing** - Run Flask mode for manual testing  
✅ **Production ready** - MCP mode for Claude Desktop  
✅ **Flexible** - Choose the mode you need

## Testing

### Test MCP Mode (with Claude Desktop)
1. Update `claude_desktop_config.json`
2. Restart Claude Desktop
3. Ask: "help me manage my Gmail"

### Test Flask Mode (manually)
```bash
# Terminal 1
python app.py

# Terminal 2
curl http://localhost:8080/health
curl http://localhost:8080/api/accounts
```

## Summary

- **`python app.py`** → Starts Flask API (for manual use)
- **Claude Desktop** → Automatically starts MCP server (for AI)
- **Same code** → Works both ways automatically!

