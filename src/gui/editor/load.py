import customtkinter as ctk
from typing import Any

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

        self.current_load: Load | None = None

        self.parameters: list[dict[str, Any]] = [
            {
                "name": "Position",
                "variable": None,
                "entry": None,
                "label": "Position:",
                "unit": "m",
                "get": lambda: getattr(self.current_load, "position"),
                "set": lambda v: setattr(self.current_load, "position", v)
            }
        ]

        self.BtnFlerken: ctk.CTkButton | None = None

    def add_load(self):
        ...

    def edit_load(self, load: Load):
        self.current_load = load

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
