# TypeScript MCP vs Python Flask - Comparison Guide

This document compares the original TypeScript MCP server with the Python Flask version.

## Architecture Comparison

### TypeScript MCP Version
```
User Request
    ↓
Claude Desktop (MCP Client)
    ↓ (stdin/stdout JSON-RPC)
MCP Server (index.ts)
    ↓
Tool Handlers
    ↓
AuthManager → Google APIs
```

**Communication**: JSON-RPC 2.0 over stdin/stdout  
**Protocol**: MCP (Model Context Protocol)  
**Target**: AI Assistants (Claude Desktop, Cline)  
**Language**: TypeScript/Node.js

### Python Flask Version
```
User Request
    ↓
HTTP Client (browser, curl, Postman, etc.)
    ↓ (HTTP REST API)
Flask Server (app.py)
    ↓
Route Handlers
    ↓
AuthManager → Google APIs
```

**Communication**: HTTP REST API  
**Protocol**: REST  
**Target**: General purpose (web apps, mobile apps, scripts)  
**Language**: Python

## Feature Comparison

| Feature | TypeScript MCP | Python Flask |
|---------|---------------|--------------|
| Gmail Operations | ✅ | ✅ |
| Calendar Operations | ✅ | ✅ |
| Drive Operations | ✅ | ✅ |
| Contacts Operations | ✅ | ✅ |
| Google Docs | ✅ | ✅ |
| OAuth 2.0 Auth | ✅ | ✅ |
| Multi-Account Support | ✅ | ✅ |
| Token Storage | ✅ | ✅ |
| Automatic Token Refresh | ✅ | ✅ |

## API Comparison

### TypeScript MCP - Tool-based
```typescript
// Tools are called by name with arguments
{
  "method": "tools/call",
  "params": {
    "name": "search_workspace_emails",
    "arguments": {
      "email": "user@gmail.com",
      "query": "is:unread"
    }
  }
}
```

### Python Flask - REST API
```python
# HTTP POST requests to endpoints
POST /api/gmail/search
Content-Type: application/json

{
  "email": "user@gmail.com",
  "query": "is:unread",
  "maxResults": 10
}
```

## Usage Examples

### Original TypeScript MCP

```javascript
// Configured in Claude Desktop
{
  "mcpServers": {
    "google-workspace-mcp": {
      "command": "node",
      "args": ["path/to/dist/index.js"],
      "env": {
        "GOOGLE_CLIENT_ID": "...",
        "GOOGLE_CLIENT_SECRET": "..."
      }
    }
  }
}

// Used via Claude Desktop
// You: "Show me my unread emails"
// Claude calls the search_workspace_emails tool automatically
```

### Python Flask

```python
# Using requests library
import requests

response = requests.post(
    "http://localhost:8080/api/gmail/search",
    json={
        "email": "user@gmail.com",
        "query": "is:unread",
        "maxResults": 10
    }
)

print(response.json())
```

## Key Differences

### 1. Communication Protocol

**TypeScript MCP:**
- Uses JSON-RPC 2.0
- Communication via stdin/stdout
- Designed for subprocess execution
- AI assistant specific

**Python Flask:**
- Uses HTTP REST API
- Communication via HTTP requests
- Standard web API pattern
- General purpose

### 2. Client Type

**TypeScript MCP:**
- Configured in MCP clients (Claude Desktop, Cline)
- Automatic tool discovery
- AI assistant integration

**Python Flask:**
- Any HTTP client
- REST endpoints
- Manual API calls

### 3. Response Format

**TypeScript MCP:**
```typescript
// Tool definition for AI
{
  name: 'search_workspace_emails',
  description: 'Search emails in Gmail',
  inputSchema: { /* schema */ }
}

// Response
{
  content: [{
    type: 'text',
    text: JSON.stringify(results)
  }]
}
```

**Python Flask:**
```python
# Standard JSON response
{
  "messages": [...],
  "total": 10,
  "query": "is:unread"
}
```

## Migration Guide

### From TypeScript MCP to Python Flask

1. **Setup**
   - Instead of Node.js, install Python 3.8+
   - Install dependencies: `pip install -r requirements.txt`
   - Copy `env.example` to `.env` and configure

2. **Running**
   - TypeScript: `npm start`
   - Flask: `python app.py`

3. **Authentication**
   - Both use OAuth 2.0
   - Both redirect to localhost:8080/oauth/callback
   - Both store tokens in `config/tokens/`

4. **Using the API**
   - TypeScript: Used automatically by Claude
   - Flask: Make HTTP requests or use `example_usage.py`

## When to Use Each Version

### Use TypeScript MCP when:
- Building for Claude Desktop or AI assistants
- Need automatic tool discovery
- Want MCP protocol benefits
- Prefer TypeScript/Node.js ecosystem

### Use Python Flask when:
- Building web applications
- Need a general-purpose API
- Want HTTP-based integration
- Prefer Python ecosystem
- Building mobile applications

## Performance

Both versions are similar in performance:
- OAuth authentication: Same flow
- API calls: Same Google API libraries
- Token management: Same logic
- File operations: Similar performance

The main difference is the protocol overhead:
- TypeScript MCP: stdin/stdout (lower overhead)
- Python Flask: HTTP requests (more standard, more flexible)

## Security

Both versions:
- ✅ Store tokens securely in `config/tokens/`
- ✅ Use environment variables for credentials
- ✅ Support token refresh
- ✅ Support multiple accounts
- ✅ No credentials in code

Python Flask additionally:
- ✅ CORS configuration
- ✅ HTTP-based (can add rate limiting)
- ✅ Can deploy with HTTPS

## Development

### TypeScript MCP
```bash
npm install
npm run dev
npm run build
```

### Python Flask
```bash
pip install -r requirements.txt
python app.py
```

Both have similar development experience with hot reload in development mode.

## Conclusion

Both versions provide the same core functionality:
- Google Workspace integration
- OAuth 2.0 authentication
- Gmail, Calendar, Drive, Contacts, Docs
- Multi-account support

**Choose TypeScript MCP** if you're building for AI assistants like Claude Desktop.

**Choose Python Flask** if you need a general-purpose REST API for web/mobile apps or scripts.

