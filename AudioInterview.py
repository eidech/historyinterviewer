from dotenv import load_dotenv
import os

load_dotenv()

GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

def main():
    
    # load up available voices and PlayHT voice URLs from Google Sheet

    # call PlayHT for each of the questions, generating an audio file, then saving the audio file to Google Drive
    # store Google Drive Folder IDs as we go

    # generate email for teacher, with links to Google Drive folders; send email

    return

if __name__== "__main__":
    main()