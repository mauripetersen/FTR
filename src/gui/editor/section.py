import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
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

        LblSection = ctk.CTkLabel(
            FrmEditor, text=Language.get('Editor', 'Section', 'section_type'),
            font=("Segoe UI", 16),
            text_color=Theme.Editor.text
        )
        LblSection.place(relx=0.5, y=20, anchor="n")

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

            LblDimB = ctk.CTkLabel(FrmEditor, text="b:", font=("Segoe UI", 14),
                                   text_color=Theme.Editor.text)
            LblDimB.place(x=20, y=420, anchor="w")

            self.VarDimB = ctk.StringVar()
            self.VarDimB.set("0.0")
            self.VarDimB.trace_add("write", self.on_change)

            self.EntDimB = ctk.CTkEntry(
                FrmEditor, font=("Segoe UI", 14), border_width=0, corner_radius=0, width=80,
                text_color=Theme.Editor.text, textvariable=self.VarDimB
            )
            self.EntDimB.place(x=50, y=420, anchor="w")
            self.EntDimB.bind("<Return>", self.on_ok)

            LblDimB_unit = ctk.CTkLabel(
                FrmEditor, text="cm", font=("Segoe UI", 14),
                text_color=Theme.Editor.text
            )
            LblDimB_unit.place(x=140, y=420, anchor="w")

            LblDimH = ctk.CTkLabel(FrmEditor, text="h:", font=("Segoe UI", 14),
                                   text_color=Theme.Editor.text)
            LblDimH.place(x=20, y=450, anchor="w")

            self.EntDimH = ctk.CTkEntry(FrmEditor, corner_radius=0, font=("Segoe UI", 14), width=80,
                                        text_color=Theme.Editor.text)
            self.EntDimH.place(x=40, y=450, anchor="w")
        elif isinstance(self.current_section, SectionI):
            img = Image.open(os.path.join(Settings.IMAGES_DIR, "editor", "i_shape.png")).convert("RGBA")
            self.canvas_img = ImageTk.PhotoImage(img.resize((200, 280)))
            self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_img)

            LblDimBF = ctk.CTkLabel(FrmEditor, text="bf:", font=("Segoe UI", 14),
                                    text_color=Theme.Editor.text)
            LblDimBF.place(x=20, y=420, anchor="w")

            self.EntDimBF = ctk.CTkEntry(FrmEditor, corner_radius=0, font=("Segoe UI", 14), width=80,
                                         text_color=Theme.Editor.text)
            self.EntDimBF.place(x=40, y=420, anchor="w")

            LblDimD = ctk.CTkLabel(FrmEditor, text="d:", font=("Segoe UI", 14),
                                   text_color=Theme.Editor.text)
            LblDimD.place(x=20, y=450, anchor="w")

            self.EntDimD = ctk.CTkEntry(FrmEditor, corner_radius=0, font=("Segoe UI", 14), width=80,
                                        text_color=Theme.Editor.text)
            self.EntDimD.place(x=40, y=450, anchor="w")

            LblDimH = ctk.CTkLabel(FrmEditor, text="h:", font=("Segoe UI", 14),
                                   text_color=Theme.Editor.text)
            LblDimH.place(x=20, y=480, anchor="w")

            self.EntDimH = ctk.CTkEntry(FrmEditor, corner_radius=0, font=("Segoe UI", 14), width=80,
                                        text_color=Theme.Editor.text)
            self.EntDimH.place(x=40, y=480, anchor="w")
        elif isinstance(self.current_section, SectionT):
            img = Image.open(os.path.join(Settings.IMAGES_DIR, "editor", "rectangle.png")).convert("RGBA")
            self.canvas_img = ImageTk.PhotoImage(img.resize((200, 280)))
            self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_img)
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
            b = self.VarDimB.get()
            try:
                b_float = float(b)
                if ProjectManager.current.elastic_modulus != b_float:
                    has_changed = True
            except ValueError:
                self.EntDimB.configure(fg_color=Theme.Editor.error, font=("Segoe UI", 14, "bold"))
            else:
                self.EntDimB.configure(fg_color=Theme.Editor.secondary[0], font=("Segoe UI", 14))
        elif isinstance(self.current_section, SectionI):
            ...
        elif isinstance(self.current_section, SectionT):
            ...
        else:
            ...

    def on_ok(self, event=None):
        chosen_sec = self.OptSection.get()
        match chosen_sec:
            case "None":
                ...
            case SectionType.R:
                ...
