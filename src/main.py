import customtkinter as ctk

from gui.app import App
from font_manager import register_all_fonts

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    app = App()
    register_all_fonts()
    app.mainloop()
