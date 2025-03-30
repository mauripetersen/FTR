import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

from gui.style import *
from gui.menu import MainMenu

__all__ = ["SplashScreen"]


class SplashScreen:
    def __init__(self, root: tk.Tk):
        self.root = root
        configure_app(self.root, 500, 300)
        self.root.overrideredirect(True)

        # ===== Frame superior com imagem e nome lado a lado =====
        self.top_frame = tk.Frame(root, bg=Palette.background)
        self.top_frame.pack(expand=True)

        # ===== Logo =====
        self.logo_img = self.load_logo("c:/GitHub/mauripetersen/FTR/assets/images/logo.png")
        if self.logo_img:
            self.logo_label = tk.Label(self.top_frame, image=self.logo_img, bg=Palette.background)
            self.logo_label.grid(row=0, column=0, padx=(20, 10))

        # ===== Nome do programa =====
        self.label = tk.Label(self.top_frame, text="FTR", font=("Segoe UI", 24, "bold"), bg=Palette.background, fg="white")
        self.label.grid(row=0, column=1, padx=(10, 20))

        # ===== Barra de progresso =====
        self.progress = ttk.Progressbar(root, orient="horizontal", length=400, mode="determinate")
        self.progress.pack(pady=(0, 30))
        self.progress["maximum"] = 100
        self.progress_val = 0

        self.load_progress()

    @staticmethod
    def load_logo(path):
        try:
            img = Image.open(path)
            img = img.resize((150, 150), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(img)
        except Exception as e:
            print(f"Erro ao carregar imagem: {e}")
            return None

    def load_progress(self):
        if self.progress_val < 100:
            self.progress_val += 5
            self.progress["value"] = self.progress_val
            self.root.after(80, self.load_progress)
        else:
            self.start_main_menu()

    def start_main_menu(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        MainMenu(self.root)
