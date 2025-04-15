import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from typing import Any
import math

from gui.style import Theme
from project import Project, Section, Support, Node, Load, LoadType, SupportType

__all__ = ["CADInterface"]


class CADInterface(ctk.CTkFrame):
    def __init__(self, master: ctk.CTkFrame, project: Project):
        super().__init__(master)
        self.project = project

        self.canvas = tk.Canvas(self, bg=Theme.CAD.background, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        self.view = {
            "scale": 1,
            "ppm": 100,
            "P": (-5.0, 5.0)
        }

        self.garbage = []
        self.select_rect = None
        self.start_x = self.start_y = 0

        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Button-1>", self.mouse_down_left)
        self.canvas.bind("<B1-Motion>", self.mouse_move_left)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_up_left)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        # self.adding_load = False
        # self.canvas.bind("<Button-3>", self.toggle_add_load)

        self.after(200, self.draw_canvas)

    def on_motion(self, event):
        self.master.master.FrmStatusBar.LblPos.configure(text=f"{self.to_model(event.x, event.y, 2)}")

        nearest = self.get_nearest(event)
        if nearest:
            self.canvas.configure(cursor="hand2")
        else:
            self.canvas.configure(cursor="arrow")

        self.draw_canvas()

    def get_nearest(self, event) -> Any:
        for node in self.project.nodes:
            if check_hover_node(node, event.x, event.y, self.to_screen):
                return node
        for load in self.project.loads:
            if check_hover_load(load, event.x, event.y, self.to_screen):
                return load
        return None

    def mouse_down_left(self, event):
        self.start_x = event.x
        self.start_y = event.y

        # Creates the rectangle with equal initial coordinates
        self.select_rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                                        outline=Theme.CAD.select_rect)

    def mouse_move_left(self, event):
        # Updates rectangle while dragging:
        self.canvas.coords(self.select_rect, self.start_x, self.start_y, event.x, event.y)

    def mouse_up_left(self, event):
        # Aqui você pode fazer lógica de seleção de elementos
        # coords = self.canvas.coords(self.select_rect)
        # print("Selecionado:", coords)

        # Remove the selection rectangle (by ID)
        self.canvas.delete(self.select_rect)
        self.select_rect = None

    def on_mouse_wheel(self, event):
        Mzx, Mzy = self.to_model(event.x, event.y)
        s = 1.1 if event.delta > 0 else 1 / 1.1

        P0x, P0y = self.view["P"]
        P1x = Mzx - (Mzx - P0x) / s
        P1y = Mzy - (Mzy - P0y) / s

        self.view["scale"] *= s
        self.view["P"] = (P1x, P1y)

        self.draw_canvas()

    def to_screen(self, x_model: float, y_model: float) -> tuple[int, int]:
        """
        Converts coordinates from model to canvas.
        """
        scale, ppm, P = self.view.values()
        x_screen = int((x_model - P[0]) * ppm * scale)
        y_screen = int((P[1] - y_model) * ppm * scale)
        return x_screen, y_screen

    def to_model(self, x_screen: int, y_screen: int, ndigits: int = 0) -> tuple[float, float]:
        """
        Converts coordinates from canvas to model.
        """
        scale, ppm, P = self.view.values()
        x_model = P[0] + x_screen / (ppm * scale)
        y_model = P[1] - y_screen / (ppm * scale)
        if ndigits > 0:
            x_model = round(x_model, ndigits)
            y_model = round(y_model, ndigits)
        return x_model, y_model

    def draw_canvas(self):
        for g in self.garbage:
            self.canvas.delete(g)
        self.garbage.clear()

        nodes = self.project.nodes
        loads = self.project.loads
        scale, ppm, P = self.view.values()

        # GRID:
        if self.master.master.FrmStatusBar.VarGrid.get():
            dx, dy = (1, 1)
            kx0 = math.ceil(P[0] / dx)
            kx1 = math.floor((P[0] + self.canvas.winfo_width() / (scale * ppm)) / dx)
            ky0 = math.ceil((P[1] - self.canvas.winfo_height() / (scale * ppm)) / dy)
            ky1 = math.floor(P[1] / dy)

            for k in range(kx0, kx1 + 1):
                p1 = self.to_screen(k * dx, (ky0 - 1) * dy)
                p2 = self.to_screen(k * dx, (ky1 + 1) * dy)
                self.garbage.append(self.canvas.create_line(*p1, *p2, fill=Theme.CAD.grid[1], width=1))

            for k in range(ky0, ky1 + 1):
                p1 = self.to_screen((kx0 - 1) * dx, k * dy)
                p2 = self.to_screen((kx1 + 1) * dx, k * dy)
                self.garbage.append(self.canvas.create_line(*p1, *p2, fill=Theme.CAD.grid[1], width=1))

            p1 = self.to_screen(0, (ky0 - 1) * dy)
            p2 = self.to_screen(0, (ky1 + 1) * dy)
            self.garbage.append(self.canvas.create_line(*p1, *p2, fill=Theme.CAD.grid[0], width=2))

            p1 = self.to_screen((kx0 - 1) * dx, 0)
            p2 = self.to_screen((kx1 + 1) * dx, 0)
            self.garbage.append(self.canvas.create_line(*p1, *p2, fill=Theme.CAD.grid[0], width=2))

        # SPANS:
        for k in range(len(nodes) - 1):
            x1, y1 = self.to_screen(nodes[k].position, 0)
            x2, y2 = self.to_screen(nodes[k + 1].position, 0)
            self.garbage.append(self.canvas.create_line(x1, y1, x2, y2, fill=Theme.CAD.spans, width=5))

        # SUPPORTS:
        for node in nodes:
            if node.support:
                draw_support(self.canvas, node, self.to_screen)

        # LOADS:
        for load in loads:
            draw_load(self.canvas, load, self.to_screen)

        # NODES:
        for node in nodes:
            draw_node(self.canvas, node, self.to_screen)


def draw_spans(canvas: tk.Canvas, node0: Node, node1: Node, to_screen):
    ...


def draw_support(canvas: tk.Canvas, node: Node, to_screen):
    clr = Theme.CAD.supports
    pos = to_screen(node.position, 0)
    side, dy = node.support.imgDims.values()

    dx = side / 3
    wi = 5 * dx
    height = side * math.sqrt(3) / 2

    img = Image.new("RGBA", (int(wi), int(wi)))
    dwg = ImageDraw.Draw(img)
    width = 2

    match node.support.type:
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

    node.support.image = ImageTk.PhotoImage(img)
    canvas.create_image(*pos, anchor="n", image=node.support.image)


def draw_load(canvas: tk.Canvas, load: Load, to_screen):
    clr = Theme.CAD.loads[1] if load.is_highlighted else Theme.CAD.loads[0]

    if load.type == LoadType.M:
        pos = to_screen(load.positions[0], 0)
        val = load.values[0]
        rPt, r, ax, ay, b = load.imgDims[LoadType.M].values()

        img = Image.new("RGBA", (2 * (r + b), 2 * (r + b)))
        dwg = ImageDraw.Draw(img)

        p0 = (b + r, b + r)
        p1 = (b, b)
        p2 = (2 * r + b, 2 * r + b)
        pa1 = (2 * r + b, r + b)
        if val > 0:
            pa2 = (2 * r + b - ax, r + b + ay)
            pa3 = (2 * r + b + ax, r + b + ay)
            start = 0
            end = 270
            angle = -45
        else:
            pa2 = (2 * r + b - ax, r + b - ay)
            pa3 = (2 * r + b + ax, r + b - ay)
            start = 90
            end = 360
            angle = 45

        dwg.circle(p0, radius=rPt, fill=clr, width=0)
        dwg.arc((*p1, *p2), start=start, end=end, fill=clr, width=2)
        dwg.line((*pa1, *pa2), fill=clr, width=2)
        dwg.line((*pa1, *pa3), fill=clr, width=2)
        img = img.rotate(angle=angle, resample=Image.Resampling.BICUBIC)

        load.image = ImageTk.PhotoImage(img)
        canvas.create_image(*pos, anchor="c", image=load.image)
    elif load.type == LoadType.PL:
        val = load.values[0]
        pos = to_screen(load.positions[0], 0)
        h, ax, ay, b = load.imgDims[LoadType.PL].values()

        img = Image.new("RGBA", (2 * b, h))
        dwg = ImageDraw.Draw(img)

        if val > 0:
            p1 = (b, 0)
            p2 = (b, h)
            p3 = (b - ax, ay)
            p4 = (b + ax, ay)
            anchor = "n"
        else:
            p1 = (b, h)
            p2 = (b, 0)
            p3 = (b - ax, h - ay)
            p4 = (b + ax, h - ay)
            anchor = "s"

        dwg.line((*p1, *p2), fill=clr, width=2)
        dwg.line((*p1, *p3), fill=clr, width=2)
        dwg.line((*p1, *p4), fill=clr, width=2)

        load.image = ImageTk.PhotoImage(img)
        canvas.create_image(*pos, anchor=anchor, image=load.image)


def draw_node(canvas: tk.Canvas, node: Node, to_screen):
    clr = Theme.CAD.nodes[1] if node.is_highlighted else Theme.CAD.nodes[0]
    pos = to_screen(node.position, 0)
    r, b = node.imgDims.values()

    img = Image.new("RGBA", (2 * (r + b), 2 * (r + b)))
    dwg = ImageDraw.Draw(img)

    pc = (r + b, r + b)
    dwg.circle(pc, radius=5, fill=clr, width=0)

    node.image = ImageTk.PhotoImage(img)
    canvas.create_image(*pos, anchor="c", image=node.image)


def check_hover_node(node: Node, x, y, to_screen):
    pos = to_screen(node.position, 0)
    d = math.sqrt((x - pos[0]) ** 2 + (y - pos[1]) ** 2)
    r1, = node.bbox.values()

    node.is_highlighted = False
    if d <= r1:
        node.is_highlighted = True
        return True
    return False


def check_hover_load(load: Load, x, y, to_screen) -> bool:
    if load.type == LoadType.M:
        pos = to_screen(load.positions[0], 0)
        d = math.sqrt((x - pos[0]) ** 2 + (y - pos[1]) ** 2)
        r1, r2, r3 = load.bbox[LoadType.M].values()

        load.is_highlighted = False
        if (d <= r1) or (r2 <= d <= r3):
            load.is_highlighted = True
            return True
    elif load.type == LoadType.PL:
        pos = to_screen(load.positions[0], 0)
        val = load.values[0]
        h = load.imgDims[LoadType.PL]["height"]
        bx, by = load.bbox[LoadType.PL].values()

        if val > 0:
            x1, y1 = pos[0] - bx, pos[1] - by
            x2, y2 = pos[0] + bx, pos[1] + h + by
        else:
            x1, y1 = pos[0] - bx, pos[1] - h - by
            x2, y2 = pos[0] + bx, pos[1] + by

        load.is_highlighted = False
        if x1 <= x <= x2 and y1 <= y <= y2:
            load.is_highlighted = True
            return True
    return False
