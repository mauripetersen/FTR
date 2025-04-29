import customtkinter as ctk

from gui.style import Theme
from manager.language import lang

__all__ = ["create_tab"]


def create_tab(app, master):
    master.active_menu = None

    BtnFile = ctk.CTkButton(master, text=lang.get('file'),
                            fg_color="transparent", hover_color=Theme.Tab.highlight,
                            font=("Segoe UI", 14),
                            text_color=Theme.Tab.text, corner_radius=0, width=80)
    BtnFile.pack(side="left", fill="y")

    MnuFile_toggle = create_dropdown_menu(
        app=app,
        master=master,
        master_button=BtnFile,
        options=[
            (lang.get('new_project'), lambda: print("Novo projeto")),
            (lang.get('open_project'), app.open_project),
            (lang.get('save_project'), lambda: print("Salvar Projeto")),
            ("---", None),
            (lang.get('exit'), app.confirm_close)
        ]
    )
    BtnFile.configure(command=MnuFile_toggle)

    BtnTools = ctk.CTkButton(master, text=lang.get('tools'),
                             fg_color="transparent", hover_color=Theme.Tab.highlight,
                             font=("Segoe UI", 14),
                             text_color=Theme.Tab.text, corner_radius=0, width=100)
    BtnTools.pack(side="left", fill="y")

    MnuTools_toggle = create_dropdown_menu(
        app=app,
        master=master,
        master_button=BtnTools,
        options=[
            ("Isostática", lambda: None),
            ("Hiperestática", lambda: None),
            ("Normas NBR", lambda: None)
        ]
    )
    BtnTools.configure(command=MnuTools_toggle)


def create_dropdown_menu(app: ctk.CTk,
                         master: ctk.CTkFrame,
                         master_button: ctk.CTkButton,
                         options: list[tuple[str, callable]]):
    """
    Creates a custom dropdown menu below a button.

    :param app: Main app
    :param master: CTkFrame that the button belongs
    :param master_button: CTkButton that triggers the menu
    :param options: Tuple list (text, callback_function)
    :return:
    """
    menu = ctk.CTkFrame(app, fg_color=Theme.Tab.menu, corner_radius=4, border_width=0)
    menu.place_forget()

    for text, command in options:
        if text == "---":
            ctk.CTkLabel(menu, text="─" * 10, text_color=Theme.Tab.secondary, height=1).pack(pady=2)
        else:
            btn = ctk.CTkButton(menu, text=text, command=lambda cmd=command: [cmd(), menu.place_forget()],
                                font=("Segoe UI", 14),
                                fg_color="transparent", hover_color=Theme.Tab.highlight,
                                text_color=Theme.Tab.text, anchor="w", corner_radius=0)
            btn.pack(fill="x", pady=3)

    def toggle_menu():
        if (master.active_menu and master.active_menu is not menu) or not master.active_menu:
            if master.active_menu:
                master.active_menu.place_forget()
            x = master_button.winfo_rootx() - app.winfo_rootx()
            y = master_button.winfo_rooty() - app.winfo_rooty() + master_button.winfo_height()

            menu.place(x=x, y=y)
            menu.lift()

            app.bind_all("<Button-1>", on_click)
            app.bind_all("<Escape>", hide_menu)

            master.active_menu = menu
        else:
            hide_menu()

    def on_click(event):
        obj = event.widget
        while type(obj) is not ctk.CTkFrame:
            obj = obj.master  # go to the master frame
        if str(obj) == str(master):
            return  # clicked in the tab frame
        hide_menu()

    def hide_menu(event=None):
        if master.active_menu:
            master.active_menu.place_forget()
            app.unbind_all("<Button-1>")
            app.unbind_all("<Escape>")
            master.active_menu = None

    return toggle_menu
