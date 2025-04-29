import customtkinter as ctk

from gui.style import Theme
from manager.language import lang

__all__ = ["create_statusbar"]


def create_statusbar(app, master):
    master.LblPos = ctk.CTkLabel(master, text="Pos=(x, y)", text_color=Theme.StatusBar.text, font=("Segoe UI", 14))
    master.LblPos.pack(side="left", padx=10)

    master.VarGrid = ctk.BooleanVar(value=True)
    master.ChkGrid = ctk.CTkCheckBox(master, text=lang.get('grid'), text_color=Theme.StatusBar.text, font=("Segoe UI", 14),
                                     corner_radius=12, checkbox_width=24, checkbox_height=24, width=70,
                                     hover_color=Theme.StatusBar.highlight,
                                     fg_color=Theme.StatusBar.highlight,
                                     variable=master.VarGrid, onvalue=True, offvalue=False)
    master.ChkGrid.pack(side="right", padx=5)
