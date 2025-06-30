import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import os
from datetime import datetime, date
import locale

# Tenta configurar o locale para Português do Brasil para formatar datas e moeda.
try:
    locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')
except locale.Error:
    try:
        locale.setlocale(locale.LC_ALL, 'Portuguese_Brazil.1252') # Windows
    except locale.Error:
        try:
            locale.setlocale(locale.LC_ALL, 'pt_BR') # Outra tentativa
        except locale.Error:
            print("Não foi possível definir o locale para pt_BR. Usando o padrão do sistema.")

try:
    from tkcalendar import DateEntry
except ImportError:
    messagebox.showerror("Erro de Importação", "A biblioteca tkcalendar não está instalada.\nPor favor, instale com: pip install tkcalendar")
    exit()


from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.units import inch, cm
from reportlab.lib.pagesizes import A4
from reportlab.lib.enums import TA_RIGHT, TA_CENTER, TA_LEFT


class ItemManagerWindow(tk.Toplevel):
    """
    Janela para gerenciar produtos, débitos ou descontos MEI de um profissional.
    """
    def __init__(self, master, app_instance, professional_name, item_type, on_close_callback):
        super().__init__(master)
        self.app_instance = app_instance
        self.professional_name = professional_name
        self.item_type = item_type 
        self.on_close_callback = on_close_callback

        self.title(f"Gerenciar {item_type.replace('_', ' ').capitalize()} - {professional_name}")
        self.geometry("600x450")
        self.transient(master)
        self.grab_set()

        entry_frame = ttk.LabelFrame(self, text=f"Adicionar Novo Item ({item_type.replace('_', ' ').capitalize()})")
        entry_frame.pack(padx=10, pady=10, fill="x")

        ttk.Label(entry_frame, text="Nome/Descrição do Item:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.item_name_entry = ttk.Entry(entry_frame, width=30)
        self.item_name_entry.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        self.item_qty_label = ttk.Label(entry_frame, text="Quantidade:")
        self.item_qty_entry = ttk.Entry(entry_frame, width=10)
        
        self.item_value_label = ttk.Label(entry_frame, text="Valor Unitário (R$):")
        if self.item_type == "mei_descontos":
            self.item_value_label.config(text="Valor do Desconto (R$):")
            self.item_qty_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.item_qty_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
            self.item_qty_entry.insert(0, "1") 
        elif self.item_type == "produtos":
            self.item_value_label.config(text="Valor Comissão Unit. (R$):") 
            self.item_qty_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.item_qty_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")
        else: # Débitos
            self.item_qty_label.grid(row=1, column=0, padx=5, pady=5, sticky="w")
            self.item_qty_entry.grid(row=1, column=1, padx=5, pady=5, sticky="w")

        self.item_value_label.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.item_value_entry = ttk.Entry(entry_frame, width=10)
        self.item_value_entry.grid(row=2, column=1, padx=5, pady=5, sticky="w")

        add_button = ttk.Button(entry_frame, text="Adicionar Item", command=self.add_item)
        add_button.grid(row=3, column=0, columnspan=2, pady=10)

        list_frame = ttk.LabelFrame(self, text=f"Itens Adicionados ({item_type.replace('_', ' ').capitalize()})")
        list_frame.pack(padx=10, pady=10, fill="both", expand=True)

        columns = ("nome", "qtd", "valor_unit", "valor_total")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=5)
        self.tree.heading("nome", text="Nome/Descrição")
        self.tree.heading("qtd", text="Qtd.")
        self.tree.heading("valor_unit", text="Val. Unit./Comissão/Desc. (R$)")
        self.tree.heading("valor_total", text="Val. Total (R$)")

        self.tree.column("nome", width=200)
        self.tree.column("qtd", width=50, anchor="center")
        self.tree.column("valor_unit", width=150, anchor="e") 
        self.tree.column("valor_total", width=100, anchor="e")
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.pack(side="right", fill="y")
        
        remove_button = ttk.Button(list_frame, text="Remover Selecionado", command=self.remove_item)
        remove_button.pack(pady=5)

        self.total_label_var = tk.StringVar(value=f"Total {item_type.replace('_', ' ').capitalize()}: R$ 0.00")
        ttk.Label(self, textvariable=self.total_label_var, font=("Arial", 10, "bold")).pack(pady=5)

        ttk.Button(self, text="Salvar e Fechar", command=self.save_and_close).pack(pady=10)
        self.protocol("WM_DELETE_WINDOW", self.save_and_close)
        self.load_items()

    def load_items(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        items_list = self.app_instance.professionals_data[self.professional_name].get(self.item_type + "_list", [])
        for item_data in items_list:
            self.tree.insert("", "end", values=(
                item_data["nome"],
                item_data["qtd"],
                f"{item_data['valor_unit']:.2f}",
                f"{item_data['valor_total']:.2f}"
            ))
        self.update_total_display()

    def add_item(self):
        nome = self.item_name_entry.get()
        try:
            qtd_str = self.item_qty_entry.get()
            if not qtd_str and self.item_type == "mei_descontos": 
                qtd = 1
            else:
                qtd = int(qtd_str)

            valor_unit_str = self.item_value_entry.get().replace(",", ".")
            valor_unit = float(valor_unit_str)
        except ValueError:
            messagebox.showerror("Erro de Entrada", "Quantidade e Valor devem ser números válidos.", parent=self)
            return

        if not nome or qtd <= 0 or valor_unit < 0: 
            messagebox.showerror("Erro de Entrada", "Nome deve ser preenchido. Quantidade > 0. Valor >= 0.", parent=self)
            return

        valor_total = qtd * valor_unit
        item_data = {"nome": nome, "qtd": qtd, "valor_unit": valor_unit, "valor_total": valor_total}
        
        self.app_instance.professionals_data[self.professional_name].setdefault(self.item_type + "_list", []).append(item_data)
        
        self.load_items()
        self.item_name_entry.delete(0, tk.END)
        self.item_qty_entry.delete(0, tk.END)
        if self.item_type == "mei_descontos":
            self.item_qty_entry.insert(0,"1")
        self.item_value_entry.delete(0, tk.END)

    def remove_item(self):
        selected_item_iid = self.tree.selection()
        if not selected_item_iid:
            messagebox.showwarning("Nenhum item selecionado", "Por favor, selecione um item da lista para remover.", parent=self)
            return

        selected_item_values = self.tree.item(selected_item_iid[0])['values']
        item_nome_to_remove = selected_item_values[0]
        item_qtd_to_remove = int(selected_item_values[1])
        item_valor_unit_to_remove = float(str(selected_item_values[2]).replace(",", "."))

        current_list = self.app_instance.professionals_data[self.professional_name].get(self.item_type + "_list", [])
        
        found_item_index = -1
        for i, item in enumerate(current_list):
            if (item["nome"] == item_nome_to_remove and
                item["qtd"] == item_qtd_to_remove and
                abs(item["valor_unit"] - item_valor_unit_to_remove) < 0.001): 
                found_item_index = i
                break
        
        if found_item_index != -1:
            current_list.pop(found_item_index)
        self.load_items()

    def update_total_display(self):
        items_list = self.app_instance.professionals_data[self.professional_name].get(self.item_type + "_list", [])
        total_value = sum(item['valor_total'] for item in items_list)
        self.total_label_var.set(f"Total {self.item_type.replace('_', ' ').capitalize()}: R$ {total_value:.2f}")

    def save_and_close(self):
        if self.on_close_callback:
            self.on_close_callback(self.professional_name)
        self.destroy()


class ReciboApp:
    def __init__(self, root_window):
        self.root = root_window
        self.root.title("Gerador de Recibos Profissionais")
        self.root.geometry("950x750") 

        self.professionals_data = {} 
        self.professional_ui_elements = {} 

        top_frame = ttk.Frame(self.root, padding="10")
        top_frame.pack(fill="x")

        load_button = ttk.Button(top_frame, text="Carregar CSV de Comissões", command=self.load_comissoes_action)
        load_button.pack(side="left", padx=5)

        today = date.today()
        first_day_month = today.replace(day=1)
        try:
            next_month_first_day = first_day_month.replace(month=first_day_month.month % 12 + 1)
            if first_day_month.month == 12: 
                 next_month_first_day = next_month_first_day.replace(year=first_day_month.year +1)
            last_day_month = next_month_first_day - pd.Timedelta(days=1)
        except ValueError: 
            if first_day_month.month == 2: 
                is_leap = (first_day_month.year % 4 == 0 and first_day_month.year % 100 != 0) or \
                          (first_day_month.year % 400 == 0)
                last_day_month = first_day_month.replace(day=29 if is_leap else 28)
            elif first_day_month.month in [4, 6, 9, 11]: 
                last_day_month = first_day_month.replace(day=30)
            else: 
                last_day_month = first_day_month.replace(day=31)


        ttk.Label(top_frame, text="Período De:").pack(side="left", padx=(10, 0))
        self.start_date_entry = DateEntry(top_frame, width=12, background='darkblue',
                                     foreground='white', borderwidth=2, locale='pt_BR',
                                     date_pattern='dd/MM/yyyy', year=today.year, month=today.month, day=1)
        self.start_date_entry.set_date(first_day_month)
        self.start_date_entry.pack(side="left", padx=5)

        ttk.Label(top_frame, text="Até:").pack(side="left")
        self.end_date_entry = DateEntry(top_frame, width=12, background='darkblue',
                                   foreground='white', borderwidth=2, locale='pt_BR',
                                   date_pattern='dd/MM/yyyy', year=today.year, month=today.month, day=last_day_month.day)
        self.end_date_entry.set_date(last_day_month)
        self.end_date_entry.pack(side="left", padx=5)


        main_canvas_frame = ttk.Frame(self.root, padding="5")
        main_canvas_frame.pack(fill="both", expand=True)
        
        self.canvas = tk.Canvas(main_canvas_frame, borderwidth=0)
        self.professionals_scrollable_frame = ttk.Frame(self.canvas) 
        
        self.scrollbar = ttk.Scrollbar(main_canvas_frame, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.scrollbar.set)

        self.scrollbar.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        self.canvas_window = self.canvas.create_window((0, 0), window=self.professionals_scrollable_frame, anchor="nw")

        self.professionals_scrollable_frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.bind("<Configure>", self.on_canvas_configure)

        bottom_frame = ttk.Frame(self.root, padding="10")
        bottom_frame.pack(fill="x")

        generate_button = ttk.Button(bottom_frame, text="Gerar Recibos em PDF", command=self.generate_receipts_action)
        generate_button.pack()
        
        self.style = ttk.Style()
        self.style.configure("Bold.TLabel", font=("Arial", 10, "bold"))

    def on_frame_configure(self, event=None):
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))

    def on_canvas_configure(self, event=None):
        self.canvas.itemconfig(self.canvas_window, width=event.width)

    def load_comissoes_action(self):
        filepath = filedialog.askopenfilename(
            title="Selecione o arquivo CSV de Comissões",
            filetypes=(("CSV files", "*.csv"), ("All files", "*.*"))
        )
        if not filepath: return
        try:
            try:
                df_comissoes = pd.read_csv(filepath, dtype=str, keep_default_na=False) 
                if df_comissoes.shape[1] == 1 and ';' in df_comissoes.iloc[0,0]: 
                    df_comissoes = pd.read_csv(filepath, delimiter=';', dtype=str, keep_default_na=False)
            except Exception as e:
                 messagebox.showerror("Erro de Leitura CSV", f"Não foi possível ler o CSV. Verifique o delimitador e o arquivo.\nDetalhe: {e}", parent=self.root)
                 return
            
            # --- CONFIGURAÇÕES IMPORTANTES PARA LEITURA DO CSV ---
            col_profissional = 'Profissional'
            col_servico = 'Serviço'
            col_quantidade_servico = 'Quantidade'
            col_valor_comissao_servico = 'Valor comissão' 
            col_identificadora_tipo_servico = 'Filial'  
            valor_csv_para_sem_clube = 'Sem clube'    
            valor_csv_para_com_clube = 'Com clube'    
            # --- FIM DAS CONFIGURAÇÕES IMPORTANTES ---

            required_cols = [col_profissional, col_servico, col_quantidade_servico, col_valor_comissao_servico, col_identificadora_tipo_servico]
            missing_cols = [col for col in required_cols if col not in df_comissoes.columns]
            if missing_cols:
                messagebox.showerror("Erro de CSV", f"As seguintes colunas obrigatórias não foram encontradas no CSV: {', '.join(missing_cols)}.\nVerifique os nomes das colunas no arquivo e nas configurações do código.", parent=self.root)
                return

            df_comissoes[col_valor_comissao_servico] = df_comissoes[col_valor_comissao_servico].astype(str).str.replace('R$', '', regex=False)\
                                                                 .str.strip()\
                                                                 .str.replace('.', '', regex=False)\
                                                                 .str.replace(',', '.', regex=False)
            df_comissoes[col_valor_comissao_servico] = pd.to_numeric(df_comissoes[col_valor_comissao_servico], errors='coerce').fillna(0.0)
            
            df_comissoes[col_quantidade_servico] = pd.to_numeric(df_comissoes[col_quantidade_servico], errors='coerce').fillna(0).astype(int)

            self.professionals_data = {} 
            
            current_professional_name_from_csv = None
            current_commission_category = None 
            
            # print("DEBUG CSV: Iniciando leitura do DataFrame...")
            for index, row in df_comissoes.iterrows():
                # print(f"DEBUG CSV: Lendo linha {index}: {row.to_dict()}")

                identificador_categoria = str(row[col_identificadora_tipo_servico]).strip().lower()
                if identificador_categoria == valor_csv_para_sem_clube.lower():
                    current_commission_category = "Sem Clube"
                    # print(f"DEBUG CSV: Categoria mudou para: Sem Clube (linha {index})")
                    continue 
                elif identificador_categoria == valor_csv_para_com_clube.lower():
                    current_commission_category = "Com Clube"
                    # print(f"DEBUG CSV: Categoria mudou para: Com Clube (linha {index})")
                    continue 

                profissional_na_linha = str(row[col_profissional]).strip()
                servico_na_linha = str(row[col_servico]).strip()

                if servico_na_linha.lower() == 'total' or not profissional_na_linha or not servico_na_linha:
                    # print(f"DEBUG CSV: Linha {index} ignorada (Total ou Prof/Serviço vazio).")
                    continue
                
                if profissional_na_linha not in self.professionals_data:
                    # print(f"DEBUG CSV: Novo profissional detectado: {profissional_na_linha}")
                    self.professionals_data[profissional_na_linha] = {
                        "comissao_servicos_sem_clube_csv_val": 0.0,
                        "servicos_sem_clube_details": [],
                        "comissao_servicos_com_clube_csv_val": 0.0, 
                        "servicos_com_clube_details_csv": [],
                        "comissao_assinaturas_manual_var": tk.DoubleVar(value=0.0), 
                        "produtos_list": [], "debitos_list": [], "mei_descontos_list": [],
                        "total_produtos_var": tk.DoubleVar(value=0.0), 
                        "total_debitos_var": tk.DoubleVar(value=0.0),
                        "total_mei_descontos_var": tk.DoubleVar(value=0.0),
                        "liquido_a_receber_var": tk.DoubleVar(value=0.0)
                    }
                
                if current_commission_category and profissional_na_linha:
                    try:
                        quantidade = int(row[col_quantidade_servico])
                        valor_comissao = float(row[col_valor_comissao_servico])
                    except ValueError:
                        # print(f"DEBUG CSV: Erro conversão Qtd/Valor para {servico_na_linha} de {profissional_na_linha}. Linha {index}")
                        continue 

                    # print(f"DEBUG CSV: Processando Serviço: {servico_na_linha}, Qtd: {quantidade}, ValCom: {valor_comissao} para {profissional_na_linha} [{current_commission_category}]")

                    if current_commission_category == "Sem Clube":
                        if quantidade > 0 or valor_comissao > 0:
                            self.professionals_data[profissional_na_linha]["servicos_sem_clube_details"].append({'servico': servico_na_linha, 'quantidade': quantidade})
                            self.professionals_data[profissional_na_linha]["comissao_servicos_sem_clube_csv_val"] += valor_comissao
                    elif current_commission_category == "Com Clube":
                        if quantidade > 0: 
                            self.professionals_data[profissional_na_linha]["servicos_com_clube_details_csv"].append({'servico': servico_na_linha, 'quantidade': quantidade})
                            self.professionals_data[profissional_na_linha]["comissao_servicos_com_clube_csv_val"] += valor_comissao 

            # print(f"DEBUG CSV: Processamento finalizado. {len(self.professionals_data)} profissionais carregados.")
            # for name, data_prof in self.professionals_data.items():
            #     print(f"DEBUG CSV: Dados Finais para {name}: SemClubeVal={data_prof['comissao_servicos_sem_clube_csv_val']}, ServSemClube={len(data_prof['servicos_sem_clube_details'])}, ComClubeValCSV={data_prof['comissao_servicos_com_clube_csv_val']}, ServComClube={len(data_prof['servicos_com_clube_details_csv'])}")


            if not self.professionals_data:
                messagebox.showwarning("Aviso", "Nenhum dado de profissional foi processado do CSV. Verifique o arquivo, as configurações de nome de coluna no código e o console para mensagens de DEBUG CSV.", parent=self.root)
            else:
                messagebox.showinfo("Sucesso", f"{len(self.professionals_data)} profissional(is) processado(s) do CSV!", parent=self.root)
            self.display_professionals_ui()

        except Exception as e:
            messagebox.showerror("Erro ao Processar CSV", f"Ocorreu um erro: {e}\nVerifique o console para detalhes.", parent=self.root)
            import traceback
            print(f"Detalhes completos do erro CSV: {traceback.format_exc()}")

    def _on_assinatura_focus_in(self, event, entry_widget):
        """Limpa o campo se for '0.00' ou '0'."""
        if entry_widget.get() in ["0.00", "0,00", "0.0", "0,0", "0"]:
            entry_widget.delete(0, tk.END)

    def _on_assinatura_focus_out(self, event, entry_widget, entry_var, prof_name):
        """Valida e atualiza a DoubleVar. Se vazio, define DoubleVar como 0.0 mas deixa Entry visualmente vazia."""
        current_value_str = entry_widget.get().strip()
        val_float = 0.0
        try:
            if current_value_str: # Se não estiver vazio
                val_float = float(current_value_str.replace(",", "."))
        except ValueError: # Se a entrada não for um número válido
            val_float = 0.0 # Default para 0.0
        
        entry_var.set(val_float) # Atualiza a DoubleVar

        # Decide o que mostrar na Entry
        if not current_value_str and val_float == 0.0:
            entry_widget.delete(0, tk.END) # Mantém visualmente vazio
            entry_widget.insert(0, "0.00") # Ou reinsere o placeholder
        elif current_value_str and val_float == 0.0 and current_value_str not in ["0.00", "0,00", "0.0", "0,0", "0"]:
             # Se o usuário digitou algo que resultou em 0 (ex: texto inválido), mostra "0.00"
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, "0.00")
        elif val_float != 0.0 : # Se for um valor válido diferente de zero, formata
            entry_widget.delete(0,tk.END)
            # Tenta formatar com o locale para vírgula decimal, se não, ponto.
            try:
                formatted_val = locale.format_string("%.2f", val_float, grouping=False)
            except:
                formatted_val = f"{val_float:.2f}"
            entry_widget.insert(0, formatted_val)


        self.update_professional_summary(prof_name)


    def display_professionals_ui(self):
        for widget in self.professionals_scrollable_frame.winfo_children():
            widget.destroy()
        self.professional_ui_elements = {}

        if not self.professionals_data:
            ttk.Label(self.professionals_scrollable_frame, text="Nenhum profissional. Carregue o CSV.").pack(pady=20)
            return

        for prof_name, data in sorted(self.professionals_data.items()):
            outer_prof_frame = ttk.Frame(self.professionals_scrollable_frame)
            outer_prof_frame.pack(fill="x", padx=10, pady=5)

            header_frame = ttk.Frame(outer_prof_frame)
            header_frame.pack(fill="x")
            
            prof_label = ttk.Label(header_frame, text=prof_name, font=("Arial", 12, "bold"))
            prof_label.pack(side="left", padx=(0,10))

            details_frame = ttk.Frame(outer_prof_frame, relief="groove", borderwidth=1, padding="5")
            
            toggle_button = ttk.Button(header_frame, text="+", width=3, # Inicia com "+" para indicar recolhido
                                       command=lambda df=details_frame: self.toggle_frame_visibility(df))
            toggle_button.pack(side="left")
            
            comissoes_frame = ttk.Frame(details_frame)
            comissoes_frame.pack(fill="x", pady=(0,5))

            ttk.Label(comissoes_frame, text=f"Com. Serv. Sem Clube (CSV): R$ {data.get('comissao_servicos_sem_clube_csv_val', 0.0):.2f}").grid(row=0, column=0, sticky="w", padx=5, pady=2)
            ttk.Label(comissoes_frame, text=f"Com. Serv. Com Clube (CSV): R$ {data.get('comissao_servicos_com_clube_csv_val', 0.0):.2f}").grid(row=1, column=0, sticky="w", padx=5, pady=2)
            
            ttk.Label(comissoes_frame, text="Com. Sobre Assinaturas (MANUAL R$):").grid(row=0, column=1, sticky="w", padx=5, pady=2) 
            
            assinatura_var = data["comissao_assinaturas_manual_var"]
            assinatura_var.set(0.0) 
            com_assinaturas_manual_entry = ttk.Entry(comissoes_frame, width=10) 
            com_assinaturas_manual_entry.insert(0, "0.00") 
            com_assinaturas_manual_entry.grid(row=0, column=2, sticky="w", padx=5, pady=2)
            
            com_assinaturas_manual_entry.bind("<FocusIn>", lambda e, entry=com_assinaturas_manual_entry, var=assinatura_var: self._on_assinatura_focus_in(e, entry, var))
            com_assinaturas_manual_entry.bind("<FocusOut>", lambda e, entry=com_assinaturas_manual_entry, var=assinatura_var, p_name=prof_name: self._on_assinatura_focus_out(e, entry, var, p_name))
            
            btn_frame = ttk.Frame(details_frame)
            btn_frame.pack(fill="x", pady=5)
            ttk.Button(btn_frame, text="Ger. Ganhos Produtos", command=lambda p=prof_name: self.open_item_manager(p, "produtos")).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Ger. Débitos", command=lambda p=prof_name: self.open_item_manager(p, "debitos")).pack(side="left", padx=5)
            ttk.Button(btn_frame, text="Ger. Descontos MEI", command=lambda p=prof_name: self.open_item_manager(p, "mei_descontos")).pack(side="left", padx=5)

            parciais_frame = ttk.Frame(details_frame)
            parciais_frame.pack(fill="x", pady=5)

            total_ganhos_produtos_label = ttk.Label(parciais_frame, text="Total Ganhos Produtos: R$ 0.00") 
            total_ganhos_produtos_label.grid(row=0, column=0, sticky="w", padx=5, pady=2)
            total_debitos_label = ttk.Label(parciais_frame, text="Total Débitos (dedução): R$ 0.00")
            total_debitos_label.grid(row=0, column=1, sticky="w", padx=5, pady=2)
            total_mei_label = ttk.Label(parciais_frame, text="Total Descontos MEI: R$ 0.00") 
            total_mei_label.grid(row=0, column=2, sticky="w", padx=5, pady=2)

            liquido_label = ttk.Label(details_frame, text="Líquido a Receber: R$ 0.00", style="Bold.TLabel") 
            liquido_label.pack(fill="x", pady=(5,0), padx=5)

            self.professional_ui_elements[prof_name] = {
                "com_assinaturas_manual_entry": com_assinaturas_manual_entry, 
                "total_ganhos_produtos_label": total_ganhos_produtos_label, 
                "total_debitos_label": total_debitos_label,
                "total_mei_label": total_mei_label, 
                "liquido_label": liquido_label,
                "details_frame": details_frame, 
                "toggle_button": toggle_button 
            }
            details_frame.pack_forget() # Inicia recolhido
            self.update_professional_summary(prof_name) 
        
        self.professionals_scrollable_frame.update_idletasks() 
        self.on_frame_configure() 

    def toggle_frame_visibility(self, frame_to_toggle):
        """Mostra ou esconde o frame de detalhes."""
        button = None
        for ui_set in self.professional_ui_elements.values():
            if ui_set["details_frame"] == frame_to_toggle:
                button = ui_set["toggle_button"]
                break

        if frame_to_toggle.winfo_ismapped():
            frame_to_toggle.pack_forget()
            if button: button.config(text="+")
        else:
            frame_to_toggle.pack(fill="x", expand=True, pady=(5,0))
            if button: button.config(text="-")
        
        self.professionals_scrollable_frame.update_idletasks()
        self.on_frame_configure()


    def open_item_manager(self, professional_name, item_type):
        ItemManagerWindow(self.root, self, professional_name, item_type, 
                          on_close_callback=self.update_professional_summary)

    def update_professional_summary(self, prof_name):
        if prof_name not in self.professionals_data or prof_name not in self.professional_ui_elements: 
            return

        data = self.professionals_data[prof_name]
        ui_elems = self.professional_ui_elements[prof_name]
        
        comissao_assinaturas_manual = 0.0 
        try:
            comissao_assinaturas_manual = data["comissao_assinaturas_manual_var"].get()
        except (ValueError, tk.TclError) as e:
            comissao_assinaturas_manual = 0.0
            if "comissao_assinaturas_manual_var" in data: 
                 data["comissao_assinaturas_manual_var"].set(0.0)


        comissao_servicos_sem_clube_csv = data.get("comissao_servicos_sem_clube_csv_val", 0.0)
        comissao_servicos_com_clube_csv = data.get("comissao_servicos_com_clube_csv_val", 0.0)

        total_ganhos_produtos = sum(p['valor_total'] for p in data.get('produtos_list', [])) 
        total_debitos = sum(d['valor_total'] for d in data.get('debitos_list', [])) 
        total_mei_descontos = sum(m['valor_total'] for m in data.get('mei_descontos_list', []))

        data["total_produtos_var"].set(total_ganhos_produtos) 
        data["total_debitos_var"].set(total_debitos)   
        data["total_mei_descontos_var"].set(total_mei_descontos)

        total_comissoes_gerais = comissao_servicos_sem_clube_csv + comissao_servicos_com_clube_csv + comissao_assinaturas_manual
        
        total_creditos = total_comissoes_gerais + total_ganhos_produtos 
        deducoes_para_liquido = total_mei_descontos 
        liquido = total_creditos - deducoes_para_liquido
        data["liquido_a_receber_var"].set(liquido) 

        # print(f"DEBUG CALC LIQUIDO ({prof_name}): ComServSemClubeCSV={comissao_servicos_sem_clube_csv}, ComServComClubeCSV={comissao_servicos_com_clube_csv}, ComAssinaturasManual={comissao_assinaturas_manual}, TotalComissoes={total_comissoes_gerais}, GanhosProd={total_ganhos_produtos}, DebitosExibicao={total_debitos}, MEI={total_mei_descontos}, TotalCred={total_creditos}, DeducoesParaLiquido={deducoes_para_liquido}, Liquido={liquido}")

        ui_elems["total_ganhos_produtos_label"].config(text=f"Total Ganhos Produtos: R$ {total_ganhos_produtos:.2f}") 
        ui_elems["total_debitos_label"].config(text=f"Débitos Consumo/Compra: R$ {total_debitos:.2f}") 
        ui_elems["total_mei_label"].config(text=f"Total Descontos MEI: R$ {total_mei_descontos:.2f}") 
        ui_elems["liquido_label"].config(text=f"Líquido a Receber: R$ {liquido:.2f}")

    def format_currency(self, value):
        try:
            return locale.currency(value, grouping=True, symbol='R$ ') 
        except Exception: 
            formatted_value = f"{value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            return f"R$ {formatted_value}"


    def generate_receipts_action(self):
        start_date_obj = self.start_date_entry.get_date()
        end_date_obj = self.end_date_entry.get_date()
        start_date_str = start_date_obj.strftime('%d/%m/%Y')
        end_date_str = end_date_obj.strftime('%d/%m/%Y')
        
        try:
            mes_nota_fiscal = start_date_obj.strftime("%B").capitalize()
            ano_nota_fiscal = start_date_obj.strftime("%Y")
        except Exception:
            mes_nota_fiscal = "REFERÊNCIA" 
            ano_nota_fiscal = ""


        if not self.professionals_data:
            messagebox.showwarning("Sem Dados", "Nenhum profissional carregado. Carregue o CSV e verifique os dados.", parent=self.root)
            return

        output_dir = filedialog.askdirectory(title="Selecione a pasta para salvar os recibos PDF")
        if not output_dir: return

        styles = getSampleStyleSheet()
        style_normal = styles['Normal']
        style_normal_right = ParagraphStyle(name='NormalRight', parent=styles['Normal'], alignment=TA_RIGHT)
        style_bold = ParagraphStyle(name='Bold', parent=styles['Normal'], fontName='Helvetica-Bold')
        style_heading = ParagraphStyle(name='Heading1', parent=styles['Heading1'], alignment=TA_CENTER, fontSize=14, spaceBottom=12, fontName='Helvetica-Bold')
        style_subheading = ParagraphStyle(name='Heading2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=11, spaceBefore=8, spaceBottom=2, leftIndent=0) 
        style_table_text = styles['Normal']
        style_table_text_right = ParagraphStyle(name='TableTextRight', parent=styles['Normal'], alignment=TA_RIGHT)
        style_total_label = ParagraphStyle(name='TotalLabel', parent=style_bold, alignment=TA_LEFT) 
        style_total_value = ParagraphStyle(name='TotalValue', parent=style_bold, alignment=TA_RIGHT)
        style_nota_fiscal_header = ParagraphStyle(name='NotaFiscalHeader', parent=style_bold, fontSize=10, spaceBefore=10, spaceBottom=4)
        style_nota_fiscal_text = ParagraphStyle(name='NotaFiscalText', parent=styles['Normal'], fontSize=9, leading=11)


        num_recibos_gerados = 0
        for prof_name, data in self.professionals_data.items():
            self.update_professional_summary(prof_name) 

            comissao_servicos_sem_clube_csv = data.get("comissao_servicos_sem_clube_csv_val", 0.0)
            servicos_sem_clube_details = data.get("servicos_sem_clube_details", [])
            
            comissao_servicos_com_clube_csv = data.get("comissao_servicos_com_clube_csv_val", 0.0)
            servicos_com_clube_details_csv = data.get("servicos_com_clube_details_csv", [])
            comissao_assinaturas_manual = data.get("comissao_assinaturas_manual_var").get()
            
            produtos_list = data.get("produtos_list", [])
            debitos_list = data.get("debitos_list", [])
            mei_descontos_list = data.get("mei_descontos_list", [])

            total_ganhos_produtos = data.get("total_produtos_var").get()
            total_debitos_consumo = data.get("total_debitos_var").get() 
            total_mei_descontos = data.get("total_mei_descontos_var").get()
            
            total_comissoes_gerais = comissao_servicos_sem_clube_csv + comissao_servicos_com_clube_csv + comissao_assinaturas_manual
            total_creditos = total_comissoes_gerais + total_ganhos_produtos
            
            deducoes_para_liquido = total_mei_descontos
            liquido_a_receber = total_creditos - deducoes_para_liquido
            
            valor_nota_fiscal = total_comissoes_gerais + total_ganhos_produtos 

            clean_prof_name = "".join(c if c.isalnum() else "_" for c in prof_name)
            period_str_file = f"{self.start_date_entry.get_date().strftime('%d-%m-%Y')}_a_{self.end_date_entry.get_date().strftime('%d-%m-%Y')}"
            filename = os.path.join(output_dir, f"Recibo_{clean_prof_name}_{period_str_file}.pdf")

            doc = SimpleDocTemplate(filename, pagesize=A4, topMargin=1.5*cm, bottomMargin=1.5*cm, leftMargin=1.5*cm, rightMargin=1.5*cm)
            story = []

            story.append(Paragraph(f"DEMONSTRATIVO DE PAGAMENTO - {prof_name.upper()}", style_heading))
            story.append(Paragraph(f"Período: {start_date_str} a {end_date_str}", ParagraphStyle(name='Period', parent=styles['Normal'], alignment=TA_CENTER, spaceBottom=10)))
            
            if servicos_sem_clube_details:
                sem_clube_data = [["Serviço Sem Clube", "Quantidade"]] 
                for item in servicos_sem_clube_details:
                    sem_clube_data.append([Paragraph(item['servico'], style_table_text), Paragraph(str(item['quantidade']), style_table_text_right)])
                sem_clube_table = Table(sem_clube_data, colWidths=[doc.width - 2.5*cm, 2*cm])
                sem_clube_table.setStyle(TableStyle([
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), 
                    ('ALIGN', (0,0), (-1,0), 'CENTER'),
                    ('ALIGN', (1,1), (1,-1), 'RIGHT'), 
                    ('LINEBELOW', (0,0), (-1,0), 0.5, colors.grey), 
                    ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ]))
                story.append(sem_clube_table)
                story.append(Paragraph(f"Subtotal Serviços Sem Clube: {self.format_currency(comissao_servicos_sem_clube_csv)}", style_total_value))
                story.append(Spacer(1, 0.15*cm)) # Espaço reduzido


            if servicos_com_clube_details_csv:
                com_clube_data = [["Serviço Com Clube", "Quantidade"]] 
                for item in servicos_com_clube_details_csv:
                    com_clube_data.append([Paragraph(item['servico'], style_table_text), Paragraph(str(item['quantidade']), style_table_text_right)])
                com_clube_table = Table(com_clube_data, colWidths=[doc.width - 2.5*cm, 2*cm])
                com_clube_table.setStyle(TableStyle([
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), 
                    ('ALIGN', (0,0), (-1,0), 'CENTER'),
                    ('ALIGN', (1,1), (1,-1), 'RIGHT'), 
                    ('LINEBELOW', (0,0), (-1,0), 0.5, colors.grey), 
                    ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ]))
                story.append(com_clube_table)
                story.append(Paragraph(f"Subtotal Serviços Com Clube: {self.format_currency(comissao_servicos_com_clube_csv)}", style_total_value))
                story.append(Spacer(1, 0.15*cm)) # Espaço reduzido

            # Tabela de Totais de Comissão (sem o título "TOTAIS DE COMISSÃO")
            totais_comissao_data = [
                [Paragraph("Subtotal Comissões de Serviços (Sem Clube + Com Clube):", style_table_text), Paragraph(self.format_currency(comissao_servicos_sem_clube_csv + comissao_servicos_com_clube_csv), style_table_text_right)],
                [Paragraph("Comissão Total Sobre Assinaturas:", style_table_text), Paragraph(self.format_currency(comissao_assinaturas_manual), style_table_text_right)],
            ]
            # A "Comissão Total" agora é a soma de todas as comissões E ganhos com produtos.
            # No entanto, para a seção de totais de comissão, vamos mostrar a comissão de serviços + assinaturas.
            # O total_comissoes_gerais já é isso.
            # Ganhos com produtos serão somados no Resumo Financeiro para "Total de Créditos".

            # TOTAL GERAL DE COMISSÕES (Serviços + Assinaturas)
            totais_comissao_data.append([Paragraph("<b>COMISSÃO TOTAL (Serviços + Assinaturas):</b>", style_total_label), Paragraph(self.format_currency(total_comissoes_gerais), style_total_value)]) 

            totais_comissao_table = Table(totais_comissao_data, colWidths=[doc.width - 2.5*cm, 2*cm])
            totais_comissao_table.setStyle(TableStyle([
                ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                ('LINEABOVE', (0,-1), (-1,-1), 0.5, colors.black),
                ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2),
            ]))
            story.append(totais_comissao_table)
            story.append(Spacer(1, 0.15*cm)) # Espaço reduzido conforme imagem
            
            if produtos_list:
                produtos_data = [["Produto Vendido", "Qtd", "Comissão Total"]]
                for prod in produtos_list:
                    produtos_data.append([Paragraph(prod['nome'], style_table_text), Paragraph(str(prod['qtd']), style_table_text_right), Paragraph(self.format_currency(prod['valor_total']), style_table_text_right)])
                produtos_data.append([Paragraph("TOTAL GANHOS PRODUTOS:", style_total_label), "", Paragraph(self.format_currency(total_ganhos_produtos), style_total_value)])
                produtos_table = Table(produtos_data, colWidths=[doc.width - 3.5*cm, 1*cm, 2*cm])
                produtos_table.setStyle(TableStyle([
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('ALIGN', (0,0), (-1,0), 'CENTER'),
                    ('ALIGN', (1,1), (1,-1), 'RIGHT'), ('ALIGN', (2,1), (2,-1), 'RIGHT'),
                    ('LINEBELOW', (0,0), (-1,0), 0.5, colors.grey),
                    ('LINEABOVE', (0,-1), (-1,-1), 0.5, colors.black),
                    ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                    ('SPAN', (0,-1), (1,-1)), 
                    ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ]))
                story.append(produtos_table)
                story.append(Spacer(1, 0.15*cm)) # Espaço reduzido
            
            if debitos_list:
                debitos_data = [["Débito de Consumo/Compra", "Qtd", "Valor Total"]]
                for deb in debitos_list:
                    debitos_data.append([Paragraph(deb['nome'], style_table_text), Paragraph(str(deb['qtd']), style_table_text_right), Paragraph(self.format_currency(deb['valor_total']), style_table_text_right)])
                debitos_data.append([Paragraph("TOTAL DÉBITOS DE CONSUMO/COMPRA:", style_total_label), "", Paragraph(self.format_currency(total_debitos_consumo), style_total_value)])
                debitos_table = Table(debitos_data, colWidths=[doc.width - 3.5*cm, 1*cm, 2*cm])
                debitos_table.setStyle(TableStyle([
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('ALIGN', (0,0), (-1,0), 'CENTER'),
                    ('ALIGN', (1,1), (1,-1), 'RIGHT'), ('ALIGN', (2,1), (2,-1), 'RIGHT'),
                    ('LINEBELOW', (0,0), (-1,0), 0.5, colors.grey),
                    ('LINEABOVE', (0,-1), (-1,-1), 0.5, colors.black),
                    ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                    ('SPAN', (0,-1), (1,-1)), 
                    ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ]))
                story.append(debitos_table)
                story.append(Spacer(1, 0.15*cm)) # Espaço reduzido

            if mei_descontos_list:
                mei_data = [["Desconto MEI / Outro", "Valor Total"]]
                for mei in mei_descontos_list:
                    mei_data.append([Paragraph(mei['nome'], style_table_text), Paragraph(self.format_currency(mei['valor_total']), style_table_text_right)])
                mei_data.append([Paragraph("TOTAL DESCONTOS MEI / OUTROS:", style_total_label), Paragraph(self.format_currency(total_mei_descontos), style_total_value)])
                mei_table = Table(mei_data, colWidths=[doc.width - 2.5*cm, 2*cm])
                mei_table.setStyle(TableStyle([
                    ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('ALIGN', (0,0), (-1,0), 'CENTER'),
                    ('ALIGN', (1,1), (1,-1), 'RIGHT'),
                    ('LINEBELOW', (0,0), (-1,0), 0.5, colors.grey),
                    ('LINEABOVE', (0,-1), (-1,-1), 0.5, colors.black),
                    ('FONTNAME', (0,-1), (-1,-1), 'Helvetica-Bold'),
                    ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2),
                ]))
                story.append(mei_table)
                story.append(Spacer(1, 0.4*cm)) # Espaço antes do resumo final

            story.append(Paragraph("RESUMO FINANCEIRO", style_subheading))
            summary_final_data = [
                [Paragraph("Comissão Total (Serviços + Assinaturas):", style_table_text), Paragraph(self.format_currency(total_comissoes_gerais), style_table_text_right)],
                [Paragraph("Total Ganhos com Produtos:", style_table_text), Paragraph(self.format_currency(total_ganhos_produtos), style_table_text_right)],
                [Paragraph("Débitos de Consumo/Compra:", style_table_text), Paragraph(self.format_currency(total_debitos_consumo), style_table_text_right)], 
                [Paragraph("Descontos MEI / Outros (Dedução):", style_table_text), Paragraph(self.format_currency(total_mei_descontos), style_table_text_right)],
                [Spacer(1,0.1*cm), Spacer(1,0.1*cm)], 
                [Paragraph("<b>LÍQUIDO A RECEBER:</b>", ParagraphStyle(name='LiquidBold', parent=style_bold, fontSize=12, alignment=TA_LEFT)), 
                 Paragraph(self.format_currency(liquido_a_receber), ParagraphStyle(name='LiquidBoldRight', parent=style_bold, fontSize=12, alignment=TA_RIGHT))],
                [Spacer(1,0.2*cm), Spacer(1,0.2*cm)], 
                [Paragraph("<b>VALOR DA NOTA FISCAL A SER EMITIDA:</b>", style_total_label), Paragraph(self.format_currency(valor_nota_fiscal), style_total_value)],
            ]
            summary_col_widths = [doc.width - 3*cm, 2.5*cm] 

            summary_final_table = Table(summary_final_data, colWidths=summary_col_widths)
            summary_final_table.setStyle(TableStyle([
                ('ALIGN', (1,0), (1,-1), 'RIGHT'),
                ('LINEABOVE', (0,5), (1,5), 1.5, colors.black), 
                ('LINEBELOW', (0,5), (1,5), 1.5, colors.black),
                ('FONTNAME', (0,5), (1,5), 'Helvetica-Bold'),
                ('TEXTCOLOR', (0,5), (1,5), colors.black),
                ('FONTNAME', (0,7), (1,7), 'Helvetica-Bold'), 
                ('TOPPADDING', (0,0), (-1,-1), 2), ('BOTTOMPADDING', (0,0), (-1,-1), 2), 
                ('TOPPADDING', (0,5), (1,5), 5), ('BOTTOMPADDING', (0,5), (1,5), 5), 
                ('TOPPADDING', (0,7), (1,7), 5), ('BOTTOMPADDING', (0,7), (1,7), 5), 
            ]))
            story.append(summary_final_table)
            story.append(Spacer(1, 0.5*cm))

            story.append(Paragraph("DADOS PARA A NOTA FISCAL", style_nota_fiscal_header))
            nota_fiscal_text = f"""
            CNPJ: 24.754.181.0001/00<br/>
            INSCRIÇÃO MUNICIPAL: 92598<br/>
            E-MAIL: BARBEARIAVALDELILEMOS@HOTMAIL.COM<br/>
            NÚMERO: (21) 99914-5817<br/>
            CÓDIGO TRIBUTAÇÃO NACIONAL: 06.01.01<br/>
            ITEM DA NBS CORRESPONDENTE AO SERVIÇO PRESTADO: 1.26.02.10-00<br/><br/>
            FAVOR ENVIAR A NOTA FISCAL PARA E-MAIL: BARBEARIAVALDELILEMOS@HOTMAIL.COM<br/>
            COM O ASSUNTO: NOTA FISCAL MÊS {mes_nota_fiscal.upper()}/{ano_nota_fiscal} - {prof_name.upper()}
            """ 
            story.append(Paragraph(nota_fiscal_text, style_nota_fiscal_text))

            
            try:
                doc.build(story)
                num_recibos_gerados +=1
            except Exception as e:
                messagebox.showerror("Erro ao Salvar PDF", f"Não foi possível salvar o PDF para {prof_name}.\nErro: {e}\nVerifique o console para detalhes.", parent=self.root)
                print(f"Erro ao gerar PDF {filename}: {e}")
        
        if num_recibos_gerados > 0:
            messagebox.showinfo("Sucesso", f"{num_recibos_gerados} recibo(s) em PDF gerado(s) em:\n{output_dir}", parent=self.root)
        else:
            messagebox.showwarning("Atenção", "Nenhum recibo PDF foi gerado. Verifique os dados e se há profissionais carregados (veja o console para DEBUG CSV).", parent=self.root)

if __name__ == "__main__":
    main_root = tk.Tk()
    app = ReciboApp(main_root)
    main_root.mainloop()
