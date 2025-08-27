import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import re
import threading
import queue

class CIDE:
    def __init__(self, root):
        self.root = root
        self.root.title("C IDE")
        self.root.geometry("1000x700")
        
        # Configurações para highlight de sintaxe
        self.configure_tags()
        
        # Fila para comunicação entre threads
        self.queue = queue.Queue()
        
        # Variáveis
        self.current_file = None
        self.compile_process = None
        
        # Criar interface
        self.create_menu()
        self.create_editor()
        self.create_status_bar()
        self.create_console()
        
        # Verificar atualizações da fila periodicamente
        self.check_queue()
        
        # Bindings de teclado
        self.bind_shortcuts()
    
    def configure_tags(self):
        # Tags para highlight de sintaxe
        self.keywords = [
            'auto', 'break', 'case', 'char', 'const', 'continue', 'default',
            'do', 'double', 'else', 'enum', 'extern', 'float', 'for', 'goto',
            'if', 'int', 'long', 'register', 'return', 'short', 'signed',
            'sizeof', 'static', 'struct', 'switch', 'typedef', 'union',
            'unsigned', 'void', 'volatile', 'while', '#include', '#define',
            '#ifdef', '#ifndef', '#endif', '#else', '#pragma'
        ]
        
        # Padrões para reconhecimento de tokens
        self.patterns = {
            'keyword': r'\b(' + '|'.join(self.keywords) + r')\b',
            'string': r'"[^"]*"',
            'comment': r'//.*?$|/\*.*?\*/',
            'function': r'\b[a-zA-Z_][a-zA-Z0-9_]*\s*(?=\()',
            'number': r'\b\d+\b',
            'preprocessor': r'#\s*[a-zA-Z_][a-zA-Z0-9_]*',
        }
        
        # Cores para diferentes tipos de tokens
        self.colors = {
            'keyword': 'blue',
            'string': 'green',
            'comment': 'gray',
            'function': 'purple',
            'number': 'orange',
            'preprocessor': 'brown',
            'error': 'red',
        }
    
    def create_menu(self):
        menubar = tk.Menu(self.root)
        
        # Menu Arquivo
        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Novo", command=self.new_file, accelerator="Ctrl+N")
        file_menu.add_command(label="Abrir", command=self.open_file, accelerator="Ctrl+O")
        file_menu.add_command(label="Salvar", command=self.save_file, accelerator="Ctrl+S")
        file_menu.add_command(label="Salvar Como", command=self.save_as_file, accelerator="Ctrl+Shift+S")
        file_menu.add_separator()
        file_menu.add_command(label="Sair", command=self.exit_ide)
        menubar.add_cascade(label="Arquivo", menu=file_menu)
        
        # Menu Compilar
        compile_menu = tk.Menu(menubar, tearoff=0)
        compile_menu.add_command(label="Compilar", command=self.compile_code, accelerator="F9")
        compile_menu.add_command(label="Executar", command=self.run_code, accelerator="F5")
        compile_menu.add_command(label="Compilar e Executar", command=self.compile_and_run, accelerator="F10")
        menubar.add_cascade(label="Compilar", menu=compile_menu)
        
        self.root.config(menu=menubar)
    
    def create_editor(self):
        # Frame principal para editor e números de linha
        editor_frame = ttk.Frame(self.root)
        editor_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Números de linha
        self.line_numbers = tk.Text(editor_frame, width=4, padx=5, pady=5, takefocus=0, 
                                   border=0, background='lightgray', state='disabled')
        self.line_numbers.pack(side=tk.LEFT, fill=tk.Y)
        
        # Editor de texto
        self.text_area = scrolledtext.ScrolledText(editor_frame, wrap=tk.WORD, padx=5, pady=5, 
                                                  undo=True, autoseparators=True, maxundo=-1)
        self.text_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Configurar tags para syntax highlighting
        for token_type, color in self.colors.items():
            self.text_area.tag_configure(token_type, foreground=color)
            if token_type == 'error':
                self.text_area.tag_configure(token_type, underline=True, underlinefg='red')
        
        # Bind events
        self.text_area.bind('<KeyRelease>', self.on_key_release)
        self.text_area.bind('<Button-1>', self.update_line_numbers)
        self.text_area.bind('<MouseWheel>', self.update_line_numbers)
        
        # Inicializar números de linha
        self.update_line_numbers()
    
    def create_status_bar(self):
        self.status_bar = ttk.Label(self.root, text="Pronto", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
    
    def create_console(self):
        console_frame = ttk.LabelFrame(self.root, text="Console")
        console_frame.pack(fill=tk.BOTH, expand=False, padx=5, pady=5, side=tk.BOTTOM)
        console_frame.config(height=150)
        
        self.console = scrolledtext.ScrolledText(console_frame, wrap=tk.WORD, height=10)
        self.console.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        self.console.config(state='disabled')
    
    def bind_shortcuts(self):
        self.root.bind('<Control-n>', lambda event: self.new_file())
        self.root.bind('<Control-o>', lambda event: self.open_file())
        self.root.bind('<Control-s>', lambda event: self.save_file())
        self.root.bind('<Control-Shift-S>', lambda event: self.save_as_file())
        self.root.bind('<F9>', lambda event: self.compile_code())
        self.root.bind('<F5>', lambda event: self.run_code())
        self.root.bind('<F10>', lambda event: self.compile_and_run())
    
    def on_key_release(self, event=None):
        self.update_line_numbers()
        self.highlight_syntax()
        self.check_errors()
    
    def update_line_numbers(self, event=None):
        # Atualizar números de linha
        lines = self.text_area.get('1.0', 'end-1c').count('\n') + 1
        line_numbers_text = '\n'.join(str(i) for i in range(1, lines + 1))
        
        self.line_numbers.config(state='normal')
        self.line_numbers.delete('1.0', 'end')
        self.line_numbers.insert('1.0', line_numbers_text)
        self.line_numbers.config(state='disabled')
    
    def highlight_syntax(self):
        # Remover todas as tags existentes
        for tag in self.text_area.tag_names():
            if tag != "sel":
                self.text_area.tag_remove(tag, "1.0", "end")
        
        # Obter todo o texto
        text = self.text_area.get("1.0", "end-1c")
        
        # Aplicar highlight para cada padrão
        for token_type, pattern in self.patterns.items():
            for match in re.finditer(pattern, text, re.MULTILINE | re.DOTALL):
                start = f"1.0 + {match.start()} chars"
                end = f"1.0 + {match.end()} chars"
                self.text_area.tag_add(token_type, start, end)
    
    def check_errors(self):
        # Esta é uma verificação básica de erros
        # Em uma implementação real, você usaria um parser de C ou o próprio GCC
        text = self.text_area.get("1.0", "end-1c")
        
        # Remover tags de erro existentes
        self.text_area.tag_remove("error", "1.0", "end")
        
        # Verificar por ponto e vírgula ausentes (exemplo simples)
        lines = text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            # Verificação muito básica - apenas para demonstração
            if line and not line.startswith('#') and not line.startswith('//'):
                if line.endswith('}') or line.endswith('{') or line.endswith(';'):
                    continue
                if 'if' in line or 'for' in line or 'while' in line or 'else' in line:
                    continue
                if line.endswith(',') or line.endswith('(') or line.endswith(')'):
                    continue
                if not line or line.endswith('\\'):
                    continue
                
                # Marcar como possível erro
                start = f"{i+1}.0"
                end = f"{i+1}.end"
                self.text_area.tag_add("error", start, end)
    
    def new_file(self):
        self.text_area.delete(1.0, tk.END)
        self.current_file = None
        self.root.title("C IDE - Novo Arquivo")
        self.status_bar.config(text="Novo arquivo criado")
    
    def open_file(self):
        file_path = filedialog.askopenfilename(
            defaultextension=".c",
            filetypes=[("Arquivos C", "*.c"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                    self.text_area.delete(1.0, tk.END)
                    self.text_area.insert(1.0, content)
                
                self.current_file = file_path
                self.root.title(f"C IDE - {file_path}")
                self.status_bar.config(text=f"Arquivo aberto: {file_path}")
                self.highlight_syntax()
                self.check_errors()
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao abrir arquivo: {str(e)}")
    
    def save_file(self):
        if self.current_file:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(self.current_file, 'w') as file:
                    file.write(content)
                
                self.status_bar.config(text=f"Arquivo salvo: {self.current_file}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")
        else:
            self.save_as_file()
    
    def save_as_file(self):
        file_path = filedialog.asksaveasfilename(
            defaultextension=".c",
            filetypes=[("Arquivos C", "*.c"), ("Todos os arquivos", "*.*")]
        )
        
        if file_path:
            try:
                content = self.text_area.get(1.0, tk.END)
                with open(file_path, 'w') as file:
                    file.write(content)
                
                self.current_file = file_path
                self.root.title(f"C IDE - {file_path}")
                self.status_bar.config(text=f"Arquivo salvo: {file_path}")
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao salvar arquivo: {str(e)}")
    
    def exit_ide(self):
        if messagebox.askokcancel("Sair", "Deseja realmente sair?"):
            self.root.destroy()
    
    def compile_code(self):
        if not self.current_file:
            self.save_as_file()
            if not self.current_file:
                return
        
        # Salvar o arquivo antes de compilar
        self.save_file()
        
        # Limpar console
        self.console.config(state='normal')
        self.console.delete(1.0, tk.END)
        self.console.insert(tk.END, "Compilando...\n")
        self.console.config(state='disabled')
        
        # Compilar em uma thread separada
        threading.Thread(target=self._compile_thread, daemon=True).start()
    
    def _compile_thread(self):
        try:
            # Nome do arquivo de saída
            output_file = os.path.splitext(self.current_file)[0] + ".exe"
            
            # Comando de compilação
            cmd = ["gcc", self.current_file, "-o", output_file, "-Wall"]
            
            # Executar compilação
            process = subprocess.Popen(
                cmd, 
                stdout=subprocess.PIPE, 
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            # Enviar resultado para a fila
            self.queue.put(("compile_result", process.returncode, stdout, stderr))
            
        except Exception as e:
            self.queue.put(("error", str(e)))
    
    def run_code(self):
        if not self.current_file:
            messagebox.showwarning("Aviso", "Salve o arquivo antes de executar")
            return
        
        output_file = os.path.splitext(self.current_file)[0] + ".exe"
        
        if not os.path.exists(output_file):
            messagebox.showwarning("Aviso", "Compile o código antes de executar")
            return
        
        # Limpar console
        self.console.config(state='normal')
        self.console.delete(1.0, tk.END)
        self.console.insert(tk.END, "Executando...\n")
        self.console.config(state='disabled')
        
        # Executar em uma thread separada
        threading.Thread(target=self._run_thread, args=(output_file,), daemon=True).start()
    
    def _run_thread(self, output_file):
        try:
            # Executar o programa compilado
            process = subprocess.Popen(
                [output_file],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            stdout, stderr = process.communicate()
            
            # Enviar resultado para a fila
            self.queue.put(("run_result", process.returncode, stdout, stderr))
            
        except Exception as e:
            self.queue.put(("error", str(e)))
    
    def compile_and_run(self):
        self.compile_code()
        # A execução será iniciada após a compilação bem-sucedida através do check_queue
    
    def check_queue(self):
        # Verificar se há mensagens na fila
        try:
            while True:
                msg = self.queue.get_nowait()
                
                if msg[0] == "compile_result":
                    returncode, stdout, stderr = msg[1], msg[2], msg[3]
                    
                    self.console.config(state='normal')
                    self.console.delete(1.0, tk.END)
                    
                    if returncode == 0:
                        self.console.insert(tk.END, "Compilação bem-sucedida!\n")
                        self.status_bar.config(text="Compilação bem-sucedida")
                        
                        # Se a compilação foi bem-sucedida, executar o programa
                        output_file = os.path.splitext(self.current_file)[0] + ".exe"
                        threading.Thread(target=self._run_thread, args=(output_file,), daemon=True).start()
                    else:
                        self.console.insert(tk.END, "Erros de compilação:\n")
                        self.console.insert(tk.END, stderr)
                        self.status_bar.config(text="Erros de compilação")
                        
                        # Tentar extrair informações de erro para destacar no código
                        self.parse_compiler_errors(stderr)
                    
                    self.console.config(state='disabled')
                
                elif msg[0] == "run_result":
                    returncode, stdout, stderr = msg[1], msg[2], msg[3]
                    
                    self.console.config(state='normal')
                    self.console.insert(tk.END, "\nSaída do programa:\n")
                    self.console.insert(tk.END, stdout)
                    
                    if stderr:
                        self.console.insert(tk.END, "\nErros durante execução:\n")
                        self.console.insert(tk.END, stderr)
                    
                    if returncode != 0:
                        self.console.insert(tk.END, f"\nPrograma terminou com código de saída: {returncode}\n")
                    
                    self.console.config(state='disabled')
                    self.status_bar.config(text="Execução concluída")
                
                elif msg[0] == "error":
                    error_msg = msg[1]
                    self.console.config(state='normal')
                    self.console.insert(tk.END, f"Erro: {error_msg}\n")
                    self.console.config(state='disabled')
                    self.status_bar.config(text="Erro durante operação")
                
                self.queue.task_done()
                
        except queue.Empty:
            pass
        
        # Verificar novamente após 100ms
        self.root.after(100, self.check_queue)
    
    def parse_compiler_errors(self, error_output):
        # Remover tags de erro existentes
        self.text_area.tag_remove("error", "1.0", "end")
        
        # Padrão para extrair informações de erro do GCC
        error_pattern = r"([^\s]+\.c):(\d+):(\d+): (.*)"
        
        for line in error_output.split('\n'):
            match = re.search(error_pattern, line)
            if match:
                filename, line_num, col_num, error_msg = match.groups()
                
                # Se o erro é para o arquivo atual
                if filename == os.path.basename(self.current_file):
                    # Destacar a linha com erro
                    start = f"{line_num}.0"
                    end = f"{line_num}.end"
                    self.text_area.tag_add("error", start, end)
                    
                    # Adicionar informação de erro no console
                    self.console.config(state='normal')
                    self.console.insert(tk.END, f"Linha {line_num}: {error_msg}\n")
                    self.console.config(state='disabled')

if __name__ == "__main__":
    root = tk.Tk()
    ide = CIDE(root)
    root.mainloop()