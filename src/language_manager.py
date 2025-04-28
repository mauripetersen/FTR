import json
import os

from config import languages_dir
from configs_manager import configs_manager

__all__ = ["lang"]


class LanguageManager:
    def __init__(self, language: str = "en"):
        self.language = language
        self.translations = {}
        self.load_language()

    def load_language(self):
        path = os.path.join(languages_dir, f"{self.language}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                self.translations = json.load(f)
        except Exception as e:
            self.translations = {}
            raise FileNotFoundError(f'Error to load the language "{self.language}": {e}')

    def set(self, language: str):
        self.language = language
        self.load_language()

    def get(self, key1: str, key2: str | None = None) -> str:
        if key2:
            return self.translations.get(key1).get(key2)
        else:
            return self.translations.get(key1, key1)  # If not found, returns the key1 itself


# Instância global:
lang = LanguageManager(language=configs_manager.get(key="language", default="pt"))
