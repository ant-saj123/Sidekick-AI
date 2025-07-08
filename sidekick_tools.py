from playwright.async_api import async_playwright
from langchain_community.agent_toolkits import PlayWrightBrowserToolkit
from dotenv import load_dotenv
import os
import requests
from langchain.agents import Tool
from langchain_community.agent_toolkits import FileManagementToolkit
from langchain_community.tools.wikipedia.tool import WikipediaQueryRun
from langchain_experimental.tools import PythonREPLTool
from langchain_community.utilities import GoogleSerperAPIWrapper
from langchain_community.utilities.wikipedia import WikipediaAPIWrapper

# PDF creation
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
import io

#Youtube search
from youtubesearchpython import VideosSearch

#Google calender integration
from google.oauth2 import service_account
from googleapiclient.discovery import build



load_dotenv(override=True)
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_user = os.getenv("PUSHOVER_USER")
pushover_url = "https://api.pushover.net/1/messages.json"
serper = GoogleSerperAPIWrapper()

async def playwright_tools():
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=False)
    toolkit = PlayWrightBrowserToolkit.from_browser(async_browser=browser)
    return toolkit.get_tools(), browser, playwright


def push(text: str):
    """Send a push notification to the user"""
    requests.post(pushover_url, data = {"token": pushover_token, "user": pushover_user, "message": text})
    return "success"

def create_calendar_event(args: str):
    """
    Create a Google Calendar event.
    Args should be a comma-separated string: summary, start_time, end_time, description
    """
    try:
        parts = [p.strip() for p in args.split(",")]
        if len(parts) < 3:
            return "Error: Please provide at least summary, start_time, and end_time."
        summary = parts[0]
        start_time = parts[1]
        end_time = parts[2]
        description = parts[3] if len(parts) > 3 else ""
        # (rest of your code, using summary, start_time, end_time, description)
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        service = build('calendar', 'v3', credentials=credentials)
        event = {
            'summary': summary,
            'description': description,
            'start': {
                'dateTime': start_time,
                'timeZone': 'America/Chicago',
            },
            'end': {
                'dateTime': end_time,
                'timeZone': 'America/Chicago',
            },
        }
        event = service.events().insert(calendarId='antonysajesh321@gmail.com', body=event).execute()
        return f"Event created: {event.get('htmlLink')}"
    except Exception as e:
        return f"Error creating calendar event: {str(e)}"
    
def delete_calendar_event(event_id: str):
    """Delete a Google Calendar event by its ID"""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=['https://www.googleapis.com/auth/calendar']
        )
        service = build('calendar', 'v3', credentials=credentials)
        service.events().delete(calendarId='antonysajesh321@gmail.com', eventId=event_id).execute()
        return f"Event with ID {event_id} has been deleted successfully"
    except Exception as e:
        return f"Error deleting calendar event: {str(e)}"


def list_calendar_events(max_results: int = 10):
    """List upcoming calendar events"""
    try:
        # Set up credentials
        credentials = service_account.Credentials.from_service_account_file(
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS"),
            scopes=['https://www.googleapis.com/auth/calendar.readonly']
        )
        
        # Build the service
        service = build('calendar', 'v3', credentials=credentials)
        
        # Get current time
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc).isoformat()
        
        # Get events
        events_result = service.events().list(
            calendarId='antonysajesh321@gmail.com',
            timeMin=now,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        if not events:
            return "No upcoming events found."
        
        # Format the results
        result = "Upcoming events:\n\n"
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            result += f"📅 {event['summary']}\n"
            result += f"   📆 {start}\n"
            result += f"   �� Event ID: {event['id']}\n"  # Add event ID
            if 'description' in event:
                result += f"   📝 {event['description']}\n"
            result += "\n"
        
        return result
        
    except Exception as e:
        return f"Error listing calendar events: {str(e)}"

def search_youtube(query, max_results=5):
    api_key = os.getenv("YOUTUBE_API_KEY")
    youtube = build("youtube", "v3", developerKey=api_key)
    request = youtube.search().list(
        q=query,
        part="snippet",
        type="video",
        maxResults=max_results
    )
    response = request.execute()
    results = []
    for item in response["items"]:
        title = item["snippet"]["title"]
        video_id = item["id"]["videoId"]
        url = f"https://www.youtube.com/watch?v={video_id}"
        results.append({"title": title, "link": url})
    return results
    



def create_pdf(content: str, filename: str = "document.pdf"):
    """Create a PDF file with the given content and return file data for Gradio"""
    try:
        # Create a buffer to store the PDF
        buffer = io.BytesIO()
        
        # Create the PDF document
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        styles = getSampleStyleSheet()
        
        # Build the PDF content
        story = []
        
        # Split content into paragraphs
        paragraphs = content.split('\n\n')
        for para in paragraphs:
            if para.strip():
                story.append(Paragraph(para.strip(), styles['Normal']))
                story.append(Spacer(1, 12))
        
        # Build the PDF
        doc.build(story)
        
        # Get the PDF data
        pdf_data = buffer.getvalue()
        buffer.close()
        
        # Save to file in sandbox directory
        sandbox_path = os.path.join("sandbox", filename)
        with open(sandbox_path, 'wb') as f:
            f.write(pdf_data)
        
        # Return both success message and file path for Gradio
        return {
            "message": f"PDF created successfully: {filename}",
            "file_path": sandbox_path,
            "file_data": pdf_data
        }
    except Exception as e:
        return {
            "message": f"Error creating PDF: {str(e)}",
            "file_path": None,
            "file_data": None
        }


def get_file_tools():
    toolkit = FileManagementToolkit(root_dir="sandbox")
    return toolkit.get_tools()




async def other_tools():
    push_tool = Tool(name="send_push_notification", func=push, description="Use this tool when you want to send a push notification")
    pdf_tool = Tool(name="create_pdf", func=create_pdf, description="Use this tool when you want to create a PDF document with text content")
    youtube_tool = Tool(name="youtube_search", func=search_youtube, description="Use this tool when you want to find a youtube video")
    file_tools = get_file_tools()

    # Calendar tools (only if credentials are set up)
    calendar_tools = []
    if os.getenv("GOOGLE_APPLICATION_CREDENTIALS"):
        calendar_create = Tool(
            name="create_calendar_event", 
            func=create_calendar_event, 
            description="Create a Google Calendar event. Use format: summary, start_time (ISO format), end_time (ISO format), description (optional)"
        )
        calendar_list = Tool(
            name="list_calendar_events", 
            func=list_calendar_events, 
            description="List upcoming Google Calendar events with their IDs"
        )
        calendar_delete = Tool(
            name="delete_calendar_event", 
            func=delete_calendar_event, 
            description="Delete a Google Calendar event by its event ID"
        )
        calendar_tools = [calendar_create, calendar_list, calendar_delete]

    tool_search =Tool(
        name="search",
        func=serper.run,
        description="Use this tool when you want to get the results of an online web search"
    )

    wikipedia = WikipediaAPIWrapper()
    wiki_tool = WikipediaQueryRun(api_wrapper=wikipedia)

    python_repl = PythonREPLTool()
    
    return file_tools + [push_tool, pdf_tool, youtube_tool] + calendar_tools + [tool_search, python_repl, wiki_tool]

