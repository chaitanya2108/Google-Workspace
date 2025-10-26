"""
Authentication Manager for Google OAuth 2.0
Handles token storage, refresh, and authenticated client creation
"""

import os
import json
import uuid
from pathlib import Path
from typing import Dict, Optional, Any
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import Flow
from googleapiclient.discovery import build

class AuthManager:
    """Manages Google OAuth authentication for multiple accounts"""
    
    def __init__(self):
        """Initialize the Auth Manager with OAuth configuration"""
        self.client_id = os.getenv('GOOGLE_CLIENT_ID')
        self.client_secret = os.getenv('GOOGLE_CLIENT_SECRET')
        self.redirect_uri = os.getenv('GOOGLE_REDIRECT_URI', 'http://localhost:8080/oauth/callback')
        
        if not self.client_id or not self.client_secret:
            raise ValueError('GOOGLE_CLIENT_ID and GOOGLE_CLIENT_SECRET environment variables are required')
        
        # Set up directories
        project_root = os.getenv('GOOGLE_WORKSPACE_PROJECT_ROOT', os.getcwd())
        self.config_dir = Path(project_root) / 'config'
        self.tokens_dir = self.config_dir / 'tokens'
        self.workspace_dir = Path(project_root) / 'workspace'
        
        # Create directories if they don't exist
        self.tokens_dir.mkdir(parents=True, exist_ok=True)
        self.workspace_dir.mkdir(parents=True, exist_ok=True)
        
        # OAuth scopes
        self.scopes = [
            'openid',  # Required for userinfo endpoints
            'https://www.googleapis.com/auth/gmail.readonly',
            'https://www.googleapis.com/auth/gmail.send',
            'https://www.googleapis.com/auth/gmail.modify',
            'https://www.googleapis.com/auth/gmail.labels',
            'https://www.googleapis.com/auth/gmail.settings.basic',
            'https://www.googleapis.com/auth/calendar',
            'https://www.googleapis.com/auth/calendar.events',
            'https://www.googleapis.com/auth/drive',
            'https://www.googleapis.com/auth/drive.file',
            'https://www.googleapis.com/auth/documents',
            'https://www.googleapis.com/auth/documents.readonly',
            'https://www.googleapis.com/auth/spreadsheets',
            'https://www.googleapis.com/auth/contacts.readonly',
            'https://www.googleapis.com/auth/userinfo.email',
            'https://www.googleapis.com/auth/userinfo.profile',
        ]
    
    def get_auth_url(self, email: Optional[str] = None) -> Dict[str, Any]:
        """Generate OAuth authorization URL"""
        try:
            state = str(uuid.uuid4())
            
            # Create OAuth flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            auth_url, _ = flow.authorization_url(
                access_type='offline',
                include_granted_scopes='true',
                state=state,
                prompt='consent'
            )
            
            return {
                'success': True,
                'authUrl': auth_url,
                'state': state
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def handle_oauth_callback(self, code: str, state: str) -> Dict[str, Any]:
        """Handle OAuth callback and save tokens"""
        try:
            # Create OAuth flow
            flow = Flow.from_client_config(
                {
                    "web": {
                        "client_id": self.client_id,
                        "client_secret": self.client_secret,
                        "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                        "token_uri": "https://oauth2.googleapis.com/token",
                        "redirect_uris": [self.redirect_uri]
                    }
                },
                scopes=self.scopes,
                redirect_uri=self.redirect_uri
            )
            
            # Exchange code for tokens
            flow.fetch_token(code=code)
            
            # Get user info to determine email
            creds = flow.credentials
            service = build('oauth2', 'v2', credentials=creds)
            user_info = service.userinfo().get().execute()
            email = user_info.get('email')
            
            if not email:
                raise ValueError('Could not retrieve user email')
            
            # Save tokens
            self._save_tokens(email, creds)
            
            return {
                'success': True,
                'email': email
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def get_authenticated_client(self, email: str, service_name: str = 'gmail', version: str = 'v1'):
        """Get an authenticated Google API client"""
        try:
            creds = self._load_tokens(email)
            if not creds:
                return None
            
            # Refresh token if expired
            if creds.expired and creds.refresh_token:
                creds.refresh(Request())
                self._save_tokens(email, creds)
            
            return build(service_name, version, credentials=creds)
        except Exception as e:
            print(f'Failed to get authenticated client: {e}')
            return None
    
    def list_accounts(self) -> list:
        """List all authenticated accounts"""
        try:
            accounts = []
            for token_file in self.tokens_dir.glob('*.json'):
                email = token_file.stem
                accounts.append({
                    'email': email,
                    'authenticated': True
                })
            return accounts
        except Exception as e:
            print(f'Failed to list accounts: {e}')
            return []
    
    def remove_account(self, email: str) -> bool:
        """Remove an account and its tokens"""
        try:
            token_file = self.tokens_dir / f'{email}.json'
            if token_file.exists():
                token_file.unlink()
            return True
        except Exception as e:
            print(f'Failed to remove account: {e}')
            return False
    
    def is_authenticated(self, email: str) -> bool:
        """Check if an account is authenticated"""
        return (self.tokens_dir / f'{email}.json').exists()
    
    def _save_tokens(self, email: str, creds: Credentials):
        """Save tokens to file"""
        token_file = self.tokens_dir / f'{email}.json'
        token_data = {
            'token': creds.token,
            'refresh_token': creds.refresh_token,
            'token_uri': creds.token_uri,
            'client_id': creds.client_id,
            'client_secret': creds.client_secret,
            'scopes': creds.scopes,
            'expiry': creds.expiry.isoformat() if creds.expiry else None
        }
        
        with open(token_file, 'w') as f:
            json.dump(token_data, f)
    
    def _load_tokens(self, email: str) -> Optional[Credentials]:
        """Load tokens from file"""
        token_file = self.tokens_dir / f'{email}.json'
        
        if not token_file.exists():
            return None
        
        try:
            with open(token_file, 'r') as f:
                token_data = json.load(f)
            
            creds = Credentials(
                token=token_data.get('token'),
                refresh_token=token_data.get('refresh_token'),
                token_uri=token_data.get('token_uri'),
                client_id=token_data.get('client_id'),
                client_secret=token_data.get('client_secret'),
                scopes=token_data.get('scopes'),
            )
            
            # Parse expiry date
            if token_data.get('expiry'):
                from datetime import datetime
                creds.expiry = datetime.fromisoformat(token_data['expiry'])
            
            return creds
        except Exception as e:
            print(f'Failed to load tokens: {e}')
            return None

