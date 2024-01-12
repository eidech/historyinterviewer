from dotenv import load_dotenv
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from ChatGPTCaller import call_chatgpt
from PlayHTCaller import call_playht
import GoogleAuth
import os, uuid

load_dotenv()

GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

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

    # dictionaries to hold voices, folders; list to hold questions
    voices = get_voices(sheet) # KEY voice name VAL Voice objects
    folder_ids = get_folders(sheet) # KEY group name VAL folder ID
    questions = get_questions(sheet)

    # iterate through questions
    for question in questions:

        print(question.question)
        # get the question response from ChatGPT
        response = call_chatgpt(question.question, voices[question.voice].prompt)
        print(response)

        # call PlayHT to generate the audio file
        # generate unique filename
        audio_filename = question.group + str(uuid.uuid4()) + '.wav'

        print('Writing audio to file...')
        with open(audio_filename, mode='bx') as f:
            audio = call_playht(response, voice=voices[question.voice].voice_url)
            f.write(audio)
        print('Audio creation complete')

        upload_to_google_drive(audio_filename, folder_ids[question.group], drive_service)
    
    print('Execution complete')
    exit()
        
###############################################
### Helper Functions ##########################
###############################################

def get_voices(sheet):
    voices = {}
    # load voices data from sheet
    result = sheet.values().get(spreadsheetId=GOOGLE_SHEET_ID, range='Voices Lookup!A:C').execute()
    values = result.get('values', [])

    # verify that data was retrieved
    if not values:
        print('No data found!')
        return

    # load data into voices dictionary    
    for value in values:
        voices[value[0]] = Voice(value[0], value[1], value[2])
    
    return voices

def get_folders(sheet):
    folder_ids = {}

    # load up folders to store generated audio from Google Sheet
    # load folders data from sheet
    result = sheet.values().get(spreadsheetId=GOOGLE_SHEET_ID, range='Folders Lookup!A:B').execute()
    values = result.get('values', [])

    # verify that data was retrieved
    if not values:
        print('No data found!')
        return

    # load data into voices dictionary    
    for value in values:
        folder_ids[value[0]] = value[1]
    
    return folder_ids

def get_questions(sheet):
    questions = []
    # load up questions from Google Sheet
    # load questions data from sheet
    result = sheet.values().get(spreadsheetId=GOOGLE_SHEET_ID, range='Form Responses 1!A2:E').execute()
    values = result.get('values', [])

    # verify that data was retrieved
    if not values:
        print('No data found!')
        return

    # load data into questions list    
    for value in values:
        questions.append(Question(value[2], value[3], value[4]))
    
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

class Question():

    def __init__(self, group, voice, question):
        self.group = group
        self.voice = voice
        self.question = question

class Voice():

    def __init__(self, name, voice_url, prompt):
        self.name = name
        self.voice_url = voice_url
        self.prompt = prompt

if __name__== "__main__":
    main()