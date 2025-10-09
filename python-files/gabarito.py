import tkinter as tk
from tkinter import filedialog, messagebox

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("Inseridor de Letras A B C D")

        # Variável para controlar o limite de letras antes do Enter
        self.limite = tk.IntVar(value=0)
        self.contador = 0

        # Campo de texto
        self.text = tk.Text(root, width=60, height=15, font=("Consolas", 12))
        self.text.pack(pady=10)
        self.text.bind("<Key>", self.key_press)

        # Frame para botões de letras
        frame_botoes = tk.Frame(root)
        frame_botoes.pack()

        for letra in ["A", "B", "C", "D"]:
            tk.Button(frame_botoes, text=letra, width=5, height=2, 
                      command=lambda l=letra: self.inserir_letra(l)).pack(side="left", padx=5)

        # Escolher limite de letras
        tk.Label(root, text="Letras antes do ENTER automático:").pack(pady=(10, 0))
        tk.Spinbox(root, from_=0, to=100, textvariable=self.limite, width=5).pack()

        # Botões de ação
        frame_acoes = tk.Frame(root)
        frame_acoes.pack(pady=10)

        tk.Button(frame_acoes, text="Copiar", command=self.copiar).pack(side="left", padx=5)
        tk.Button(frame_acoes, text="Salvar (.dat)", command=self.salvar).pack(side="left", padx=5)
        tk.Button(frame_acoes, text="Carregar", command=self.carregar).pack(side="left", padx=5)

    def inserir_letra(self, letra):
        self.text.insert(tk.END, letra + ";")
        self.contador += 1
        self.verifica_enter()

    def key_press(self, event):
        if event.keysym in ["a", "s", "d", "f"]:
            mapa = {"a": "A;", "s": "B;", "d": "C;", "f": "D;"}
            self.text.insert(tk.END, mapa[event.keysym])
            self.contador += 1
            self.verifica_enter()
            return "break"  # impede o caractere original
        elif event.keysym == "BackSpace":
            return  # permite apagar normalmente
        else:
            pass  # permite outras teclas (Ctrl, setas, etc.)

    def verifica_enter(self):
        if self.limite.get() > 0 and self.contador >= self.limite.get():
            self.text.insert(tk.END, "\n")
            self.contador = 0

    def copiar(self):
        conteudo = self.text.get("1.0", tk.END).strip()
        self.root.clipboard_clear()
        self.root.clipboard_append(conteudo)
        messagebox.showinfo("Copiar", "Texto copiado para a área de transferência!")

    def salvar(self):
        conteudo = self.text.get("1.0", tk.END).strip()
        if not conteudo:
            messagebox.showwarning("Aviso", "Não há nada para salvar!")
            return
        nome_arquivo = filedialog.asksaveasfilename(defaultextension=".dat", filetypes=[("Arquivos DAT", "*.dat")])
        if nome_arquivo:
            with open(nome_arquivo, "w", encoding="utf-8") as f:
                f.write(conteudo)
            messagebox.showinfo("Salvar", f"Arquivo salvo como: {nome_arquivo}")

    def carregar(self):
        nome_arquivo = filedialog.askopenfilename(filetypes=[("Arquivos DAT", "*.dat")])
        if nome_arquivo:
            with open(nome_arquivo, "r", encoding="utf-8") as f:
                conteudo = f.read()
            self.text.delete("1.0", tk.END)
            self.text.insert(tk.END, conteudo)
            messagebox.showinfo("Carregar", f"Arquivo carregado com sucesso!")

if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
