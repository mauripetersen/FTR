import customtkinter as ctk

from gui.screens import SplashScreen, MainScreen


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.withdraw()
        self.window = SplashScreen(master=self)
        
    def start_app(self):
        self.window.destroy()
        self.window = MainScreen(master=self)
