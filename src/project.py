from tkinter import messagebox
from typing import Literal
import shutil
import json
import os

from config import __version__
from config import SectionType, SupportType, LoadType
from config import FTR_NAME_0, projects_dir

__all__ = ["Project", "Section", "Support", "Node", "Load"]


class Project:
    def __init__(self, project_name: str | None = None):
        self.name: str | None = project_name
        self.elastic_modulus: float | None = None
        self.section: Section | None = None
        self.nodes: list[Node] = []
        self.loads: list[Load] = []
        self.metadata: dict[str, str] = self.get_metadata()

        self.modified: bool = False
        self.last_error: str | None = None

    def __str__(self):
        res = f"Project(\n"
        res += f"\tname={self.name},\n"
        res += f"\telastic_modulus={self.elastic_modulus},\n"
        res += f"\tsection={self.section}\n"
        res += f"\tnodes=[\n"
        for node in self.nodes:
            res += f"\t\t{node},\n"
        res += f"\t],\n"
        res += f"\tloads=[\n"
        for load in self.loads:
            res += f"\t\t{load},\n"
        res += f"\t],\n"
        res += f"\tmetadata={self.metadata}\n"
        res += ")"

        return res

    def get_project_path(self, check: bool = False) -> str:
        project_path = os.path.normpath(os.path.join(projects_dir, self.name))
        if check:
            if not (os.path.exists(project_path) and os.path.isdir(project_path)):
                return ""
        return project_path

    def get_data_path(self, check: bool = False) -> str:
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

            sec = data["section"]
            if sec:
                self.section = Section(sec["type"], sec["dims"])
            else:
                self.section = None

            self.nodes = []
            for node in data["nodes"]:
                pos = node["position"]
                sup = node["support"]
                if sup:
                    self.nodes.append(Node(pos, Support(sup["type"], sup["angle"])))
                else:
                    self.nodes.append(Node(pos, None))

            self.loads = []
            for load in data["loads"]:
                self.loads.append(Load(load["type"], load["positions"], load["values"]))

            self.metadata = data["metadata"]
            self.modified = False  # flerken 2

            return True
        except Exception as e:
            messagebox.showerror(FTR_NAME_0, f"ERRO ao carregar o arquivo de dados: {e}")
            self.last_error = str(e)
            return False

    def save_data(self) -> bool:
        try:
            data_path = self.get_data_path()

            data = {"elastic_modulus": self.elastic_modulus,
                    "section": self.section.to_dict() if self.section else None,
                    "nodes": [node.to_dict() for node in self.nodes],
                    "loads": [load.to_dict() for load in self.loads],
                    "metadata": self.metadata}

            json_str = json.dumps(data, indent=4)
            json_str_with_tabs = json_str.replace("    ", "\t")
            with open(data_path, "w") as f:
                f.write(json_str_with_tabs)

            self.modified = False  # flerken 2

            return True
        except Exception as e:
            messagebox.showerror(FTR_NAME_0, f"ERRO ao salvar o arquivo de dados: {e}")
            self.last_error = str(e)
            return False

    def create_new(self, ask_user: bool = True) -> bool:
        try:
            if not self.name:
                e = "Nome do projeto não definido."
                messagebox.showerror(FTR_NAME_0, f"ERRO: {e}")
                self.last_error = str(e)
                return False

            project_path = self.get_project_path()
            if os.path.exists(project_path) and os.path.isdir(project_path):
                if ask_user:
                    if not messagebox.askyesnocancel(FTR_NAME_0, "Já existe um projeto com este nome. Sobrescrever?"):
                        return False
                self.delete()

            os.makedirs(project_path, exist_ok=True)

            # clear the variables:
            self.elastic_modulus = None
            self.section = None
            self.nodes = []
            self.loads = []
            self.metadata = self.get_metadata()
            self.last_error = None

            self.save_data()
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
                shutil.rmtree(self.get_project_path())
            return True
        except Exception as e:
            messagebox.showerror(FTR_NAME_0, f"ERRO ao deletar o projeto: {e}")
            self.last_error = str(e)
            return False

    def exists(self) -> bool:
        return os.path.isfile(self.get_data_path())

    @staticmethod
    def get_metadata() -> dict[str, str]:
        return {"created_by": "FTR", "version": __version__}


class Section:
    def __init__(self,
                 section_type: SectionType | Literal["R", "I", "T"] | None,
                 dims: dict[str, float] | None):
        self.type = section_type
        self.dims = {key: float(val) for key, val in dims.items()} if dims else None

    def __str__(self):
        return f"Section(type={self.type}, dims={self.dims})"

    def to_dict(self):
        return {
            "type": self.type,
            "dims": self.dims
        }


class Support:
    def __init__(self,
                 support_type: SupportType | Literal["roller", "pinned", "fixed"],
                 angle: float):
        self.type = support_type
        self.angle = float(angle)

    def __str__(self):
        return f"Support(type={self.type}, angle={self.angle})"

    def to_dict(self):
        return {
            "type": str(self.type),
            "angle": self.angle
        }


class Node:
    def __init__(self,
                 position: float,
                 support: Support | None):
        self.position = float(position)
        self.support = support

        self.is_highlighted = False
        self.is_selected = False

    def __str__(self):
        return f"Node(position={self.position}, support={self.support})"

    def to_dict(self):
        return {
            "position": self.position,
            "support": self.support.to_dict() if self.support else None
        }


class Load:
    def __init__(self,
                 load_type: LoadType | Literal["M", "PL", "UDL", "LVDL"],
                 positions: list[float],
                 values: list[float]):
        self.type = load_type
        self.positions = [float(pos) for pos in positions]
        self.values = [float(val) for val in values]

        self.is_highlighted = False
        self.is_selected = False

    def __str__(self):
        return f"Load(type={self.type}, positions={self.positions}, values={self.values})"

    def to_dict(self):
        return {
            "type": self.type,
            "positions": self.positions,
            "values": self.values
        }
