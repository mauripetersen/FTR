import customtkinter as ctk

from config import Theme

__all__ = ["create_sidebar", "section_editor"]


def create_sidebar(app, main_screen, master_frame):
    lbl = ctk.CTkLabel(master_frame, text="Sidebar", text_color=Theme.SideBar.text)
    lbl.pack(padx=10, pady=10)


def section_editor(app, main_screen, master_frame):
    ...


def node_editor(app, main_screen, master_frame):
    ...
