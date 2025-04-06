import customtkinter as ctk

from gui.style import Theme

__all__ = ["create_statusbar"]


def create_statusbar(app, master):
    lbl = ctk.CTkLabel(master, text="Status: Pronto", text_color=Theme.headline)
    lbl.pack(side="left", padx=10)
