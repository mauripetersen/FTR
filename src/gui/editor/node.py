import customtkinter as ctk
from tkinter import messagebox
from typing import Any

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

        self.entries: list[dict[str, Any]] = [
            {
                "name": "position",
                "variable": None,
                "entry": None,
                "label": "Position:",
                "unit": "m",
                "get": lambda: getattr(self.current_node, "position"),
                "set": lambda v: setattr(self.current_node, "position", v)
            }
        ]

    def add_node(self):
        project = ProjectManager.current

        if len(project.nodes) == 0:
            project.nodes.append(Node(0.0, None))

            ProjectManager.save_history()
            self.main_screen.update_title()
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

            ProjectManager.save_history()
            self.main_screen.update_title()
            self.cad.update_all_images()
            self.cad.draw_canvas()

    def edit_node(self, node: Node):
        self.current_node = node

        self.editor.create_area(Language.get('Editor', 'Node', 'title'), self.on_ok)
        self.editor.lock_ok_button()

        FrmEditor = self.editor.FrmEditor

        for ix, item in enumerate(self.entries):
            ctk.CTkLabel(
                FrmEditor, text=item["label"], font=("Segoe UI", 14),
                text_color=Theme.Editor.text
            ).place(x=20, y=30, anchor="w")

            item["variable"] = ctk.StringVar()
            item["variable"].set(str(item["get"]()))
            item["variable"].trace_add("write", self.on_change)

            item["entry"] = ctk.CTkEntry(
                FrmEditor, font=("Segoe UI", 14), border_width=0, corner_radius=0, width=80,
                text_color=Theme.Editor.text,
                textvariable=item["variable"]
            )
            item["entry"].place(x=80, y=30, anchor="w")
            item["entry"].bind("<Return>", self.on_ok)

            ctk.CTkLabel(
                FrmEditor, text="m", font=("Segoe UI", 14),
                text_color=Theme.Editor.text
            ).place(x=170, y=30, anchor="w")

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
        self.editor.node.edit_node(self.current_node)
