import tkinter as tk
from config import *
from style import *


def obter_dados_viga():
    viga = {
        'comprimento': 10,  # Exemplo de viga de 10 metros
        'cargas': [(5, 100), (7, 150)],  # Exemplo: carga de 100 kN na posição 5m e 150 kN em 7m
        # Adicione outros dados conforme necessário
    }
    return viga


class VigaApp:
    def __init__(self, root):
        self.root = root
        self.root.title(FTR_NAME)

        window_size = (800, 500)
        screen_size = (self.root.winfo_screenwidth(), self.root.winfo_screenheight())

        pos_x = int((screen_size[0] - window_size[0]) / 2)
        pos_y = int((screen_size[1] - window_size[1]) / 2)

        # Tamanho da janela
        self.root.geometry(f"{window_size[0]}x{window_size[1]}+{pos_x}+{pos_y}")

        # Título
        self.label_titulo = FtrLabel(root, text="Insira os dados da viga", font_height=24)
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
        self.btn_processar = FtrButton(root, text="Calcular", command=self.processar_dados, font_height=18)
        self.btn_processar.pack(pady=20)

    def processar_dados(self):
        comprimento = self.entry_comprimento.get()
        carga = self.entry_carga.get()
        momento = self.entry_momento.get()

        # Aqui você pode passar os dados para o cálculo (módulo calculos.py)
        print(f"Comprimento: {comprimento} m, Carga: {carga} kN, Momento: {momento} kN.m")
        # Em seguida, você pode usar esses dados em funções de cálculos que estarão no módulo `calculos.py`.


# Criar a janela principal
root = tk.Tk()
root.configure(bg=Palette.background)

app = VigaApp(root)

root.mainloop()
