import os
import shutil
import sys
from joplinexport import joplinexport

# Define the directory where you want to download the notes
save_path = 'downloads'


def save_note_to_file(note_title, note_body, note_id):
    filename = os.path.join(save_path, f"{note_title.replace('/', '-')}.md")
    with open(filename, 'w', encoding='utf-8') as f:
        if note_body:
            f.write(note_body)
        else:
            print(f"Note {note_id} does not have a body")

    resources = joplinexport.get_note_resources(note_id)
    for resource in resources['items']:
        resource_data = joplinexport.download_resource(resource['id'])
        if resource_data:
            resource_filename = os.path.join(save_path, resource['title'].replace('/', '-'))
            with open(resource_filename, 'wb') as f:
                f.write(resource_data.data)


def export_notebook(notebook):
    notes = joplinexport.get_notes_from_notebook(notebook['id'])
    for note in notes:
        note_title, note_body = joplinexport.get_note_details(note['id'])
        save_note_to_file(note_title, note_body, note['id'])



def main(notebook_name):

     # check if save_path directory exists, if not create it
    if not os.path.exists(save_path):
        os.mkdir(save_path)


    notebooks = joplinexport.get_notebooks()
    for notebook in notebooks:
        if notebook['title'] == notebook_name:
            export_notebook(notebook)
            break
    else:
        print(f"No notebook found with the name {notebook_name}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python jopchop.py <notebook_name>")
    else:
        main(sys.argv[1])
