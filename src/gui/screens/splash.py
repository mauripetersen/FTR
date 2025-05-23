import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import math
import os

from config import Settings, Theme
from gui.style import configure_TopLevel
from manager import Language

__all__ = ["SplashScreen"]


class SplashScreen(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(master=app)
        self.app = app

        self.size = (800, 500)
        configure_TopLevel(self, maximized=False, win_size=self.size, flat=True)

        self.canvas = tk.Canvas(self, bg=Theme.background, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        try:
            logo_path = os.path.abspath(os.path.join(Settings.IMAGES_DIR, "logo_splash_gray.png"))
            logo_img = Image.open(logo_path).convert("RGBA")
            img = logo_img.resize(size=(350, 350))
            logo_imgTk = ImageTk.PhotoImage(img)
            self.canvas.create_image(240, self.size[1] / 2 - 30, image=logo_imgTk)
            self.logo_img = logo_imgTk
        except Exception as e:
            print(f"{Language.get('Error', 'load_image')}: {e}")

        self.canvas.create_text(420, 190, text=Settings.FTR_NAME[1], font=("Cambria", 62, "bold"), anchor="w",
                                fill=Theme.headline)
        self.canvas.create_text(420, 255, text=Settings.FTR_NAME[2], font=("Cambria", 24, "bold"), anchor="w",
                                fill=Theme.paragraph)
        self.canvas.create_text(self.size[0] - 15, self.size[1] - 25, text="created by: Maurício Petersen Pithon",
                                font=("Cambria", 13, "italic"), fill=Theme.tertiary, anchor="e")
        self.load_id = None

        self.PrgLoad = ctk.CTkProgressBar(self, width=self.size[0], height=10,
                                          progress_color=Theme.highlight, corner_radius=0)
        self.PrgLoad.place(relx=0.5, y=self.size[1] - 55, anchor="center")
        self.PrgLoad.set(0)
        self.progress = 0

        self._pan_start = None
        self._holding = {
            "space": False,
            "Left": False,
            "Right": False
        }

        self.bind("<KeyPress>", self.on_key_press)
        self.bind("<KeyRelease>", self.on_key_release)
        self.bind("<Button-1>", self.on_mouse_down_left)
        self.bind("<B1-Motion>", self.on_mouse_move_left)

        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
        self.load_progress()

    def on_key_press(self, event):
        if event.keysym in ["space", "Left", "Right"]:
            self._holding[event.keysym] = True

    def on_key_release(self, event):
        if event.keysym in ["space", "Left", "Right"]:
            self._holding[event.keysym] = False

    def on_mouse_down_left(self, event):
        self._pan_start = event.x, event.y

    def on_mouse_move_left(self, event):
        if self._pan_start:
            dx, dy = self.winfo_pointerx() - self._pan_start[0], self.winfo_pointery() - self._pan_start[1]
            self.geometry(f"+{dx}+{dy}")

    def load_progress(self):
        self.canvas.delete(self.load_id)
        self.load_id = self.canvas.create_text(
            15, self.size[1] - 25, text="Loading" + "." * min([3, math.floor(self.progress / 25)]),
            font=("Cambria", 13, "italic"), fill=Theme.paragraph, anchor="w"
        )

        if self.progress <= 100:
            if self._holding["space"]:
                if self._holding["Left"]:
                    self.progress -= 0.5
                elif self._holding["Right"]:
                    self.progress += 0.5
                self.PrgLoad.set(self.progress / 100)
            else:
                self.progress += 0.5
                self.PrgLoad.set(self.progress / 100)
            self.after(1, self.load_progress)  # flerken: ajeitar o tempo depois
        else:
            self.app.start_app()
