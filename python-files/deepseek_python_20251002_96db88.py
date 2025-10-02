import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import json
import os
from datetime import datetime, timedelta
import webbrowser
import tempfile
import pandas as pd
from pathlib import Path

class WeeklyPlannerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Planeamento Semanal - Python")
        self.root.geometry("1400x900")
        self.root.configure(bg='#F8FDFE')
        
        # Estado da aplicação
        self.current_file = {
            'name': None,
            'last_saved': None,
            'has_unsaved_changes': False
        }
        
        self.app_state = {
            'active_sheet_id': f"sheet_{int(datetime.now().timestamp())}",
            'sheets': [{
                'id': f"sheet_{int(datetime.now().timestamp())}",
                'title': '🗓️ O Meu Planeamento',
                'data': []
            }]
        }
        
        self.dias_da_semana = ['Dom', 'Seg', 'Ter', 'Qua', 'Qui', 'Sex', 'Sáb']
        
        self.setup_ui()
        self.load_previous_state()
        self.update_file_status()
        
        # Bind Ctrl+S para guardar
        self.root.bind('<Control-s>', lambda e: self.save_file())
        
    def setup_ui(self):
        # Container principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Título
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 20))
        
        self.title_label = ttk.Label(
            title_frame, 
            text="Planeamento Semanal", 
            font=('Montserrat', 24, 'bold'),
            foreground='#333333'
        )
        self.title_label.pack()
        
        # Barra de estado do ficheiro
        self.file_status_frame = ttk.Frame(main_frame, style='FileStatus.TFrame')
        self.file_status_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.file_name_label = ttk.Label(
            self.file_status_frame, 
            text="Sem título",
            font=('Montserrat', 10, 'bold'),
            foreground='#2e7d32'
        )
        self.file_name_label.pack(side=tk.LEFT)
        
        self.file_info_label = ttk.Label(
            self.file_status_frame,
            text="Não guardado",
            font=('Montserrat', 9),
            foreground='#666666'
        )
        self.file_info_label.pack(side=tk.LEFT, padx=(10, 0))
        
        self.rename_btn = ttk.Button(
            self.file_status_frame,
            text="Alterar nome",
            command=self.rename_file
        )
        self.rename_btn.pack(side=tk.RIGHT)
        
        # Gestor de páginas
        page_manager_frame = ttk.Frame(main_frame, style='PageManager.TFrame')
        page_manager_frame.pack(fill=tk.X, pady=(0, 15))
        
        ttk.Label(page_manager_frame, text="Página Atual:", font=('Montserrat', 10, 'bold')).pack(side=tk.LEFT)
        
        self.sheet_selector = ttk.Combobox(
            page_manager_frame, 
            values=[sheet['title'] for sheet in self.app_state['sheets']],
            state="readonly",
            width=20
        )
        self.sheet_selector.set(self.app_state['sheets'][0]['title'])
        self.sheet_selector.pack(side=tk.LEFT, padx=(5, 10))
        self.sheet_selector.bind('<<ComboboxSelected>>', self.on_sheet_changed)
        
        ttk.Button(
            page_manager_frame, 
            text="Nova Página", 
            command=self.add_sheet
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            page_manager_frame,
            text="Apagar Página",
            command=self.delete_sheet
        ).pack(side=tk.LEFT)
        
        # Controlos de seleção
        selection_frame = ttk.Frame(main_frame)
        selection_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.select_all_var = tk.BooleanVar()
        self.select_all_cb = ttk.Checkbutton(
            selection_frame,
            text="Selecionar Todas",
            variable=self.select_all_var,
            command=self.toggle_select_all
        )
        self.select_all_cb.pack(side=tk.LEFT)
        
        self.selected_count_label = ttk.Label(
            selection_frame,
            text="0 atividades selecionadas",
            font=('Montserrat', 9)
        )
        self.selected_count_label.pack(side=tk.LEFT, padx=(20, 0))
        
        # Barra de ferramentas
        toolbar_frame = ttk.Frame(main_frame)
        toolbar_frame.pack(fill=tk.X, pady=(0, 20))
        
        # Botões de ficheiro
        file_btn_frame = ttk.Frame(toolbar_frame)
        file_btn_frame.pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            file_btn_frame,
            text="Guardar",
            command=self.save_file
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            file_btn_frame,
            text="Guardar Como",
            command=self.save_as_file
        ).pack(side=tk.LEFT, padx=(0, 5))
        
        ttk.Button(
            toolbar_frame,
            text="Carregar Ficheiro",
            command=self.load_file
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            toolbar_frame,
            text="Adicionar Atividade",
            command=self.add_row
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            toolbar_frame,
            text="Exportar Excel",
            command=self.export_excel
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            toolbar_frame,
            text="Exportar TXT",
            command=self.export_txt
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            toolbar_frame,
            text="Partilhar WhatsApp",
            command=self.open_whatsapp_dialog
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            toolbar_frame,
            text="Imprimir",
            command=self.print_table
        ).pack(side=tk.LEFT)
        
        # Tabela
        table_frame = ttk.Frame(main_frame)
        table_frame.pack(fill=tk.BOTH, expand=True)
        
        # Criar Treeview com scrollbars
        self.setup_table(table_frame)
        
        # Configurar estilos
        self.setup_styles()
        
    def setup_table(self, parent):
        # Frame para a tabela e scrollbars
        table_container = ttk.Frame(parent)
        table_container.pack(fill=tk.BOTH, expand=True)
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(table_container, orient=tk.VERTICAL)
        h_scrollbar = ttk.Scrollbar(table_container, orient=tk.HORIZONTAL)
        
        # Treeview (tabela)
        self.tree = ttk.Treeview(
            table_container,
            columns=('select', 'data', 'hora', 'dia', 'local', 'grupo', 'atividades', 'descricao', 'observacoes', 'acoes'),
            show='headings',
            yscrollcommand=v_scrollbar.set,
            xscrollcommand=h_scrollbar.set
        )
        
        # Configurar colunas
        columns = {
            'select': 'Sel.',
            'data': 'Data',
            'hora': 'Hora', 
            'dia': 'Dia',
            'local': 'Local',
            'grupo': '⭐ Grupo',
            'atividades': 'Atividades',
            'descricao': 'Descrição',
            'observacoes': 'Observações',
            'acoes': 'Ações'
        }
        
        for col, heading in columns.items():
            self.tree.heading(col, text=heading)
            if col == 'select':
                self.tree.column(col, width=40, minwidth=40)
            elif col == 'acoes':
                self.tree.column(col, width=80, minwidth=80)
            else:
                self.tree.column(col, width=120, minwidth=80)
        
        # Configurar scrollbars
        v_scrollbar.config(command=self.tree.yview)
        h_scrollbar.config(command=self.tree.xview)
        
        # Layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        v_scrollbar.grid(row=0, column=1, sticky='ns')
        h_scrollbar.grid(row=1, column=0, sticky='ew')
        
        table_container.grid_rowconfigure(0, weight=1)
        table_container.grid_columnconfigure(0, weight=1)
        
        # Bind events
        self.tree.bind('<Double-1>', self.on_cell_double_click)
        
    def setup_styles(self):
        style = ttk.Style()
        
        # Configurar estilos personalizados
        style.configure('FileStatus.TFrame', background='#e8f5e8')
        style.configure('PageManager.TFrame', background='white')
        
        # Configurar cores para a treeview
        style.configure("Treeview", 
                       background="#ffffff",
                       foreground="#333333",
                       rowheight=25,
                       fieldbackground="#ffffff")
        
        style.map('Treeview', background=[('selected', '#fff9e6')])
        
    def load_previous_state(self):
        """Carregar estado anterior do ficheiro"""
        try:
            state_file = Path.home() / '.weekly_planner_state.json'
            if state_file.exists():
                with open(state_file, 'r', encoding='utf-8') as f:
                    state = json.load(f)
                    self.current_file['name'] = state.get('current_file_name')
                    self.current_file['last_saved'] = state.get('last_saved')
                    self.current_file['has_unsaved_changes'] = False
        except Exception as e:
            print(f"Erro ao carregar estado anterior: {e}")
    
    def save_state(self):
        """Guardar estado atual"""
        try:
            state_file = Path.home() / '.weekly_planner_state.json'
            state = {
                'current_file_name': self.current_file['name'],
                'last_saved': self.current_file['last_saved']
            }
            with open(state_file, 'w', encoding='utf-8') as f:
                json.dump(state, f, ensure_ascii=False, indent=2)
        except Exception as e:
            print(f"Erro ao guardar estado: {e}")
    
    def update_file_status(self):
        """Atualizar barra de estado do ficheiro"""
        if self.current_file['name'] or self.current_file['has_unsaved_changes']:
            self.file_status_frame.pack(fill=tk.X, pady=(0, 15))
            
            # Atualizar nome do ficheiro
            file_name = self.current_file['name'] or "Sem título"
            self.file_name_label.config(text=file_name)
            
            # Atualizar informação do ficheiro
            if self.current_file['last_saved']:
                last_saved = datetime.fromisoformat(self.current_file['last_saved'])
                info_text = f"Guardado: {last_saved.strftime('%d/%m/%Y %H:%M')}"
                
                if self.current_file['has_unsaved_changes']:
                    info_text += " • ⚠️ Alterações não guardadas"
                    self.file_info_label.config(foreground='#d32f2f')
                else:
                    self.file_info_label.config(foreground='#666666')
            else:
                info_text = "⚠️ Alterações não guardadas" if self.current_file['has_unsaved_changes'] else "Não guardado"
                self.file_info_label.config(foreground='#d32f2f')
            
            self.file_info_label.config(text=info_text)
            
            # Atualizar cor do frame conforme estado
            if self.current_file['has_unsaved_changes']:
                self.file_status_frame.configure(style='FileStatusModified.TFrame')
            else:
                self.file_status_frame.configure(style='FileStatus.TFrame')
        else:
            self.file_status_frame.pack_forget()
        
        # Atualizar título da janela
        title_suffix = " *" if self.current_file['has_unsaved_changes'] else ""
        file_name = self.current_file['name'] or "Sem título"
        self.root.title(f"{file_name}{title_suffix} - Planeamento Semanal")
    
    def mark_as_modified(self):
        """Marcar que há alterações não guardadas"""
        if not self.current_file['has_unsaved_changes']:
            self.current_file['has_unsaved_changes'] = True
            self.update_file_status()
    
    def save_file(self, filename=None):
        """Guardar ficheiro - comportamento inteligente"""
        if filename:
            self.current_file['name'] = filename
        
        # Se não tem nome, comporta-se como "Guardar Como"
        if not self.current_file['name']:
            return self.save_as_file()
        
        try:
            # Guardar dados
            with open(self.current_file['name'], 'w', encoding='utf-8') as f:
                json.dump(self.app_state, f, ensure_ascii=False, indent=2)
            
            # Atualizar estado
            self.current_file['last_saved'] = datetime.now().isoformat()
            self.current_file['has_unsaved_changes'] = False
            
            # Guardar estado da aplicação
            self.save_state()
            self.update_file_status()
            
            messagebox.showinfo("Sucesso", f"Ficheiro '{self.current_file['name']}' guardado com sucesso!")
            return True
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao guardar ficheiro: {e}")
            return False
    
    def save_as_file(self):
        """Guardar como - sempre pede nova localização"""
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("Ficheiros JSON", "*.json"), ("Todos os ficheiros", "*.*")],
            title="Guardar Como",
            initialfile=self.current_file['name'] or "meu_planeamento.json"
        )
        
        if filename:
            return self.save_file(filename)
        return False
    
    def rename_file(self):
        """Alterar nome do ficheiro atual"""
        if self.current_file['name']:
            new_name = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("Ficheiros JSON", "*.json"), ("Todos os ficheiros", "*.*")],
                title="Alterar nome do ficheiro",
                initialfile=self.current_file['name']
            )
            if new_name:
                self.current_file['name'] = new_name
                self.save_file()
        else:
            self.save_as_file()
    
    def load_file(self):
        """Carregar ficheiro"""
        filename = filedialog.askopenfilename(
            filetypes=[("Ficheiros JSON", "*.json"), ("Todos os ficheiros", "*.*")],
            title="Carregar Ficheiro"
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    loaded_state = json.load(f)
                
                # Validar estrutura
                if 'sheets' in loaded_state and 'active_sheet_id' in loaded_state:
                    self.app_state = loaded_state
                    self.current_file['name'] = filename
                    self.current_file['last_saved'] = datetime.now().isoformat()
                    self.current_file['has_unsaved_changes'] = False
                    
                    self.update_sheet_selector()
                    self.render_table()
                    self.save_state()
                    self.update_file_status()
                    
                    messagebox.showinfo("Sucesso", "Ficheiro carregado com sucesso!")
                else:
                    messagebox.showerror("Erro", "Ficheiro de planeamento inválido!")
                    
            except Exception as e:
                messagebox.showerror("Erro", f"Erro ao carregar ficheiro: {e}")
    
    def get_active_sheet(self):
        """Obter página ativa"""
        for sheet in self.app_state['sheets']:
            if sheet['id'] == self.app_state['active_sheet_id']:
                return sheet
        return self.app_state['sheets'][0]
    
    def update_sheet_selector(self):
        """Atualizar selector de páginas"""
        sheets = [sheet['title'] for sheet in self.app_state['sheets']]
        self.sheet_selector['values'] = sheets
        active_sheet = self.get_active_sheet()
        self.sheet_selector.set(active_sheet['title'])
        self.title_label.config(text=active_sheet['title'])
    
    def on_sheet_changed(self, event):
        """Quando muda a página selecionada"""
        selected_title = self.sheet_selector.get()
        for sheet in self.app_state['sheets']:
            if sheet['title'] == selected_title:
                self.app_state['active_sheet_id'] = sheet['id']
                self.title_label.config(text=sheet['title'])
                self.render_table()
                break
    
    def add_sheet(self):
        """Adicionar nova página"""
        sheet_name = tk.simpledialog.askstring(
            "Nova Página", 
            "Nome da nova página:",
            initialvalue=f"Página {len(self.app_state['sheets']) + 1}"
        )
        
        if sheet_name:
            new_sheet = {
                'id': f"sheet_{int(datetime.now().timestamp())}",
                'title': sheet_name,
                'data': []
            }
            self.app_state['sheets'].append(new_sheet)
            self.app_state['active_sheet_id'] = new_sheet['id']
            self.mark_as_modified()
            self.update_sheet_selector()
            self.render_table()
    
    def delete_sheet(self):
        """Apagar página atual"""
        if len(self.app_state['sheets']) <= 1:
            messagebox.showwarning("Aviso", "Não pode apagar a última página!")
            return
        
        active_sheet = self.get_active_sheet()
        if messagebox.askyesno("Confirmar", f"Tem a certeza que quer apagar a página '{active_sheet['title']}'?"):
            self.app_state['sheets'] = [s for s in self.app_state['sheets'] if s['id'] != active_sheet['id']]
            self.app_state['active_sheet_id'] = self.app_state['sheets'][0]['id']
            self.mark_as_modified()
            self.update_sheet_selector()
            self.render_table()
    
    def add_row(self):
        """Adicionar nova linha/atividade"""
        sheet = self.get_active_sheet()
        new_row = {
            'id': f"row_{int(datetime.now().timestamp())}",
            'Data': datetime.now().strftime('%Y-%m-%d'),
            'Hora': '',
            'Local': '',
            'Grupo': '',
            'Atividades': '',
            'Descrição': '',
            'Observações': ''
        }
        sheet['data'].append(new_row)
        self.mark_as_modified()
        self.render_table()
    
    def render_table(self):
        """Renderizar tabela com dados atuais"""
        # Limpar tabela
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        sheet = self.get_active_sheet()
        
        # Ordenar dados por data e hora
        sheet['data'].sort(key=lambda x: (x.get('Data', ''), x.get('Hora', '')))
        
        # Adicionar linhas
        for row_data in sheet['data']:
            dia = self.get_dia_da_semana(row_data.get('Data', ''))
            
            self.tree.insert('', 'end', values=(
                '',  # Checkbox seleção
                row_data.get('Data', ''),
                row_data.get('Hora', ''),
                dia,
                row_data.get('Local', ''),
                row_data.get('Grupo', ''),
                row_data.get('Atividades', ''),
                row_data.get('Descrição', ''),
                row_data.get('Observações', ''),
                '🗑️'  # Ação eliminar
            ), tags=(row_data['id'],))
    
    def on_cell_double_click(self, event):
        """Editar célula ao duplo clique"""
        item = self.tree.selection()[0] if self.tree.selection() else None
        if not item:
            return
        
        column = self.tree.identify_column(event.x)
        col_index = int(column.replace('#', '')) - 1
        
        # Ignorar colunas de seleção e ações
        if col_index in [0, 9]:
            if col_index == 9:  # Coluna ações - eliminar
                self.delete_row(item)
            return
        
        col_names = ['select', 'data', 'hora', 'dia', 'local', 'grupo', 'atividades', 'descricao', 'observacoes', 'acoes']
        col_name = col_names[col_index]
        
        # Obter valores atuais
        values = list(self.tree.item(item, 'values'))
        current_value = values[col_index]
        
        # Criar entrada para edição
        x, y, width, height = self.tree.bbox(item, column)
        
        entry = ttk.Entry(self.tree)
        entry.place(x=x, y=y, width=width, height=height)
        entry.insert(0, current_value)
        entry.focus()
        
        def save_edit(event=None):
            new_value = entry.get()
            values[col_index] = new_value
            self.tree.item(item, values=values)
            entry.destroy()
            
            # Atualizar dados
            self.update_row_data(item, col_name, new_value)
        
        def cancel_edit(event=None):
            entry.destroy()
        
        entry.bind('<Return>', save_edit)
        entry.bind('<Escape>', cancel_edit)
        entry.bind('<FocusOut>', lambda e: save_edit())
    
    def update_row_data(self, item, column, value):
        """Atualizar dados da linha"""
        row_id = self.tree.item(item, 'tags')[0]
        sheet = self.get_active_sheet()
        
        for row_data in sheet['data']:
            if row_data['id'] == row_id:
                # Mapear nome da coluna para campo dos dados
                field_map = {
                    'data': 'Data',
                    'hora': 'Hora', 
                    'local': 'Local',
                    'grupo': 'Grupo',
                    'atividades': 'Atividades',
                    'descricao': 'Descrição',
                    'observacoes': 'Observações'
                }
                
                if column in field_map:
                    row_data[field_map[column]] = value
                    self.mark_as_modified()
                
                # Se a data mudou, atualizar dia da semana
                if column == 'data':
                    self.update_dia_column(item, value)
                break
    
    def update_dia_column(self, item, date_value):
        """Atualizar coluna do dia da semana"""
        dia = self.get_dia_da_semana(date_value)
        values = list(self.tree.item(item, 'values'))
        values[3] = dia  # Coluna dia
        self.tree.item(item, values=values)
    
    def get_dia_da_semana(self, date_string):
        """Obter dia da semana a partir da data"""
        if not date_string:
            return '---'
        try:
            date_obj = datetime.strptime(date_string, '%Y-%m-%d')
            return self.dias_da_semana[date_obj.weekday()]
        except:
            return '---'
    
    def delete_row(self, item):
        """Eliminar linha"""
        if messagebox.askyesno("Confirmar", "Tem a certeza que deseja eliminar esta atividade?"):
            row_id = self.tree.item(item, 'tags')[0]
            sheet = self.get_active_sheet()
            sheet['data'] = [r for r in sheet['data'] if r['id'] != row_id]
            self.tree.delete(item)
            self.mark_as_modified()
            self.update_selected_count()
    
    def toggle_select_all(self):
        """Selecionar/desselecionar todas as linhas"""
        select_all = self.select_all_var.get()
        for item in self.tree.get_children():
            values = list(self.tree.item(item, 'values'))
            values[0] = '✓' if select_all else ''
            self.tree.item(item, values=values)
        self.update_selected_count()
    
    def update_selected_count(self):
        """Atualizar contador de seleções"""
        count = 0
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if values[0] == '✓':
                count += 1
        
        self.selected_count_label.config(text=f"{count} atividades selecionadas")
    
    def get_selected_rows_data(self):
        """Obter dados das linhas selecionadas"""
        selected_data = []
        sheet = self.get_active_sheet()
        
        for item in self.tree.get_children():
            values = self.tree.item(item, 'values')
            if values[0] == '✓':
                row_id = self.tree.item(item, 'tags')[0]
                row_data = next((r for r in sheet['data'] if r['id'] == row_id), None)
                if row_data:
                    selected_data.append(row_data)
        
        return selected_data
    
    def export_excel(self):
        """Exportar para Excel"""
        try:
            selected_data = self.get_selected_rows_data()
            all_data = self.get_active_sheet()['data']
            data_to_export = selected_data if selected_data else all_data
            
            if not data_to_export:
                messagebox.showwarning("Aviso", "Não existem atividades para exportar.")
                return
            
            # Preparar dados
            export_data = []
            for row in data_to_export:
                export_data.append({
                    'Data': row.get('Data', ''),
                    'Hora': row.get('Hora', ''),
                    'Dia': self.get_dia_da_semana(row.get('Data', '')),
                    'Local': row.get('Local', ''),
                    'Grupo': row.get('Grupo', ''),
                    'Atividades': row.get('Atividades', ''),
                    'Descrição': row.get('Descrição', ''),
                    'Observações': row.get('Observações', '')
                })
            
            # Criar DataFrame e exportar
            df = pd.DataFrame(export_data)
            filename = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Ficheiros Excel", "*.xlsx")],
                initialfile="planeamento_atividades.xlsx"
            )
            
            if filename:
                df.to_excel(filename, index=False)
                messagebox.showinfo("Sucesso", "Ficheiro Excel exportado com sucesso!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar para Excel: {e}")
    
    def export_txt(self):
        """Exportar para TXT"""
        try:
            selected_data = self.get_selected_rows_data()
            all_data = self.get_active_sheet()['data']
            data_to_export = selected_data if selected_data else all_data
            
            if not data_to_export:
                messagebox.showwarning("Aviso", "Não existem atividades para exportar.")
                return
            
            # Gerar conteúdo
            sheet = self.get_active_sheet()
            content = f"{sheet['title']}\n\n"
            content += "=" * 50 + "\n\n"
            
            if selected_data:
                content += f"{len(selected_data)} atividades selecionadas\n\n"
            
            for i, row in enumerate(data_to_export, 1):
                content += f"ATIVIDADE {i}\n"
                content += f"Data: {row.get('Data', '')}\n"
                content += f"Hora: {row.get('Hora', '')}\n"
                content += f"Dia: {self.get_dia_da_semana(row.get('Data', ''))}\n"
                content += f"Local: {row.get('Local', '')}\n"
                content += f"Grupo: {row.get('Grupo', '')}\n"
                content += f"Atividades: {row.get('Atividades', '')}\n"
                content += f"Descrição: {row.get('Descrição', '')}\n"
                content += f"Observações: {row.get('Observações', '')}\n"
                content += "-" * 30 + "\n\n"
            
            content += f"Exportado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n"
            
            # Guardar ficheiro
            filename = filedialog.asksaveasfilename(
                defaultextension=".txt",
                filetypes=[("Ficheiros de texto", "*.txt")],
                initialfile="planeamento_atividades.txt"
            )
            
            if filename:
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(content)
                messagebox.showinfo("Sucesso", "Ficheiro TXT exportado com sucesso!")
                
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao exportar para TXT: {e}")
    
    def open_whatsapp_dialog(self):
        """Abrir diálogo de partilha no WhatsApp"""
        dialog = WhatsAppDialog(self.root, self)
        self.root.wait_window(dialog)
    
    def generate_whatsapp_message(self, selected_only=False):
        """Gerar mensagem para WhatsApp"""
        if selected_only:
            data_to_export = self.get_selected_rows_data()
        else:
            data_to_export = self.get_active_sheet()['data']
        
        if not data_to_export:
            return "Não há atividades para partilhar."
        
        sheet = self.get_active_sheet()
        message = f"*{sheet['title']}*\n\n"
        
        if selected_only:
            message += f"*{len(data_to_export)} atividades selecionadas*\n\n"
        
        for i, row in enumerate(data_to_export, 1):
            message += f"*Atividade {i}*\n"
            message += f"📅 Data: {row.get('Data', '')}\n"
            message += f"⏰ Hora: {row.get('Hora', '')}\n"
            message += f"📌 Dia: {self.get_dia_da_semana(row.get('Data', ''))}\n"
            message += f"📍 Local: {row.get('Local', '')}\n"
            message += f"⭐ Grupo: {row.get('Grupo', '')}\n"
            message += f"🎯 Atividades: {row.get('Atividades', '')}\n"
            message += f"📝 Descrição: {row.get('Descrição', '')}\n"
            message += f"📋 Observações: {row.get('Observações', '')}\n"
            message += "─" * 15 + "\n\n"
        
        message += f"_Partilhado em: {datetime.now().strftime('%d/%m/%Y %H:%M')}_"
        return message
    
    def send_to_whatsapp(self, message, include_json=True, include_txt=True):
        """Enviar para WhatsApp"""
        try:
            # Codificar mensagem para URL
            encoded_message = message.replace(' ', '%20').replace('\n', '%0A')
            whatsapp_url = f"https://web.whatsapp.com/send?text={encoded_message}"
            
            # Abrir WhatsApp Web
            webbrowser.open(whatsapp_url)
            
            # Gerar ficheiros temporários se solicitado
            temp_files = []
            if include_json:
                json_file = self._create_temp_json_file()
                temp_files.append(json_file)
            if include_txt:
                txt_file = self._create_temp_txt_file()
                temp_files.append(txt_file)
            
            if temp_files:
                messagebox.showinfo(
                    "Ficheiros Gerados", 
                    f"Ficheiros gerados em:\n" + "\n".join(temp_files) +
                    "\n\nPode agora anexá-los manualmente no WhatsApp."
                )
            
            return True
            
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao abrir WhatsApp: {e}")
            return False
    
    def _create_temp_json_file(self):
        """Criar ficheiro JSON temporário"""
        temp_dir = tempfile.gettempdir()
        filename = os.path.join(temp_dir, "planeamento_whatsapp.json")
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(self.app_state, f, ensure_ascii=False, indent=2)
        
        return filename
    
    def _create_temp_txt_file(self):
        """Criar ficheiro TXT temporário"""
        temp_dir = tempfile.gettempdir()
        filename = os.path.join(temp_dir, "planeamento_whatsapp.txt")
        
        content = self.generate_whatsapp_message(selected_only=False)
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return filename
    
    def print_table(self):
        """Imprimir tabela (simulação)"""
        messagebox.showinfo("Imprimir", "Funcionalidade de impressão seria implementada aqui.")


class WhatsAppDialog(tk.Toplevel):
    """Diálogo para partilha no WhatsApp"""
    
    def __init__(self, parent, app):
        super().__init__(parent)
        self.app = app
        self.title("Partilhar no WhatsApp")
        self.geometry("600x500")
        self.configure(bg='white')
        
        self.setup_ui()
    
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Mensagem
        ttk.Label(main_frame, text="Mensagem para o WhatsApp:", font=('Montserrat', 10, 'bold')).pack(anchor=tk.W)
        
        self.message_text = tk.Text(main_frame, height=8, width=70)
        self.message_text.pack(fill=tk.X, pady=(5, 15))
        
        # Gerar mensagem inicial
        initial_message = self.app.generate_whatsapp_message()
        self.message_text.insert('1.0', initial_message)
        
        # Opções de seleção
        self.selected_only_var = tk.BooleanVar()
        ttk.Checkbutton(
            main_frame,
            text="Incluir apenas atividades selecionadas",
            variable=self.selected_only_var,
            command=self.update_message
        ).pack(anchor=tk.W)
        
        # Opções de ficheiros
        file_frame = ttk.LabelFrame(main_frame, text="Ficheiros para partilhar", padding="10")
        file_frame.pack(fill=tk.X, pady=15)
        
        self.include_json_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            file_frame,
            text="Incluir ficheiro JSON (ficheiro de salvamento completo)",
            variable=self.include_json_var
        ).pack(anchor=tk.W)
        
        self.include_txt_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            file_frame,
            text="Incluir ficheiro TXT (formato legível)",
            variable=self.include_txt_var
        ).pack(anchor=tk.W)
        
        # Botões
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=20)
        
        ttk.Button(
            button_frame,
            text="Cancelar",
            command=self.destroy
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        ttk.Button(
            button_frame,
            text="Abrir WhatsApp",
            command=self.send_whatsapp
        ).pack(side=tk.LEFT)
    
    def update_message(self):
        """Atualizar mensagem quando muda a seleção"""
        selected_only = self.selected_only_var.get()
        new_message = self.app.generate_whatsapp_message(selected_only)
        
        self.message_text.delete('1.0', tk.END)
        self.message_text.insert('1.0', new_message)
    
    def send_whatsapp(self):
        """Enviar para WhatsApp"""
        message = self.message_text.get('1.0', tk.END).strip()
        include_json = self.include_json_var.get()
        include_txt = self.include_txt_var.get()
        
        if not message and not (include_json or include_txt):
            messagebox.showwarning("Aviso", "Selecione pelo menos um ficheiro ou adicione uma mensagem.")
            return
        
        success = self.app.send_to_whatsapp(message, include_json, include_txt)
        if success:
            self.destroy()


def main():
    root = tk.Tk()
    app = WeeklyPlannerApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()