import re
import os
import shutil
import urllib.parse
from .joplin_api import get_note_resources, get_sub_notebooks, download_resource

def replace_links_with_filenames(text, resources_dict, note_ids_dict):
    pattern = r'(!?)\[(.*?)\]\(:/([a-fA-F0-9]+)\)'
    def repl(matchobj):
        is_image = matchobj.group(1)  # This will be '!' for images, and '' for links
        title = matchobj.group(2)
        id = matchobj.group(3)
        # Check if id is a resource id or note id
        if id in resources_dict:
            filename = resources_dict[id]
            return f'{is_image}[{title}]({filename})' 
        elif id in note_ids_dict:
            note_title = note_ids_dict[id]
            note_title_encoded = urllib.parse.quote(note_title) + '.md'
            return f'[{title}]({note_title_encoded})'
        else:
            return matchobj.group(0)  # If id not found, return the original link
    return re.sub(pattern, repl, text)

def save_note_to_file(note_title, note_body, note_id, full_path, resources_dict, note_ids_dict):

    resources = get_note_resources(note_id)
    for resource in resources['items']:
        filename = resource['title'].replace('/', '-') if resource['title'] else resource['id']
        resource_filepath = os.path.join(full_path, filename)
        with open(resource_filepath, 'wb') as f:
            resource_data = download_resource(resource['id'])
            shutil.copyfileobj(resource_data, f)
        # Add the resource filename to the dictionary that maps resource IDs to filenames
        # Don't need this anymore
        # resource_id_to_file_path_main[resource['id']] = filename

    note_filename = os.path.join(full_path, f"{note_title.replace('/', '-')}.md")

   # note_id_to_title_main[note_id] = note_title

    with open(note_filename, 'w', encoding='utf-8') as f:
        # Replace the resource links with markdown links to the resource files before writing the body to the file
        note_body = replace_links_with_filenames(note_body, resources_dict, note_ids_dict)
        f.write(note_body)



