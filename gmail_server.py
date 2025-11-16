from typing import Any, List
import base64
import email
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP
import os

# Initialize FastMCP server
mcp = FastMCP("gmail")

# Gmail API scopes
SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.send',
    'https://www.googleapis.com/auth/gmail.compose',
    'https://www.googleapis.com/auth/gmail.modify'
]

def authenticate_gmail():
    """Authenticate and return Gmail service."""
    creds = None
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('gmail', 'v1', credentials=creds)
    return service

@mcp.tool()
async def list_messages(query: str = "", max_results: int = 10) -> str:
    """List Gmail messages with optional query.
    
    Args:
        query: Gmail search query (e.g., 'from:someone@example.com', 'subject:important')
        max_results: Maximum number of messages to return (default: 10)
    """
    try:
        service = authenticate_gmail()
        result = service.users().messages().list(
            userId='me', 
            q=query, 
            maxResults=max_results
        ).execute()
        
        messages = result.get('messages', [])
        if not messages:
            return "No messages found."
        
        message_list = []
        for msg in messages:
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = message['payload'].get('headers', [])
            
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            message_list.append(f"""
Subject: {subject}
From: {sender}
Date: {date}
ID: {msg['id']}
""")
        
        return "\n---\n".join(message_list)
    
    except Exception as e:
        return f"Error listing messages: {str(e)}"

@mcp.tool()
async def read_message(message_id: str) -> str:
    """Read a specific Gmail message by ID.
    
    Args:
        message_id: The ID of the message to read
    """
    try:
        service = authenticate_gmail()
        message = service.users().messages().get(userId='me', id=message_id).execute()
        
        # Extract headers
        headers = message['payload'].get('headers', [])
        subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
        sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
        date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
        
        # Extract body
        body = ""
        if 'parts' in message['payload']:
            for part in message['payload']['parts']:
                if part['mimeType'] == 'text/plain':
                    data = part['body']['data']
                    body = base64.urlsafe_b64decode(data).decode('utf-8')
                    break
        else:
            if message['payload']['body'].get('data'):
                body = base64.urlsafe_b64decode(
                    message['payload']['body']['data']
                ).decode('utf-8')
        
        return f"""
Subject: {subject}
From: {sender}
Date: {date}

{body}
"""
    
    except Exception as e:
        return f"Error reading message: {str(e)}"

@mcp.tool()
async def send_email(to: str, subject: str, body: str, cc: str = "", bcc: str = "") -> str:
    """Send an email via Gmail.
    
    Args:
        to: Recipient email address
        subject: Email subject
        body: Email body content
        cc: CC recipients (comma-separated, optional)
        bcc: BCC recipients (comma-separated, optional)
    """
    try:
        service = authenticate_gmail()
        
        message = MIMEMultipart()
        message['to'] = to
        message['subject'] = subject
        if cc:
            message['cc'] = cc
        if bcc:
            message['bcc'] = bcc
        
        message.attach(MIMEText(body, 'plain'))
        
        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode()
        
        send_message = service.users().messages().send(
            userId='me', 
            body={'raw': raw_message}
        ).execute()
        
        return f"Email sent successfully. Message ID: {send_message['id']}"
    
    except Exception as e:
        return f"Error sending email: {str(e)}"

@mcp.tool()
async def search_emails(query: str, max_results: int = 20) -> str:
    """Search emails with advanced Gmail search syntax.
    
    Args:
        query: Search query (e.g., 'from:john@example.com has:attachment')
        max_results: Maximum number of results (default: 20)
    """
    try:
        service = authenticate_gmail()
        result = service.users().messages().list(
            userId='me',
            q=query,
            maxResults=max_results
        ).execute()
        
        messages = result.get('messages', [])
        if not messages:
            return f"No messages found for query: {query}"
        
        search_results = []
        for msg in messages[:10]:  # Limit detailed results
            message = service.users().messages().get(userId='me', id=msg['id']).execute()
            headers = message['payload'].get('headers', [])
            
            subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
            sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown Sender')
            date = next((h['value'] for h in headers if h['name'] == 'Date'), 'Unknown Date')
            
            search_results.append(f"""
Subject: {subject}
From: {sender}
Date: {date}
ID: {msg['id']}
""")
        
        return f"Found {len(messages)} messages. Showing first 10:\n" + "\n---\n".join(search_results)
    
    except Exception as e:
        return f"Error searching emails: {str(e)}"

def main():
    """Initialize and run the Gmail MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()