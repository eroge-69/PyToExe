import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, colorchooser
import json
import time
import os
import sys # <-- NOVO: Importar o módulo sys para argumentos de linha de comando

class PyNotePlus:
    def __init__(self, root):
        self.root = root
        self.root.title("Sem Título - PyNote+")
        self.root.geometry("800x600")

        self.current_file_path = None
        self.default_bg = "#FFFFFF"
        self.default_fg = "#000000"

        self.text_area = scrolledtext.ScrolledText(
            self.root, 
            wrap=tk.WORD, 
            undo=True,
            font=("Consolas", 12),
            bg=self.default_bg,
            fg=self.default_fg,
            insertbackground=self.default_fg
        )
        self.text_area.pack(expand=True, fill='both')

        self.create_menu()

        self.root.bind('<Control-n>', self.new_file)
        self.root.bind('<Control-o>', self.open_file)
        self.root.bind('<Control-s>', self.save_file)
        self.root.bind('<Control-S>', self.save_as_file)

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Abrir...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Salvar", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Salvar Como...", accelerator="Ctrl+Shift+S", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Desfazer", command=self.text_area.edit_undo)
        edit_menu.add_command(label="Refazer", command=self.text_area.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Recortar", command=lambda: self.text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copiar", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Colar", command=lambda: self.text_area.event_generate("<<Paste>>"))

        format_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Formatar", menu=format_menu)
        format_menu.add_command(label="Cor de Fundo...", command=self.change_background_color)
        format_menu.add_command(label="Cor do Texto (Padrão)...", command=self.change_default_text_color)
        format_menu.add_command(label="Cor do Texto (Seleção)...", command=self.change_selected_text_color)

    def update_title(self):
        if self.current_file_path:
            self.root.title(f"{os.path.basename(self.current_file_path)} - PyNote+")
        else:
            self.root.title("Sem Título - PyNote+")

    def new_file(self, event=None):
        self.text_area.delete('1.0', tk.END)
        self.current_file_path = None
        self.text_area.config(bg=self.default_bg, fg=self.default_fg, insertbackground=self.default_fg)
        self.update_title()
        for tag in self.text_area.tag_names():
            if tag.startswith("color_"):
                self.text_area.tag_delete(tag)

    # REATORAÇÃO: A função "Abrir" agora apenas pega o caminho e chama a lógica principal
    def open_file(self, event=None):
        file_path = filedialog.askopenfilename(
            defaultextension=".pynote",
            filetypes=[("PyNote+ Files", "*.pynote"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.load_file(file_path)

    # NOVO MÉTODO: Contém a lógica de carregamento real do arquivo, pode ser chamado de qualquer lugar
    def load_file(self, file_path):
        if not file_path:
            return
        try:
            self.new_file() # Limpa o editor atual
            self.current_file_path = file_path
            
            if file_path.endswith('.pynote'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    
                    bg_color = data['metadata'].get('background_color', self.default_bg)
                    fg_color = data['metadata'].get('default_foreground_color', self.default_fg)
                    self.text_area.config(bg=bg_color, fg=fg_color, insertbackground=fg_color)
                    
                    self.text_area.insert('1.0', data['content'])
                    
                    for tag_info in data['tags']:
                        tag_name = tag_info['name']
                        self.text_area.tag_configure(tag_name, **tag_info['config'])
                        for start, end in tag_info['ranges']:
                            self.text_area.tag_add(tag_name, start, end)
            else:
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.text_area.insert('1.0', file.read())
            
            self.update_title()
            self.text_area.edit_reset() # Limpa o histórico de undo/redo ao abrir

        except Exception as e:
            messagebox.showerror("Erro ao Abrir", f"Não foi possível ler o arquivo.\n\nErro: {e}")
            self.new_file()

    def save_file(self, event=None):
        if self.current_file_path:
            self._save_logic(self.current_file_path)
        else:
            self.save_as_file()

    def save_as_file(self, event=None):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".pynote",
            filetypes=[("PyNote+ Files", "*.pynote"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if not file_path:
            return
        self._save_logic(file_path)

    def _save_logic(self, file_path):
        try:
            if file_path.endswith('.txt'):
                content = self.text_area.get('1.0', tk.END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
            else:
                content = self.text_area.get('1.0', 'end-1c')
                tags_data = []
                tag_names = [tag for tag in self.text_area.tag_names() if tag.startswith("color_")]
                
                for tag_name in tag_names:
                    tag_ranges = self.text_area.tag_ranges(tag_name)
                    if tag_ranges:
                        ranges_as_strings = [ (str(tag_ranges[i]), str(tag_ranges[i+1])) for i in range(0, len(tag_ranges), 2) ]
                        tags_data.append({
                            'name': tag_name,
                            'config': {'foreground': self.text_area.tag_cget(tag_name, 'foreground')},
                            'ranges': ranges_as_strings
                        })
                data_to_save = {
                    'metadata': {
                        'background_color': self.text_area.cget('bg'),
                        'default_foreground_color': self.text_area.cget('fg')
                    },
                    'content': content,
                    'tags': tags_data
                }
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data_to_save, file, indent=2)
            self.current_file_path = file_path
            self.update_title()
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo.\n\nErro: {e}")

    def change_background_color(self):
        color_code = colorchooser.askcolor(title="Escolha a Cor de Fundo")
        if color_code and color_code[1]:
            self.text_area.config(bg=color_code[1])
            
    def change_default_text_color(self):
        color_code = colorchooser.askcolor(title="Escolha a Cor Padrão do Texto")
        if color_code and color_code[1]:
            self.text_area.config(fg=color_code[1], insertbackground=color_code[1])
            
    def change_selected_text_color(self):
        try:
            if self.text_area.tag_ranges("sel"):
                color_code = colorchooser.askcolor(title="Escolha a Cor do Texto Selecionado")
                if color_code and color_code[1]:
                    tag_name = f"color_{int(time.time() * 1000000)}"
                    self.text_area.tag_configure(tag_name, foreground=color_code[1])
                    self.text_area.tag_add(tag_name, "sel.first", "sel.last")
        except tk.TclError:
            pass

# <-- MUDANÇA PRINCIPAL AQUI -->
if __name__ == "__main__":
    root = tk.Tk()
    app = PyNotePlus(root)

    # Verifica se um argumento de linha de comando (caminho do arquivo) foi passado
    # sys.argv é a lista de argumentos. sys.argv[0] é o nome do script.
    # Se len(sys.argv) > 1, então o segundo item (índice 1) é o nosso arquivo.
    if len(sys.argv) > 1:
        file_path_from_args = sys.argv[1]
        # Verifica se o caminho é válido antes de tentar carregar
        if os.path.isfile(file_path_from_args):
            app.load_file(file_path_from_args)
        else:
            messagebox.showwarning("Arquivo não encontrado", f"O arquivo '{file_path_from_args}' não foi encontrado.")

    root.mainloop()