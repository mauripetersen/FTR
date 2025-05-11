import customtkinter as ctk
import tkinter as tk
from typing import Literal

from config import Theme
from manager import Language

__all__ = ["StatusBar"]


class StatusBar(ctk.CTkFrame):
    def __init__(self, app, main_screen):
        super().__init__(main_screen, fg_color=Theme.MainScreen.StatusBar.background, corner_radius=0, height=30)
        self.pack_propagate(False)  # Prevents the Frame from adjusting to the content
        self.app = app
        self.main_screen = main_screen

        self.add_sep(side="left")
        self.LblPos = ctk.CTkLabel(
            self, text="Pos=(x, y)", font=("Segoe UI", 14), text_color=Theme.MainScreen.StatusBar.text,
            width=120, anchor="w"
        )
        self.LblPos.pack(side="left", padx=10)

        self.VarGrid = ctk.BooleanVar(value=True)
        self.ChkGrid = ctk.CTkCheckBox(
            self, text=Language.get('MainScreen', 'StatusBar', 'grid'),
            text_color=Theme.MainScreen.StatusBar.text, font=("Segoe UI", 14),
            corner_radius=12, checkbox_width=20, checkbox_height=20, width=80,
            hover_color=Theme.MainScreen.StatusBar.highlight,
            fg_color=Theme.MainScreen.StatusBar.highlight,
            variable=self.VarGrid, onvalue=True, offvalue=False,
            command=self.toggle_ChkGrid
        )
        self.ChkGrid.pack(side="right", padx=10)
        self.add_sep(side="right")

    def add_sep(self, side: Literal["left", "right", "top", "bottom"], width=2):
        sep = tk.Canvas(self, bg=Theme.secondary, highlightthickness=0, width=width)
        sep.pack(side=side, fill="y")

    def toggle_ChkGrid(self):
        if self.main_screen.cad_interface:
            self.main_screen.cad_interface.draw_canvas()
