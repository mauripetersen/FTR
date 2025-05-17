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
    ribbon = None
    sidebar = None
    cad = None

    material: MaterialEditor | None = None
    section: SectionEditor | None = None
    node: NodeEditor | None = None
    load: LoadEditor | None = None

    FrmTitle: ctk.CTkFrame | None = None
    FrmEditor: ctk.CTkFrame | None = None

    active = False

    @classmethod
    def start(cls, ribbon, sidebar, cad):
        cls.ribbon = ribbon
        cls.sidebar = sidebar
        cls.cad = cad

        cls.material = MaterialEditor(cls, ribbon, sidebar, cad)
        cls.section = SectionEditor(cls, ribbon, sidebar, cad)
        cls.node = NodeEditor(cls, ribbon, sidebar, cad)
        cls.load = LoadEditor(cls, ribbon, sidebar, cad)

        cls.active = True

    @classmethod
    def close(cls):
        cls.clear_area()

    @classmethod
    def stop(cls):
        cls.clear_area()

        cls.ribbon = None
        cls.sidebar = None
        cls.cad = None

        cls.material = None
        cls.section = None
        cls.node = None
        cls.load = None

        cls.active = False

    @classmethod
    def create_area(cls, title: str | None = None):
        cls.clear_area()

        if title:
            cls.FrmTitle = ctk.CTkFrame(cls.sidebar, fg_color="transparent", height=42)
            cls.FrmTitle.pack(side="top", fill="x")

            lbl_title = ctk.CTkLabel(
                cls.FrmTitle, text=title,
                font=("Segoe UI Semibold", 18),
                text_color=Theme.MainScreen.Editor.text
            )
            lbl_title.place(relx=0.5, y=20, anchor="c")

            sep = tk.Canvas(cls.FrmTitle, bg=Theme.tertiary, highlightthickness=0, height=2)
            sep.place(x=0, y=40, relwidth=1)

        cls.FrmEditor = ctk.CTkFrame(cls.sidebar, fg_color="transparent")
        cls.FrmEditor.pack(fill="both", expand=True)

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
                w.destroy()
            cls.FrmEditor.pack_forget()
            cls.FrmEditor.destroy()
            cls.FrmEditor = None
