import customtkinter as ctk
from tkinter import messagebox, filedialog

from config import Settings, Theme
from gui.style import configure_TopLevel
from gui.layout import tab, ribbon, sidebar, statusbar, cad
from gui.editor import Editor
from project import ProjectManager
from manager import Language

__all__ = ["MainScreen"]


class MainScreen(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(master=app)
        self.app = app

        configure_TopLevel(self)

        # Tab (top menu)
        self.FrmTab = tab.Tab(self.app, self)
        self.FrmTab.pack(side="top", fill="x")

        # Sidebar (side menu)
        self.FrmSideBar = sidebar.SideBar(self.app, self)
        self.FrmSideBar.pack(side="left", fill="y")

        # Ribbon (tools menu)
        self.FrmRibbon = ribbon.Ribbon(self.app, self)
        self.FrmRibbon.pack(side="top", fill="x")

        # Status bar
        self.FrmStatusBar = statusbar.StatusBar(self.app, self)
        self.FrmStatusBar.pack(side="bottom", fill="x")

        # Main graphical area (CAD)
        self.FrmCAD = ctk.CTkFrame(self, corner_radius=0)
        self.FrmCAD.pack(side="left", fill="both", expand=True)
        self.cad_interface: cad.CADInterface | None = None

        # flerken:
        # self.new_project()
        self.open_project("c:/GitHub/mauripetersen/FTR/projects/Projeto 1.ftr")

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

    def new_project(self):
        self.open_project(flag_new=True)

    def open_project(self, project_path: str = None, flag_new: bool = False):
        if not flag_new:
            if not project_path:
                project_path = filedialog.askopenfilename(
                    title=Language.get('open_project_title'),
                    initialdir=Settings.PROJECTS_DIR,
                    filetypes=[(Language.get('ftr_projects'), "*.ftr")]
                )
            if not project_path:
                return
        if self.close_project(message=Language.get('Quest', 'save_before_open_project')):
            ProjectManager.open(project_path)
            # create CADInterface:
            self.cad_interface = cad.CADInterface(self.app, self, self.FrmCAD)
            self.cad_interface.pack(fill="both", expand=True)
            # start Editor:
            if self.FrmRibbon and self.FrmSideBar and self.cad_interface:
                Editor.start(self.app, self)
            self.update_title()
            self.after(200, self.focus)

    def save_project(self, save_as: bool = False):
        if not ProjectManager.current:
            return
        if ProjectManager.current.path and not save_as:
            ProjectManager.save()
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
            ProjectManager.save_as(project_path)
        self.update_title()

    def close_project(self, ask_user: bool = True, message: str | None = None) -> bool:
        """
        Closes the project. It can be called for many reasons.
        :param ask_user: Flag to ask the user if the project is not saved.
        :param message: Message to the user if the project is not saved.
        :return: True if the project was successfully closed and False if it didn't (and the user don't want to).
        """
        if ask_user and ProjectManager.current and ProjectManager.current.modified:
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

            self.unbind("<KeyPress>")
            self.unbind("<KeyRelease>")
            self.unbind("<Control-a>")
            self.unbind("<Control-y>")
            self.unbind("<Control-z>")
            self.unbind("<Delete>")
            self.unbind("<Escape>")

        Editor.stop()
        ProjectManager.close()

        self.update_title()
        self.FrmStatusBar.LblPos.configure(text="")
        self.after(100, self.focus)  # flerken: verificar isso
        return True

    def update_title(self):
        project = ProjectManager.current
        if project:
            if project.modified:
                title = f"{Settings.FTR_NAME[0]}: {project.name}*.ftr"
            else:
                title = f"{Settings.FTR_NAME[0]}: {project.name}.ftr"
        else:
            title = Settings.FTR_NAME[0]
        self.title(title)

    def on_close(self):
        if self.close_project():
            self.master.destroy()
