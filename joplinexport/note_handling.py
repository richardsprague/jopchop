import re
import os
import glob
import datetime
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


def md_files(dir=os.getcwd()):
    return sorted(glob.glob(os.path.join(dir, 'Notes*.md')))

def notes_date(nname):
    match = re.match(r"Notes (\d{6}) (\w+)", nname)
    if match:
        d = datetime.datetime.strptime(match.group(1), '%y%m%d').date()
        date_str = d.strftime("%A, %B %d")
        return f'<div class="raw"><p class="date-box">{date_str}</p></div>'
    else:
        return f'<div class="raw"><p class="date-box">{nname}</p></div>'

def format_notes_date(nname):
    return notes_date(nname)

def concat_files(fnames, before_str="\n", after_str="\n"):
    contents = []
    for fname in fnames:
        with open(fname, "r") as f:
            fcontents = f.read()
            contents.append(before_str + format_notes_date(os.path.splitext(os.path.basename(fname))[0]) + after_str + fcontents)
    return "\n".join(contents)

def remove_md_files(dir=os.getcwd()):
    md_file_list = glob.glob(os.path.join(dir, '*.md'))
    days_of_week = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    for file in md_file_list:
        basename = os.path.basename(file)
        if re.match(r"Notes \d{6} ", basename) and any(day in basename for day in days_of_week):

            try:
                os.remove(file)
            except OSError as e:
                print(f"Error: {e.filename} - {e.strerror}.")


