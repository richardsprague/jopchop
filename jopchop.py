import os
import sys


from joplinexport import get_save_path, notebook_handling

# Define the directory where you want to download the notes

# resource_id_to_file_path_main = {}
# note_id_to_title_main = {} # Initialize an empty dictionary outside save_note_to_file


def main(notebook_name):
    save_path = get_save_path("downloads")
     # check if save_path directory exists, if not create it
    if not os.path.exists(save_path):
        os.mkdir(save_path)
    notebook_handling.export_notebook(notebook_name)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python jopchop.py <notebook_name>")
    else:
        main(sys.argv[1])
