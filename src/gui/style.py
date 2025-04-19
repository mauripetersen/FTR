from dataclasses import dataclass
import customtkinter as ctk
import json
import os

from config import FTR_NAME_0, icon_dir, themes_dir

__all__ = ["Theme", "configure_TopLevel"]


# region "Theme"
@dataclass
class ThmTab:
    background: str
    text: str
    highlight: str
    menu: str
    secondary: str


@dataclass
class ThmSideBar:
    background: str
    text: str
    highlight: str


@dataclass
class ThmRibbon:
    background: str
    text: str
    highlight: str


@dataclass
class ThmStatusBar:
    background: str
    text: str
    highlight: str


@dataclass
class ThmCAD:
    background: str
    grid: list[str]
    select_rect: str
    spans: str
    nodes: list[str]
    supports: str
    loads: list[str]


@dataclass
class ThmTheme:
    background: str
    headline: str
    paragraph: str
    highlight: str
    secondary: str
    tertiary: str
    Tab: ThmTab
    SideBar: ThmSideBar
    Ribbon: ThmRibbon
    StatusBar: ThmStatusBar
    CAD: ThmCAD


theme_path = os.path.join(themes_dir, "DarkMode.json")
with open(theme_path, 'r', encoding='utf-8') as f:
    raw = json.load(f)

Theme = ThmTheme(
    background=raw["background"],
    headline=raw["headline"],
    paragraph=raw["paragraph"],
    highlight=raw["highlight"],
    secondary=raw["secondary"],
    tertiary=raw["tertiary"],
    Tab=ThmTab(**raw["Tab"]),
    SideBar=ThmSideBar(**raw["SideBar"]),
    Ribbon=ThmRibbon(**raw["Ribbon"]),
    StatusBar=ThmStatusBar(**raw["StatusBar"]),
    CAD=ThmCAD(**raw["CAD"])
)


# endregion


def configure_TopLevel(root: ctk.CTkToplevel, title=FTR_NAME_0, fg_color=Theme.background, flat=False,
                       maximized=True, win_size=(1200, 800), min_size=(800, 600), max_size=(1920, 1080)):
    root.title(title)
    root.configure(fg_color=fg_color)
    root.overrideredirect(flat)  # flat UI

    try:
        logo_path = os.path.normpath(os.path.join(icon_dir, "icon_x256.ico"))
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
