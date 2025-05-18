from tkinter import messagebox
import tkinter as tk
import json
import math
import copy
import os

from config import __version__, SectionType, LoadType, SupportType, Settings
from manager import Language

__all__ = ["Project", "ProjectManager",
           "Section", "SectionR", "SectionI", "SectionT",
           "Node", "Support",
           "Load", "PLLoad", "DLLoad"]


class Project:
    def __init__(self, path: str | None = None):
        self.path: str | None = path

        # Project Data:
        self.elastic_modulus: float = 0.0
        self.fck: float = 0.0
        self.section: Section | None = None
        self.nodes: list[Node] = []
        self.loads: list[Load] = []
        self.metadata: dict[str, str] = self.get_metadata()

        self.modified: bool = False
        self.last_error: str | None = None

    def __repr__(self):
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

    @property
    def name(self):
        if self.path:
            return os.path.splitext(os.path.basename(self.path))[0]
        return "Untitled"

    def load_data(self) -> bool:
        """Load the project data."""
        if not self.exists():
            return False
        try:
            with open(self.path, "r") as f:
                data = json.load(f)

            self.elastic_modulus = data["elastic_modulus"]  # flerken: fazer verificações do E para tipo int ou None
            self.fck = data["fck"]  # flerken: fazer verificações do fck para tipo float ou None

            sec = data["section"]
            if sec:
                dims = sec["dims"]
                if sec["type"] == SectionType.R:
                    self.section = SectionR(dims["b"], dims["h"])
                elif sec["type"] == SectionType.I:
                    self.section = SectionI(dims["bf"], dims["d"], dims["tf"], dims["tw"], dims["R"])
                elif sec["type"] == SectionType.T:
                    self.section = SectionT(dims["bf"], dims["d"], dims["tf"], dims["tw"], dims["R"])
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

            self.modified = False
            return True
        except Exception as e:
            messagebox.showerror(Settings.FTR_NAME[0], f"{Language.get('Error', 'load_data')}: {e}")
            self.last_error = str(e)
            return False

    def save_data(self) -> bool:
        """Saves the project data."""
        if not self.path:
            return False
        try:
            data = self.to_dict()
            json_str = json.dumps(data, indent=4)
            json_str_with_tabs = json_str.replace("    ", "\t")
            with open(self.path, "w") as f:
                f.write(json_str_with_tabs)
            self.modified = False

            return True
        except Exception as e:
            messagebox.showerror(Settings.FTR_NAME[0], f"{Language.get('Error', 'save_data')}: {e}")
            self.last_error = str(e)
            return False

    def exists(self) -> bool:
        """Checks if the project exists."""
        if self.path:
            return os.path.exists(self.path) and os.path.isfile(self.path)
        return False

    @staticmethod
    def get_metadata() -> dict[str, str]:
        return {"created_by": "FTR", "version": __version__}

    def to_dict(self) -> dict:
        return {
            "elastic_modulus": self.elastic_modulus,
            "fck": self.fck,
            "section": self.section.to_dict() if self.section else None,
            "nodes": [node.to_dict() for node in self.nodes],
            "loads": [load.to_dict() for load in self.loads],
            "metadata": self.metadata
        }

    def check_integrity(self):
        node_pos = [node.position for node in self.nodes]
        if node_pos:
            min_pos, max_pos = min(node_pos), max(node_pos)

            if min_pos != 0:
                for node in self.nodes:
                    node.position -= min_pos
                for load in self.loads:
                    if isinstance(load, PLLoad):
                        load.position -= min_pos
                    elif isinstance(load, DLLoad):
                        load.start -= min_pos
                        load.end -= min_pos
                node_pos = [node.position for node in self.nodes]
                min_pos, max_pos = min(node_pos), max(node_pos)

            for load in self.loads:
                if isinstance(load, PLLoad):
                    if load.position < min_pos or load.position > max_pos:
                        self.loads.remove(load)
                elif isinstance(load, DLLoad):
                    if load.start < min_pos or load.end > max_pos:
                        self.loads.remove(load)
        else:
            self.loads.clear()


class ProjectManager:
    current: Project | None = None
    history: list[Project] = []
    history_ix: int = -1

    @classmethod
    def open(cls, project_path: str | None = None):
        cls.current = Project(project_path)
        cls.clear_history()
        cls.current.load_data()
        cls.save_history()

    @classmethod
    def save(cls):
        cls.current.save_data()

    @classmethod
    def save_as(cls, project_path: str):
        if project_path:
            cls.current.path = project_path
            cls.current.save_data()

    @classmethod
    def close(cls):
        cls.current = None
        cls.clear_history()

    @classmethod
    def save_history(cls) -> bool:
        if cls.current:
            cls.history = cls.history[:cls.history_ix + 1]  # remove future states
            cls.history.append(copy.deepcopy(cls.current))
            cls.history_ix += 1
            return True
        return False

    @classmethod
    def clear_history(cls):
        cls.history.clear()
        cls.history_ix = -1

    @classmethod
    def undo(cls) -> bool:
        if cls.history_ix > 0:
            cls.history_ix -= 1
            cls.current = copy.deepcopy(cls.history[cls.history_ix])
            return True
        return False

    @classmethod
    def redo(cls) -> bool:
        if cls.history_ix < len(cls.history) - 1:
            cls.history_ix += 1
            cls.current = copy.deepcopy(cls.history[cls.history_ix])
            return True
        return False


class Section:
    def __init__(self):
        self.dims = {}

    @property
    def type(self) -> SectionType | None:
        if isinstance(self, SectionR):
            return SectionType.R
        elif isinstance(self, SectionI):
            return SectionType.I
        elif isinstance(self, SectionT):
            return SectionType.T
        else:
            return None

    @property
    def CG(self) -> tuple[float, float]:
        raise NotImplementedError("Subclass must implement CG()")

    @property
    def Inertia(self) -> float:
        raise NotImplementedError("Subclass must implement Inertia()")

    def to_dict(self) -> dict:
        raise NotImplementedError("Subclass must implement to_dict()")


class SectionR(Section):
    def __init__(self, b: float, h: float):
        super().__init__()
        self.dims = {"b": float(b),
                     "h": float(h)}

    def __repr__(self):
        return f"Section(type={self.type}, dims={self.dims}, CG={self.CG}, I={self.Inertia})"

    @property
    def CG(self) -> tuple[float, float]:
        b, h = self.dims.values()
        return b / 2, h / 2

    @property
    def Inertia(self) -> float:
        b, h = self.dims.values()
        return (b * h ** 3) / 12

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "dims": self.dims
        }


class SectionI(Section):
    def __init__(self, bf: float, d: float, tf: float, tw: float, R: float = 0.0):
        super().__init__()
        self.dims = {"bf": float(bf),
                     "d": float(d),
                     "h": float(d - 2 * tf),
                     "tf": float(tf),
                     "tw": float(tw),
                     "R": float(R)}

    def __repr__(self):
        return f"Section(type={self.type}, dims={self.dims}, CG={self.CG}, I={self.Inertia})"

    @property
    def CG(self) -> tuple[float, float]:
        bf, d, h, tf, tw, R = self.dims.values()
        return bf / 2, d / 2

    @property
    def Inertia(self) -> float:
        bf, d, h, tf, tw, R = self.dims.values()
        return (bf * h ** 3) / 12

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "dims": self.dims
        }


class SectionT(Section):
    def __init__(self, bf: float, d: float, tf: float, tw: float, R: float = 0.0):
        super().__init__()
        self.dims = {"bf": float(bf),
                     "d": float(d),
                     "h": float(d - tf),
                     "tf": float(tf),
                     "tw": float(tw),
                     "R": float(R)}

    def __repr__(self):
        return f"Section(type={self.type}, dims={self.dims}, CG={self.CG}, I={self.Inertia})"

    @property
    def CG(self) -> tuple[float, float]:
        bf, d, h, tf, tw, R = self.dims.values()
        return bf / 2, d / 2

    @property
    def Inertia(self) -> float:
        bf, d, h, tf, tw, R = self.dims.values()
        return (bf * h ** 3) / 12

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "dims": self.dims
        }


class Support:
    def __init__(self,
                 support_type: SupportType,
                 angle: float,
                 parent_node=None):
        self.type = support_type
        self.angle = float(angle)
        self.parent_node = parent_node

        self.imgDims = {"side": 60, "dy": 15}

    def __repr__(self):
        return f"Support(type={self.type}, angle={self.angle})"

    def to_dict(self) -> dict:
        return {
            "type": self.type,
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

    def __repr__(self):
        return f"Node(position={self.position}, support={self.support})"

    def check_hover(self, event: tk.Event, to_screen) -> bool:
        pos = to_screen(self.position, 0)
        dx, dy = event.x - pos[0], pos[1] - event.y
        d = math.sqrt(dx ** 2 + dy ** 2)
        if d <= 15:
            return True
        return False

    def to_dict(self) -> dict:
        return {
            "position": self.position,
            "support": self.support.to_dict() if self.support else None
        }


class Load:
    def __init__(self):
        ...

    @property
    def type(self) -> LoadType:
        if isinstance(self, PLLoad):
            return LoadType.PL
        elif isinstance(self, DLLoad):
            return LoadType.DL

    def check_hover(self, event: tk.Event, to_screen) -> bool:
        raise NotImplementedError("Subclass must implement check_hover()")

    def to_dict(self) -> dict:
        raise NotImplementedError("Subclass must implement to_dict()")


class PLLoad(Load):
    def __init__(self,
                 position: float,
                 fx: float = 0.0,
                 fy: float = 0.0,
                 mz: float = 0.0):
        super().__init__()
        self.position = float(position)
        self.Fx = float(fx)
        self.Fy = float(fy)
        self.Mz = float(mz)

        self.imgDims = {"Fx": {"length": 90, "arrow_x": 20, "arrow_y": 10},
                        "Fy": {"length": 90, "arrow_x": 10, "arrow_y": 20},
                        "Mz": {"radius_point": 4, "radius": 50, "arrow_x": 15, "arrow_y": 15},
                        "border": 30}

    def __repr__(self):
        return f"Load(type={self.type}, position={self.position}, Fx={self.Fx}, Fy={self.Fy}, Mz={self.Mz})"

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

    def to_dict(self) -> dict:
        return {
            "type": self.type,
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
        super().__init__()
        self.start = float(start)
        self.end = float(end)
        self.q_start = float(q_start)
        self.q_end = float(q_end)

        self.imgDims = {"length_1": 90, "length_2": 110, "arrow_x": 10, "arrow_y": 20, "border": 15}

    def __repr__(self):
        return f"Load(type={self.type}, start={self.start}, end={self.end}, q_start={self.q_start}, q_end={self.q_end})"

    def check_hover(self, event: tk.Event, to_screen) -> bool:
        # pos1 = to_screen(self.start, 0)
        # pos2 = to_screen(self.end, 0)
        return False

    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "start": self.start,
            "end": self.end,
            "q_start": self.q_start,
            "q_end": self.q_end
        }
