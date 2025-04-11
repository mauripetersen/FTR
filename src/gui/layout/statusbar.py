import customtkinter as ctk

from gui.style import Theme

__all__ = ["create_statusbar"]


def create_statusbar(app, master):
    master.LblPos = ctk.CTkLabel(master, text="Pos=(x, y)", text_color=Theme.headline,
                                 font=("Segoe UI", 14))
    master.LblPos.pack(side="left", padx=10)

    # lbl = ctk.CTkLabel(master, text="Status: Pronto", text_color=Theme.headline)
    # lbl.pack(side="right", padx=10)
