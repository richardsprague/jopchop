# notes_make.py:  special case export when a note title = Notes*.md

from .note_handling import notes_date
from .notebook_handling import collect_all_resources_and_note_ids
from .joplin_api import get_notebooks, get_notes_from_notebook, get_note_details, get_sub_notebooks, get_note_resources, download_resource
from . import get_save_path

import datetime

import re
import os
import shutil

from unidecode import unidecode
from pathvalidate import sanitize_filename

def export_notes(notebook_name):
    """
    Exports all notes in `notebook_name` as one huge text string, suitable for saving to disk.

    Parameters:
    notebook_name (str): The notebook to be exported.

    Returns:
    str: The sanitized filename.
    """


    notebooks = get_notebooks()
    output = ""

    for notebook in notebooks:
            if notebook['title'] == notebook_name:
                resources_dict, note_ids_dict = collect_all_resources_and_note_ids(notebook, get_save_path())
                output+=export_notes_args(notebook, resources_dict, note_ids_dict)
                return output
    else:
        print(f"No notebook found with the name {notebook_name}")


def export_notes_args(notebook, resources_dict, note_ids_dict):
    notes = get_notes_from_notebook(notebook['id'])

    output = ""

    for note in notes:
        note_title, note_body, note_tags = get_note_details(note['id'])
        note_header = notes_date(note_title)
        output+=note_header+get_note_contents(note_title, note_body, note_tags, note['id'],resources_dict, note_ids_dict)

    # Recursively export sub-notebooks
    sub_notebooks = get_sub_notebooks(notebook['id'])
    if not sub_notebooks:  # This will be True if sub_notebooks is None or an empty list
        return output
    for sub_notebook in sub_notebooks:
        return output+export_notes_args(sub_notebook, resources_dict, note_ids_dict)

def notes_date(nname):
    """
    Extracts a date from the note name and formats it. If the note name does not match the expected pattern, 
    the original name is returned instead. Also generates an anchor ID based on the note name for linking purposes.

    Parameters:
    nname (str): The name of the note, expected to contain a date in the format "Notes yymmdd".

    Returns:
    str: An HTML string containing the formatted date or original name, enclosed in a div with a link anchor.
    """
    match = re.match(r"Notes (\d{6}) (\w+)", nname)
    if match:
        d = datetime.datetime.strptime(match.group(1), '%y%m%d').date()
        date_str = d.strftime("%A, %B %d")
        link_anchor = linkable_filename(nname)
        return f'<div id="{link_anchor}" class="raw"><p class="date-box">{date_str}</p></div>'
    else:
        return f'<div class="raw"><p class="date-box">{linkable_filename(nname)}</p></div>'



def linkable_filename(title):
    """
    Transforms the title into a sanitized string that can be used as a filename.
    Non-ASCII characters are converted to closest ASCII equivalents, and any character not 
    suitable for a filename is replaced with "-".

    Parameters:
    title (str): The original title string to be sanitized.

    Returns:
    str: The sanitized filename.
    """
    ascii_title = unidecode(title)  # Convert non-ASCII characters to closest ASCII equivalents
    sanitized = sanitize_filename(ascii_title, replacement_text="-")
    return sanitized

def replace_links_with_filenames(text, resources_dict, note_ids_dict):
    pattern = r'(!?)\[(.*?)\]\(:/([a-fA-F0-9]+)(#[^\)]+)?\)'  # Modified pattern to capture optional heading
    def repl(matchobj):
        is_image = matchobj.group(1)  # This will be '!' for images, and '' for links
        title = matchobj.group(2)
        id = matchobj.group(3)
        heading = matchobj.group(4)  # The heading part (including the '#'), or None if there's no heading
        # Check if id is a resource id or note id
        if id in resources_dict:
            filename = resources_dict[id]
            return f'{is_image}[{title}]({linkable_filename(filename)}{heading or ""})'  # Include heading if present
        elif id in note_ids_dict:
            note_title = note_ids_dict[id]
            note_title_encoded = linkable_filename(note_title)
            return f'[{title}](#{note_title_encoded}{heading or ""})'  # Include heading if present
        else:
            return f'[{title}](/index.html)'  # if not found, go home.
    return re.sub(pattern, repl, text)


def get_note_contents(note_title, note_body, note_tags, note_id, resources_dict, note_ids_dict):
    resources = get_note_resources(note_id)
    for resource in resources['items']:
        filename = linkable_filename(resource['title']) if resource['title'] else resource['id']
        resource_filepath = os.path.join(get_save_path(), filename)
        with open(resource_filepath, 'wb') as f:
            resource_data = download_resource(resource['id'])
            shutil.copyfileobj(resource_data, f)

    note_body = replace_links_with_filenames(note_body, resources_dict, note_ids_dict)

    return note_body

