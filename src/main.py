import customtkinter as ctk
import ctypes

from config import Settings, Theme
from gui.app import App
from manager import FontManager, Language

if __name__ == "__main__":
    Settings.load()
    Language.load()
    Theme.load()

    ctk.set_appearance_mode(Settings.theme)
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # SYSTEM_AWARE
        scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        ctk.set_window_scaling(1 / scale_factor)
        ctk.set_widget_scaling(1 / scale_factor)
    except Exception as e:
        print(f"{Language.get('Error', 'detect_scale')}: {e}")

    app = App()
    FontManager.register_all_fonts()  # it must be after app created, se we can access tk._default_root
    app.mainloop()
