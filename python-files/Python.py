Python

import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
import fnmatch

class BuscadorDeArquivos(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Buscador e Copiador de Arquivos")
        self.geometry("500x440")
        self.configure(bg="#E0F2F7")

        self.directory_label = tk.Label(self, text="Diret�rio:")
        self.directory_label.pack(padx=10, pady=(10, 0), anchor="w")

        self.directory_entry = tk.Entry(self, width=60)
        self.directory_entry.pack(padx=10, pady=5, fill="x")

        self.select_button = tk.Button(self, text="Selecionar Pasta", command=self.select_folder)
        self.select_button.pack(padx=10, pady=5, anchor="e")

        self.keyword_label = tk.Label(self, text="Palavra-chave:")
        self.keyword_label.pack(padx=10, pady=(10, 0), anchor="w")

        self.keyword_entry = tk.Entry(self, width=60)
        self.keyword_entry.pack(padx=10, pady=5, fill="x")

        self.search_button = tk.Button(self, text="Buscar", command=self.search_files)
        self.search_button.pack(padx=10, pady=(10, 0), side="left")
        
        self.mode_button = tk.Button(self, text="Por Nome", command=self.toggle_mode)
        self.mode_button.pack(padx=5, pady=(10, 0), side="left")
        self.search_mode = "nome"

        self.listbox_frame = tk.Frame(self)
        self.listbox_frame.pack(padx=10, pady=10, fill="both", expand=True)

        self.listbox = tk.Listbox(self.listbox_frame, selectmode="multiple")
        self.listbox.pack(side="left", fill="both", expand=True)
        
        self.scrollbar = tk.Scrollbar(self.listbox_frame, orient="vertical", command=self.listbox.yview)
        self.listbox.config(yscrollcommand=self.scrollbar.set)
        self.scrollbar.pack(side="right", fill="y")
        
        self.copy_button = tk.Button(self, text="Copiar para...", command=self.copy_results)
        self.copy_button.pack(padx=10, pady=10, anchor="w")

        self.status_bar = tk.Label(self, text="Pronto.", bd=1, relief="sunken", anchor="w")
        self.status_bar.pack(fill="x", side="bottom")

    def select_folder(self):
        folder_path = filedialog.askdirectory()
        if folder_path:
            self.directory_entry.delete(0, tk.END)
            self.directory_entry.insert(0, folder_path)
            self.status_bar.config(text=f"Diret�rio selecionado: {folder_path}")

    def toggle_mode(self):
        if self.search_mode == "nome":
            self.search_mode = "conteudo"
            self.mode_button.config(text="Por Conte�do")
            self.status_bar.config(text="Modo de busca: LENTO (por conte�do)")
        else:
            self.search_mode = "nome"
            self.mode_button.config(text="Por Nome")
            self.status_bar.config(text="Modo de busca: R�PIDO (por nome)")

    def search_files(self):
        directory = self.directory_entry.get()
        keyword = self.keyword_entry.get()

        if not directory:
            messagebox.showwarning("Aviso", "Por favor, selecione um diret�rio antes de iniciar a busca.")
            return

        self.listbox.delete(0, tk.END)
        self.status_bar.config(text="Buscando...")

        found_files = []
        for root, _, files in os.walk(directory):
            for filename in files:
                file_path = os.path.join(root, filename)
                
                if self.search_mode == "nome":
                    if keyword.lower() in filename.lower():
                        found_files.append(file_path)
                elif self.search_mode == "conteudo":
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            content = f.read()
                            if keyword.lower() in content.lower():
                                found_files.append(file_path)
                    except Exception as e:
                        # Ignora arquivos bin�rios ou ileg�veis
                        pass
        
        for file in found_files:
            self.listbox.insert(tk.END, file)
            
        self.status_bar.config(text=f"Busca conclu�da. {len(found_files)} resultados encontrados.")
        if not found_files:
            messagebox.showinfo("Busca", "Nenhum arquivo encontrado com a palavra-chave fornecida.")

    def copy_results(self):
        selected_indices = self.listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Aviso", "Por favor, selecione os arquivos que deseja copiar.")
            return

        dest_folder = filedialog.askdirectory(title="Selecione o diret�rio de destino")
        if not dest_folder:
            return

        copied_count = 0
        for index in selected_indices:
            source_path = self.listbox.get(index)
            file_name = os.path.basename(source_path)
            dest_path = os.path.join(dest_folder, file_name)
            
            try:
                shutil.copy2(source_path, dest_path)
                copied_count += 1
            except Exception as e:
                messagebox.showerror("Erro de C�pia", f"N�o foi poss�vel copiar o arquivo: {file_name}\nErro: {e}")
                self.status_bar.config(text="C�pia interrompida devido a um erro.")
                return

        messagebox.showinfo("Sucesso", f"C�pia conclu�da! {copied_count} item(s) foram copiados para: {dest_folder}")
        self.status_bar.config(text="Pronto.")

if __name__ == "__main__":
    app = BuscadorDeArquivos()
    app.mainloop()