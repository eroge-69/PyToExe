import pandas as pd
import os
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET
from xml.dom import minidom
from datetime import datetime, timedelta, time
from html import unescape
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from tkinter.scrolledtext import ScrolledText  


# var_botton = 0
# diretorio_relatorios_botton = r'.\Relatórios'
# from tkinter import messagebox, filedialog
# arquivos_xlsx_botton = [arquivo for arquivo in os.listdir(diretorio_relatorios_botton) if arquivo.endswith('.xlsx')]

# def excluir_arquivos_xlsx():
    
#     arquivos_xlsx_botton = [arquivo for arquivo in os.listdir(diretorio_relatorios_botton) if arquivo.endswith('.xlsx')]


#     # Verificar se o diretório existe
#     if os.path.exists(diretorio_relatorios_botton):
#         # Listar arquivos .xlsx no diretório
       

#         # Verificar se há arquivos para excluir
#         if arquivos_xlsx_botton:
#             # Perguntar ao usuário se deseja manter os arquivos
#             resposta = messagebox.askquestion("Confirmação", "Deseja manter os arquivos de relatório existentes?")   
#             if resposta == 'no':
#                 var_botton = 0
#                 messagebox.showinfo("Concluído", "Arquivos de relatório excluídos com sucesso.")
#             else:
#                 var_botton = 1
#                 messagebox.showinfo("Concluído", "Nenhum arquivo de relatório foi excluído.")

#         else:
#             messagebox.showinfo("Concluído", "Não há arquivos de relatório para excluir.")
#     else:
#         messagebox.showwarning("Aviso", "O diretório de relatórios não foi encontrado.")

#     # Excluir cada arquivo .xlsx

# Criar a janela principal
janela = tk.Tk()
janela.title("Integração Playlist Winradio")


# Definir o caminho para o arquivo de ícone (.ico)
caminho_icone = "logo_kakttus.ico"

# Verificar se o arquivo de ícone existe antes de atribuí-lo
if os.path.exists(caminho_icone):
    janela.iconbitmap(caminho_icone)

# Criar um rótulo de processo
label_processo = ttk.Label(janela, text="Aguardando execução...")
label_processo.pack()   

# # Adicionar um botão
# botao_excluir = tk.Button(janela, text="Grenciar Relatorios", command=excluir_arquivos_xlsx)
# botao_excluir.pack(pady=10)

# Criar uma área de texto para exibir a lista de arquivos
lista_arquivos_text = ScrolledText(janela, wrap=tk.WORD, height=10, width=40)
lista_arquivos_text.pack()



# Função para extrair dados do arquivo
def extrair_dados_txt(arquivo):
    dados = {}
    with open(arquivo, 'r') as file:
        for linha in file:
            partes = linha.strip().split()
            hora = partes[0]
            ids = partes[1:]
            dados[hora] = ids
    return dados

def criar_tabela_txt(dados):
    tabela = []
    for hora, ids in dados.items():
        # Verificar se há IDs para a hora atual
        if ids:
            for id in ids:
                if id != ',':
                    # Remover vírgulas dos IDs
                    id_sem_virgula = id.replace(',', '')
                    tabela.append({'ID': id_sem_virgula, 'Bloco': hora})
        else:
            # Adicionar entrada vazia na tabela para a hora sem IDs
            tabela.append({'ID': '', 'Bloco': hora})

    return tabela

# Função para salvar tabela em um arquivo Excel
def salvar_excel_txt(tabela, nome_arquivo='tabela.xlsx'):
    df = pd.DataFrame(tabela)
    df.to_excel(nome_arquivo, index=False)


# Suponha que os arquivos estejam no mesmo diretório do script
diretorio_arquivos = r'\\10.0.1.145\d\Playlist\pgm\Mapas'  # Atualize para o diretório correto se necessário

# Lista de DDs a serem processados
# Gerar a lista de "01" a "31"
dds_a_processar = [f"{i:02d}" for i in range(1, 32)]

# Imprimir a lista gerada
#!!!print(dds_a_processar)
# Extrair dados do arquivo

nomes_arquivos_gerados = []
for dd in dds_a_processar:
    
        # Obter a data de hoje
    hoje = datetime.today()
    
    # Converter a variável dd para inteiro
    dd_int = int(dd)

    # Obter o dia do mês atual
    dia_atual = hoje.day

    # Verificar se a variável dd é menor que o dia atual
    if dd_int < dia_atual:
        # Avançar para o próximo mês
        proximo_mes = hoje.month + 1

        # Verificar se o próximo mês ultrapassa dezembro
        if proximo_mes > 12:
            # Incrementar o ano e definir o mês para janeiro
            proximo_mes = 1
            ano = hoje.year + 1
        else:
            ano = hoje.year

    else:
        # Manter o mês e ano atuais
        proximo_mes = hoje.month
        ano = hoje.year

    # Formatar o nome do arquivo no formato AAAAMMDD
    nome_arquivo_data = f"{ano}{proximo_mes:02d}{dd_int:02d}"
    nome_arquivo = f"MAPA{dd_int:02d}-{proximo_mes:02d}-{ano}.txt"
    #print(f"nome arquivo: {nome_arquivo}")
    caminho_arquivo = os.path.join(diretorio_arquivos, nome_arquivo)
    # Adicionar o nome do arquivo à lista
    

    # Verificar a existência do arquivo
    if os.path.exists(caminho_arquivo):
        label_processo["text"] = f"Lista de Arquivos Processados:"
        lista_arquivos_text.insert(tk.END, f"{nome_arquivo}\n")
        janela.update()  # Atualizar a interface gráfica para refletir a mudança
        print(f"Processando arquivo: {nome_arquivo}")
        print(caminho_arquivo)

        # Extrair dados do arquivo
        dados_extrair = extrair_dados_txt(caminho_arquivo)
        

        # Criar tabela com id e bloco (IDs sem vírgulas)
        tabela_resultante = criar_tabela_txt(dados_extrair)

        # Salvar a tabela em um arquivo Excel
        salvar_excel_txt(tabela_resultante, f'{nome_arquivo_data}.xlsx')

        print(f"Arquivo {nome_arquivo_data} processado com sucesso.")
        
        nomes_arquivos_gerados.append(nome_arquivo_data)
        # print(nomes_arquivos_gerados)
    else:
        print(f"Arquivo {nome_arquivo_data} não encontrado!")



def extrair_dados_xml(xml_path):
    tree = ET.parse(xml_path)
    root = tree.getroot()

    contratos_data = []

    # Itera sobre todos os elementos Contrato no XML
    for contrato in root.findall(".//Contrato"):
        contrato_data = {
            "Codigo": contrato.find(".//Codigo").text,
        }

        spots_data = []

        for spot in contrato.find(".//Spots"):
            spot_data = {
                "Codigo": contrato_data["Codigo"],
                "Spot_ID": spot.get("ID"),
                "Spot_Audio": spot.get("Audio"),
                "Duracao": contrato.find(".//Duracao").text if contrato.find(".//Duracao") is not None else None,
            }
            spots_data.append(spot_data)

        contratos_data.extend(spots_data)

    return contratos_data

def criar_tabela_xml(dados):
    # Inicializa listas para cada coluna
    codigos = []
    spot_ids = []
    spot_audios = []
    duracoes = []

    # Itera sobre os dados
    for d in dados:
        codigo = d.get('Codigo', '')
        spot_id = d.get('Spot_ID', '')
        spot_audio = d.get('Spot_Audio', '')
        duracao = d.get('Duracao', '')

        # Concatena código e spot ID, se houver
        codigo_spot_id = f"{codigo}-{spot_id}" if spot_id else codigo

        # Adiciona valores às listas
        codigos.append(codigo_spot_id)
        spot_ids.append(spot_id)
        spot_audios.append(spot_audio)
        duracoes.append(duracao)

    # Cria um DataFrame pandas
    tabela = pd.DataFrame({
        'Código-SpotID': codigos,
        'SpotID': spot_ids,
        'SpotAudio': spot_audios,
        'Duracao': duracoes
    })

    return tabela

def salvar_excel_xml(tabela, excel_path):
    tabela.to_excel(excel_path, index=False)


# Diretório onde os arquivos .xml estão localizados
# diretorio = r'\\10.0.1.140\Contratos'  # Atualize para o diretório correto se necessário

# # Listar todos os arquivos no diretório
# arquivos_no_diretorio = os.listdir(diretorio)

# # Filtrar apenas os arquivos .xml
# arquivos_xml = [arquivo for arquivo in arquivos_no_diretorio if arquivo.endswith('.xml')]

# # Renomear cada arquivo .xml para "contrato.xml"
# for arquivo in arquivos_xml:
#     caminho_arquivo_antigo = os.path.join(diretorio, arquivo)
#     caminho_arquivo_novo = os.path.join(diretorio, 'contrato.xml')

#     # Renomear o arquivo
#     os.rename(caminho_arquivo_antigo, caminho_arquivo_novo)
#     print(f"Arquivo {arquivo} renomeado para contrato.xml.")

# Caminho do arquivo XML
xml_path = r'\\10.0.1.140\Contratos\contrato.xml'

# Extrair dados do XML
dados = extrair_dados_xml(xml_path)

# Criar tabela
tabela_resultante2 = criar_tabela_xml(dados)

# Salvar tabela em um arquivo Excel
salvar_excel_xml(tabela_resultante2, "tabela2.xlsx")


# Exemplo de uso
if __name__ == "__main__":
  
    for arquivo in nomes_arquivos_gerados:
       
        # Ler as tabelas já existentes
        tabela_resultante = pd.read_excel(f"{arquivo}.xlsx")
        tabela_resultante2 = pd.read_excel("tabela2.xlsx")

        # Renomear colunas da tabela_resultante para evitar conflitos
        tabela_resultante.rename(columns={'ID': 'ID_Horario'}, inplace=True)

        # Mesclar as tabelas usando a coluna comum 'ID_Horario'
                # Verificar se 'ID_Horario' está presente no DataFrame
        if 'ID_Horario' in tabela_resultante.columns:
            # Converter a coluna 'ID_Horario' para string
            tabela_resultante['ID_Horario'] = tabela_resultante['ID_Horario'].astype(str)
            tabela3 = pd.merge(tabela_resultante, tabela_resultante2, left_on='ID_Horario', right_on='Código-SpotID', how='inner')

            # Selecionar colunas desejadas e renomear
            tabela3 = tabela3[['ID_Horario', 'SpotAudio', 'Bloco', 'Duracao']]
            tabela3.rename(columns={'ID_Horario': 'ID', 'SpotAudio': 'AUDIO', 'Bloco':'Horario'}, inplace=True)

            # Salvar tabela3 em um arquivo Excel
            tabela3.to_excel(f"Relatório_{arquivo}.xlsx", index=False)

        else:
            caminho_arquivo = f"Relatório_{arquivo}.xlsx"
            if os.path.exists(caminho_arquivo):
                os.remove(caminho_arquivo)
            print(f"A coluna referente ao Bloco, não está presente no {arquivo}.")
                    



        # Carregar dados do arquivo XLS (Excel)
        def ler_excel(nome_arquivo):
            return pd.read_excel(nome_arquivo)

        # Converter dados do Excel para XML
        def converter_para_xml(dados):
            bloco_element_dict = {}

            for indice, linha in dados.iterrows():
                bloco = linha['Horario']
                
                if bloco not in bloco_element_dict:
                    bloco_element_dict[bloco] = Element("bloco", tp="C", tempo="60000", usr="")
                    medias_element = SubElement(bloco_element_dict[bloco], "medias")
                else:
                    medias_element = bloco_element_dict[bloco].find("medias")

                media_element = SubElement(medias_element, "media", tp="C", ind_vinheta="0", ind_tkm="0", ind_ctr="0")

                nro_int_element = SubElement(media_element, "nro_int")
                nro_int_element.text = rf"<![CDATA[{linha['ID']}]]>"

                path_element = SubElement(media_element, "path")
                path_element.text = f"<![CDATA[{linha['AUDIO']}]]>"

                nro_tkm_element = SubElement(media_element, "nro_tkm")
                nro_tkm_element.text = f"<![CDATA[0]]>"

                nome_element = SubElement(media_element, "nome")
                nome_element.text = f"<![CDATA[{linha['AUDIO']}]]>"
                
                nome_element = SubElement(media_element, "tempo")        
                # Verificar se o valor não é NaN antes de converter
                if pd.notna(linha['Duracao']):
                    duracao_milissegundos = int(linha['Duracao']) * 1000
                    nome_element.text = f"<![CDATA[{duracao_milissegundos}]]>"
                else:
                    # Trate o caso em que o valor é NaN, atribua um valor padrão ou faça o que for apropriado para o seu caso
                    nome_element.text = f"<![CDATA[0]]>"
                    
        # Verificar se 'Duracao' está presente no DataFrame
        # if 'Duracao' in dados.columns:
        #     duracao = converte_para_timedelta(linha['Duracao'])
        #     tempo_milissegundos = converte_para_milissegundos(duracao)
        #     tempo_element = SubElement(media_element, "tempo")
        #     tempo_element.text = f"<![CDATA[{tempo_milissegundos}]]>"
                
                # Adicionando campos adicionais
                campos_adicionais = ['campanha', 'base', 'logada', 'formato', 'obs', 'controle']
                for campo in campos_adicionais:
                    elemento = SubElement(media_element, campo)
                    elemento.text = "<![CDATA[]]>"

                # Adicione outros elementos conforme necessário

            return bloco_element_dict
        lista_nome_arquivo = []  
        def salvar_xml_na_pasta(xml_dict, pasta_destino):
            # Inicializa o cabeçalho do XML
            cabecalho = '<?xml version="1.0" encoding="ISO-8859-1" standalone="yes" ?>'
            
            for bloco, xml in xml_dict.items():
                if pd.notna(bloco):
                    bloco = datetime.strptime(bloco, "%H:%M")
                    bloco_str = bloco.strftime("%H:%M")
                    bloco_datetime = datetime.strptime(bloco_str, "%H:%M")

                    # Arredondar para o múltiplo de 5 minutos mais próximo
                    #bloco_rounded = (bloco_datetime - timedelta(minutes=bloco_datetime.minute % 5)).replace(second=0, microsecond=0)

                    # Criar o diretório com base na data
                    pasta_data = os.path.join(pasta_destino, datetime.today().strftime(arquivo))
                    os.makedirs(pasta_data, exist_ok=True)

                    # Adiciona a letra 'c' ao nome do arquivo
                    nome_arquivo = f"{bloco_datetime.strftime('%H%M%S')}C.xml"
                    caminho_arquivo = os.path.join(pasta_data, nome_arquivo)
                    lista_nome_arquivo.append(nome_arquivo)
                    

                # Converte o ElementTree em uma string
                    xml_str = minidom.parseString(tostring(xml)).toprettyxml(indent="    ")

                    # Remove a primeira linha do XML (que é a tag raiz)
                    xml_str = '\n'.join(xml_str.split('\n')[1:])
                    
                    # Corrige a interpretação de &lt; e &gt; para < e >
                    xml_str = unescape(xml_str)

                    # Remover caracteres que não existem em latin-1
                    xml_str = xml_str.encode('latin-1', errors='replace').decode('latin-1')


                    with open(caminho_arquivo, "w", encoding="ISO-8859-1") as xml_file:
                        # Adiciona o cabeçalho ao XML e formata o conteúdo do XML
                        xml_file.write(f'{cabecalho}\n{xml_str}')
                        
                       # Verifica e apaga arquivos extras na pasta
                    arquivos_na_pasta = os.listdir(pasta_data)
                    for arquivo_na_pasta in arquivos_na_pasta:
                        if arquivo_na_pasta not in lista_nome_arquivo:
                            caminho_arquivo_extra = os.path.join(pasta_data, arquivo_na_pasta)
                            os.remove(caminho_arquivo_extra)
                            #print(f"Arquivo extra removido: {caminho_arquivo_extra}")
                            
        # Função para converter tempo para milissegundos
        def converte_para_timedelta(duracao):
            # Verifica se é uma instância de datetime.time
            if isinstance(duracao, time):
                # Converte a hora, minuto e segundo para timedelta
                return timedelta(hours=duracao.hour, minutes=duracao.minute, seconds=duracao.second)
            elif isinstance(duracao, str):
                # Converte uma string no formato HH:MM:SS para timedelta
                horas, minutos, segundos = map(int, duracao.split(':'))
                return timedelta(hours=horas, minutes=minutos, seconds=segundos)
            else:
                # Se não for nem datetime.time nem string, retorna None
                return None

        def converte_para_milissegundos(tempo):
            # A função timedelta.total_seconds() retorna o tempo total em segundos,
            # então multiplicamos por 1000 para converter para milissegundos
            return int(tempo.total_seconds() * 1000)
        
        arquivo_excel = f"Relatório_{arquivo}.xlsx"
        if os.path.exists(arquivo_excel):
            dados_excel = ler_excel(arquivo_excel)
            dados_xml_dict = converter_para_xml(dados_excel)
            # Especifique o diretório de destino
            pasta_destino = rf"\\10.0.1.145\BandNews Ar\Integracao\Programacao"
            #\\10.0.1.145\BandNews Ar\Integracao\Programacao
            salvar_xml_na_pasta(dados_xml_dict, pasta_destino)


        

    janela.mainloop()
    # Apagar as tabelas geradas
    # Filtrar apenas os arquivos .xlsx
    diretorio = '.'
    arquivos_no_diretorio = os.listdir(diretorio)
    arquivos_xlsx = [arquivo for arquivo in arquivos_no_diretorio if arquivo.endswith('.xlsx')]

    # Excluir cada arquivo .xlsx
    for arquivo in arquivos_xlsx:
        caminho_arquivo = os.path.join(diretorio, arquivo)
        os.remove(caminho_arquivo)
    # if var_botton == 0:
    #         diretorio_relatorios_botton = r'.'
    #         for arquivo in arquivos_xlsx_botton:
    #             caminho_arquivo = os.path.join(diretorio_relatorios_botton, arquivo)
    #             os.remove(caminho_arquivo)
    #             print(f"Arquivo {arquivo} excluído com sucesso.")
            
        
        #print(f"Arquivo {arquivo} excluído com sucesso.")
print("Implantação Completa!")