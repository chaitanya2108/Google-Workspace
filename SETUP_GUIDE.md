# Setup Guide for Google Workspace Flask API

## Quick Start

This guide will help you set up and run the Google Workspace Flask API.

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

### Step 2: Google Cloud Console Setup

1. **Create a Project**
   - Go to https://console.cloud.google.com/
   - Create a new project or select an existing one

2. **Enable APIs**
   - Go to "APIs & Services" → "Library"
   - Search and enable these APIs:
     - Gmail API
     - Google Calendar API
     - Google Drive API
     - People API (for Contacts)
     - Google Docs API

3. **Configure OAuth Consent Screen**
   - Go to "APIs & Services" → "OAuth consent screen"
   - Choose "External" user type
   - Fill in the required information:
     - App name: "Google Workspace API"
     - User support email: your email
     - Developer contact information: your email
   - Add scopes:
     - ../auth/gmail.readonly
     - ../auth/gmail.send
     - ../auth/calendar
     - ../auth/drive
     - ../auth/documents
     - ../auth/contacts.readonly
     - ../auth/userinfo.email
     - ../auth/userinfo.profile
   - Add yourself as a test user

4. **Create OAuth Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth client ID"
   - Choose "Web application"
   - Name it "Google Workspace API"
   - Add authorized redirect URI: `http://localhost:8080/oauth/callback`
   - Click "Create"
   - Copy the Client ID and Client Secret

### Step 3: Configure Environment Variables

1. **Copy the example environment file**
   ```bash
   cp env.example .env
   ```

2. **Edit `.env` file**
   ```env
   GOOGLE_CLIENT_ID=your-client-id-from-google.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret-from-google
   GOOGLE_REDIRECT_URI=http://localhost:8080/oauth/callback
   PORT=8080
   FLASK_ENV=development
   ```

### Step 4: Run the Server

```bash
python app.py
```

The API will be available at `http://localhost:8080`

### Step 5: Authenticate Your Account

1. **Get the authentication URL**
   ```bash
   curl -X POST http://localhost:8080/api/accounts/authenticate \
     -H "Content-Type: application/json" \
     -d '{"email": "your-email@gmail.com"}'
   ```

2. **Visit the URL** returned in the response

3. **Sign in** with your Google account

4. **Grant permissions** when prompted

5. **You'll be redirected** to a success page

6. **Your account is now authenticated!**

## Testing the API

### Health Check
```bash
curl http://localhost:8080/health
```

### List Accounts
```bash
curl http://localhost:8080/api/accounts
```

### Search Emails
```bash
curl -X POST http://localhost:8080/api/gmail/search \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@gmail.com",
    "query": "is:unread",
    "maxResults": 10
  }'
```

### Create Calendar Event
```bash
curl -X POST http://localhost:8080/api/calendar/event \
  -H "Content-Type: application/json" \
  -d '{
    "email": "your-email@gmail.com",
    "summary": "Test Event",
    "start": {
      "dateTime": "2025-01-15T10:00:00Z",
      "timeZone": "UTC"
    },
    "end": {
      "dateTime": "2025-01-15T11:00:00Z",
      "timeZone": "UTC"
    }
  }'
```

## Python Example

See `example_usage.py` for Python examples using the `requests` library.

## Troubleshooting

### "Account not authenticated" error
- Make sure you've completed the OAuth flow
- Check that `config/tokens/` contains your email's token file
- Try removing and re-authenticating

### "OAuth credentials error"
- Verify `.env` file contains correct credentials
- Check that redirect URI in Google Cloud Console matches the one in `.env`

### "API not enabled" error
- Go to Google Cloud Console
- Enable the required APIs (Gmail, Calendar, Drive, People, Docs)

### Port already in use
- Change the `PORT` in `.env` file
- Kill the process using the port:
  ```bash
  # Windows
  netstat -ano | findstr :8080
  taskkill /PID <PID> /F
  
  # Linux/Mac
  lsof -ti:8080 | xargs kill
  ```

## Differences from TypeScript MCP Version

### Architecture
- **Original**: MCP (Model Context Protocol) server communicating via stdin/stdout
- **Flask Version**: REST API accessible via HTTP requests

### Communication
- **Original**: JSON-RPC 2.0 protocol for AI assistants
- **Flask Version**: RESTful HTTP API for general use

### Usage
- **Original**: Designed for Claude Desktop and AI assistants
- **Flask Version**: Can be used by any HTTP client (web apps, mobile apps, scripts)

### Setup
- **Both**: Require Google Cloud OAuth credentials
- **Flask**: Additional HTTP client for testing (curl, Postman, Python requests)

## API Documentation

For complete API documentation, see the `README.md` file in the project root.

## Next Steps

1. Start the server: `python app.py`
2. Authenticate your account using the OAuth flow
3. Test the API using curl, Postman, or the `example_usage.py` script
4. Integrate with your application

## Support

For issues or questions:
1. Check the troubleshooting section
2. Review Google Cloud Console configuration
3. Verify all environment variables are set correctly
4. Ensure all required APIs are enabled

