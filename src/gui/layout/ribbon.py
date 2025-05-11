import customtkinter as ctk

from config import Settings, Theme
from gui.editor import Editor
from gui.tool_tip import CTkToolTip
from project import Project, ProjectHolder
from manager import Language

__all__ = ["Ribbon"]


class Ribbon(ctk.CTkFrame):
    def __init__(self, app, main_screen, editor: Editor):
        super().__init__(main_screen, fg_color=Theme.MainScreen.Ribbon.background, corner_radius=0, height=40)
        self.pack_propagate(False)  # Prevents the Frame from adjusting to the content
        self.app = app
        self.main_screen = main_screen
        self.editor = editor

        # Section Properties:
        self.BtnSectionProperties = ctk.CTkButton(
            self, text="", image=Settings.BTN_SECTION_PROPERTIES_IMG, cursor="hand2",
            fg_color="transparent", hover_color=Theme.MainScreen.Ribbon.highlight,
            corner_radius=0, width=self.winfo_height(),
            command=self.on_section_properties  # flerken
        )
        self.BtnSectionProperties.pack(side="left", fill="y")
        CTkToolTip(self.BtnSectionProperties, Language.get('MainScreen', 'Ribbon', 'section_properties'))

        # Add Node:
        self.BtnAddNode = ctk.CTkButton(
            self, text="", image=Settings.BTN_NODE_IMG, cursor="hand2",
            fg_color="transparent", hover_color=Theme.MainScreen.Ribbon.highlight,
            corner_radius=0, width=self.winfo_height(),
            command=self.on_add_node  # flerken
        )
        self.BtnAddNode.pack(side="left", fill="y")
        CTkToolTip(self.BtnAddNode, Language.get('MainScreen', 'Ribbon', 'add_node'))

        # Add Load:
        self.BtnAddLoad = ctk.CTkButton(
            self, text="LOAD", image=None, cursor="hand2",
            fg_color="transparent", hover_color=Theme.MainScreen.Ribbon.highlight,
            corner_radius=0, width=self.winfo_height(),
            command=self.on_add_load  # flerken
        )
        self.BtnAddLoad.pack(side="left", fill="y")
        CTkToolTip(self.BtnAddLoad, Language.get('MainScreen', 'Ribbon', 'add_load'))

    def on_section_properties(self):
        if ProjectHolder.current and self.main_screen.FrmSideBar:
            self.editor.section_properties(ProjectHolder.current.section)

    def on_add_node(self):
        if ProjectHolder.current and self.main_screen.FrmSideBar:
            self.editor.add_node()

    def on_add_load(self):
        if ProjectHolder.current and self.main_screen.FrmSideBar:
            self.editor.add_load()
