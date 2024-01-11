from ChatGPTCaller import call_chatgpt
from PlayHTCaller import call_playht
from DiDCaller import call_did_createvideo, call_did_getvideo
from FileServerCaller import upload_file_to_server
from dotenv import load_dotenv
import os, uuid, urllib.request
from os import startfile

load_dotenv()

def main():
    exitloop = False

    while not exitloop:
        question = input("Ask FDR a question: ")
        answer = call_chatgpt(question, "You are the president Franklin Delano Roosevelt in a high school history class. You are answering student questions about your life. Try to answer in three sentences or less")

        # generate unique filename
        audio_filename = str(uuid.uuid4()) + '.wav'

        with open(audio_filename, mode='bx') as f:
            audio = call_playht(answer, voice="s3://voice-cloning-zero-shot/807979aa-6c63-42eb-8643-b94239115b64/fdr/manifest.json")
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
