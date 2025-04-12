import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageDraw, ImageTk
from typing import Any
import math

from gui.style import Theme
from project import Project, Section, Support, Node, Load, LoadType

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
        self.canvas.bind("<Button-1>", self.button_down_left)
        self.canvas.bind("<B1-Motion>", self.button_move_left)
        self.canvas.bind("<ButtonRelease-1>", self.button_up_left)
        self.canvas.bind("<MouseWheel>", self.perform_zoom)

        # self.adding_load = False
        # self.canvas.bind("<Button-3>", self.toggle_add_load)

        self.draw_canvas()

    def on_motion(self, event):
        self.master.master.FrmStatusBar.LblPos.configure(text=f"Pos={self.to_model(event.x, event.y, 2)}")

        near_node = self.get_nearest(event)
        if near_node:
            self.canvas.configure(cursor="hand2")
        else:
            self.canvas.configure(cursor="arrow")

        self.draw_canvas()

    def get_nearest(self, event) -> Any:
        for node in self.project.nodes:
            nx, ny = self.to_screen(node.position, 0)
            d = 15
            node.is_highlighted = False
            if point_in_rect(event.x, event.y, nx - d, ny - d, nx + d, ny + d):
                node.is_highlighted = True
                return node
        return None

    def button_down_left(self, event):
        self.start_selection(event)

    def button_move_left(self, event):
        self.update_selection(event)

    def button_up_left(self, event):
        self.end_selection(event)

    def perform_zoom(self, event):
        Mzx, Mzy = self.to_model(event.x, event.y)

        if event.delta > 0:
            s = 1.1
        else:
            s = 1 / 1.1
        self.view["scale"] *= s

        P0x, P0y = self.view["P"]
        P1x = Mzx - (Mzx - P0x) / s
        P1y = Mzy - (Mzy - P0y) / s

        self.view["P"] = (P1x, P1y)

        self.draw_canvas()

    def start_selection(self, event):
        self.start_x = event.x
        self.start_y = event.y

        # Creates the rectangle with equal initial coordinates
        self.select_rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y,
                                                        outline=Theme.CAD.select_rect)

    def update_selection(self, event):
        # Updates rectangle while dragging:
        self.canvas.coords(self.select_rect, self.start_x, self.start_y, event.x, event.y)

    def end_selection(self, event):
        # Aqui você pode fazer lógica de seleção de elementos
        # coords = self.canvas.coords(self.select_rect)
        # print("Selecionado:", coords)

        # Remove the selection rectangle (by ID)
        self.canvas.delete(self.select_rect)
        self.select_rect = None

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
        for k in range(len(nodes) - 1):
            x1, y1 = self.to_screen(nodes[k].position, 0)
            x2, y2 = self.to_screen(nodes[k + 1].position, 0)
            self.garbage.append(self.canvas.create_line(x1, y1, x2, y2, fill="white", width=5))

        for node in nodes:
            x, y = self.to_screen(node.position, 0)
            clr = "#ff0000" if node.is_highlighted else Theme.Illustration.highlight
            self.garbage.append(self.canvas.create_oval(x - 5, y - 5, x + 5, y + 5, fill=clr, width=0))

        loads = self.project.loads
        for load in loads:
            if load.type == LoadType.M:
                pos = self.to_screen(load.positions[0], 0)
                val = load.values[0]
                r = 80 * self.view["scale"]
                self.garbage.append(
                    self.canvas.create_arc(pos[0] - r, pos[1] - r, pos[0] + r, pos[1] + r, start=45, extent=270,
                                           style="arc", outline="#5566ff", width=3))

                if val > 0:
                    p1 = (r / 2, - r * math.sqrt(3) / 2)
                    p2 = (r / 2, - r * math.sqrt(3) / 2)
                    p3 = (r / 2, - r * math.sqrt(3) / 2)
                else:
                    ...

                self.garbage.append(self.canvas.create_line(0, 0, 0, 0, width=3))
            elif load.type == LoadType.PL:
                pos = self.to_screen(load.positions[0], 0)
                val = load.values[0]
                d = 100 * self.view["scale"]
                
                if val > 0:
                    p1 = (pos[0], -d)
                else:
                    p1 = (pos[0], d)

                self.garbage.append(self.canvas.create_line(*pos, *p1, fill="#5566ff", width=3))


def point_in_rect(x, y, x1, y1, x2, y2) -> bool:
    return x1 <= x <= x2 and y1 <= y <= y2


def draw_support(frame: ctk.CTkFrame, canvas: tk.Canvas, event: tk.Event):
    img_support = Image.new("RGBA", (150, 150))
    dwg = ImageDraw.Draw(img_support)

    support_type = "roller"
    match support_type:
        case "roller":
            dwg.line((75, 0, 120, 78), fill="white", width=3)
            dwg.line((75, 0, 30, 78), fill="white", width=3)
            dwg.line((30, 78, 120, 78), fill="white", width=3)

            dwg.line((0, 78, 150, 78), fill="white", width=3)
            dwg.line((0, 100, 150, 100), fill="white", width=3)
        case "pinned":
            dwg.line((75, 0, 120, 78), fill="white", width=3)
            dwg.line((75, 0, 30, 78), fill="white", width=3)
            dwg.line((30, 78, 120, 78), fill="white", width=3)

            dwg.line((0, 78, 150, 78), fill="white", width=3)

            dwg.line((0, 98, 30, 78), fill="white", width=3)
            dwg.line((30, 98, 60, 78), fill="white", width=3)
            dwg.line((60, 98, 90, 78), fill="white", width=3)
            dwg.line((90, 98, 120, 78), fill="white", width=3)
            dwg.line((120, 98, 150, 78), fill="white", width=3)
        case "fixed":
            dwg.line((0, 0, 150, 0), fill="white", width=3)

            dwg.line((0, 20, 30, 0), fill="white", width=3)
            dwg.line((30, 20, 60, 0), fill="white", width=3)
            dwg.line((60, 20, 90, 0), fill="white", width=3)
            dwg.line((90, 20, 120, 0), fill="white", width=3)
            dwg.line((120, 20, 150, 0), fill="white", width=3)

    frame.imgTk_support = ImageTk.PhotoImage(img_support)
    canvas.create_image(event.x, event.y, anchor="n", image=frame.imgTk_support)
