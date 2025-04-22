import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageDraw, ImageTk
import math

from config import FTR_NAME_0, LoadType, SupportType
from project import Project, Section, Support, Node, Load, PLLoad, DLLoad
from gui.style import Theme

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
            if node.check_hover(event, self.to_screen):
                return node
        for load in self.project.loads:
            if load.check_hover(event, self.to_screen):
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
            node.update_image()
            if node.support:
                node.support.update_image()
        for load in self.project.loads:
            load.update_image()

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
                    node.support.draw(self.canvas, self.to_screen)
            for load in loads:  # LOADS
                load.draw(self.canvas, self.to_screen)
            for node in nodes:  # NODES
                node.draw(self.canvas, self.to_screen)
            return True
        except Exception as e:
            messagebox.showerror(FTR_NAME_0, f"ERRO ao desenhar o canvas: {e}")
            self.project.last_error = str(e)
            return False
