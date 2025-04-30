import customtkinter as ctk

from gui.style import Theme
from manager.language import lang

__all__ = ["create_statusbar"]


def create_statusbar(app, main_screen, master_frame):
    master_frame.LblPos = ctk.CTkLabel(master_frame, text="Pos=(x, y)",
                                       text_color=Theme.StatusBar.text, font=("Segoe UI", 14))
    master_frame.LblPos.pack(side="left", padx=10)

    master_frame.VarGrid = ctk.BooleanVar(value=True)
    master_frame.ChkGrid = ctk.CTkCheckBox(master_frame, text=lang.get('grid'), text_color=Theme.StatusBar.text,
                                           font=("Segoe UI", 14),
                                           corner_radius=12, checkbox_width=24, checkbox_height=24, width=70,
                                           hover_color=Theme.StatusBar.highlight,
                                           fg_color=Theme.StatusBar.highlight,
                                           variable=master_frame.VarGrid, onvalue=True, offvalue=False)
    master_frame.ChkGrid.pack(side="right", padx=5)
