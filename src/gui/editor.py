import customtkinter as ctk
import tkinter as tk

from config import Theme
from project import ProjectHolder, Section, Node, Load, PLLoad, DLLoad
from manager import Language

__all__ = ["Editor"]


class Editor:
    def __init__(self, app, main_screen):
        self.app = app
        self.main_screen = main_screen

        self.current_element: Section | Node | Load | None = None
        self._modified = False

        # EDITOR:
        self.FrmEditor = None
        self.LblEditorTitle = None

        # Section Editor:
        self.LblSection = None
        self.OptSection = None
        self.CanImage = None
        self.LblDimB = None
        self.LblDimH = None

        # Node Editor:
        # ...

        # Load Editor:
        # ...

    def create_editor_frame(self, title=None):
        self.close_editor()
        self.FrmEditor = ctk.CTkFrame(self.main_screen.FrmSideBar, fg_color="transparent")
        self.FrmEditor.pack(fill="both", expand=True)

        if title:
            self.LblEditorTitle = ctk.CTkLabel(
                self.FrmEditor, text=title,
                font=("Segoe UI Semibold", 18),
                text_color=Theme.MainScreen.Editor.Label.text
            )
            self.LblEditorTitle.pack(pady=10)

            sep = tk.Canvas(self.FrmEditor, bg=Theme.tertiary, highlightthickness=0, height=2)
            sep.pack(pady=0, fill="y")

    def close_editor(self):
        if self.FrmEditor:
            for widget in self.FrmEditor.winfo_children():
                widget.destroy()
            self.FrmEditor.pack_forget()
            self.FrmEditor = None
        self.current_element = None

    def section_properties(self, section: Section):
        self.current_element = section
        self._modified = False

        self.create_editor_frame(title=Language.get('MainScreen', 'Editor', 'Section', 'title'))

        self.LblSection = ctk.CTkLabel(
            self.FrmEditor, text=Language.get('MainScreen', 'Editor', 'Section', 'section_type'), font=("Segoe UI", 16),
            text_color=Theme.MainScreen.Editor.Label.text
        )
        self.LblSection.pack(pady=15)

        self.OptSection = ctk.CTkOptionMenu(self.FrmEditor,
                                            values=["Rectangle", "I-shape", "T-shape"],
                                            width=130,
                                            # height=30,
                                            corner_radius=0,
                                            font=("Segoe UI", 16),
                                            text_color=Theme.MainScreen.Editor.OptionMenu.text,
                                            fg_color=Theme.MainScreen.Editor.OptionMenu.fg,
                                            button_color=Theme.MainScreen.Editor.OptionMenu.button,
                                            button_hover_color=Theme.MainScreen.Editor.OptionMenu.button_hover,
                                            dropdown_font=('Segoe UI', 16),
                                            hover=True,
                                            anchor='center',  # 'n', 'e', 's', 'w', 'center'
                                            state='normal',
                                            dynamic_resizing=True)
        self.OptSection.pack(pady=0)

        self.CanImage = tk.Canvas(self.FrmEditor, background="white", width=200)
        self.CanImage.pack(pady=50)

    def add_node(self):
        project = ProjectHolder.current
        if len(project.nodes) == 0:
            project.nodes.append(Node(0.0, None))
            self.main_screen.cad_interface.update_all_images()
            self.main_screen.cad_interface.draw_canvas()
        else:
            ...

    def edit_node(self, node: Node):
        self.current_element = node
        self._modified = False

        self.create_editor_frame(title=Language.get('MainScreen', 'Editor', 'Node', 'title'))

    def add_load(self):
        ...

    def edit_load(self, load: Load):
        self.current_element = load
        self._modified = False

        self.create_editor_frame(title=Language.get('MainScreen', 'Editor', 'Load', 'title'))

        if isinstance(load, PLLoad):
            ...
        elif isinstance(load, DLLoad):
            ...
        else:
            ...
