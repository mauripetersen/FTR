import customtkinter as ctk

from config import *
from gui.style import *

__all__ = ["CADInterface"]


class CADInterface:
    def __init__(self, root: ctk.CTk):
        self.root = root
        configure_root(self.root)

        self.FrmTabMenu = ctk.CTkFrame(root, bg_color="#101214")
        # self.FrmTabMenu.pack_propagate(False)
        self.FrmTabMenu.pack(side="top", fill="x")

        self.FrmSide = ctk.CTkFrame(root, bg_color="#21252b", width=150)
        self.FrmSide.pack(side="left", fill="y")

        self.FrmRibbon = ctk.CTkFrame(root, bg_color="yellow", height=40)
        self.FrmRibbon.pack(side="top", fill="x")

        self.FrmStatusBar = ctk.CTkFrame(root, bg_color="green", height=30)
        self.FrmStatusBar.pack(side="bottom", fill="x")

        MnbFile = ctk.CTkButton(self.FrmTabMenu, text="Arquivo", width=100, height=40,
                                fg_color="transparent", hover_color="#3d424b", text_color=Palette.headline,
                                corner_radius=0)
        MnbFile.pack(side="left", fill="y")

        menu_arquivo_toggle = create_dropdown_menu(
            master_button=MnbFile,
            root_window=self.root,
            options=[
                ("Novo", lambda: print("Novo")),
                ("Abrir", lambda: print("Abrir")),
                ("---", None),
                ("Sair", self.root.quit)
            ],
            palette={
                "bg": self.FrmTabMenu["bg"],
                "hover": "#3d424b",
                "text": Palette.headline
            }
        )

        MnbFile.configure(command=menu_arquivo_toggle)

        # # Título
        # self.label_titulo = FtrLabel(root, text="Insira os dados da viga")
        # self.label_titulo.pack(pady=10)
        #
        # # Vão
        # self.label_comprimento = FtrLabel(root, text="Comprimento da viga (m):")
        # self.label_comprimento.pack()
        # self.entry_comprimento = FtrEntry(root)
        # self.entry_comprimento.pack(pady=5)
        #
        # # Carga
        # self.label_carga = FtrLabel(root, text="Carga (kN):")
        # self.label_carga.pack()
        # self.entry_carga = FtrEntry(root)
        # self.entry_carga.pack(pady=5)
        #
        # # Momento
        # self.label_momento = FtrLabel(root, text="Momento (kN.m):")
        # self.label_momento.pack()
        # self.entry_momento = FtrEntry(root)
        # self.entry_momento.pack(pady=5)
        #
        # # Botão
        # self.btn_processar = FtrButton(root, text="Calcular", command=self.processar_dados)
        # self.btn_processar.pack(pady=20)
        #
        # # Canvas para desenhar
        # self.canvas = tk.Canvas(self.root, width=600, height=400)
        # self.canvas.pack()
        #
        # # Variáveis para armazenar as coordenadas
        # self.start_x = None
        # self.start_y = None
        #
        # # Adicionar eventos de clique e arrasto
        # self.canvas.bind("<Button-1>", self.on_click)
        # self.canvas.bind("<B1-Motion>", self.on_drag)
        #
        # # Modo de adicionar carga
        # self.adding_load = False
        # self.canvas.bind("<Button-3>", self.toggle_add_load)

    def processar_dados(self):
        comprimento = self.entry_comprimento.get()
        carga = self.entry_carga.get()
        momento = self.entry_momento.get()

        # Aqui você pode passar os dados para o cálculo (módulo calculos.py)
        print(f"Comprimento: {comprimento} m, Carga: {carga} kN, Momento: {momento} kN.m")
        # Em seguida, você pode usar esses dados em funções de cálculos que estarão no módulo `calculos.py`.

    def on_click(self, event):
        if not self.start_x and not self.start_y:
            # Início do desenho da viga
            self.start_x = event.x
            self.start_y = event.y
        else:
            # Desenha a viga
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, width=2, fill="black")
            self.start_x, self.start_y = None, None

    def on_drag(self, event):
        if self.start_x and self.start_y:
            # Atualiza o desenho da viga enquanto o mouse é movido
            self.canvas.delete("temp_line")  # Remove a linha temporária anterior
            self.canvas.create_line(self.start_x, self.start_y, event.x, event.y, width=2, fill="black",
                                    tags="temp_line")

    def toggle_add_load(self, event):
        # Alterna o modo de adicionar cargas
        self.adding_load = not self.adding_load
        if self.adding_load:
            print("Modo de adicionar carga ativado")
        else:
            print("Modo de adicionar carga desativado")

    def add_load(self, event):
        if self.adding_load:
            # Adiciona uma carga (por exemplo, um círculo)
            self.canvas.create_oval(event.x - 5, event.y - 5, event.x + 5, event.y + 5, fill="red", tags="load")
