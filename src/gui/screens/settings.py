from tkinter import messagebox
import customtkinter as ctk

from config import Settings, Theme
from gui.style import configure_TopLevel
from manager import Language

__all__ = ["SettingsScreen"]


class SettingsScreen(ctk.CTkToplevel):
    def __init__(self, app):
        super().__init__(master=app)
        self.app = app

        self.size = (800, 500)
        configure_TopLevel(self, maximized=False, win_size=self.size, flat=True)

        self.FrmTitleBar = ctk.CTkFrame(self, height=30, fg_color=Theme.SettingsScreen.titlebar, corner_radius=0)
        self.FrmTitleBar.pack(fill="x", side="top")

        self.FrmMain = ctk.CTkFrame(self, fg_color=Theme.SettingsScreen.background, corner_radius=0)
        self.FrmMain.pack(side="top", fill="both", expand=True)

        # FrmTitleBar:
        self.LblTitle = ctk.CTkLabel(
            self.FrmTitleBar, text=Language.get('SettingsScreen', 'title'), font=("Segoe UI", 14),
            text_color=Theme.SettingsScreen.text
        )
        self.LblTitle.place(relx=0.5, rely=0.5, anchor="center")

        self.BtnClose = ctk.CTkButton(
            self.FrmTitleBar, text="✕", width=30, height=30, corner_radius=0,
            fg_color="transparent", hover_color="#ff5555",
            command=self.on_close
        )
        self.BtnClose.pack(side="right", padx=0)

        self.BtnMinimize = ctk.CTkButton(
            self.FrmTitleBar, text="—", width=30, height=30, corner_radius=0,
            fg_color="transparent", hover_color=Theme.SettingsScreen.secondary,
            command=app.withdraw_settings
        )
        self.BtnMinimize.pack(side="right", padx=0)

        # FrmMain:
        self.LblLanguage = ctk.CTkLabel(
            self.FrmMain, text=Language.get("SettingsScreen", "language"), font=("Segoe UI", 14),
            text_color=Theme.SettingsScreen.text
        )
        self.LblLanguage.place(x=15, y=15, anchor="nw")

        self.OptLanguage = ctk.CTkOptionMenu(self.FrmMain,
                                             values=[lang for lang in Settings.LANGUAGES.values()],
                                             width=150,
                                             height=25,
                                             corner_radius=0,
                                             font=("Segoe UI", 14),
                                             text_color=Theme.SettingsScreen.text,
                                             fg_color=Theme.SettingsScreen.secondary,
                                             button_color=Theme.secondary,
                                             button_hover_color=Theme.secondary,
                                             dropdown_font=('Segoe UI', 14),
                                             hover=True,
                                             anchor='center',  # 'n', 'e', 's', 'w', 'center'
                                             state='normal',
                                             dynamic_resizing=True)
        self.OptLanguage.place(x=15, y=45, anchor="nw")

        if Settings.LANGUAGES.get(Settings.language):
            self.OptLanguage.set(Settings.LANGUAGES.get(Settings.language))

        self.update()
        self.BtnOK = ctk.CTkButton(
            self.FrmMain, width=40, height=30, corner_radius=5,
            fg_color=Theme.SettingsScreen.secondary, hover_color=Theme.highlight,
            text="OK", font=("Segoe UI Semibold", 14),
            command=self.on_ok
        )
        self.BtnOK.place(x=self.FrmMain.winfo_width() - 15, y=self.FrmMain.winfo_height() - 15, anchor="se")

        self.pan_start = None

        self.bind("<Escape>", self.on_escape)
        self.FrmTitleBar.bind("<Button-1>", self.on_mouse_down_left)
        self.FrmTitleBar.bind("<B1-Motion>", self.on_mouse_move_left)
        self.FrmTitleBar.bind("<ButtonRelease-1>", self.on_mouse_up_left)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.after(100, self.focus)

    # region "Binds"

    def on_escape(self, event):
        self.on_close()

    def on_mouse_down_left(self, event):
        self.pan_start = (event.x, event.y)

    def on_mouse_move_left(self, event):
        if self.pan_start is None:
            return
        dx, dy = self.winfo_pointerx() - self.pan_start[0], self.winfo_pointery() - self.pan_start[1]
        self.geometry(f"+{dx}+{dy}")

    def on_mouse_up_left(self, event):
        self.pan_start = None

    # endregion

    def on_ok(self):
        # Language:
        lang = self.OptLanguage.get()
        for k, v in Settings.LANGUAGES.items():
            if v == lang:
                Settings.language = k
        # flerken: verificar se farei assim:
        Settings.save()
        Language.load()
        self.app.close_settings()

    def on_close(self):
        self.app.close_settings()
