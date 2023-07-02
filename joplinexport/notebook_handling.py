
import os
from .joplin_api import get_notes_from_notebook, get_note_resources, get_sub_notebooks, get_note_details, get_notebooks
from .note_handling import save_note_to_file
from . import get_save_path


def collect_all_resources_and_note_ids(notebook, parent_path):
    full_path = os.path.join(parent_path, notebook['title'].replace('/', '-'))
    
    resources = {}
    note_ids = {}

    notes = get_notes_from_notebook(notebook['id'])
    for note in notes:
        note_title = note['title']
        note_id = note['id']
        note_ids[note_id] = note_title  # Populate note_id_to_title
    
        note_resources = get_note_resources(note_id)
        for resource in note_resources['items']:
            filename = resource['title'].replace('/', '-') if resource['title'] else resource['id']
            resources[resource['id']] = filename

    sub_notebooks = get_sub_notebooks(notebook['id'])
    for sub_notebook in sub_notebooks:
        sub_notebook_resources, sub_notebook_note_ids = collect_all_resources_and_note_ids(sub_notebook, full_path)
        resources.update(sub_notebook_resources)
        note_ids.update(sub_notebook_note_ids)

    return resources, note_ids

def export_notebook(notebook_name):


    notebooks = get_notebooks()
    full_path = get_save_path()

    for notebook in notebooks:
            if notebook['title'] == notebook_name:
                resources_dict, note_ids_dict = collect_all_resources_and_note_ids(notebook, get_save_path())
                export_notebook_args(notebook, get_save_path(), resources_dict, note_ids_dict)
                break
    else:
        print(f"No notebook found with the name {notebook_name}")
    export_notebook_args(notebook, full_path, resources_dict, note_ids_dict)



def export_notebook_args(notebook, full_path, resources_dict, note_ids_dict):
    notes = get_notes_from_notebook(notebook['id'])

    for note in notes:
        note_title, note_body = get_note_details(note['id'])
        save_note_to_file(note_title, note_body, note['id'], full_path, resources_dict, note_ids_dict)

    # Recursively export sub-notebooks
    sub_notebooks = get_sub_notebooks(notebook['id'])
    if not sub_notebooks:  # This will be True if sub_notebooks is None or an empty list
        return
    for sub_notebook in sub_notebooks:
        export_notebook_args(sub_notebook, full_path, resources_dict, note_ids_dict)

