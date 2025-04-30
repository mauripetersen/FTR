import customtkinter as ctk

from gui.style import Theme

__all__ = ["create_sidebar"]


def create_sidebar(app, main_screen, master_frame):
    lbl = ctk.CTkLabel(master_frame, text="Sidebar", text_color=Theme.SideBar.text)
    lbl.pack(padx=10, pady=10)
