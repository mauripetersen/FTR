import customtkinter as ctk

from gui.style import Theme

__all__ = ["create_ribbon"]


def create_ribbon(app, master):
    lbl = ctk.CTkLabel(master, text="Ribbon", text_color=Theme.paragraph)
    lbl.pack(side="left", padx=10)
