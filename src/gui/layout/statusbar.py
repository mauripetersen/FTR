import customtkinter as ctk

from gui.style import Theme

__all__ = ["create_statusbar"]


def create_statusbar(app, master):
    master.LblPos = ctk.CTkLabel(master, text="Pos=(x, y)", text_color=Theme.headline, font=("Segoe UI", 14))
    master.LblPos.pack(side="left", padx=10)

    master.VarGrid = ctk.BooleanVar(value=True)
    master.ChkGrid = ctk.CTkCheckBox(master, text="Grid", text_color=Theme.headline, font=("Segoe UI", 14),
                                     corner_radius=12, checkbox_width=24, checkbox_height=24, width=70,
                                     hover_color=Theme.Illustration.highlight,
                                     fg_color=Theme.Illustration.highlight,
                                     variable=master.VarGrid, onvalue=True, offvalue=False)
    master.ChkGrid.pack(side="right", padx=5)
