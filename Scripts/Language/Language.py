import json
import os
import toml

class LanguageLoader:
    def __init__(self, config_path='config.toml'):
        self.config_path = config_path
        self.language = 'en'
        self.translations = {}
        self.load_config()
        self.load_translations()

    def load_config(self):
        if os.path.exists(self.config_path):
            with open(self.config_path, 'r') as file:
                config = toml.load(file)
                self.language = config.get('Language', 'en')

    def load_translations(self):
        lang_file = f'Scripts/Language/Files/{self.language}.json'
        if os.path.exists(lang_file):
            with open(lang_file, 'r', encoding='utf-8') as file:
                self.translations = json.load(file)

    def get_translation(self, key):
        return self.translations.get(key, key)

language_loader = LanguageLoader()

def translate(key):
    return language_loader.get_translation(key)
