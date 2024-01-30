from ChatGPTCaller import call_chatgpt
from PlayHTCaller import call_playht
from DiDCaller import call_did_createvideo, call_did_getvideo
from FileServerCaller import upload_file_to_server
from dotenv import load_dotenv
import os, uuid, urllib.request, json
from os import startfile

load_dotenv()

def main():
    exitloop = False

    # load up video interviews from file
    with open('interviews.json', 'r') as json_file:
        data = json.load(json_file)
    
    video_interviews = {}
    for figure_name, figure_data in data['figures'].items():
        video_interview = VideoInterview(
            figure_data['prompt'],
            figure_data['photofilename'],
            figure_data['voiceurl']
        )
        video_interviews[figure_name] = video_interview

    # prompt for the figure; at this time, don't give choices from file, will add later (time crunch)
    interviewee = input('Whom would you like to interview? (FDR, DrPhil): ')
    interview = video_interviews[interviewee]

    while not exitloop:
        question = input("Ask " + interviewee + " a question: ")
        answer = call_chatgpt(question, interview.prompt)
        print(answer)

        # generate unique filename
        audio_filename = str(uuid.uuid4()) + '.wav'

        with open(audio_filename, mode='bx') as f:
            audio = call_playht(answer, voice=interview.voiceurl)
            f.write(audio)

        upload_file_to_server(audio_filename)
        audio_url = 'https://' + os.getenv('FILE_SERVER_URL') + '/retrieve/' + audio_filename
        picture_url = os.getenv('IMAGE_URL') + interview.photofilename

        video_id = call_did_createvideo(audio_url, picture_url)

        video_download_url = call_did_getvideo(video_id)
        print(video_download_url)

        urllib.request.urlretrieve(video_download_url, 'movie.mp4')

        startfile('movie.mp4')

        if input("Do you want to ask another question? ").lower() == "no":
            exitloop = True

class VideoInterview:
    def __init__(self, prompt, photofilename, voiceurl):
        self.prompt = prompt
        self.photofilename = photofilename
        self.voiceurl = voiceurl

if __name__ == "__main__":
    main()
