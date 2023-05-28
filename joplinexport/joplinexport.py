import os
import requests
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
token = os.getenv("JOPLIN_TOKEN")
port = 41184

def get_notebooks():
    response = requests.get(f'http://localhost:{port}/folders?token={token}')
    response.raise_for_status()
    data = response.json()
    return data['items'] if 'items' in data else []

def get_note_details(note_id):
    response = requests.get(f'http://localhost:{port}/notes/{note_id}?fields=body,title&token={token}')
    response.raise_for_status()
    data = response.json()
    return data['title'], data['body']



def get_notes_from_notebook(notebook_id):
    response = requests.get(f'http://localhost:{port}/folders/{notebook_id}/notes?token={token}')
    response.raise_for_status()
    data = response.json()
    return data['items'] if 'items' in data else []

def get_note_content(note_id):
    return json.loads(requests.get(f'http://localhost:{port}/notes/{note_id}?fields=body,title&token={token}').text)

def get_note_resources(note_id):
    return json.loads(requests.get(f'http://localhost:{port}/notes/{note_id}/resources?token={token}').text)

def download_resource(resource_id):
    response = requests.get(f'http://localhost:{port}/resources/{resource_id}/file?token={token}', stream=True)
    if response.status_code == 200:
        return response.raw
    else:
        print(f"Error downloading resource {resource_id}")
        return None
