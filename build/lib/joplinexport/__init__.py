from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()
token = os.getenv("JOPLIN_TOKEN")
port = 41184

SAVE_PATH = None

SAVE_PATH = None

def get_save_path(path=None):
    global SAVE_PATH
    if path is not None:
        SAVE_PATH = path
    elif SAVE_PATH is None:
        SAVE_PATH = 'downloads'
    
    if not os.path.exists(SAVE_PATH):
        os.mkdir(SAVE_PATH)
    
    return SAVE_PATH
