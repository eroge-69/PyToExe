import tkinter as tk
from tkinter import ttk, messagebox
from datetime import datetime

class InventarioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Inventário de Materiais")
        self.root.geometry("900x600")
        
        # Dados de exemplo (lista de dicionários)
        self.itens = [
            {"item": "Parafusos M5", "quant_atual": 150, "quant_min": 50, "local": "Prateleira A1", 
             "data": "15/10/2023", "obs": "Em bom estado"},
            {"item": "Fios Elétricos (10m)", "quant_atual": 5, "quant_min": 2, "local": "Caixa B2", 
             "data": "15/10/2023", "obs": "Verificar validade"},
            {"item": "Ferramenta de Corte", "quant_atual": 3, "quant_min": 1, "local": "Gaveta C3", 
             "data": "15/10/2023", "obs": "Uma danificada"}
        ]
        
        self.selecionado = None  # Para edição
        
        self.criar_interface()
        self.atualizar_tabela()
    
    def criar_interface(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Título
        titulo = ttk.Label(main_frame, text="Inventário de Materiais", font=("Arial", 16, "bold"))
        titulo.grid(row=0, column=0, columnspan=4, pady=10)
        
        # Campos de entrada (para adicionar/editar)
        campos_frame = ttk.LabelFrame(main_frame, text="Adicionar/Editar Item", padding="5")
        campos_frame.grid(row=1, column=0, columnspan=4, sticky=(tk.W, tk.E), pady=5)
        
        # Labels e Entries
        ttk.Label(campos_frame, text="Item/Material:").grid(row=0, column=0, sticky=tk.W, padx=5)
        self.entry_item = ttk.Entry(campos_frame, width=20)
        self.entry_item.grid(row=0, column=1, padx=5, pady=2)
        
        ttk.Label(campos_frame, text="Quant. Atual:").grid(row=0, column=2, sticky=tk.W, padx=5)
        self.entry_quant_atual = ttk.Entry(campos_frame, width=10)
        self.entry_quant_atual.grid(row=0, column=3, padx=5, pady=2)
        
        ttk.Label(campos_frame, text="Quant. Mínima:").grid(row=1, column=0, sticky=tk.W, padx=5)
        self.entry_quant_min = ttk.Entry(campos_frame, width=10)
        self.entry_quant_min.grid(row=1, column=3, padx=5, pady=2)
        
        ttk.Label(campos_frame, text="Localização:").grid(row=1, column=1, sticky=tk.W, padx=5)
        self.entry_local = ttk.Entry(campos_frame, width=20)
        self.entry_local.grid(row=1, column=2, padx=5, pady=2)
        
        ttk.Label(campos_frame, text="Observações:").grid(row=2, column=0, sticky=tk.W, padx=5)
        self.entry_obs = ttk.Entry(campos_frame, width=50)
        self.entry_obs.grid(row=2, column=1, columnspan=3, padx=5, pady=2, sticky=(tk.W, tk.E))
        
        # Data é auto-preenchida
        self.data_atual = datetime.now().strftime("%d/%m/%Y")
        
        # Botões
        botoes_frame = ttk.Frame(main_frame)
        botoes_frame.grid(row=2, column=0, columnspan=4, pady=10)
        
        self.btn_adicionar = ttk.Button(botoes_frame, text="Adicionar", command=self.adicionar_item)
        self.btn_adicionar.grid(row=0, column=0, padx=5)
        
        self.btn_editar = ttk.Button(botoes_frame, text="Editar Selecionado", command=self.editar_item)
        self.btn_editar.grid(row=0, column=1, padx=5)
        
        self.btn_remover = ttk.Button(botoes_frame, text="Remover Selecionado", command=self.remover_item)
        self.btn_remover.grid(row=0, column=2, padx=5)
        
        self.btn_limpar = ttk.Button(botoes_frame, text="Limpar Campos", command=self.limpar_campos)
        self.btn_limpar.grid(row=0, column=3, padx=5)
        
        # Tabela
        tabela_frame = ttk.LabelFrame(main_frame, text="Lista de Itens", padding="5")
        tabela_frame.grid(row=3, column=0, columnspan=4, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        
        # Treeview para tabela
        colunas = ("Item", "Quant. Atual", "Quant. Mín.", "Local", "Data", "Obs.")
        self.tree = ttk.Treeview(tabela_frame, columns=colunas, show="headings", height=15)
        
        # Definir cabeçalhos
        self.tree.heading("Item", text="Item/Material")
        self.tree.heading("Quant. Atual", text="Quant. Atual")
        self.tree.heading("Quant. Mín.", text="Quant. Mínima")
        self.tree.heading("Local", text="Localização")
        self.tree.heading("Data", text="Data Atualização")
        self.tree.heading("Obs.", text="Observações")
        
        # Larguras das colunas
        self.tree.column("Item", width=150)
        self.tree.column("Quant. Atual", width=80)
        self.tree.column("Quant. Mín.", width=80)
        self.tree.column("Local", width=100)
        self.tree.column("Data", width=100)
        self.tree.column("Obs.", width=200)
        
        # Scrollbar para tabela
        scrollbar = ttk.Scrollbar(tabela_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Seleção na tabela
        self.tree.bind("<<TreeviewSelect>>", self.selecionar_item)
        
        # Configurar redimensionamento
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(3, weight=1)
        tabela_frame.columnconfigure(0, weight=1)
        tabela_frame.rowconfigure(0, weight=1)
        campos_frame.columnconfigure(1, weight=1)
    
    def atualizar_tabela(self):
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        # Adicionar itens
        for i, item in enumerate(self.itens):
            self.tree.insert("", "end", iid=i, values=(
                item["item"], item["quant_atual"], item["quant_min"], 
                item["local"], item["data"], item["obs"]
            ))
    
    def adicionar_item(self):
        item = self.entry_item.get().strip()
        if not item:
            messagebox.showwarning("Aviso", "Preencha pelo menos o nome do item!")
            return
        
        try:
            quant_atual = int(self.entry_quant_atual.get() or 0)
            quant_min = int(self.entry_quant_min.get() or 0)
        except ValueError:
            messagebox.showerror("Erro", "Quantidades devem ser números inteiros!")
            return
        
        novo_item = {
            "item": item,
            "quant_atual": quant_atual,
            "quant_min": quant_min,
            "local": self.entry_local.get().strip(),
            "data": self.data_atual,
            "obs": self.entry_obs.get().strip()
        }
        
        self.itens.append(novo_item)
        self.atualizar_tabela()
        self.limpar_campos()
        messagebox.showinfo("Sucesso", "Item adicionado!")
    
    def selecionar_item(self, event):
        selecionado = self.tree.selection()
        if selecionado:
            self.selecionado = self.tree.item(selecionado[0])["values"]
            # Preencher campos para edição
            self.entry_item.delete(0, tk.END)
            self.entry_item.insert(0, self.selecionado[0])
            self.entry_quant_atual.delete(0, tk.END)
            self.entry_quant_atual.insert(0, self.selecionado[1])
            self.entry_quant_min.delete(0, tk.END)
            self.entry_quant_min.insert(0, self.selecionado[2])
            self.entry_local.delete(0, tk.END)
            self.entry_local.insert(0, self.selecionado[3])
            self.entry_obs.delete(0, tk.END)
            self.entry_obs.insert(0, self.selecionado[5])
        else:
            self.selecionado = None
    
    def editar_item(self):
        if not self.selecionado:
            messagebox.showwarning("Aviso", "Selecione um item na tabela para editar!")
            return
        
        indice = self.tree.selection()[0]
        item = self.entry_item.get().strip()
        if not item:
            messagebox.showwarning("Aviso", "Preencha o nome do item!")
            return
        
        try:
            quant_atual = int(self.entry_quant_atual.get() or 0)
            quant_min = int(self.entry_quant_min.get() or 0)
        except ValueError:
            messagebox.showerror("Erro", "Quantidades devem ser números inteiros!")
            return
        
        self.itens[int(indice)] = {
            "item": item,
            "quant_atual": quant_atual,
            "quant_min": quant_min,
            "local": self.entry_local.get().strip(),
            "data": self.data_atual,  # Atualiza data
            "obs": self.entry_obs.get().strip()
        }
        
        self.atualizar_tabela()
        self.limpar_campos()
        self.selecionado = None
        messagebox.showinfo("Sucesso", "Item editado!")
    
    def remover_item(self):
        if not self.tree.selection():
            messagebox.showwarning("Aviso", "Selecione um item na tabela para remover!")
            return
        
        if messagebox.askyesno("Confirmação", "Deseja remover este item?"):
            indice = int(self.tree.selection()[0])
            del self.itens[indice]
            self.atualizar_tabela()
            self.limpar_campos()
            self.selecionado = None
            messagebox.showinfo("Sucesso", "Item removido!")
    
    def limpar_campos(self):
        self.entry_item.delete(0, tk.END)
        self.entry_quant_atual.delete(0, tk.END)
        self.entry_quant_min.delete(0, tk.END)
        self.entry_local.delete(0, tk.END)
        self.entry_obs.delete(0, tk.END)
        self.selecionado = None

if __name__ == "__main__":
    root = tk.Tk()
    app = InventarioApp(root)
    root.mainloop()