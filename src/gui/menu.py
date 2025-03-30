import tkinter as tk

from config import *
from gui.style import *


class MainMenu:
    def __init__(self, root: tk.Tk):
        root.overrideredirect(False)
        root.state("zoomed")

        FtrLabel(root, text="Menu Principal").pack(pady=20)
        FtrButton(root, text="Novo Projeto", command=lambda: print("Novo")).pack(pady=10)
        FtrButton(root, text="Sair", command=root.quit).pack(pady=10)


class VigaApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title(FTR_NAME)

        window_size = (800, 500)
        screen_size = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())

        pos_x = int((screen_size[0] - window_size[0]) / 2)
        pos_y = int((screen_size[1] - window_size[1]) / 2)

        # Tamanho da janela
        self.root.geometry(f"{window_size[0]}x{window_size[1]}+{pos_x}+{pos_y}")

        # Título
        self.label_titulo = FtrLabel(root, text="Insira os dados da viga")
        self.label_titulo.pack(pady=10)

        # Vão
        self.label_comprimento = FtrLabel(root, text="Comprimento da viga (m):")
        self.label_comprimento.pack()
        self.entry_comprimento = FtrEntry(root)
        self.entry_comprimento.pack(pady=5)

        # Carga
        self.label_carga = FtrLabel(root, text="Carga (kN):")
        self.label_carga.pack()
        self.entry_carga = FtrEntry(root)
        self.entry_carga.pack(pady=5)

        # Momento
        self.label_momento = FtrLabel(root, text="Momento (kN.m):")
        self.label_momento.pack()
        self.entry_momento = FtrEntry(root)
        self.entry_momento.pack(pady=5)

        # Botão
        self.btn_processar = FtrButton(root, text="Calcular", command=self.processar_dados)
        self.btn_processar.pack(pady=20)

    def processar_dados(self):
        comprimento = self.entry_comprimento.get()
        carga = self.entry_carga.get()
        momento = self.entry_momento.get()

        # Aqui você pode passar os dados para o cálculo (módulo calculos.py)
        print(f"Comprimento: {comprimento} m, Carga: {carga} kN, Momento: {momento} kN.m")
        # Em seguida, você pode usar esses dados em funções de cálculos que estarão no módulo `calculos.py`.
