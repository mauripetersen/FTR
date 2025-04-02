import customtkinter as ctk
from PIL import Image, ImageTk
import os

from config import FTR_NAME, assets_dir
from gui.style import *
from gui.interface import App

__all__ = ["SplashScreen"]


class SplashScreen(ctk.CTk):
    def __init__(self):
        super().__init__()
        configure_root(self, maximized=False, win_size=(800, 494), flat=True)

        # ===== Frame superior com imagem e nome lado a lado =====
        self.top_frame = ctk.CTkFrame(self, bg_color=Theme.background, fg_color=Theme.background, corner_radius=30)
        self.top_frame.pack(expand=True)

        # ===== Logo =====
        logo = self.load_logo(os.path.abspath(os.path.join(assets_dir, "images/logo.png")))
        if logo:
            self.LblLogo = ctk.CTkLabel(self.top_frame, image=logo, text="", fg_color="transparent", bg_color="red")
            self.LblLogo.grid(row=0, column=0, padx=(0, 0))

        # ===== Nome do programa =====
        self.LblName1 = ctk.CTkLabel(self.top_frame, text=FTR_NAME.split(" - ")[0], font=("Cambria", 64, "bold"),
                                     text_color=Theme.headline, bg_color=Theme.background)
        self.LblName1.grid(row=0, column=1, padx=(0, 0))

        self.LblName2 = ctk.CTkLabel(self.top_frame, text=FTR_NAME.split(" - ")[1], font=("Cambria", 32, "bold"),
                                     text_color=Theme.headline, bg_color=Theme.background)
        self.LblName2.grid(row=0, column=2, padx=(0, 0))

        # ===== Barra de progresso =====
        self.PrgLoad = ctk.CTkProgressBar(self, width=400)
        self.PrgLoad.pack(pady=(0, 30))
        self.PrgLoad.set(0)
        self.progress_val = 0

        self.progress_after_id = None
        self.load_progress()

    @staticmethod
    def load_logo(path):
        try:
            img_pil = Image.open(path)
            img_pil = img_pil.resize((300, 300), Image.LANCZOS)
            img_tk = ImageTk.PhotoImage(img_pil)
            return img_tk
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            return None

    def load_progress(self):
        if self.progress_val < 100:
            self.progress_val += 1
            self.PrgLoad.set(self.progress_val / 100)
            self.progress_after_id = self.after(1000, self.load_progress)
        else:
            self.start_main_menu()

    def start_main_menu(self):
        if self.progress_after_id:
            self.after_cancel(self.progress_after_id)
        self.destroy()
        app = App()
        app.run()
