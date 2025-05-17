import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os

from config import Settings, Theme, SectionType
from project import ProjectManager
from manager import Language

__all__ = ["SectionEditor"]


class SectionEditor:
    def __init__(self, editor, ribbon, sidebar, cad):
        self.editor = editor
        self.ribbon = ribbon
        self.sidebar = sidebar
        self.cad = cad

        self.section_options = {
            "None": "None",
            SectionType.R: "Rectangle",
            SectionType.I: "I-shape",
            SectionType.T: "T-shape"
        }

        self.OptSection: ctk.CTkOptionMenu | None = None
        self.canvas: tk.Canvas | None = None
        self.canvas_img: ImageTk.PhotoImage | None = None
        self.BtnOk: ctk.CTkButton | None = None

        # Rectangle:
        self.EntDimB: ctk.CTkEntry | None = None
        self.EntDimH: ctk.CTkEntry | None = None

        # I-shape and T-shape:
        self.EntDimBF: ctk.CTkEntry | None = None
        self.EntDimD: ctk.CTkEntry | None = None
        self.EntDimTF: ctk.CTkEntry | None = None
        self.EntDimTW: ctk.CTkEntry | None = None
        self.EntDimR: ctk.CTkEntry | None = None

    def get_code(self, name: str):
        for k, v in self.section_options.items():
            if v == name:
                return k
        return None

    def get_name(self, code: str):
        return self.section_options.get(code)

    def section_properties(self):
        if not ProjectManager.current:
            return
        project = ProjectManager.current

        if project.section:
            self.update_sec_prop(project.section.type)
        else:
            self.update_sec_prop("None")

    def load_sec_prop(self, name):
        ...

    def update_sec_prop(self, name):
        code = self.get_code(name)

        self.editor.create_area(title=Language.get('MainScreen', 'Editor', 'Section', 'title'))

        FrmEditor: ctk.CTkFrame = self.editor.FrmEditor

        lbl_section = ctk.CTkLabel(
            FrmEditor, text=Language.get('MainScreen', 'Editor', 'Section', 'section_type'),
            font=("Segoe UI", 16),
            text_color=Theme.MainScreen.Editor.text
        )
        lbl_section.place(relx=0.5, y=20, anchor="n")

        self.OptSection = ctk.CTkOptionMenu(FrmEditor,
                                            values=[val for val in self.section_options.values()],
                                            width=130,
                                            # height=30,
                                            corner_radius=0,
                                            font=("Segoe UI", 16),
                                            text_color=Theme.MainScreen.Editor.text,
                                            fg_color=Theme.MainScreen.Editor.secondary[2],
                                            button_color=Theme.MainScreen.Editor.secondary[1],
                                            button_hover_color=Theme.MainScreen.Editor.secondary[0],
                                            dropdown_font=('Segoe UI', 16),
                                            hover=True,
                                            anchor='center',  # 'n', 'e', 's', 'w', 'center'
                                            state='normal',
                                            dynamic_resizing=True,
                                            command=self.update_sec_prop)
        self.OptSection.place(relx=0.5, y=50, anchor="n")
        self.OptSection.set(self.section_options.get(code))

        self.canvas = tk.Canvas(FrmEditor, background=Theme.MainScreen.SideBar.background,
                                width=200, height=280, highlightthickness=1)
        self.canvas.place(relx=0.5, y=100, anchor="n")

        if code == "None":
            self.canvas_img = None
        elif code == SectionType.R:
            ...
        elif code == SectionType.I:
            ...
        elif code == SectionType.T:
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

    def create_type_r(self):
        FrmEditor: ctk.CTkFrame = self.editor.FrmEditor

        img = Image.open(os.path.join(Settings.IMAGES_DIR, "editor", "rectangle.png")).convert("RGBA")
        self.canvas_img = ImageTk.PhotoImage(img.resize((200, 280)))
        self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_img)

        lbl_dimB = ctk.CTkLabel(FrmEditor, text="b:", font=("Segoe UI", 14),
                                text_color=Theme.MainScreen.Editor.text)
        lbl_dimB.place(x=20, y=420, anchor="w")

        self.EntDimB = ctk.CTkEntry(FrmEditor, corner_radius=0, font=("Segoe UI", 14),
                                    text_color=Theme.MainScreen.Editor.text)
        self.EntDimB.place(x=40, y=420, anchor="w")

        lbl_dimH = ctk.CTkLabel(FrmEditor, text="h:", font=("Segoe UI", 14),
                                text_color=Theme.MainScreen.Editor.text)
        lbl_dimH.place(x=20, y=450, anchor="w")

        self.EntDimH = ctk.CTkEntry(FrmEditor, corner_radius=0, font=("Segoe UI", 14),
                                    text_color=Theme.MainScreen.Editor.text)
        self.EntDimH.place(x=40, y=450, anchor="w")

    def create_type_i(self):
        FrmEditor: ctk.CTkFrame = self.editor.FrmEditor

        img = Image.open(os.path.join(Settings.IMAGES_DIR, "editor", "i_shape.png")).convert("RGBA")
        self.canvas_img = ImageTk.PhotoImage(img.resize((200, 280)))
        self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_img)

        lbl_dimBF = ctk.CTkLabel(FrmEditor, text="bf:", font=("Segoe UI", 14),
                                 text_color=Theme.MainScreen.Editor.text)
        lbl_dimBF.place(x=20, y=420, anchor="w")

        self.EntDimBF = ctk.CTkEntry(FrmEditor, corner_radius=0, font=("Segoe UI", 14),
                                     text_color=Theme.MainScreen.Editor.text)
        self.EntDimBF.place(x=40, y=420, anchor="w")

        lbl_dimD = ctk.CTkLabel(FrmEditor, text="d:", font=("Segoe UI", 14),
                                text_color=Theme.MainScreen.Editor.text)
        lbl_dimD.place(x=20, y=450, anchor="w")

        self.EntDimD = ctk.CTkEntry(FrmEditor, corner_radius=0, font=("Segoe UI", 14),
                                    text_color=Theme.MainScreen.Editor.text)
        self.EntDimD.place(x=40, y=450, anchor="w")

        lbl_dimH = ctk.CTkLabel(FrmEditor, text="h:", font=("Segoe UI", 14),
                                text_color=Theme.MainScreen.Editor.text)
        lbl_dimH.place(x=20, y=480, anchor="w")

        self.EntDimH = ctk.CTkEntry(FrmEditor, corner_radius=0, font=("Segoe UI", 14),
                                    text_color=Theme.MainScreen.Editor.text)
        self.EntDimH.place(x=40, y=480, anchor="w")

    def create_type_t(self):
        FrmEditor: ctk.CTkFrame = self.editor.FrmEditor

        img = Image.open(os.path.join(Settings.IMAGES_DIR, "editor", "rectangle.png")).convert("RGBA")
        self.canvas_img = ImageTk.PhotoImage(img.resize((200, 280)))
        self.canvas.create_image(0, 0, anchor="nw", image=self.canvas_img)

    def on_ok(self):
        chosen_sec = self.OptSection.get()
        match chosen_sec:
            case "None":
                ...
            case SectionType.R:
                ...
