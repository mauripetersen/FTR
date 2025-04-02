from dataclasses import dataclass
import customtkinter as ctk
import json
import os

from config import FTR_NAME_0, themes_dir

__all__ = ["Theme", "FtrLabel", "FtrEntry", "FtrButton", "create_dropdown_menu", "configure_root"]


# region "Theme"
@dataclass
class DcCAD:
    background: str
    lines: str


@dataclass
class DcButton:
    fore: str
    hover: str
    border: str
    text: str


@dataclass
class DcEntry:
    fore: str
    hover: str
    border: str
    text: str


@dataclass
class DcIllustration:
    stroke: str
    main: str
    highlight: str
    secondary: str
    tertiary: str


@dataclass
class DcTheme:
    background: str
    headline: str
    paragraph: str
    CAD: DcCAD
    Button: DcButton
    Entry: DcEntry
    Illustration: DcIllustration


theme_path = os.path.join(themes_dir, "DarkMode.json")
with open(theme_path, 'r', encoding='utf-8') as f:
    raw = json.load(f)

Theme = DcTheme(
    background=raw["background"],
    headline=raw["headline"],
    paragraph=raw["paragraph"],
    CAD=DcCAD(**raw["CAD"]),
    Button=DcButton(**raw["Button"]),
    Entry=DcEntry(**raw["Entry"]),
    Illustration=DcIllustration(**raw["Illustration"])
)


# endregion


def FtrLabel(master, text, font_name="Cambria", font_height=14):
    return ctk.CTkLabel(
        master,
        text=text,
        fg=Theme.paragraph,
        bg=Theme.background,
        relief=ctk.FLAT,
        bd=0,
        font=(font_name, font_height)
    )


def FtrEntry(master, text="", font_name="Cambria", font_height=14):
    return ctk.CTkEntry(
        master,
        # text=text,
        fg=Theme.Entry.text,
        bg=Theme.Entry.fore,
        relief=ctk.FLAT,
        bd=0,
        font=(font_name, font_height)
    )


def FtrButton(master, text, command=None, font_name="Cambria", font_height=14):
    return ctk.CTkButton(
        master,
        text=text,
        command=command,
        fg=Theme.Button.text,
        bg=Theme.Button.fore,
        activebackground=Theme.Button.hover,
        relief=ctk.FLAT,
        bd=0,
        font=(font_name, font_height)
    )


def create_dropdown_menu(master_button, root_window, options, palette):
    """
    Cria um menu suspenso customizado abaixo de um botão.

    Parâmetros:
        master_button: o CTkButton que dispara o menu
        root_window: janela principal (normalmente o root)
        options: lista de tuplas (texto, função_callback)
        palette: dicionário com cores (ex: {"bg": "#1e1e2f", "hover": "#3d424b", "text": "#ffffff"})
    """
    menu_frame = ctk.CTkFrame(root_window, fg_color=palette["bg"], corner_radius=0)
    menu_frame.place_forget()

    for text, callback in options:
        if text == "---":
            ctk.CTkLabel(menu_frame, text="─" * 30, text_color=palette["text"]).pack(pady=2)
        else:
            btn = ctk.CTkButton(menu_frame, text=text,
                                command=callback,
                                fg_color="transparent",
                                hover_color=palette["hover"],
                                text_color=palette["text"],
                                font=ctk.CTkFont(size=13),
                                anchor="w")
            btn.pack(fill="x", padx=10, pady=2)

    def toggle():
        if menu_frame.winfo_ismapped():
            menu_frame.place_forget()
        else:
            x = master_button.winfo_rootx() - root_window.winfo_rootx()
            y = master_button.winfo_rooty() - root_window.winfo_rooty() + master_button.winfo_height()
            menu_frame.place(x=x, y=y)

    return toggle


def configure_root(root: ctk.CTk, title=FTR_NAME_0, fg_color=Theme.background, flat=False,
                   maximized=True, win_size=(1200, 800), min_size=(800, 600), max_size=(1920, 1080)):
    root.title(title)
    root.configure(fg_color=fg_color)
    root.overrideredirect(flat)  # flat UI

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
