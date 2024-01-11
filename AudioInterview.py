from dotenv import load_dotenv
from googleapiclient.discovery import build
from ChatGPTCaller import call_chatgpt
from PlayHTCaller import call_playht
import GoogleAuth
import os, uuid

load_dotenv()

GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

def main():
    
    # dictionaries to hold voices, folders; list to hold questions
    voices = {} # KEY voice name VAL Voice objects
    folder_ids = {} # KEY group name VAL folder ID
    questions = []

    # load up available voices and PlayHT voice URLs from Google Sheet
    # authenticate w Google
    creds = GoogleAuth.getCreds()
    sheet_service = build('sheets', 'v4', credentials=creds)
    drive_service = build('drive', 'v3', credentials=creds)

    # load up Google Sheets
    sheet = sheet_service.spreadsheets()

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

    # load up questions from Google Sheet
    # load questions data from sheet
    result = sheet.values().get(spreadsheetId=GOOGLE_SHEET_ID, range='Form Responses 1!A2:E').execute()
    values = result.get('values', [])

    # verify that data was retrieved
    if not values:
        print('No data found!')
        return

    # load data into voices dictionary    
    for value in values:
        questions.append(Question(value[2], value[3], value[4]))

    # iterate through questions
    for question in questions:

        # get the question response from ChatGPT
        response = call_chatgpt(question.question, voices[question.voice].prompt)
        print(response)

        # call PlayHT to generate the audio file
        # generate unique filename
        audio_filename = question.group + str(uuid.uuid4()) + '.wav'

        with open(audio_filename, mode='bx') as f:
            audio = call_playht(response, voice=voices[question.voice].voice_url)
            f.write(audio)

        # upload the audio file to Google Drive
        file_metadata = {
            'name': audio_filename,
            'parents': folder_ids[question.group]
        }
        media = drive_service.files().create(
            body=file_metadata,
            media_body=audio_filename,
            fields='id'
        ).execute()
        

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