from dataclasses import dataclass
import customtkinter as ctk
import json
import os

from config import FTR_NAME_0, assets_dir, themes_dir

__all__ = ["Theme", "configure_TopLevel"]


# region "Theme"
@dataclass
class ThmCAD:
    background: str
    lines: str
    select_rect: str


@dataclass
class ThmButton:
    fore: str
    hover: str
    border: str
    text: str


@dataclass
class ThmEntry:
    fore: str
    hover: str
    border: str
    text: str


@dataclass
class ThmIllustration:
    stroke: str
    main: str
    highlight: str
    secondary: str
    tertiary: str


@dataclass
class ThmTheme:
    background: str
    dark_1: str
    dark_2: str
    headline: str
    paragraph: str
    CAD: ThmCAD
    Button: ThmButton
    Entry: ThmEntry
    Illustration: ThmIllustration


theme_path = os.path.join(themes_dir, "DarkMode.json")
with open(theme_path, 'r', encoding='utf-8') as f:
    raw = json.load(f)

Theme = ThmTheme(
    background=raw["background"],
    dark_1=raw["dark_1"],
    dark_2=raw["dark_2"],
    headline=raw["headline"],
    paragraph=raw["paragraph"],
    CAD=ThmCAD(**raw["CAD"]),
    Button=ThmButton(**raw["Button"]),
    Entry=ThmEntry(**raw["Entry"]),
    Illustration=ThmIllustration(**raw["Illustration"])
)


# endregion


def configure_TopLevel(root: ctk.CTkToplevel, title=FTR_NAME_0, fg_color=Theme.background, flat=False,
                       maximized=True, win_size=(1200, 800), min_size=(800, 600), max_size=(1920, 1080)):
    root.title(title)
    root.configure(fg_color=fg_color)
    root.overrideredirect(flat)  # flat UI

    try:
        logo_path = os.path.normpath(os.path.join(assets_dir, "icon/icon_x256.ico"))
        root.after(250, lambda: root.iconbitmap(logo_path))
    except Exception as e:
        print(f"Error: {e}")

    if maximized:
        root.minsize(*min_size)
        root.maxsize(*max_size)
        root.geometry(f"{win_size[0]}x{win_size[1]}")
        root.update()
        root.state("zoomed")
        root.focus_force()
    else:
        screen_size = (root.winfo_screenwidth(), root.winfo_screenheight())
        pos = (int((screen_size[0] - win_size[0]) / 2),
               int((screen_size[1] - win_size[1]) / 2))
        root.geometry(f"{win_size[0]}x{win_size[1]}+{pos[0]}+{pos[1]}")
        root.minsize(*win_size)
        root.maxsize(*win_size)
