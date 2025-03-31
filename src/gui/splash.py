import customtkinter as ctk
from PIL import Image
import os

from config import FTR_NAME, assets_dir
from gui.style import *
from gui.CAD import CADInterface

__all__ = ["SplashScreen"]


class SplashScreen:
    def __init__(self, root: ctk.CTk):
        self.root = root
        configure_root(self.root, maximized=False, win_size=(800, 494), flat=True)

        # ===== Frame superior com imagem e nome lado a lado =====
        self.top_frame = ctk.CTkFrame(root, bg_color="red", fg_color="blue", corner_radius=30)
        self.top_frame.pack(expand=True)

        # ===== Logo =====
        logo = self.load_logo(os.path.join(assets_dir, "images/logo.png"))
        if logo:
            self.LblLogo = ctk.CTkLabel(self.top_frame, image=logo, text="", bg_color=Palette.background)
            self.LblLogo.grid(row=0, column=0, padx=(0, 0))

        # ===== Nome do programa =====
        self.LblName1 = ctk.CTkLabel(self.top_frame, text=FTR_NAME.split(" - ")[0], font=("Cambria", 64, "bold"),
                                     text_color=Palette.headline, bg_color=Palette.background)
        self.LblName1.grid(row=0, column=1, padx=(0, 0))

        self.LblName2 = ctk.CTkLabel(self.top_frame, text=FTR_NAME.split(" - ")[1], font=("Cambria", 32, "bold"),
                                     text_color=Palette.headline, bg_color=Palette.background)
        self.LblName2.grid(row=0, column=2, padx=(0, 0))

        # ===== Barra de progresso =====
        self.PrgLoad = ctk.CTkProgressBar(self.root, width=400)
        self.PrgLoad.pack(pady=(0, 30))
        self.PrgLoad.set(0)
        self.progress_val = 0

        self.load_progress()

    @staticmethod
    def load_logo(path):
        try:
            img = Image.open(path)
            return ctk.CTkImage(dark_image=img, light_image=img, size=(150, 150))
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            return None

    def load_progress(self):
        # flerken 1:
        # self.start_main_menu()
        if self.progress_val < 100:
            self.progress_val += 1
            self.PrgLoad.set(self.progress_val / 100)
            self.root.after(50, self.load_progress)
        else:
            self.start_main_menu()

    def start_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        CADInterface(self.root)
