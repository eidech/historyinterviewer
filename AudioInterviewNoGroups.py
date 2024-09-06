from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from ChatGPTCaller import call_chatgpt
from PlayHTCaller import call_playht
import GoogleAuth
import os, uuid, re

load_dotenv()

GOOGLE_SHEET_ID = os.getenv('NO_GROUP_GOOGLE_SHEET_ID')
FOLDER_ID = os.getenv('NO_GROUP_FOLDER_ID')

###############################################
### Main Function - All Functionality #########
###############################################

def main():
    # load up available voices and PlayHT voice URLs from Google Sheet
    # authenticate w Google
    creds = GoogleAuth.getCreds()
    sheet_service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # load up Google Sheets
    sheet = sheet_service.spreadsheets()

    # get the folder and voice needed for this submission
    voice = Voice('Dr Phil', 's3://voice-cloning-zero-shot/69e1c988-7cdb-4eed-bb0c-c4c711a79163/original/manifest.json', 'You are Dr. Phil McGraw in a high school psychology class. You are answering student questions. Try to answer in three sentences or less.')

    # get the questions from the sheet
    questions = get_questions(sheet)

    for question in questions:
        print(question)
        # get the question response from ChatGPT
        response = call_chatgpt(question, voice.prompt)
        print(response)

        # Create a safe filename
        filename = re.sub(r'[^a-zA-Z0-9 ]', '_', question)
        filename = filename.replace(' ', '_')
        filename = filename[:20]

        # call PlayHT to generate the audio file
        # generate unique filename
        audio_filename = filename + str(uuid.uuid4()) + '.wav'

        print('Writing audio to file...')
        with open(audio_filename, mode='bx') as f:
            audio = call_playht(response, voice=voice.voice_url, speed=0.8)
            f.write(audio)
        print('Audio creation complete')

        upload_to_google_drive(audio_filename, FOLDER_ID, drive_service)

###############################################
### Helper Functions ##########################
###############################################

def get_questions(sheet):
    questions = []
    # load up questions from Google Sheet
    # load questions data from sheet
    result = sheet.values().get(spreadsheetId=GOOGLE_SHEET_ID, range='Form Responses 1!A2:C').execute()
    values = result.get('values', [])

    # verify that data was retrieved
    if not values:
        print('No data found!')
        return

    # load data into questions list    
    for value in values:
        questions.append(value[2])
    
    return questions

def upload_to_google_drive(filename, folderid, drive_service):
    print('Uploading to Google Drive...')
    folderid = [folderid]
    file_metadata = {
        'name': filename,
        'parents': folderid
    }
    media_body = MediaFileUpload(filename)
    drive_service.files().create(
        body=file_metadata,
        media_body=media_body,
        fields='id'
    ).execute()
    print('Upload complete')

class Voice():

    def __init__(self, name, voice_url, prompt):
        self.name = name
        self.voice_url = voice_url
        self.prompt = prompt

if __name__== "__main__":
    main()