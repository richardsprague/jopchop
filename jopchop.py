import os
import shutil
import sys
import re
from joplinexport import joplinexport

# Define the directory where you want to download the notes
save_path = 'downloads'
resource_id_to_file_path = {}

def replace_links_with_filenames(text):
    pattern = r'\!\[([^\]]*)\]\(:/([a-z0-9]+)\)'
    def repl(matchobj):
        title = matchobj.group(1)
        resource_id = matchobj.group(2)
        filename = resource_id_to_file_path.get(resource_id, '')
        return f'![{title}]({filename})'
    return re.sub(pattern, repl, text)


def save_note_to_file(note_title, note_body, note_id):

    resources = joplinexport.get_note_resources(note_id)
    for resource in resources['items']:
        filename = resource['title'].replace('/', '-')
        resource_filepath = os.path.join(save_path, filename)
        with open(resource_filepath, 'wb') as f:
            resource_data = joplinexport.download_resource(resource['id'])
            shutil.copyfileobj(resource_data, f)
        # Add the resource filename to the dictionary that maps resource IDs to filenames
        resource_id_to_file_path[resource['id']] = filename

    note_filename = os.path.join(save_path, f"{note_title.replace('/', '-')}.md")
    with open(note_filename, 'w', encoding='utf-8') as f:
        # Replace the resource links with markdown links to the resource files before writing the body to the file
        note_body = replace_links_with_filenames(note_body)
        f.write(note_body)



 


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
