import os
import requests
import json

from . import token, port

def get_notebooks():
    page = 1
    notebooks = []
    while True:
        response = requests.get(f'http://localhost:{port}/folders?token={token}&page={page}')
        response.raise_for_status()
        data = response.json()
        if 'items' in data:
            notebooks.extend(data['items'])
        if 'has_more' in data and data['has_more']:
            page += 1
        else:
            break
    return notebooks

def get_note_details(note_id):
    # Get the note title and body
    response = requests.get(f'http://localhost:{port}/notes/{note_id}?fields=body,title&token={token}')
    response.raise_for_status()
    data = response.json()
    title, body = data['title'], data['body']

    # Get the tags for the note
    response = requests.get(f'http://localhost:{port}/notes/{note_id}/tags?token={token}')
    response.raise_for_status()
    tags_data = response.json()

    # Check if tags exist for the note
    if tags_data and 'items' in tags_data and isinstance(tags_data['items'], list):
        tags = [tag['title'] for tag in tags_data['items']]
    else:
        tags = []

    return title, body, tags


def get_sub_notebooks(parent_id):
    all_folders = get_notebooks()
    sub_notebooks = [folder for folder in all_folders if folder['parent_id'] == parent_id]
    return sub_notebooks


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
