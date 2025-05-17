import customtkinter as ctk
from tkinter import messagebox

from config import Settings, Theme
from project import ProjectManager, Node
from manager import Language

__all__ = ["NodeEditor"]


class NodeEditor:
    def __init__(self, editor, ribbon, sidebar, cad):
        self.editor = editor
        self.ribbon = ribbon
        self.sidebar = sidebar
        self.cad = cad

        self.EntPosition: ctk.CTkEntry | None = None

        self.BtnOk: ctk.CTkButton | None = None

    def add_node(self):
        project = ProjectManager.current

        if len(project.nodes) == 0:
            project.nodes.append(Node(0.0, None))
            self.cad.update_all_images()
            self.cad.draw_canvas()
        else:
            dialog = ctk.CTkInputDialog(text="Insert the span length",
                                        font=("Segoe UI Semibold", 14),
                                        title=Settings.FTR_NAME[0],
                                        fg_color=Theme.background,
                                        button_fg_color=Theme.highlight,
                                        button_hover_color=Theme.secondary,
                                        button_text_color=Theme.headline,
                                        entry_fg_color=Theme.secondary,
                                        entry_border_color=Theme.secondary,
                                        entry_text_color=Theme.headline)
            span = dialog.get_input()
            if not span:
                return

            try:
                span = float(span)
            except ValueError:
                messagebox.showerror(Settings.FTR_NAME[0], "Value not accepted.")
                return
            last_pos = max(node.position for node in project.nodes)
            project.nodes.append(Node(last_pos + float(span), None))

            self.cad.update_all_images()
            self.cad.draw_canvas()

    def edit_node(self, node: Node):
        self.editor.create_area(title=Language.get('MainScreen', 'Editor', 'Node', 'title'))

        FrmEditor: ctk.CTkFrame = self.editor.FrmEditor

        LblPosition = ctk.CTkLabel(
            FrmEditor, text="Position:", font=("Segoe UI", 14),
            text_color=Theme.MainScreen.Editor.text
        )
        LblPosition.place(x=20, y=30, anchor="w")

        self.EntPosition = ctk.CTkEntry(
            FrmEditor, font=("Segoe UI", 14), border_width=0, corner_radius=0,
            text_color=Theme.MainScreen.Editor.text
        )
        self.EntPosition.place(x=80, y=30, anchor="w")
        self.EntPosition.insert(0, node.position)

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
