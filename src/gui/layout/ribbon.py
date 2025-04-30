import customtkinter as ctk

from gui.style import Theme

__all__ = ["create_ribbon"]


def create_ribbon(app, main_screen, master_frame):
    # lbl = ctk.CTkLabel(master, text="Ribbon", text_color=Theme.Ribbon.text)
    # lbl.pack(side="left", padx=10)

    BtnAddLoad = ctk.CTkButton(master_frame, text="test",
                               fg_color="transparent", hover_color=Theme.Ribbon.highlight,
                               font=("Segoe UI", 14),
                               text_color=Theme.Ribbon.text, corner_radius=0, width=80)
    BtnAddLoad.pack(side="left", fill="y")
