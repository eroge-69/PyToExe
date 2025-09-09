import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

class CleanerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Limpador de Arquivos - Manter apenas os da lista")
        self.root.geometry("1100x600")

        self.allowed_files = set()
        self.allowed_list_full = {}
        self.folder_path = ""
        self.found_files = []
        self.files_to_delete = []

        # Título
        tk.Label(root, text="Limpador de Arquivos por Lista", font=("Arial", 16, "bold")).pack(pady=10)

        # Botões
        tk.Button(root, text="1. Carregar Lista de Arquivos Permitidos", command=self.load_allowed_list, height=2, width=40).pack(pady=5)
        tk.Button(root, text="2. Selecionar Pasta para Verificar", command=self.select_folder, height=2, width=40).pack(pady=5)
        tk.Button(root, text="3. Verificar e Comparar Arquivos", command=self.compare_files, height=2, width=40).pack(pady=5)

        # Tabela
        frame_table = tk.Frame(root)
        frame_table.pack(padx=20, pady=10, fill="both", expand=True)

        scroll_x = tk.Scrollbar(frame_table, orient="horizontal")
        scroll_y = tk.Scrollbar(frame_table, orient="vertical")

        self.tree = ttk.Treeview(
            frame_table,
            columns=("Permitido", "Encontrado", "Status"),
            show="headings",
            xscrollcommand=scroll_x.set,
            yscrollcommand=scroll_y.set,
            height=18
        )

        scroll_x.pack(side="bottom", fill="x")
        scroll_y.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)

        scroll_x.config(command=self.tree.xview)
        scroll_y.config(command=self.tree.yview)

        # Colunas
        self.tree.heading("Permitido", text="Arquivo Permitido (da Lista)")
        self.tree.heading("Encontrado", text="Arquivo Encontrado na Pasta")
        self.tree.heading("Status", text="Status")

        self.tree.column("Permitido", width=300, anchor="w")
        self.tree.column("Encontrado", width=400, anchor="w")
        self.tree.column("Status", width=200, anchor="center")

        # Cores
        self.tree.tag_configure("preservado", foreground="green")
        self.tree.tag_configure("deletado", foreground="red")
        self.tree.tag_configure("nao_encontrado", foreground="orange")

        # Botão de exclusão
        tk.Button(
            root,
            text="4. ⚠️ EXCLUIR ARQUIVOS (confirmar)",
            bg="red", fg="white", font=("Arial", 10, "bold"),
            command=self.confirm_deletion,
            height=2, width=40
        ).pack(pady=10)

        self.status_label = tk.Label(root, text="Aguardando ações...", fg="gray")
        self.status_label.pack(pady=5)

    def load_allowed_list(self):
        file_path = filedialog.askopenfilename(
            title="Selecione o arquivo com a lista de arquivos permitidos",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not file_path:
            return
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f if line.strip()]
                self.allowed_files = {os.path.basename(line) for line in lines}
                self.allowed_list_full = {os.path.basename(line): line for line in lines}
            self.status_label.config(text=f"✅ Lista carregada: {len(self.allowed_files)} arquivos.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao ler lista:\n{e}")

    def select_folder(self):
        folder = filedialog.askdirectory(title="Selecione a pasta para verificar")
        if folder:
            self.folder_path = folder
            self.status_label.config(text=f"📁 Pasta selecionada: {os.path.basename(folder)}")

    def compare_files(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        if not self.allowed_files or not self.folder_path:
            messagebox.showwarning("Atenção", "Carregue a lista e selecione uma pasta.")
            return

        found_files_map = {}
        self.files_to_delete = []

        for root_dir, _, files in os.walk(self.folder_path):
            for file in files:
                full_path = os.path.join(root_dir, file)
                rel_path = os.path.relpath(full_path, self.folder_path)
                found_files_map[file] = rel_path
                if file not in self.allowed_files:
                    self.files_to_delete.append(full_path)

        all_displayed = set()

        for name in self.allowed_files:
            if name in found_files_map:
                self.tree.insert("", "end", values=(self.allowed_list_full.get(name, name), found_files_map[name], "✅ Preservado"), tags=("preservado",))
                all_displayed.add(name)
            else:
                self.tree.insert("", "end", values=(self.allowed_list_full.get(name, name), "—", "⚠️ Não encontrado"), tags=("nao_encontrado",))

        for file, path in found_files_map.items():
            if file not in all_displayed:
                self.tree.insert("", "end", values=("—", path, "❌ Será deletado"), tags=("deletado",))

        self.status_label.config(
            text=f"🔍 {len(self.allowed_files)} permitidos | {len(found_files_map)} encontrados | {len(self.files_to_delete)} serão deletados."
        )

    def confirm_deletion(self):
        if not self.files_to_delete:
            messagebox.showinfo("Informação", "Nenhum arquivo para excluir.")
            return
        if messagebox.askyesno("Confirmação", f"Excluir {len(self.files_to_delete)} arquivos?"):
            deleted = 0
            errors = []
            for file in self.files_to_delete:
                try:
                    os.remove(file)
                    deleted += 1
                except Exception as e:
                    errors.append(f"{os.path.basename(file)}: {e}")
            msg = f"✅ {deleted} arquivos excluídos."
            if errors:
                msg += f"\n\n❌ Erros:\n" + "\n".join(errors)
                messagebox.showerror("Resultado", msg)
            else:
                messagebox.showinfo("Concluído", msg)
            self.status_label.config(text=f"🧹 {deleted} arquivos removidos.")

if __name__ == "__main__":
    root = tk.Tk()
    app = CleanerApp(root)
    root.mainloop()