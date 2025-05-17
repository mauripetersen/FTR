import customtkinter as ctk
from config import Settings, Theme
from project import ProjectManager, Load, PLLoad, DLLoad
from manager import Language

__all__ = ["MaterialEditor"]


class MaterialEditor:
    def __init__(self, editor, ribbon, sidebar, cad):
        self.editor = editor
        self.ribbon = ribbon
        self.sidebar = sidebar
        self.cad = cad

        self.EntElasticModulus: ctk.CTkEntry | None = None
        self.EntFCK: ctk.CTkEntry | None = None

        self.BtnOk: ctk.CTkButton | None = None

    def open(self):
        self.editor.create_area(title=Language.get('MainScreen', 'Editor', 'Material', 'title'))

        project = ProjectManager.current
        FrmEditor: ctk.CTkFrame = self.editor.FrmEditor

        LblElasticModulus = ctk.CTkLabel(
            FrmEditor, text="E:", font=("Segoe UI", 14),
            text_color=Theme.MainScreen.Editor.text
        )
        LblElasticModulus.place(x=20, y=30, anchor="w")

        self.EntElasticModulus = ctk.CTkEntry(
            FrmEditor, font=("Segoe UI", 14), border_width=0, corner_radius=0, width=80,
            text_color=Theme.MainScreen.Editor.text
        )
        self.EntElasticModulus.place(x=50, y=30, anchor="w")
        self.EntElasticModulus.insert(0, project.elastic_modulus)

        LblElasticModulus_unit = ctk.CTkLabel(
            FrmEditor, text="MPa", font=("Segoe UI", 14),
            text_color=Theme.MainScreen.Editor.text
        )
        LblElasticModulus_unit.place(x=140, y=30, anchor="w")

        LblFCK = ctk.CTkLabel(
            FrmEditor, text="fck:", font=("Segoe UI", 14),
            text_color=Theme.MainScreen.Editor.text
        )
        LblFCK.place(x=20, y=60, anchor="w")

        self.EntFCK = ctk.CTkEntry(
            FrmEditor, font=("Segoe UI", 14), border_width=0, corner_radius=0, width=80,
            text_color=Theme.MainScreen.Editor.text
        )
        self.EntFCK.place(x=50, y=60, anchor="w")
        self.EntFCK.insert(0, project.fck)

        LblFCK_unit = ctk.CTkLabel(
            FrmEditor, text="MPa", font=("Segoe UI", 14),
            text_color=Theme.MainScreen.Editor.text
        )
        LblFCK_unit.place(x=140, y=60, anchor="w")

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
