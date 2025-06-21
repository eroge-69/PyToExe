# notapro.py
# Requer Python 3 com Tkinter (geralmente incluído por padrão)

import tkinter as tk
from tkinter import filedialog, messagebox, font, colorchooser, simpledialog
import json
import os
from datetime import datetime

class FindDialog(tk.Toplevel):
    """Janela de diálogo para Localizar e Substituir."""
    def __init__(self, master, text_widget):
        super().__init__(master)
        self.transient(master)
        self.title("Localizar e Substituir")
        self.text_widget = text_widget
        self.geometry("350x130")
        self.resizable(False, False)

        tk.Label(self, text="Localizar:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.find_entry = tk.Entry(self)
        self.find_entry.grid(row=0, column=1, padx=5, pady=5, sticky="we")

        tk.Label(self, text="Substituir por:").grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.replace_entry = tk.Entry(self)
        self.replace_entry.grid(row=1, column=1, padx=5, pady=5, sticky="we")

        button_frame = tk.Frame(self)
        button_frame.grid(row=2, column=0, columnspan=2, pady=10)

        tk.Button(button_frame, text="Localizar Próximo", command=self.find_next).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Substituir", command=self.replace).pack(side=tk.LEFT, padx=5)
        tk.Button(button_frame, text="Substituir Todos", command=self.replace_all).pack(side=tk.LEFT, padx=5)
        
        self.find_entry.focus_set()
        self.protocol("WM_DELETE_WINDOW", self.destroy)

    def find_next(self, start_index=None):
        self.text_widget.tag_remove('found', '1.0', tk.END)
        find_text = self.find_entry.get()
        if not find_text:
            return

        start = start_index or self.text_widget.index(tk.INSERT)
        pos = self.text_widget.search(find_text, start, stopindex=tk.END)
        if not pos:
            messagebox.showinfo("Fim da Busca", f"Não foi possível encontrar \"{find_text}\"", parent=self)
            return None
        
        end_pos = f"{pos}+{len(find_text)}c"
        self.text_widget.tag_add('found', pos, end_pos)
        self.text_widget.mark_set(tk.INSERT, end_pos)
        self.text_widget.see(tk.INSERT)
        self.text_widget.focus_set()
        self.text_widget.tag_config('found', background='yellow', foreground='black')
        return pos

    def replace(self):
        if not self.text_widget.tag_ranges("sel"):
            self.find_next()
            return
        
        if self.find_entry.get() != self.text_widget.get("sel.first", "sel.last"):
            self.find_next()
            return

        replace_text = self.replace_entry.get()
        self.text_widget.delete("sel.first", "sel.last")
        self.text_widget.insert("sel.first", replace_text)
        self.find_next(self.text_widget.index("sel.first"))

    def replace_all(self):
        find_text = self.find_entry.get()
        replace_text = self.replace_entry.get()
        if not find_text:
            return

        count = 0
        start_index = '1.0'
        while True:
            pos = self.text_widget.search(find_text, start_index, stopindex=tk.END)
            if not pos:
                break
            end_pos = f"{pos}+{len(find_text)}c"
            self.text_widget.delete(pos, end_pos)
            self.text_widget.insert(pos, replace_text)
            start_index = pos
            count += 1
        
        if count > 0:
            messagebox.showinfo("Substituir Tudo", f"{count} ocorrência(s) substituída(s).", parent=self)


class NotaPro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sem Título - NotaPro")
        self.geometry("800x600")

        self.current_file_path = None
        self.text_changed = False
        self.style_counter = 0 # Para criar nomes de tags únicos

        # Configurações padrão
        self.default_font = ("Consolas", 12, "normal")
        self.zoom_level = 100

        self._create_widgets()
        self._create_menu()
        self._bind_shortcuts()

        self.protocol("WM_DELETE_WINDOW", self._exit_app)
        self.text_widget.bind("<<Modified>>", self._on_text_change)

    def _create_widgets(self):
        # --- Área de Texto Principal ---
        self.text_widget = tk.Text(self, undo=True, wrap=tk.WORD, font=self.default_font)
        self.text_widget.pack(expand=True, fill='both')

        # --- Barra de Status ---
        self.status_bar_frame = tk.Frame(self, bd=1, relief=tk.SUNKEN)
        self.status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)

        self.line_col_label = tk.Label(self.status_bar_frame, text="Lin: 1, Col: 1", width=20, anchor='w')
        self.line_col_label.pack(side=tk.LEFT, padx=5)

        self.char_count_label = tk.Label(self.status_bar_frame, text="Caracteres: 0", width=20, anchor='w')
        self.char_count_label.pack(side=tk.LEFT, padx=5)
        
        self.zoom_label = tk.Label(self.status_bar_frame, text=f"Zoom: {self.zoom_level}%", width=15, anchor='e')
        self.zoom_label.pack(side=tk.RIGHT, padx=5)

        self.encoding_label = tk.Label(self.status_bar_frame, text="UTF-8", width=10, anchor='e')
        self.encoding_label.pack(side=tk.RIGHT, padx=5)
        
        # Eventos para atualizar a barra de status
        self.text_widget.bind("<KeyRelease>", self._update_status_bar)
        self.text_widget.bind("<ButtonRelease-1>", self._update_status_bar)
        self._update_status_bar()

    def _create_menu(self):
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        # --- Menu Arquivo ---
        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo", accelerator="Ctrl+N", command=self._new_file)
        file_menu.add_command(label="Abrir...", accelerator="Ctrl+O", command=self._open_file)
        file_menu.add_command(label="Salvar", accelerator="Ctrl+S", command=self._save_file)
        file_menu.add_command(label="Salvar Como...", command=self._save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Configurar Página...", command=self._unimplemented) # Placeholder
        file_menu.add_command(label="Imprimir...", command=self._unimplemented) # Placeholder
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self._exit_app)

        # --- Menu Editar ---
        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Desfazer", accelerator="Ctrl+Z", command=self.text_widget.edit_undo)
        edit_menu.add_command(label="Refazer", accelerator="Ctrl+Y", command=self.text_widget.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Recortar", accelerator="Ctrl+X", command=lambda: self.text_widget.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copiar", accelerator="Ctrl+C", command=lambda: self.text_widget.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Colar", accelerator="Ctrl+V", command=lambda: self.text_widget.event_generate("<<Paste>>"))
        edit_menu.add_command(label="Excluir", accelerator="Del", command=lambda: self.text_widget.event_generate("<<Clear>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Localizar...", accelerator="Ctrl+F", command=self._find_replace)
        edit_menu.add_command(label="Localizar Próxima", accelerator="F3", command=self._find_next)
        edit_menu.add_command(label="Substituir...", accelerator="Ctrl+H", command=self._find_replace)
        edit_menu.add_command(label="Ir para...", accelerator="Ctrl+G", command=self._go_to_line)
        edit_menu.add_separator()
        edit_menu.add_command(label="Selecionar Tudo", accelerator="Ctrl+A", command=self._select_all)
        edit_menu.add_command(label="Data/Hora", accelerator="F5", command=self._insert_datetime)

        # --- Menu Formatar ---
        format_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Formatar", menu=format_menu)
        self.wrap_var = tk.BooleanVar(value=True)
        format_menu.add_checkbutton(label="Quebra Automática de Linha", onvalue=True, offvalue=False, variable=self.wrap_var, command=self._toggle_word_wrap)
        format_menu.add_command(label="Fonte Padrão...", command=lambda: self._change_font(is_selection=False))
        format_menu.add_separator()
        format_menu.add_command(label="Alterar Fonte do Trecho...", command=lambda: self._change_font(is_selection=True))
        format_menu.add_command(label="Alterar Cor do Trecho...", command=self._change_selection_color)
        format_menu.add_separator()
        format_menu.add_command(label="Cor do Texto Padrão...", command=self._change_default_text_color)
        format_menu.add_command(label="Cor de Fundo...", command=self._change_bg_color)
        
        # --- Menu Exibir ---
        view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Exibir", menu=view_menu)
        zoom_menu = tk.Menu(view_menu, tearoff=0)
        view_menu.add_cascade(label="Zoom", menu=zoom_menu)
        zoom_menu.add_command(label="Aumentar", accelerator="Ctrl++", command=lambda: self._zoom(10))
        zoom_menu.add_command(label="Diminuir", accelerator="Ctrl+-", command=lambda: self._zoom(-10))
        zoom_menu.add_command(label="Restaurar Zoom Padrão", accelerator="Ctrl+0", command=lambda: self._zoom(0))
        view_menu.add_separator()
        self.status_bar_var = tk.BooleanVar(value=True)
        view_menu.add_checkbutton(label="Barra de Status", onvalue=True, offvalue=False, variable=self.status_bar_var, command=self._toggle_status_bar)

    def _bind_shortcuts(self):
        self.bind("<Control-n>", lambda event: self._new_file())
        self.bind("<Control-o>", lambda event: self._open_file())
        self.bind("<Control-s>", lambda event: self._save_file())
        self.bind("<Control-a>", lambda event: self._select_all())
        self.bind("<Control-f>", lambda event: self._find_replace())
        self.bind("<F3>", lambda event: self._find_next())
        self.bind("<Control-h>", lambda event: self._find_replace())
        self.bind("<Control-g>", lambda event: self._go_to_line())
        self.bind("<F5>", lambda event: self._insert_datetime())
        self.bind("<Control-plus>", lambda event: self._zoom(10))
        self.bind("<Control-minus>", lambda event: self._zoom(-10))
        self.bind("<Control-0>", lambda event: self._zoom(0))
        # Ctrl+Y para refazer (Tkinter padrão é Shift+Ctrl+Z)
        self.bind("<Control-y>", lambda event: self.text_widget.edit_redo())

    # --- Funções de Arquivo ---
    def _new_file(self):
        if self._check_unsaved_changes():
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.edit_reset() # Limpa histórico de undo/redo
            self.current_file_path = None
            self.title("Sem Título - NotaPro")
            self.text_changed = False
            # Resetar todas as tags de estilo
            for tag in self.text_widget.tag_names():
                if tag.startswith("style_"):
                    self.text_widget.tag_delete(tag)

    def _open_file(self):
        if not self._check_unsaved_changes():
            return
        
        filepath = filedialog.askopenfilename(
            filetypes=[("Arquivos NotaPro", "*.npro"), ("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        if not filepath:
            return

        try:
            self._new_file() # Limpa o editor antes de abrir
            if filepath.endswith('.npro'):
                self._load_npro_file(filepath)
            else:
                with open(filepath, "r", encoding='utf-8') as f:
                    self.text_widget.insert("1.0", f.read())
            
            self.current_file_path = filepath
            self.title(f"{os.path.basename(filepath)} - NotaPro")
            self.text_widget.edit_modified(False) # Marca como não modificado
            self.text_changed = False
            self._update_status_bar()
        except Exception as e:
            messagebox.showerror("Erro ao Abrir", f"Não foi possível abrir o arquivo:\n{e}")

    def _save_file(self):
        if self.current_file_path:
            self._save_to_path(self.current_file_path)
        else:
            self._save_as_file()

    def _save_as_file(self):
        filepath = filedialog.asksaveasfilename(
            defaultextension=".npro",
            filetypes=[("Arquivos NotaPro", "*.npro"), ("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        if not filepath:
            return
        self._save_to_path(filepath)

    def _save_to_path(self, filepath):
        try:
            if filepath.endswith('.npro'):
                self._save_npro_file(filepath)
            else:
                content = self.text_widget.get("1.0", tk.END)
                with open(filepath, "w", encoding='utf-8') as f:
                    f.write(content)
            
            self.current_file_path = filepath
            self.title(f"{os.path.basename(filepath)} - NotaPro")
            self.text_widget.edit_modified(False)
            self.text_changed = False
        except Exception as e:
            messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{e}")

    # --- Funções de Formato Proprietário (.npro) ---
    def _save_npro_file(self, filepath):
        font_tuple = self.text_widget.cget("font")
        current_font = font.Font(font=font_tuple)
        
        data = {
            "global_config": {
                "background": self.text_widget.cget("bg"),
                "foreground": self.text_widget.cget("fg"),
                "font": [current_font.actual("family"), current_font.actual("size"), current_font.actual("weight")]
            },
            "content": self.text_widget.get("1.0", tk.END),
            "tags": []
        }

        for tag_name in self.text_widget.tag_names():
            if tag_name.startswith("style_"):
                ranges = self.text_widget.tag_ranges(tag_name)
                for i in range(0, len(ranges), 2):
                    start, end = ranges[i], ranges[i+1]
                    tag_config = self.text_widget.tag_cget(tag_name, "font")
                    if tag_config:
                        tag_font = font.Font(font=tag_config)
                        font_details = [tag_font.actual("family"), tag_font.actual("size"), tag_font.actual("weight"), tag_font.actual("slant")]
                    else:
                        font_details = None

                    data["tags"].append({
                        "name": tag_name,
                        "start": str(start),
                        "end": str(end),
                        "config": {
                            "foreground": self.text_widget.tag_cget(tag_name, "foreground"),
                            "font": font_details,
                        }
                    })
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)

    def _load_npro_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Aplicar configurações globais
        config = data.get("global_config", {})
        self.text_widget.config(
            bg=config.get("background", "white"),
            fg=config.get("foreground", "black"),
            font=tuple(config.get("font", self.default_font))
        )

        self.text_widget.insert("1.0", data.get("content", ""))

        # Aplicar tags de estilo
        for tag_info in data.get("tags", []):
            tag_name = tag_info["name"]
            start, end = tag_info["start"], tag_info["end"]
            tag_config = tag_info["config"]
            
            font_config = tuple(tag_config.get("font")) if tag_config.get("font") else None
            
            self.text_widget.tag_add(tag_name, start, end)
            self.text_widget.tag_config(
                tag_name,
                foreground=tag_config.get("foreground"),
                font=font_config
            )
            
            # Atualizar o contador de estilos para evitar colisões
            if tag_name.startswith("style_"):
                try:
                    num = int(tag_name.split("_")[1])
                    if num >= self.style_counter:
                        self.style_counter = num + 1
                except (ValueError, IndexError):
                    pass


    # --- Funções de Edição ---
    def _find_replace(self):
        FindDialog(self, self.text_widget)

    def _find_next(self):
        # Uma versão simplificada se a janela de busca não estiver aberta
        messagebox.showinfo("Localizar", "Use Ctrl+F para abrir a janela de busca e então use 'Localizar Próximo'.")

    def _go_to_line(self):
        if self.wrap_var.get():
            messagebox.showwarning("Aviso", "Desative a 'Quebra Automática de Linha' para usar 'Ir para'.")
            return
        
        line_num = simpledialog.askinteger("Ir para Linha", "Número da linha:", parent=self, minvalue=1)
        if line_num:
            self.text_widget.mark_set(tk.INSERT, f"{line_num}.0")
            self.text_widget.see(f"{line_num}.0")
            self.text_widget.focus_set()

    def _select_all(self):
        self.text_widget.tag_add(tk.SEL, "1.0", tk.END)
        self.text_widget.mark_set(tk.INSERT, "1.0")
        self.text_widget.see(tk.INSERT)
        return "break" # Impede o comportamento padrão

    def _insert_datetime(self):
        now = datetime.now().strftime("%H:%M %d/%m/%Y")
        self.text_widget.insert(tk.INSERT, now)
    
    # --- Funções de Formatação ---
    def _toggle_word_wrap(self):
        if self.wrap_var.get():
            self.text_widget.config(wrap=tk.WORD)
        else:
            self.text_widget.config(wrap=tk.NONE)

    def _change_font(self, is_selection):
        try:
            current_font = font.Font(font=self.text_widget.cget("font"))
            if is_selection and self.text_widget.tag_ranges(tk.SEL):
                # Se houver seleção, usa a fonte da seleção como base
                tags = self.text_widget.tag_names("sel.first")
                for t in reversed(tags):
                    if t.startswith("style_"):
                        current_font = font.Font(font=self.text_widget.tag_cget(t, "font"))
                        break

            font_tuple = font.askfont(self, family=current_font.actual("family"), size=current_font.actual("size"), weight=current_font.actual("weight"), slant=current_font.actual("slant"))
            
            if font_tuple:
                new_font = font.Font(family=font_tuple['family'], size=font_tuple['size'], weight=font_tuple['weight'], slant=font_tuple['slant'])
                if is_selection and self.text_widget.tag_ranges(tk.SEL):
                    tag_name = f"style_{self.style_counter}"
                    self.style_counter += 1
                    self.text_widget.tag_add(tag_name, "sel.first", "sel.last")
                    self.text_widget.tag_config(tag_name, font=new_font)
                else:
                    self.text_widget.config(font=new_font)
                    self.default_font = new_font.actual()
                    self._on_text_change(None) # Marca como modificado
        except Exception as e:
            messagebox.showerror("Erro de Fonte", f"Não foi possível aplicar a fonte: {e}")

    def _change_selection_color(self):
        if self.text_widget.tag_ranges(tk.SEL):
            color = colorchooser.askcolor(title="Escolha a cor do texto")
            if color and color[1]:
                tag_name = f"style_{self.style_counter}"
                self.style_counter += 1
                self.text_widget.tag_add(tag_name, "sel.first", "sel.last")
                self.text_widget.tag_config(tag_name, foreground=color[1])
                self._on_text_change(None)
        else:
            messagebox.showinfo("Nenhuma Seleção", "Selecione um trecho de texto para alterar a cor.")
    
    def _change_default_text_color(self):
        color = colorchooser.askcolor(title="Escolha a cor do texto padrão")
        if color and color[1]:
            self.text_widget.config(fg=color[1])
            self._on_text_change(None)

    def _change_bg_color(self):
        color = colorchooser.askcolor(title="Escolha a cor de fundo")
        if color and color[1]:
            self.text_widget.config(bg=color[1])
            self._on_text_change(None)

    # --- Funções de Exibição ---
    def _zoom(self, amount):
        current_font = font.Font(font=self.text_widget.cget("font"))
        new_size = current_font.actual("size")
        
        if amount == 0: # Reset
            self.zoom_level = 100
            new_size = self.default_font[1] # Usa o tamanho da fonte padrão
        else:
            self.zoom_level += amount
            if self.zoom_level < 10: self.zoom_level = 10
            new_size = int(self.default_font[1] * (self.zoom_level / 100))

        # Atualiza a fonte padrão com o novo tamanho
        base_font_name = font.Font(font=self.text_widget.cget("font")).actual("family")
        self.text_widget.config(font=(base_font_name, new_size))
        
        # Atualiza todas as tags de estilo com o novo zoom
        for tag_name in self.text_widget.tag_names():
            if tag_name.startswith("style_"):
                tag_font_config = self.text_widget.tag_cget(tag_name, "font")
                if tag_font_config:
                    tag_font = font.Font(font=tag_font_config)
                    original_size = tag_font.actual("size") # Deveríamos salvar o tamanho original na tag
                    new_tag_size = int(original_size * (self.zoom_level/100)) # Simplificação: recalcula baseado no tamanho atual
                    # Uma abordagem melhor seria salvar o tamanho base na criação da tag
                    self.text_widget.tag_config(tag_name, font=(tag_font.actual("family"), new_tag_size, tag_font.actual("weight"), tag_font.actual("slant")))
        
        self.zoom_label.config(text=f"Zoom: {self.zoom_level}%")

    def _toggle_status_bar(self):
        if self.status_bar_var.get():
            self.status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        else:
            self.status_bar_frame.pack_forget()

    # --- Funções de Utilitários e Eventos ---
    def _update_status_bar(self, event=None):
        row, col = self.text_widget.index(tk.INSERT).split('.')
        char_count = len(self.text_widget.get("1.0", "end-1c")) # -1c para não contar o newline final
        self.line_col_label.config(text=f"Lin: {row}, Col: {int(col) + 1}")
        self.char_count_label.config(text=f"Caracteres: {char_count}")

    def _on_text_change(self, event=None):
        if self.text_widget.edit_modified():
            self.text_changed = True
            if not self.title().startswith("*"):
                self.title("*" + self.title())
        else: # O estado modificado foi resetado (ex: após salvar)
            self.text_changed = False
            if self.title().startswith("*"):
                self.title(self.title()[1:])
        
        # Precisa chamar o update da barra de status explicitamente aqui também
        self._update_status_bar()

    def _check_unsaved_changes(self):
        if self.text_changed:
            response = messagebox.askyesnocancel("NotaPro", f"Deseja salvar as alterações em {self.title().strip('*')}?")
            if response is True:  # Sim
                self._save_file()
                return not self.text_changed # Retorna True se o salvamento foi bem-sucedido
            elif response is False: # Não
                return True
            else: # Cancelar
                return False
        return True

    def _exit_app(self):
        if self._check_unsaved_changes():
            self.destroy()

    def _unimplemented(self):
        messagebox.showinfo("Não Implementado", "Esta funcionalidade ainda não foi implementada.")

if __name__ == "__main__":
    app = NotaPro()
    app.mainloop()