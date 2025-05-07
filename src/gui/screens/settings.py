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

        self.FrmTitleBar = ctk.CTkFrame(self, height=30, fg_color="#1a1a1a", corner_radius=0)
        self.FrmTitleBar.pack(fill="x", side="top")

        self.LblTitle = ctk.CTkLabel(
            self.FrmTitleBar,
            text=f"{Settings.FTR_NAME[1]} - {Language.get('SettingsScreen', 'title')}",
            text_color="#ffffff"
        )
        self.LblTitle.place(relx=0.5, rely=0.5, anchor="center")

        self.BtnClose = ctk.CTkButton(self.FrmTitleBar, text="✕", width=30, height=30, corner_radius=0,
                                      fg_color="transparent", hover_color="#ff5555",
                                      command=app.close_settings)
        self.BtnClose.pack(side="right", padx=0)

        self.BtnMinimize = ctk.CTkButton(self.FrmTitleBar, text="—", width=30, height=30, corner_radius=0,
                                         fg_color="transparent", hover_color="#444444",
                                         command=app.withdraw_settings)
        self.BtnMinimize.pack(side="right", padx=0)

        langs = ["en", "pt"]
        self.OptLanguage = ctk.CTkOptionMenu(self,
                                             values=langs,
                                             width=200,
                                             height=30,
                                             corner_radius=10,
                                             font=('helvetica', 18),
                                             text_color='black',
                                             fg_color="#ff0000",
                                             button_color="#00ff00",
                                             button_hover_color="#0000ff",
                                             dropdown_font=('helvetica', 18),
                                             hover=True,
                                             anchor='center',  # 'n', 'e', 's', 'w', 'center'
                                             state='normal',
                                             dynamic_resizing=True)
        self.OptLanguage.pack(pady=70)

        self.BtnOK = ctk.CTkButton(self, width=30, height=30, corner_radius=0, hover_color="#ff5555",
                                   text=Language.get("SettingsScreen", "btn_ok"), fg_color="transparent",
                                   command=app.close_settings)
        self.BtnOK.pack(side="right", padx=0)

        self.BtnApply = ctk.CTkButton(self, width=30, height=30, corner_radius=0, hover_color="#ff5555",
                                      text=Language.get("SettingsScreen", "btn_apply"), fg_color="transparent",
                                      command=app.close_settings)
        self.BtnApply.pack(side="right", padx=0)

        self.pan_start = None
        self.FrmTitleBar.bind("<Button-1>", self.mouse_down_left)
        self.FrmTitleBar.bind("<B1-Motion>", self.mouse_move_left)
        self.FrmTitleBar.bind("<ButtonRelease-1>", self.mouse_up_left)

        self.protocol("WM_DELETE_WINDOW", app.close_settings)

    def mouse_down_left(self, event):
        self.configure(cursor="hand2")
        self.pan_start = (event.x, event.y)

    def mouse_move_left(self, event):
        if self.pan_start is None:
            return
        dx, dy = self.winfo_pointerx() - self.pan_start[0], self.winfo_pointery() - self.pan_start[1]
        self.geometry(f"+{dx}+{dy}")

    def mouse_up_left(self, event):
        self.configure(cursor="arrow")
        self.pan_start = None
