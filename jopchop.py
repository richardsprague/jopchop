import os
import shutil
import sys
import re
import urllib.parse

from joplinexport import joplinexport

# Define the directory where you want to download the notes
save_path = 'downloads'
resource_id_to_file_path = {}
note_id_to_title = {} # Initialize an empty dictionary outside save_note_to_file



def replace_links_with_filenames(text):
    pattern = r'(!?)\[(.*?)\]\(:/([a-fA-F0-9]+)\)'
    def repl(matchobj):
        is_image = matchobj.group(1)  # This will be '!' for images, and '' for links
        title = matchobj.group(2)
        id = matchobj.group(3)
        # Check if id is a resource id or note id
        if id in resource_id_to_file_path:
            filename = resource_id_to_file_path[id]
            return f'{is_image}[{title}]({filename})' 
        elif id in note_id_to_title:
            note_title = note_id_to_title[id]
            note_title_encoded = urllib.parse.quote(note_title) + '.md'
            return f'[{title}]({note_title_encoded})'
        else:
            return matchobj.group(0)  # If id not found, return the original link
    return re.sub(pattern, repl, text)

def save_note_to_file(note_title, note_body, note_id):

    resources = joplinexport.get_note_resources(note_id)
    for resource in resources['items']:
        filename = resource['title'].replace('/', '-') if resource['title'] else resource['id']
        resource_filepath = os.path.join(save_path, filename)
        with open(resource_filepath, 'wb') as f:
            resource_data = joplinexport.download_resource(resource['id'])
            shutil.copyfileobj(resource_data, f)
        # Add the resource filename to the dictionary that maps resource IDs to filenames
        resource_id_to_file_path[resource['id']] = filename

    note_filename = os.path.join(save_path, f"{note_title.replace('/', '-')}.md")

    note_id_to_title[note_id] = note_title

    with open(note_filename, 'w', encoding='utf-8') as f:
        # Replace the resource links with markdown links to the resource files before writing the body to the file
        note_body = replace_links_with_filenames(note_body)
        f.write(note_body)



 


def export_notebook(notebook):
    notes = joplinexport.get_notes_from_notebook(notebook['id'])

    # FIRST PASS
    for note in notes:
        note_title = note['title']
        note_id = note['id']
        note_id_to_title[note_id] = note_title  # Populate note_id_to_title
    

    for note in notes:
        note_title, note_body = joplinexport.get_note_details(note['id'])
        save_note_to_file(note_title, note_body, note['id'])

    # Recursively export sub-notebooks
    sub_notebooks = joplinexport.get_sub_notebooks(notebook['id'])
    if not sub_notebooks:  # This will be True if sub_notebooks is None or an empty list
        return
    for sub_notebook in sub_notebooks:
        export_notebook(sub_notebook)


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
