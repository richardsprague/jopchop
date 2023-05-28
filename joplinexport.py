import requests
import json
import os

# replace with your Joplin Web Clipper port
port = 41184
notebook_name = "Notes 202302 Oaxaca"
save_path = "/Users/sprague/dev/notes/notes2023/oaxaca/d2"
token = "0cb3d6e6963e4ae85edca5bf816369f5291eb7bd05feb441c96e7461872f8ea5d4dc222a63109c5ada59767f444b6ce7e836cae3a4153a39828d2fc872dec747"

headers = {
    'Authorization': f'Token {token}',
}

def get_notebook_id(notebook_name):
    notebooks = json.loads(requests.get(f'http://localhost:{port}/folders?token={token}').text)
    for notebook in notebooks['items']:
        if notebook['title'] == notebook_name:
            return notebook['id']
    raise ValueError(f"No notebook found with the name {notebook_name}")

def get_notes_from_notebook(notebook_id):
    return json.loads(requests.get(f'http://localhost:{port}/folders/{notebook_id}/notes?token={token}').text)['items']

def get_note_content(note_id):
    return json.loads(requests.get(f'http://localhost:{port}/notes/{note_id}?fields=body,title&token={token}').text)


def save_note_to_file(note):
    note_content = get_note_content(note['id'])
    filename = os.path.join(save_path, f"{note_content['title'].replace('/', '-')}.md")
    with open(filename, 'w', encoding='utf-8') as f:
        if 'body' in note_content:
            f.write(note_content['body'])
        else:
            print(f"Note {note['id']} does not have a body")

def main():
    notebook_id = get_notebook_id(notebook_name)
    notes = get_notes_from_notebook(notebook_id)
    for note in notes:
        save_note_to_file(note)
    print(f'Exported {len(notes)} notes from {notebook_name} to {save_path}')

if __name__ == "__main__":
    main()
