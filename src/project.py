import tkinter as tk
from tkinter import messagebox
from typing import Literal
from PIL import Image, ImageDraw, ImageTk
import shutil
import json
import math
import os

from config import __version__
from config import SectionType, SupportType, LoadType
from config import FTR_NAME_0, projects_dir
from gui.style import Theme
from font_manager import get_pillow_font

__all__ = ["Project", "Section", "Support", "Node", "Load", "PLLoad", "DLLoad"]


class Project:
    def __init__(self, project_name: str):
        self.name: str = project_name
        self.elastic_modulus: float | None = None
        self.fck: float | None = None
        self.section: Section | None = None
        self.nodes: list[Node] = []
        self.loads: list[Load] = []
        self.metadata: dict[str, str] = self.get_metadata()

        self.modified: bool = False  # flerken 2
        self.last_error: str | None = None

    def __str__(self):
        res = f"Project(\n"
        res += f"\tname={self.name},\n"
        res += f"\telastic_modulus={self.elastic_modulus},\n"
        res += f"\tfck={self.fck},\n"
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

    def get_project_path(self, check: bool = False) -> str | None:
        project_path = os.path.normpath(os.path.join(projects_dir, self.name))
        if check and not (os.path.exists(project_path) and os.path.isdir(project_path)):
            return None
        return project_path

    def get_data_path(self, check: bool = False) -> str | None:
        data_path = os.path.normpath(os.path.join(self.get_project_path(), "data.ftr"))
        if check and not (os.path.exists(data_path) and os.path.isfile(data_path)):
            return None
        return data_path

    def load_data(self) -> bool:
        data_path = self.get_data_path()
        try:
            with open(data_path, "r") as f:
                data = json.load(f)

            self.elastic_modulus = data["elastic_modulus"]  # flerken: fazer verificações do E para tipo int ou None
            self.fck = data["fck"]  # flerken: fazer verificações do fck para tipo float ou None

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
                if load["type"] == LoadType.PL:
                    self.loads.append(PLLoad(load["position"], load["Fx"], load["Fy"], load["Mz"]))
                elif load["type"] == LoadType.DL:
                    self.loads.append(DLLoad(load["start"], load["end"], load["q_start"], load["q_end"]))

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
                    "fck": self.fck,
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
        """Creates the project folder."""
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
            self.fck = None
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
        """Checks if the project exists."""
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
                 angle: float,
                 parent_node=None):
        self.type = support_type
        self.angle = float(angle)
        self.parent_node = parent_node

        self.imgDims = {"side": 60, "dy": 15}

    def __str__(self):
        return f"Support(type={self.type}, angle={self.angle})"

    def generate_image(self, clr: str) -> Image:
        side, dy = self.imgDims.values()

        dx = side / 3
        wi = 5 * dx
        height = side * math.sqrt(3) / 2
        width = 1

        img = Image.new("RGBA", (int(wi), int(wi)))
        dwg = ImageDraw.Draw(img)

        match self.type:
            case SupportType.Roller:
                dwg.line((wi / 2, 0, 4 * dx, height), fill=clr, width=width)
                dwg.line((wi / 2, 0, dx, height), fill=clr, width=width)
                dwg.line((dx, height, 4 * dx, height), fill=clr, width=width)

                dwg.line((0, height, wi, height), fill=clr, width=width)
                dwg.line((0, height + dy, wi, height + dy), fill=clr, width=width)
            case SupportType.Pinned:
                dwg.line((wi / 2, 0, 4 * dx, height), fill=clr, width=width)
                dwg.line((wi / 2, 0, dx, height), fill=clr, width=width)
                dwg.line((dx, height, 4 * dx, height), fill=clr, width=width)

                dwg.line((0, height, wi, height), fill=clr, width=width)
                for k in range(5):
                    dwg.line((k * dx, height + dy, (k + 1) * dx, height), fill=clr, width=width)
            case SupportType.Fixed:
                dwg.line((0, 0, wi, 0), fill=clr, width=width)
                for k in range(5):
                    dwg.line((k * dx, dy, (k + 1) * dx, 0), fill=clr, width=width)
        return img

    def update_image(self) -> list[ImageTk.PhotoImage]:
        img = self.generate_image(Theme.CAD.supports)
        return [ImageTk.PhotoImage(img)]

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
        if self.support:
            self.support.parent_node = self

        self.imgDims = {"radius": 5, "border": 0}

        self.is_highlighted: bool = False
        self.is_selected: bool = False

    def __str__(self):
        return f"Node(position={self.position}, support={self.support})"

    def generate_image(self, clr: str) -> Image:
        r, b = self.imgDims.values()

        img = Image.new("RGBA", (2 * (r + b), 2 * (r + b)))
        dwg = ImageDraw.Draw(img)

        pc = (r + b, r + b)
        dwg.circle(pc, radius=r, fill=clr, width=0)

        return img

    def update_image(self) -> list[ImageTk.PhotoImage]:
        img0 = self.generate_image(Theme.CAD.nodes[0])
        img1 = self.generate_image(Theme.CAD.nodes[1])
        return [ImageTk.PhotoImage(img0), ImageTk.PhotoImage(img1)]

    def check_hover(self, event: tk.Event, to_screen) -> bool:
        pos = to_screen(self.position, 0)
        dx, dy = event.x - pos[0], pos[1] - event.y
        d = math.sqrt(dx ** 2 + dy ** 2)
        if d <= 15:
            return True
        return False

    def select(self):
        self.is_selected = True
        self.is_highlighted = True

    def deselect(self):
        self.is_selected = False
        self.is_highlighted = False

    def to_dict(self):
        return {
            "position": self.position,
            "support": self.support.to_dict() if self.support else None
        }


class Load:
    def __init__(self, load_type: LoadType | Literal["PL", "DL"]):
        self._type = load_type

        self.is_highlighted: bool = False
        self.is_selected: bool = False

    @property
    def type(self) -> LoadType | Literal["PL", "DL"]:
        return self._type

    def update_image(self) -> list[ImageTk.PhotoImage]:
        raise NotImplementedError("Subclass must implement update_image()")

    def check_hover(self, event: tk.Event, to_screen) -> bool:
        raise NotImplementedError("Subclass must implement check_hover()")

    def select(self):
        raise NotImplementedError("Subclass must implement select()")

    def deselect(self):
        raise NotImplementedError("Subclass must implement deselect()")

    def to_dict(self):
        raise NotImplementedError("Subclass must implement to_dict()")


class PLLoad(Load):
    def __init__(self,
                 position: float,
                 fx: float = 0.0,
                 fy: float = 0.0,
                 mz: float = 0.0):
        super().__init__(load_type=LoadType.PL)
        self.position = float(position)
        self.Fx = float(fx)
        self.Fy = float(fy)
        self.Mz = float(mz)

        self.imgDims = {"Fx": {"length": 90, "arrow_x": 20, "arrow_y": 10},
                        "Fy": {"length": 90, "arrow_x": 10, "arrow_y": 20},
                        "Mz": {"radius_point": 4, "radius": 50, "arrow_x": 15, "arrow_y": 15},
                        "border": 30}

    def __str__(self):
        return f"Load(type={self.type}, position={self.position}, Fx={self.Fx}, Fy={self.Fy}, Mz={self.Mz})"

    def generate_image(self, clr: str) -> Image:
        ImageDraw.ImageDraw.font = get_pillow_font("Segoe UI Semibold", 20)
        width = 2

        Fx_len, Fx_ax, Fx_ay = self.imgDims["Fx"].values()
        Fy_len, Fy_ax, Fy_ay = self.imgDims["Fy"].values()
        Mz_rPt, Mz_r, Mz_ax, Mz_ay = self.imgDims["Mz"].values()
        border = self.imgDims["border"]

        side = int(2 * (max(Fx_len, Fy_len, Mz_r) + border))
        pc = (side / 2, side / 2)

        img = Image.new("RGBA", (side, side))
        dwg = ImageDraw.Draw(img)

        if self.Fx != 0:
            if self.Fx > 0:
                p1 = (pc[0] - Fx_len, pc[1])
                p2 = (pc[0] - Fx_ax, pc[1] - Fx_ay)
                p3 = (pc[0] - Fx_ax, pc[1] + Fx_ay)
                dwg.text((pc[0] - Fx_len / 2, pc[1] - 15), text=f"{self.Fx} kN", fill=clr, anchor="ms")
            else:
                p1 = (pc[0] + Fx_len, pc[1])
                p2 = (pc[0] + Fx_ax, pc[1] - Fx_ay)
                p3 = (pc[0] + Fx_ax, pc[1] + Fx_ay)
                dwg.text((pc[0] + Fx_len / 2, pc[1] - 15), text=f"{self.Fx} kN", fill=clr, anchor="ms")

            dwg.line((*pc, *p1), fill=clr, width=width)
            dwg.line((*pc, *p2), fill=clr, width=width)
            dwg.line((*pc, *p3), fill=clr, width=width)
        if self.Fy != 0:
            if self.Fy > 0:
                p1 = (pc[0], pc[1] + Fy_len)
                p2 = (pc[0] - Fy_ax, pc[1] + Fy_ay)
                p3 = (pc[0] + Fy_ax, pc[1] + Fy_ay)
                dwg.text((pc[0], pc[1] + Fy_len + 10), text=f"{self.Fy} kN", fill=clr, anchor="mt")
            else:
                p1 = (pc[0], pc[1] - Fy_len)
                p2 = (pc[0] - Fy_ax, pc[1] - Fy_ay)
                p3 = (pc[0] + Fy_ax, pc[1] - Fy_ay)
                dwg.text((pc[0], pc[1] - Fy_len - 10), text=f"{self.Fy} kN", fill=clr, anchor="ms")

            dwg.line((*pc, *p1), fill=clr, width=width)
            dwg.line((*pc, *p2), fill=clr, width=width)
            dwg.line((*pc, *p3), fill=clr, width=width)
        if self.Mz != 0:
            img_Mz = Image.new("RGBA", (2 * (Mz_r + border), 2 * (Mz_r + border)))
            dwg_Mz = ImageDraw.Draw(img_Mz)

            p0 = (border + Mz_r, border + Mz_r)
            p1 = (border, border)
            p2 = (2 * Mz_r + border, 2 * Mz_r + border)
            pa1 = (2 * Mz_r + border, Mz_r + border)
            if self.Mz > 0:
                pa2 = (2 * Mz_r + border - Mz_ax, Mz_r + border + Mz_ay)
                pa3 = (2 * Mz_r + border + Mz_ax, Mz_r + border + Mz_ay)
                start = 0
                end = 270
                angle = -45
            else:
                pa2 = (2 * Mz_r + border - Mz_ax, Mz_r + border - Mz_ay)
                pa3 = (2 * Mz_r + border + Mz_ax, Mz_r + border - Mz_ay)
                start = 90
                end = 360
                angle = 45

            dwg_Mz.circle(p0, radius=Mz_rPt, fill=clr, width=0)
            dwg_Mz.arc((*p1, *p2), start=start, end=end, fill=clr, width=width)
            dwg_Mz.line((*pa1, *pa2), fill=clr, width=width)
            dwg_Mz.line((*pa1, *pa3), fill=clr, width=width)
            img_Mz = img_Mz.rotate(angle=angle, resample=Image.Resampling.BICUBIC)

            dwg_Mz = ImageDraw.Draw(img_Mz)
            dwg_Mz.text((Mz_r + border, 0), text=f"{self.Mz} kN.m", fill=clr, anchor="mt")

            pt_ins = int(pc[0] - img_Mz.width / 2), int(pc[1] - img_Mz.height / 2)
            img.paste(img_Mz, pt_ins, mask=img_Mz)
        return img

    def update_image(self) -> list[ImageTk.PhotoImage]:
        img0 = self.generate_image(Theme.CAD.loads[0])
        img1 = self.generate_image(Theme.CAD.loads[1])
        return [ImageTk.PhotoImage(img0), ImageTk.PhotoImage(img1)]

    def check_hover(self, event: tk.Event, to_screen) -> bool:
        pos = to_screen(self.position, 0)
        dx, dy = event.x - pos[0], pos[1] - event.y
        border = 15

        if self.Fx != 0:
            length = self.imgDims["Fx"]["length"]
            if self.Fx > 0:
                x1, y1 = -length - border, -border
                x2, y2 = border, border
            else:
                x1, y1 = - border, -border
                x2, y2 = length + border, border
            if x1 <= dx <= x2 and y1 <= dy <= y2:
                return True
        if self.Fy != 0:
            length = self.imgDims["Fy"]["length"]
            if self.Fy > 0:
                x1, y1 = -border, -length - border
                x2, y2 = border, border
            else:
                x1, y1 = -border, -border
                x2, y2 = border, length + border
            if x1 <= dx <= x2 and y1 <= dy <= y2:
                return True
        if self.Mz != 0:
            d = math.sqrt(dx ** 2 + dy ** 2)
            r1 = self.imgDims["Mz"]["radius_point"] + 4
            r2 = self.imgDims["Mz"]["radius"] - border
            r3 = self.imgDims["Mz"]["radius"] + border
            if (d <= r1) or (r2 <= d <= r3):
                return True
        return False

    def select(self):
        self.is_selected = True
        self.is_highlighted = True

    def deselect(self):
        self.is_selected = False
        self.is_highlighted = False

    def to_dict(self):
        return {
            "type": str(self.type),
            "position": self.position,
            "Fx": self.Fx,
            "Fy": self.Fy,
            "Mz": self.Mz
        }


class DLLoad(Load):
    def __init__(self,
                 start: float,
                 end: float,
                 q_start: float,
                 q_end: float):
        super().__init__(load_type=LoadType.DL)
        self.start = float(start)
        self.end = float(end)
        self.q_start = float(q_start)
        self.q_end = float(q_end)

        self.imgDims = {"length_1": 90, "length_2": 110, "arrow_x": 10, "arrow_y": 20, "border": 15}

    def __str__(self):
        return f"Load(type={self.type}, start={self.start}, end={self.end}, q_start={self.q_start}, q_end={self.q_end})"

    def generate_image(self, clr: str) -> Image:
        ...

    def update_image(self) -> list[ImageTk.PhotoImage]:
        ...

    def check_hover(self, event: tk.Event, to_screen) -> bool:
        pos1 = to_screen(self.start, 0)
        pos2 = to_screen(self.end, 0)

        return False

    def select(self):
        self.is_selected = True
        self.is_highlighted = True

    def deselect(self):
        self.is_selected = False
        self.is_highlighted = False

    def to_dict(self):
        return {
            "type": str(self.type),
            "start": self.start,
            "end": self.end,
            "q_start": self.q_start,
            "q_end": self.q_end
        }
