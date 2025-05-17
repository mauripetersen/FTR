import customtkinter as ctk
from PIL import Image
from dataclasses import dataclass
from enum import StrEnum
import json
import sys
import os

__version__ = "1.0.0"

__all__ = ["__version__",
           "SectionType", "SupportType", "LoadType",
           "Settings", "Theme"]


class SectionType(StrEnum):
    """
    "R" = Rectangle
    "I" = I-shape
    "T" = T-shape
    """
    R = "R"
    I = "I"
    T = "T"


class SupportType(StrEnum):
    """
    "roller" = 2 degrees of freedom
    "pinned" = 1 degree of freedom
    "fixed" = 0 degrees of freedom
    """
    Roller = "roller"
    Pinned = "pinned"
    Fixed = "fixed"


class LoadType(StrEnum):
    """
    "PL" = Point Load
    "DL" = Distributed Load
    """
    PL = "PL"
    DL = "DL"


class Settings:
    # Ensures BASE_DIR for both cases (.py and .exe):
    if getattr(sys, 'frozen', False):
        BASE_DIR: str = os.path.dirname(sys.executable)
    else:
        BASE_DIR: str = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

    # Main directories
    ASSETS_DIR = os.path.join(BASE_DIR, "assets")
    CONFIGS_DIR = os.path.join(BASE_DIR, "configs")
    PROJECTS_DIR = os.path.join(BASE_DIR, "projects")

    # Sub-Directories
    FONTS_DIR = os.path.join(ASSETS_DIR, "fonts")
    ICONS_DIR = os.path.join(ASSETS_DIR, "icons")
    IMAGES_DIR = os.path.join(ASSETS_DIR, "images")
    LANGUAGES_DIR = os.path.join(CONFIGS_DIR, "languages")
    THEMES_DIR = os.path.join(CONFIGS_DIR, "themes")

    FTR_NAME = ("FTR - Ferri Tractus Ratio",
                "FTR",
                "Ferri Tractus Ratio")
    LANGUAGES = {"en": "English",
                 "pt": "Português (BR)"}

    BTN_MATERIAL_PARAMETERS_IMG = ctk.CTkImage(Image.open(os.path.join(IMAGES_DIR, "material.png")), size=(40, 40))
    BTN_SECTION_PROPERTIES_IMG = ctk.CTkImage(Image.open(os.path.join(IMAGES_DIR, "section.png")), size=(40, 40))
    BTN_NODE_IMG = ctk.CTkImage(Image.open(os.path.join(IMAGES_DIR, "node.png")), size=(40, 40))

    # BTN_LOAD_IMG = ctk.CTkImage(Image.open(os.path.join(IMAGES_DIR, "load.png")), size=(40, 40))

    settings_path = os.path.join(CONFIGS_DIR, "settings.json")
    language = "en"
    theme = "dark"

    @classmethod
    def load(cls):
        """Load the settings from the file FTR/configs/settings.json"""
        try:
            if os.path.exists(cls.settings_path):
                with open(cls.settings_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                    cls.language = data.get("language", cls.language)
                    cls.theme = data.get("theme", cls.theme)
            else:
                cls.set_default()
                cls.save()
        except Exception as e:
            raise RuntimeError(f"Error loading FTR settings: {e}")

    @classmethod
    def save(cls):
        """Save the current settings in the file FTR/configs/settings.json"""
        data = {
            "language": cls.language,
            "theme": cls.theme
        }
        try:
            json_str = json.dumps(data, indent=4)
            json_str_with_tabs = json_str.replace("    ", "\t")
            with open(cls.settings_path, "w") as f:
                f.write(json_str_with_tabs)
        except Exception as e:
            raise RuntimeError(f"Error saving FTR settings: {e}")

    @classmethod
    def set_default(cls):
        cls.language = "pt"
        cls.theme = "dark"


class Theme:
    background: str
    headline: str
    paragraph: str
    highlight: str
    secondary: str
    tertiary: str

    @dataclass
    class AboutFTRScreen:
        background: str
        text: str
        secondary: str
        titlebar: str

    @dataclass
    class MainScreen:
        @dataclass
        class Editor:
            text: str
            highlight: str
            secondary: list[str]

        @dataclass
        class Tab:
            background: str
            text: str
            highlight: str
            menu: str
            secondary: str

        @dataclass
        class SideBar:
            background: str
            text: str
            highlight: str

        @dataclass
        class Ribbon:
            background: str
            text: str
            highlight: str

        @dataclass
        class StatusBar:
            background: str
            text: str
            highlight: str

        @dataclass
        class CAD:
            background: str
            grid: list[str]
            select_rect: str
            spans: str
            nodes: list[str]
            supports: str
            loads: list[str]

    @dataclass
    class SettingsScreen:
        background: str
        text: str
        secondary: str
        titlebar: str

    @classmethod
    def load(cls):
        try:
            theme_path = os.path.join(Settings.THEMES_DIR, f"{Settings.theme}.json")
            with open(theme_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for key, val in data.items():
                cls.add_item(cls, key, val)
        except Exception as e:
            raise RuntimeError(f"Error loading FTR Theme: {e}")

    @classmethod
    def add_item(cls, cls_at, key_at, val_at):
        if isinstance(val_at, dict):
            sub_cls = getattr(cls_at, key_at, None)
            if sub_cls:
                for sub_key, sub_val in val_at.items():
                    cls.add_item(sub_cls, sub_key, sub_val)
        else:
            setattr(cls_at, key_at, val_at)


Theme.load()
