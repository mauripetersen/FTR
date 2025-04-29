import customtkinter as ctk
from tkinter import messagebox, filedialog
import os

from config import FTR_NAME_0, projects_dir
from gui.style import Theme, configure_TopLevel
from gui.layout import tab, ribbon, sidebar, statusbar, cad
from gui.screens.open_project import OpenProjectScreen
from project import Project
from manager.language import lang

__all__ = ["MainScreen"]


class MainScreen(ctk.CTkToplevel):
    def __init__(self, master: ctk.CTk):
        super().__init__(master=master)
        configure_TopLevel(self)
        self.app = master

        # Tab (top menu)
        self.FrmTab = ctk.CTkFrame(self, fg_color=Theme.Tab.background, corner_radius=0)
        self.FrmTab.pack(side="top", fill="x")
        tab.create_tab(self, self.FrmTab)

        # Sidebar (side menu)
        self.FrmSideBar = ctk.CTkFrame(self, fg_color=Theme.SideBar.background, corner_radius=0, width=200)
        self.FrmSideBar.pack_propagate(False)  # Prevents the Frame from adjusting to the content
        self.FrmSideBar.pack(side="left", fill="y")
        sidebar.create_sidebar(self, self.FrmSideBar)

        # Ribbon (tools menu)
        self.FrmRibbon = ctk.CTkFrame(self, fg_color=Theme.Ribbon.background, corner_radius=0, height=40)
        self.FrmRibbon.pack_propagate(False)  # Prevents the Frame from adjusting to the content
        self.FrmRibbon.pack(side="top", fill="x")
        ribbon.create_ribbon(self, self.FrmRibbon)

        # Status bar
        self.FrmStatusBar = ctk.CTkFrame(self, fg_color=Theme.StatusBar.background, corner_radius=0, height=30)
        self.FrmStatusBar.pack_propagate(False)  # Prevents the Frame from adjusting to the content
        self.FrmStatusBar.pack(side="bottom", fill="x")
        statusbar.create_statusbar(self, self.FrmStatusBar)

        # Main graphical area (CAD)
        self.FrmCAD = ctk.CTkFrame(self, corner_radius=0)
        self.FrmCAD.pack(side="left", fill="both", expand=True)
        self.cad_interface: cad.CADInterface | None = None

        self.project: Project | None = Project("Untitled")
        self.create_cad_interface()

        self.op_screen: OpenProjectScreen | None = None

        self.protocol("WM_DELETE_WINDOW", self.confirm_close)

    def create_cad_interface(self):
        if self.project:
            self.cad_interface = cad.CADInterface(self, self.FrmCAD, self.project)
            self.cad_interface.pack(fill="both", expand=True)
            self.title(f"{FTR_NAME_0} ({self.project.name})")

    def open_project(self):
        self.op_screen = OpenProjectScreen(master=self.app)

        # project_path = filedialog.askdirectory(initialdir=projects_dir, mustexist=True,
        #                                        title=lang.get('choose_project'))
        # project_name = os.path.basename(project_path)
        # if project_name:
        #     if self.project and self.project.modified:
        #         result = messagebox.askyesnocancel(lang.get('project_not_saved'),
        #                                            lang.get('quest', 'save_before_open_project'))
        #         if result is None:
        #             return
        #         elif result:
        #             self.project.save_data()
        #
        #     self.close_project()
        #     self.project = Project(project_name)
        #     self.project.load_data()
        #     self.create_cad_interface()

    def close_project(self):
        self.cad_interface.pack_forget()  # flerken (é necessário?)
        self.cad_interface.destroy()
        self.cad_interface = None
        self.project = None
        
    def confirm_close(self):
        if self.project and self.project.modified:
            result = messagebox.askyesnocancel(lang.get('project_not_saved'), lang.get('quest', 'save_before_close'))
            if result is None:
                return
            elif result:
                self.project.save_data()
        self.master.destroy()
