import customtkinter as ctk
from tkinter import messagebox

from config import Settings, Theme
from project import ProjectManager, Load, PLLoad, DLLoad
from manager import Language

__all__ = ["MaterialEditor"]


class MaterialEditor:
    def __init__(self, app, main_screen):
        from gui.editor import Editor
        self.editor = Editor

        self.app = app
        self.main_screen = main_screen
        self.ribbon = main_screen.FrmRibbon
        self.sidebar = main_screen.FrmSideBar
        self.cad = main_screen.cad_interface

        self.VarElasticModulus: ctk.StringVar | None = None
        self.EntElasticModulus: ctk.CTkEntry | None = None
        self.VarFCK: ctk.StringVar | None = None
        self.EntFCK: ctk.CTkEntry | None = None

    def edit_material(self):
        self.editor.create_area(Language.get('Editor', 'Material', 'title'), self.on_ok)
        self.editor.lock_ok_button()

        FrmEditor = self.editor.FrmEditor
        project = ProjectManager.current

        LblElasticModulus = ctk.CTkLabel(
            FrmEditor, text="E:", font=("Segoe UI", 14),
            text_color=Theme.Editor.text
        )
        LblElasticModulus.place(x=20, y=30, anchor="w")

        self.VarElasticModulus = ctk.StringVar()
        self.VarElasticModulus.set(str(project.elastic_modulus))
        self.VarElasticModulus.trace_add("write", self.on_change)

        self.EntElasticModulus = ctk.CTkEntry(
            FrmEditor, font=("Segoe UI", 14), border_width=0, corner_radius=0, width=80,
            text_color=Theme.Editor.text, textvariable=self.VarElasticModulus
        )
        self.EntElasticModulus.place(x=50, y=30, anchor="w")
        self.EntElasticModulus.bind("<Return>", self.on_ok)

        LblElasticModulus_unit = ctk.CTkLabel(
            FrmEditor, text="MPa", font=("Segoe UI", 14),
            text_color=Theme.Editor.text
        )
        LblElasticModulus_unit.place(x=140, y=30, anchor="w")

        LblFCK = ctk.CTkLabel(
            FrmEditor, text="fck:", font=("Segoe UI", 14),
            text_color=Theme.Editor.text
        )
        LblFCK.place(x=20, y=60, anchor="w")

        self.VarFCK = ctk.StringVar()
        self.VarFCK.set(str(project.fck))
        self.VarFCK.trace_add("write", self.on_change)

        self.EntFCK = ctk.CTkEntry(
            FrmEditor, font=("Segoe UI", 14), border_width=0, corner_radius=0, width=80,
            text_color=Theme.Editor.text, textvariable=self.VarFCK
        )
        self.EntFCK.place(x=50, y=60, anchor="w")
        self.EntFCK.bind("<Return>", self.on_ok)

        LblFCK_unit = ctk.CTkLabel(
            FrmEditor, text="MPa", font=("Segoe UI", 14),
            text_color=Theme.Editor.text
        )
        LblFCK_unit.place(x=140, y=60, anchor="w")

    def on_change(self, *args):
        has_changed = False

        em = self.VarElasticModulus.get()
        try:
            em_float = float(em)
            if ProjectManager.current.elastic_modulus != em_float:
                has_changed = True
        except ValueError:
            self.EntElasticModulus.configure(fg_color=Theme.Editor.error, font=("Segoe UI", 14, "bold"))
        else:
            self.EntElasticModulus.configure(fg_color=Theme.Editor.secondary[0], font=("Segoe UI", 14))

        fck = self.VarFCK.get()
        try:
            fck_float = float(fck)
            if ProjectManager.current.fck != fck_float:
                has_changed = True
        except ValueError:
            self.EntFCK.configure(fg_color=Theme.Editor.error, font=("Segoe UI", 14, "bold"))
        else:
            self.EntFCK.configure(fg_color=Theme.Editor.secondary[0], font=("Segoe UI", 14))

        if has_changed:
            self.editor.unlock_ok_button()
        else:
            self.editor.lock_ok_button()

    def on_ok(self, event=None):
        em = self.VarElasticModulus.get()
        try:
            em_float = float(em)
        except ValueError:
            messagebox.showerror("Value Error", "Elastic Modulus must be a valid number.")
        else:
            ProjectManager.current.elastic_modulus = em_float
            ProjectManager.current.modified = True
            ProjectManager.save_history()

            self.main_screen.update_title()
            self.cad.update_all_images()
            self.cad.draw_canvas()

        fck = self.VarFCK.get()
        try:
            fck_float = float(fck)
        except ValueError:
            messagebox.showerror("Value Error", "fck must be a valid number.")
        else:
            ProjectManager.current.fck = fck_float
            ProjectManager.current.modified = True
            ProjectManager.save_history()

            self.main_screen.update_title()
            self.cad.update_all_images()
            self.cad.draw_canvas()
