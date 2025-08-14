import os
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import datetime
import subprocess
from pathlib import Path

# Font configuration
default_font = 'Segoe UI'
title_font = (default_font, 16, 'bold')
subtitle_font = (default_font, 10)
label_font = (default_font, 10)
button_font = (default_font, 10, 'bold')

# Paths
DOCUMENTS = str(Path.home() / 'Documents')
PASTA_PRINCIPAL = os.path.join(DOCUMENTS, 'Projetos Alunos')
PASTA_BACKUP = os.path.join(DOCUMENTS, 'Projetos Alunos - Backup')

CATEGORIAS = ['Games Jr', 'Games Pleno', 'Web Development', 'Mobile Apps', 'Desktop Apps']

# Colors
COLORS = {
    'bg_primary': '#0D1117',
    'bg_secondary': '#161B22',
    'bg_tertiary': '#21262D',
    'bg_quaternary': '#30363D',
    'accent': '#238636',
    'accent_hover': '#2EA043',
    'text_primary': '#F0F6FC',
    'text_secondary': '#8B949E',
    'border': '#30363D',
    'success': '#238636',
    'warning': '#D29922',
    'danger': '#F85149'
}

def criar_pasta_principal():
    os.makedirs(PASTA_PRINCIPAL, exist_ok=True)
    os.makedirs(PASTA_BACKUP, exist_ok=True)

def abrir_pasta_principal():
    if os.path.exists(PASTA_PRINCIPAL):
        subprocess.Popen(f'explorer "{PASTA_PRINCIPAL}"')
    else:
        messagebox.showerror('Erro', 'A pasta principal não existe!')

def organizar_upload():
    nome = entry_nome.get().strip()
    data = entry_data.get().strip()
    categoria = combo_categoria.get().strip()
    arquivo = entry_arquivo.get().strip()
    nome_projeto = entry_projeto.get().strip()

    if not (nome and data and categoria and arquivo):
        messagebox.showerror('Erro', 'Preencha todos os campos obrigatórios e selecione um arquivo!')
        return

    # Validar formato de data
    try:
        datetime.datetime.strptime(data, '%Y-%m-%d')
    except ValueError:
        messagebox.showerror('Erro', 'Formato de data inválido! Use YYYY-MM-DD')
        return

    # Caminhos
    pasta_destino = os.path.join(PASTA_PRINCIPAL, categoria, data, nome)
    pasta_backup = os.path.join(PASTA_BACKUP, categoria, data, nome)
    
    os.makedirs(pasta_destino, exist_ok=True)
    os.makedirs(pasta_backup, exist_ok=True)

    # Nome do arquivo
    ext = os.path.splitext(arquivo)[1]
    if nome_projeto:
        nome_base = f'{nome} - {data} - {nome_projeto}'
    else:
        nome_base = f'{nome} - {data}'

    def nome_disponivel(pasta):
        nome_arquivo = f'{nome_base}{ext}'
        caminho = os.path.join(pasta, nome_arquivo)
        versao = 1
        while os.path.exists(caminho):
            nome_arquivo = f'{nome_base}_v{versao}{ext}'
            caminho = os.path.join(pasta, nome_arquivo)
            versao += 1
        return caminho

    caminho_destino = nome_disponivel(pasta_destino)
    caminho_backup = nome_disponivel(pasta_backup)

    try:
        shutil.copy2(arquivo, caminho_destino)
        shutil.copy2(arquivo, caminho_backup)
        
        messagebox.showinfo('✅ Sucesso', 
                          f'Arquivo enviado com sucesso!\n\n'
                          f'📁 Pasta: {os.path.dirname(caminho_destino)}\n'
                          f'📄 Arquivo: {os.path.basename(caminho_destino)}\n\n'
                          f'💾 Backup criado automaticamente!')
        
        # Limpar campos
        entry_arquivo.delete(0, tk.END)
        entry_projeto.delete(0, tk.END)
        popular_arvore()
        
    except Exception as e:
        messagebox.showerror('❌ Erro', f'Erro ao copiar arquivo:\n{e}')

def selecionar_arquivo():
    filetypes = [
        ('Todos os arquivos', '*.*'),
        ('Arquivos de código', '*.py;*.js;*.html;*.css;*.java;*.cpp;*.c'),
        ('Arquivos compactados', '*.zip;*.rar;*.7z'),
        ('Documentos', '*.pdf;*.docx;*.txt'),
        ('Imagens', '*.png;*.jpg;*.jpeg;*.gif;*.bmp')
    ]
    
    file_path = filedialog.askopenfilename(
        title='Selecione o arquivo do projeto',
        filetypes=filetypes
    )
    
    if file_path:
        entry_arquivo.delete(0, tk.END)
        entry_arquivo.insert(0, file_path)

def preencher_data_hoje():
    hoje = datetime.date.today().strftime('%Y-%m-%d')
    entry_data.delete(0, tk.END)
    entry_data.insert(0, hoje)

def popular_arvore():
    # Limpar árvore
    for item in arvore.get_children():
        arvore.delete(item)
    
    # Dicionário para mapear itens da árvore para caminhos
    arvore.node_paths = {}
    
    def inserir_pasta(pasta, parent=''):
        try:
            itens = sorted(os.listdir(pasta))
        except (OSError, FileNotFoundError):
            return
            
        for item in itens:
            caminho = os.path.join(pasta, item)
            
            if os.path.isdir(caminho):
                # Pasta
                node = arvore.insert(parent, 'end', text=f"📁 {item}", 
                                   values=('', 'Pasta'), open=False)
                arvore.node_paths[node] = caminho
                inserir_pasta(caminho, node)
            else:
                # Arquivo
                try:
                    stat = os.stat(caminho)
                    data_mod = datetime.datetime.fromtimestamp(stat.st_mtime).strftime('%Y-%m-%d')
                    tamanho = f"{stat.st_size / 1024:.1f} KB" if stat.st_size < 1024*1024 else f"{stat.st_size / (1024*1024):.1f} MB"
                    
                    # Ícone baseado na extensão
                    ext = os.path.splitext(item)[1].lower()
                    icon = {
                        '.py': '🐍', '.js': '📜', '.html': '🌐', '.css': '🎨',
                        '.zip': '📦', '.rar': '📦', '.7z': '📦',
                        '.pdf': '📄', '.docx': '📝', '.txt': '📝',
                        '.png': '🖼️', '.jpg': '🖼️', '.jpeg': '🖼️', '.gif': '🖼️'
                    }.get(ext, '📄')
                    
                    node = arvore.insert(parent, 'end', text=f"{icon} {item}", 
                                       values=(data_mod, tamanho), open=False)
                    arvore.node_paths[node] = caminho
                except OSError:
                    continue
    
    if os.path.exists(PASTA_PRINCIPAL):
        inserir_pasta(PASTA_PRINCIPAL)
    else:
        arvore.insert('', 'end', text="📁 Nenhum projeto encontrado", values=('', ''))

def abrir_no_explorer(event):
    item = arvore.focus()
    if not item or not hasattr(arvore, 'node_paths'):
        return
        
    caminho = arvore.node_paths.get(item)
    if not caminho or not os.path.exists(caminho):
        return
        
    try:
        if os.path.isdir(caminho):
            subprocess.Popen(f'explorer "{caminho}"')
        else:
            subprocess.Popen(f'explorer /select,"{caminho}"')
    except Exception as e:
        messagebox.showerror('Erro', f'Erro ao abrir no Explorer:\n{e}')

# Interface Principal
criar_pasta_principal()

root = tk.Tk()
root.title('📚 Organizador de Projetos de Alunos')
root.geometry('1200x700')
root.minsize(1000, 600)
root.configure(bg=COLORS['bg_primary'])

# Configurar estilo
style = ttk.Style()
style.theme_use('clam')

# Configuração de estilos
style.configure('Title.TLabel',
               background=COLORS['bg_primary'],
               foreground=COLORS['text_primary'],
               font=title_font)

style.configure('Subtitle.TLabel',
               background=COLORS['bg_primary'],
               foreground=COLORS['text_secondary'],
               font=subtitle_font)

style.configure('Modern.TFrame',
               background=COLORS['bg_secondary'],
               relief='flat',
               borderwidth=0)

style.configure('Card.TFrame',
               background=COLORS['bg_tertiary'],
               relief='solid',
               borderwidth=1,
               bordercolor=COLORS['border'])

style.configure('Modern.TLabel',
               background=COLORS['bg_tertiary'],
               foreground=COLORS['text_primary'],
               font=label_font)

style.configure('Modern.TEntry',
               fieldbackground=COLORS['bg_quaternary'],
               foreground=COLORS['text_primary'],
               bordercolor=COLORS['border'],
               insertcolor=COLORS['text_primary'],
               relief='solid',
               borderwidth=1)

style.configure('Modern.TCombobox',
               fieldbackground=COLORS['bg_quaternary'],
               foreground=COLORS['text_primary'],
               bordercolor=COLORS['border'],
               arrowcolor=COLORS['text_primary'])

style.configure('Primary.TButton',
               background=COLORS['accent'],
               foreground='white',
               font=button_font,
               relief='flat',
               borderwidth=0,
               padding=(10, 8))

style.map('Primary.TButton',
         background=[('active', COLORS['accent_hover'])])

style.configure('Secondary.TButton',
               background=COLORS['bg_quaternary'],
               foreground=COLORS['text_primary'],
               font=label_font,
               relief='flat',
               borderwidth=0,
               padding=(8, 6))

style.map('Secondary.TButton',
         background=[('active', COLORS['border'])])

style.configure('Modern.Treeview',
               background=COLORS['bg_tertiary'],
               foreground=COLORS['text_primary'],
               fieldbackground=COLORS['bg_tertiary'],
               borderwidth=0,
               relief='flat',
               font=(default_font, 10))

style.configure('Modern.Treeview.Heading',
               background=COLORS['bg_quaternary'],
               foreground=COLORS['text_primary'],
               relief='flat',
               font=(default_font, 10, 'bold'))

# Layout Principal
main_container = tk.Frame(root, bg=COLORS['bg_primary'])
main_container.pack(fill='both', expand=True, padx=20, pady=20)

# Header
header_frame = tk.Frame(main_container, bg=COLORS['bg_primary'])
header_frame.pack(fill='x', pady=(0, 20))

title_label = tk.Label(header_frame, 
                      text='📚 Organizador de Projetos de Alunos',
                      font=title_font,
                      fg=COLORS['text_primary'],
                      bg=COLORS['bg_primary'])
title_label.pack(anchor='w')

subtitle_label = tk.Label(header_frame,
                         text='Gerencie e organize projetos estudantis com facilidade',
                         font=subtitle_font,
                         fg=COLORS['text_secondary'],
                         bg=COLORS['bg_primary'])
subtitle_label.pack(anchor='w', pady=(5, 0))

# Container principal dividido
content_frame = tk.PanedWindow(main_container, 
                              orient='horizontal',
                              bg=COLORS['bg_primary'],
                              sashwidth=10,
                              sashrelief='flat')
content_frame.pack(fill='both', expand=True)

# Painel do formulário
form_panel = tk.Frame(content_frame, bg=COLORS['bg_secondary'], padx=25, pady=25)
content_frame.add(form_panel, width=400, minsize=350)

# Card do formulário
form_card = ttk.Frame(form_panel, style='Card.TFrame', padding=20)
form_card.pack(fill='both', expand=True)

# Campos do formulário
ttk.Label(form_card, text='👤 Nome do Aluno *', style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
entry_nome = ttk.Entry(form_card, style='Modern.TEntry', font=label_font)
entry_nome.pack(fill='x', pady=(0, 15), ipady=6)

ttk.Label(form_card, text='📅 Data (YYYY-MM-DD) *', style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
date_frame = tk.Frame(form_card, bg=COLORS['bg_tertiary'])
date_frame.pack(fill='x', pady=(0, 15))

entry_data = ttk.Entry(date_frame, style='Modern.TEntry', font=label_font)
entry_data.pack(side='left', fill='x', expand=True, ipady=6)

btn_hoje = ttk.Button(date_frame, text='Hoje', command=preencher_data_hoje, 
                     style='Secondary.TButton')
btn_hoje.pack(side='right', padx=(10, 0))

ttk.Label(form_card, text='🏷️ Nome do Projeto (opcional)', style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
entry_projeto = ttk.Entry(form_card, style='Modern.TEntry', font=label_font)
entry_projeto.pack(fill='x', pady=(0, 15), ipady=6)

ttk.Label(form_card, text='📂 Categoria *', style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
combo_categoria = ttk.Combobox(form_card, values=CATEGORIAS, state='readonly', 
                              style='Modern.TCombobox', font=label_font)
combo_categoria.pack(fill='x', pady=(0, 15), ipady=6)
combo_categoria.set(CATEGORIAS[0])

ttk.Label(form_card, text='📎 Arquivo do Projeto *', style='Modern.TLabel').pack(anchor='w', pady=(0, 5))
file_frame = tk.Frame(form_card, bg=COLORS['bg_tertiary'])
file_frame.pack(fill='x', pady=(0, 25))

entry_arquivo = ttk.Entry(file_frame, style='Modern.TEntry', font=label_font)
entry_arquivo.pack(side='left', fill='x', expand=True, ipady=6)

btn_selecionar = ttk.Button(file_frame, text='Procurar', command=selecionar_arquivo,
                           style='Secondary.TButton')
btn_selecionar.pack(side='right', padx=(10, 0))

# Botões principais
btn_upload = ttk.Button(form_card, text='📤 Enviar e Organizar', 
                       command=organizar_upload, style='Primary.TButton')
btn_upload.pack(fill='x', pady=(10, 15), ipady=4)

btn_abrir_pasta = ttk.Button(form_card, text='📁 Abrir Pasta de Projetos',
                            command=abrir_pasta_principal, style='Secondary.TButton')
btn_abrir_pasta.pack(fill='x', ipady=4)

# Painel da árvore
tree_panel = tk.Frame(content_frame, bg=COLORS['bg_secondary'], padx=25, pady=25)
content_frame.add(tree_panel, minsize=500)

# Card da árvore
tree_card = ttk.Frame(tree_panel, style='Card.TFrame', padding=20)
tree_card.pack(fill='both', expand=True)

# Header da árvore
tree_header = tk.Frame(tree_card, bg=COLORS['bg_tertiary'])
tree_header.pack(fill='x', pady=(0, 15))

tree_title = tk.Label(tree_header, text='📋 Projetos Cadastrados',
                     font=(default_font, 12, 'bold'),
                     fg=COLORS['text_primary'],
                     bg=COLORS['bg_tertiary'])
tree_title.pack(side='left')

btn_atualizar = ttk.Button(tree_header, text='🔄 Atualizar', 
                          command=popular_arvore, style='Secondary.TButton')
btn_atualizar.pack(side='right')

# Container da árvore
tree_container = tk.Frame(tree_card, bg=COLORS['bg_tertiary'])
tree_container.pack(fill='both', expand=True)

# Treeview
arvore = ttk.Treeview(tree_container,
                     columns=('date', 'size'),
                     show='tree headings',
                     style='Modern.Treeview')

arvore.heading('#0', text='📁 Nome', anchor='w')
arvore.heading('date', text='📅 Data', anchor='w')
arvore.heading('size', text='📏 Tamanho', anchor='w')

arvore.column('#0', width=350, minwidth=200)
arvore.column('date', width=120, minwidth=100)
arvore.column('size', width=100, minwidth=80)

# Scrollbar
scrollbar = ttk.Scrollbar(tree_container, orient='vertical', command=arvore.yview)
arvore.configure(yscrollcommand=scrollbar.set)

arvore.pack(side='left', fill='both', expand=True)
scrollbar.pack(side='right', fill='y')

# Eventos
arvore.bind('<Double-1>', abrir_no_explorer)

# Inicializar
popular_arvore()
preencher_data_hoje()

# Status bar
status_frame = tk.Frame(main_container, bg=COLORS['bg_secondary'], height=30)
status_frame.pack(fill='x', pady=(15, 0))

status_label = tk.Label(status_frame,
                       text=f"📂 Pasta principal: {PASTA_PRINCIPAL}",
                       font=(default_font, 9),
                       fg=COLORS['text_secondary'],
                       bg=COLORS['bg_secondary'])
status_label.pack(side='left', padx=10, pady=5)

root.mainloop()