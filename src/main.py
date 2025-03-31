import customtkinter as ctk

from gui.splash import SplashScreen

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    root = ctk.CTk()
    SplashScreen(root)
    root.mainloop()
