# Sidekick AI Agent

Sidekick AI Agent is a personal AI assistant built with LangChain, Gradio, and various APIs. It provides a web-based interface for web search, file management, PDF creation, YouTube search, and Google Calendar integration.

## Features

- **Web Search**: Search the web using Google Serper API.
- **File Management**: Upload, download, and manage files in a sandboxed directory.
- **PDF Creation**: Generate PDF documents from text content.
- **YouTube Search**: Search for YouTube videos and get direct links.
- **Google Calendar Integration**: Create, list, and delete events on your Google Calendar.
- **Gmail Integration**: Send emails using your Gmail account.
- **Push Notifications**: Send push notifications to your device using Pushover.

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <your-repo-url>
cd langraph
```

### 2. Create and Activate a Virtual Environment
```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Variables
Create a `.env` file in the project root with the following variables:

```
GOOGLE_APPLICATION_CREDENTIALS=path/to/your/service_account.json
YOUTUBE_API_KEY=your_youtube_api_key
PUSHOVER_TOKEN=your_pushover_token
PUSHOVER_USER=your_pushover_user_key
SERPER_API_KEY=your_serper_api_key
```

- **Google Calendar**: Follow [Google's guide](https://developers.google.com/calendar/api/quickstart/python) to create a **Service Account** and download the credentials JSON file. Name this file `credentials1.json` and update `GOOGLE_APPLICATION_CREDENTIALS` in your `.env` to `credentials1.json`.
- **Gmail**: You need separate **OAuth2 Client ID** credentials for a **Desktop app**. Go to the [Google Cloud Console](https://console.developers.google.com/) > APIs & Services > Credentials > Create Credentials > OAuth client ID > Application type: Desktop app. Download the `client_secret.json` or `credentials.json` file and save it as `credentials.json` in your project root.
- **YouTube Data API**: Get an API key from the [Google Cloud Console](https://console.developers.google.com/).
- **Pushover**: Register at [Pushover](https://pushover.net/) to get your token and user key.
- **Serper API**: Get a key from [Serper](https://serper.dev/).

### 5. Playwright Setup
Install browser binaries for Playwright:
```bash
playwright install
```

### 6. Create the Sandbox Directory
```bash
mkdir -p sandbox
```

## Running the App

```bash
python app.py
```

The app will be available at [http://127.0.0.1:7864](http://127.0.0.1:7864).

## Usage
- Use the web interface to interact with the AI agent.
- Use the available tools for web search, file management, PDF creation, YouTube search, calendar management, and sending emails.

## Troubleshooting
- Ensure all environment variables and credential files (`credentials.json` for Gmail, `credentials1.json` for Calendar) are set up correctly.
- If you encounter "Access blocked" errors with Google APIs, ensure your Google Cloud project's OAuth consent screen has your email address(es) added as "Test users". Go to [Google Cloud Console](https://console.developers.google.com/) > APIs & Services > OAuth consent screen > Test users > + Add Users.
- If you encounter issues with Google Calendar, verify your service account and calendar permissions.
- For YouTube search errors, check your API key and quota.
- If Playwright tools fail, ensure browser binaries are installed (`playwright install`).

## Contributing
Pull requests are welcome! For major changes, please open an issue first to discuss what you would like to change.

## License
MIT
