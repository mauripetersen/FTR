import customtkinter as ctk
import tkinter as tk

from config import FTR_NAME_1, FTR_NAME_2, images_dir
from gui.style import Theme, configure_TopLevel
from manager.language import lang

__all__ = ["OpenProjectScreen"]


class OpenProjectScreen(ctk.CTkToplevel):
    def __init__(self, master: ctk.CTk):
        super().__init__(master=master)
        self.size = (500, 800)
        configure_TopLevel(self, maximized=False, win_size=self.size)

        self.LbxProjects = tk.Listbox(self, height=10, selectmode="single")
        self.LbxProjects.pack(padx=30, pady=30, fill="both", expand=True)
        
        self.after(100, self.focus)
