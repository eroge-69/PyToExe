import os
from datetime import datetime, timedelta
import re

def converter_csv_para_txt(nome_arquivo_csv):
    nome_arquivo_txt = nome_arquivo_csv.replace('.csv', '.txt')
    with open(nome_arquivo_csv, encoding='ISO-8859-1') as csvfile, \
         open(nome_arquivo_txt, 'w', encoding='ISO-8859-1') as txtfile:
        for linha in csvfile:
            linha_convertida = linha.replace(';', '\t')
            txtfile.write(linha_convertida)
    return nome_arquivo_txt

def corrigir_cnae(campos):
    if len(campos) > 7:
        cnae = campos[7]
        match = re.match(r'^(\d{2})/0?(\d{1})/(\d{4})$', cnae)
        if match:
            classe, grupo, secao = match.groups()
            campos[7] = f"{secao}-{grupo}/{classe}"
    return campos

def corrigir_estabelecimento(campos):
    if len(campos) > 5:
        campos[5] = campos[5].replace('\t', '.')
    return campos


def corrigir_estabelecimento_csv(campos):
    if len(campos) > 6:
        i = 6
        while i < len(campos):
            if re.fullmatch(r'\d+', campos[i]):
                break
            campos[5] += f".{campos[i]}"
            del campos[i]
    return campos


# Nome do novo arquivo:
data_amanha = (datetime.now() + timedelta(days=1)).strftime('%Y%m%d')
nome_arquivo_saida = f"cadastro_de_empregadores{data_amanha}.txt"

# Registros errados:
nomes_excluir = {"DALVA MARIA SIMONATO", "ELZO SIMONATO"}

# Arquivos para processar:
arquivos_para_processar = []
for nome_arquivo in os.listdir('.'):
    if nome_arquivo.lower().endswith('.csv'):
        nome_convertido = converter_csv_para_txt(nome_arquivo)
        arquivos_para_processar.append(nome_convertido)
    elif nome_arquivo.lower().endswith('.txt') and nome_arquivo != nome_arquivo_saida:
        arquivos_para_processar.append(nome_arquivo)

# Processamento dos arquivos:
for nome_arquivo in arquivos_para_processar:
    with open(nome_arquivo, encoding='ISO-8859-1') as arquivo:
        with open(nome_arquivo_saida, 'a', encoding='ISO-8859-1') as txtfile:
            for linha in arquivo:
                campos = linha.strip().split('\t')

                # Ignora linhas com menos de 10 colunas
                if len(campos) < 10:
                    continue

                # Tira aspas duplas, espaços excessivos e troca ";" por TAB
                campos = [
                    re.sub(r' {2,}', '', campo.replace('"', '').replace(';', '\t'))
                    for campo in campos
                ]

                # Exclui registros errados
                linha_completa = '\t'.join(campos).upper()
                if any(nome in linha_completa for nome in nomes_excluir):
                    continue

                campos = corrigir_estabelecimento_csv(campos)
                campos = corrigir_estabelecimento(campos)

                campos = corrigir_cnae(campos)

                txtfile.write('\t'.join(campos) + '\n')

# Registros corrigidos:
linhas_adicionais = [
    "152\t2023\tPR\tDALVA MARIA SIMONATO\t02572413965\tPR 281 KM 618 S N COXILHA ALTA PLANALTO PR\t1\t4619-2/00\t29/09/2023\t29/09/2023",
    "213\t2023\tPR\tELZO SIMONATO\t84906213000177\tPR 281 KM 618 S N COXILHA ALTA PLANALTO PR\t1\t4619-2/00\t29/09/2023\t29/09/2023",
    "214\t2023\tPR\tELZO SIMONATO\t33329125934\tPR 281 KM 618 S N COXILHA ALTA PLANALTO PR\t1\t4619-2/00\t29/09/2023\t29/09/2023"
]
with open(nome_arquivo_saida, 'a', encoding='ISO-8859-1') as txtfile:
    for linha in linhas_adicionais:
        txtfile.write(linha + '\n')
