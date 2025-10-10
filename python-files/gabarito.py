import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class LetraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inseridor de Letras A;B;C;D;NULO")
        self.root.geometry("650x480")

        # Área de texto
        self.texto = tk.Text(root, wrap="word", height=15, undo=True)
        self.texto.pack(pady=10, padx=10, fill="both", expand=True)

        # Contadores
        self.contador_label = tk.Label(root, text="Letras: 0")
        self.contador_label.pack()
        self.alunos_label = tk.Label(root, text="Quantidade de Alunos: 0 | Ausentes: 0")
        self.alunos_label.pack()

        # Frame de botões de letras
        frame_botoes = tk.Frame(root)
        frame_botoes.pack(pady=5)

        for letra in ["A", "B", "C", "D"]:
            tk.Button(frame_botoes, text=letra, width=5,
                      command=lambda l=letra: self.inserir_letra(l)).pack(side="left", padx=5)

        tk.Button(frame_botoes, text="NULO", width=6,
                  command=self.inserir_nulo).pack(side="left", padx=5)

        # Opções de quebra automática
        frame_opcoes = tk.Frame(root)
        frame_opcoes.pack(pady=5)

        tk.Label(frame_opcoes, text="Enter automático após:").pack(side="left")
        self.qtd_var = tk.StringVar(value="0")
        self.combo = ttk.Combobox(frame_opcoes, textvariable=self.qtd_var,
                                  values=list(range(0, 101)), width=5)
        self.combo.pack(side="left", padx=5)
        tk.Label(frame_opcoes, text="letras").pack(side="left")

        self.combo.bind("<FocusOut>", lambda e: self.qtd_var.set(self.qtd_var.get() or "0"))

        # Frame de funções
        frame_funcoes = tk.Frame(root)
        frame_funcoes.pack(pady=10)

        tk.Button(frame_funcoes, text="Copiar Tudo", command=self.copiar_texto).pack(side="left", padx=5)
        tk.Button(frame_funcoes, text="Salvar .DAT", command=self.salvar_arquivo).pack(side="left", padx=5)
        tk.Button(frame_funcoes, text="Carregar .DAT", command=self.carregar_arquivo).pack(side="left", padx=5)
        tk.Button(frame_funcoes, text="Limpar Tudo", command=self.limpar_tudo, fg="red").pack(side="left", padx=5)

        # Novo botão: preencher 1 linha com NULO
        tk.Button(root, text="Preencher linha com NULO",
                  command=self.preencher_nulo_uma_linha, bg="#ddd").pack(pady=5)

        # Eventos
        self.texto.bind("<KeyPress>", self.tecla_pressionada)
        self.texto.bind("<<Modified>>", self.atualizar_contador_evento)

        self.contador = 0

    def inserir_letra(self, letra):
        self.texto.insert(tk.END, letra + ";")
        self.atualizar_contador()
        self.verificar_quebra()

    def inserir_nulo(self):
        self.texto.insert(tk.END, ";")
        self.atualizar_contador()
        self.verificar_quebra()

    def apagar_ultimo(self):
        conteudo = self.texto.get("1.0", tk.END).rstrip("\n")
        if not conteudo:
            return
        if conteudo.endswith(";"):
            conteudo = conteudo[:-1]
            while conteudo and conteudo[-1].isalpha():
                conteudo = conteudo[:-1]
        self.texto.delete("1.0", tk.END)
        self.texto.insert("1.0", conteudo)
        self.atualizar_contador()

    def tecla_pressionada(self, event):
        if event.state & 0x4:
            return
        if event.char.isalpha():
            self.inserir_letra(event.char.upper())
            return "break"
        elif event.keysym == "space":
            self.inserir_nulo()
            return "break"
        elif event.keysym == "BackSpace":
            self.apagar_ultimo()
            return "break"
        elif event.keysym == "Return":
            self.texto.insert(tk.END, "\n")
            self.contador = 0
            self.contador_label.config(text=f"Letras: {self.contador}")
            self.atualizar_alunos()
            return "break"

    def atualizar_contador_evento(self, event):
        self.texto.edit_modified(False)
        self.atualizar_contador()
        self.atualizar_alunos()

    def atualizar_contador(self):
        linhas = self.texto.get("1.0", tk.END).split("\n")
        if linhas:
            ultima_linha = linhas[-2] if linhas[-1] == "" else linhas[-1]
            if ultima_linha.strip() == "":
                self.contador = 0
            else:
                partes = ultima_linha.split(";")
                if partes and partes[-1] == "":
                    partes = partes[:-1]
                self.contador = len(partes)
        else:
            self.contador = 0
        self.contador_label.config(text=f"Letras: {self.contador}")

    def atualizar_alunos(self):
        """Conta total de linhas e ausentes"""
        linhas = [l.strip() for l in self.texto.get("1.0", tk.END).split("\n") if l.strip() != ""]
        total_alunos = len(linhas)
        ausentes = sum(1 for l in linhas if l.replace(";", "") == "")
        self.alunos_label.config(text=f"Quantidade de Alunos: {total_alunos} | Ausentes: {ausentes}")

    def verificar_quebra(self):
        try:
            limite = int(self.qtd_var.get())
        except (tk.TclError, ValueError):
            return
        if limite > 0 and self.contador > 0 and self.contador % limite == 0:
            self.texto.insert(tk.END, "\n")
            self.contador = 0
            self.contador_label.config(text=f"Letras: {self.contador}")
            self.atualizar_alunos()

    def preencher_nulo_uma_linha(self):
        """Adiciona apenas uma linha preenchida com NULO"""
        try:
            limite = int(self.qtd_var.get())
        except ValueError:
            messagebox.showerror("Erro", "Defina um número válido de letras por linha.")
            return
        if limite <= 0:
            messagebox.showwarning("Aviso", "Escolha uma quantidade de letras maior que 0.")
            return

        linha = ";" * limite
        self.texto.insert(tk.END, linha + "\n")
        self.atualizar_contador()
        self.atualizar_alunos()

    def copiar_texto(self):
        conteudo = self.texto.get("1.0", tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(conteudo)
        messagebox.showinfo("Copiado", "Texto copiado para a área de transferência!")

    def salvar_arquivo(self):
        conteudo = self.texto.get("1.0", tk.END).strip()
        if not conteudo:
            messagebox.showwarning("Aviso", "Não há nada para salvar!")
            return
        nome_arquivo = filedialog.asksaveasfilename(defaultextension=".dat",
                                                    filetypes=[("Arquivos DAT", "*.dat")])
        if nome_arquivo:
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                f.write(conteudo)
            messagebox.showinfo("Salvo", f"Arquivo salvo como {nome_arquivo}")

    def carregar_arquivo(self):
        nome_arquivo = filedialog.askopenfilename(filetypes=[("Arquivos DAT", "*.dat")])
        if nome_arquivo:
            with open(nome_arquivo, "r", encoding="utf-8") as f:
                conteudo = f.read()
            self.texto.delete("1.0", tk.END)
            self.texto.insert(tk.END, conteudo)
            self.atualizar_contador()
            self.atualizar_alunos()
            messagebox.showinfo("Carregado", f"Arquivo {nome_arquivo} carregado!")

    def limpar_tudo(self):
        if messagebox.askyesno("Confirmar", "Deseja realmente apagar todo o conteúdo?"):
            self.texto.delete("1.0", tk.END)
            self.contador = 0
            self.contador_label.config(text="Letras: 0")
            self.alunos_label.config(text="Quantidade de Alunos: 0 | Ausentes: 0")
            messagebox.showinfo("Limpo", "Todo o conteúdo foi apagado!")

# Execução
if __name__ == "__main__":
    root = tk.Tk()
    app = LetraApp(root)
    root.mainloop()
