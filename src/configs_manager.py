import json
import os

from config import configs_dir

__all__ = ["configs_manager"]


class ConfigsManager:
    def __init__(self):
        self.path = os.path.join(configs_dir, "configs.json")
        self.configs = {}
        self.load()

    def load(self):
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                self.configs = json.load(f)
        else:
            self.configs = self.default_configs()
            self.save()

    def save(self):
        json_str = json.dumps(self.configs, indent=4)
        json_str_with_tabs = json_str.replace("    ", "\t")
        with open(self.path, "w") as f:
            f.write(json_str_with_tabs)

    def get(self, key, default=None):
        return self.configs.get(key, default)

    def set(self, key, value):
        self.configs[key] = value
        self.save()

    @staticmethod
    def default_configs():
        return {
            "language": "pt",
            "theme": "dark"
        }


# Instância global:
configs_manager = ConfigsManager()
