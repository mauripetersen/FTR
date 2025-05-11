import customtkinter as ctk
import tkinter as tk

from config import Theme
from project import Project, Node, Load, PLLoad, DLLoad
from gui.editor import Editor

__all__ = ["SideBar"]


class SideBar(ctk.CTkFrame):
    def __init__(self, app, main_screen):
        super().__init__(main_screen, fg_color=Theme.MainScreen.SideBar.background, corner_radius=0, width=300)
        self.pack_propagate(False)  # Prevents the Frame from adjusting to the content
        self.app = app
        self.main_screen = main_screen

        self.current_element: Node | Load | None = None
        self._modified = False
