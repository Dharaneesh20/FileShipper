import requests

API_URL = 'http://<server-ip>:8000/api/'
TOKEN = '<your-auth-token>'

def upload_file(filepath):
    with open(filepath, 'rb') as f:
        files = {'file': (filepath, f)}
        headers = {'Authorization': f'Token {TOKEN}'}
        response = requests.post(API_URL + 'upload/', files=files, headers=headers)
        print(response.json())

def list_files():
    headers = {'Authorization': f'Token {TOKEN}'}
    response = requests.get(API_URL + 'list/', headers=headers)
    print(response.json())

def download_file(file_id, save_as):
    headers = {'Authorization': f'Token {TOKEN}'}
    response = requests.get(API_URL + f'download/{file_id}/', headers=headers, stream=True)
    with open(save_as, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded to {save_as}")

# Example usage:
# upload_file('test.jpg')
# list_files()
# download_file(1, 'output.jpg')
