import customtkinter as ctk

from gui.style import Theme, configure_TopLevel
from gui.interface.layout import tab, ribbon, sidebar, statusbar, cad
from project import Project

__all__ = ["MainScreen"]


class MainScreen(ctk.CTkToplevel):
    def __init__(self, master: ctk.CTk):
        super().__init__(master=master)
        configure_TopLevel(self)

        self.project = Project("Projeto 1")
        self.project.load_data()
        # self.project = None

        # Tab (top menu)
        self.FrmTab = ctk.CTkFrame(self, fg_color=Theme.dark_1, bg_color=Theme.background, corner_radius=0)
        self.FrmTab.pack(side="top", fill="x")
        tab.create_tab(self, self.FrmTab)

        # Sidebar (side menu)
        self.FrmSideBar = ctk.CTkFrame(self, fg_color=Theme.dark_2, bg_color=Theme.background, corner_radius=0,
                                       width=150)
        self.FrmSideBar.pack_propagate(False)  # Prevents the Frame from adjusting to the content
        self.FrmSideBar.pack(side="left", fill="y")
        sidebar.create_sidebar(self, self.FrmSideBar)

        # Ribbon (tools menu)
        self.FrmRibbon = ctk.CTkFrame(self, fg_color=Theme.dark_1, bg_color=Theme.background, corner_radius=0,
                                      height=40)
        self.FrmRibbon.pack_propagate(False)  # Prevents the Frame from adjusting to the content
        self.FrmRibbon.pack(side="top", fill="x")
        ribbon.create_ribbon(self, self.FrmRibbon)

        # Status bar
        self.FrmStatusBar = ctk.CTkFrame(self, fg_color=Theme.Illustration.secondary, bg_color=Theme.background,
                                         corner_radius=0, height=30)  # height = 25
        self.FrmStatusBar.pack(side="bottom", fill="x")
        statusbar.create_statusbar(self, self.FrmStatusBar)

        # Main graphical area (CAD)
        self.FrmCAD = ctk.CTkFrame(self, corner_radius=0)
        self.FrmCAD.pack(side="left", fill="both", expand=True)
        self.cad_interface = cad.CADInterface(self.FrmCAD, self.project)
        self.cad_interface.pack(fill="both", expand=True)

        self.protocol("WM_DELETE_WINDOW", self.master.destroy)
