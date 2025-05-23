import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import ImageTk
import math

from config import Settings, Theme
from project import ProjectManager, Support, Node, Load, PLLoad, DLLoad
from gui.render import update_image
from gui.editor import Editor
from manager import Language

__all__ = ["CADInterface"]


class CADInterface(ctk.CTkFrame):
    def __init__(self, app, main_screen, master_frame):
        super().__init__(master_frame)
        self.app = app
        self.main_screen = main_screen

        self.canvas = tk.Canvas(self, bg=Theme.MainScreen.CAD.background, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        self.view = View(scale_fac=1.1, ppm_0=100, P=(-5.0, 5.0))

        self.selected: list[Node | Load] = []
        self.highlighted: Node | Load | None = None

        self.image_cache: dict[Support | Node | Load, list[ImageTk.PhotoImage]] = {}
        self.canvas_id: dict[Support | Node | Load, int | None] = {}
        self.image_garbage: list[int] = []

        self._select_rect = None
        self._select_rect_start = None
        self._pan_start = None

        self._holding_ctrl = False
        self._holding_shift = False

        self.main_screen.bind("<KeyPress>", self.on_key_press)
        self.main_screen.bind("<KeyRelease>", self.on_key_release)

        self.main_screen.bind("<Control-a>", self.on_ctrl_a)
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
        self.after(150, self.draw_canvas)

    # region "Binds"

    def on_key_press(self, event: tk.Event):
        if event.keysym in ("Control_L", "Control_R"):
            self._holding_ctrl = True
        elif event.keysym in ("Shift_L", "Shift_R"):
            self._holding_shift = True

    def on_key_release(self, event):
        if event.keysym in ("Control_L", "Control_R"):
            self._holding_ctrl = False
        elif event.keysym in ("Shift_L", "Shift_R"):
            self._holding_shift = False

    def on_ctrl_a(self, event):
        self.select_all()

    def on_delete(self, event):
        self.delete_selected()

    def on_escape(self, event):
        self.deselect_all()

    def on_mouse_motion(self, event):
        self.main_screen.FrmStatusBar.LblPos.configure(text=f"Pos={self.to_model(event.x, event.y, 2)}")

        nearest = self.get_nearest(event)
        if nearest:
            self.highlighted = nearest
            self.canvas.configure(cursor="hand2")
        else:
            self.highlighted = None
            self.canvas.configure(cursor="arrow")

        self.draw_canvas()

    def on_mouse_down_left(self, event):
        Editor.close()
        nearest = self.get_nearest(event)
        if nearest:
            if self._holding_ctrl:
                if nearest not in self.selected:
                    self.selected.append(nearest)
            elif self._holding_shift:
                if nearest in self.selected:
                    self.selected.remove(nearest)
            else:
                self.deselect_all(flag_draw_canvas=False)
                self.selected.append(nearest)

                if isinstance(nearest, Node):
                    Editor.node.edit_node(nearest)
                elif isinstance(nearest, Load):
                    Editor.load.edit_load(nearest)
        else:
            self._select_rect_start = (event.x, event.y)

            # Creates the rectangle with equal initial coordinates:
            self._select_rect = self.canvas.create_rectangle(*self._select_rect_start, *self._select_rect_start,
                                                             outline=Theme.MainScreen.CAD.select_rect, width=2)
        self.draw_canvas()

    def on_mouse_move_left(self, event):
        # Updates rectangle while dragging:
        if self._select_rect:
            self.canvas.coords(self._select_rect, *self._select_rect_start, event.x, event.y)
            self.canvas.tag_raise(self._select_rect)  # puts the select_rect in above

    def on_mouse_up_left(self, event):
        project = ProjectManager.current

        if self._select_rect:
            x1, y1, x2, y2 = self.canvas.coords(self._select_rect)

            elements: list[Node | Load] = []
            for node in project.nodes:
                px, py = self.to_screen(node.position, 0)
                if x1 <= px <= x2 and y1 <= py <= y2:
                    elements.append(node)
            for load in project.loads:
                if isinstance(load, PLLoad):
                    px, py = self.to_screen(load.position, 0)
                    if x1 <= px <= x2 and y1 <= py <= y2:
                        elements.append(load)
                elif isinstance(load, DLLoad):
                    ...

            if not self._holding_ctrl and not self._holding_shift:
                self.deselect_all(flag_draw_canvas=False)

            for element in elements:
                if self._holding_shift:
                    if element in self.selected:
                        self.selected.remove(element)
                else:
                    if element not in self.selected:
                        self.selected.append(element)

            self.canvas.delete(self._select_rect)  # Remove the selection rectangle (by ID)
            self._select_rect = None
        self.draw_canvas()

    def on_mouse_down_middle(self, event):
        self.canvas.configure(cursor="fleur")
        self._pan_start = event.x, event.y

    def on_mouse_move_middle(self, event):
        if self._pan_start is None:
            return
        dx, dy = event.x - self._pan_start[0], self._pan_start[1] - event.y
        self._pan_start = event.x, event.y

        self.view.translate(dx, dy)
        self.draw_canvas()

    def on_mouse_up_middle(self, event):
        self.canvas.configure(cursor="arrow")
        self._pan_start = None

    def on_mouse_wheel(self, event):
        Mz = self.to_model(event.x, event.y)
        self.view.zoom(Mz, event.delta)
        self.draw_canvas()

    # endregion

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
        project = ProjectManager.current

        for node in project.nodes:
            if node.check_hover(event, self.to_screen):
                return node
        for load in project.loads:
            if load.check_hover(event, self.to_screen):
                return load
        return None

    def select_all(self, flag_draw_canvas=True):
        project = ProjectManager.current
        Editor.close()
        self.selected = [*project.nodes, *project.loads]
        if flag_draw_canvas:
            self.draw_canvas()

    def deselect_all(self, flag_draw_canvas=True):
        Editor.close()
        self.selected.clear()
        if flag_draw_canvas:
            self.draw_canvas()

    def delete_element(self, element: Node | Load):
        project = ProjectManager.current

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

            project.nodes.remove(element)
        elif isinstance(element, Load):
            if self.canvas_id.get(element):
                self.canvas.delete(self.canvas_id[element])
                self.canvas_id.pop(element)
            if self.image_cache.get(element):
                self.image_cache.pop(element)

            project.loads.remove(element)
        # project.modified = True
        self.main_screen.update_title()  # flerken: verificar se farei assim mesmo

    def delete_selected(self):
        if self.selected:
            for element in self.selected:
                self.delete_element(element)
            ProjectManager.current.check_integrity()
            self.update_all_images()
            self.canvas.delete("all")
            self.draw_canvas()
            ProjectManager.save_history()

    def undo(self):
        if ProjectManager.undo():
            self.canvas.delete("all")
            self.deselect_all()
            self.update_all_images()
            self.draw_canvas()
            self.main_screen.update_title()

    def redo(self):
        if ProjectManager.redo():
            self.canvas.delete("all")
            self.deselect_all()
            self.update_all_images()
            self.draw_canvas()
            self.main_screen.update_title()

    def update_all_images(self):
        project = ProjectManager.current

        for node in project.nodes:
            self.image_cache[node] = update_image(node)
            if node.support:
                self.image_cache[node.support] = update_image(node.support)
        for load in project.loads:
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

            if element in self.selected or element == self.highlighted:
                img = self.image_cache[element][1]
            else:
                img = self.image_cache[element][0]

            if self.canvas_id.get(element):
                self.canvas.delete(self.canvas_id[element])
            self.canvas_id[element] = self.canvas.create_image(*pos, anchor="c", image=img)
        elif isinstance(element, PLLoad):
            if self.image_cache.get(element) is None:
                return
            pos = self.to_screen(element.position, 0)

            if element in self.selected or element == self.highlighted:
                img = self.image_cache[element][1]
            else:
                img = self.image_cache[element][0]

            if self.canvas_id.get(element):
                self.canvas.delete(self.canvas_id[element])
            self.canvas_id[element] = self.canvas.create_image(*pos, anchor="c", image=img)
        elif isinstance(element, DLLoad):
            ...

    def draw_canvas(self) -> bool:
        project = ProjectManager.current

        if not project:
            self.destroy()
        try:
            nodes = project.nodes
            loads = project.loads

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
            project.last_error = str(e)
            return False


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
