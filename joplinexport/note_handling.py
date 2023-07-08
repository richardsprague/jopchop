import re
import os
import glob
import datetime
import shutil
import urllib.parse

import frontmatter
from io import StringIO

from unidecode import unidecode
from pathvalidate import sanitize_filename


from .joplin_api import get_note_resources, get_sub_notebooks, download_resource

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
            return f'{is_image}[{title}]({pandocable_filename(filename)}{heading or ""})'  # Include heading if present
        elif id in note_ids_dict:
            note_title = note_ids_dict[id]
            note_title_encoded = pandocable_filename(note_title)
            return f'[{title}]({note_title_encoded}.md{heading or ""})'  # Include heading if present
        else:
            return f'[{title}](/index.html)'  # if not found, go home.
    return re.sub(pattern, repl, text)


def save_note_to_file(note_title, note_body, note_tags, note_id, full_path, resources_dict, note_ids_dict, frontmatter=False):
    resources = get_note_resources(note_id)
    for resource in resources['items']:
        filename = pandocable_filename(resource['title']) if resource['title'] else resource['id']
        resource_filepath = os.path.join(full_path, filename)
        with open(resource_filepath, 'wb') as f:
            resource_data = download_resource(resource['id'])
            shutil.copyfileobj(resource_data, f)

    note_filename = os.path.join(full_path, f"{pandocable_filename(note_title)}.md")

    note_body = replace_links_with_filenames(note_body, resources_dict, note_ids_dict)

    with open(note_filename, 'w', encoding='utf-8') as f:
        # If frontmatter is True, add front matter to the note body before writing it to the file
        if frontmatter:
            note_body = note_with_header(note_body, note_title, note_tags)
        f.write(note_body)


def pandocable_filename(title):
    ascii_title = unidecode(title)  # Convert non-ASCII characters to closest ASCII equivalents
    sanitized = sanitize_filename(ascii_title, replacement_text="-")
    return sanitized

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


# Example usage:
# modify_yaml_header("path/to/file.md")
def modify_yaml_header(fname):
    """Modify the YAML header of a Markdown file"""
    with open(fname, "r", encoding="utf-8") as f:
        content = f.read()
        post = Frontmatter.loads(content)
        if "title" in post.keys():
            # Rename the "tags" key to "categories" if it exists
            if "tags" in post.keys():
                post["categories"] = post.pop("tags")
            # Write the modified YAML header and content back to the file
            with open(fname, "w", encoding="utf-8") as fw:
                fw.write(Frontmatter.dumps(post))



def note_with_header(note_body, note_title, note_tags):
    post = frontmatter.Post(note_body, title=note_title, categories=note_tags)
    return frontmatter.dumps(post)
