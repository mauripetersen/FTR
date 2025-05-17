import customtkinter as ctk

from config import Theme

__all__ = ["SideBar"]


class SideBar(ctk.CTkFrame):
    def __init__(self, app, main_screen):
        super().__init__(main_screen, fg_color=Theme.MainScreen.SideBar.background, corner_radius=0, width=300)
        self.pack_propagate(False)  # Prevents the Frame from adjusting to the content
        self.app = app
        self.main_screen = main_screen
