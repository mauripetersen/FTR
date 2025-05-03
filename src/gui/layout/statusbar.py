import customtkinter as ctk

from config import Theme
from manager import Language

__all__ = ["StatusBar"]


class StatusBar(ctk.CTkFrame):
    def __init__(self, app, main_screen):
        super().__init__(main_screen, fg_color=Theme.StatusBar.background, corner_radius=0, height=30)
        self.pack_propagate(False)  # Prevents the Frame from adjusting to the content
        self.app = app
        self.main_screen = main_screen

        self.LblPos = ctk.CTkLabel(self, text="Pos=(x, y)", text_color=Theme.StatusBar.text, font=("Segoe UI", 14))
        self.LblPos.pack(side="left", padx=10)

        self.VarGrid = ctk.BooleanVar(value=True)
        self.ChkGrid = ctk.CTkCheckBox(
            self, text=Language.get('StatusBar', 'grid'),
            text_color=Theme.StatusBar.text, font=("Segoe UI", 14),
            corner_radius=12, checkbox_width=24, checkbox_height=24, width=70,
            hover_color=Theme.StatusBar.highlight,
            fg_color=Theme.StatusBar.highlight,
            variable=self.VarGrid, onvalue=True, offvalue=False
        )
        self.ChkGrid.pack(side="right", padx=5)
