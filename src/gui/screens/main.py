import customtkinter as ctk
from tkinter import messagebox, filedialog

from config import Settings, Theme
from gui.style import configure_TopLevel
from gui.layout import tab, ribbon, sidebar, statusbar, cad
from gui.editor import Editor
from project import Project, ProjectHolder
from manager import Language

__all__ = ["MainScreen"]


class MainScreen(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(master=app)
        self.app = app

        configure_TopLevel(self)
        # flerken:
        # ProjectHolder.current = Project()
        ProjectHolder.current = Project("c:/GitHub/mauripetersen/FTR/projects/Projeto 1.ftr")
        ProjectHolder.current.load_data()
        ProjectHolder.save_history()

        self.editor = Editor(self.app, self)

        # Tab (top menu)
        self.FrmTab = tab.Tab(self.app, self)
        self.FrmTab.pack(side="top", fill="x")

        # Sidebar (side menu)
        self.FrmSideBar = sidebar.SideBar(self.app, self)
        self.FrmSideBar.pack(side="left", fill="y")

        # Ribbon (tools menu)
        self.FrmRibbon = ribbon.Ribbon(self.app, self, self.editor)
        self.FrmRibbon.pack(side="top", fill="x")

        # Status bar
        self.FrmStatusBar = statusbar.StatusBar(self.app, self)
        self.FrmStatusBar.pack(side="bottom", fill="x")

        # Main graphical area (CAD)
        self.FrmCAD = ctk.CTkFrame(self, corner_radius=0)
        self.FrmCAD.pack(side="left", fill="both", expand=True)
        self.cad_interface: cad.CADInterface | None = None
        self.create_cad_interface()

        self.bind("<Control-n>", self.on_ctrl_n)
        self.bind("<Control-o>", self.on_ctrl_o)
        self.bind("<Control-s>", self.on_ctrl_s)
        self.bind("<Control-w>", self.on_ctrl_w)

        self.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_ctrl_n(self, event):
        self.new_project()

    def on_ctrl_o(self, event):
        self.open_project()

    def on_ctrl_s(self, event):
        self.save_project()

    def on_ctrl_w(self, event):
        self.close_project()

    def create_cad_interface(self):
        if ProjectHolder.current:
            self.cad_interface = cad.CADInterface(self.app, self, self.FrmCAD, self.editor)
            self.cad_interface.pack(fill="both", expand=True)
        self.update_title()

    def new_project(self):
        if self.close_project():
            ProjectHolder.current = Project()
            ProjectHolder.save_history()
            self.create_cad_interface()

    def open_project(self, project_path: str = None):
        if not project_path:
            project_path = filedialog.askopenfilename(
                title=Language.get('open_project_title'),
                initialdir=Settings.PROJECTS_DIR,
                filetypes=[(Language.get('ftr_projects'), "*.ftr")]
            )
        if not project_path:
            return
        if self.close_project(message=Language.get('Quest', 'save_before_open_project')):
            ProjectHolder.current = Project(project_path)
            if ProjectHolder.current.load_data():
                ProjectHolder.save_history()
                self.create_cad_interface()
                self.after(100, self.focus)

    def save_project(self, save_as: bool = False):
        project = ProjectHolder.current
        if not project:
            return
        if project.path and not save_as:
            project.save_data()
        else:
            title = Language.get('save_as_project_title') if save_as else Language.get('save_project_title')
            project_path = filedialog.asksaveasfilename(
                title=title,
                initialdir=Settings.PROJECTS_DIR,
                filetypes=[(Language.get('ftr_projects'), "*.ftr")],
                initialfile="Untitled",
                defaultextension=".ftr"
            )
            if not project_path:
                return
            project.path = project_path
            project.save_data()
        self.update_title()

    def close_project(self, ask_user: bool = True, message: str | None = None) -> bool:
        """
        Closes the project. It can be called for many reasons.
        :param ask_user: Flag to ask the user if the project is not saved.
        :param message: Message to the user if the project is not saved.
        :return: True if the project was successfully closed and False if it didn't (and the user don't want to).
        """
        if ask_user and ProjectHolder.current and ProjectHolder.current.modified:
            msg = message if message else Language.get('Quest', 'save_before_close')
            result = messagebox.askyesnocancel(Language.get('project_not_saved'), msg, icon="warning")
            if result is None:
                return False
            elif result:
                self.save_project()

        if self.cad_interface:
            self.cad_interface.pack_forget()
            self.cad_interface.destroy()
            self.cad_interface = None

            self.unbind("<Control-a>")
            self.unbind("<Control-y>")
            self.unbind("<Control-z>")
            self.unbind("<Delete>")
            self.unbind("<Escape>")

        ProjectHolder.current = None
        ProjectHolder.clear_history()

        self.update_title()
        self.FrmStatusBar.LblPos.configure(text="")
        self.after(100, self.focus)  # flerken: verificar isso
        return True

    def update_title(self):
        project = ProjectHolder.current
        if project:
            if project.modified:
                title = f"{Settings.FTR_NAME[0]}: {project.name}*.ftr"
            else:
                title = f"{Settings.FTR_NAME[0]}: {project.name}.ftr"
        else:
            title = Settings.FTR_NAME[0]
        self.title(title)

    def on_close(self):
        self.close_project()
        self.master.destroy()
