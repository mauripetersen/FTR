import customtkinter as ctk

from gui.style import Theme

__all__ = ["create_tab"]


def create_tab(master, app):
    BtnFile = ctk.CTkButton(master, text="Arquivo",
                            fg_color="transparent", hover_color=Theme.Button.hover,
                            font=("Segoe UI", 14),
                            text_color=Theme.Button.text, corner_radius=0, width=80)
    BtnFile.pack(side="left", fill="y")

    MnuFile_toggle = create_dropdown_menu(
        master_button=BtnFile,
        app=app,
        options=[
            ("Novo Projeto", lambda: print("Novo projeto")),
            ("Abrir Projeto", lambda: print("Abrir projeto")),
            ("Salvar", lambda: print("Salvar")),
            ("---", None),
            ("Sair", app.quit)
        ]
    )
    BtnFile.configure(command=MnuFile_toggle)

    BtnTools = ctk.CTkButton(master, text="Ferramentas",
                             fg_color="transparent", hover_color=Theme.Button.hover,
                             font=("Segoe UI", 14),
                             text_color=Theme.Button.text, corner_radius=0, width=100)
    BtnTools.pack(side="left", fill="y")

    MnuTools_toggle = create_dropdown_menu(
        master_button=BtnTools,
        app=app,
        options=[
            ("Isostática", None),
            ("Hiperestática", None),
            ("Normas NBR", None)
        ]
    )
    BtnTools.configure(command=MnuTools_toggle)


def create_dropdown_menu(master_button: ctk.CTkButton, app: ctk.CTk, options: list[tuple[str, callable]]):
    """
    Creates a custom dropdown menu below a button.

    :param master_button: CTkButton that triggers the menu
    :param app: Main app
    :param options: Tuple list (text, callback_function)
    :return:
    """
    menu = ctk.CTkFrame(app, fg_color=Theme.background, corner_radius=4, border_width=0)
    menu.place_forget()

    for text, command in options:
        if text == "---":
            ctk.CTkLabel(menu, text="─" * 10, text_color=Theme.Illustration.tertiary, height=1).pack(pady=2)
        else:
            btn = ctk.CTkButton(menu, text=text, command=lambda cmd=command: [cmd(), menu.place_forget()],
                                font=("Segoe UI", 14),
                                fg_color="transparent", hover_color=Theme.Button.hover,
                                text_color=Theme.Button.text, anchor="w", corner_radius=0)
            btn.pack(fill="x", pady=3)

    def toggle_menu():
        if (app.active_menu and app.active_menu != menu) or not app.active_menu:
            if app.active_menu:
                app.active_menu.place_forget()
            x = master_button.winfo_rootx() - app.winfo_rootx()
            y = master_button.winfo_rooty() - app.winfo_rooty() + master_button.winfo_height()
            menu.place(x=x, y=y)
            menu.lift()
            app.bind_all("<Button-1>", hide_menu)
            app.bind_all("<Escape>", hide_menu)
            app.active_menu = menu
        else:
            hide_menu()

    # def click_outside(event):
    #     widget = event.widget
    #     if widget is master_button or str(widget).startswith(str(menu)):
    #         return  # clicou dentro do botão ou do menu → ignora
    #     hide_menu()

    def hide_menu(event=None):
        menu.place_forget()
        app.unbind_all("<Button-1>")
        app.unbind_all("<Escape>")
        app.active_menu = None

    return toggle_menu
