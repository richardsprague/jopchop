# Export Your Joplin Notebook

This simple script uses the module `joplinexport` to export all the notes from a specific notebook in your Joplin instance.

## Requirements
You'll need a working instance of [Joplin](https://joplinapp.org/), running locally on your machine.

You also need your Joplin token, which you can find from the Desktop under `Settings/Web Clipper Advanced Options`.

Save the token in the file `.env` in your current directory

```sh
JOPLIN_TOKEN=yourlongtoken
```

## Install

Create and activate a new virtual environment and add the appropriate dependencies.

```sh
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Run the App

To download all notes from the Joplin notebook "MyNoteBook"

```sh
python jopchop.py "MyNoteBook"
```

There is also a standalone version if you prefer not to deal with Python

```sh
Jopchop "MyNotebook"
```



Everything, including any resources associated with the note, will be downloaded to the directory `downloads`

