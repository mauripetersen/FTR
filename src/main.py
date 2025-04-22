import customtkinter as ctk
import ctypes

from gui.app import App
from font_manager import register_all_fonts

if __name__ == "__main__":
    ctk.set_appearance_mode("Dark")
    try:
        ctypes.windll.shcore.SetProcessDpiAwareness(1)  # SYSTEM_AWARE
        scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0) / 100
        ctk.set_window_scaling(1 / scale_factor)
        ctk.set_widget_scaling(1 / scale_factor)
    except Exception as e:
        print(f"Falha ao detectar escala do sistema: {e}")

    app = App()
    register_all_fonts()
    app.mainloop()
