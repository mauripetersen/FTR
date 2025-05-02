import ctypes
import tkinter as tk
import tkinter.font as tkFont
import os
from PIL import ImageFont

from config import Settings

__all__ = ["FontManager"]


class FontManager:
    # Dictionary with fonts used in FTR
    FONTS = {
        "Cambria": {
            "file": os.path.join(Settings.FONTS_DIR, "Cambria", "cambria.ttc"),
            "internal_name": "Cambria"
        },
        "Segoe UI": {
            "file": os.path.join(Settings.FONTS_DIR, "Segoe UI", "segoeui.ttf"),
            "internal_name": "Segoe UI"
        },
        "Segoe UI Semibold": {
            "file": os.path.join(Settings.FONTS_DIR, "Segoe UI", "segoeuisb.ttf"),
            "internal_name": "Segoe UI Semibold"
        }
    }

    @classmethod
    def is_font_available(cls, name: str) -> bool:
        """Checks if a font is already registered in the system."""
        if not tk._default_root:
            raise RuntimeError("Nenhuma instância Tk foi criada ainda. Crie o App() antes de registrar fontes.")
        return name in tkFont.families()

    @classmethod
    def register_font(cls, ttf_path: str, internal_name: str):
        """Registers a .ttf font in the system if it is not already available."""
        if not cls.is_font_available(internal_name):
            if not os.path.exists(ttf_path):
                raise FileNotFoundError(f'Fonte não encontrada: "{ttf_path}"')
            ctypes.windll.gdi32.AddFontResourceW(ttf_path)

    @classmethod
    def register_all_fonts(cls):
        """Registers all fonts listed in the FONTS dictionary."""
        for key, font_data in cls.FONTS.items():
            cls.register_font(font_data["file"], font_data["internal_name"])

    @classmethod
    def get_pillow_font(cls, name: str, size: int = 12):
        """Returns a PIL.ImageFont object for use in Pillow."""
        if name not in cls.FONTS:
            raise KeyError(f'Fonte "{name}" não está registrada em FONTS.')
        return ImageFont.truetype(cls.FONTS[name]["file"], size)
