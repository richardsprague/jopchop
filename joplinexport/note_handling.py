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

def md_files(dir=os.getcwd()):
    return sorted(glob.glob(os.path.join(dir, 'Notes*.md')))

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
        link_anchor = pandocable_filename(nname)
        return f'<div id="{link_anchor}" class="raw"><p class="date-box">{date_str}</p></div>'
    else:
        return f'<div class="raw"><p class="date-box">{pandocable_filename(nname)}</p></div>'


def format_notes_date(nname):
    return notes_date(nname)

def concat_files(fnames, before_str="\n", after_str="\n"):
    """
    Reads multiple files and concatenates their contents, with a formatted date string from each filename inserted before its contents.

    Parameters:
    fnames (list): A list of file names to read and concatenate.
    before_str (str, optional): A string to insert before the date string for each file. Default is "\n".
    after_str (str, optional): A string to insert after the date string for each file. Default is "\n".

    Returns:
    str: A string containing the concatenated file contents, with date strings inserted.
    """
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
