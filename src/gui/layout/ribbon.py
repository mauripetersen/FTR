import customtkinter as ctk
from PIL import Image
import os

from config import images_dir
from gui.style import Theme

__all__ = ["create_ribbon"]


def create_ribbon(app, main_screen, master_frame: ctk.CTkFrame):
    # lbl = ctk.CTkLabel(master, text="Ribbon", text_color=Theme.Ribbon.text)
    # lbl.pack(side="left", padx=10)
    
    img_path = os.path.abspath(os.path.join(images_dir, "section.png"))
    img_pil = Image.open(img_path)
    img = ctk.CTkImage(img_pil, size=(40, 40))
    BtnSection = ctk.CTkButton(master_frame, text="", image=img, cursor="hand2",
                               fg_color="transparent", hover_color=Theme.Ribbon.highlight,
                               corner_radius=0, width=master_frame.winfo_height())
    BtnSection.pack(side="left", fill="y")

    # BtnLoad...
