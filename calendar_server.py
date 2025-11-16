from typing import Any, List
import datetime
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from mcp.server.fastmcp import FastMCP
import os

# Initialize FastMCP server
mcp = FastMCP("google-calendar")

# Google Calendar API scopes
SCOPES = [
    'https://www.googleapis.com/auth/calendar.readonly',
    'https://www.googleapis.com/auth/calendar.events'
]

def authenticate_calendar():
    """Authenticate and return Google Calendar service."""
    creds = None
    # Token file stores the user's access and refresh tokens
    if os.path.exists('calendar_token.json'):
        creds = Credentials.from_authorized_user_file('calendar_token.json', SCOPES)
    
    # If there are no (valid) credentials available, let the user log in
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('calendar_token.json', 'w') as token:
            token.write(creds.to_json())
    
    service = build('calendar', 'v3', credentials=creds)
    return service

@mcp.tool()
async def list_calendars() -> str:
    """List all calendars accessible to the authenticated user."""
    try:
        service = authenticate_calendar()
        calendar_list = service.calendarList().list().execute()
        
        calendars = calendar_list.get('items', [])
        if not calendars:
            return "No calendars found."
        
        calendar_info = []
        for calendar in calendars:
            info = f"""
Calendar: {calendar['summary']}
ID: {calendar['id']}
Description: {calendar.get('description', 'No description')}
Time Zone: {calendar['timeZone']}
Access Role: {calendar['accessRole']}
Primary: {calendar.get('primary', False)}
"""
            calendar_info.append(info)
        
        return "\n---\n".join(calendar_info)
    
    except Exception as e:
        return f"Error listing calendars: {str(e)}"

@mcp.tool()
async def get_events(calendar_id: str = "primary", max_results: int = 10, days_ahead: int = 7) -> str:
    """Get upcoming events from a calendar.
    
    Args:
        calendar_id: Calendar ID (default: 'primary')
        max_results: Maximum number of events to return (default: 10)
        days_ahead: Number of days ahead to look for events (default: 7)
    """
    try:
        service = authenticate_calendar()
        
        # Get current time and time for days_ahead
        now = datetime.datetime.utcnow().isoformat() + 'Z'
        future_date = (datetime.datetime.utcnow() + datetime.timedelta(days=days_ahead)).isoformat() + 'Z'
        
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=now,
            timeMax=future_date,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            return f"No upcoming events found in the next {days_ahead} days."
        
        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Format datetime
            if 'T' in start:  # It's a datetime
                start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
                start_formatted = start_dt.strftime("%Y-%m-%d %H:%M")
                end_formatted = end_dt.strftime("%Y-%m-%d %H:%M")
            else:  # It's a date (all-day event)
                start_formatted = start
                end_formatted = end
            
            attendees = event.get('attendees', [])
            attendee_emails = [att.get('email', '') for att in attendees]
            
            event_info = f"""
Title: {event.get('summary', 'No Title')}
ID: {event['id']}
Start: {start_formatted}
End: {end_formatted}
Description: {event.get('description', 'No description')}
Location: {event.get('location', 'No location')}
Creator: {event.get('creator', {}).get('email', 'Unknown')}
Attendees: {', '.join(attendee_emails) if attendee_emails else 'None'}
Status: {event.get('status', 'Unknown')}
"""
            event_list.append(event_info)
        
        return f"Upcoming events in the next {days_ahead} days:\n" + "\n---\n".join(event_list)
    
    except Exception as e:
        return f"Error getting events: {str(e)}"

@mcp.tool()
async def create_event(
    summary: str,
    start_datetime: str,
    end_datetime: str,
    calendar_id: str = "primary",
    description: str = "",
    location: str = "",
    attendees: str = ""
) -> str:
    """Create a new calendar event.
    
    Args:
        summary: Event title
        start_datetime: Start date/time (ISO format: 2023-12-25T10:00:00)
        end_datetime: End date/time (ISO format: 2023-12-25T11:00:00)
        calendar_id: Calendar ID (default: 'primary')
        description: Event description (optional)
        location: Event location (optional)
        attendees: Comma-separated list of attendee emails (optional)
    """
    try:
        service = authenticate_calendar()
        
        # Parse datetime strings
        try:
            start_dt = datetime.datetime.fromisoformat(start_datetime)
            end_dt = datetime.datetime.fromisoformat(end_datetime)
        except ValueError:
            return "Error: Invalid datetime format. Use ISO format (YYYY-MM-DDTHH:MM:SS)"
        
        event = {
            'summary': summary,
            'start': {
                'dateTime': start_dt.isoformat(),
                'timeZone': 'UTC',
            },
            'end': {
                'dateTime': end_dt.isoformat(),
                'timeZone': 'UTC',
            },
        }
        
        if description:
            event['description'] = description
        
        if location:
            event['location'] = location
        
        if attendees:
            attendee_list = []
            for email in attendees.split(','):
                attendee_list.append({'email': email.strip()})
            event['attendees'] = attendee_list
        
        created_event = service.events().insert(calendarId=calendar_id, body=event).execute()
        
        return f"""
Event created successfully!
Title: {created_event['summary']}
ID: {created_event['id']}
Start: {created_event['start']['dateTime']}
End: {created_event['end']['dateTime']}
Link: {created_event['htmlLink']}
"""
    
    except Exception as e:
        return f"Error creating event: {str(e)}"

@mcp.tool()
async def search_events(query: str, calendar_id: str = "primary", max_results: int = 20) -> str:
    """Search for events in a calendar.
    
    Args:
        query: Search query
        calendar_id: Calendar ID (default: 'primary')
        max_results: Maximum number of results (default: 20)
    """
    try:
        service = authenticate_calendar()
        
        events_result = service.events().list(
            calendarId=calendar_id,
            q=query,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        if not events:
            return f"No events found matching query: {query}"
        
        event_list = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            # Format datetime
            if 'T' in start:  # It's a datetime
                start_dt = datetime.datetime.fromisoformat(start.replace('Z', '+00:00'))
                end_dt = datetime.datetime.fromisoformat(end.replace('Z', '+00:00'))
                start_formatted = start_dt.strftime("%Y-%m-%d %H:%M")
                end_formatted = end_dt.strftime("%Y-%m-%d %H:%M")
            else:  # It's a date (all-day event)
                start_formatted = start
                end_formatted = end
            
            event_info = f"""
Title: {event.get('summary', 'No Title')}
ID: {event['id']}
Start: {start_formatted}
End: {end_formatted}
Description: {event.get('description', 'No description')}
Location: {event.get('location', 'No location')}
Status: {event.get('status', 'Unknown')}
"""
            event_list.append(event_info)
        
        return f"Found {len(events)} events matching '{query}':\n" + "\n---\n".join(event_list)
    
    except Exception as e:
        return f"Error searching events: {str(e)}"

@mcp.tool()
async def delete_event(event_id: str, calendar_id: str = "primary") -> str:
    """Delete a calendar event.
    
    Args:
        event_id: ID of the event to delete
        calendar_id: Calendar ID (default: 'primary')
    """
    try:
        service = authenticate_calendar()
        
        service.events().delete(calendarId=calendar_id, eventId=event_id).execute()
        
        return f"Event {event_id} deleted successfully."
    
    except Exception as e:
        return f"Error deleting event: {str(e)}"

@mcp.tool()
async def get_free_busy(
    start_time: str,
    end_time: str,
    calendar_ids: str = "primary"
) -> str:
    """Check free/busy status for calendars.
    
    Args:
        start_time: Start time (ISO format: 2023-12-25T10:00:00Z)
        end_time: End time (ISO format: 2023-12-25T18:00:00Z)
        calendar_ids: Comma-separated calendar IDs (default: 'primary')
    """
    try:
        service = authenticate_calendar()
        
        # Parse calendar IDs
        calendar_list = [cal.strip() for cal in calendar_ids.split(',')]
        
        body = {
            "timeMin": start_time,
            "timeMax": end_time,
            "items": [{"id": cal_id} for cal_id in calendar_list]
        }
        
        freebusy_result = service.freebusy().query(body=body).execute()
        
        calendars_info = []
        for cal_id in calendar_list:
            cal_data = freebusy_result['calendars'].get(cal_id, {})
            busy_times = cal_data.get('busy', [])
            
            if not busy_times:
                busy_str = "No busy times"
            else:
                busy_list = []
                for busy in busy_times:
                    start = datetime.datetime.fromisoformat(busy['start'].replace('Z', '+00:00'))
                    end = datetime.datetime.fromisoformat(busy['end'].replace('Z', '+00:00'))
                    busy_list.append(f"  {start.strftime('%Y-%m-%d %H:%M')} - {end.strftime('%Y-%m-%d %H:%M')}")
                busy_str = "\n".join(busy_list)
            
            cal_info = f"""
Calendar: {cal_id}
Busy times:
{busy_str}
Errors: {', '.join([err['reason'] for err in cal_data.get('errors', [])]) if cal_data.get('errors') else 'None'}
"""
            calendars_info.append(cal_info)
        
        return f"Free/busy status from {start_time} to {end_time}:\n" + "\n---\n".join(calendars_info)
    
    except Exception as e:
        return f"Error getting free/busy status: {str(e)}"

def main():
    """Initialize and run the Google Calendar MCP server."""
    mcp.run(transport='stdio')

if __name__ == "__main__":
    main()