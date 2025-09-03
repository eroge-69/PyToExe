import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# Dados fictícios
dados = {
    "Lisboa": ["Farmácia Central", "Farmácia Avenida", "Farmácia da Sé"],
    "Porto": ["Farmácia do Norte", "Farmácia Ribeira", "Farmácia Cedofeita"],
    "Coimbra": ["Farmácia Mondego", "Farmácia Universitária", "Farmácia Santa Clara"]
}

class FarmaciaApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Farmácias de Serviço")

        self.selecoes = {}

        row = 0
        tk.Label(root, text="Selecione a farmácia de serviço para cada cidade:", font=("Arial", 12)).grid(row=row, column=0, columnspan=2, pady=10)

        row += 1
        for cidade, farmacias in dados.items():
            tk.Label(root, text=cidade, font=("Arial", 10)).grid(row=row, column=0, padx=10, pady=5, sticky="e")
            combo = ttk.Combobox(root, values=farmacias, state="readonly")
            combo.grid(row=row, column=1, padx=10, pady=5)
            self.selecoes[cidade] = combo
            row += 1

        # Botão Exportar
        tk.Button(root, text="Exportar para TXT", command=self.exportar).grid(row=row, column=0, columnspan=2, pady=20)

    def exportar(self):
        linhas = []
        for cidade, combo in self.selecoes.items():
            escolha = combo.get()
            if escolha:
                linhas.append(f"{cidade}: {escolha}")
            else:
                linhas.append(f"{cidade}: (não selecionado)")

        try:
            with open("farmacias_selecionadas.txt", "w", encoding="utf-8") as f:
                f.write("\n".join(linhas))
            messagebox.showinfo("Sucesso", "Ficheiro exportado com sucesso como 'farmacias_selecionadas.txt'.")
        except Exception as e:
            messagebox.showerror("Erro", f"Ocorreu um erro ao exportar:\n{str(e)}")

# Iniciar a app
if __name__ == "__main__":
    root = tk.Tk()
    app = FarmaciaApp(root)
    root.mainloop()
