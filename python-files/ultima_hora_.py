import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import json

class MKVSubtitleEditor:
    def __init__(self, root):
        self.root = root
        self.root.title("Editor de Legendas MKV")
        
        # Initialize variables
        self.current_file = None
        self.current_subtitles = []
        self.selected_subtitle_id = None
        self.progress_value = tk.DoubleVar()
        self.progress_text = tk.StringVar(value="Pronto para começar")
        self.alert_window = None
        self.selected_id = tk.StringVar()
        self.title_var = tk.StringVar()
        self.apply_to_all = tk.BooleanVar(value=True)
        self.blink_state = False  # Para controlar o estado do piscar
        
        # Check for required tools
        self.mkvmerge = self.find_tool("mkvmerge.exe")
        self.mkvpropedit = self.find_tool("mkvpropedit.exe")
        
        if not self.mkvmerge or not self.mkvpropedit:
            messagebox.showerror("Erro", "Instale o MKVToolNix primeiro!")
            self.root.after(100, self.root.destroy)
            return
        
        # Create UI
        self.create_widgets()
        self.root.state('zoomed')
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def on_close(self):
        """Handle window close properly"""
        self.root.destroy()

    def find_tool(self, tool_name):
        """Find MKVToolNix utilities"""
        paths = [
            os.path.join(os.environ.get("ProgramFiles", ""), "MKVToolNix", tool_name),
            os.path.join(os.environ.get("LocalAppData", ""), "Programs", "MKVToolNix", tool_name),
            tool_name
        ]
        for path in paths:
            if os.path.exists(path):
                return path
        return None

    def update_progress(self, value, text=None):
        """Update progress bar and status text"""
        self.progress_value.set(value)
        if text:
            self.progress_text.set(text)
        self.root.update_idletasks()

    def create_widgets(self):
        """Create all UI elements"""
        main_frame = tk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 1. File selection section
        file_frame = tk.LabelFrame(main_frame, text="1. Selecione arquivos MKV")
        file_frame.pack(fill=tk.X, pady=5)
        
        button_frame = tk.Frame(file_frame)
        button_frame.pack(fill=tk.X)
        
        tk.Button(button_frame, text="Abrir Arquivos", command=self.add_files, 
                bg='#0078D7', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Abrir Pasta", command=self.add_folder, 
                bg='#FFD700', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Selecionar Todos", command=self.select_all_files, 
                bg='#0078D7', fg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)
        tk.Button(button_frame, text="Limpar", command=self.clear_files, 
                bg='white', font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=2)
        
        list_container = tk.Frame(file_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        scrollbar = tk.Scrollbar(list_container)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(
            list_container, 
            height=8, 
            selectmode=tk.EXTENDED,
            yscrollcommand=scrollbar.set
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)
        
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)

        # 2. Subtitles section
        sub_frame = tk.LabelFrame(main_frame, text="2. Legendas disponíveis")
        sub_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        self.tree = ttk.Treeview(sub_frame, columns=('ID', 'Língua', 'Nome', 'Padrão'), show='headings')
        for col, text in zip(['ID', 'Língua', 'Nome', 'Padrão'], ['ID', 'Língua', 'Nome', 'Padrão']):
            self.tree.heading(col, text=text)
            self.tree.column(col, width=50 if col == 'ID' else 100 if col == 'Língua' else 60 if col == 'Padrão' else 300)
        
        yscroll = ttk.Scrollbar(sub_frame, orient='vertical', command=self.tree.yview)
        xscroll = ttk.Scrollbar(sub_frame, orient='horizontal', command=self.tree.xview)
        self.tree.configure(yscroll=yscroll.set, xscroll=xscroll.set)
        
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        yscroll.pack(side=tk.RIGHT, fill=tk.Y)
        xscroll.pack(side=tk.BOTTOM, fill=tk.X)
        
        self.tree.bind('<ButtonRelease-1>', self.on_subtitle_select)

        # 3. Title editing section
        title_frame = tk.LabelFrame(main_frame, text="3. Editar Título do Arquivo")
        title_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(title_frame, text="Novo título (deixe em branco para remover):").pack(anchor=tk.W)
        self.title_entry = tk.Entry(title_frame, textvariable=self.title_var, width=50)
        self.title_entry.pack(fill=tk.X, pady=3)
        
        title_button_frame = tk.Frame(title_frame)
        title_button_frame.pack(fill=tk.X, pady=3)
        
        center_frame = tk.Frame(title_button_frame)
        center_frame.pack(expand=True)
        
        tk.Button(center_frame, text="Aplicar Título", command=self.apply_title, 
                 bg='#4CAF50', fg='white', width=15, font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=20)
        tk.Button(center_frame, text="Remover Título", command=self.remove_title, 
                 bg='#F44336', fg='white', width=15, font=('Arial', 10, 'bold')).pack(side=tk.LEFT, padx=20)

        # 4. Action section
        action_frame = tk.Frame(main_frame)
        action_frame.pack(fill=tk.X, pady=10)
        
        tk.Checkbutton(
            action_frame, 
            text="Aplicar a TODOS os arquivos selecionados",
            variable=self.apply_to_all
        ).pack(anchor=tk.W)
        
        process_frame = tk.Frame(action_frame)
        process_frame.pack(fill=tk.X, pady=5)
        
        self.btn_process = tk.Button(
            process_frame, 
            text="DEFINIR LEGENDA SEGUINTE COMO PADRÃO", 
            command=self.process_subtitles,
            bg='green', fg='white',
            font=('Arial', 10, 'bold'),
            state=tk.DISABLED
        )
        self.btn_process.pack(side=tk.LEFT, expand=True, fill=tk.X)
        
        tk.Button(
            process_frame,
            text="SAIR",
            command=self.root.destroy,
            bg='red',
            fg='white',
            font=('Arial', 10, 'bold')
        ).pack(side=tk.LEFT, padx=10)
        
        tk.Label(action_frame, text="ID Selecionado:").pack(side=tk.LEFT)
        tk.Entry(action_frame, textvariable=self.selected_id, width=8, state='readonly').pack(side=tk.LEFT, padx=5)

        # 5. Progress bar
        progress_frame = tk.LabelFrame(main_frame, text="Progresso")
        progress_frame.pack(fill=tk.X, pady=5)
        
        self.progress_bar = ttk.Progressbar(
            progress_frame,
            variable=self.progress_value,
            maximum=100,
            mode='determinate'
        )
        self.progress_bar.pack(fill=tk.X, padx=5, pady=5)
        
        self.progress_label = tk.Label(
            progress_frame,
            textvariable=self.progress_text,
            font=('Arial', 9)
        )
        self.progress_label.pack()

    def add_files(self):
        """Add individual files to list"""
        filetypes = [("Arquivos MKV", "*.mkv"), ("Todos os arquivos", "*.*")]
        files = filedialog.askopenfilenames(title="Selecione arquivos MKV", filetypes=filetypes)
        if files:
            for file in files:
                if file not in self.file_listbox.get(0, tk.END):
                    self.file_listbox.insert(tk.END, file)
            self.update_process_button_text()

    def add_folder(self):
        """Add all MKV files from folder"""
        folder = filedialog.askdirectory(title="Selecione uma pasta com arquivos MKV")
        if folder:
            self.update_progress(0, "A procurar arquivos MKV...")
            mkv_files = [f for f in os.listdir(folder) if f.lower().endswith('.mkv')]
            total = len(mkv_files)
            
            for i, file in enumerate(mkv_files, 1):
                full_path = os.path.join(folder, file)
                if full_path not in self.file_listbox.get(0, tk.END):
                    self.file_listbox.insert(tk.END, full_path)
                self.update_progress(i/total*100, f"Processando {i} de {total} arquivos")
            
            self.update_progress(100, "Pronto!")
            self.update_process_button_text()

    def select_all_files(self):
        """Select all files in list"""
        self.file_listbox.selection_set(0, tk.END)
        self.on_file_select(None)
        self.update_process_button_text()

    def clear_files(self):
        """Clear file list"""
        self.file_listbox.delete(0, tk.END)
        self.clear_subtitle_list()
        self.btn_process.config(state=tk.DISABLED)
        self.selected_id.set("")
        self.current_file = None
        self.current_subtitles = []
        self.selected_subtitle_id = None
        self.title_var.set("")
        self.update_process_button_text()
        self.update_progress(0, "Pronto para começar")

    def clear_subtitle_list(self):
        """Clear subtitle treeview"""
        for item in self.tree.get_children():
            self.tree.delete(item)

    def on_file_select(self, event):
        """Handle file selection"""
        sel = self.file_listbox.curselection()
        if not sel:
            self.btn_process.config(state=tk.DISABLED)
            return
            
        self.current_file = self.file_listbox.get(sel[0])
        self.load_subtitles()
        self.update_process_button_text()

    def _blink_no_subtitles_message(self):
        """Make the 'no subtitles' message blink between black and red"""
        if hasattr(self, 'blinking_message_active') and self.blinking_message_active:
            current_color = self.progress_label.cget("foreground")
            new_color = "red" if current_color == "black" else "black"
            self.progress_label.config(foreground=new_color)
            self.root.after(500, self._blink_no_subtitles_message)

    def load_subtitles(self):
        """Load subtitles from selected file"""
        if not self.current_file:
            return
            
        try:
            self.update_progress(0, "A carregar legendas...")
            result = subprocess.run(
                [self.mkvmerge, '-i', '--identification-format', 'json', self.current_file],
                capture_output=True,
                text=True,
                check=True
            )
            
            data = json.loads(result.stdout)
            self.current_subtitles = [t for t in data.get('tracks', []) if t.get('type') == 'subtitles']
            
            if not self.current_subtitles:
                # Stop any previous blinking
                if hasattr(self, 'blinking_message_active'):
                    self.blinking_message_active = False
                
                # Set initial state
                self.progress_label.config(foreground="red")
                self.update_progress(100, "Nenhuma legenda encontrada no arquivo!")
                
                # Start blinking
                self.blinking_message_active = True
                self._blink_no_subtitles_message()
                
                self.clear_subtitle_list()
                return
                
            # Stop blinking if active
            if hasattr(self, 'blinking_message_active'):
                self.blinking_message_active = False
                self.progress_label.config(foreground="black")
                
            self.display_subtitles()
            
            if not self.check_pt_subtitles():
                self.show_alert(
                    "AVISO: Não foram encontradas legendas em Português neste ficheiro!\n\n"
                    "Variantes reconhecidas:\n"
                    "- Português (pt/pt-pt/por)\n"
                    "- Português Brasileiro (pt-br)"
                )
            
            self.update_progress(100, "Legendas carregadas!")
            
        except Exception as e:
            messagebox.showerror("Erro", f"Falha ao ler legendas:\n{str(e)}")
            self.clear_subtitle_list()
            self.update_progress(0, "Erro ao carregar legendas")

    def check_pt_subtitles(self):
        """Check for Portuguese subtitles"""
        if not self.current_subtitles:
            return False
            
        pt_variants = ['pt', 'por', 'pt-pt', 'pt-br']
        
        for track in self.current_subtitles:
            props = track.get('properties', {})
            lang = props.get('language', 'und').lower()
            track_name = props.get('track_name', '').lower()
            
            if (lang in pt_variants or 
                any(variant in track_name for variant in pt_variants)):
                return True
        return False

    def detect_pt_variant(self, track):
        """Detect Portuguese variant"""
        props = track.get('properties', {})
        lang = props.get('language', 'und').lower()
        track_name = props.get('track_name', '').lower()
        
        br_keywords = ['brazil', 'brasil', 'pt-br']
        pt_keywords = ['portugal', 'european', 'pt-pt']
        
        if any(kw in track_name for kw in br_keywords) or lang == 'pt-br':
            return 'pt-br'
        elif any(kw in track_name for kw in pt_keywords) or lang == 'pt-pt':
            return 'pt-pt'
        elif lang in ['pt', 'por']:
            return 'pt'
        return lang

    def display_subtitles(self):
        """Display subtitles in treeview"""
        self.clear_subtitle_list()
        
        if not self.current_subtitles:
            return
            
        for track in self.current_subtitles:
            props = track.get('properties', {})
            lang = props.get('language', 'und')
            
            if lang.lower() in ['pt', 'por', 'pt-pt', 'pt-br']:
                lang = self.detect_pt_variant(track)
            
            self.tree.insert('', 'end', values=(
                track.get('id'),
                lang,
                props.get('track_name', ''),
                'Sim' if props.get('default_track', False) else 'Não'
            ))

    def update_process_button_text(self):
        """Update process button text based on selection"""
        selected_count = len(self.file_listbox.curselection())
        if selected_count == 1:
            self.btn_process.config(text="PROCESSAR FICHEIRO")
        elif selected_count > 1:
            self.btn_process.config(text="PROCESSAR FICHEIROS")
        else:
            self.btn_process.config(text="DEFINIR LEGENDA SEGUINTE COMO PADRÃO")

    def show_alert(self, message):
        """Show warning alert with blinking text"""
        if self.alert_window:
            self.alert_window.destroy()
            
        self.alert_window = tk.Toplevel(self.root)
        self.alert_window.title("Aviso")
        self.alert_window.geometry("500x180")
        self.alert_window.resizable(False, False)
        
        # Center window
        self.alert_window.update_idletasks()
        width = self.alert_window.winfo_width()
        height = self.alert_window.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.alert_window.geometry(f"+{x}+{y}")
        
        # Split message
        parts = message.split("AVISO: Não foram encontradas legendas em Português neste ficheiro!")
        before_warning = parts[0]
        warning_text = "AVISO: Não foram encontradas legendas em Português neste ficheiro!"
        after_warning = parts[1] if len(parts) > 1 else ""

        # Content frame
        content_frame = tk.Frame(self.alert_window)
        content_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)

        # Before warning
        if before_warning:
            tk.Label(
                content_frame,
                text=before_warning,
                font=('Arial', 10),
                justify=tk.LEFT,
                wraplength=450
            ).pack(anchor=tk.W)

        # Blinking warning
        self.warning_label = tk.Label(
            content_frame,
            text=warning_text,
            font=('Arial', 10, 'bold'),
            fg='red',
            justify=tk.LEFT
        )
        self.warning_label.pack(anchor=tk.W)

        # After warning
        if after_warning:
            tk.Label(
                content_frame,
                text=after_warning,
                font=('Arial', 10),
                justify=tk.LEFT,
                wraplength=450
            ).pack(anchor=tk.W)

        # Styled OK button
        btn_frame = tk.Frame(self.alert_window)
        btn_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(
            btn_frame,
            text="OK",
            command=self.alert_window.destroy,
            bg='black',
            fg='white',
            font=('Arial', 10, 'bold'),
            width=10,
            relief=tk.FLAT,
            padx=10,
            pady=5
        ).pack()

        # Start blinking
        self.blink_warning()
        self.alert_window.grab_set()

    def blink_warning(self):
        """Blink warning text between red and black"""
        if not self.alert_window or not self.alert_window.winfo_exists():
            return
            
        current_color = self.warning_label.cget("foreground")
        new_color = "black" if current_color == "red" else "red"
        self.warning_label.config(foreground=new_color)
        self.alert_window.after(500, self.blink_warning)

    def on_subtitle_select(self, event):
        """Handle subtitle selection"""
        item = self.tree.identify_row(event.y)
        if item:
            self.selected_subtitle_id = self.tree.item(item)['values'][0]
            self.selected_id.set(self.selected_subtitle_id)
            self.btn_process.config(state=tk.NORMAL)

    def apply_title(self):
        """Apply title to selected files"""
        selected_files = [self.file_listbox.get(i) for i in self.file_listbox.curselection()]
        if not selected_files:
            messagebox.showwarning("Aviso", "Selecione pelo menos um arquivo!")
            return
            
        title = self.title_var.get()
        success = 0
        errors = 0
        total = len(selected_files)
        
        self.update_progress(0, "A processar títulos...")
        
        for i, filepath in enumerate(selected_files, 1):
            try:
                if title:
                    subprocess.run(
                        [self.mkvpropedit, filepath, '--edit', 'info', '--set', f'title={title}'],
                        check=True
                    )
                else:
                    subprocess.run(
                        [self.mkvpropedit, filepath, '--edit', 'info', '--set', 'title='],
                        check=True
                    )
                success += 1
                self.update_progress(i/total*100, f"Processando {i} de {total} arquivos")
            except Exception as e:
                errors += 1
                print(f"Erro ao definir título em {os.path.basename(filepath)}: {str(e)}")
                self.update_progress(i/total*100, f"Erro no arquivo {os.path.basename(filepath)}")
        
        if success > 0:
            message = "Título removido com sucesso!" if not title else f"Título '{title}' aplicado com sucesso!"
            self.update_progress(100, f"{message} em {success} arquivo(s)!")
            messagebox.showinfo("Sucesso", f"{message} em {success} arquivo(s)!")
        
        if errors > 0:
            messagebox.showwarning("Aviso", f"Não foi possível modificar o título em {errors} arquivo(s). Verifique o console.")

    def remove_title(self):
        """Remove title from selected files"""
        self.title_var.set("")
        self.apply_title()

    def process_subtitles(self):
        """Process subtitles - set next as default"""
        if not self.selected_subtitle_id:
            messagebox.showwarning("Aviso", "Selecione uma legenda primeiro!")
            return
            
        selected_files = [self.file_listbox.get(i) for i in self.file_listbox.curselection()]
        if not selected_files:
            messagebox.showwarning("Aviso", "Selecione pelo menos um arquivo!")
            return
        
        if not self.apply_to_all.get():
            selected_files = [selected_files[0]]
        
        success = 0
        errors = 0
        total = len(selected_files)
        
        self.update_progress(0, "A processar legendas...")
        
        for i, filepath in enumerate(selected_files, 1):
            try:
                # Get current track info
                result = subprocess.run(
                    [self.mkvmerge, '-i', '--identification-format', 'json', filepath],
                    capture_output=True,
                    text=True,
                    check=True
                )
                
                data = json.loads(result.stdout)
                subtitles = [t for t in data.get('tracks', []) if t.get('type') == 'subtitles']
                subtitle_ids = [track['id'] for track in subtitles]
                
                # Verify selected subtitle exists
                if int(self.selected_subtitle_id) not in subtitle_ids:
                    self.update_progress(i/total*100, f"Legenda {self.selected_subtitle_id} não existe em {os.path.basename(filepath)}")
                    errors += 1
                    continue
                
                # Find next subtitle
                try:
                    current_index = subtitle_ids.index(int(self.selected_subtitle_id))
                    next_id = subtitle_ids[current_index + 1] if current_index < len(subtitle_ids) - 1 else subtitle_ids[0]
                except ValueError:
                    next_id = int(self.selected_subtitle_id) + 1
                
                # Verify next track exists
                if next_id not in subtitle_ids:
                    self.update_progress(i/total*100, f"Legenda seguinte ({next_id}) não existe em {os.path.basename(filepath)}")
                    errors += 1
                    continue
                
                # Reset all subtitle flags
                for track in subtitles:
                    subprocess.run(
                        [self.mkvpropedit, filepath, '--edit', f'track:{track["id"]}', 
                         '--set', 'flag-default=0'],
                        check=True,
                        stderr=subprocess.DEVNULL
                    )
                
                # Set new default subtitle
                subprocess.run(
                    [self.mkvpropedit, filepath, '--edit', f'track:{next_id}', 
                     '--set', 'flag-default=1', '--set', 'flag-forced=0'],
                    check=True,
                    stderr=subprocess.DEVNULL
                )
                
                success += 1
                self.update_progress(i/total*100, f"Processando {i} de {total} arquivos")
            except subprocess.CalledProcessError as e:
                errors += 1
                error_msg = f"Erro em {os.path.basename(filepath)}: "
                if "No track with the ID" in str(e.stderr):
                    error_msg += f"Legenda não encontrada"
                else:
                    error_msg += str(e.stderr).strip()
                self.update_progress(i/total*100, error_msg)
            except Exception as e:
                errors += 1
                self.update_progress(i/total*100, f"Erro em {os.path.basename(filepath)}: {str(e)}")
        
        if success > 0:
            self.update_progress(100, f"Legenda seguinte aplicada em {success} arquivo(s)!")
            messagebox.showinfo("Sucesso", 
                             f"Legenda SEGUINTE aplicada em {success} arquivo(s)!")
            
            if self.current_file in selected_files:
                self.load_subtitles()
        
        if errors > 0:
            messagebox.showwarning("Aviso", 
                                 f"Não foi possível processar {errors} arquivo(s). Verifique os detalhes no log.")

if __name__ == "__main__":
    root = tk.Tk()
    try:
        app = MKVSubtitleEditor(root)
        root.mainloop()
    except Exception as e:
        messagebox.showerror("Erro Fatal", f"Ocorreu um erro inesperado:\n{str(e)}")
        root.destroy()