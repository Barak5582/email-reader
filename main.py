# Import necessary libraries
import base64
import os.path
import pickle
import re
import time
import webbrowser 
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# Set up Gmail API credentials (you need to create these on Google Cloud Console)
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

def main():
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'email-reader/credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    # Connect to Gmail API
    service = build('gmail', 'v1', credentials=creds)
    
    # Search for emails
    query = "in:inbox -category:promotions"
    results = service.users().messages().list(userId='me', q=query, maxResults=7).execute()
    messages = results.get('messages', [])

    # Loop through the list of messages
    for message in messages:
        msg = service.users().messages().get(userId='me', id=message['id'], format='full').execute()

        # Recursive function to extract email content
        def extract_email_content(part):
            if 'parts' in part:
                for sub_part in part['parts']:
                    if 'data' in sub_part['body']:
                        data = sub_part['body']['data']
                        return base64.urlsafe_b64decode(data).decode('utf-8')
                    elif 'parts' in sub_part:
                        return extract_email_content(sub_part)
            return ''

        # Extract email content from the payload
        payload = msg['payload']
        email_content = extract_email_content(payload)

        if "we decided to move forward with other candidates" in email_content or "Unfortunately" in email_content:
            # Trigger Spotify playback or any desired action
            print("Oh no! another generic email that says that you are not fit for the possition.")
            webbrowser.open("https://open.spotify.com/track/4YbFRdxbiuzpEXNZMGgv7c")


    if not messages:
        print("No matching emails found.")
        return
        

if __name__ == '__main__':
    main()
