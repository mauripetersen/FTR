import customtkinter as ctk

from config import Theme
from project import Project, Node, Load, PLLoad, DLLoad

__all__ = ["SideBar"]


class SideBar(ctk.CTkFrame):
    def __init__(self, app, main_screen, project: Project):
        super().__init__(main_screen, fg_color=Theme.MainScreen.SideBar.background, corner_radius=0, width=300)
        self.pack_propagate(False)  # Prevents the Frame from adjusting to the content
        self.app = app
        self.main_screen = main_screen
        self.project = project

        self.editor_frame = ctk.CTkFrame(self, fg_color="transparent")
        self.editor_frame.pack(fill="both", expand=True)
        self.current_element = None

    def clear_editor(self):
        for widget in self.editor_frame.winfo_children():
            widget.destroy()

    def section_editor(self):
        if not self.project:
            return

    def element_editor(self, element: Node | Load):
        if isinstance(element, Node):
            ...
        elif isinstance(element, PLLoad):
            ...
        elif isinstance(element, DLLoad):
            ...
