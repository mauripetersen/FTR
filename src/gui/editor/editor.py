import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox

from config import Theme
from project import ProjectManager, Section, Node, Load, PLLoad, DLLoad

from .material import MaterialEditor
from .section import SectionEditor
from .node import NodeEditor
from .load import LoadEditor

__all__ = ["Editor"]


class Editor:
    app = None
    main_screen = None

    ribbon = None
    sidebar = None
    cad = None

    material: MaterialEditor | None = None
    section: SectionEditor | None = None
    node: NodeEditor | None = None
    load: LoadEditor | None = None

    FrmTitle: ctk.CTkFrame | None = None
    FrmEditor: ctk.CTkFrame | None = None
    BtnOk: ctk.CTkButton | None = None

    active: bool = False

    @classmethod
    def start(cls, app, main_screen):
        """
        Starts the Editor -
        References the needed dependencies (App, MainScreen, FrmRibbon, FrmSidebar and CADInterface).
        Initiate the sub-editors (MaterialEditor, SectionEditor, NodeEditor and LoadEditor).
        """
        cls.app = app
        cls.main_screen = main_screen

        cls.ribbon = main_screen.FrmRibbon
        cls.sidebar = main_screen.FrmSideBar
        cls.cad = main_screen.cad_interface

        cls.material = MaterialEditor(app, main_screen)
        cls.section = SectionEditor(app, main_screen)
        cls.node = NodeEditor(app, main_screen)
        cls.load = LoadEditor(app, main_screen)

        cls.active = True

    @classmethod
    def close(cls):
        """Just visually closes the Editor."""
        cls.clear_area()  # for now just clear the area...

    @classmethod
    def stop(cls):
        """Stops the Editor - Clear the area and empties all dependencies."""
        cls.clear_area()

        cls.app = None
        cls.main_screen = None

        cls.ribbon = None
        cls.sidebar = None
        cls.cad = None

        cls.material = None
        cls.section = None
        cls.node = None
        cls.load = None

        cls.active = False

    @classmethod
    def create_area(cls, title: str | None = None, ok_command: callable = None):
        cls.clear_area()

        if title:
            cls.FrmTitle = ctk.CTkFrame(cls.sidebar, fg_color="transparent", height=42)
            cls.FrmTitle.pack(side="top", fill="x")

            lbl_title = ctk.CTkLabel(
                cls.FrmTitle, text=title,
                font=("Segoe UI Semibold", 18),
                text_color=Theme.Editor.text
            )
            lbl_title.place(relx=0.5, y=20, anchor="c")

            sep = tk.Canvas(cls.FrmTitle, bg=Theme.tertiary, highlightthickness=0, height=2)
            sep.place(x=0, y=40, relwidth=1)

        cls.FrmEditor = ctk.CTkFrame(cls.sidebar, fg_color="transparent")
        cls.FrmEditor.pack(fill="both", expand=True)

        cls.FrmEditor.update_idletasks()
        cls.BtnOk = ctk.CTkButton(
            cls.FrmEditor, text="Ok", font=("Segoe UI", 18, "bold"), width=60, height=37, corner_radius=0,
            text_color=Theme.Editor.text, fg_color=Theme.Editor.highlight,
            hover_color=Theme.Editor.secondary[1],
            command=ok_command
        )
        cls.BtnOk.place(x=cls.FrmEditor.winfo_width() - 20,
                        y=cls.FrmEditor.winfo_height() - 20,
                        anchor="se")

    @classmethod
    def clear_area(cls):
        if cls.FrmTitle:
            for w in cls.FrmTitle.winfo_children():
                w.destroy()
            cls.FrmTitle.pack_forget()
            cls.FrmTitle.destroy()
            cls.FrmTitle = None

        if cls.FrmEditor:
            for w in cls.FrmEditor.winfo_children():
                w.unbind("<Return>")
                w.destroy()
            cls.FrmEditor.pack_forget()
            cls.FrmEditor.destroy()
            cls.FrmEditor = None

    @classmethod
    def lock_ok_button(cls):
        cls.BtnOk.configure(state='disabled', fg_color=Theme.Editor.secondary[1])

    @classmethod
    def unlock_ok_button(cls):
        cls.BtnOk.configure(state='normal', fg_color=Theme.Editor.highlight)
