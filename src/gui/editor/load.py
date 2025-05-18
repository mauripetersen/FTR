import customtkinter as ctk
from config import Settings, Theme
from project import ProjectManager, Load, PLLoad, DLLoad
from manager import Language

__all__ = ["LoadEditor"]


class LoadEditor:
    def __init__(self, app, main_screen):
        from gui.editor import Editor
        self.editor = Editor

        self.app = app
        self.main_screen = main_screen
        self.ribbon = main_screen.FrmRibbon
        self.sidebar = main_screen.FrmSideBar
        self.cad = main_screen.cad_interface

        self.BtnFlerken: ctk.CTkButton | None = None

    def add_load(self):
        ...

    def edit_load(self, load: Load):
        self.editor.create_area(Language.get('Editor', 'Load', 'title'), self.on_ok)
        self.editor.lock_ok_button()

        FrmEditor = self.editor.FrmEditor

        if isinstance(load, PLLoad):
            ...
        elif isinstance(load, DLLoad):
            ...
        else:
            ...

    def on_ok(self, event=None):
        ...
