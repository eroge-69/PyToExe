import tkinter as tk
from tkinter import ttk, filedialog, messagebox

class LetraApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inseridor de Letras A;B;C;D;")
        self.root.geometry("600x400")

        # Variáveis
        self.texto = tk.Text(root, wrap="word", height=15)
        self.texto.pack(pady=10, padx=10, fill="both", expand=True)

        self.contador_label = tk.Label(root, text="Letras: 0")
        self.contador_label.pack()

        frame_botoes = tk.Frame(root)
        frame_botoes.pack(pady=5)

        for letra in ["A", "B", "C", "D"]:
            tk.Button(frame_botoes, text=letra, width=5, command=lambda l=letra: self.inserir_letra(l)).pack(side="left", padx=5)

        frame_opcoes = tk.Frame(root)
        frame_opcoes.pack(pady=5)

        tk.Label(frame_opcoes, text="Enter automático após:").pack(side="left")
        self.qtd_var = tk.IntVar(value=0)
        self.combo = ttk.Combobox(frame_opcoes, textvariable=self.qtd_var, values=list(range(0, 101)), width=5)
        self.combo.pack(side="left", padx=5)
        tk.Label(frame_opcoes, text="letras").pack(side="left")

        frame_funcoes = tk.Frame(root)
        frame_funcoes.pack(pady=10)

        tk.Button(frame_funcoes, text="Copiar Tudo", command=self.copiar_texto).pack(side="left", padx=5)
        tk.Button(frame_funcoes, text="Salvar .DAT", command=self.salvar_arquivo).pack(side="left", padx=5)
        tk.Button(frame_funcoes, text="Carregar .DAT", command=self.carregar_arquivo).pack(side="left", padx=5)

        # Eventos de teclado
        root.bind("<KeyPress>", self.tecla_pressionada)

        # Contador de letras
        self.contador = 0

    def inserir_letra(self, letra):
        self.texto.insert(tk.END, letra + ";")
        self.atualizar_contador()
        self.verificar_quebra()

    def tecla_pressionada(self, event):
        mapa = {"a": "A", "s": "B", "d": "C", "f": "D"}
        if event.keysym.lower() in mapa:
            self.inserir_letra(mapa[event.keysym.lower()])
        elif event.keysym == "space":
            self.texto.insert(tk.END, " ;")
            self.atualizar_contador()
            self.verificar_quebra()

    def atualizar_contador(self):
        texto = self.texto.get("1.0", tk.END).replace("\n", "")
        letras = [ch for ch in texto if ch in "ABCD"]
        self.contador = len(letras)
        self.contador_label.config(text=f"Letras: {self.contador}")

    def verificar_quebra(self):
        limite = self.qtd_var.get()
        if limite > 0 and self.contador % limite == 0:
            self.texto.insert(tk.END, "\n")

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
        nome_arquivo = filedialog.asksaveasfilename(defaultextension=".dat", filetypes=[("Arquivos DAT", "*.dat")])
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
            messagebox.showinfo("Carregado", f"Arquivo {nome_arquivo} carregado!")

# Execução
if __name__ == "__main__":
    root = tk.Tk()
    app = LetraApp(root)
    root.mainloop()
