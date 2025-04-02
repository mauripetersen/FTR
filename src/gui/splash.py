import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os

from config import FTR_NAME_1, FTR_NAME_2, assets_dir
from gui.style import Theme, configure_root
from gui.interface import App

__all__ = ["SplashScreen"]


class SplashScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.size = (800, 500)
        configure_root(self, maximized=False, win_size=self.size, flat=True)

        self.Canvas = tk.Canvas(self, bg=Theme.background, highlightthickness=0)
        self.Canvas.pack(fill="both", expand=True)

        try:
            logo_path = os.path.abspath(os.path.join(assets_dir, "images/logo_splash_gray.png"))
            logo_img = Image.open(logo_path).convert("RGBA")
            img = logo_img.resize(size=(350, 350))
            logo_imgTk = ImageTk.PhotoImage(img)
            self.Canvas.create_image(240, self.size[1] / 2 - 30, image=logo_imgTk)
            self.logo_img = logo_imgTk
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")

        self.Canvas.create_text(420, 210 - 20, text=FTR_NAME_1, font=("Cambria", 62, "bold"), anchor="w",
                                fill=Theme.headline)
        self.Canvas.create_text(420, 280 - 25, text=FTR_NAME_2, font=("Cambria", 24, "bold"), anchor="w",
                                fill=Theme.paragraph)

        self.Canvas.create_text(self.size[0] - 15, self.size[1] - 25, text="created by: Maurício Petersen Pithon",
                                font=("Cambria", 12, "italic"), fill=Theme.Illustration.highlight, anchor="e")

        self.PrgLoad = ctk.CTkProgressBar(self, width=self.size[0], height=10,
                                          progress_color=Theme.Illustration.tertiary, corner_radius=0)
        self.PrgLoad.place(relx=0.5, y=self.size[1] - 55, anchor="center")
        self.PrgLoad.set(0)
        self.progress_val = 0

        self.progress_after_id = None
        self.load_progress()

    def load_progress(self):
        if self.progress_val < 100:
            self.progress_val += 1
            self.PrgLoad.set(self.progress_val / 100)
            # self.progress_after_id = self.after(20, self.load_progress)  # flerken 1
            self.progress_after_id = self.after(1, self.load_progress)
        else:
            self.start_main_menu()

    def start_main_menu(self):
        if self.progress_after_id:
            self.after_cancel(self.progress_after_id)
        self.destroy()
        app = App()
        app.run()
