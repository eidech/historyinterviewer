from pyht import Client
from pyht.client import TTSOptions
from dotenv import load_dotenv
import os

load_dotenv()

PLAY_HT_USER_ID = os.getenv('PLAY_HT_USER_ID')
PLAY_HT_API_KEY = os.getenv('PLAY_HT_API_KEY')

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