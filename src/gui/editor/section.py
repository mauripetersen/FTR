import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from typing import Any
import copy
import os

from config import Settings, Theme, SectionType
from project import ProjectManager, Section, SectionR, SectionI, SectionT
from manager import Language

__all__ = ["SectionEditor"]


class SectionEditor:
    def __init__(self, app, main_screen):
        from gui.editor import Editor
        self.editor = Editor

        self.app = app
        self.main_screen = main_screen
        self.ribbon = main_screen.FrmRibbon
        self.sidebar = main_screen.FrmSideBar
        self.cad = main_screen.cad_interface

        self.current_section: Section | None = None

        self.section_options = {
            "None": "None",
            SectionType.R: "Rectangle",
            SectionType.I: "I-shape",
            SectionType.T: "T-shape",
        }

        self.VarSection: ctk.Variable | None = None
        self.OptSection: ctk.CTkOptionMenu | None = None
        self.canvas: tk.Canvas | None = None
        self.canvas_img: ImageTk.PhotoImage | None = None

        # Rectangle:
        self.parameters_r: list[dict[str, Any]] = [
            {
                "name": "Base",
                "variable": None,
                "entry": None,
                "label": "b:",
                "unit": "cm",
                "get": lambda: self.current_section.dims.get("b"),
                "set": lambda v: self.current_section.dims.__setitem__("b", v)
            },
            {
                "name": "Height",
                "variable": None,
                "entry": None,
                "label": "h:",
                "unit": "cm",
                "get": lambda: self.current_section.dims.get("h"),
                "set": lambda v: self.current_section.dims.__setitem__("h", v)
            }
        ]

        self.VarDimB: ctk.StringVar | None = None
        self.EntDimB: ctk.CTkEntry | None = None
        self.VarDimH: ctk.StringVar | None = None
        self.EntDimH: ctk.CTkEntry | None = None
        
        # I-shape and T-shape:
        self.EntDimBF: ctk.CTkEntry | None = None
        self.EntDimD: ctk.CTkEntry | None = None
        self.EntDimTF: ctk.CTkEntry | None = None
        self.EntDimTW: ctk.CTkEntry | None = None
        self.EntDimR: ctk.CTkEntry | None = None

    @staticmethod
    def get_name(section: Section | None):
        if isinstance(section, SectionR):
            return "Rectangle"
        elif isinstance(section, SectionI):
            return "I-shape"
        elif isinstance(section, SectionT):
            return "T-shape"
        else:
            return "None"

    def edit_section(self):
        self.current_section = ProjectManager.current.section

        self.VarSection = ctk.Variable()
        self.VarSection.set(self.get_name(self.current_section))
        self.VarSection.trace_add("write", self.on_change_section)

        self.update_area()

    def update_area(self):
        self.editor.create_area(Language.get('Editor', 'Section', 'title'), self.on_ok)
        self.editor.lock_ok_button()
        FrmEditor = self.editor.FrmEditor

        ctk.CTkLabel(
            FrmEditor, text=Language.get('Editor', 'Section', 'section_type'),
            font=("Segoe UI", 16),
            text_color=Theme.Editor.text
        ).place(relx=0.5, y=20, anchor="n")

        self.OptSection = ctk.CTkOptionMenu(FrmEditor,
                                            values=[val for val in self.section_options.values()],
                                            width=130,
                                            # height=30,
                                            corner_radius=0,
                                            font=("Segoe UI", 16),
                                            text_color=Theme.Editor.text,
                                            fg_color=Theme.Editor.gray[2],
                                            button_color=Theme.Editor.gray[1],
                                            button_hover_color=Theme.Editor.gray[0],
                                            dropdown_font=('Segoe UI', 16),
                                            hover=True,
                                            anchor='center',  # 'n', 'e', 's', 'w', 'center'
                                            state='normal',
                                            dynamic_resizing=True,
                                            # command=self.on_change,
                                            variable=self.VarSection)
        self.OptSection.place(relx=0.5, y=50, anchor="n")

        self.canvas = tk.Canvas(FrmEditor, background=Theme.MainScreen.SideBar.background,
                                width=200, height=280, highlightthickness=1)
        self.canvas.place(relx=0.5, y=100, anchor="n")

        if isinstance(self.current_section, SectionR):
            img = Image.open(os.path.join(Settings.IMAGES_DIR, "editor", "rectangle.png")).convert("RGBA")
            self.canvas_img = ImageTk.PhotoImage(img.resize((200, 280)))
            self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_img)

            for ix, item in enumerate(self.parameters_r):
                y = 420 + ix * 30

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
        elif isinstance(self.current_section, SectionI):
            ...
        elif isinstance(self.current_section, SectionT):
            ...
        else:
            self.canvas_img = None

    def on_change_section(self, *args):
        sec = self.VarSection.get()

        if sec == "None":
            self.current_section = None
        elif sec == "Rectangle":
            self.current_section = SectionR(0.0, 0.0)
        elif sec == "I-shape":
            self.current_section = SectionI(0.0, 0.0, 0.0, 0.0)
        elif sec == "T-shape":
            self.current_section = SectionT(0.0, 0.0, 0.0, 0.0)

        self.update_area()

    def on_change(self, *args):
        has_changed = False
        
        if isinstance(self.current_section, SectionR):
            for item in self.parameters_r:
                val = item["variable"].get()
                try:
                    val_float = float(val)
                    if item["get"]() != val_float:
                        has_changed = True
                except ValueError:
                    item["entry"].configure(fg_color=Theme.Editor.error, font=("Segoe UI", 14, "bold"))
                else:
                    item["entry"].configure(fg_color=Theme.Editor.secondary[0], font=("Segoe UI", 14))
        elif isinstance(self.current_section, SectionI):
            ...
        elif isinstance(self.current_section, SectionT):
            ...
        else:
            ...

        if has_changed:
            self.editor.unlock_ok_button()
        else:
            self.editor.lock_ok_button()

    def on_ok(self, event=None):
        has_wrong = False

        if isinstance(self.current_section, SectionR):
            for item in self.parameters_r:
                val = item["variable"].get()
                try:
                    val_float = float(val)
                except ValueError:
                    has_wrong = True

            if has_wrong:
                messagebox.showerror("Value Error", "Section properties invalid.")
            else:
                for item in self.parameters_r:
                    item["set"](float(item["variable"].get()))
                ProjectManager.current.section = copy.deepcopy(self.current_section)
                # ProjectManager.current.modified = True
                ProjectManager.save_history()

                self.main_screen.update_title()
                # self.cad.update_all_images()
                # self.cad.draw_canvas()

        elif isinstance(self.current_section, SectionI):
            ...
        elif isinstance(self.current_section, SectionT):
            ...
        else:
            ...

        self.editor.close()
        self.editor.section.edit_section()
