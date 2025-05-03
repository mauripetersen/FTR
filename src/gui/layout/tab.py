import customtkinter as ctk
import tkinter as tk

from config import Theme
from manager import Language

__all__ = ["Tab"]


class Tab(ctk.CTkFrame):
    def __init__(self, app, main_screen):
        super().__init__(main_screen, fg_color=Theme.Tab.background, corner_radius=0)
        self.app = app
        self.main_screen = main_screen

        self.active_menu = None

        # FILE:
        self.BtnFile = ctk.CTkButton(
            self, text=Language.get('MainScreen', 'Tab', 'File', 'file'),
            fg_color="transparent", hover_color=Theme.Tab.highlight,
            font=("Segoe UI", 14),
            text_color=Theme.Tab.text, corner_radius=0, width=0
        )
        self.BtnFile.pack(side="left", fill="y")
        self.update_idletasks()
        self.BtnFile.configure(width=self.BtnFile.winfo_reqwidth() + 40)

        self.MnuFile_toggle = self.create_dropdown_menu(
            master_button=self.BtnFile,
            options=[
                (Language.get('MainScreen', 'Tab', 'File', 'about_FTR'), lambda: print("I love flerkens!")),
                ("---", None),
                ((Language.get('MainScreen', 'Tab', 'File', 'new_project'), "(Ctrl+N)"), main_screen.new_project),
                ((Language.get('MainScreen', 'Tab', 'File', 'open_project'), "(Ctrl+O)"), main_screen.open_project),
                ((Language.get('MainScreen', 'Tab', 'File', 'save_project'), "(Ctrl+S)"), main_screen.save_project),
                (Language.get('MainScreen', 'Tab', 'File', 'save_as_project'),
                 lambda: main_screen.save_project(save_as=True)),
                ((Language.get('MainScreen', 'Tab', 'File', 'close_project'), "(Ctrl+W)"), main_screen.close_project),
                ("---", None),
                (Language.get('MainScreen', 'Tab', 'File', 'exit'), main_screen.on_close)
            ]
        )
        self.BtnFile.configure(command=self.MnuFile_toggle)

        # TOOLS:
        self.BtnTools = ctk.CTkButton(
            self, text=Language.get('MainScreen', 'Tab', 'Tools', 'tools'),
            fg_color="transparent", hover_color=Theme.Tab.highlight,
            font=("Segoe UI", 14),
            text_color=Theme.Tab.text, corner_radius=0, width=0
        )
        self.BtnTools.pack(side="left", fill="y")
        self.update_idletasks()
        self.BtnTools.configure(width=self.BtnTools.winfo_reqwidth() + 40)

        self.MnuTools_toggle = self.create_dropdown_menu(
            master_button=self.BtnTools,
            options=[
                (Language.get('MainScreen', 'Tab', 'Tools', 'flerken 1'), lambda: None),
                (Language.get('MainScreen', 'Tab', 'Tools', 'flerken 2'), lambda: None),
                (Language.get('MainScreen', 'Tab', 'Tools', 'flerken 3'), lambda: None)
            ]
        )
        self.BtnTools.configure(command=self.MnuTools_toggle)

        # OPTIONS:
        self.BtnOptions = ctk.CTkButton(
            self, text=Language.get('MainScreen', 'Tab', 'Options', 'options'),
            fg_color="transparent", hover_color=Theme.Tab.highlight,
            font=("Segoe UI", 14),
            text_color=Theme.Tab.text, corner_radius=0, width=0
        )
        self.BtnOptions.pack(side="left", fill="y")
        self.update_idletasks()
        self.BtnOptions.configure(width=self.BtnOptions.winfo_reqwidth() + 40)

        self.MnuOptions_toggle = self.create_dropdown_menu(
            master_button=self.BtnOptions,
            options=[
                (Language.get('MainScreen', 'Tab', 'Options', 'settings'), app.open_settings),
                ("Item 2", lambda: None),
                ("Item 3", lambda: None)
            ]
        )
        self.BtnOptions.configure(command=self.MnuOptions_toggle)

    def create_dropdown_menu(
            self,
            master_button: ctk.CTkButton,
            options: list[tuple[str | tuple[str, str], callable]],
            width: int = 200
    ):
        """
        Creates a custom dropdown menu below a button.

        :param master_button: CTkButton that triggers the menu
        :param options: Tuple list (text, callback_function)
        :param width: Dropdown menu width
        :return: Nothing
        """
        menu = ctk.CTkFrame(self.main_screen, fg_color=Theme.Tab.menu, corner_radius=4, border_width=0)
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
            if (self.active_menu and self.active_menu is not menu) or not self.active_menu:
                if self.active_menu:
                    self.active_menu.place_forget()
                x = master_button.winfo_rootx() - self.main_screen.winfo_rootx()
                y = master_button.winfo_rooty() - self.main_screen.winfo_rooty() + master_button.winfo_height()

                menu.place(x=x, y=y)
                menu.lift()

                height = menu.winfo_reqheight()
                menu.pack_propagate(False)
                menu.configure(width=width)
                menu.configure(height=height)

                self.main_screen.bind_all("<Button-1>", on_click)
                self.main_screen.bind_all("<Escape>", hide_menu)

                self.active_menu = menu
            else:
                hide_menu()

        def on_click(event):
            obj = event.widget
            while not isinstance(obj, ctk.CTkFrame):
                obj = obj.master  # go to the master frame
            if str(obj) == str(self):
                return  # clicked in the tab frame
            hide_menu()

        def hide_menu(event=None):
            if self.active_menu:
                self.active_menu.place_forget()
                self.main_screen.unbind_all("<Button-1>")
                self.main_screen.unbind_all("<Escape>")
                self.active_menu = None

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
