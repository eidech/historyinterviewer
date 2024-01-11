from dotenv import load_dotenv
import os, requests

load_dotenv()

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