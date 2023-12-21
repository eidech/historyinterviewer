from openai import OpenAI
from pyht import Client
from dotenv import load_dotenv
from pyht.client import TTSOptions
import os
load_dotenv()

openaiclient = OpenAI()
playhtclient = Client(
    user_id = os.getenv('PLAY_HT_USER_ID'),
    api_key = os.getenv('PLAY_HT_API_KEY'),
)

exitloop = False

while not exitloop:
    # get the question to ask
    question = input("Ask FDR a question: ")

    # retrieve the response from ChatGPT
    response = openaiclient.chat.completions.create(
        model="gpt-3.5-turbo-1106",
        messages=[
            {"role": "system", "content": "You are the president Franklin Delano Roosevelt in a high school history class. You are answering student questions about your life. Try to answer in three sentences or less"},
            {"role": "user", "content": question}
        ]
    )
    answer = response.choices[0].message.content
    
    
    print(answer)

    # get audio from Play.ht
    options = TTSOptions(voice="s3://voice-cloning-zero-shot/807979aa-6c63-42eb-8643-b94239115b64/fdr/manifest.json")
    audio = b''
    for chunk in playhtclient.tts(answer, options):
        audio += chunk

    with open('output.wav', mode='bx') as f:
        f.write(audio)

    # get video from D-iD

    # play response video

    if input("Do you want to ask another question? ").lower() == "no":
        exitloop = True