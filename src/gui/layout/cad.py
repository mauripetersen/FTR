import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageTk, ImageFont
import math

from config import FTR_NAME_0, LoadType, SupportType
from project import Project, Section, Support, Node, Load
from gui.style import Theme
from font_manager import get_tk_font, get_pillow_font

__all__ = ["CADInterface"]


class CADInterface(ctk.CTkFrame):
    def __init__(self, app, master: ctk.CTkFrame, project: Project):
        super().__init__(master)
        self.app = app
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
        self.select_rect_start = None
        self.pan_start = None

        self.canvas.bind("<Motion>", self.on_motion)
        self.canvas.bind("<Button-1>", self.mouse_down_left)
        self.canvas.bind("<B1-Motion>", self.mouse_move_left)
        self.canvas.bind("<ButtonRelease-1>", self.mouse_up_left)
        self.canvas.bind("<Button-2>", self.mouse_down_middle)
        self.canvas.bind("<B2-Motion>", self.mouse_move_middle)
        self.canvas.bind("<ButtonRelease-2>", self.mouse_up_middle)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        self.update_all_images()

        self.after(200, self.draw_canvas)

    def on_motion(self, event):
        self.app.FrmStatusBar.LblPos.configure(text=f"{self.to_model(event.x, event.y, 2)}")

        nearest: Node | Load | None = self.get_nearest(event)

        for node in self.project.nodes:
            node.is_highlighted = False
        for load in self.project.loads:
            load.is_highlighted = False

        if nearest:
            nearest.is_highlighted = True
            self.canvas.configure(cursor="hand2")
        else:
            self.canvas.configure(cursor="arrow")

        self.draw_canvas()

    def get_nearest(self, event) -> Node | Load | None:
        for node in self.project.nodes:
            if check_hover_node(node, event.x, event.y, self.to_screen):
                return node
        for load in self.project.loads:
            if check_hover_load(load, event.x, event.y, self.to_screen):
                return load
        return None

    def mouse_down_left(self, event):
        self.select_rect_start = (event.x, event.y)

        # Creates the rectangle with equal initial coordinates
        self.select_rect = self.canvas.create_rectangle(*self.select_rect_start, *self.select_rect_start,
                                                        outline=Theme.CAD.select_rect)

    def mouse_move_left(self, event):
        # Updates rectangle while dragging:
        self.canvas.coords(self.select_rect, *self.select_rect_start, event.x, event.y)

    def mouse_up_left(self, event):
        # Aqui você pode fazer lógica de seleção de elementos
        # coords = self.canvas.coords(self.select_rect)
        # print("Selecionado:", coords)

        # Remove the selection rectangle (by ID)
        self.canvas.delete(self.select_rect)
        self.select_rect = None

    def mouse_down_middle(self, event):
        self.canvas.configure(cursor="fleur")
        self.pan_start = (event.x, event.y)

    def mouse_move_middle(self, event):
        if self.pan_start is None:
            return
        scale, ppm, P = self.view.values()

        dx = event.x - self.pan_start[0]
        dy = self.pan_start[1] - event.y

        self.view["P"] = (P[0] - dx / (scale * ppm), P[1] - dy / (scale * ppm))

        self.pan_start = (event.x, event.y)
        self.draw_canvas()

    def mouse_up_middle(self, event):
        self.canvas.configure(cursor="arrow")
        self.pan_start = None

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

    def update_all_images(self):
        for node in self.project.nodes:
            update_image_node(node)
            if node.support:
                update_image_support(node)
        for load in self.project.loads:
            update_image_load(load)

    def draw_canvas(self) -> bool:
        try:
            for g in self.garbage:
                self.canvas.delete(g)
            self.garbage.clear()

            nodes = self.project.nodes
            loads = self.project.loads

            # GRID:
            if self.app.FrmStatusBar.VarGrid.get():
                scale, ppm, P = self.view.values()
                width, height = self.canvas.winfo_width(), self.canvas.winfo_height()

                dx, dy = (1, 1)
                kx0 = math.ceil(P[0] / dx)
                kx1 = math.floor((P[0] + width / (scale * ppm)) / dx)
                ky0 = math.ceil((P[1] - height / (scale * ppm)) / dy)
                ky1 = math.floor(P[1] / dy)

                # Vertical lines:
                for k in range(kx0, kx1 + 1):
                    p1 = self.to_screen(k * dx, (ky0 - 1) * dy)
                    p2 = self.to_screen(k * dx, (ky1 + 1) * dy)
                    self.garbage.append(self.canvas.create_line(*p1, *p2, fill=Theme.CAD.grid[1], width=1))

                # Horizontal lines:
                for k in range(ky0, ky1 + 1):
                    p1 = self.to_screen((kx0 - 1) * dx, k * dy)
                    p2 = self.to_screen((kx1 + 1) * dx, k * dy)
                    self.garbage.append(self.canvas.create_line(*p1, *p2, fill=Theme.CAD.grid[1], width=1))

                # Y-Axis
                p1 = self.to_screen(0, (ky0 - 1) * dy)
                p2 = self.to_screen(0, (ky1 + 1) * dy)
                self.garbage.append(self.canvas.create_line(*p1, *p2, fill=Theme.CAD.grid[0], width=2))

                # X-Axis
                p1 = self.to_screen((kx0 - 1) * dx, 0)
                p2 = self.to_screen((kx1 + 1) * dx, 0)
                self.garbage.append(self.canvas.create_line(*p1, *p2, fill=Theme.CAD.grid[0], width=2))

            for k in range(len(nodes) - 1):  # SPANS
                p1 = self.to_screen(nodes[k].position, 0)
                p2 = self.to_screen(nodes[k + 1].position, 0)
                self.garbage.append(self.canvas.create_line(*p1, *p2, fill=Theme.CAD.spans, width=4))
            for node in nodes:  # SUPPORTS
                if node.support:
                    draw_support(self.canvas, node, self.to_screen)
            for load in loads:  # LOADS
                draw_load(self.canvas, load, self.to_screen)
            for node in nodes:  # NODES
                draw_node(self.canvas, node, self.to_screen)

            return True
        except Exception as e:
            messagebox.showerror(FTR_NAME_0, f"ERRO ao desenhar o canvas: {e}")
            self.project.last_error = str(e)
            return False


def generate_image_support(node: Node, clr: str) -> Image:
    side, dy = node.support.imgDims.values()

    dx = side / 3
    wi = 5 * dx
    height = side * math.sqrt(3) / 2
    width = 1

    img = Image.new("RGBA", (int(wi), int(wi)))
    dwg = ImageDraw.Draw(img)

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
    return img


def generate_image_node(node: Node, clr: str) -> Image:
    r, b = node.imgDims.values()

    img = Image.new("RGBA", (2 * (r + b), 2 * (r + b)))
    dwg = ImageDraw.Draw(img)

    pc = (r + b, r + b)
    dwg.circle(pc, radius=r, fill=clr, width=0)

    return img


def generate_image_load(load: Load, clr: str) -> Image:
    # ImageDraw.ImageDraw.font = ImageFont.truetype(Font.SegoeUI_SB, 20)
    ImageDraw.ImageDraw.font = get_pillow_font("Segoe UI", 20)
    width = 2

    match load.type:
        case LoadType.M:
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
            dwg.arc((*p1, *p2), start=start, end=end, fill=clr, width=width)
            dwg.line((*pa1, *pa2), fill=clr, width=width)
            dwg.line((*pa1, *pa3), fill=clr, width=width)
            img = img.rotate(angle=angle, resample=Image.Resampling.BICUBIC)

            dwg = ImageDraw.Draw(img)
            dwg.text((r + b, 0), text=f"{val} kN.m", fill=clr, anchor="mt")

            return img
        case LoadType.PL:
            val = load.values[0]
            h, ax, ay, b = load.imgDims[LoadType.PL].values()

            img = Image.new("RGBA", (2 * b, h))
            dwg = ImageDraw.Draw(img)

            if val > 0:
                p1 = (b, 0)
                p2 = (b, h)
                p3 = (b - ax, ay)
                p4 = (b + ax, ay)
            else:
                p1 = (b, h)
                p2 = (b, 0)
                p3 = (b - ax, h - ay)
                p4 = (b + ax, h - ay)

            dwg.line((*p1, *p2), fill=clr, width=width)
            dwg.line((*p1, *p3), fill=clr, width=width)
            dwg.line((*p1, *p4), fill=clr, width=width)
            dwg.text((0, 0), text=f"{val} kN", direction=None, fill=clr)

            return img
        case LoadType.UDL:
            img = Image.new("RGBA", (10, 10))
            return img
        case LoadType.LVDL:
            img = Image.new("RGBA", (10, 10))
            return img
    return None


def update_image_support(node: Node):
    img = generate_image_support(node, Theme.CAD.supports)
    node.support.image = ImageTk.PhotoImage(img)


def update_image_node(node: Node):
    img0 = generate_image_node(node, Theme.CAD.nodes[0])
    img1 = generate_image_node(node, Theme.CAD.nodes[1])

    node.image = {"normal": ImageTk.PhotoImage(img0),
                  "highlighted": ImageTk.PhotoImage(img1)}


def update_image_load(load: Load):
    img0 = generate_image_load(load, Theme.CAD.loads[0])
    img1 = generate_image_load(load, Theme.CAD.loads[1])

    load.image = {"normal": ImageTk.PhotoImage(img0),
                  "highlighted": ImageTk.PhotoImage(img1)}


def draw_support(canvas: tk.Canvas, node: Node, to_screen):
    if node.support is None or node.support.image is None:
        return
    if node.support.canvas_id:
        canvas.delete(node.support.canvas_id)
    pos = to_screen(node.position, 0)
    node.support.canvas_id = canvas.create_image(*pos, anchor="n", image=node.support.image)


def draw_node(canvas: tk.Canvas, node: Node, to_screen):
    if node.image is None:
        return
    pos = to_screen(node.position, 0)
    img = node.image["highlighted"] if node.is_highlighted else node.image["normal"]
    if node.canvas_id:
        canvas.delete(node.canvas_id)
    node.canvas_id = canvas.create_image(*pos, anchor="c", image=img)


def draw_load(canvas: tk.Canvas, load: Load, to_screen):
    if load.image is None:
        return
    pos = to_screen(load.positions[0], 0)
    val = load.values[0]
    img = load.image["highlighted"] if load.is_highlighted else load.image["normal"]

    if load.type == LoadType.M:
        anchor = "c"
    elif load.type == LoadType.PL:
        if val > 0:
            anchor = "n"
        else:
            anchor = "s"
    else:
        anchor = "c"

    if load.canvas_id:
        canvas.delete(load.canvas_id)
    load.canvas_id = canvas.create_image(*pos, anchor=anchor, image=img)


def check_hover_node(node: Node, x, y, to_screen):
    pos = to_screen(node.position, 0)
    d = math.sqrt((x - pos[0]) ** 2 + (y - pos[1]) ** 2)
    r1, = node.bbox.values()

    if d <= r1:
        return True
    return False


def check_hover_load(load: Load, x, y, to_screen) -> bool:
    if load.type == LoadType.M:
        pos = to_screen(load.positions[0], 0)
        d = math.sqrt((x - pos[0]) ** 2 + (y - pos[1]) ** 2)
        r1, r2, r3 = load.bbox[LoadType.M].values()

        if (d <= r1) or (r2 <= d <= r3):
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

        if x1 <= x <= x2 and y1 <= y <= y2:
            return True
    elif load.type == LoadType.UDL:
        ...
    elif load.type == LoadType.LVDL:
        ...
    return False
