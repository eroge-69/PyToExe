import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import pandas as pd
import os
import unicodedata
from datetime import datetime


colunas = [
    "TIPO SERV.", "CAD. NOVO", "CAD. UNICO", "CAD UNICO NOVO",
    "CAD. ATUAL.", "ESCOLARID.", "CARTAS ENC."
]


resumo_labels = [
    "CAD ATUAL:",
    "CAD ÚNICO NOVO:",
    "CAD ÚNICO:",
    "CAD NOVO:",
    "CARTAS ENC.:",
    "TIPO SERV. (IMO):",
    "TIPO SERV. (SD):",
    "ATENDIMENTO TOTAL:",
    "FUNDAMENTAL INCOMPLETO:",
    "FUNDAMENTAL COMPLETO:",
    "MÉDIO INCOMPLETO:",
    "MÉDIO COMPLETO:",
    "SUPERIOR INCOMPLETO:",
    "SUPERIOR COMPLETO:"
]


def normaliza_sim_nao(valor):
    if not valor or str(valor).strip() == "":
        return 0
    val = str(valor).strip().upper()
    val = unicodedata.normalize("NFKD", val).encode("ASCII", "ignore").decode("ASCII")
    return 1 if val in ("SIM", "S") else 0


def importar_dados():
    texto = campo_texto.get("1.0", tk.END).strip()
    linhas = texto.split("\n")
    for linha in linhas:
        dados = linha.split("\t")
        if len(dados) >= len(colunas):
            tabela.insert("", "end", values=dados[:len(colunas)])
        else:
            dados += [""] * (len(colunas) - len(dados))
            tabela.insert("", "end", values=dados)
    salvar_automatico()
    atualizar_estado_botao_salvar()
    calcular_totais_editar()


def adicionar_linha_manual():
    def salvar_linha():
        valores = [entrada.get() for entrada in entradas]
        tabela.insert("", "end", values=valores)
        salvar_automatico()
        atualizar_estado_botao_salvar()
        calcular_totais_editar()
        janela_popup.destroy()
    janela_popup = tk.Toplevel(janela)
    janela_popup.title("Inserir dados manualmente")
    entradas = []
    for i, campo in enumerate(colunas):
        tk.Label(janela_popup, text=campo).grid(row=i, column=0, sticky="e", padx=5, pady=2)
        entrada = tk.Entry(janela_popup, width=40)
        entrada.grid(row=i, column=1, padx=5, pady=2)
        entradas.append(entrada)
    btn_salvar_linha = tk.Button(janela_popup, text="Salvar", command=salvar_linha)
    btn_salvar_linha.grid(row=len(colunas), column=0, columnspan=2, pady=10)


def salvar_automatico():
    dados = [tabela.item(item)["values"] for item in tabela.get_children()]
    df = pd.DataFrame(dados, columns=colunas)
    df.to_excel("cadastro_automatico.xlsx", index=False)


def carregar_arquivo():
    arquivo = filedialog.askopenfilename(filetypes=[("Excel files", "*.xlsx")], title="Carregar Dados")
    if arquivo:
        try:
            df = pd.read_excel(arquivo)
            # Remover colunas antigas desnecessárias, se existirem
            colunas_antigas = ["Nº", "DATA", "USUÁRIO", "CPF"]
            df = df.drop(columns=colunas_antigas, errors="ignore")
            for _, row in df.iterrows():
                tabela.insert("", "end", values=row.tolist())
            salvar_automatico()
            atualizar_estado_botao_salvar()
            calcular_totais_editar()
            messagebox.showinfo("Sucesso", "Dados carregados com sucesso!")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar o arquivo:\n{e}")


def carregar_automaticamente():
    if os.path.exists("cadastro_automatico.xlsx"):
        try:
            df = pd.read_excel("cadastro_automatico.xlsx")
            # Remover colunas antigas desnecessárias
            colunas_antigas = ["Nº", "DATA", "USUÁRIO", "CPF"]
            df = df.drop(columns=colunas_antigas, errors="ignore")
            for _, row in df.iterrows():
                tabela.insert("", "end", values=row.tolist())
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao carregar dados salvos:\n{e}")
    atualizar_estado_botao_salvar()
    calcular_totais_editar()


def atualizar_estado_botao_salvar():
    btn_salvar.config(state="normal" if len(tabela.get_children()) > 0 else "disabled")
    btn_limpar.config(state="normal" if len(tabela.get_children()) > 0 else "disabled")


def calcular_totais_editar():
    cad_atual = cad_unico_novo = cad_unico = cad_novo = 0
    cartas_enc_sim = 0
    imo_total = sd_total = 0
    escolaridades = {
        "FUNDAMENTAL INCOMPLETO": 0,
        "FUNDAMENTAL COMPLETO": 0,
        "MÉDIO INCOMPLETO": 0,
        "MÉDIO COMPLETO": 0,
        "SUPERIOR INCOMPLETO": 0,
        "SUPERIOR COMPLETO": 0
    }
    for item in tabela.get_children():
        valores = tabela.item(item)["values"]
        if len(valores) < len(colunas):
            continue
        if normaliza_sim_nao(valores[4]) == 1: cad_atual += 1
        if normaliza_sim_nao(valores[3]) == 1: cad_unico_novo += 1
        if normaliza_sim_nao(valores[2]) == 1: cad_unico += 1
        if normaliza_sim_nao(valores[1]) == 1: cad_novo += 1
        if normaliza_sim_nao(valores[6]) == 1: cartas_enc_sim += 1
        tserv = str(valores[0]).strip().upper()
        if tserv == "IMO": imo_total += 1
        elif tserv == "SD": sd_total += 1
        esc = str(valores[5]).strip().upper()
        if "FUND. INCOMPLETO" in esc or "FUNDAMENTAL INCOMPLETO" in esc:
            escolaridades["FUNDAMENTAL INCOMPLETO"] += 1
        elif "FUND. COMPLETO" in esc or "FUNDAMENTAL COMPLETO" in esc:
            escolaridades["FUNDAMENTAL COMPLETO"] += 1
        elif "MEDIO INCOMPLETO" in esc:
            escolaridades["MÉDIO INCOMPLETO"] += 1
        elif "MEDIO COMPLETO" in esc:
            escolaridades["MÉDIO COMPLETO"] += 1
        elif "SUP. INCOMPLETO" in esc or "SUPERIOR INCOMPLETO" in esc:
            escolaridades["SUPERIOR INCOMPLETO"] += 1
        elif "SUP. COMPLETO" in esc or "SUPERIOR COMPLETO" in esc:
            escolaridades["SUPERIOR COMPLETO"] += 1
    total_imo_sd = imo_total + sd_total
    data = [
        str(cad_atual),
        str(cad_unico_novo),
        str(cad_unico),
        str(cad_novo),
        str(cartas_enc_sim),
        str(imo_total),
        str(sd_total),
        str(total_imo_sd),
        str(escolaridades["FUNDAMENTAL INCOMPLETO"]),
        str(escolaridades["FUNDAMENTAL COMPLETO"]),
        str(escolaridades["MÉDIO INCOMPLETO"]),
        str(escolaridades["MÉDIO COMPLETO"]),
        str(escolaridades["SUPERIOR INCOMPLETO"]),
        str(escolaridades["SUPERIOR COMPLETO"])
    ]
    for i, en in enumerate(edits_resumo):
        en.delete(0, "end")
        en.insert(0, data[i])


def salvar_resumo_profissional():
    output = []
    output.append(["", ""])
    output.append(["", ""])
    for label, ent in zip(resumo_labels, edits_resumo):
        output.append([label, ent.get()])
    df = pd.DataFrame(output, columns=["Campo", "Total"])
    arq = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel", "*.xlsx")], title="Salvar resumo profissional")
    if not arq:
        return
    with pd.ExcelWriter(arq, engine="openpyxl") as writer:
        df.to_excel(writer, index=False, header=False, sheet_name="Resumo")
        ws = writer.sheets["Resumo"]
        from openpyxl.styles import Font, Alignment
        for row in ws.iter_rows(min_row=1, max_row=len(df.index)+1, min_col=1, max_col=2):
            for cell in row:
                cell.font = Font(name="Arial", size=14, bold=True)
                cell.alignment = Alignment(horizontal="left", vertical="center")
        ws.column_dimensions["A"].width = 36
        ws.column_dimensions["B"].width = 16
    messagebox.showinfo("Resumo salvo", "Resumo editável salvo em:\n" + arq)


def limpar_tudo():
    senha = simpledialog.askstring("Confirmação", "Digite a senha para limpar (111):", show="*")
    if senha != "111":
        messagebox.showwarning("Senha Incorreta", "Senha incorreta! Operação cancelada.")
        return
    for item in tabela.get_children():
        tabela.delete(item)
    campo_texto.delete("1.0", tk.END)
    atualizar_estado_botao_salvar()
    calcular_totais_editar()


def deletar_linha_selecionada():
    selecionadas = tabela.selection()
    if not selecionadas:
        messagebox.showwarning("Nenhuma Seleção", "Nenhuma linha selecionada para deletar.")
        return
    confirm = messagebox.askyesno("Confirmação", f"Deseja deletar {len(selecionadas)} linha(s) selecionada(s)?")
    if confirm:
        for item in selecionadas:
            tabela.delete(item)
        salvar_automatico()
        atualizar_estado_botao_salvar()
        calcular_totais_editar()
        messagebox.showinfo("Sucesso", "Linha(s) deletada(s) com sucesso.")


def criar_backup():
    dados = [tabela.item(item)["values"] for item in tabela.get_children()]
    if not dados:
        messagebox.showwarning("Aviso", "Nenhum dado para fazer backup!")
        return
    data_hora = datetime.now().strftime("%Y%m%d_%H%M%S")
    nome_sugerido = f"backup_cadastro_{data_hora}.xlsx"
    arquivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel files", "*.xlsx")], 
                                          title="Salvar Backup", initialfile=nome_sugerido)
    if arquivo:
        try:
            df = pd.DataFrame(dados, columns=colunas)
            df.to_excel(arquivo, index=False)
            messagebox.showinfo("Sucesso", f"Backup salvo em:\n{arquivo}")
        except PermissionError:
            messagebox.showerror("Erro", "Permissão negada. Verifique se você tem acesso para salvar neste local.")
        except Exception as e:
            messagebox.showerror("Erro", f"Erro ao criar backup:\n{e}")


def editar_celula(event):
    item = tabela.identify_row(event.y)
    column = tabela.identify_column(event.x)
    if not item or not column:
        return
    col_index = int(column.replace("#", "")) - 1
    bbox = tabela.bbox(item, column)
    if not bbox:
        return
    entry_edit = tk.Entry(frame_tabela, font=("Segoe UI", 12))
    entry_edit.place(x=bbox[0], y=bbox[1], width=bbox[2], height=bbox[3])
    current_value = tabela.item(item, "values")[col_index]
    entry_edit.insert(0, current_value)
    entry_edit.select_range(0, tk.END)
    entry_edit.focus()
    def salvar_edicao(e=None):
        new_value = entry_edit.get()
        values = list(tabela.item(item, "values"))
        values[col_index] = new_value
        tabela.item(item, values=values)
        salvar_automatico()
        calcular_totais_editar()
        entry_edit.destroy()
    entry_edit.bind("<Return>", salvar_edicao)
    entry_edit.bind("<FocusOut>", salvar_edicao)


def criar_menu_contexto(event):
    item = tabela.identify_row(event.y)
    if item:
        tabela.selection_set(item)
        menu_contexto.post(event.x_root, event.y_root)


janela = tk.Tk()
janela.title("Cadastro e Cálculo Final")
janela.state('zoomed')


frame_tabela = tk.Frame(janela)
frame_tabela.pack(fill="both", expand=True, padx=8, pady=(8, 2))


scroll_y = ttk.Scrollbar(frame_tabela, orient="vertical")
scroll_y.pack(side="right", fill="y")
tabela = ttk.Treeview(frame_tabela, columns=colunas, show="headings", yscrollcommand=scroll_y.set)
scroll_y.config(command=tabela.yview)
style = ttk.Style()
style.configure("Treeview.Heading", font=("Segoe UI", 12, "bold"))
style.configure("Treeview", font=("Segoe UI", 12), rowheight=25)
for col in colunas:
    tabela.heading(col, text=col)
    tabela.column(col, width=120, anchor="w")
tabela.pack(fill="both", expand=True)
tabela.bind("<Double-1>", editar_celula)


menu_contexto = tk.Menu(janela, tearoff=0)
menu_contexto.add_command(label="Excluir Linha", command=deletar_linha_selecionada)
tabela.bind("<Button-3>", criar_menu_contexto)


def deletar_com_tecla(event):
    deletar_linha_selecionada()
tabela.bind("<Delete>", deletar_com_tecla)


campo_texto = tk.Text(janela, height=6, font=("Segoe UI", 12), bg="#f8f8fa", relief="groove")
campo_texto.pack(pady=8, fill="x", padx=10)


frame_botoes = tk.Frame(janela, bg="#f0f2f6")
frame_botoes.pack(pady=4)
btn_importar = tk.Button(frame_botoes, text="Importar Texto", command=importar_dados, font=("Segoe UI", 12),
                         width=16, bg="#2494e6", fg='white', activebackground="#1979b2")
btn_importar.grid(row=0, column=0, padx=5)
btn_add = tk.Button(frame_botoes, text="Adicionar Linha Manual", command=adicionar_linha_manual, font=("Segoe UI", 12),
                    width=18, bg="#38c172", fg='white', activebackground="#268146")
btn_add.grid(row=0, column=1, padx=5)
btn_carregar = tk.Button(frame_botoes, text="Carregar", command=carregar_arquivo, font=("Segoe UI", 12),
                         width=16, bg="#ff9800", fg='white', activebackground="#f57c00")
btn_carregar.grid(row=0, column=2, padx=5)
btn_atualizar = tk.Button(frame_botoes, text="Atualizar Dados", command=calcular_totais_editar, font=("Segoe UI", 12),
                          width=16, bg="#4caf50", fg='white', activebackground="#388e3c")
btn_atualizar.grid(row=0, column=3, padx=5)
btn_backup = tk.Button(frame_botoes, text="Backup", command=criar_backup, font=("Segoe UI", 12),
                       width=16, bg="#9c27b0", fg='white', activebackground="#7b1fa2")
btn_backup.grid(row=0, column=4, padx=5)
btn_deletar_selecionadas = tk.Button(frame_botoes, text="Deletar Selecionadas", command=deletar_linha_selecionada, font=("Segoe UI", 12),
                                     width=18, bg="#f55753", fg='white', activebackground="#b82d29")
btn_deletar_selecionadas.grid(row=0, column=5, padx=5)
btn_salvar = tk.Button(frame_botoes, text="Salvar Resumo (Excel)", command=salvar_resumo_profissional,
                       font=("Segoe UI", 12), width=22, bg="#574b90", fg='white', activebackground="#3d3570", state="normal")
btn_salvar.grid(row=0, column=6, padx=5)
btn_limpar = tk.Button(frame_botoes, text="Limpar Dados", command=limpar_tudo,
                       font=("Segoe UI", 12), width=15, bg="#f55753", fg="white", activebackground="#b82d29", state="normal")
btn_limpar.grid(row=0, column=7, padx=5)


frame_resumo_externo = tk.Frame(janela, bg="#f0f2f6")
frame_resumo_externo.pack(pady=10, fill="both", expand=True, padx=30)


canvas = tk.Canvas(frame_resumo_externo, bg="#f4f4fa", highlightthickness=0)
scrollbar_resumo = ttk.Scrollbar(frame_resumo_externo, orient="vertical", command=canvas.yview)
scrollbar_resumo.pack(side="right", fill="y")
canvas.pack(side="left", fill="both", expand=True)
canvas.configure(yscrollcommand=scrollbar_resumo.set)


frame_resumo = tk.Frame(canvas, bg="#f4f4fa", bd=2, relief="solid", padx=44, pady=16)
canvas.create_window((0,0), window=frame_resumo, anchor="nw")


def on_frame_resumo_configure(event):
    canvas.configure(scrollregion=canvas.bbox("all"))
frame_resumo.bind("<Configure>", on_frame_resumo_configure)


edits_resumo = []
for _ in range(2):
    tk.Label(frame_resumo, text="", bg="#f4f4fa", font=("Arial",12)).pack()
for i, label in enumerate(resumo_labels):
    frame_linha = tk.Frame(frame_resumo, bg="#f4f4fa")
    frame_linha.pack(fill="x")
    labelw = 35
    tk.Label(frame_linha, text=label, font=("Arial", 14, "bold"), fg="#222", bg="#f4f4fa", width=labelw, anchor="w").pack(side="left", padx=(0,5))
    entry = tk.Entry(frame_linha, font=("Arial", 14), width=8, justify="right", bg="#f7fcfc")
    entry.pack(side="left")
    edits_resumo.append(entry)


carregar_automaticamente()
janela.after(300, calcular_totais_editar)
janela.mainloop()
