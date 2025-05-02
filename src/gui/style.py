import customtkinter as ctk
import os

from config import Settings, Theme

__all__ = ["configure_TopLevel"]


def configure_TopLevel(root: ctk.CTkToplevel, title=Settings.FTR_NAME[0], fg_color=Theme.background, flat=False,
                       maximized=True, win_size=(1200, 800), min_size=(800, 600), max_size=(1920, 1080)):
    root.title(title)
    root.configure(fg_color=fg_color)
    root.overrideredirect(flat)  # flat UI

    try:
        logo_path = os.path.normpath(os.path.join(Settings.ICONS_DIR, "icon_x256.ico"))
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
