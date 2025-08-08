import pandas as pd
import tkinter as tk
from tkinter import filedialog, messagebox, font, colorchooser, ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class AppInterativo:
    def __init__(self, root):
        self.root = root
        root.title("Histograma Interativo com Pré-visualização")
        root.geometry("1100x900")
        root.minsize(900, 700)

        self.df = None
        self.variaveis = []
        self.coluna_valores = None
        self.cor_histograma = "#1f77b4"  # azul padrão matplotlib

        style = ttk.Style()
        style.theme_use('clam')

        frame_controles = ttk.Frame(root)
        frame_controles.grid(row=0, column=0, sticky="nswe", padx=10, pady=10)
        frame_controles.grid_rowconfigure(4, weight=1)

        frame_grafico = ttk.LabelFrame(root, text="Visualização dos Histogramas")
        frame_grafico.grid(row=0, column=1, sticky="nswe", padx=10, pady=10)

        root.grid_columnconfigure(0, weight=0)
        root.grid_columnconfigure(1, weight=1)
        root.grid_rowconfigure(0, weight=1)

        frame_arquivo = ttk.LabelFrame(frame_controles, text="Arquivo e Coluna")
        frame_arquivo.grid(row=0, column=0, sticky="ew", pady=(0,15))

        ttk.Label(frame_arquivo, text="Arquivo Excel:").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entrada_arquivo = ttk.Entry(frame_arquivo, width=45)
        self.entrada_arquivo.grid(row=0, column=1, padx=5, pady=5)
        btn_procurar = ttk.Button(frame_arquivo, text="Procurar", command=self.selecionar_arquivo)
        btn_procurar.grid(row=0, column=2, padx=5, pady=5)

        ttk.Label(frame_arquivo, text="Coluna de valores:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.frame_coluna_valores = ttk.Frame(frame_arquivo)
        self.frame_coluna_valores.grid(row=1, column=1, sticky="w", padx=5, pady=5)

        btn_carregar = ttk.Button(frame_arquivo, text="Carregar colunas", command=self.carregar_colunas)
        btn_carregar.grid(row=1, column=2, padx=5, pady=5)

        frame_limites = ttk.LabelFrame(frame_controles, text="Limites dos Eixos (para todos)")
        frame_limites.grid(row=1, column=0, sticky="ew", pady=(0,15))

        ttk.Label(frame_limites, text="X min:").grid(row=0, column=0, sticky="e", padx=2, pady=2)
        self.x_min_entry = ttk.Entry(frame_limites, width=6)
        self.x_min_entry.grid(row=0, column=1, padx=2, pady=2)
        self.x_min_entry.insert(0, "0")

        ttk.Label(frame_limites, text="X max:").grid(row=0, column=2, sticky="e", padx=2, pady=2)
        self.x_max_entry = ttk.Entry(frame_limites, width=6)
        self.x_max_entry.grid(row=0, column=3, padx=2, pady=2)
        self.x_max_entry.insert(0, "80")

        ttk.Label(frame_limites, text="Y min:").grid(row=1, column=0, sticky="e", padx=2, pady=2)
        self.y_min_entry = ttk.Entry(frame_limites, width=6)
        self.y_min_entry.grid(row=1, column=1, padx=2, pady=2)
        self.y_min_entry.insert(0, "0")

        ttk.Label(frame_limites, text="Y max:").grid(row=1, column=2, sticky="e", padx=2, pady=2)
        self.y_max_entry = ttk.Entry(frame_limites, width=6)
        self.y_max_entry.grid(row=1, column=3, padx=2, pady=2)
        self.y_max_entry.insert(0, "100")

        for e in [self.x_min_entry, self.x_max_entry, self.y_min_entry, self.y_max_entry]:
            e.bind("<KeyRelease>", self.atualizar_grafico)

        frame_textos = ttk.LabelFrame(frame_controles, text="Textos e Fontes")
        frame_textos.grid(row=2, column=0, sticky="ew", pady=(0,15))

        ttk.Label(frame_textos, text="Texto eixo X (todos):").grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entrada_eixo_x = ttk.Entry(frame_textos, width=35)
        self.entrada_eixo_x.grid(row=0, column=1, padx=5, pady=5)
        self.entrada_eixo_x.insert(0, "")
        self.entrada_eixo_x.bind("<KeyRelease>", self.atualizar_grafico)

        fontes_disponiveis = list(font.families())
        fontes_disponiveis.sort()

        ttk.Label(frame_textos, text="Fonte do Título:").grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.fonte_titulo = tk.StringVar(value="Arial")
        fonte_titulo_cb = ttk.Combobox(frame_textos, textvariable=self.fonte_titulo, values=fontes_disponiveis, state="readonly", width=32)
        fonte_titulo_cb.grid(row=1, column=1, padx=5, pady=5)
        fonte_titulo_cb.bind("<<ComboboxSelected>>", lambda e: self.atualizar_grafico())

        ttk.Label(frame_textos, text="Tamanho Fonte Título:").grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.tam_fonte_titulo = tk.IntVar(value=14)
        tamanho_titulo_spin = ttk.Spinbox(frame_textos, from_=8, to=30, width=6, textvariable=self.tam_fonte_titulo)
        tamanho_titulo_spin.grid(row=2, column=1, padx=5, pady=5, sticky="w")
        tamanho_titulo_spin.bind("<KeyRelease>", self.atualizar_grafico)
        tamanho_titulo_spin.bind("<<Increment>>", self.atualizar_grafico)
        tamanho_titulo_spin.bind("<<Decrement>>", self.atualizar_grafico)

        ttk.Label(frame_textos, text="Fonte do Eixo X:").grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.fonte_x = tk.StringVar(value="Arial")
        fonte_x_cb = ttk.Combobox(frame_textos, textvariable=self.fonte_x, values=fontes_disponiveis, state="readonly", width=32)
        fonte_x_cb.grid(row=3, column=1, padx=5, pady=5)
        fonte_x_cb.bind("<<ComboboxSelected>>", lambda e: self.atualizar_grafico())

        ttk.Label(frame_textos, text="Tamanho Fonte Eixo X:").grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.tam_fonte_x = tk.IntVar(value=12)
        tamanho_x_spin = ttk.Spinbox(frame_textos, from_=8, to=30, width=6, textvariable=self.tam_fonte_x)
        tamanho_x_spin.grid(row=4, column=1, padx=5, pady=5, sticky="w")
        tamanho_x_spin.bind("<KeyRelease>", self.atualizar_grafico)
        tamanho_x_spin.bind("<<Increment>>", self.atualizar_grafico)
        tamanho_x_spin.bind("<<Decrement>>", self.atualizar_grafico)

        frame_botoes = ttk.Frame(frame_controles)
        frame_botoes.grid(row=3, column=0, sticky="ew", pady=10)

        btn_cor = ttk.Button(frame_botoes, text="Selecionar Cor do Histograma", command=self.selecionar_cor)
        btn_cor.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        btn_salvar = ttk.Button(frame_botoes, text="Salvar Gráficos", command=self.salvar_graficos)
        btn_salvar.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        frame_botoes.grid_columnconfigure(0, weight=1)
        frame_botoes.grid_columnconfigure(1, weight=1)

        self.fig, self.axs = plt.subplots(2, 2, figsize=(10, 12))
        plt.subplots_adjust(hspace=0.8, wspace=0.3)

        self.canvas = FigureCanvasTkAgg(self.fig, master=frame_grafico)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)

        frame_grafico.grid_rowconfigure(0, weight=1)
        frame_grafico.grid_columnconfigure(0, weight=1)

        root.grid_rowconfigure(0, weight=1)
        root.grid_columnconfigure(1, weight=1)

    def selecionar_arquivo(self):
        caminho = filedialog.askopenfilename(
            title="Selecione o arquivo Excel",
            filetypes=[("Arquivos Excel", "*.xlsx *.xls")]
        )
        if caminho:
            self.entrada_arquivo.delete(0, tk.END)
            self.entrada_arquivo.insert(0, caminho)
            for widget in self.frame_coluna_valores.winfo_children():
                widget.destroy()
            self.df = None
            self.variaveis = []
            self.coluna_valores = None
            self.atualizar_grafico()

    def carregar_colunas(self):
        arquivo = self.entrada_arquivo.get()
        if not arquivo:
            messagebox.showerror("Erro", "Selecione um arquivo Excel.")
            return
        try:
            self.df = pd.read_excel(arquivo)
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar o arquivo:\n{e}")
            return

        for widget in self.frame_coluna_valores.winfo_children():
            widget.destroy()

        ttk.Label(self.frame_coluna_valores, text="Selecione a coluna de valores:").pack(side=tk.LEFT)

        colunas = list(self.df.columns)
        self.combo_coluna = ttk.Combobox(self.frame_coluna_valores, values=colunas, state="readonly", width=30)
        self.combo_coluna.pack(side=tk.LEFT, padx=5)
        self.combo_coluna.bind("<<ComboboxSelected>>", self.coluna_selecionada)

        self.coluna_valores = None

    def coluna_selecionada(self, event):
        coluna_nome = self.combo_coluna.get()
        if coluna_nome not in self.df.columns:
            messagebox.showerror("Erro", "Coluna inválida selecionada.")
            return

        self.coluna_valores = self.df.columns.get_loc(coluna_nome)
        self.carregar_variaveis()

    def carregar_variaveis(self):
        if self.df is None or self.coluna_valores is None:
            return

        self.variaveis = self.df.iloc[:, 0].unique()
        if len(self.variaveis) > 4:
            messagebox.showinfo("Aviso", "Mais de 4 variáveis encontradas, serão usados apenas os primeiros 4.")
        self.variaveis = self.variaveis[:4]

        self.atualizar_grafico()

    def selecionar_cor(self):
        cor = colorchooser.askcolor(color=self.cor_histograma, title="Escolha a cor do histograma")
        if cor[1] is not None:
            self.cor_histograma = cor[1]
            self.atualizar_grafico()

    def atualizar_grafico(self, event=None):
        if self.df is None or self.coluna_valores is None:
            for ax in self.axs.flatten():
                ax.clear()
            self.canvas.draw()
            return

        valores = self.df.iloc[:, self.coluna_valores]

        for ax in self.axs.flatten():
            ax.clear()

        fonte_titulo = self.fonte_titulo.get()
        tam_titulo = self.tam_fonte_titulo.get()

        texto_eixo_x = self.entrada_eixo_x.get()
        if texto_eixo_x.strip() == "":
            texto_eixo_x = self.df.columns[self.coluna_valores]
        fonte_x = self.fonte_x.get()
        tam_x = self.tam_fonte_x.get()

        try:
            x_min = float(self.x_min_entry.get())
            x_max = float(self.x_max_entry.get())
        except:
            x_min, x_max = None, None

        try:
            y_min = float(self.y_min_entry.get())
            y_max = float(self.y_max_entry.get())
        except:
            y_min, y_max = None, None

        for i, var in enumerate(self.variaveis):
            dados = valores[self.df.iloc[:, 0] == var].dropna()
            ax = self.axs[i // 2, i % 2]
            ax.hist(
                dados,
                bins=30,
                color=self.cor_histograma,
                alpha=0.7,
                edgecolor=self.cor_histograma,
                linewidth=1
            )
            ax.set_title(var, fontsize=tam_titulo, fontname=fonte_titulo)
            ax.set_xlabel(texto_eixo_x, fontsize=tam_x, fontname=fonte_x)
            ax.set_ylabel('Quantidade de Registros', fontsize=12)

            if x_min is not None and x_max is not None:
                ax.set_xlim(x_min, x_max)
            if y_min is not None and y_max is not None:
                ax.set_ylim(y_min, y_max)

        self.fig.tight_layout()
        self.canvas.draw()

    def salvar_graficos(self):
        if self.df is None:
            messagebox.showerror("Erro", "Nenhum gráfico para salvar. Carregue os dados primeiro.")
            return

        caminho = filedialog.asksaveasfilename(
            defaultextension=".png",
            filetypes=[("Arquivo PNG", "*.png")],
            title="Salvar Gráficos como..."
        )
        if caminho:
            try:
                self.fig.savefig(caminho)
                messagebox.showinfo("Sucesso", f"Gráficos salvos em:\n{caminho}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar o arquivo:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = AppInterativo(root)
    root.mainloop()
