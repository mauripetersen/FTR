import json
import os

from config import Settings

__all__ = ["Language"]


class Language:
    translations = {}

    @classmethod
    def load(cls):
        path = os.path.join(Settings.LANGUAGES_DIR, f"{Settings.language}.json")
        try:
            with open(path, "r", encoding="utf-8") as f:
                cls.translations = json.load(f)
        except Exception as e:
            cls.translations = {}
            raise FileNotFoundError(f'Error to load the language "{Settings.language}": {e}')

    @classmethod
    def get(cls, *args) -> str | None:
        if not args:
            return None
        last = cls.translations
        for arg in args:
            if isinstance(last, dict):
                last = last.get(arg, arg)  # If not found, returns the key itself
            else:
                break
        return last
