import customtkinter as ctk

from gui.style import Theme, configure_root
from gui.interface import tab, ribbon, sidebar, statusbar, cad

__all__ = ["App"]


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        configure_root(self)

        # Tab (menu superior)
        self.FrmTab = ctk.CTkFrame(self, fg_color=Theme.dark_1, bg_color=Theme.background, corner_radius=0)
        # self.FrmTab.pack_propagate(False)  # Prevents the Frame from adjusting to the content (height fixed)
        self.FrmTab.pack(side="top", fill="x")
        self.active_menu: ctk.CTkFrame | None = None

        tab.create_tab(self.FrmTab, self)

        # Sidebar (menu lateral)
        self.FrmSideBar = ctk.CTkFrame(self, fg_color=Theme.dark_2, bg_color=Theme.background, corner_radius=0,
                                       width=150)
        self.FrmSideBar.pack_propagate(False)
        self.FrmSideBar.pack(side="left", fill="y")
        sidebar.create_sidebar(self.FrmSideBar, self)

        # Ribbon (menu superior)
        self.FrmRibbon = ctk.CTkFrame(self, fg_color=Theme.dark_1, bg_color=Theme.background, corner_radius=0,
                                      height=40)
        self.FrmRibbon.pack(side="top", fill="x")
        ribbon.create_ribbon(self.FrmRibbon, self)

        # Status bar (rodapé)
        self.FrmStatusBar = ctk.CTkFrame(self, fg_color=Theme.Illustration.secondary, bg_color=Theme.background,
                                         corner_radius=0, height=30)  # height = 25
        self.FrmStatusBar.pack(side="bottom", fill="x")
        statusbar.create_statusbar(self.FrmStatusBar, self)

        # Área principal gráfica (CAD)
        self.FrmCAD = ctk.CTkFrame(self, fg_color="transparent", bg_color="transparent", corner_radius=0)
        self.FrmCAD.pack(side="left", fill="both", expand=True)
        self.canvas = cad.CAD(self.FrmCAD)  # classe CAD herdando de CTkCanvas ou CTkFrame
        self.canvas.pack(fill="both", expand=True)

    def run(self):
        self.mainloop()
