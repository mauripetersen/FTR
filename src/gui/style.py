from typing import NamedTuple
import customtkinter as ctk
import json
import os

from config import *

__all__ = ["Palette", "FtrLabel", "FtrEntry", "FtrButton", "create_dropdown_menu", "configure_root"]

# region "Palette"
palette_path = os.path.join(themes_dir, "palettes.json")

with open(palette_path, "r") as f:
    data = json.load(f)


def extract_key_values(d, parent_key='', result=None):
    if result is None:
        result = []

    for key, value in d.items():
        full_key = f"{parent_key}.{key}" if parent_key else key
        if isinstance(value, dict):
            extract_key_values(value, full_key, result)
        else:
            result.append((full_key, value))

    return result


i_result = extract_key_values(data)

with open("output.txt", "w") as f:
    for k, v in i_result:
        f.write(f"{k} = {v}\n")


# endregion


# region "Palette"
class EntryPalette(NamedTuple):
    fore: str
    hover: str
    border: str
    text: str


class ButtonPalette(NamedTuple):
    fore: str
    hover: str
    border: str
    text: str


class IllustrationPalette(NamedTuple):
    stroke: str
    main: str
    highlight: str
    secondary: str
    tertiary: str


class Palette(NamedTuple):
    Entry: EntryPalette
    Button: ButtonPalette
    Illustration: IllustrationPalette
    background: str
    headline: str
    paragraph: str


Palette = Palette(
    EntryPalette(
        fore="#fffffe",
        hover="#cccccb",
        border="#010101",
        text="#000000"
    ),
    ButtonPalette(
        fore="#7f5af0",
        hover="#5e43b3",
        border="#433080",
        text="#fffffe"
    ),
    IllustrationPalette(
        stroke="#010101",
        main="#fffffe",
        highlight="#7f5af0",
        secondary="#72757e",
        tertiary="#2cb67d",
    ),
    background="#242424",
    # backgroundCAD="#16161a",
    headline="#fffffe",
    paragraph="#94a1b2",
)


# endregion


def FtrLabel(master, text, font_name="Cambria", font_height=14):
    return ctk.CTkLabel(
        master,
        text=text,
        fg=Palette.paragraph,
        bg=Palette.background,
        relief=ctk.FLAT,
        bd=0,
        font=(font_name, font_height)
    )


def FtrEntry(master, text="", font_name="Cambria", font_height=14):
    return ctk.CTkEntry(
        master,
        # text=text,
        fg=Palette.Entry.text,
        bg=Palette.Entry.fore,
        relief=ctk.FLAT,
        bd=0,
        font=(font_name, font_height)
    )


def FtrButton(master, text, command=None, font_name="Cambria", font_height=14):
    return ctk.CTkButton(
        master,
        text=text,
        command=command,
        fg=Palette.Button.text,
        bg=Palette.Button.fore,
        activebackground=Palette.Button.hover,
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


def configure_root(root: ctk.CTk, title=FTR_NAME, fg_color=Palette.background, flat=False,
                   maximized=True, win_size=(1200, 800), min_size=(800, 600), max_size=(1920, 1080), centered=True):
    root.title(title)
    root.configure(fg_color=fg_color)
    root.overrideredirect(flat)  # flat UI

    if maximized:
        root.minsize(*min_size)
        root.maxsize(*max_size)
        root.geometry(f"{win_size[0]}x{win_size[1]}")
        root.update()
        root.state("zoomed")
    else:
        if centered:
            screen_size = (root.winfo_screenwidth(), root.winfo_screenheight())
            pos = (int((screen_size[0] - win_size[0]) / 2),
                   int((screen_size[1] - win_size[1]) / 2))
            root.geometry(f"{win_size[0]}x{win_size[1]}+{pos[0]}+{pos[1]}")
        else:
            root.geometry(f"{win_size[0]}x{win_size[1]}")
        root.minsize(*win_size)
        root.maxsize(*win_size)
