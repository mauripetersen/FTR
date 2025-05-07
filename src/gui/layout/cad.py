import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk
import math
import copy

from config import Settings, Theme
from project import Project, Support, Node, Load, PLLoad, DLLoad
from gui.render import update_image
from manager import Language

__all__ = ["CADInterface"]


class CADInterface(ctk.CTkFrame):
    def __init__(self, app, main_screen, master_frame, project: Project):
        super().__init__(master_frame)
        self.app = app
        self.main_screen = main_screen

        self.project = project
        self.historical: list[Project] = [copy.deepcopy(self.project)]
        self.historical_ix: int = 0

        self.canvas = tk.Canvas(self, bg=Theme.MainScreen.CAD.background, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.view = View(scale_fac=1.1, ppm_0=100, P=(-5.0, 5.0))

        self.image_cache: dict[Support | Node | Load, list[ImageTk.PhotoImage]] = {}
        self.canvas_id: dict[Support | Node | Load, int | None] = {}
        self.image_garbage: list[int] = []

        self.select_rect = None
        self.select_rect_start = None
        self.pan_start = None

        self.main_screen.bind("<Control-a>", self.on_ctrl_a)
        self.main_screen.bind("<Control-y>", self.on_ctrl_y)
        self.main_screen.bind("<Control-z>", self.on_ctrl_z)

        self.main_screen.bind("<Delete>", self.on_delete)
        self.main_screen.bind("<Escape>", self.on_escape)

        self.canvas.bind("<Motion>", self.on_mouse_motion)
        self.canvas.bind("<Button-1>", self.on_mouse_down_left)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move_left)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up_left)
        self.canvas.bind("<Button-2>", self.on_mouse_down_middle)
        self.canvas.bind("<B2-Motion>", self.on_mouse_move_middle)
        self.canvas.bind("<ButtonRelease-2>", self.on_mouse_up_middle)
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)

        self.update_all_images()

        self.after(200, self.draw_canvas)

    def on_escape(self, event):
        self.deselect_all()

    def on_ctrl_a(self, event):
        self.select_all()

    def on_ctrl_y(self, event):
        self.redo()

    def on_ctrl_z(self, event):
        self.undo()

    def on_delete(self, event):
        self.delete_selected()

    def on_mouse_motion(self, event):
        self.main_screen.FrmStatusBar.LblPos.configure(text=f"{self.to_model(event.x, event.y, 2)}")

        for node in self.project.nodes:
            if not node.is_selected:
                node.is_highlighted = False
        for load in self.project.loads:
            if not load.is_selected:
                load.is_highlighted = False

        nearest = self.get_nearest(event)
        if nearest:
            nearest.is_highlighted = True
            self.canvas.configure(cursor="hand2")
        else:
            self.canvas.configure(cursor="arrow")

        self.draw_canvas()

    def on_mouse_down_left(self, event):
        flag_shift = event.state & 0x0001
        flag_ctrl = event.state & 0x0004

        if not flag_shift and not flag_ctrl:
            self.deselect_all(flag_draw_canvas=False)
        nearest = self.get_nearest(event)
        if nearest:
            if flag_shift:
                nearest.deselect()
            else:
                nearest.select()
        else:
            self.select_rect_start = (event.x, event.y)

            # Creates the rectangle with equal initial coordinates:
            self.select_rect = self.canvas.create_rectangle(*self.select_rect_start, *self.select_rect_start,
                                                            outline=Theme.MainScreen.CAD.select_rect, width=1)
        self.draw_canvas()

    def on_mouse_move_left(self, event):
        # Updates rectangle while dragging:
        if self.select_rect:
            self.canvas.coords(self.select_rect, *self.select_rect_start, event.x, event.y)
            self.canvas.tag_raise(self.select_rect)  # puts the select_rect in above

    def on_mouse_up_left(self, event):
        if self.select_rect:
            x1, y1, x2, y2 = self.canvas.coords(self.select_rect)

            for node in self.project.nodes:
                px, py = self.to_screen(node.position, 0)
                if x1 <= px <= x2 and y1 <= py <= y2:
                    node.select()
            for load in self.project.loads:
                if isinstance(load, PLLoad):
                    px, py = self.to_screen(load.position, 0)
                    if x1 <= px <= x2 and y1 <= py <= y2:
                        load.select()
                elif isinstance(load, DLLoad):
                    ...

            self.canvas.delete(self.select_rect)  # Remove the selection rectangle (by ID)
            self.select_rect = None
        self.draw_canvas()

    def on_mouse_down_middle(self, event):
        self.canvas.configure(cursor="fleur")
        self.pan_start = (event.x, event.y)

    def on_mouse_move_middle(self, event):
        if self.pan_start is None:
            return
        dx, dy = event.x - self.pan_start[0], self.pan_start[1] - event.y
        self.pan_start = (event.x, event.y)

        self.view.translate(dx, dy)
        self.draw_canvas()

    def on_mouse_up_middle(self, event):
        self.canvas.configure(cursor="arrow")
        self.pan_start = None

    def on_mouse_wheel(self, event):
        Mz = self.to_model(event.x, event.y)
        self.view.zoom(Mz, event.delta)
        self.draw_canvas()

    def to_screen(self, x_model: float, y_model: float) -> tuple[int, int]:
        """
        Converts coordinates from model to canvas.
        """
        ppm, P = self.view.ppm, self.view.P
        x_screen = int((x_model - P[0]) * ppm)
        y_screen = int((P[1] - y_model) * ppm)
        return x_screen, y_screen

    def to_model(self, x_screen: int, y_screen: int, ndigits: int = 0) -> tuple[float, float]:
        """
        Converts coordinates from canvas to model.
        """
        ppm, P = self.view.ppm, self.view.P
        x_model = P[0] + x_screen / ppm
        y_model = P[1] - y_screen / ppm
        if ndigits > 0:
            x_model = round(x_model, ndigits)
            y_model = round(y_model, ndigits)
        return x_model, y_model

    def get_nearest(self, event) -> Node | Load | None:
        for node in self.project.nodes:
            if node.check_hover(event, self.to_screen):
                return node
        for load in self.project.loads:
            if load.check_hover(event, self.to_screen):
                return load
        return None

    def get_selected(self) -> list[Node | Load]:
        return [*[node for node in self.project.nodes if node.is_selected],
                *[load for load in self.project.loads if load.is_selected]]

    def select_all(self, flag_draw_canvas=True):
        for node in self.project.nodes:
            node.select()
        for load in self.project.loads:
            load.select()
        if flag_draw_canvas:
            self.draw_canvas()

    def deselect_all(self, flag_draw_canvas=True):
        for node in self.project.nodes:
            node.deselect()
        for load in self.project.loads:
            load.deselect()
        if flag_draw_canvas:
            self.draw_canvas()

    def delete_element(self, element: Node | Load):
        if isinstance(element, Node):
            if element.support:
                if self.canvas_id.get(element.support):
                    self.canvas.delete(self.canvas_id[element.support])
                    self.canvas_id.pop(element.support)
                if self.image_cache.get(element.support):
                    self.image_cache.pop(element.support)

            if self.canvas_id.get(element):
                self.canvas.delete(self.canvas_id[element])
                self.canvas_id.pop(element)
            if self.image_cache.get(element):
                self.image_cache.pop(element)

            self.project.nodes.remove(element)
        elif isinstance(element, Load):
            if self.canvas_id.get(element):
                self.canvas.delete(self.canvas_id[element])
                self.canvas_id.pop(element)
            if self.image_cache.get(element):
                self.image_cache.pop(element)

            self.project.loads.remove(element)
        self.project.modified = True
        self.main_screen.update_title()  # flerken (verificar se farei assim mesmo)

    def delete_selected(self):
        selected_list = self.get_selected()
        if selected_list:
            for selected in selected_list:
                self.delete_element(selected)
            self.check_integrity()
            self.draw_canvas()
            self.save_history()

    def undo(self):
        if self.historical_ix > 0:
            self.historical_ix -= 1
            self.project = copy.deepcopy(self.historical[self.historical_ix])

            self.canvas.delete("all")
            self.deselect_all()
            self.update_all_images()
            self.draw_canvas()

    def redo(self):
        if self.historical_ix < len(self.historical) - 1:
            self.historical_ix += 1
            self.project = copy.deepcopy(self.historical[self.historical_ix])

            self.canvas.delete("all")
            self.deselect_all()
            self.update_all_images()
            self.draw_canvas()

    def save_history(self):
        self.historical = self.historical[:self.historical_ix + 1]  # remove future states
        self.historical.append(copy.deepcopy(self.project))
        self.historical_ix += 1

    def update_all_images(self):
        for node in self.project.nodes:
            self.image_cache[node] = update_image(node)
            if node.support:
                self.image_cache[node.support] = update_image(node.support)
        for load in self.project.loads:
            self.image_cache[load] = update_image(load)

    def draw_element(self, element: Support | Node | Load):
        if isinstance(element, Support):
            if self.image_cache.get(element) is None:
                return
            if self.canvas_id.get(element):
                self.canvas.delete(self.canvas_id[element])
            pos = self.to_screen(element.parent_node.position, 0)
            img = self.image_cache[element][0]
            self.canvas_id[element] = self.canvas.create_image(*pos, anchor="n", image=img)
        elif isinstance(element, Node):
            if self.image_cache.get(element) is None:
                return
            pos = self.to_screen(element.position, 0)
            img = self.image_cache[element][1] if element.is_highlighted else self.image_cache[element][0]
            if self.canvas_id.get(element):
                self.canvas.delete(self.canvas_id[element])
            self.canvas_id[element] = self.canvas.create_image(*pos, anchor="c", image=img)
        elif isinstance(element, PLLoad):
            if self.image_cache.get(element) is None:
                return
            pos = self.to_screen(element.position, 0)
            img = self.image_cache[element][1] if element.is_highlighted else self.image_cache[element][0]
            if self.canvas_id.get(element):
                self.canvas.delete(self.canvas_id[element])
            self.canvas_id[element] = self.canvas.create_image(*pos, anchor="c", image=img)
        elif isinstance(element, DLLoad):
            ...

    def draw_canvas(self) -> bool:
        if not self.project:
            self.destroy()
        try:
            nodes = self.project.nodes
            loads = self.project.loads

            for g in self.image_garbage:
                self.canvas.delete(g)
            self.image_garbage.clear()

            # GRID:
            if self.main_screen.FrmStatusBar.VarGrid.get():
                scale, ppm, P = self.view.scale, self.view.ppm, self.view.P
                width, height = self.canvas.winfo_width(), self.canvas.winfo_height()

                dx = dy = max([1, 5 ** math.floor(math.log(1 / scale, 5))])
                kx0 = math.ceil(P[0] / dx)
                kx1 = math.floor((P[0] + width / ppm) / dx)
                ky0 = math.ceil((P[1] - height / ppm) / dy)
                ky1 = math.floor(P[1] / dy)

                # Vertical lines:
                for k in range(kx0, kx1 + 1):
                    p1 = self.to_screen(k * dx, (ky0 - 1) * dy)
                    p2 = self.to_screen(k * dx, (ky1 + 1) * dy)
                    clr = Theme.MainScreen.CAD.grid[1]
                    self.image_garbage.append(self.canvas.create_line(*p1, *p2, fill=clr, width=1))

                # Horizontal lines:
                for k in range(ky0, ky1 + 1):
                    p1 = self.to_screen((kx0 - 1) * dx, k * dy)
                    p2 = self.to_screen((kx1 + 1) * dx, k * dy)
                    clr = Theme.MainScreen.CAD.grid[1]
                    self.image_garbage.append(self.canvas.create_line(*p1, *p2, fill=clr, width=1))

                # Y-Axis
                p1 = self.to_screen(0, (ky0 - 1) * dy)
                p2 = self.to_screen(0, (ky1 + 1) * dy)
                clr = Theme.MainScreen.CAD.grid[0]
                self.image_garbage.append(self.canvas.create_line(*p1, *p2, fill=clr, width=2))

                # X-Axis
                p1 = self.to_screen((kx0 - 1) * dx, 0)
                p2 = self.to_screen((kx1 + 1) * dx, 0)
                clr = Theme.MainScreen.CAD.grid[0]
                self.image_garbage.append(self.canvas.create_line(*p1, *p2, fill=clr, width=2))

            for k in range(len(nodes) - 1):  # SPANS
                p1 = self.to_screen(nodes[k].position, 0)
                p2 = self.to_screen(nodes[k + 1].position, 0)
                clr = Theme.MainScreen.CAD.spans
                self.image_garbage.append(self.canvas.create_line(*p1, *p2, fill=clr, width=4))
            for node in nodes:  # SUPPORTS
                if node.support:
                    self.draw_element(node.support)
            for load in loads:  # LOADS
                self.draw_element(load)
            for node in nodes:  # NODES
                self.draw_element(node)
            return True
        except Exception as e:
            messagebox.showerror(Settings.FTR_NAME[0], f"{Language.get('Error', 'draw_canvas')}: {e}")
            self.project.last_error = str(e)
            return False

    def check_integrity(self):
        node_pos = [node.position for node in self.project.nodes]
        if node_pos:
            min_pos, max_pos = min(node_pos), max(node_pos)

            if min_pos != 0:
                for node in self.project.nodes:
                    node.position -= min_pos
                for load in self.project.loads:
                    if isinstance(load, PLLoad):
                        load.position -= min_pos
                    elif isinstance(load, DLLoad):
                        load.start -= min_pos
                        load.end -= min_pos
                node_pos = [node.position for node in self.project.nodes]
                min_pos, max_pos = min(node_pos), max(node_pos)

            for load in self.project.loads:
                if isinstance(load, PLLoad):
                    if load.position < min_pos or load.position > max_pos:
                        self.delete_element(load)
                elif isinstance(load, DLLoad):
                    if load.start < min_pos or load.end > max_pos:
                        self.delete_element(load)
            self.draw_canvas()
        else:
            for load in self.project.loads:
                self.delete_element(load)


class View:
    def __init__(
            self,
            scale_fac: float,
            ppm_0: int,
            P: tuple[float, float]
    ):
        """
        A view to reference the frame-view of the canvas.
        :param scale_fac: Scale factor (for perform zoom);
        :param ppm_0: Píxel-per-meter initial (when scale = 1.0);
        :param P: Up-Left point.
        """
        self.scale_fac: float = scale_fac
        self.scale_ix: int = 0
        self.ppm_0: int = ppm_0
        self.P: tuple[float, float] = P

    @property
    def scale(self) -> float:
        """Scale of the view."""
        return self.scale_fac ** self.scale_ix

    @property
    def ppm(self) -> float:
        """Píxel-per-meter."""
        return self.ppm_0 * self.scale

    def zoom(self, Mz: tuple[float, float], delta: int):
        """Performs a zoom in this view. Mz is the central point of zoom and delta is the 'event.delta'."""
        if delta > 0:
            if self.scale_ix == 20:
                return
            s = self.scale_fac
            self.scale_ix += 1
        else:
            if self.scale_ix == -40:
                return
            s = 1 / self.scale_fac
            self.scale_ix -= 1
        self.P = (Mz[0] - (Mz[0] - self.P[0]) / s,
                  Mz[1] - (Mz[1] - self.P[1]) / s)

    def translate(self, dx: float, dy: float):
        """Translates this view. This method apply a displacement dx and dy in the P value."""
        self.P = (self.P[0] - dx / self.ppm,
                  self.P[1] - dy / self.ppm)
