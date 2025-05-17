import customtkinter as ctk

from gui.screens import SplashScreen, MainScreen, SettingsScreen, AboutFTRScreen


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.window: ctk.CTkToplevel | None = SplashScreen(app=self)
        self.settings_window: ctk.CTkToplevel | None = None
        self.about_ftr_window: ctk.CTkToplevel | None = None

    def start_app(self):
        if self.window:
            self.window.destroy()
            self.window = MainScreen(app=self)

    def open_settings(self):
        if self.settings_window is None or not self.settings_window.winfo_exists():
            self.settings_window = SettingsScreen(app=self)  # create window if its None or destroyed
        else:
            if self.settings_window.state() == 'iconic' or self.settings_window.state() == 'withdrawn':
                self.settings_window.deiconify()  # or: self.toplevel_window.state('normal')
            self.settings_window.focus()  # if window exists focus it

    def close_settings(self):
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.destroy()
            self.settings_window = None

    def withdraw_settings(self):
        if self.settings_window is not None and self.settings_window.winfo_exists():
            self.settings_window.withdraw()  # or: self.toplevel_window.state('withdrawn')

    def open_about_ftr(self):
        if self.about_ftr_window is None or not self.about_ftr_window.winfo_exists():
            self.about_ftr_window = AboutFTRScreen(app=self)  # create window if its None or destroyed
        else:
            if self.about_ftr_window.state() == 'iconic' or self.about_ftr_window.state() == 'withdrawn':
                self.about_ftr_window.deiconify()  # or: self.toplevel_window.state('normal')
            self.about_ftr_window.focus()  # if window exists focus it

    def close_about_ftr(self):
        if self.about_ftr_window is not None and self.about_ftr_window.winfo_exists():
            self.about_ftr_window.destroy()
            self.about_ftr_window = None

    def withdraw_about_ftr(self):
        if self.about_ftr_window is not None and self.about_ftr_window.winfo_exists():
            self.about_ftr_window.withdraw()  # or: self.toplevel_window.state('withdrawn')
