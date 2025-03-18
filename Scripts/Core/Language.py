import json
import os

language_data = {}

def load_language(language_code):
    global language_data
    language_file = f"languages/{language_code.lower()}.json"
    
    if not os.path.exists(language_file):
        raise FileNotFoundError(f"Language file '{language_file}' not found.")
    
    with open(language_file, 'r', encoding='utf-8') as file:
        language_data = json.load(file)

def get_message(key):
    return language_data.get(key, f"Message key '{key}' not found.")
