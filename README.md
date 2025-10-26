# Google Workspace Flask API

A Python Flask API for integrating with Google Workspace services, providing authenticated access to Gmail, Calendar, Drive, Contacts, and Google Docs.

## Features

- **OAuth 2.0 Authentication**: Secure authentication with Google Workspace accounts
- **Gmail Integration**: Send emails, search messages, manage drafts and labels
- **Calendar Management**: Create, update, and manage calendar events
- **Drive Operations**: Upload, download, and manage files and folders
- **Contacts Access**: Retrieve and search contact information
- **Google Docs Integration**: Create and manage Google Docs
- **Multi-Account Support**: Manage multiple Google Workspace accounts

## Prerequisites

- Python 3.8 or higher
- Google Cloud Project with OAuth credentials
- Enabled Google Workspace APIs

## Quick Start

### 1. Clone and Setup

```bash
# Install dependencies
pip install -r requirements.txt
```

### 2. Google Cloud Setup

1. **Create a Google Cloud Project**:
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one

2. **Enable Required APIs**:
   - Gmail API
   - Google Calendar API
   - Google Drive API
   - People API (for Contacts)
   - Google Docs API

3. **Configure OAuth Consent Screen**:
   - Go to APIs & Services → OAuth consent screen
   - Choose "External" user type
   - Fill in required fields
   - Add yourself as a test user

4. **Create OAuth Credentials**:
   - Go to APIs & Services → Credentials
   - Create OAuth 2.0 Client ID
   - Choose "Web application"
   - Set redirect URI to: `http://localhost:8080/oauth/callback`

### 3. Configuration

1. **Environment Setup**:
   ```bash
   cp .env.example .env
   ```

2. **Edit `.env` file**:
   ```env
   GOOGLE_CLIENT_ID=your-client-id.apps.googleusercontent.com
   GOOGLE_CLIENT_SECRET=your-client-secret
   GOOGLE_REDIRECT_URI=http://localhost:8080/oauth/callback
   PORT=8080
   ```

### 4. Run the Server

```bash
python app.py
```

The API will be available at `http://localhost:8080`

## API Endpoints

### Account Management

#### List Accounts
```http
GET /api/accounts
```
Returns all configured accounts and their authentication status.

#### Authenticate Account
```http
POST /api/accounts/authenticate
Content-Type: application/json

{
  "email": "optional@example.com"
}
```
Returns an OAuth URL to visit for authentication.

#### Remove Account
```http
DELETE /api/accounts/{email}
```
Removes an account and its associated tokens.

### Gmail Operations

#### Search Emails
```http
POST /api/gmail/search
Content-Type: application/json

{
  "email": "user@example.com",
  "query": "from:boss is:unread",
  "maxResults": 10
}
```

#### Send Email
```http
POST /api/gmail/send
Content-Type: application/json

{
  "email": "user@example.com",
  "to": "recipient@example.com",
  "subject": "Hello",
  "body": "Email body here"
}
```

#### Manage Drafts
```http
POST /api/gmail/draft
Content-Type: application/json

{
  "email": "user@example.com",
  "action": "create",
  "to": "recipient@example.com",
  "subject": "Draft",
  "body": "Draft body"
}
```

### Calendar Operations

#### List Events
```http
POST /api/calendar/list
Content-Type: application/json

{
  "email": "user@example.com",
  "timeMin": "2025-01-01T00:00:00Z",
  "maxResults": 10
}
```

#### Create Event
```http
POST /api/calendar/event
Content-Type: application/json

{
  "email": "user@example.com",
  "summary": "Meeting",
  "start": {
    "dateTime": "2025-01-15T10:00:00Z",
    "timeZone": "UTC"
  },
  "end": {
    "dateTime": "2025-01-15T11:00:00Z",
    "timeZone": "UTC"
  }
}
```

### Drive Operations

#### List Files
```http
POST /api/drive/list
Content-Type: application/json

{
  "email": "user@example.com",
  "pageSize": 10
}
```

#### Upload File
```http
POST /api/drive/upload
Content-Type: application/json

{
  "email": "user@example.com",
  "filePath": "/path/to/file.pdf",
  "name": "Document.pdf"
}
```

#### Download File
```http
POST /api/drive/download/{file_id}
Content-Type: application/json

{
  "email": "user@example.com",
  "mimeType": "application/pdf"
}
```

### Contacts Operations

#### Get Contacts
```http
POST /api/contacts/list
Content-Type: application/json

{
  "email": "user@example.com",
  "pageSize": 10
}
```

## Authentication Flow

1. Call `/api/accounts/authenticate` to get an OAuth URL
2. Visit the URL in your browser
3. Sign in to Google and grant permissions
4. You will be redirected to a success page
5. The account is now authenticated and ready to use

## File Management

Files are organized in a structured workspace:

```
workspace/
├── [email@domain.com]/
│   └── downloads/        # Files downloaded from Drive
└── [email2@domain.com]/
    └── downloads/
```

## Security

- OAuth credentials are stored securely in environment variables
- Access tokens are encrypted and stored locally in `config/tokens/`
- Automatic token refresh prevents credential exposure
- Each user maintains their own Google Cloud Project
- No credentials are transmitted to external servers

## Development

### Project Structure

```
.
├── app.py                    # Main Flask application
├── auth/
│   └── auth_manager.py       # OAuth authentication management
├── routes/
│   ├── __init__.py
│   ├── account_routes.py     # Account management routes
│   ├── gmail_routes.py       # Gmail API integration
│   ├── calendar_routes.py    # Calendar API integration
│   ├── drive_routes.py       # Drive API integration
│   ├── contacts_routes.py   # Contacts API integration
│   └── docs_routes.py       # Google Docs integration
├── config/
│   └── tokens/              # Stored OAuth tokens (created automatically)
├── workspace/               # File workspace (created automatically)
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
└── README.md                 # This file
```

## Troubleshooting

### Common Issues

**Authentication Errors**:
- Verify OAuth credentials are correctly configured in `.env`
- Ensure APIs (Gmail, Calendar, Drive, People, Docs) are enabled in Google Cloud
- Check that you're added as a test user in OAuth consent screen
- Confirm redirect URI is set to `http://localhost:8080/oauth/callback`

**Connection Issues**:
- Verify port 8080 is available and not blocked by firewall
- Ensure config directory exists and has proper permissions
- Check that all dependencies are installed correctly

**Token Issues**:
- Remove and re-authenticate accounts if tokens become invalid
- Verify API scopes are properly configured in Google Cloud
- Check token expiration and refresh logic

### Getting Help

- Check the console output for detailed error messages
- Verify your Google Cloud project configuration
- Ensure all required APIs are enabled
- Check OAuth consent screen settings

## License

MIT License

## Contributing

Contributions are welcome! Please feel free to submit issues and pull requests.

## Support

For additional support:
- Check the troubleshooting section above
- Review Google Cloud Console configuration
- Verify all environment variables are set correctly
- Ensure all required APIs are enabled

