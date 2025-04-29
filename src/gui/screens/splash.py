import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os

from config import FTR_NAME_1, FTR_NAME_2, images_dir
from gui.style import Theme, configure_TopLevel
from manager.language import lang

__all__ = ["SplashScreen"]


class SplashScreen(ctk.CTkToplevel):
    def __init__(self, master: ctk.CTk):
        super().__init__(master=master)
        self.size = (800, 500)
        configure_TopLevel(self, maximized=False, win_size=self.size, flat=True)

        self.canvas = tk.Canvas(self, bg=Theme.background, highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        try:
            logo_path = os.path.abspath(os.path.join(images_dir, "logo_splash_gray.png"))
            logo_img = Image.open(logo_path).convert("RGBA")
            img = logo_img.resize(size=(350, 350))
            logo_imgTk = ImageTk.PhotoImage(img)
            self.canvas.create_image(240, self.size[1] / 2 - 30, image=logo_imgTk)
            self.logo_img = logo_imgTk
        except Exception as e:
            print(f"{lang.get('error', 'load_image')}: {e}")

        self.canvas.create_text(420, 190, text=FTR_NAME_1, font=("Cambria", 62, "bold"), anchor="w",
                                fill=Theme.headline)
        self.canvas.create_text(420, 255, text=FTR_NAME_2, font=("Cambria", 24, "bold"), anchor="w",
                                fill=Theme.paragraph)
        self.canvas.create_text(self.size[0] - 15, self.size[1] - 25, text="created by: Maurício Petersen Pithon",
                                font=("Cambria", 12, "italic"), fill=Theme.tertiary, anchor="e")

        self.PrgLoad = ctk.CTkProgressBar(self, width=self.size[0], height=10,
                                          progress_color=Theme.highlight, corner_radius=0)
        self.PrgLoad.place(relx=0.5, y=self.size[1] - 55, anchor="center")
        self.PrgLoad.set(0)
        self.progress_val = 0

        self.protocol("WM_DELETE_WINDOW", self.master.destroy)

        self.load_progress()

    def load_progress(self):
        if self.progress_val < 100:
            self.progress_val += 0.5
            self.PrgLoad.set(self.progress_val / 100)
            # flerken 1:
            # self.after(10, self.load_progress)
            self.after(1, self.load_progress)
        else:
            self.master.start_app()
