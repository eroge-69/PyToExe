import fitz  # PyMuPDF
import re
import pandas as pd
import tkinter as tk
from tkinter import filedialog

def extrair_informacoes_contracheques(caminho_pdf):
    """
    Extrai informações de contracheques de um arquivo PDF.
    """
    documento = fitz.open(caminho_pdf)
    dados_contracheques = []

    # Regex para encontrar matrícula e nome
    regex_matricula_nome = re.compile(r'\b(\d{5})\s+([A-Z\s]+)\b')

    # Regex para encontrar Salário Base, Função (cargo)
    regex_salario_funcao = re.compile(r'Salário:\s*([\d.,]+).?Função:\s([A-Z\s]+)', re.DOTALL | re.IGNORECASE)

    # Regex para encontrar Tot. Pagamentos, Tot.Descontos e Líquido
    regex_totais_liquido = re.compile(r'Tot.Pagamentos:\s*([\d.,]+)\s*Tot.Descontos:\s*([\d.,]+)\s*Líquido:\s*([\d.,]+)', re.DOTALL | re.IGNORECASE)

    # Regex para encontrar Admissão
    regex_admissao = re.compile(r'Admissão:\s*(\d{2}/\d{2}/\d{4})', re.IGNORECASE)

    # Regex para encontrar "Vale Refeição" e capturar os três valores numéricos subsequentes
    regex_vale_refeicao_tres_valores = re.compile(r'Vale Refeição(\s*[\d.,-]+)(\s*[\d.,-]+)(\s*[\d.,-]+)', re.DOTALL | re.IGNORECASE)

    for numero_pagina in range(documento.page_count):
        pagina = documento.load_page(numero_pagina)
        texto_pagina = pagina.get_text("text")

        # Encontrar todos os pares matrícula-nome na página
        encontrados_matricula_nome = list(regex_matricula_nome.finditer(texto_pagina))

        # Se nenhum funcionário for encontrado na página, pode ser uma página de resumo, pular.
        if not encontrados_matricula_nome:
            continue

        for match_matricula_nome in encontrados_matricula_nome:
            matricula = match_matricula_nome.group(1).strip()
            nome_funcionario = match_matricula_nome.group(2).strip()

            # Extrair a parte do texto que provavelmente contém as informações do contracheque
            inicio_contracheque = match_matricula_nome.start()
            fim_contracheque = len(texto_pagina)
            for next_match in encontrados_matricula_nome:
                if next_match.start() > inicio_contracheque:
                    fim_contracheque = next_match.start()
                    break
            texto_contracheque = texto_pagina[inicio_contracheque:fim_contracheque]

            salario = None
            funcao = None
            total_pagamentos = None
            total_descontos = None
            liquido = None
            admissao = None
            vale_refeicao_terceiro_valor = None

            # Buscar salário e função
            match_salario_funcao = regex_salario_funcao.search(texto_contracheque)
            if match_salario_funcao:
                salario = match_salario_funcao.group(1).strip()
                funcao = match_salario_funcao.group(2).strip()

            # Buscar totais e líquido
            match_totais_liquido = regex_totais_liquido.search(texto_contracheque)
            if match_totais_liquido:
                total_pagamentos = match_totais_liquido.group(1).strip()
                total_descontos = match_totais_liquido.group(2).strip()
                liquido = match_totais_liquido.group(3).strip()

            # Buscar Admissão
            match_admissao = regex_admissao.search(texto_contracheque)
            if match_admissao:
                admissao = match_admissao.group(1).strip()

            # Buscar Vale Refeição e os três valores subsequentes
            match_vale_refeicao_valores = regex_vale_refeicao_tres_valores.search(texto_contracheque)
            if match_vale_refeicao_valores:
                vale_refeicao_terceiro_valor = match_vale_refeicao_valores.group(3).strip()

            dados_contracheques.append({
                'Matrícula': matricula,
                'Nome do Funcionário': nome_funcionario,
                'Salário': salario,
                'Função': funcao,
                'Tot. Pagamentos': total_pagamentos,
                'Tot. Descontos': total_descontos,
                'Líquido': liquido,
                'Admissão': admissao,
                'Vale Refeição': vale_refeicao_terceiro_valor
            })

    documento.close()

    df = pd.DataFrame(dados_contracheques)

    # Realizar as correções e formatação
    cols_to_numeric = ['Tot. Pagamentos', 'Tot. Descontos', 'Líquido']
    for col in cols_to_numeric:
        df[col] = df[col].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df[col] = pd.to_numeric(df[col], errors='coerce')

    if 'Vale Refeição' in df.columns:
        df['Vale Refeição'] = df['Vale Refeição'].str.replace('-', '', regex=False).str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df['Vale Refeição'] = pd.to_numeric(df['Vale Refeição'], errors='coerce')

    if 'Função' in df.columns:
        df['Função'] = df['Função'].str.replace(r'\s*Dep\s*$', '', regex=True).str.strip()

    duplicated_mask = df.duplicated(subset='Matrícula', keep=False)
    mask_to_remove = duplicated_mask & df['Tot. Pagamentos'].isnull()
    df = df[~mask_to_remove].reset_index(drop=True)

    if 'Matrícula' in df.columns:
        df['Matrícula'] = pd.to_numeric(df['Matrícula'], errors='coerce')

    if 'Salário' in df.columns:
        df['Salário'] = df['Salário'].str.replace('.', '', regex=False).str.replace(',', '.', regex=False)
        df['Salário'] = pd.to_numeric(df['Salário'], errors='coerce')

    return df

def abrir_arquivo_pdf():
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    caminho_pdf = filedialog.askopenfilename(title="Escolha o arquivo PDF", filetypes=[("Arquivos PDF", "*.pdf")])
    return caminho_pdf

def salvar_arquivo_excel(df):
    root = tk.Tk()
    root.withdraw()  # Oculta a janela principal
    caminho_arquivo = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Arquivos Excel", "*.xlsx")])
    if caminho_arquivo:
        df.to_excel(caminho_arquivo, index=False)
        print(f"Arquivo salvo como: {caminho_arquivo}")

if __name__ == "__main__":
    caminho_pdf = abrir_arquivo_pdf()
    if caminho_pdf:
        try:
            df_contracheques = extrair_informacoes_contracheques(caminho_pdf)
            salvar_arquivo_excel(df_contracheques)
        except Exception as e:
            print(f"Ocorreu um erro: {e}")