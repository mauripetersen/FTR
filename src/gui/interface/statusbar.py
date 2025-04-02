import customtkinter as ctk

from gui.style import Theme

__all__ = ["create_statusbar"]


def create_statusbar(master, app):
    lbl = ctk.CTkLabel(master, text="Status: Pronto", text_color=Theme.paragraph)
    lbl.pack(side="left", padx=10)
