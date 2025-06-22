# notapro.py (versão final com zoom por scroll)
# Requer Python 3 com Tkinter

import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser
import json
import os
import sys
from datetime import datetime

class NotaPro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sem Título - NotaPro")
        self.geometry("800x600")

        self.current_file_path = None
        self.text_changed = False
        self.style_counter = 0

        self.default_font_family = "Consolas"
        self.default_font_size = 12
        self.zoom_level = 100

        self._create_widgets()
        self._create_menu()
        self._bind_shortcuts()

        self.protocol("WM_DELETE_WINDOW", self._exit_app)
        self.text_widget.bind("<<Modified>>", self._on_text_change)

        if len(sys.argv) > 1:
            initial_filepath = sys.argv[1]
            if os.path.exists(initial_filepath):
                self._load_file_from_path(initial_filepath)
            else:
                messagebox.showwarning("Arquivo não encontrado", f"O arquivo '{initial_filepath}' não foi encontrado.")

    def _create_widgets(self):
        self.text_widget = tk.Text(
            self,
            undo=True,
            wrap=tk.WORD,
            font=(self.default_font_family, self.default_font_size),
            insertbackground="black"
        )
        self.text_widget.pack(expand=True, fill='both')

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
        
        self.text_widget.bind("<KeyRelease>", self._update_status_bar)
        self.text_widget.bind("<ButtonRelease-1>", self._update_status_bar)
        self._update_status_bar()

    def _create_menu(self):
        self.menu_bar = tk.Menu(self)
        self.config(menu=self.menu_bar)

        file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo", accelerator="Ctrl+N", command=self._new_file)
        file_menu.add_command(label="Abrir...", accelerator="Ctrl+O", command=self._open_file)
        file_menu.add_command(label="Salvar", accelerator="Ctrl+S", command=self._save_file)
        file_menu.add_command(label="Salvar Como...", command=self._save_as_file)
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self._exit_app)

        edit_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Desfazer", accelerator="Ctrl+Z", command=self.text_widget.edit_undo)
        edit_menu.add_command(label="Refazer", accelerator="Ctrl+Y", command=self.text_widget.edit_redo)
        edit_menu.add_separator()
        edit_menu.add_command(label="Recortar", accelerator="Ctrl+X", command=lambda: self.text_widget.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copiar", accelerator="Ctrl+C", command=lambda: self.text_widget.event_generate("<<Copy>>"))
        edit_menu.add_command(label="Colar", accelerator="Ctrl+V", command=lambda: self.text_widget.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        edit_menu.add_command(label="Selecionar Tudo", accelerator="Ctrl+A", command=self._select_all)
        edit_menu.add_command(label="Data/Hora", accelerator="F5", command=self._insert_datetime)

        format_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.menu_bar.add_cascade(label="Formatar", menu=format_menu)
        self.wrap_var = tk.BooleanVar(value=True)
        format_menu.add_checkbutton(label="Quebra Automática de Linha", onvalue=True, offvalue=False, variable=self.wrap_var, command=self._toggle_word_wrap)
        format_menu.add_command(label="Alterar Cor do Trecho...", command=self._change_selection_color)
        format_menu.add_separator()
        format_menu.add_command(label="Cor do Texto Padrão...", command=self._change_default_text_color)
        format_menu.add_command(label="Cor de Fundo...", command=self._change_bg_color)
        
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
        self.bind("<F5>", lambda event: self._insert_datetime())
        self.bind("<Control-plus>", lambda event: self._zoom(10))
        self.bind("<Control-minus>", lambda event: self._zoom(-10))
        self.bind("<Control-0>", lambda event: self._zoom(0))
        self.bind("<Control-y>", lambda event: self.text_widget.edit_redo())
        # --- NOVO: Vincula o evento de scroll do mouse ao método de zoom ---
        self.text_widget.bind("<MouseWheel>", self._zoom_on_scroll)

    # --- NOVO: Método para lidar com o zoom via scroll do mouse ---
    def _zoom_on_scroll(self, event):
        # Verifica se a tecla Ctrl está pressionada (código 0x0004 para o estado 'Control')
        if (event.state & 0x0004) != 0:
            # event.delta > 0 para scroll para cima (aumentar zoom)
            # event.delta < 0 para scroll para baixo (diminuir zoom)
            if event.delta > 0:
                self._zoom(10)
            else:
                self._zoom(-10)
            return "break" # Impede que o evento continue (e role a página)
        
    def _new_file(self):
        if self._check_unsaved_changes():
            self.text_widget.delete("1.0", tk.END)
            self.text_widget.edit_reset()
            self.current_file_path = None
            self.title("Sem Título - NotaPro")
            self.text_changed = False
            for tag in self.text_widget.tag_names():
                if tag.startswith("style_"):
                    self.text_widget.tag_delete(tag)

    def _load_file_from_path(self, filepath):
        try:
            self._new_file()
            if filepath.endswith('.npro'):
                self._load_npro_file(filepath)
            else:
                with open(filepath, "r", encoding='utf-8') as f:
                    self.text_widget.insert("1.0", f.read())
            
            self.current_file_path = filepath
            self.title(f"{os.path.basename(filepath)} - NotaPro")
            self.text_widget.edit_modified(False)
            self.text_changed = False
            self._update_status_bar()
        except Exception as e:
            messagebox.showerror("Erro ao Abrir", f"Não foi possível abrir o arquivo:\n{e}")
            self._new_file()

    def _open_file(self):
        if not self._check_unsaved_changes():
            return
        filepath = filedialog.askopenfilename(
            filetypes=[("Arquivos NotaPro", "*.npro"), ("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")]
        )
        if filepath:
            self._load_file_from_path(filepath)

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
        if filepath:
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

    def _save_npro_file(self, filepath):
        data = {
            "global_config": {"background": self.text_widget.cget("bg"), "foreground": self.text_widget.cget("fg")},
            "content": self.text_widget.get("1.0", tk.END), "tags": []
        }
        for tag_name in self.text_widget.tag_names():
            if tag_name.startswith("style_"):
                ranges = self.text_widget.tag_ranges(tag_name)
                for i in range(0, len(ranges), 2):
                    start, end = ranges[i], ranges[i+1]
                    data["tags"].append({
                        "name": tag_name, "start": str(start), "end": str(end),
                        "config": {"foreground": self.text_widget.tag_cget(tag_name, "foreground")}
                    })
        with open(filepath, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2)

    def _load_npro_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f: data = json.load(f)
        config = data.get("global_config", {})
        fg_color = config.get("foreground", "black")
        self.text_widget.config(bg=config.get("background", "white"), fg=fg_color, insertbackground=fg_color)
        self.text_widget.insert("1.0", data.get("content", ""))
        for tag_info in data.get("tags", []):
            tag_name, start, end = tag_info["name"], tag_info["start"], tag_info["end"]
            tag_config = tag_info["config"]
            self.text_widget.tag_add(tag_name, start, end)
            self.text_widget.tag_config(tag_name, foreground=tag_config.get("foreground"))
            if tag_name.startswith("style_"):
                try:
                    num = int(tag_name.split("_")[1])
                    if num >= self.style_counter: self.style_counter = num + 1
                except (ValueError, IndexError): pass

    def _select_all(self):
        self.text_widget.tag_add(tk.SEL, "1.0", tk.END); self.text_widget.mark_set(tk.INSERT, "1.0"); self.text_widget.see(tk.INSERT); return "break"
    def _insert_datetime(self): self.text_widget.insert(tk.INSERT, datetime.now().strftime("%H:%M %d/%m/%Y"))
    def _toggle_word_wrap(self): self.text_widget.config(wrap=tk.WORD if self.wrap_var.get() else tk.NONE)

    def _change_selection_color(self):
        if self.text_widget.tag_ranges(tk.SEL):
            color = colorchooser.askcolor(title="Escolha a cor do texto")
            if color and color[1]:
                tag_name = f"style_{self.style_counter}"; self.style_counter += 1
                self.text_widget.tag_add(tag_name, "sel.first", "sel.last")
                self.text_widget.tag_config(tag_name, foreground=color[1])
                self._on_text_change(None)
        else: messagebox.showinfo("Nenhuma Seleção", "Selecione um trecho de texto para alterar a cor.")
    
    def _change_default_text_color(self):
        color = colorchooser.askcolor(title="Escolha a cor do texto padrão")
        if color and color[1]:
            self.text_widget.config(fg=color[1], insertbackground=color[1])
            self._on_text_change(None)

    def _change_bg_color(self):
        color = colorchooser.askcolor(title="Escolha a cor de fundo")
        if color and color[1]: self.text_widget.config(bg=color[1]); self._on_text_change(None)

    def _zoom(self, amount):
        if amount == 0: self.zoom_level = 100
        else:
            self.zoom_level += amount
            if self.zoom_level < 10: self.zoom_level = 10
        new_size = int(self.default_font_size * (self.zoom_level / 100))
        if new_size < 1: new_size = 1
        self.text_widget.config(font=(self.default_font_family, new_size))
        self.zoom_label.config(text=f"Zoom: {self.zoom_level}%")

    def _toggle_status_bar(self):
        if self.status_bar_var.get(): self.status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        else: self.status_bar_frame.pack_forget()

    def _update_status_bar(self, event=None):
        row, col = self.text_widget.index(tk.INSERT).split('.')
        char_count = len(self.text_widget.get("1.0", "end-1c"))
        self.line_col_label.config(text=f"Lin: {row}, Col: {int(col) + 1}")
        self.char_count_label.config(text=f"Caracteres: {char_count}")

    def _on_text_change(self, event=None):
        if self.text_widget.edit_modified():
            self.text_changed = True
            if not self.title().startswith("*"): self.title("*" + self.title())
        else:
            self.text_changed = False
            if self.title().startswith("*"): self.title(self.title()[1:])
        self._update_status_bar()

    def _check_unsaved_changes(self):
        if self.text_changed:
            response = messagebox.askyesnocancel("NotaPro", f"Deseja salvar as alterações em {self.title().strip('*')}?")
            if response is True: self._save_file(); return not self.text_changed
            elif response is False: return True
            else: return False
        return True

    def _exit_app(self):
        if self._check_unsaved_changes(): self.destroy()

if __name__ == "__main__":
    app = NotaPro()
    app.mainloop()