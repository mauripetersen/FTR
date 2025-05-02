import customtkinter as ctk
from PIL import Image
import os

from config import Settings, Theme
from gui.tool_tip import CTkToolTip
from gui.layout.sidebar import section_editor  # flerken
from manager import Language

__all__ = ["create_ribbon"]


def create_ribbon(app, main_screen, master_frame: ctk.CTkFrame):
    # lbl = ctk.CTkLabel(master_frame, text="Ribbon", text_color=Theme.Ribbon.text)
    # lbl.pack(side="left", padx=10)
    
    img_path = os.path.abspath(os.path.join(Settings.IMAGES_DIR, "section.png"))
    img_pil = Image.open(img_path)
    img = ctk.CTkImage(img_pil, size=(40, 40))
    BtnSection = ctk.CTkButton(master_frame, text="", image=img, cursor="hand2",
                               fg_color="transparent", hover_color=Theme.Ribbon.highlight,
                               corner_radius=0, width=master_frame.winfo_height(),
                               command=None)
    BtnSection.pack(side="left", fill="y")
    CTkToolTip(BtnSection, Language.get('Ribbon', 'section_properties'))

    # BtnAddNode...

    # BtnAddLoad...
