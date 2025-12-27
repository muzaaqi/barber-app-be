import os

BASE_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DOCS_DIR = os.path.join(BASE_APP_DIR, 'docs')

def get_doc_path(filename):
    path_parts = filename.split('/')
    full_path = os.path.join(DOCS_DIR, *path_parts)

    return full_path