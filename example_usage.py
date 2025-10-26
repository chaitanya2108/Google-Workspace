"""
Example usage of the Google Workspace Flask API
This file demonstrates how to use the API endpoints
"""

import requests

# Base URL of your API
BASE_URL = "http://localhost:8080"

# Example 1: List accounts
def list_accounts():
    """List all authenticated accounts"""
    response = requests.get(f"{BASE_URL}/api/accounts")
    print("Accounts:", response.json())

# Example 2: Authenticate an account
def authenticate_account():
    """Get OAuth URL for authentication"""
    response = requests.post(
        f"{BASE_URL}/api/accounts/authenticate",
        json={"email": "user@example.com"}
    )
    result = response.json()
    print("Visit this URL to authenticate:", result['authUrl'])

# Example 3: Search Gmail
def search_emails(email, query):
    """Search emails in Gmail"""
    response = requests.post(
        f"{BASE_URL}/api/gmail/search",
        json={
            "email": email,
            "query": query,
            "maxResults": 10
        }
    )
    print("Search Results:", response.json())

# Example 4: Send an email
def send_email(email, to, subject, body):
    """Send an email through Gmail"""
    response = requests.post(
        f"{BASE_URL}/api/gmail/send",
        json={
            "email": email,
            "to": to,
            "subject": subject,
            "body": body
        }
    )
    print("Send Result:", response.json())

# Example 5: List calendar events
def list_calendar_events(email, time_min, max_results=10):
    """List calendar events"""
    response = requests.post(
        f"{BASE_URL}/api/calendar/list",
        json={
            "email": email,
            "timeMin": time_min,
            "maxResults": max_results
        }
    )
    print("Calendar Events:", response.json())

# Example 6: Create a calendar event
def create_calendar_event(email, summary, start, end):
    """Create a calendar event"""
    response = requests.post(
        f"{BASE_URL}/api/calendar/event",
        json={
            "email": email,
            "summary": summary,
            "start": {
                "dateTime": start,
                "timeZone": "UTC"
            },
            "end": {
                "dateTime": end,
                "timeZone": "UTC"
            }
        }
    )
    print("Created Event:", response.json())

# Example 7: List Drive files
def list_drive_files(email, page_size=10):
    """List files in Google Drive"""
    response = requests.post(
        f"{BASE_URL}/api/drive/list",
        json={
            "email": email,
            "pageSize": page_size
        }
    )
    print("Drive Files:", response.json())

# Example 8: Get contacts
def get_contacts(email, page_size=10):
    """Get contacts"""
    response = requests.post(
        f"{BASE_URL}/api/contacts/list",
        json={
            "email": email,
            "pageSize": page_size
        }
    )
    print("Contacts:", response.json())

# Example 9: Health check
def health_check():
    """Check if the API is running"""
    response = requests.get(f"{BASE_URL}/health")
    print("Health Status:", response.json())

if __name__ == "__main__":
    print("Google Workspace Flask API - Example Usage")
    print("=" * 40)
    
    # Check if API is running
    try:
        health_check()
        
        # List accounts
        list_accounts()
        
        # Note: Before using other endpoints, authenticate your account first
        # Uncomment and use these examples after authentication:
        
        # authenticate_account()  # Get OAuth URL
        # search_emails("user@example.com", "is:unread")
        # send_email("user@example.com", "recipient@example.com", "Test", "Hello!")
        
    except requests.exceptions.ConnectionError:
        print("Error: Could not connect to the API. Make sure the server is running.")
        print("Run: python app.py")

