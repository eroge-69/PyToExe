import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from pathlib import Path

class PhotoOrganizerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Organizador de Fotos")
        self.root.geometry("600x400")
        self.root.resizable(False, False)
        
        # Configurar estilo
        self.style = ttk.Style()
        self.style.configure('TFrame', background='#f0f0f0')
        self.style.configure('TLabel', background='#f0f0f0', font=('Arial', 10))
        self.style.configure('TButton', font=('Arial', 10))
        self.style.configure('Header.TLabel', font=('Arial', 14, 'bold'))
        
        self.create_widgets()
    
    def create_widgets(self):
        # Cabeçalho
        header_frame = ttk.Frame(self.root)
        header_frame.pack(pady=20)
        
        ttk.Label(header_frame, text="Organizador de Fotos", style='Header.TLabel').pack()
        ttk.Label(header_frame, text="Move todas as fotos de subpastas para uma pasta principal").pack(pady=5)
        
        # Campos de entrada
        input_frame = ttk.Frame(self.root)
        input_frame.pack(pady=20, padx=20, fill='x')
        
        # Pasta origem
        ttk.Label(input_frame, text="Pasta com subpastas (Origem):").grid(row=0, column=0, sticky='w', pady=5)
        self.origin_path = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.origin_path, width=50).grid(row=0, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Procurar", command=self.browse_origin).grid(row=0, column=2, padx=5, pady=5)
        
        # Pasta destino
        ttk.Label(input_frame, text="Pasta principal (Destino):").grid(row=1, column=0, sticky='w', pady=5)
        self.dest_path = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.dest_path, width=50).grid(row=1, column=1, padx=5, pady=5)
        ttk.Button(input_frame, text="Procurar", command=self.browse_dest).grid(row=1, column=2, padx=5, pady=5)
        
        # Botão de ação
        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=20)
        
        ttk.Button(button_frame, text="Organizar Fotos", command=self.organize_photos).pack(pady=10)
        
        # Barra de progresso
        self.progress = ttk.Progressbar(self.root, mode='indeterminate')
        self.progress.pack(pady=10, padx=20, fill='x')
        
        # Área de log
        ttk.Label(self.root, text="Log de atividades:").pack(anchor='w', padx=20)
        
        log_frame = ttk.Frame(self.root)
        log_frame.pack(pady=10, padx=20, fill='both', expand=True)
        
        self.log_text = tk.Text(log_frame, height=10, width=70)
        scrollbar = ttk.Scrollbar(log_frame, orient='vertical', command=self.log_text.yview)
        self.log_text.configure(yscrollcommand=scrollbar.set)
        
        self.log_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
    
    def browse_origin(self):
        folder = filedialog.askdirectory(title="Selecione a pasta com subpastas")
        if folder:
            self.origin_path.set(folder)
    
    def browse_dest(self):
        folder = filedialog.askdirectory(title="Selecione a pasta destino")
        if folder:
            self.dest_path.set(folder)
    
    def log_message(self, message):
        self.log_text.insert('end', message + '\n')
        self.log_text.see('end')
        self.root.update_idletasks()
    
    def organize_photos(self):
        origem = self.origin_path.get()
        destino = self.dest_path.get()
        
        if not origem or not destino:
            messagebox.showerror("Erro", "Por favor, selecione as pastas de origem e destino.")
            return
        
        origem_path = Path(origem)
        destino_path = Path(destino)
        
        if not origem_path.exists():
            messagebox.showerror("Erro", f"A pasta de origem não existe:\n{origem}")
            return
        
        if not destino_path.exists():
            messagebox.showerror("Erro", f"A pasta de destino não existe:\n{destino}")
            return
        
        # Confirmar ação
        confirm = messagebox.askyesno(
            "Confirmar", 
            "Isso moverá todas as fotos das subpastas para a pasta principal.\n\nTem certeza que deseja continuar?"
        )
        
        if not confirm:
            return
        
        # Iniciar organização
        self.progress.start()
        self.log_message("Iniciando organização de fotos...")
        self.log_message(f"Origem: {origem}")
        self.log_message(f"Destino: {destino}")
        self.log_message("-" * 50)
        
        try:
            # Extensões de arquivo de imagem
            extensoes = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp')
            
            # Contadores para estatísticas
            total_movidas = 0
            total_ignoradas = 0
            
            # Percorrer todas as subpastas
            for pasta_atual, subpastas, arquivos in os.walk(origem):
                for arquivo in arquivos:
                    if arquivo.lower().endswith(extensoes):
                        caminho_origem = Path(pasta_atual) / arquivo
                        caminho_destino = destino_path / arquivo
                        
                        # Verificar se arquivo já existe no destino
                        if caminho_destino.exists():
                            # Adicionar sufixo numérico se o arquivo já existir
                            nome = caminho_destino.stem
                            extensao = caminho_destino.suffix
                            contador = 1
                            
                            while caminho_destino.exists():
                                novo_nome = f"{nome}_{contador}{extensao}"
                                caminho_destino = destino_path / novo_nome
                                contador += 1
                        
                        # Mover o arquivo
                        try:
                            shutil.move(str(caminho_origem), str(caminho_destino))
                            self.log_message(f"Movido: {arquivo}")
                            total_movidas += 1
                        except Exception as e:
                            self.log_message(f"Erro ao mover {arquivo}: {e}")
                            total_ignoradas += 1
            
            # Finalizar
            self.progress.stop()
            self.log_message("-" * 50)
            self.log_message("Organização concluída!")
            self.log_message(f"Total de fotos movidas: {total_movidas}")
            self.log_message(f"Total de fotos com erro: {total_ignoradas}")
            
            messagebox.showinfo("Concluído", f"Organização concluída!\n\nFotos movidas: {total_movidas}\nErros: {total_ignoradas}")
            
        except Exception as e:
            self.progress.stop()
            self.log_message(f"Erro durante a organização: {e}")
            messagebox.showerror("Erro", f"Ocorreu um erro durante a organização:\n{e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = PhotoOrganizerApp(root)
    root.mainloop()