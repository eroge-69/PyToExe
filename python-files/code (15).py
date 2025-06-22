# notapro.py (versão com funcionalidade Localizar)
# Requer Python 3 com Tkinter

import tkinter as tk
from tkinter import filedialog, messagebox, colorchooser, simpledialog, font
import json
import os
import sys
import subprocess
from datetime import datetime

# --- NOVA CLASSE PARA A JANELA DE BUSCA ---
class FindDialog(tk.Toplevel):
    def __init__(self, master):
        super().__init__(master)
        self.master = master
        self.transient(master)
        self.title("Localizar")
        self.geometry("380x130")
        self.resizable(False, False)

        # Variáveis de controle da UI
        self.find_what = tk.StringVar(value=master.last_search["term"])
        self.match_case = tk.BooleanVar(value=master.last_search["case"])
        self.direction = tk.StringVar(value=master.last_search["direction"])

        # Widgets
        tk.Label(self, text="Localizar:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.find_entry = tk.Entry(self, textvariable=self.find_what, width=30)
        self.find_entry.grid(row=0, column=1, padx=5, pady=5, sticky="w")
        self.find_entry.focus_set()
        self.find_entry.select_range(0, tk.END)

        # Botões
        self.find_button = tk.Button(self, text="Localizar próxima", width=15, command=self._on_find_next)
        self.find_button.grid(row=0, column=2, padx=5, pady=5)
        self.cancel_button = tk.Button(self, text="Cancelar", width=15, command=self.withdraw)
        self.cancel_button.grid(row=1, column=2, padx=5, pady=5)

        # Checkbox e Radio buttons
        tk.Checkbutton(self, text="Diferenciar maiúsculas de minúsculas", variable=self.match_case).grid(row=2, column=0, columnspan=2, padx=5, sticky="w")
        
        direction_frame = tk.LabelFrame(self, text="Direção")
        direction_frame.grid(row=2, column=1, columnspan=2, sticky="e", padx=5)
        tk.Radiobutton(direction_frame, text="Para cima", variable=self.direction, value="up").pack(side=tk.LEFT)
        tk.Radiobutton(direction_frame, text="Para baixo", variable=self.direction, value="down").pack(side=tk.LEFT)
        
        # Esconder a janela em vez de destruí-la ao clicar no 'X'
        self.protocol("WM_DELETE_WINDOW", self.withdraw)

    def _on_find_next(self):
        # Atualiza o estado da busca na janela principal
        self.master.last_search["term"] = self.find_what.get()
        self.master.last_search["case"] = self.match_case.get()
        self.master.last_search["direction"] = self.direction.get()
        
        # Chama a função de busca da janela principal
        self.master._find_next()

class FontDialog(tk.Toplevel):
    # ... (O código da FontDialog permanece inalterado) ...
    def __init__(self, parent):
        super().__init__(parent)
        self.transient(parent); self.title("Escolher Fonte"); self.geometry("400x400"); self.result = None
        self.fonts = sorted(["Arial", "Calibri", "Courier New", "Georgia", "Helvetica", "Impact", "Times New Roman", "Verdana"])
        self.font_family = tk.StringVar(value="Arial"); self.font_size = tk.IntVar(value=12); self.is_bold = tk.BooleanVar(value=False); self.is_italic = tk.BooleanVar(value=False)
        font_frame = tk.Frame(self); font_frame.pack(pady=10, padx=10, fill=tk.X)
        tk.Label(font_frame, text="Fonte:").pack(side=tk.LEFT)
        self.font_listbox = tk.Listbox(font_frame, listvariable=tk.StringVar(value=self.fonts), height=6, exportselection=False)
        self.font_listbox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        font_scrollbar = tk.Scrollbar(font_frame, orient=tk.VERTICAL, command=self.font_listbox.yview)
        self.font_listbox.config(yscrollcommand=font_scrollbar.set); font_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.font_listbox.bind("<<ListboxSelect>>", self._update_preview)
        style_frame = tk.Frame(self); style_frame.pack(pady=5, padx=10, fill=tk.X)
        tk.Checkbutton(style_frame, text="Negrito", variable=self.is_bold, command=self._update_preview).pack(side=tk.LEFT, padx=5)
        tk.Checkbutton(style_frame, text="Itálico", variable=self.is_italic, command=self._update_preview).pack(side=tk.LEFT, padx=5)
        tk.Label(style_frame, text="Tamanho:").pack(side=tk.LEFT, padx=(20, 5))
        self.size_spinbox = tk.Spinbox(style_frame, from_=8, to=72, width=5, textvariable=self.font_size, command=self._update_preview)
        self.size_spinbox.pack(side=tk.LEFT)
        preview_frame = tk.LabelFrame(self, text="Amostra", padx=10, pady=10); preview_frame.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)
        self.preview_label = tk.Label(preview_frame, text="AaBbYyZz", font=("Arial", 12)); self.preview_label.pack()
        button_frame = tk.Frame(self); button_frame.pack(pady=10)
        tk.Button(button_frame, text="OK", width=10, command=self._on_ok).pack(side=tk.LEFT, padx=10)
        tk.Button(button_frame, text="Cancelar", width=10, command=self.destroy).pack(side=tk.LEFT, padx=10)
        self.grab_set(); self._update_preview()
    def _update_preview(self, event=None):
        family = self.fonts[self.font_listbox.curselection()[0]] if self.font_listbox.curselection() else "Arial"
        size = self.font_size.get(); weight = "bold" if self.is_bold.get() else "normal"; slant = "italic" if self.is_italic.get() else "roman"
        preview_font = font.Font(family=family, size=size, weight=weight, slant=slant); self.preview_label.config(font=preview_font)
    def _on_ok(self):
        family = self.fonts[self.font_listbox.curselection()[0]] if self.font_listbox.curselection() else "Arial"
        size = self.font_size.get(); weight = "bold" if self.is_bold.get() else "normal"; slant = "italic" if self.is_italic.get() else "roman"
        self.result = (family, size, weight, slant); self.destroy()

class NotaPro(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Sem Título - NotaPro"); self.geometry("800x600")
        self.current_file_path = None; self.text_changed = False; self.style_counter = 0
        self.default_font_family = "Consolas"; self.default_font_size = 12; self.zoom_level = 100
        
        # --- NOVO: Variáveis para estado da busca ---
        self.last_search = {"term": "", "case": False, "direction": "down"}
        self.find_dialog_instance = None
        
        self._create_widgets(); self._create_menu(); self._create_context_menu(); self._bind_shortcuts()
        self.protocol("WM_DELETE_WINDOW", self._exit_app)
        self.text_widget.bind("<<Modified>>", self._on_text_change)
        if len(sys.argv) > 1:
            initial_filepath = sys.argv[1]
            if os.path.exists(initial_filepath): self._load_file_from_path(initial_filepath)
            else: messagebox.showwarning("Arquivo não encontrado", f"O arquivo '{initial_filepath}' não foi encontrado.")

    def _create_widgets(self):
        self.text_widget = tk.Text(self, undo=True, wrap=tk.WORD, font=(self.default_font_family, self.default_font_size), insertbackground="black")
        self.text_widget.pack(expand=True, fill='both')
        self.status_bar_frame = tk.Frame(self, bd=1, relief=tk.SUNKEN); self.status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        self.line_col_label = tk.Label(self.status_bar_frame, text="Lin: 1, Col: 1", width=20, anchor='w'); self.line_col_label.pack(side=tk.LEFT, padx=5)
        self.char_count_label = tk.Label(self.status_bar_frame, text="Caracteres: 0", width=20, anchor='w'); self.char_count_label.pack(side=tk.LEFT, padx=5)
        self.zoom_label = tk.Label(self.status_bar_frame, text=f"Zoom: {self.zoom_level}%", width=15, anchor='e'); self.zoom_label.pack(side=tk.RIGHT, padx=5)
        self.encoding_label = tk.Label(self.status_bar_frame, text="UTF-8", width=10, anchor='e'); self.encoding_label.pack(side=tk.RIGHT, padx=5)
        self.text_widget.bind("<KeyRelease>", self._update_status_bar); self.text_widget.bind("<ButtonRelease-1>", self._update_status_bar)
        self.text_widget.bind("<Button-3>", self._show_context_menu); self._update_status_bar()

    def _create_context_menu(self):
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Recortar", command=lambda: self.text_widget.event_generate("<<Cut>>"))
        self.context_menu.add_command(label="Copiar", command=lambda: self.text_widget.event_generate("<<Copy>>"))
        self.context_menu.add_command(label="Colar", command=lambda: self.text_widget.event_generate("<<Paste>>"))
        self.context_menu.add_separator(); self.context_menu.add_command(label="Selecionar tudo", command=self._select_all)

    def _show_context_menu(self, event):
        selection = self.text_widget.tag_ranges(tk.SEL)
        self.context_menu.entryconfig("Recortar", state=tk.NORMAL if selection else tk.DISABLED)
        self.context_menu.entryconfig("Copiar", state=tk.NORMAL if selection else tk.DISABLED)
        try: self.clipboard_get(); self.context_menu.entryconfig("Colar", state=tk.NORMAL)
        except tk.TclError: self.context_menu.entryconfig("Colar", state=tk.DISABLED)
        content = self.text_widget.get("1.0", "end-1c")
        self.context_menu.entryconfig("Selecionar tudo", state=tk.NORMAL if content else tk.DISABLED)
        self.context_menu.tk_popup(event.x_root, event.y_root)

    def _create_menu(self):
        self.menu_bar = tk.Menu(self); self.config(menu=self.menu_bar)
        file_menu = tk.Menu(self.menu_bar, tearoff=0); self.menu_bar.add_cascade(label="Arquivo", menu=file_menu)
        file_menu.add_command(label="Novo", accelerator="Ctrl+N", command=self._new_file)
        file_menu.add_command(label="Nova Janela", accelerator="Ctrl+Shift+N", command=self._new_window)
        file_menu.add_command(label="Abrir...", accelerator="Ctrl+O", command=self._open_file)
        file_menu.add_command(label="Salvar", accelerator="Ctrl+S", command=self._save_file)
        file_menu.add_command(label="Salvar Como...", command=self._save_as_file)
        file_menu.add_separator(); file_menu.add_command(label="Sair", command=self._exit_app)
        
        edit_menu = tk.Menu(self.menu_bar, tearoff=0); self.menu_bar.add_cascade(label="Editar", menu=edit_menu)
        edit_menu.add_command(label="Desfazer", accelerator="Ctrl+Z", command=self.text_widget.edit_undo); edit_menu.add_command(label="Refazer", accelerator="Ctrl+Y", command=self.text_widget.edit_redo)
        edit_menu.add_separator(); edit_menu.add_command(label="Recortar", accelerator="Ctrl+X", command=lambda: self.text_widget.event_generate("<<Cut>>"))
        edit_menu.add_command(label="Copiar", accelerator="Ctrl+C", command=lambda: self.text_widget.event_generate("<<Copy>>")); edit_menu.add_command(label="Colar", accelerator="Ctrl+V", command=lambda: self.text_widget.event_generate("<<Paste>>"))
        edit_menu.add_separator()
        # --- NOVO ITEM DE MENU ---
        edit_menu.add_command(label="Localizar...", accelerator="Ctrl+F", command=self._open_find_dialog)
        edit_menu.add_command(label="Localizar próxima", accelerator="F3", command=self._find_next)
        edit_menu.add_separator()
        edit_menu.add_command(label="Selecionar Tudo", accelerator="Ctrl+A", command=self._select_all); edit_menu.add_command(label="Data/Hora", accelerator="F5", command=self._insert_datetime)
        
        format_menu = tk.Menu(self.menu_bar, tearoff=0); self.menu_bar.add_cascade(label="Formatar", menu=format_menu)
        self.wrap_var = tk.BooleanVar(value=True); format_menu.add_checkbutton(label="Quebra Automática de Linha", onvalue=True, offvalue=False, variable=self.wrap_var, command=self._toggle_word_wrap)
        format_menu.add_separator(); format_menu.add_command(label="Alterar fonte do trecho...", command=self._change_selection_font)
        format_menu.add_command(label="Alterar cor do trecho...", command=self._change_selection_color); format_menu.add_command(label="Grifar trecho...", command=self._highlight_selection)
        format_menu.add_command(label="Sublinhar trecho...", accelerator="Ctrl+U", command=self._apply_colored_underline); format_menu.add_separator()
        format_menu.add_command(label="Cor do Texto Padrão...", command=self._change_default_text_color); format_menu.add_command(label="Cor de Fundo...", command=self._change_bg_color)
        
        view_menu = tk.Menu(self.menu_bar, tearoff=0); self.menu_bar.add_cascade(label="Exibir", menu=view_menu)
        zoom_menu = tk.Menu(view_menu, tearoff=0); view_menu.add_cascade(label="Zoom", menu=zoom_menu)
        zoom_menu.add_command(label="Aumentar", accelerator="Ctrl++", command=lambda: self._zoom(10)); zoom_menu.add_command(label="Diminuir", accelerator="Ctrl+-", command=lambda: self._zoom(-10))
        zoom_menu.add_command(label="Restaurar Zoom Padrão", accelerator="Ctrl+0", command=lambda: self._zoom(0)); view_menu.add_separator()
        self.status_bar_var = tk.BooleanVar(value=True); view_menu.add_checkbutton(label="Barra de Status", onvalue=True, offvalue=False, variable=self.status_bar_var, command=self._toggle_status_bar)

    def _bind_shortcuts(self):
        self.bind("<Control-n>", lambda e: self._new_file()); self.bind("<Control-o>", lambda e: self._open_file()); self.bind("<Control-s>", lambda e: self._save_file())
        self.bind("<Control-a>", lambda e: self._select_all()); self.bind("<F5>", lambda e: self._insert_datetime()); self.bind("<Control-plus>", lambda e: self._zoom(10))
        self.bind("<Control-minus>", lambda e: self._zoom(-10)); self.bind("<Control-0>", lambda e: self._zoom(0)); self.bind("<Control-y>", lambda e: self.text_widget.edit_redo())
        self.bind("<Control-u>", lambda e: self._apply_colored_underline()); self.bind("<Control-Shift-n>", lambda e: self._new_window())
        self.text_widget.bind("<MouseWheel>", self._zoom_on_scroll)
        # --- NOVOS ATALHOS ---
        self.bind("<Control-f>", lambda e: self._open_find_dialog())
        self.bind("<F3>", lambda e: self._find_next())

    # --- NOVOS MÉTODOS PARA A BUSCA ---
    def _open_find_dialog(self):
        if self.find_dialog_instance is None or not self.find_dialog_instance.winfo_exists():
            self.find_dialog_instance = FindDialog(self)
        else:
            self.find_dialog_instance.deiconify() # Traz para a frente se estiver minimizada
        self.find_dialog_instance.lift() # Traz para a frente de outras janelas

    def _find_next(self, event=None):
        term = self.last_search["term"]
        if not term:
            self._open_find_dialog()
            return
        
        # Remove a seleção anterior
        self.text_widget.tag_remove('found', '1.0', tk.END)

        direction = self.last_search["direction"]
        is_case_sensitive = self.last_search["case"]

        if direction == 'down':
            start_pos = self.text_widget.index(tk.INSERT)
            stop_pos = tk.END
            backwards = False
        else: # up
            start_pos = self.text_widget.index(tk.INSERT)
            stop_pos = '1.0'
            backwards = True

        pos = self.text_widget.search(term, start_pos, stopindex=stop_pos, nocase=not is_case_sensitive, backwards=backwards)

        if pos:
            end_pos = f"{pos}+{len(term)}c"
            self.text_widget.tag_add('found', pos, end_pos)
            self.text_widget.tag_config('found', background='yellow', foreground='black')
            self.text_widget.mark_set(tk.INSERT, end_pos if direction == 'down' else pos)
            self.text_widget.see(pos)
            self.text_widget.focus_set()
        else:
            messagebox.showinfo("Fim da Busca", f"Não foi possível encontrar '{term}'", parent=self)

    # O restante do código (funções de salvamento, formatação, etc.) permanece o mesmo.
    # ... (código anterior omitido por brevidade, mas deve ser mantido) ...
    def _new_window(self):
        try:
            command = []
            if getattr(sys, 'frozen', False): command = [sys.executable]
            else:
                script_path = os.path.abspath(__file__); python_executable = sys.executable
                pythonw_path = os.path.join(os.path.dirname(python_executable), 'pythonw.exe')
                interpreter = pythonw_path if os.path.exists(pythonw_path) else python_executable
                command = [interpreter, script_path]
            subprocess.Popen(command)
        except Exception as e: messagebox.showerror("Erro ao Abrir Nova Janela", f"Não foi possível iniciar uma nova instância:\n{e}")
    def _blend_colors(self, fg_hex, bg_hex, alpha):
        fg_rgb = self.winfo_rgb(fg_hex); bg_rgb = self.winfo_rgb(bg_hex)
        fg_r, fg_g, fg_b = [x / 256 for x in fg_rgb]; bg_r, bg_g, bg_b = [x / 256 for x in bg_rgb]
        res_r = int(fg_r * alpha + bg_r * (1 - alpha)); res_g = int(fg_g * alpha + bg_g * (1 - alpha)); res_b = int(fg_b * alpha + bg_b * (1 - alpha))
        return f'#{res_r:02x}{res_g:02x}{res_b:02x}'
    def _zoom_on_scroll(self, event):
        if (event.state & 0x0004) != 0:
            if event.delta > 0: self._zoom(10)
            else: self._zoom(-10)
            return "break"
    def _new_file(self):
        if self._check_unsaved_changes():
            self.text_widget.delete("1.0", tk.END); self.text_widget.edit_reset()
            self.current_file_path = None; self.title("Sem Título - NotaPro"); self.text_changed = False
            for tag in self.text_widget.tag_names():
                if tag.startswith("style_") or tag == 'found': self.text_widget.tag_delete(tag)
    def _load_file_from_path(self, filepath):
        try:
            self._new_file()
            if filepath.endswith('.npro'): self._load_npro_file(filepath)
            else:
                with open(filepath, "r", encoding='utf-8') as f: self.text_widget.insert("1.0", f.read())
            self.current_file_path = filepath; self.title(f"{os.path.basename(filepath)} - NotaPro")
            self.text_widget.edit_modified(False); self.text_changed = False; self._update_status_bar()
        except Exception as e: messagebox.showerror("Erro ao Abrir", f"Não foi possível abrir o arquivo:\n{e}"); self._new_file()
    def _open_file(self):
        if not self._check_unsaved_changes(): return
        filepath = filedialog.askopenfilename(filetypes=[("Arquivos NotaPro", "*.npro"), ("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")])
        if filepath: self._load_file_from_path(filepath)
    def _save_file(self):
        if self.current_file_path: self._save_to_path(self.current_file_path)
        else: self._save_as_file()
    def _save_as_file(self):
        filepath = filedialog.asksaveasfilename(defaultextension=".npro", filetypes=[("Arquivos NotaPro", "*.npro"), ("Arquivos de Texto", "*.txt"), ("Todos os Arquivos", "*.*")])
        if filepath: self._save_to_path(filepath)
    def _save_to_path(self, filepath):
        try:
            if filepath.endswith('.npro'): self._save_npro_file(filepath)
            else:
                with open(filepath, "w", encoding='utf-8') as f: f.write(self.text_widget.get("1.0", tk.END))
            self.current_file_path = filepath; self.title(f"{os.path.basename(filepath)} - NotaPro")
            self.text_widget.edit_modified(False); self.text_changed = False
        except Exception as e: messagebox.showerror("Erro ao Salvar", f"Não foi possível salvar o arquivo:\n{e}")
    def _save_npro_file(self, filepath):
        data = {"global_config": {"background": self.text_widget.cget("bg"), "foreground": self.text_widget.cget("fg")}, "content": self.text_widget.get("1.0", tk.END), "tags": []}
        for tag_name in self.text_widget.tag_names():
            if tag_name.startswith("style_"):
                config = {}
                font_config = self.text_widget.tag_cget(tag_name, "font"); fg = self.text_widget.tag_cget(tag_name, "foreground"); bg = self.text_widget.tag_cget(tag_name, "background"); ul = self.text_widget.tag_cget(tag_name, "underline")
                if font_config: f = font.Font(font=font_config); config["font"] = [f.actual("family"), f.actual("size"), f.actual("weight"), f.actual("slant")]
                if fg: config["foreground"] = fg
                if bg: config["background"] = bg
                if ul: config["underline"] = bool(ul)
                if config:
                    ranges = self.text_widget.tag_ranges(tag_name)
                    for i in range(0, len(ranges), 2): data["tags"].append({"name": tag_name, "start": str(ranges[i]), "end": str(ranges[i+1]), "config": config})
        with open(filepath, 'w', encoding='utf-8') as f: json.dump(data, f, indent=2)
    def _load_npro_file(self, filepath):
        with open(filepath, 'r', encoding='utf-8') as f: data = json.load(f)
        config = data.get("global_config", {}); fg_color = config.get("foreground", "black")
        self.text_widget.config(bg=config.get("background", "white"), fg=fg_color, insertbackground=fg_color); self.text_widget.insert("1.0", data.get("content", ""))
        for tag_info in data.get("tags", []):
            tag_name, start, end = tag_info["name"], tag_info["start"], tag_info["end"]; config_to_apply = {}
            if "font" in tag_info["config"]: config_to_apply["font"] = tuple(tag_info["config"]["font"])
            if "foreground" in tag_info["config"]: config_to_apply["foreground"] = tag_info["config"]["foreground"]
            if "background" in tag_info["config"]: config_to_apply["background"] = tag_info["config"]["background"]
            if "underline" in tag_info["config"]: config_to_apply["underline"] = tag_info["config"]["underline"]
            self.text_widget.tag_add(tag_name, start, end)
            if config_to_apply: self.text_widget.tag_config(tag_name, **config_to_apply)
            if tag_name.startswith("style_"):
                try:
                    num = int(tag_name.split("_")[1])
                    if num >= self.style_counter: self.style_counter = num + 1
                except (ValueError, IndexError): pass
    def _select_all(self): self.text_widget.tag_add(tk.SEL, "1.0", tk.END); self.text_widget.mark_set(tk.INSERT, "1.0"); self.text_widget.see(tk.INSERT); return "break"
    def _insert_datetime(self): self.text_widget.insert(tk.INSERT, datetime.now().strftime("%H:%M %d/%m/%Y"))
    def _toggle_word_wrap(self): self.text_widget.config(wrap=tk.WORD if self.wrap_var.get() else tk.NONE)
    def _change_selection_font(self):
        if not self.text_widget.tag_ranges(tk.SEL): messagebox.showinfo("Nenhuma Seleção", "Selecione um trecho de texto para formatar a fonte."); return
        dialog = FontDialog(self); self.wait_window(dialog)
        if dialog.result:
            new_font = dialog.result; tag_name = f"style_{self.style_counter}"; self.style_counter += 1
            self.text_widget.tag_add(tag_name, "sel.first", "sel.last"); self.text_widget.tag_config(tag_name, font=new_font); self._on_text_change(None)
    def _change_selection_color(self):
        if self.text_widget.tag_ranges(tk.SEL):
            color = colorchooser.askcolor(title="Escolha a cor do texto")
            if color and color[1]:
                tag_name = f"style_{self.style_counter}"; self.style_counter += 1
                self.text_widget.tag_add(tag_name, "sel.first", "sel.last"); self.text_widget.tag_config(tag_name, foreground=color[1]); self._on_text_change(None)
        else: messagebox.showinfo("Nenhuma Seleção", "Selecione um trecho de texto para formatar.")
    def _highlight_selection(self):
        if not self.text_widget.tag_ranges(tk.SEL): messagebox.showinfo("Nenhuma Seleção", "Selecione um trecho de texto para grifar."); return
        chosen_color = colorchooser.askcolor(title="Escolha a cor do grifo")
        if not (chosen_color and chosen_color[1]): return
        opacity = simpledialog.askinteger("Opacidade", "Digite a opacidade do grifo (1-100%):", parent=self, minvalue=1, maxvalue=100)
        if opacity is None: return
        main_bg_color = self.text_widget.cget("bg"); alpha_value = opacity / 100.0; blended_color = self._blend_colors(chosen_color[1], main_bg_color, alpha_value)
        tag_name = f"style_{self.style_counter}"; self.style_counter += 1
        self.text_widget.tag_add(tag_name, "sel.first", "sel.last"); self.text_widget.tag_config(tag_name, background=blended_color); self._on_text_change(None)
    def _apply_colored_underline(self):
        if not self.text_widget.tag_ranges(tk.SEL): messagebox.showinfo("Nenhuma Seleção", "Selecione um trecho de texto para sublinhar."); return
        chosen_color = colorchooser.askcolor(title="Escolha a cor do sublinhado")
        if not (chosen_color and chosen_color[1]): return
        tag_name = f"style_{self.style_counter}"; self.style_counter += 1
        self.text_widget.tag_add(tag_name, "sel.first", "sel.last"); self.text_widget.tag_config(tag_name, foreground=chosen_color[1], underline=True); self._on_text_change(None)
    def _change_default_text_color(self):
        color = colorchooser.askcolor(title="Escolha a cor do texto padrão")
        if color and color[1]: self.text_widget.config(fg=color[1], insertbackground=color[1]); self._on_text_change(None)
    def _change_bg_color(self):
        color = colorchooser.askcolor(title="Escolha a cor de fundo")
        if color and color[1]: self.text_widget.config(bg=color[1]); self._on_text_change(None)
    def _zoom(self, amount):
        if amount == 0: self.zoom_level = 100
        else: self.zoom_level += amount; self.zoom_level = max(10, self.zoom_level)
        new_size = max(1, int(self.default_font_size * (self.zoom_level / 100)))
        self.text_widget.config(font=(self.default_font_family, new_size)); self.zoom_label.config(text=f"Zoom: {self.zoom_level}%")
    def _toggle_status_bar(self):
        if self.status_bar_var.get(): self.status_bar_frame.pack(side=tk.BOTTOM, fill=tk.X)
        else: self.status_bar_frame.pack_forget()
    def _update_status_bar(self, event=None):
        row, col = self.text_widget.index(tk.INSERT).split('.'); char_count = len(self.text_widget.get("1.0", "end-1c"))
        self.line_col_label.config(text=f"Lin: {row}, Col: {int(col) + 1}"); self.char_count_label.config(text=f"Caracteres: {char_count}")
    def _on_text_change(self, event=None):
        if self.text_widget.edit_modified():
            self.text_changed = True
            if not self.title().startswith("*"): self.title("*" + self.title())
        else: self.text_changed = False; self.title(self.title().lstrip("*"))
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