from typing import NamedTuple
import tkinter as tk

from config import *

__all__ = ["configure_app", "Palette", "FtrLabel", "FtrEntry", "FtrButton"]


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
    background="#16161a",
    headline="#fffffe",
    paragraph="#94a1b2",
)


# endregion


def FtrLabel(master, text, font_name="Cambria", font_height=14):
    return tk.Label(
        master,
        text=text,
        fg=Palette.paragraph,
        bg=Palette.background,
        # activebackground="#0000ff",
        relief=tk.FLAT,
        bd=0,
        font=(font_name, font_height)
    )


def FtrEntry(master, text="", font_name="Cambria", font_height=14):
    return tk.Entry(
        master,
        # text=text,
        fg=Palette.Entry.text,
        bg=Palette.Entry.fore,
        relief=tk.FLAT,
        bd=0,
        font=(font_name, font_height)
    )


def FtrButton(master, text, command=None, font_name="Cambria", font_height=14):
    return tk.Button(
        master,
        text=text,
        command=command,
        fg=Palette.Button.text,
        bg=Palette.Button.fore,
        activebackground=Palette.Button.hover,
        relief=tk.FLAT,
        bd=0,
        font=(font_name, font_height)
    )


def configure_app(root: tk.Tk, wi, he, title=FTR_NAME, centered=True, bg=Palette.background):
    root.title(title)
    root.configure(bg=bg)

    if centered:
        screen_size = (root.winfo_screenwidth(), root.winfo_screenheight())
        pos_x = int((screen_size[0] - wi) / 2)
        pos_y = int((screen_size[1] - he) / 2)
        root.geometry(f"{wi}x{he}+{pos_x}+{pos_y}")
    else:
        root.geometry(f"{wi}x{he}")
