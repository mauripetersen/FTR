import customtkinter as ctk

from gui.style import Theme

__all__ = ["create_sidebar"]


def create_sidebar(master, app):
    lbl = ctk.CTkLabel(master, text="Sidebar", text_color=Theme.paragraph)
    lbl.pack(padx=10, pady=10)
