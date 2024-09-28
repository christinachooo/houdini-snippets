import json
import logging
import os

logger = logging.getLogger(__name__)


def get_versioned_filepath(path: str, name: str, category: str) -> str:
    version = 1
    dir_path = os.path.join(path, category, name)
    filepath = f"{dir_path}_v{version:02d}.hip"

    while os.path.exists(filepath):
        version += 1
        filepath = f"{dir_path}_v{version:02d}.hip"
    return filepath


def get_directories(path: str) -> dict:
    snippets = {}

    if not os.path.isdir(path):
        return snippets

    for category in os.listdir(path):
        category_path = os.path.join(path, category)
        if os.path.isdir(category_path):
            category_files = os.listdir(category_path)
            if category_files:
                snippet_files = {}
                snippets[category] = snippet_files

                for file in category_files:
                    filename, ext = os.path.splitext(file)
                    filepath = os.path.join(category_path, file)
                    if ext == ".hip":
                        snippet_files[filename] = filepath
                        snippets[category] = snippet_files

    return snippets
