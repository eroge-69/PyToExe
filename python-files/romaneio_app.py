
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from datetime import datetime

class RomaneioApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Controle de Descargas de Biomassa")
        self.data = []
        self.placas_motoristas = {}

        self.create_widgets()

    def create_widgets(self):
        fields = ['Data da Nota', 'Data da Descarga', 'Placa', 'Nota Fiscal',
                  'Quantidade da Nota', 'Quantidade Real Descarga',
                  'Local de Carregamento', 'Local de Descarga']
        self.entries = {}
        for i, field in enumerate(fields):
            ttk.Label(self.root, text=field).grid(row=i, column=0)
            entry = ttk.Entry(self.root)
            entry.grid(row=i, column=1)
            self.entries[field] = entry

        ttk.Button(self.root, text="Adicionar Romaneio", command=self.add_romaneio).grid(row=0, column=2, padx=10)
        ttk.Button(self.root, text="Salvar e Gerar Relatórios", command=self.save_and_generate_reports).grid(row=1, column=2, padx=10)
        ttk.Button(self.root, text="Importar Placas/Motoristas", command=self.import_placas_motoristas).grid(row=2, column=2, padx=10)

    def add_romaneio(self):
        entry_values = [self.entries[field].get() for field in self.entries]
        if not all(entry_values):
            messagebox.showwarning("Atenção", "Preencha todos os campos!")
            return
        self.data.append(entry_values)
        messagebox.showinfo("Sucesso", "Romaneio adicionado!")
        for entry in self.entries.values():
            entry.delete(0, tk.END)

    def import_placas_motoristas(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return
        df = pd.read_csv(file_path)
        self.placas_motoristas = dict(zip(df['Placa'], df['Motorista']))
        messagebox.showinfo("Importado", f"{len(self.placas_motoristas)} placas/motoristas importados.")

    def save_and_generate_reports(self):
        if not self.data:
            messagebox.showwarning("Atenção", "Nenhum romaneio adicionado!")
            return

        df = pd.DataFrame(self.data, columns=['Data da Nota', 'Data da Descarga', 'Placa', 'Nota Fiscal',
                                              'Quantidade da Nota', 'Quantidade Real Descarga',
                                              'Local de Carregamento', 'Local de Descarga'])
        df['Motorista'] = df['Placa'].map(self.placas_motoristas).fillna('Desconhecido')

        save_path = filedialog.asksaveasfilename(defaultextension='.xlsx', filetypes=[("Excel files", "*.xlsx")])
        if not save_path:
            return
        with pd.ExcelWriter(save_path) as writer:
            df.to_excel(writer, index=False, sheet_name='Romaneios')
            resumo_entregas = df.groupby(['Data da Descarga', 'Local de Descarga'])['Quantidade Real Descarga'].sum().reset_index()
            resumo_entregas.to_excel(writer, index=False, sheet_name='Resumo Entregas')
            resumo_carregamentos = df.groupby(['Data da Nota', 'Local de Carregamento'])['Quantidade da Nota'].sum().reset_index()
            resumo_carregamentos.to_excel(writer, index=False, sheet_name='Resumo Carregamentos')
            resumo_motoristas = df.groupby(['Motorista', 'Data da Descarga'])['Quantidade Real Descarga'].sum().reset_index()
            resumo_motoristas.to_excel(writer, index=False, sheet_name='Resumo Motoristas')
        messagebox.showinfo("Relatórios Gerados", f"Relatórios salvos em {save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = RomaneioApp(root)
    root.mainloop()
