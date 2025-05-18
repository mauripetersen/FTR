import customtkinter as ctk
from tkinter import messagebox

from config import Settings, Theme
from project import ProjectManager, Node
from manager import Language

__all__ = ["NodeEditor"]


class NodeEditor:
    def __init__(self, app, main_screen):
        from gui.editor import Editor
        self.editor = Editor

        self.app = app
        self.main_screen = main_screen
        self.ribbon = main_screen.FrmRibbon
        self.sidebar = main_screen.FrmSideBar
        self.cad = main_screen.cad_interface

        self.current_node: Node | None = None

        self.VarPosition: ctk.StringVar | None = None
        self.EntPosition: ctk.CTkEntry | None = None

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
        self.current_node = node

        self.editor.create_area(Language.get('Editor', 'Node', 'title'), self.on_ok)
        self.editor.lock_ok_button()

        FrmEditor = self.editor.FrmEditor

        LblPosition = ctk.CTkLabel(
            FrmEditor, text="Position:", font=("Segoe UI", 14),
            text_color=Theme.Editor.text
        )
        LblPosition.place(x=20, y=30, anchor="w")

        self.VarPosition = ctk.StringVar()
        self.VarPosition.set(str(self.current_node.position))
        self.VarPosition.trace_add("write", self.on_change)

        self.EntPosition = ctk.CTkEntry(
            FrmEditor, font=("Segoe UI", 14), border_width=0, corner_radius=0, width=80,
            text_color=Theme.Editor.text,
            textvariable=self.VarPosition
        )
        self.EntPosition.place(x=80, y=30, anchor="w")
        self.EntPosition.bind("<Return>", self.on_ok)

        LblPosition_unit = ctk.CTkLabel(
            FrmEditor, text="m", font=("Segoe UI", 14),
            text_color=Theme.Editor.text
        )
        LblPosition_unit.place(x=170, y=30, anchor="w")

    def on_change(self, *args):
        has_changed = False

        pos = self.VarPosition.get()
        try:
            pos_float = float(pos)
            if self.current_node.position != pos_float:
                has_changed = True
        except ValueError:
            self.EntPosition.configure(fg_color=Theme.Editor.error, font=("Segoe UI", 14, "bold"))
        else:
            self.EntPosition.configure(fg_color=Theme.Editor.secondary[0], font=("Segoe UI", 14))

        if has_changed:
            self.editor.unlock_ok_button()
        else:
            self.editor.lock_ok_button()

    def on_ok(self, event=None):
        pos = self.VarPosition.get()

        try:
            pos_float = float(pos)
        except ValueError:
            messagebox.showerror("Value Error", "Position must be a valid number.")
        else:
            self.current_node.position = pos_float
            ProjectManager.current.modified = True
            ProjectManager.save_history()

            self.main_screen.update_title()
            self.cad.update_all_images()
            self.cad.draw_canvas()
