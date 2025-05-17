import customtkinter as ctk

from config import Theme
from gui.style import configure_TopLevel
from manager import Language

__all__ = ["AboutFTRScreen"]


class AboutFTRScreen(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(master=app)
        self.app = app

        self.size = (800, 500)
        configure_TopLevel(self, maximized=False, win_size=self.size, flat=True)

        self.FrmTitleBar = ctk.CTkFrame(self, height=30, fg_color=Theme.AboutFTRScreen.titlebar, corner_radius=0)
        self.FrmTitleBar.pack(fill="x", side="top")

        self.FrmMain = ctk.CTkFrame(self, fg_color=Theme.AboutFTRScreen.background, corner_radius=0)
        self.FrmMain.pack(side="top", fill="both", expand=True)

        # FrmTitleBar:
        self.LblTitle = ctk.CTkLabel(
            self.FrmTitleBar, text=Language.get('AboutFTRScreen', 'title'), font=("Segoe UI", 14),
            text_color=Theme.AboutFTRScreen.text
        )
        self.LblTitle.place(relx=0.5, rely=0.5, anchor="center")

        self.BtnClose = ctk.CTkButton(
            self.FrmTitleBar, text="✕", width=30, height=30, corner_radius=0,
            fg_color="transparent", hover_color="#ff5555",
            command=self.app.close_about_ftr
        )
        self.BtnClose.pack(side="right", padx=0)

        self.BtnMinimize = ctk.CTkButton(
            self.FrmTitleBar, text="—", width=30, height=30, corner_radius=0,
            fg_color="transparent", hover_color=Theme.AboutFTRScreen.secondary,
            command=app.withdraw_settings
        )
        self.BtnMinimize.pack(side="right", padx=0)

        # FrmMain:
        self._pan_start = None

        self.bind("<Escape>", self.on_escape)
        self.FrmTitleBar.bind("<Button-1>", self.on_mouse_down_left)
        self.FrmTitleBar.bind("<B1-Motion>", self.on_mouse_move_left)
        self.FrmTitleBar.bind("<ButtonRelease-1>", self.on_mouse_up_left)

        self.protocol("WM_DELETE_WINDOW", self.app.close_about_ftr)
        self.after(100, self.focus)

    # region "Binds"

    def on_escape(self, event):
        self.app.close_about_ftr()

    def on_mouse_down_left(self, event):
        self._pan_start = (event.x, event.y)

    def on_mouse_move_left(self, event):
        if self._pan_start is None:
            return
        dx, dy = self.winfo_pointerx() - self._pan_start[0], self.winfo_pointery() - self._pan_start[1]
        self.geometry(f"+{dx}+{dy}")

    def on_mouse_up_left(self, event):
        self._pan_start = None

    # endregion
