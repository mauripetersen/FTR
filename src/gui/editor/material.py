import customtkinter as ctk
from tkinter import messagebox
from typing import Any

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

        self.entries: list[dict[str, Any]] = [
            {
                "name": "Elastic Modulus",
                "variable": None,
                "entry": None,
                "label": "E:",
                "unit": "MPa",
                "get": lambda: getattr(ProjectManager.current, "elastic_modulus"),
                "set": lambda v: setattr(ProjectManager.current, "elastic_modulus", v)
            },
            {
                "name": "FCK",
                "variable": None,
                "entry": None,
                "label": "fck:",
                "unit": "MPa",
                "get": lambda: getattr(ProjectManager.current, "fck"),
                "set": lambda v: setattr(ProjectManager.current, "fck", v)
            }
        ]

    def edit_material(self):
        self.editor.create_area(Language.get('Editor', 'Material', 'title'), self.on_ok)
        self.editor.lock_ok_button()

        FrmEditor = self.editor.FrmEditor

        for ix, item in enumerate(self.entries):
            y = 30 + ix * 30
            
            ctk.CTkLabel(
                FrmEditor, text=item.get("label"), font=("Segoe UI", 14),
                text_color=Theme.Editor.text
            ).place(x=20, y=y, anchor="w")

            item["variable"] = ctk.StringVar()
            item["variable"].set(str(item["get"]()))
            item["variable"].trace_add("write", self.on_change)

            item["entry"] = ctk.CTkEntry(
                FrmEditor, font=("Segoe UI", 14), border_width=0, corner_radius=0, width=80,
                text_color=Theme.Editor.text, textvariable=item["variable"]
            )
            item["entry"].place(x=50, y=y, anchor="w")
            item["entry"].bind("<Return>", self.on_ok)

            if item.get("unit"):
                ctk.CTkLabel(
                    FrmEditor, text=item.get("unit"), font=("Segoe UI", 14),
                    text_color=Theme.Editor.text
                ).place(x=140, y=y, anchor="w")

    def on_change(self, *args):
        has_changed = False

        for item in self.entries:
            val = item["variable"].get()
            try:
                val_float = float(val)
                if item["get"]() != val_float:
                    has_changed = True
            except ValueError:
                item["entry"].configure(fg_color=Theme.Editor.error, font=("Segoe UI", 14, "bold"))
            else:
                item["entry"].configure(fg_color=Theme.Editor.secondary[0], font=("Segoe UI", 14))

        if has_changed:
            self.editor.unlock_ok_button()
        else:
            self.editor.lock_ok_button()

    def on_ok(self, event=None):
        for item in self.entries:
            val = item["variable"].get()
            try:
                val_float = float(val)
            except ValueError:
                messagebox.showerror("Value Error", "Invalid type.")
            else:
                item["set"](val_float)
                # ProjectManager.current.modified = True
                ProjectManager.save_history()

                self.main_screen.update_title()
                self.cad.update_all_images()
                self.cad.draw_canvas()
        self.editor.close()
        self.editor.material.edit_material()
