import customtkinter as ctk

from gui.screens import SplashScreen, MainScreen


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.window = SplashScreen(app=self)

    def start_app(self):
        if self.window:
            self.window.destroy()
            self.window = MainScreen(app=self)
