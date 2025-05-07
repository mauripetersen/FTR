import customtkinter as ctk
from PIL import Image
import os

from config import Settings, Theme
from gui.tool_tip import CTkToolTip
from project import Project
from manager import Language

__all__ = ["Ribbon"]


class Ribbon(ctk.CTkFrame):
    def __init__(self, app, main_screen, project: Project):
        super().__init__(main_screen, fg_color=Theme.MainScreen.Ribbon.background, corner_radius=0, height=40)
        self.pack_propagate(False)  # Prevents the Frame from adjusting to the content
        self.app = app
        self.main_screen = main_screen

        # Section Properties:
        img_path = os.path.abspath(os.path.join(Settings.IMAGES_DIR, "section.png"))
        img_pil = Image.open(img_path)
        img = ctk.CTkImage(img_pil, size=(40, 40))
        self.BtnSection = ctk.CTkButton(
            self, text="", image=img, cursor="hand2",
            fg_color="transparent", hover_color=Theme.MainScreen.Ribbon.highlight,
            corner_radius=0, width=self.winfo_height(),
            command=self.main_screen.FrmSideBar.section_editor  # flerken
        )
        self.BtnSection.pack(side="left", fill="y")
        CTkToolTip(self.BtnSection, Language.get('MainScreen', 'Ribbon', 'section_properties'))

        # Add Node:
        img_path = os.path.abspath(os.path.join(Settings.IMAGES_DIR, "node.png"))
        img_pil = Image.open(img_path)
        img = ctk.CTkImage(img_pil, size=(40, 40))
        self.BtnNode = ctk.CTkButton(
            self, text="", image=img, cursor="hand2",
            fg_color="transparent", hover_color=Theme.MainScreen.Ribbon.highlight,
            corner_radius=0, width=self.winfo_height(),
            command=lambda: print(app.settings_window)  # flerken
        )
        self.BtnNode.pack(side="left", fill="y")
        CTkToolTip(self.BtnNode, Language.get('Ribbon', 'add_node'))

        # BtnAddLoad...
