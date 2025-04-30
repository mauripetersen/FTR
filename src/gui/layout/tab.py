import customtkinter as ctk
import tkinter as tk

from gui.style import Theme
from manager.language import lang

__all__ = ["create_tab"]


def create_tab(app, main_screen, master_frame):
    master_frame.active_menu = None

    # FILE:
    BtnFile = ctk.CTkButton(master_frame, text=lang.get('file'),
                            fg_color="transparent", hover_color=Theme.Tab.highlight,
                            font=("Segoe UI", 14),
                            text_color=Theme.Tab.text, corner_radius=0, width=80)
    BtnFile.pack(side="left", fill="y")

    MnuFile_toggle = create_dropdown_menu(
        main_screen=main_screen,
        master_frame=master_frame,
        master_button=BtnFile,
        options=[
            (lang.get('about_FTR'), lambda: print("I love flerkens!")),
            ("---", None),
            ((lang.get('new_project'), "(Ctrl+N)"), main_screen.new_project),
            ((lang.get('open_project'), "(Ctrl+O)"), main_screen.open_project),
            ((lang.get('save_project'), "(Ctrl+S)"), main_screen.save_project),
            (lang.get('save_as_project'), lambda: main_screen.save_project(save_as=True)),
            ((lang.get('close_project'), "(Ctrl+W)"), main_screen.close_project),
            ("---", None),
            (lang.get('exit'), main_screen.on_close)
        ]
    )
    BtnFile.configure(command=MnuFile_toggle)

    # TOOLS:
    BtnTools = ctk.CTkButton(master_frame, text=lang.get('tools'),
                             fg_color="transparent", hover_color=Theme.Tab.highlight,
                             font=("Segoe UI", 14),
                             text_color=Theme.Tab.text, corner_radius=0, width=100)
    BtnTools.pack(side="left", fill="y")

    MnuTools_toggle = create_dropdown_menu(
        main_screen=main_screen,
        master_frame=master_frame,
        master_button=BtnTools,
        options=[
            ("Isostática", lambda: None),
            ("Hiperestática", lambda: None),
            ("Normas NBR", lambda: None)
        ]
    )
    BtnTools.configure(command=MnuTools_toggle)

    # OPTIONS:
    BtnOptions = ctk.CTkButton(master_frame, text=lang.get('options'),
                               fg_color="transparent", hover_color=Theme.Tab.highlight,
                               font=("Segoe UI", 14),
                               text_color=Theme.Tab.text, corner_radius=0, width=100)
    BtnOptions.pack(side="left", fill="y")

    MnuOptions_toggle = create_dropdown_menu(
        main_screen=main_screen,
        master_frame=master_frame,
        master_button=BtnOptions,
        options=[
            ((lang.get('language'), ">"), lambda: None),
            ("Item 2", lambda: None),
            ("Item 3", lambda: None)
        ]
    )
    BtnOptions.configure(command=MnuOptions_toggle)


def create_dropdown_menu(main_screen: ctk.CTkToplevel,
                         master_frame: ctk.CTkFrame,
                         master_button: ctk.CTkButton,
                         options: list[tuple[str | tuple[str, str], callable]],
                         width: int = 200):
    """
    Creates a custom dropdown menu below a button.

    :param main_screen: MainScreen
    :param master_frame: CTkFrame that the button belongs
    :param master_button: CTkButton that triggers the menu
    :param options: Tuple list (text, callback_function)
    :param width: Dropdown menu width
    :return: Nothing
    """
    menu = ctk.CTkFrame(main_screen, fg_color=Theme.Tab.menu, corner_radius=4, border_width=0)
    menu.place_forget()

    for text, command in options:
        if text == "---":
            sep = tk.Canvas(menu, bg=Theme.Tab.secondary, highlightthickness=0, height=2)
            sep.pack(fill="x", expand=True)
        else:
            btn = DualTextButton(menu, text=text, command=lambda cmd=command: [menu.place_forget(), cmd()],
                                 font=("Segoe UI", 14), fg_color="transparent", hover_color=Theme.Tab.highlight,
                                 text_color=Theme.Tab.text, corner_radius=0)
            btn.pack(fill="x", expand=True, pady=0)

    def toggle_menu():
        if (master_frame.active_menu and master_frame.active_menu is not menu) or not master_frame.active_menu:
            if master_frame.active_menu:
                master_frame.active_menu.place_forget()
            x = master_button.winfo_rootx() - main_screen.winfo_rootx()
            y = master_button.winfo_rooty() - main_screen.winfo_rooty() + master_button.winfo_height()

            menu.place(x=x, y=y)
            menu.lift()

            height = menu.winfo_reqheight()
            menu.pack_propagate(False)
            menu.configure(width=width)
            menu.configure(height=height)

            main_screen.bind_all("<Button-1>", on_click)
            main_screen.bind_all("<Escape>", hide_menu)

            master_frame.active_menu = menu
        else:
            hide_menu()

    def on_click(event):
        obj = event.widget
        while type(obj) is not ctk.CTkFrame:
            obj = obj.master  # go to the master frame
        if str(obj) == str(master_frame):
            return  # clicked in the tab frame
        hide_menu()

    def hide_menu(event=None):
        if master_frame.active_menu:
            master_frame.active_menu.place_forget()
            main_screen.unbind_all("<Button-1>")
            main_screen.unbind_all("<Escape>")
            master_frame.active_menu = None

    return toggle_menu


class DualTextButton(ctk.CTkFrame):
    def __init__(self, master, text, command, font, fg_color, hover_color, text_color, corner_radius):
        super().__init__(master, fg_color=fg_color, corner_radius=corner_radius)
        self.command = command
        self.fg_color = fg_color
        self.hover_color = hover_color

        self.configure(cursor="hand2")

        inner = ctk.CTkFrame(self, fg_color=fg_color)
        inner.pack(fill="both", expand=True)

        widgets = [self, inner]
        if isinstance(text, tuple):
            self.left_label = ctk.CTkLabel(inner, text=text[0], anchor="w", font=font, text_color=text_color)
            self.left_label.pack(side="left", fill="x", expand=True, padx=5, pady=2)
            widgets.append(self.left_label)

            self.right_label = ctk.CTkLabel(inner, text=text[1], anchor="e", font=font, text_color=text_color)
            self.right_label.pack(side="right", fill="x", expand=True, padx=5, pady=2)
            widgets.append(self.right_label)
        else:
            self.left_label = ctk.CTkLabel(inner, text=text, anchor="w", font=font, text_color=text_color)
            self.left_label.pack(side="left", fill="x", expand=True, padx=5, pady=2)
            widgets.append(self.left_label)

        for widget in widgets:
            widget.bind("<Button-1>", self.on_click)
            widget.bind("<Enter>", self.on_enter)
            widget.bind("<Leave>", self.on_leave)

    def on_click(self, event):
        if self.command:
            self.command()

    def on_enter(self, event):
        self.configure(fg_color=self.hover_color)

    def on_leave(self, event):
        self.configure(fg_color=self.fg_color)
