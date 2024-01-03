from openai import OpenAI
from pyht import Client
from dotenv import load_dotenv
from pyht.client import TTSOptions
import os, uuid, requests, urllib.request, time, base64
from os import startfile

load_dotenv()
DID_USERNAME = os.getenv('DID_USERNAME')
DID_PASSWORD = os.getenv('DID_PASSWORD')
PLAY_HT_USER_ID = os.getenv('PLAY_HT_USER_ID')
PLAY_HT_API_KEY = os.getenv('PLAY_HT_API_KEY')
DID_AUTH = "Basic " + base64.b64encode((DID_USERNAME + ":" + DID_PASSWORD).encode()).decode()

def call_chatgpt(question):
    openaiclient = OpenAI()
    response = openaiclient.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "You are the president Franklin Delano Roosevelt in a high school history class. You are answering student questions about your life. Try to answer in three sentences or less"},
            {"role": "user", "content": question}
        ]
    )
    return response.choices[0].message.content

def call_playht(answer):
    playhtclient = Client(
        user_id=PLAY_HT_USER_ID,
        api_key=PLAY_HT_API_KEY,
    )
    options = TTSOptions(voice="s3://voice-cloning-zero-shot/807979aa-6c63-42eb-8643-b94239115b64/fdr/manifest.json")
    audio = b''
    for chunk in playhtclient.tts(answer, options):
        audio += chunk
    return audio

def call_did_createvideo(audio_url, picture_url):
    url = "https://api.d-id.com/talks"

    payload = {
        "script": {
            "type": "audio",
            "subtitles": "false",
            "provider": {
                "type": "microsoft",
                "voice_id": "en-US-JennyNeural"
            },
            "ssml": "false",
            "audio_url": audio_url
        },
        "config": {
            "fluent": "false",
            "pad_audio": "0.0"
        },
        "source_url": picture_url
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": DID_AUTH
    }

    response = requests.post(url, json=payload, headers=headers)
    print(response.text)
    response_data = response.json()

    return response_data['id']


def call_did_getvideo(video_id):
    url = "https://api.d-id.com/talks/" + video_id

    headers = {
        "accept": "application/json",
        "authorization": DID_AUTH
    }

    response = requests.get(url, headers=headers)
    response_data = response.json()

    while 'result_url' not in response_data:
        time.sleep(5)
        response = requests.get(url, headers=headers)
        response_data = response.json()
    else:
        return response_data['result_url']

def upload_file_to_server(file_path):
    file_server_url = os.getenv('FILE_SERVER_URL')

    if file_server_url:
        upload_url = f'https://{file_server_url}/upload'

        files = {'file': open(file_path, 'rb')}

        try:
            response = requests.post(upload_url, files=files)
            response.raise_for_status()
            print('File uploaded successfully.')
        except requests.exceptions.RequestException as e:
            print(f'Error uploading file: {e}')
    else:
        print('File server URL not found in .env file.')
    
    response_data = response.json()
    print(response_data)

    if 'url' in response_data:
        file_url = response_data['url']
        print(f'File uploaded successfully.  Access it at: {file_url}')
        return file_url

def main():
    exitloop = False

    while not exitloop:
        question = input("Ask FDR a question: ")
        answer = call_chatgpt(question)

        # generate unique filename
        audio_filename = str(uuid.uuid4()) + '.wav'

        with open(audio_filename, mode='bx') as f:
            audio = call_playht(answer)
            f.write(audio)

        upload_file_to_server(audio_filename)
        audio_url = 'https://' + os.getenv('FILE_SERVER_URL') + '/retrieve/' + audio_filename
        picture_url = os.getenv('IMAGE_URL')

        video_id = call_did_createvideo(audio_url, picture_url)

        video_download_url = call_did_getvideo(video_id)
        print(video_download_url)

        urllib.request.urlretrieve(video_download_url, 'movie.mp4')

        startfile('movie.mp4')

        if input("Do you want to ask another question? ").lower() == "no":
            exitloop = True

if __name__ == "__main__":
    main()
