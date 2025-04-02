import customtkinter as ctk

from gui.style import Theme, create_dropdown_menu

__all__ = ["create_tab"]


def create_tab(master, app):
    MnbFile = ctk.CTkButton(master, text="Arquivo", width=100, height=40,
                            fg_color="transparent", hover_color="#3d424b", text_color=Theme.headline,
                            corner_radius=0)
    MnbFile.pack(side="left", fill="y")

    menu_arquivo_toggle = create_dropdown_menu(
        master_button=MnbFile,
        root_window=app,
        options=[
            ("Novo", lambda: print("Novo")),
            ("Abrir", lambda: print("Abrir")),
            ("---", None),
            ("Sair", app.quit)
        ],
        palette={
            "bg": master["bg"],
            "hover": "#3d424b",
            "text": Theme.headline
        }
    )

    MnbFile.configure(command=menu_arquivo_toggle)
