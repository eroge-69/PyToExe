import tkinter as tk
from tkinter import scrolledtext, filedialog, messagebox, colorchooser, font
import json
import time
import os
import sys
from datetime import datetime

# --- Classes de Diálogo Auxiliares ---

class FindDialog(tk.Toplevel):
    """Caixa de diálogo para a funcionalidade de Localizar."""
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent)
        self.parent = parent
        self.title("Localizar")
        self.geometry("350x120")
        self.resizable(False, False)

        self.last_find_index = "1.0"
        
        # UI Elements
        top_frame = tk.Frame(self)
        top_frame.pack(pady=10, padx=10, fill="x")

        tk.Label(top_frame, text="Localizar:").pack(side="left")
        self.find_entry = tk.Entry(top_frame)
        self.find_entry.pack(side="left", expand=True, fill="x", padx=5)
        self.find_entry.focus_set()

        # Checkbox para 'Diferenciar maiúsculas/minúsculas'
        self.case_sensitive = tk.BooleanVar()
        self.case_check = tk.Checkbutton(self, text="Diferenciar maiúsculas/minúsculas", variable=self.case_sensitive)
        self.case_check.pack(anchor="w", padx=10)
        
        # Botões
        button_frame = tk.Frame(self)
        button_frame.pack(pady=5, padx=10, fill="x")
        
        self.find_next_button = tk.Button(button_frame, text="Localizar Próxima", command=self.find_next)
        self.find_next_button.pack(side="right")
        
        cancel_button = tk.Button(button_frame, text="Cancelar", command=self.destroy)
        cancel_button.pack(side="right", padx=5)

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.bind('<Return>', self.find_next)

    def find_next(self, event=None):
        search_term = self.find_entry.get()
        if search_term:
            self.parent.find_text(search_term, self.case_sensitive.get(), self.last_find_index)

    def on_close(self):
        # Limpa o realce ao fechar a janela
        self.parent.text_area.tag_remove("search_highlight", "1.0", tk.END)
        self.destroy()

class FontDialog(tk.Toplevel):
    """Caixa de diálogo para a escolha de fonte."""
    def __init__(self, parent, current_font):
        super().__init__(parent)
        self.transient(parent)
        self.title("Fonte")
        self.geometry("450x300")
        self.result = None

        # Dados da fonte
        self.font_family = tk.StringVar(value=current_font[0])
        self.font_size = tk.IntVar(value=current_font[1])
        self.font_style = tk.StringVar(value=current_font[2])
        
        # --- UI ---
        main_frame = tk.Frame(self, padx=10, pady=10)
        main_frame.pack(expand=True, fill="both")

        # Coluna da Família
        font_frame = tk.LabelFrame(main_frame, text="Fonte:")
        font_frame.pack(side="left", padx=5, fill="y")
        font_listbox = tk.Listbox(font_frame, exportselection=False)
        font_listbox.pack(side="left", fill="y")
        font_scrollbar = tk.Scrollbar(font_frame, command=font_listbox.yview)
        font_scrollbar.pack(side="right", fill="y")
        font_listbox.config(yscrollcommand=font_scrollbar.set)
        
        # Preencher com as fontes disponíveis no sistema
        self.font_families = sorted(font.families())
        for f in self.font_families:
            font_listbox.insert(tk.END, f)
        try:
            # Tentar selecionar a fonte atual
            idx = self.font_families.index(current_font[0])
            font_listbox.selection_set(idx)
            font_listbox.see(idx)
        except ValueError:
            pass
        font_listbox.bind('<<ListboxSelect>>', lambda e: self.font_family.set(font_listbox.get(font_listbox.curselection())))

        # Coluna do Estilo
        style_frame = tk.LabelFrame(main_frame, text="Estilo:")
        style_frame.pack(side="left", padx=5, fill="y")
        style_listbox = tk.Listbox(style_frame, exportselection=False, height=4)
        style_listbox.pack()
        self.styles = ["normal", "bold", "italic", "bold italic"]
        for s in self.styles:
            style_listbox.insert(tk.END, s)
        try:
            idx = self.styles.index(current_font[2])
            style_listbox.selection_set(idx)
        except ValueError:
            style_listbox.selection_set(0)
        style_listbox.bind('<<ListboxSelect>>', lambda e: self.font_style.set(style_listbox.get(style_listbox.curselection())))

        # Coluna do Tamanho
        size_frame = tk.LabelFrame(main_frame, text="Tamanho:")
        size_frame.pack(side="left", padx=5, fill="y")
        self.size_entry = tk.Entry(size_frame, textvariable=self.font_size, width=5)
        self.size_entry.pack()

        # Botões OK e Cancelar
        button_frame = tk.Frame(self)
        button_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        tk.Button(button_frame, text="OK", width=10, command=self.on_ok).pack(side="right")
        tk.Button(button_frame, text="Cancelar", width=10, command=self.destroy).pack(side="right", padx=5)

    def on_ok(self):
        self.result = (self.font_family.get(), self.font_size.get(), self.font_style.get())
        self.destroy()

# --- Classe Principal do Aplicativo ---

class PyNotePlus:
    def __init__(self, root):
        self.root = root
        self.root.title("Sem Título - PyNote+")
        self.root.geometry("900x650")

        # Variáveis de estado
        self.current_file_path = None
        self.find_dialog = None
        self.last_find_index = "1.0"
        
        # Configurações de fonte e zoom
        self.base_font_family = "Consolas"
        self.base_font_size = 12
        self.base_font_style = "normal"
        self.zoom_level = 100
        self.active_font = font.Font(family=self.base_font_family, size=self.base_font_size)
        
        # --- Widgets ---
        # Frame principal para texto e barra de rolagem
        text_frame = tk.Frame(self.root)
        text_frame.pack(expand=True, fill='both')
        
        self.text_area = scrolledtext.ScrolledText(
            text_frame, 
            wrap=tk.WORD, 
            undo=True,
            font=self.active_font
        )
        self.text_area.pack(expand=True, fill='both')
        self.text_area.tag_configure("search_highlight", background="yellow", foreground="black")

        # Barra de Status
        self.status_bar = tk.Label(self.root, text="Zoom: 100%", bd=1, relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        # Menus e Atalhos
        self.create_menu()
        self.bind_shortcuts()

    def update_font_and_display(self):
        """Atualiza a fonte com base no zoom e o texto da barra de status."""
        new_size = int(self.base_font_size * (self.zoom_level / 100.0))
        self.active_font.config(family=self.base_font_family, size=new_size)
        
        # Atualiza a fonte padrão do widget
        self.text_area.config(font=self.active_font)
        
        # Atualiza a barra de status
        self.status_bar.config(text=f"Zoom: {self.zoom_level}%")

    def create_menu(self):
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)

        # Arquivo
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo", accelerator="Ctrl+N", command=self.new_file)
        file_menu.add_command(label="Abrir...", accelerator="Ctrl+O", command=self.open_file)
        file_menu.add_command(label="Salvar", accelerator="Ctrl+S", command=self.save_file)
        file_menu.add_command(label="Salvar Como...", accelerator="Ctrl+Shift+S", command=self.save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.root.quit)

        # Editar
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Desfazer", accelerator="Ctrl+Z", command=self.text_area.edit_undo)
        edit_menu.add_command(label="Refazer", accelerator="Ctrl+Y", command=self.text_area.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Recortar", accelerator="Ctrl+X", command=lambda: self.text_area.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copiar", accelerator="Ctrl+C", command=lambda: self.text_area.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Colar", accelerator="Ctrl+V", command=lambda: self.text_area.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Localizar...", accelerator="Ctrl+F", command=self.open_find_dialog)
        edit_menu.add_separator()
        edit_menu.add_command(label="Data e Hora", accelerator="F5", command=self.insert_date_time)

        # Formatar
        format_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Formatar", menu=format_menu)
        format_menu.add_command(label="Fonte (Global)...", command=self.change_global_font)
        format_menu.add_command(label="Fonte (Seleção)...", command=self.change_selected_font)
        format_menu.add_separator()
        format_menu.add_command(label="Cor de Fundo...", command=self.change_background_color)
        format_menu.add_command(label="Cor do Texto (Padrão)...", command=self.change_default_text_color)
        format_menu.add_command(label="Cor do Texto (Seleção)...", command=self.change_selected_text_color)

        # Exibir
        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="Exibir", menu=view_menu)
        zoom_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Zoom", menu=zoom_menu)
        zoom_menu.add_command(label="Ampliar", accelerator="Ctrl++", command=self.zoom_in)
        zoom_menu.add_command(label="Reduzir", accelerator="Ctrl+-", command=self.zoom_out)
        zoom_menu.add_command(label="Restaurar Zoom Padrão", accelerator="Ctrl+0", command=self.reset_zoom)
    
    def bind_shortcuts(self):
        self.root.bind('<Control-n>', self.new_file)
        self.root.bind('<Control-o>', self.open_file)
        self.root.bind('<Control-s>', self.save_file)
        self.root.bind('<Control-S>', self.save_as_file)
        self.root.bind('<Control-f>', self.open_find_dialog)
        self.root.bind('<F5>', self.insert_date_time)
        self.root.bind('<Control-plus>', self.zoom_in)
        self.root.bind('<Control-minus>', self.zoom_out)
        self.root.bind('<Control-0>', self.reset_zoom)

    # --- Funcionalidades de Arquivo ---
    
    def new_file(self, event=None):
        self.text_area.delete('1.0', tk.END)
        self.current_file_path = None
        self.root.title("Sem Título - PyNote+")
        # Limpa todas as tags de formatação
        for tag in self.text_area.tag_names():
            if tag.startswith("style_"):
                self.text_area.tag_delete(tag)
        self.reset_zoom()
        self.text_area.config(bg="#FFFFFF", fg="#000000")

    def open_file(self, event=None):
        file_path = filedialog.askopenfilename(
            defaultextension=".pynote",
            filetypes=[("PyNote+ Files", "*.pynote"), ("Text Files", "*.txt"), ("All Files", "*.*")]
        )
        if file_path:
            self.load_file(file_path)

    def load_file(self, file_path):
        try:
            self.new_file()
            self.current_file_path = file_path
            
            if file_path.endswith('.pynote'):
                with open(file_path, 'r', encoding='utf-8') as file:
                    data = json.load(file)
                    metadata = data.get('metadata', {})
                    # Carregar configurações globais
                    self.text_area.config(bg=metadata.get('background_color', "#FFFFFF"))
                    self.base_font_family = metadata.get('font_family', "Consolas")
                    self.base_font_size = metadata.get('font_size', 12)
                    self.base_font_style = metadata.get('font_style', "normal")
                    self.zoom_level = metadata.get('zoom', 100)
                    self.update_font_and_display()
                    
                    self.text_area.insert('1.0', data['content'])
                    
                    # Carregar tags de estilo
                    for tag_info in data.get('tags', []):
                        tag_name = tag_info['name']
                        config = tag_info['config']
                        tag_config_dict = {}
                        if 'foreground' in config:
                            tag_config_dict['foreground'] = config['foreground']
                        if 'font' in config:
                            fam, size, style = config['font']
                            weight = "bold" if "bold" in style else "normal"
                            slant = "italic" if "italic" in style else "roman"
                            tag_font = font.Font(family=fam, size=size, weight=weight, slant=slant)
                            tag_config_dict['font'] = tag_font
                        
                        self.text_area.tag_configure(tag_name, **tag_config_dict)
                        for start, end in tag_info['ranges']:
                            self.text_area.tag_add(tag_name, start, end)
            else: # Arquivo de texto plano
                with open(file_path, 'r', encoding='utf-8') as file:
                    self.text_area.insert('1.0', file.read())
            
            self.root.title(f"{os.path.basename(file_path)} - PyNote+")
            self.text_area.edit_reset()

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
        if file_path:
            self._save_logic(file_path)

    def _save_logic(self, file_path):
        try:
            if file_path.endswith('.txt'):
                content = self.text_area.get('1.0', tk.END)
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
            else: # Salvar no formato .pynote
                content = self.text_area.get('1.0', 'end-1c')
                tags_data = []
                tag_names = [tag for tag in self.text_area.tag_names() if tag.startswith("style_")]
                
                for tag_name in tag_names:
                    tag_ranges = self.text_area.tag_ranges(tag_name)
                    if not tag_ranges: continue
                    
                    ranges_as_strings = [(str(tag_ranges[i]), str(tag_ranges[i+1])) for i in range(0, len(tag_ranges), 2)]
                    config_dict = {}
                    
                    # Salvar cor
                    fg_color = self.text_area.tag_cget(tag_name, 'foreground')
                    if fg_color:
                        config_dict['foreground'] = fg_color

                    # Salvar fonte
                    font_name = self.text_area.tag_cget(tag_name, 'font')
                    if font_name:
                        actual_font = font.Font(name=font_name, exists=True)
                        f_fam = actual_font.actual("family")
                        f_size = actual_font.actual("size")
                        f_weight = actual_font.actual("weight")
                        f_slant = actual_font.actual("slant")
                        f_style = f"{f_weight if f_weight == 'bold' else ''}{' ' if f_weight == 'bold' and f_slant == 'italic' else ''}{f_slant if f_slant == 'italic' else ''}".strip() or "normal"
                        config_dict['font'] = [f_fam, f_size, f_style]
                        
                    tags_data.append({'name': tag_name, 'config': config_dict, 'ranges': ranges_as_strings})

                data_to_save = {
                    'metadata': {
                        'background_color': self.text_area.cget('bg'),
                        'font_family': self.base_font_family,
                        'font_size': self.base_font_size,
                        'font_style': self.base_font_style,
                        'zoom': self.zoom_level
                    },
                    'content': content,
                    'tags': tags_data
                }
                with open(file_path, 'w', encoding='utf-8') as file:
                    json.dump(data_to_save, file, indent=2)

            self.current_file_path = file_path
            self.root.title(f"{os.path.basename(file_path)} - PyNote+")
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo.\n\nErro: {e}")

    # --- Funcionalidades de Edição e Formatação ---

    def open_find_dialog(self, event=None):
        if self.find_dialog is None or not self.find_dialog.winfo_exists():
            self.find_dialog = FindDialog(self.root)
            self.find_dialog.last_find_index = self.text_area.index(tk.INSERT)
        self.find_dialog.deiconify()
        self.find_dialog.focus_set()

    def find_text(self, term, case_sensitive, start_index):
        self.text_area.tag_remove("search_highlight", "1.0", tk.END)
        if not term: return

        nocase = not case_sensitive
        pos = self.text_area.search(term, start_index, stopindex=tk.END, nocase=nocase)

        if pos:
            end_pos = f"{pos}+{len(term)}c"
            self.text_area.tag_add("search_highlight", pos, end_pos)
            self.text_area.see(pos)
            if self.find_dialog:
                self.find_dialog.last_find_index = end_pos
        else: # Se não encontrar, busca do início
            if self.find_dialog:
                self.find_dialog.last_find_index = "1.0"
            messagebox.showinfo("Localizar", f"Não foi possível encontrar \"{term}\"", parent=self.find_dialog)

    def insert_date_time(self, event=None):
        current_time = datetime.now().strftime('%d/%m/%Y %H:%M:%S')
        self.text_area.insert(tk.INSERT, current_time)

    def change_global_font(self):
        current_font_tuple = (self.base_font_family, self.base_font_size, self.base_font_style)
        dialog = FontDialog(self.root, current_font_tuple)
        self.root.wait_window(dialog)
        
        if dialog.result:
            self.base_font_family, self.base_font_size, self.base_font_style = dialog.result
            self.update_font_and_display()

    def _apply_style_to_selection(self, color=None, font_tuple=None):
        if not self.text_area.tag_ranges("sel"): return
        
        tag_name = f"style_{int(time.time() * 1000000)}"
        config_dict = {}

        if color:
            config_dict['foreground'] = color

        if font_tuple:
            fam, size, style_str = font_tuple
            weight = "bold" if "bold" in style_str else "normal"
            slant = "italic" if "italic" in style_str else "roman"
            new_font = font.Font(family=fam, size=size, weight=weight, slant=slant)
            config_dict['font'] = new_font
        
        if config_dict:
            self.text_area.tag_configure(tag_name, **config_dict)
            self.text_area.tag_add(tag_name, "sel.first", "sel.last")

    def change_selected_font(self):
        # Pega a fonte do texto no início da seleção como base
        try:
            current_tags = self.text_area.tag_names("sel.first")
            font_tag = next((tag for tag in reversed(current_tags) if self.text_area.tag_cget(tag, 'font')), None)
            if font_tag:
                f_obj = font.Font(name=self.text_area.tag_cget(font_tag, 'font'), exists=True)
                fam, size, weight, slant = f_obj.actual("family"), f_obj.actual("size"), f_obj.actual("weight"), f_obj.actual("slant")
                style = f"{weight if weight == 'bold' else ''}{' ' if weight == 'bold' and slant == 'italic' else ''}{slant if slant == 'italic' else ''}".strip() or "normal"
                current_font_tuple = (fam, size, style)
            else:
                raise ValueError
        except (ValueError, tk.TclError):
            current_font_tuple = (self.base_font_family, self.base_font_size, self.base_font_style)

        dialog = FontDialog(self.root, current_font_tuple)
        self.root.wait_window(dialog)
        if dialog.result:
            self._apply_style_to_selection(font_tuple=dialog.result)

    def change_background_color(self):
        color = colorchooser.askcolor(title="Escolha a Cor de Fundo")
        if color and color[1]:
            self.text_area.config(bg=color[1])
            
    def change_default_text_color(self):
        # Esta função foi removida pois a fonte global agora controla a aparência
        messagebox.showinfo("Aviso", "Para alterar a cor padrão, mude a fonte global.")

    def change_selected_text_color(self):
        color = colorchooser.askcolor(title="Escolha a Cor do Texto")
        if color and color[1]:
            self._apply_style_to_selection(color=color[1])

    # --- Funcionalidades de Exibição (Zoom) ---

    def zoom_in(self, event=None):
        if self.zoom_level < 300: # Limite máximo
            self.zoom_level += 10
            self.update_font_and_display()

    def zoom_out(self, event=None):
        if self.zoom_level > 20: # Limite mínimo
            self.zoom_level -= 10
            self.update_font_and_display()
    
    def reset_zoom(self, event=None):
        self.zoom_level = 100
        self.update_font_and_display()

if __name__ == "__main__":
    root = tk.Tk()
    app = PyNotePlus(root)

    # Lógica para abrir arquivo via argumento de linha de comando
    if len(sys.argv) > 1:
        file_path_from_args = sys.argv[1]
        if os.path.isfile(file_path_from_args):
            app.load_file(file_path_from_args)
        else:
            messagebox.showwarning("Arquivo não encontrado", f"O arquivo '{file_path_from_args}' não foi encontrado.")

    root.mainloop()