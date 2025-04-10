from tkinter import messagebox
from typing import Any
import shutil
import json
import os

from config import SectionType, SupportType, LoadType
from config import FTR_NAME_0, configs_dir, projects_dir

__all__ = ["Project"]


class Project:
    def __init__(self, project_name: str | None = None):
        self.name: str | None = project_name

        self.elastic_modulus: float | None = None
        self.Section: Section | None = None
        self.Nodes: list[Node] = []
        self.Loads: list[Load] = []

        self.last_error: str | None = None

    def get_project_path(self, check: bool = True) -> str:
        project_path = os.path.normpath(os.path.join(projects_dir, self.name))
        if check:
            if not (os.path.exists(project_path) and os.path.isdir(project_path)):
                return ""
        return project_path

    def get_data_path(self, check: bool = True) -> str:
        data_path = os.path.normpath(os.path.join(self.get_project_path(), "data.ftr"))
        if check:
            if not (os.path.exists(data_path) and os.path.isfile(data_path)):
                return ""
        return data_path

    def load_data(self) -> bool:
        data_path = self.get_data_path()
        try:
            with open(data_path, "r") as f:
                data = json.load(f)

            self.elastic_modulus = data["elastic_modulus"]
            self.Section = Section(data["section"]["type"], data["section"]["dims"])

            self.Nodes = []
            for node in data["nodes"]:
                pos = node["position"]
                sup = node["support"]
                if sup:
                    sup_type = sup["type"]
                    ang = sup["angle"]
                    self.Nodes.append(Node(pos, Support(sup_type, ang)))
                else:
                    self.Nodes.append(Node(pos, None))

            self.Loads = []
            for load in data["loads"]:
                self.Loads.append(Load(load["type"], load["position"], load["value"]))

            return True
        except Exception as e:
            messagebox.showerror(FTR_NAME_0, f"ERRO ao carregar o arquivo de dados: {e}")
            self.last_error = str(e)
            return False

    def save_data(self) -> bool:
        data_path = self.get_data_path()
        try:
            with open(data_path, "w") as f:
                json.dump(self.data, f, indent=4)
            return True
        except Exception as e:
            messagebox.showerror(FTR_NAME_0, f"ERRO ao salvar o arquivo de dados: {e}")
            self.last_error = str(e)
            return False

    def create_new(self) -> bool:
        try:
            if not self.name:
                e = "Nome do projeto não definido."
                messagebox.showerror(FTR_NAME_0, f"ERRO: {e}")
                self.last_error = str(e)
                return False
            os.makedirs(self.get_project_path(check=False), exist_ok=True)
            default_data_path = os.path.normpath(os.path.join(configs_dir, "default_data.ftr"))
            with open(default_data_path, "r") as f:
                default_data = json.load(f)
            with open(self.get_data_path(check=False), "w") as f_out:
                json.dump(default_data, f_out, indent=4)
            self.data = default_data
            return True
        except Exception as e:
            messagebox.showerror(FTR_NAME_0, f"ERRO ao criar novo projeto: {e}")
            self.last_error = str(e)
            return False

    def delete(self, ask_user: bool = False) -> bool:
        try:
            res = True
            if ask_user:
                res = messagebox.askyesnocancel(FTR_NAME_0, "Tem certeza que deseja excluir o projeto?")
            if res:
                shutil.rmtree(self.get_project_path(check=False))
            return True
        except Exception as e:
            messagebox.showerror(FTR_NAME_0, f"ERRO ao deletar o projeto: {e}")
            self.last_error = str(e)
            return False

    def exists(self) -> bool:
        return os.path.isfile(self.get_data_path(check=False))


class Section:
    def __init__(self,
                 section_type: SectionType | str | None,
                 dims: dict | None):
        self.type = section_type
        self.dims = dims


class Support:
    def __init__(self,
                 support_type: SupportType | str,
                 angle: float):
        self.type = support_type
        self.angle = angle

    def __str__(self):
        return f"(type: {self.type}, angle: {self.angle})"


class Node:
    def __init__(self,
                 position: float,
                 support: Support | None):
        self.position = position
        self.support = support

    def __str__(self):
        return f"(pos: {self.position}, support: {self.support})"


class Load:
    def __init__(self,
                 load_type: LoadType | str,
                 position: list[float],
                 value: list[float]):
        self.type = load_type
        self.position = position
        self.value = value

    def __str__(self):
        return f"(type: {self.type}, position: {self.position}, value: {self.value})"
