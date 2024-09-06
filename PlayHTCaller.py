from pyht import Client
from pyht.client import TTSOptions
from dotenv import load_dotenv
import os

load_dotenv()

PLAY_HT_USER_ID = os.getenv('PLAY_HT_USER_ID')
PLAY_HT_API_KEY = os.getenv('PLAY_HT_API_KEY')

def call_playht(answer, voice):
    playhtclient = Client(
        user_id=PLAY_HT_USER_ID,
        api_key=PLAY_HT_API_KEY,
    )
    options = TTSOptions(voice)
    audio = b''
    for chunk in playhtclient.tts(answer, options):
        audio += chunk
    return audio

def call_playht(answer, voice, speed):
    playhtclient = Client(
        user_id=PLAY_HT_USER_ID,
        api_key=PLAY_HT_API_KEY
    )
    options = TTSOptions(voice, speed=speed)
    audio = b''
    for chunk in playhtclient.tts(answer, options):
        audio += chunk
    return audio