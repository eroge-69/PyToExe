import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pefile
import os
import sys
import subprocess
import webbrowser
import json
import csv

# Instala requests automaticamente se não estiver presente
try:
    import requests
except ModuleNotFoundError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
    import requests

# Tenta importar suporte a drag and drop
try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
    DND_AVAILABLE = True
except ImportError:
    DND_AVAILABLE = False


def analisar_dll(filepath):
    try:
        pe = pefile.PE(filepath)
        info = []
        info.append("=" * 60)
        info.append(f"📁 Nome do Arquivo: {os.path.basename(filepath)}")
        info.append(f"📦 Tamanho: {os.path.getsize(filepath):,} bytes")
        info.append(f"🔢 Arquitetura: {'64-bit' if pe.OPTIONAL_HEADER.Magic == 0x20b else '32-bit'}")
        info.append(f"📌 Entrypoint: {hex(pe.OPTIONAL_HEADER.AddressOfEntryPoint)}")
        info.append(f"🧠 Imagem Base: {hex(pe.OPTIONAL_HEADER.ImageBase)}")
        info.append("=" * 60)
        info.append("\n📥 Importações:\n")

        if hasattr(pe, 'DIRECTORY_ENTRY_IMPORT'):
            for entry in pe.DIRECTORY_ENTRY_IMPORT:
                dll_name = entry.dll.decode(errors="ignore") if entry.dll else '---'
                info.append(f"  ➜ {dll_name}:")
                for imp in entry.imports:
                    nome = imp.name.decode(errors="ignore") if imp.name else '---'
                    info.append(f"     {hex(imp.address)}\t{nome}")
        else:
            info.append("  Nenhuma importação encontrada.")

        info.append("=" * 60)
        info.append("\n🔗 Exportações:\n")
        if hasattr(pe, 'DIRECTORY_ENTRY_EXPORT'):
            for exp in pe.DIRECTORY_ENTRY_EXPORT.symbols:
                info.append(f"  ➜ {exp.name.decode(errors='ignore') if exp.name else '---'} -> {hex(exp.address)}")
        else:
            info.append("  Nenhuma exportação encontrada.")

        info.append("=" * 60)
        info.append("\n🔒 Seções:\n")
        for section in pe.sections:
            info.append(f"  ➜ {section.Name.decode(errors='ignore').strip()}: {hex(section.VirtualAddress)}")

        return "\n".join(info)
    except Exception as e:
        return f"❌ Erro ao analisar o arquivo: {str(e)}"


class App(tk.Tk if not DND_AVAILABLE else TkinterDnD.Tk):
    def __init__(self):
        super().__init__()
        self.title("Analisador de DLL / EXE")
        self.geometry("900x650")
        self.configure(bg="#f0f0f0")

        self.arquivo_analisado = None
        self.modo_escuro = False

        self._criar_widgets()
        self._criar_menu()
        self._aplicar_tema_claro()

    def _criar_widgets(self):
        self.instrucoes = ttk.Label(
            self,
            text="Arraste um arquivo .dll ou .exe aqui ou use o menu para abrir",
            font=("Segoe UI", 12)
        )
        self.instrucoes.pack(pady=10)

        search_frame = ttk.Frame(self)
        search_frame.pack(pady=5)

        self.search_var = tk.StringVar()
        self.entry_busca = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.entry_busca.grid(row=0, column=0, padx=5)

        self.btn_buscar = ttk.Button(search_frame, text="🔍 Buscar", command=self.buscar_texto)
        self.btn_buscar.grid(row=0, column=1, padx=5)

        text_frame = ttk.Frame(self)
        text_frame.pack(expand=True, fill="both", padx=10, pady=10)

        self.text_output = tk.Text(
            text_frame,
            wrap=tk.WORD,
            font=("Courier New", 10),
            background="#ffffff",
            borderwidth=1,
            relief="solid"
        )
        self.text_output.pack(side=tk.LEFT, expand=True, fill="both")
        self.text_output.config(state=tk.DISABLED)

        if DND_AVAILABLE:
            self.text_output.drop_target_register(DND_FILES)
            self.text_output.dnd_bind('<<Drop>>', self.drop_file)

        self.botoes_frame = ttk.Frame(self)
        self.botoes_frame.pack(pady=5)

        self.btn_pesquisar = ttk.Button(
            self.botoes_frame,
            text="🔎 Pesquisar Online",
            command=self.pesquisar_online
        )
        self.btn_pesquisar.grid(row=0, column=0, padx=5)

        self.btn_copiar = ttk.Button(
            self.botoes_frame,
            text="📋 Copiar Resultado",
            command=self.copiar_resultado
        )
        self.btn_copiar.grid(row=0, column=1, padx=5)

        self.status = ttk.Label(self, text="Pronto", relief=tk.SUNKEN, anchor="w")
        self.status.pack(fill=tk.X, side=tk.BOTTOM)

    def _criar_menu(self):
        menu_bar = tk.Menu(self)

        arquivo_menu = tk.Menu(menu_bar, tearoff=0)
        arquivo_menu.add_command(label="📂 Abrir Arquivo", command=self.abrir_arquivo)
        arquivo_menu.add_command(label="💾 Salvar Relatório", command=self.salvar_relatorio)
        arquivo_menu.add_separator()
        arquivo_menu.add_command(label="❌ Sair", command=self.quit)
        menu_bar.add_cascade(label="Arquivo", menu=arquivo_menu)

        exportar_menu = tk.Menu(menu_bar, tearoff=0)
        exportar_menu.add_command(label="💾 Exportar JSON", command=self.exportar_json)
        exportar_menu.add_command(label="💾 Exportar CSV", command=self.exportar_csv)
        menu_bar.add_cascade(label="Exportar", menu=exportar_menu)

        tema_menu = tk.Menu(menu_bar, tearoff=0)
        tema_menu.add_command(label="🌙 Modo Escuro", command=self._alternar_tema)
        menu_bar.add_cascade(label="Tema", menu=tema_menu)

        self.config(menu=menu_bar)

    def abrir_arquivo(self):
        filepath = filedialog.askopenfilename(filetypes=[("Executáveis ou DLLs", "*.dll *.exe")])
        if filepath:
            self._analisar_e_exibir(filepath)

    def salvar_relatorio(self):
        conteudo = self.text_output.get(1.0, tk.END).strip()
        if not conteudo:
            messagebox.showwarning("Aviso", "Nada para salvar!")
            return

        arquivo = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Texto", "*.txt")])
        if arquivo:
            with open(arquivo, "w", encoding="utf-8") as f:
                f.write(conteudo)
            messagebox.showinfo("Sucesso", "Relatório salvo com sucesso.")

    def exportar_json(self):
        self._exportar("json")

    def exportar_csv(self):
        self._exportar("csv")

    def _exportar(self, formato):
        conteudo = self.text_output.get(1.0, tk.END).strip()
        if not conteudo:
            messagebox.showwarning("Aviso", f"Nada para exportar para {formato.upper()}!")
            return

        try:
            dados = {"resultado": conteudo.split("\n")}
            extensao = ".json" if formato == "json" else ".csv"
            arquivo = filedialog.asksaveasfilename(defaultextension=extensao, filetypes=[(formato.upper(), f"*{extensao}")])
            if arquivo:
                if formato == "json":
                    with open(arquivo, "w", encoding="utf-8") as f:
                        json.dump(dados, f, ensure_ascii=False, indent=4)
                else:
                    with open(arquivo, "w", newline='', encoding="utf-8") as f:
                        writer = csv.writer(f)
                        writer.writerows([[linha] for linha in conteudo.split("\n")])
                messagebox.showinfo("Sucesso", f"Relatório exportado como {formato.upper()}.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar {formato.upper()}: {e}")

    def pesquisar_online(self):
        if not self.arquivo_analisado:
            messagebox.showinfo("Info", "Nenhum arquivo analisado ainda.")
            return
        nome_arquivo = os.path.basename(self.arquivo_analisado)
        query = f"https://www.google.com/search?q={nome_arquivo}"
        webbrowser.open(query)

    def copiar_resultado(self):
        conteudo = self.text_output.get(1.0, tk.END).strip()
        if conteudo:
            self.clipboard_clear()
            self.clipboard_append(conteudo)
            self.status.config(text="Resultado copiado para a área de transferência.")
        else:
            self.status.config(text="Nada para copiar.")

    def buscar_texto(self):
        termo = self.search_var.get().strip()
        if not termo:
            return
        self.text_output.tag_remove("highlight", "1.0", tk.END)
        start = "1.0"
        while True:
            pos = self.text_output.search(termo, start, stopindex=tk.END, nocase=True)
            if not pos:
                break
            end = f"{pos}+{len(termo)}c"
            self.text_output.tag_add("highlight", pos, end)
            self.text_output.tag_config("highlight", background="yellow")
            start = end
        self.status.config(text=f"Busca por '{termo}' concluída.")

    def drop_file(self, event):
        filepath = event.data.strip('{}')
        if not (filepath.lower().endswith(".dll") or filepath.lower().endswith(".exe")):
            messagebox.showerror("Erro", "Por favor, selecione um arquivo .dll ou .exe")
            return
        self._analisar_e_exibir(filepath)

    def _analisar_e_exibir(self, filepath):
        self.status.config(text=f"Analisando: {os.path.basename(filepath)}...")
        self.update_idletasks()
        
        resultado = analisar_dll(filepath)
        self.arquivo_analisado = filepath

        self.text_output.config(state=tk.NORMAL)
        self.text_output.delete(1.0, tk.END)
        self.text_output.insert(tk.END, resultado)
        self.text_output.config(state=tk.DISABLED)

        self.status.config(text="Análise concluída")

    def _alternar_tema(self):
        self.modo_escuro = not self.modo_escuro
        if self.modo_escuro:
            self._aplicar_tema_escuro()
        else:
            self._aplicar_tema_claro()

    def _aplicar_tema_claro(self):
        self.configure(bg="#f0f0f0")
        self.text_output.configure(bg="white", fg="black", insertbackground="black")

    def _aplicar_tema_escuro(self):
        self.configure(bg="#121212")
        self.text_output.configure(
            bg="#1e1e1e",
            fg="#e0e0e0",
            insertbackground="#bb86fc",  # cursor roxo claro
            selectbackground="#3a3a3a",  # seleção mais suave
            selectforeground="#ffffff"
        )
        style = ttk.Style(self)
        style.theme_use('clam')

        style.configure('TLabel',
                        background="#121212",
                        foreground="#e0e0e0",
                        font=("Segoe UI", 12))
        style.configure('TButton',
                        background="#2c2c2c",
                        foreground="#e0e0e0",
                        font=("Segoe UI", 10),
                        borderwidth=1)
        style.map('TButton',
                  background=[('active', '#bb86fc')], foreground=[('active', '#121212')])

        style.configure('TEntry',
                        fieldbackground="#2c2c2c",
                        foreground="#e0e0e0",
                        insertcolor="#bb86fc")

        self.botoes_frame.configure(style='TFrame')
        self.instrucoes.configure(style='TLabel')
        self.status.configure(background="#121212", foreground="#e0e0e0")
        self.text_output.tag_config("highlight", background="#bb86fc", foreground="#121212")


if __name__ == "__main__":
    app = App()
    app.mainloop()
