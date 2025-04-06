import json
import os

from config import projects_dir

__all__ = ["BeamData"]


class BeamData:
    def __init__(self, path: str):
        with open(path, "r") as f:
            self.raw_data = json.load(f)

        self.elastic_modulus = float(self.raw_data.get("elastic_modulus", 0))
        self.section_type = self.raw_data["section"]["type"]
        self.b = float(self.raw_data["section"]["b"])
        self.h = float(self.raw_data["section"]["h"])
        self.supports = self.raw_data.get("supports", [])
        self.loads = self.raw_data.get("loads", [])


def load_data(project_path: str) -> bool:
    data_path = os.path.normpath(os.path.join(project_path, "data.ftr"))

    try:
        if not (os.path.exists(data_path) and os.path.isfile(data_path)):
            return False

        return True
    except Exception as e:
        print(f"error: {e}")
        return False


if __name__ == "__main__":
    path = os.path.normpath(os.path.join(projects_dir, "Projeto 1"))
    print(load_data(path))
