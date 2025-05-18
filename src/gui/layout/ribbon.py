import customtkinter as ctk

from config import Settings, Theme
from gui.tool_tip import CTkToolTip
from gui.editor import Editor
from manager import Language

__all__ = ["Ribbon"]


class Ribbon(ctk.CTkFrame):
    def __init__(self, app, main_screen):
        super().__init__(main_screen, fg_color=Theme.MainScreen.Ribbon.background, corner_radius=0, height=40)
        self.pack_propagate(False)  # Prevents the Frame from adjusting to the content
        self.app = app
        self.main_screen = main_screen
        
        # Material Parameters:
        self.BtnMaterialParameters = ctk.CTkButton(
            self, text="", image=Settings.BTN_MATERIAL_PARAMETERS_IMG, cursor="hand2",
            fg_color="transparent", hover_color=Theme.MainScreen.Ribbon.highlight,
            corner_radius=0, width=self.winfo_height(),
            command=lambda: Editor.material.edit_material() if Editor.active else None
        )
        self.BtnMaterialParameters.pack(side="left", fill="y")
        CTkToolTip(self.BtnMaterialParameters, Language.get('MainScreen', 'Ribbon', 'material_parameters'))

        # Section Properties:
        self.BtnSectionProperties = ctk.CTkButton(
            self, text="", image=Settings.BTN_SECTION_PROPERTIES_IMG, cursor="hand2",
            fg_color="transparent", hover_color=Theme.MainScreen.Ribbon.highlight,
            corner_radius=0, width=self.winfo_height(),
            command=lambda: Editor.section.edit_section() if Editor.active else None
        )
        self.BtnSectionProperties.pack(side="left", fill="y")
        CTkToolTip(self.BtnSectionProperties, Language.get('MainScreen', 'Ribbon', 'section_properties'))

        # Add Node:
        self.BtnAddNode = ctk.CTkButton(
            self, text="", image=Settings.BTN_NODE_IMG, cursor="hand2",
            fg_color="transparent", hover_color=Theme.MainScreen.Ribbon.highlight,
            corner_radius=0, width=self.winfo_height(),
            command=lambda: Editor.node.add_node() if Editor.active else None
        )
        self.BtnAddNode.pack(side="left", fill="y")
        CTkToolTip(self.BtnAddNode, Language.get('MainScreen', 'Ribbon', 'add_node'))

        # Add Load:
        self.BtnAddLoad = ctk.CTkButton(
            self, text="LOAD", image=None, cursor="hand2",
            fg_color="transparent", hover_color=Theme.MainScreen.Ribbon.highlight,
            corner_radius=0, width=self.winfo_height(),
            command=lambda: Editor.load.add_load() if Editor.active else None
        )
        self.BtnAddLoad.pack(side="left", fill="y")
        CTkToolTip(self.BtnAddLoad, Language.get('MainScreen', 'Ribbon', 'add_load'))
