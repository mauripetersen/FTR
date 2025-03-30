import tkinter as tk


class VigaApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Tractus Ferri - Ferramenta de Cálculo de Vigas Contínuas e Hiperestáticas")

        window_size = (800, 500)
        screen_size = (self.master.winfo_screenwidth(), self.master.winfo_screenheight())

        pos_x = int((screen_size[0] - window_size[0]) / 2)
        pos_y = int((screen_size[1] - window_size[1]) / 2)

        # Tamanho da janela
        self.master.geometry(f"{window_size[0]}x{window_size[1]}+{pos_x}+{pos_y}")

        # Título
        self.label_titulo = tk.Label(master, text="Insira os dados da viga", font=("Cambria", 18))
        self.label_titulo.pack(pady=10)

        # Vão
        self.label_comprimento = tk.Label(master, text="Comprimento da viga (m):", font=("Cambria", 12))
        self.label_comprimento.pack()
        self.entry_comprimento = tk.Entry(master)
        self.entry_comprimento.pack(pady=5)

        # Carga
        self.label_carga = tk.Label(master, text="Carga (kN):", font=("Cambria", 12))
        self.label_carga.pack()
        self.entry_carga = tk.Entry(master)
        self.entry_carga.pack(pady=5)

        # Momento
        self.label_momento = tk.Label(master, text="Momento (kN.m):", font=("Cambria", 12))
        self.label_momento.pack()
        self.entry_momento = tk.Entry(master)
        self.entry_momento.pack(pady=5)

        # Botão
        self.btn_processar = tk.Button(master, text="Calcular", command=self.processar_dados, font=("Cambria", 12))
        self.btn_processar.pack(pady=20)

    def processar_dados(self):
        comprimento = self.entry_comprimento.get()
        carga = self.entry_carga.get()
        momento = self.entry_momento.get()

        # Aqui você pode passar os dados para o cálculo (módulo calculos.py)
        print(f"Comprimento: {comprimento} m, Carga: {carga} kN, Momento: {momento} kN.m")
        # Em seguida, você pode usar esses dados em funções de cálculos que estarão no módulo `calculos.py`.


if __name__ == "__main__":
    root = tk.Tk()
    app = VigaApp(root)
    root.mainloop()
