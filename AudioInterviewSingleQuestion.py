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
    group_name = 'Group 1'
    voice_name = 'Winston Churchill'
    question = 'What was your most cherished possession?'

    single_question(group_name, voice_name, question)

def single_question(group_name, voice_name, question):
    # load up available voices and PlayHT voice URLs from Google Sheet
    # authenticate w Google
    creds = GoogleAuth.getCreds()
    sheet_service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # load up Google Sheets
    sheet = sheet_service.spreadsheets()

    # dictionaries to hold voices, folders
    voices = get_voices(sheet) # KEY voice name VAL Voice objects
    folder_ids = get_folders(sheet) # KEY group name VAL folder ID

    # get the folder and voice needed for this submission
    voice = voices[voice_name]
    folder_id = folder_ids[group_name]

    print(question)
    # get the question response from ChatGPT
    response = call_chatgpt(question, voice.prompt)
    print(response)

    # call PlayHT to generate the audio file
    # generate unique filename
    audio_filename = group_name + str(uuid.uuid4()) + '.wav'

    print('Writing audio to file...')
    with open(audio_filename, mode='bx') as f:
        audio = call_playht(response, voice=voice.voice_url)
        f.write(audio)
    print('Audio creation complete')

    upload_to_google_drive(audio_filename, folder_id, drive_service)

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