## this is a sample script intended to download a bunch of specific notes
## python notes_script.py <notebook-name>
## It will download as .md and then concatenate all the files into one big huge notes.qmd file
## intended to be processed later with Quarto.


import os
import sys


from joplinexport import get_save_path, notebook_handling, note_handling

JOINED_FILENAME = "notes.qmd" # f"all_{datetime.now().strftime('%Y%m%d-%H%M%S')}.md"


def main(notebook_name):
    save_path = get_save_path("downloads")
     # check if save_path directory exists, if not create it
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    notebook_handling.export_notebook(notebook_name)
       # Check if the directory exists
    if not os.path.isdir(save_path):
        print(f"Error: Directory not found: {save_path}")
        sys.exit(1)

    # Get a list of file paths for all Markdown files in the directory
    all_md_files = note_handling.md_files(save_path)

    # Sort the list of file paths alphabetically by filename
    all_files = sorted(all_md_files)

    # Concatenate the file contents and format the output
    output = note_handling.concat_files(all_files)

    # Write the output to a file
    output_filename = os.path.join(save_path, JOINED_FILENAME)
    with open(output_filename, "w") as f:
        f.write(output)
    
    # note_handling.remove_md_files(save_path)

    print(f"Output written to file: {output_filename}")



if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python notes_script.py <notebook_name>")
    else:
        main(sys.argv[1])
