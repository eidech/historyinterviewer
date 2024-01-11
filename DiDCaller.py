from dotenv import load_dotenv
import os, base64, requests, time

load_dotenv()
DID_USERNAME = os.getenv('DID_USERNAME')
DID_PASSWORD = os.getenv('DID_PASSWORD')
DID_AUTH = "Basic " + base64.b64encode((DID_USERNAME + ":" + DID_PASSWORD).encode()).decode()

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