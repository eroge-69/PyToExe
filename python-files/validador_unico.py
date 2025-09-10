import pandas as pd
from PyPDF2 import PdfReader
import re
import sys
import locale
import os
import requests
from dateutil.parser import parse
import pdfplumber
from rapidfuzz import fuzz
from datetime import datetime
import contextlib
import numpy as np
from extract_msg import Message
from bs4 import BeautifulSoup
from io import StringIO

sys.stdin.reconfigure(encoding='utf-8')
locale.setlocale(locale.LC_ALL, 'pt_BR.UTF-8')


# Tentando adicionar novo formato
# regex_data = r'\d{2}\s*[./-]\s*\d{2}\s*[./-]\s*\d{2,4}, \d{2}\d{2}2025\b, \d{2}\d{2}2024\b, \d{2}\d{2}2026\b'
regex_data = r'\d{2}\s*[./]\s*\d{2}\s*[./]\s*\d{2,4}|\d{2}\s*[-]\s*\d{2}\s*[-]\s*\d{2,4}|\d{2}\d{2}2025\b|\d{2}\d{2}2026\b|\d{2}\d{2}2024\b|\d{2}\d{2}2027\b|\d{2}\d{2}2028\b|\d{2}\d{2}2029\b|\d{2}\d{2}2030\b'

# testes
regex_valor = r'R?\$?\s?(?:\d{1,3}(?:\.\d{3})+|\d+),\d{2}|\d+\.\d{2}(?=\s|$)'

@contextlib.contextmanager
def suppress_stderr():
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr

def treat_text_encode(text):
    return text.replace('\xa0', ' ')

def treat_data_encode(df):
    df.columns = df.columns.map(treat_text_encode)
    df.columns = df.columns.str.strip()

    for col in df.columns:
        try:
            df[col] = df[col].map(treat_text_encode)
            df[col] = df[col].str.strip()
        except:
            pass

    return df

def normalizar_valor(valor):
    valor = valor.replace("R$", "").replace("R", "").replace("$", "").replace(" ", "").strip()

    if ',' in valor and '.' in valor:
        # Ex: 1.234,56 → 1234.56
        valor = valor.replace('.', '').replace(',', '.')
    elif ',' in valor:
        # Ex: 1234,56 → 1234.56
        valor = valor.replace(',', '.')
    # se tiver só ponto → já é padrão americano
    return round(float(valor), 2)

def normalizar_data(data_str):
    # Remove espaços ao redor dos separadores e espaços extras
    data_str = re.sub(r'\s*([./-])\s*', r'\1', data_str.strip())

    # Tenta os formatos incluindo os com ano de 2 dígitos
    formatos_possiveis = ["%d/%m/%Y", "%d.%m.%Y", "%d/%m/%y", "%d.%m.%y", "%Y-%m-%d", "%Y/%m/%d", "%d-%m-%Y", "%d%m%Y"]

    for formato in formatos_possiveis:
        try:
            data = datetime.strptime(data_str, formato)
            # Corrige anos com 2 dígitos, como 25 para 2025
            if data.year < 100:
                data = data.replace(year=data.year + 2000)
            return data.strftime("%d/%m/%Y")
        except ValueError:
            continue

    return data_str

def isSubstring(Sub, Text):
    return Text.contains(Sub)

def search_file_by_subname(path, subtext, numtext):
    resultados = []
    for item in os.listdir(path):
        caminho_completo = os.path.join(path, item)
        if os.path.isfile(caminho_completo):
            if len(caminho_completo.split("\\")[-1]) >= 25:
                if item.lower().endswith(('.pdf', '.msg')) and subtext.lower() in item.lower() and numtext in item.lower():
                    resultados.append(caminho_completo)
            elif item.lower().endswith(('.pdf', '.msg')) and subtext.lower() in item.lower():
                resultados.append(caminho_completo)
            else:
                pass

    return resultados

def extrair_pares_msg(caminho_msg):
    pares_data_valor = []

    msg = Message(caminho_msg)
    html_content = msg.htmlBody
    # html_io = StringIO(html_content)
    # print(msg.htmlBody)
    soup = BeautifulSoup(html_content, 'html.parser')
    # print(soup)
    tables = soup.find_all('table')

    extracted_tables = []

    try:
        for i, table in enumerate(tables):
            html_io = StringIO(str(table))
            # df = pd.read_html(str(table))[0]
            df = pd.read_html(html_io, header=0)[0]
            extracted_tables.append(df)

        for tabela_datas_valores in extracted_tables:
            if "Valor" in tabela_datas_valores.columns:
                for i in tabela_datas_valores.index:
                    try:
                        data, valor = str(normalizar_data(tabela_datas_valores.loc[i,"Vencimento"])), str(normalizar_valor(tabela_datas_valores.loc[i,"Valor"]))
                        pares_data_valor.append(data + " " + valor)
                    except:
                        pass
            else:
                datas = []
                for i, col in enumerate(tabela_datas_valores.columns):
                    for match in re.finditer(regex_data, col):
                        data = match.group()
                        datas.append((data, i))

                for data, n_col in datas:
                    for val in tabela_datas_valores.iloc[:,n_col]:
                        try:
                            pares_data_valor.append(str(normalizar_data(data)) + " " + str(normalizar_valor(val)))
                        except:
                            pass
            
    except:
        pass

    # Encontra todos os parágrafos que podem conter os dados
    # paragraphs = soup.find_all('p', class_='MsoNormal')
    htmls = soup.find_all('html')
    spans = soup.find_all('span')
    # print(spans[0].get_text())

    # Extrai todos os textos dos spans
    if spans != []:
        partes = [span.get_text(strip=True) for span in spans]
    else:
        pass
        partes = [str(html).replace("<br/><br/>", " ") for html in htmls]
        # partes = [(parte.get_text(strip=True)) for parte in primeira_parte]
    

    texto = ' '.join(partes)
    
    # Padrão regex para capturar data e valor mesmo quando separados
    padrao = r'(\d{1,2}[./]\d{1,2}[./]\d{2,4})\s*[:–-]\s*R\$\s*([\d.,]+)'
    matches = re.finditer(padrao, texto)
    
    for match in matches:
        data = match.group(1)
        valor = match.group(2)
        try:
            par_normalizado = f"{normalizar_data(data)} {normalizar_valor(valor)}"
            pares_data_valor.append(par_normalizado)
        except:
            pass

    return pares_data_valor

def extrair_pares_pdf(caminho_pdf):
    pares_data_valor = []

    with pdfplumber.open(caminho_pdf) as pdf:
        for pagina in pdf.pages:
            linhas = pagina.extract_text().split('\n')

            datas = []
            valores = []
            flag_valor_antes = 0

            for i, linha in enumerate(linhas):
                if ("Valor Vencimento" in linha) or ("001 R$" in linha) or ("TOTAL A PAGAR" in linha) or ("DATA VENCTO C/D DATA VENCTO S/D DUPLICATA" in linha):
                    flag_valor_antes = 1
                # print(re.fullmatch(regex_data, linha))
                # for teste in re.fullmatch(regex_data, linha):
                #     print(teste)
                for match in re.finditer(regex_data, linha):
                    data = match.group()
                    posicao_na_linha = match.start()  # Posição do início da data na linha
                    datas.append((data, i, posicao_na_linha))
                
                # Para valores
                for match in re.finditer(regex_valor, linha):
                    valor = match.group()
                    posicao_na_linha = match.start()  # Posição do início do valor na linha
                    valores.append((normalizar_valor(valor), i, posicao_na_linha))

            posicoes_extras = 0
            flag_posicoes_extras = 0

            # Emparelha data com valor mais próximo na linha
            for data, linha_data, posicao_na_linha in datas:
                # if data in ["20/05/2025", "30/05/2025", "15/06/2025"]:
                #     print(data, " ", linha_data, " ", posicao_na_linha, "\n")
                if flag_valor_antes == 0:
                    posicao_mais_proxima = np.inf
                else:
                    posicao_mais_proxima = -100
                valor_mais_proximo = ()
                # valores_mais_proximos = []
                for valor in [val for val in valores if (val[0] > 0)]:
                    # if data in ["20/05/2025", "30/05/2025", "15/06/2025"]:
                    #     print(valor)
                    #     print(linha_data == valor[1])
                    # Se o valor estiver na mesma linha que a data, adiciona ao par
                    if flag_valor_antes == 0:
                        if (linha_data == valor[1]) and (valor[2] > posicao_na_linha):
                            if valor[2] < posicao_mais_proxima:
                                valor_mais_proximo = valor
                                posicao_mais_proxima = valor[2]
                    else:
                        if (linha_data == valor[1]) and (valor[2] < posicao_na_linha):
                            if valor[2] > posicao_mais_proxima:
                                valor_mais_proximo = valor
                                posicao_mais_proxima = valor[2]
                
                if valor_mais_proximo != ():
                    pares_data_valor.append(str(normalizar_data(data)) + " " + str(valor_mais_proximo[0]))

                else:
                    # posicao_na_linha = posicao_na_linha - posicoes_extras
                    # print(posicao_na_linha, linha_data, data)
                    valores_nas_linhas_proximas = [val for val in valores if (val[0] > 0) and (abs(val[1] - linha_data) <= 1) and (val[1] != linha_data)]
                    # coluna_mais_esquerda = np.min([val[2] for val in valores_nas_linhas_proximas])
                    if flag_posicoes_extras == 0:
                        if valores_nas_linhas_proximas != []:
                            posicoes_extras = posicao_na_linha- np.min([int(val[2]) for val in valores_nas_linhas_proximas])
                            flag_posicoes_extras = 1
                            
                    # print(posicoes_extras)
                    posicao_na_linha = posicao_na_linha - posicoes_extras
                    # print(coluna_mais_esquerda-posicao_na_linha)
                    valor_mais_proximo = min(
                        [val for val in valores if (val[0] > 0) and (abs(val[1] - linha_data) <= 2) and (val[1] != linha_data)],
                        key=lambda x: np.sqrt(pow(x[1] - linha_data, 2) + pow(x[2] - posicao_na_linha, 2)),
                        # key=lambda x: abs(x[1] - linha_data),
                        default=(None, None)
                    )
                    # if data == "30/04/2025":
                    #     print(valor_mais_proximo)
                    if valor_mais_proximo[0]:
                        pares_data_valor.append(str(normalizar_data(data)) + " " + str(valor_mais_proximo[0]))
                        # print(valor_mais_proximo)

    return pares_data_valor


def extrai_valores_coluna(caminho_arquivo):
    with suppress_stderr():
        try:
            if caminho_arquivo.lower().endswith('pdf'):
                datas_valores_extraidos = extrair_pares_pdf(caminho_arquivo)
            else:
                datas_valores_extraidos = extrair_pares_msg(caminho_arquivo)
        except:
            datas_valores_extraidos = []
    
    return datas_valores_extraidos

def retorna_notas_verificadas(caminho_tabela_valores = r".\Data\registros_nfs_atual_lote_4.xlsx", 
                              diretorio_arquivos = r".\Data\1900618861-D",
                              nome_arquivo_final = r".\Data\resultados_validacao.xlsx"):

    registros = pd.read_excel(caminho_tabela_valores)
    registros.columns = ['Itm', 'Texto', 'Atribuicao', 'No_doc.', 'Data pgto.', 'Mont.em MI', 
                     'MP', 'BlP', 'DocCompens', 'Fornecedor', 'Empr']
    registros = treat_data_encode(registros)
    registros["Data pgto."] = registros["Data pgto."].str.replace('.', '/')
    registros["Mont.em MI"] = registros["Mont.em MI"].str.rstrip('-')
    registros["Mont.em MI"] = [str(normalizar_valor(val)) for val in registros["Mont.em MI"]]
    registros["Data_valor"] = registros["Data pgto."] + " " + registros["Mont.em MI"]

    registros_grupos = registros.groupby(['Atribuicao', 'Fornecedor']).agg(list).copy()
    registros_grupos.head()

    pdf_encontrados = {}
    for index, row in registros_grupos.iterrows():
        numtext = row['Texto'][0].split(" ")[1].split("-")[-1]
        try:
            pdf_encontrados[index] = search_file_by_subname(diretorio_arquivos, index[1], numtext)
        except:
            pdf_encontrados[index] = []
            pass

    df = pd.DataFrame.from_dict(pdf_encontrados, orient= "index").reset_index()

    search = df.copy()
    achado = pd.DataFrame(columns=['Data_valor', 'validado'])

    for ind in search.index:
        indice = search.loc[ind]["index"]
        data_valor_lista = registros_grupos.loc[indice]["Data_valor"]
        datas_valores_extraidos = []

        # for colunas in [search.loc[ind][0], search.loc[ind][1]]:
        #     datas_valores_extraidos.extend(extrai_valores_coluna(colunas))

        for coluna in [search.loc[ind][name_col] for name_col in search.columns[1:]]:
            datas_valores_extraidos.extend(extrai_valores_coluna(coluna))

        for dat in data_valor_lista:
            indice_data = str(indice)+ " - " + str(dat)
            validado = dat in datas_valores_extraidos
            if indice_data not in achado.index:
                achado.loc[indice_data] = [dat, validado]
            else:
                if validado == True:
                    # Atualiza o campo 'validado' se a data já existe
                    achado.loc[indice_data, 'validado'] = validado

    achado["Atribuicao"] = achado.index.map(lambda x: x.split(" - ")[0].replace("'", "").replace("(", "").replace(")", "").split(", ")[0])
    achado["Fornecedor"] = achado.index.map(lambda x: x.split(" - ")[0].replace("'", "").replace("(", "").replace(")", "").split(", ")[1])

    resultados_validacao = registros.copy()

    resultados_validacao = resultados_validacao.merge(
        achado[['Atribuicao', 'Fornecedor', 'Data_valor', 'validado']],
        left_on=['Atribuicao', 'Fornecedor', 'Data_valor'],
        right_on=['Atribuicao', 'Fornecedor', 'Data_valor'],
        how='left'
    )

    df["Atribuicao"] = df["index"].map(lambda x: x[0])
    df["Fornecedor"] = df["index"].map(lambda x: x[1])

    resultados_validacao = resultados_validacao.merge(
        df[['Atribuicao', 'Fornecedor'] + df.columns.tolist()[1:-2]],
        left_on=['Atribuicao', 'Fornecedor'],
        right_on=['Atribuicao', 'Fornecedor'],
        how='left'
    )

    resultados_validacao.to_excel(nome_arquivo_final, index=False)
    
    return resultados_validacao

import plyer
from plyer import filechooser
from pathlib import Path
import os

def selecionar_arquivo_excel():
    """Seleciona um arquivo Excel"""
    print("Selecione o arquivo Excel...")
    arquivo = filechooser.open_file(
        title="Selecione o arquivo Excel com os items das NFS",
        filters=[("Arquivos Excel", "*.xlsx;*.xls")],
        multiple=False
    )
    return arquivo[0] if arquivo else None

def selecionar_diretorio_leitura():
    """Seleciona diretório para leitura"""
    print("Selecione o diretório de leitura...")
    diretorio = filechooser.choose_dir(
        title="Selecione o diretório dos PDFS e e-mails"
    )
    return diretorio

def selecionar_diretorio_salvamento():
    """Seleciona diretório para salvamento"""
    print("Selecione o diretório para salvar o resultado...")
    diretorio = filechooser.choose_dir(
        title="Selecione o diretório para salvar o resultado"
    )
    return diretorio

def main():
    try:
        # 1) Selecionar arquivo Excel
        arquivo_excel = selecionar_arquivo_excel()
        if not arquivo_excel:
            print("Nenhum arquivo Excel selecionado. Operação cancelada.")
            return
        
        print(f"Arquivo selecionado: {arquivo_excel}")
        
        # 2) Selecionar diretório de leitura
        dir_leitura = selecionar_diretorio_leitura()
        if not dir_leitura:
            print("Nenhum diretório de leitura selecionado. Operação cancelada.")
            return
        
        print(f"Diretório de leitura: {dir_leitura}")
        
        # 3) Selecionar diretório de salvamento
        dir_salvamento = selecionar_diretorio_salvamento()
        if not dir_salvamento:
            print("Nenhum diretório de salvamento selecionado. Operação cancelada.")
            return
        
        print(f"Diretório de salvamento: {dir_salvamento}")
        
        # Aqui você pode adicionar o processamento do seu script
        print("\n✅ Seleção concluída! Aguarde o processamento...")
        
        # Exemplo de como ler o Excel (descomente se necessário)
        # df = pd.read_excel(arquivo_excel)
        # print(f"Planilha carregada com {len(df)} linhas")
        
        return {
            'arquivo_entrada': arquivo_excel,
            'dir_leitura': dir_leitura[0],
            'dir_salvamento': dir_salvamento[0]
        }
        
    except Exception as e:
        print(f"Erro durante a seleção: {e}")
        return None

from interface import *
from extrai_informacoes_arquivos import *

if __name__ == "__main__":
    parametros = main()
    nome_arquivo = "RESULTADOS_" + parametros['arquivo_entrada'].split("\\")[-1]
    arquivo_resultado = parametros['dir_salvamento'] + "\\" + nome_arquivo
    resultados = retorna_notas_verificadas(caminho_tabela_valores = parametros['arquivo_entrada'], 
                                       diretorio_arquivos = parametros['dir_leitura'],
                                       nome_arquivo_final=arquivo_resultado)

    print("FIM DO PROCESSAMENTO\nQuantidade de itens não validados: ", resultados[resultados["validado"] == False].shape[0])