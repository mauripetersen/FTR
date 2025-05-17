import customtkinter as ctk
from config import Settings, Theme
from project import ProjectManager, Load, PLLoad, DLLoad
from manager import Language

__all__ = ["LoadEditor"]


class LoadEditor:
    def __init__(self, editor, ribbon, sidebar, cad):
        self.editor = editor
        self.ribbon = ribbon
        self.sidebar = sidebar
        self.cad = cad

        self.BtnOk: ctk.CTkButton | None = None

    def add_load(self):
        ...

    def edit_load(self, load: Load):
        self.editor.create_area(title=Language.get('MainScreen', 'Editor', 'Load', 'title'))

        FrmEditor: ctk.CTkFrame = self.editor.FrmEditor

        if isinstance(load, PLLoad):
            ...
        elif isinstance(load, DLLoad):
            ...
        else:
            ...

        FrmEditor.update_idletasks()
        self.BtnOk = ctk.CTkButton(
            FrmEditor, text="Ok", font=("Segoe UI", 18, "bold"), width=60, height=37, corner_radius=0,
            text_color=Theme.MainScreen.Editor.text, fg_color=Theme.MainScreen.Editor.highlight,
            hover_color=Theme.MainScreen.Editor.secondary[2],
            command=self.on_ok
        )
        self.BtnOk.place(x=FrmEditor.winfo_width() - 20,
                         y=FrmEditor.winfo_height() - 20,
                         anchor="se")

    def on_ok(self):
        ...
