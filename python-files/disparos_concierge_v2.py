import schedule
from selenium import webdriver
import time 
import os, shutil
from datetime import datetime, date, timedelta
import pandas as pd
import glob
from pathlib import Path
import csv
import openpyxl
import win32com.client as win32
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import pyodbc

while True:
    try:
        class MeuScript:
            def __init__(self):
                self.control = False
                if not self.control:  
                    self.executa_script()
                    self.control = True
                schedule.every(1).minutes.do(self.executa_script)
            
            def executa_script(self):
                dvar=1
                while dvar == 1:
                    # URL da página
                    print("Obtendo a base...")
                    url = "http://urademaiss.santanderbr.corp/PesquisaSatisfacao/extracao"

                    # Fazer a requisição GET para obter o conteúdo da página
                    response = requests.get(url)

                    # Verificar se a requisição foi bem-sucedida
                    if response.status_code == 200:
                        # Extrair o conteúdo HTML da resposta
                        html_content = response.text
                        # Criar um objeto BeautifulSoup para analisar o HTML
                        soup = BeautifulSoup(html_content, "html.parser")
                        # Selecionar o formulário
                        form = soup.find("form")
                        # Selecionar a opção "Pesquisa PF"
                        radio_button = form.find("input", {"value": "10"})
                        # Obter os valores dos campos necessários para a requisição POST
                        pesquisa_id = radio_button["value"]
                        
                        # Calcular a data inicial (dia - 3) e formatar como "aaaa-dd-mm"
                        data_corte = (date.today() - timedelta(days=2)).strftime("%d/%m/%Y")
                        initial_date = (date.today() - timedelta(days=2)).strftime("%Y-%m-%d")
                        print(initial_date)
                        final_date = form.find("input", {"id": "finalDate"})["value"]
                        
                        # Dados para a requisição POST
                        data = {
                            "pesquisaID": pesquisa_id,
                            "initialDate": initial_date,
                            "finalDate": final_date
                        }
                        
                        # Enviar a requisição POST para pesquisar
                        response = requests.post(url, data=data)
                        
                        # Verificar se a requisição foi bem-sucedida
                        if response.status_code == 200:
                            # Extrair o conteúdo HTML da resposta
                            html_content = response.text
                            # Criar um objeto BeautifulSoup para analisar o HTML
                            soup = BeautifulSoup(html_content, "html.parser")
                            # Selecionar o link de download
                            download_link = soup.find("a", href=True)
                            # Obter o URL do arquivo CSV
                            csv_href = download_link["href"]
                            csv_url = urljoin("http://urademaiss.santanderbr.corp/", csv_href)
                            print(csv_url)
                            
                            # Definir o diretório de download como a pasta de download do usuário
                            download_directory = os.path.expanduser("~") + "/Downloads"
                            
                            # Fazer o download do arquivo CSV
                            response = requests.get(csv_url)
                            
                            # Verificar se o download foi bem-sucedido
                            if response.status_code == 200:
                                # Salvar o arquivo CSV no diretório especificado
                                with open(os.path.join(download_directory, "pesquisa_satisfacao.csv"), "wb") as file:
                                    file.write(response.content)
                                print("Download concluído com sucesso!")
                                dvar=0
                            else:
                                print("Falha ao fazer o download do arquivo CSV.")
                        else:
                            print("Falha na solicitação de pesquisa.")
                    else:
                        print("Falha ao acessar a página.")

                print("Manipulando Arquivos...")
                downloads_dir = os.path.join(os.path.expanduser('~'), 'downloads')
                dest_dir = r'\\mscluster41fs\ANTIFRAUDELID\BASE CONCIERGE\AUXILIAR'
                
                # Listar arquivos
                csv_files = [f for f in os.listdir(downloads_dir) if f.endswith('.csv')]
                
                # Ordenar os arquivos por data
                csv_files.sort(key=lambda x: os.path.getatime(os.path.join(downloads_dir, x)))
                
                # Pegar o ULTIMO DOWNLOAD
                last_two_csv_files = csv_files[-1:]
                print("pass")
                # Excluir arquivos do diretório de destino
                for file in os.listdir(dest_dir):
                    file_path = os.path.join(dest_dir, file)
                    try:
                        if os.path.isfile(file_path):
                            os.remove(file_path)
                            print(f"Arquivo '{file}' removido de '{dest_dir}'")
                    except Exception as e:
                        print(f"Erro ao remover '{file}': {e}")
                print("pass")
                # Copiar para diretório de destino e excluir arquivos originais
                for csv_file in last_two_csv_files:
                    src_path = os.path.join(downloads_dir, csv_file)
                    dest_path = os.path.join(dest_dir, csv_file)
                    shutil.copy(src_path, dest_path)
                    #print("pass")
                    #os.remove(src_path)
                    print(f"Arquivo '{csv_file}' copiado para '{dest_dir}'")# e removido de '{downloads_dir}'
                
                print("pass")
                path1 = (r'\\mscluster41fs\ANTIFRAUDELID\BASE CONCIERGE\EMAILS')
                os.chdir(r"\\mscluster41fs\ANTIFRAUDELID\BASE CONCIERGE\AUXILIAR")

                extension = 'csv'
                all_filenames = [i for i in glob.glob('*.{}'.format(extension))]
                
                diretorio = r"\\mscluster41fs\ANTIFRAUDELID\BASE CONCIERGE\AUXILIAR"
                extensao = "*.csv"

                arquivos_csv = glob.glob(os.path.join(diretorio, extensao))
                print("pass")
                if arquivos_csv:
                    print("Combinando arquivos...")
                    # combinar todos os arquivos da lista
                    combined_csv = pd.concat([pd.read_csv(f, sep=";",encoding='cp1252', low_memory=False) for f in all_filenames ])

                    #exportar para csv
                    combined_csv.to_csv(path1+"\MAIL.csv", index=False, encoding='cp1252', sep=";")

                    base = pd.read_csv(r'\\mscluster41fs\ANTIFRAUDELID\BASE CONCIERGE\EMAILS\MAIL.csv', sep=";", encoding='cp1252')
                    b_ura = pd.read_csv(r'\\mscluster41fs\ANTIFRAUDELID\BASE CONCIERGE\EMAILS\MAIL.csv', sep=";", encoding='cp1252')
                    print('b_ura')
                    print(b_ura)
                    # b_ura = b_ura[b_ura['DATAINICIO'] > data_corte]
                    print('b_ura corte')
                    print(b_ura)
                    b_ura_condicional = base[(base["ORDEM"] == 1) & (base["SEGMENTO"].isin(["select", "selectHigh"])) & (base["RESPOSTA"] <=6)]
        


                    b_ura_condicional['CONDICIONAL'] = b_ura_condicional['RESPOSTA'].apply(lambda x: 'DETRATOR' if x <= 6 else 'NEUTRO' if x >= 7 and x <= 8 else 'PROMOTOR')

                    b_ura_condicional.drop(['DATAINICIO',	'DATAFIM',	'PESQUISA_ID',	'TIPODOC', 'NUMDOCUMENTO',	'NOME',	'SEGMENTO',	'PONTO', 'ORDEM', 'SERVICO', 'TIPOPERGUNTA'	,'FRASES'	,'RESPOSTA'	,'TFC', 'SERVICO_PESQUISADO'],axis=1, inplace=True)

                    print("base1")
                    print(b_ura_condicional)

                    b_ura = base[((base["ORDEM"] == 2) & (base["RESPOSTA"] == 1) | (base["ORDEM"] == 3) & (base["RESPOSTA"] == 1))]

                    b_ura = pd.merge(b_ura,b_ura_condicional, on="CONNID_ORIGINAL", how="inner")
                    print("base2")

                    b_ura = b_ura[b_ura['CONNID_ORIGINAL'] != '4,39036E+14']

                    print(b_ura)
                    b_ura["NUMDOCUMENTO"] = b_ura["NUMDOCUMENTO"].astype(str)
                    path = (r'\\mscluster41fs\ANTIFRAUDELID\BASE CONCIERGE')


                    # Caminho do banco de dados Access
                    access_db = r"\\mscluster41fs\ANTIFRAUDELID\BASE CONCIERGE\DB_SELECT.accdb" 

                    # Função para formatar a data no padrão do banco de dados Access
                    def formatar_data(data):
                        return data.strftime('%d/%m/%Y %H:%M')

                    # Cria a conexão com o banco de dados Access
                    conn = pyodbc.connect(r'Driver={Microsoft Access Driver (*.mdb, *.accdb)};DBQ=' + access_db)
                    cursor = conn.cursor()

                    # Define as datas de hoje e ontem formatadas no padrão do banco de dados

                    hoje = (datetime.now() + timedelta(days=1)).strftime('%m/%d/%Y')
                    ontem = (datetime.now() - timedelta(days=1)).strftime('%m/%d/%Y')
                    
                    
                    print(ontem)
                    
                    # Consulta os dados da tabela TB_SELECT apenas para hoje e ontem
                    
                    query = f"SELECT * FROM TB_SELECT WHERE DT_ABERTURA >= #"+ ontem +" 00:00# AND DT_ABERTURA < #"+ hoje +" 00:00#"
                    
                    print(query)
                    b_concierge = pd.read_sql(query, conn)


                    print(b_concierge)
                    
                    b_concierge['DT_ABERTURA'] = pd.to_datetime(b_concierge['DT_ABERTURA'], format='%d/%m/%Y')
                    
                    print('formata data')
                    print(b_concierge)
                    print(data_corte)
                    print('corteeeeeeeeeee datas')
                    print(b_concierge)

                    b_concierge["DOCUMENTO"] = b_concierge["DOCUMENTO"].str.replace(r'\D', '', regex=True)

                    print("pass")

                    b_concierge["DOCUMENTO"] = pd.to_numeric(b_concierge["DOCUMENTO"])


                    b_concierge["DOCUMENTO"] = b_concierge["DOCUMENTO"].astype(str)
                    
                    b_concierge = b_concierge.rename(columns={'DOCUMENTO': 'NUMDOCUMENTO'})
                    b_concierge = b_concierge.drop(columns=['ID'], axis=1)

                    
                    print(b_concierge)
                    merge_col = "NUMDOCUMENTO"

                    b_merged = pd.merge(b_concierge,b_ura, on= merge_col, how="inner")

                    print("mergeeeeeeeeed")

                    print(b_merged)

                    #Nota errada
                    filter3_results = b_merged[b_merged['MOTIVO'] != 'Nota errada']
                    filter3_results = filter3_results[filter3_results['MOTIVO'] != 'Nota Errada']
                    filter3_results = filter3_results[filter3_results['MOTIVO'] != 'NOTA ERRADA']
                    filter3_results = filter3_results[filter3_results['MOTIVO'] != 'nota errada']
                    print("- nota erradas")
                    print(filter3_results)
                    #filter3_results = b_merged[b_merged['CONDICIONAL'] != 'NEUTRO']
                    print("1")
                    print(filter3_results)

                    b_quadro = pd.read_excel(path + "\QUADRO.xlsx")

                    merge_col2 = "TFC"

                    b_merged2 = pd.merge(filter3_results,b_quadro, on= merge_col2, how="inner")
                    print("b_merged2")
                    print(b_merged2)

                    filter4_results = b_merged2[b_merged2['TLIDER'].notna()] 
                    print("F41")
                    print(filter4_results)

                    print("PASS UG")
                    
                    filter4_results.to_excel(path+"\EMAILS\B_AUTO_POLICE.xlsx", index=False)
                    print("CRIADO ARQUIVO AUTO POLICE")


                    path = (r'\\mscluster41fs\ANTIFRAUDELID\BASE CONCIERGE')

                    workbook = openpyxl.load_workbook(r'\\mscluster41fs\ANTIFRAUDELID\BASE CONCIERGE\EMAILS\B_AUTO_POLICE.xlsx')
                    print("AUTOPOLICE READ OK")
                    sheet = workbook.active
                    print("SELECIONA A PLANILHA")
                    # Inicializar o Outlook 
                    outlook = win32.Dispatch('Outlook.Application')
                    print("INICIA O OUTLOOK")

                    log_dir = r'\\mscluster41fs\ANTIFRAUDELID\BASE CONCIERGE\EMAILS\LOG'
                    log_file_path = os.path.join(log_dir, 'log.csv')

                    #carregar os protocolos
                    print("CARREGANDO PROTOCOLOS")
                    protocolos_no_log = []
                    if os.path.exists(log_file_path):
                        with open(log_file_path, 'r') as file:
                            reader = csv.reader(file)
                            header = next(reader) #pula cabe็alho

                            for log_row in reader:
                                protocolos_no_log.append(log_row[0])

                    print("ITERA PELAS LINHAS DO XLSX")     
                    # Iterar pelas linhas do arquivo XLSX 
                    for row in sheet.iter_rows(min_row=2, values_only=True): 
                        Protocolo,NUMDOCUMENTO,DatadeAbertura,Responsแvel,FCR,Status,VINCULACAO,Retorno,NotaRevertida,QualArea,Atendido,MotivodoContato,DatadeConclusใo,DATAINICIO,DATAFIM,PESQUISA_ID,TIPODOC,NOME_x,SEGMENTO,PONTO,ORDEM,TIPOPERGUNTA,FRASES,RESPOSTA,TFC,CONNID_ORIGINAL,SERVICO,SERVICO_PESQUISADO,CONDICIONAL,TESPECILISTA,NOME_y,LIDERESPECIALISTA,TLIDER,LIDERSENIOR,TSENIOR,LIDEREXECUTIVO,TEXEC,OPERACAO, SITE, RESP1,RESP2,RESP3 = row 
                        print("no loop")
                        #verifica se ja existe

                        if str(NUMDOCUMENTO) not in protocolos_no_log:
                            outlook = win32.Dispatch('outlook.application') 
                            # Criar um objeto Email 
                            email = outlook.CreateItem(0) # 0 representa um novo email 
                            # Configurar os campos do email 
                            email.Subject = 'URGENTE SELECT - ALERTA CONCIERGE ' + CONDICIONAL +  "( "+ SITE + " " +DATAINICIO +" )" 
                            email.HTMLBody = (r"""<!DOCTYPE html><html xmlns:v="urn:schemas-microsoft-com:vml" xmlns:o="urn:schemas-microsoft-com:office:office" lang="en"><head><title></title><meta http-equiv="Content-Type" content="text/html; charset=utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><!--[if mso]><xml><o:OfficeDocumentSettings><o:PixelsPerInch>96</o:PixelsPerInch><o:AllowPNG/></o:OfficeDocumentSettings></xml><![endif]--><!--[if !mso]><!--><link 
                            href="https://fonts.googleapis.com/css2?family=Source+Sans+Pro:wght@400;700;900&amp;display=swap" rel="stylesheet" type="text/css"><!--<![endif]--><style>
                            *{box-sizing:border-box}body{margin:0;padding:0}a[x-apple-data-detectors]{color:inherit!important;text-decoration:inherit!important}#MessageViewBody a{color:inherit;text-decoration:none}p{line-height:inherit}.desktop_hide,.desktop_hide table{mso-hide:all;display:none;max-height:0;overflow:hidden}.image_block img+div{display:none} @media (max-width:720px){.mobile_hide{display:none}.row-content{width:100%!important}.stack .column{width:100%;display:block}.mobile_hide{min-height:0;max-height:0;max-width:0;overflow:hidden;font-size:0}.desktop_hide,.desktop_hide table{display:table!important;max-height:none!important}}
                            </style></head><body style="background-color:#fff;margin:0;padding:0;-webkit-text-size-adjust:none;text-size-adjust:none"><table class="nl-container" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;background-color:#fff"><tbody><tr><td><table class="row row-1" align="center" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0"><tbody><tr><td><table 
                            class="row-content stack" align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;background-color:#efefef;border-bottom:1px solid #aaa5a5;border-radius:10px 10px 0 0;color:#000;width:700px;margin:0 auto" width="700"><tbody><tr><td class="column column-1" width="66.66666666666667%" 
                            style="mso-table-lspace:0;mso-table-rspace:0;font-weight:400;text-align:left;padding-bottom:5px;padding-top:15px;vertical-align:top;border-top:0;border-right:0;border-bottom:0;border-left:0"><table class="paragraph_block block-1" width="100%" border="0" cellpadding="10" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;word-break:break-word"><tr><td class="pad"><div 
                            style="color:#000;direction:ltr;font-family:'Source Sans Pro',Tahoma,Verdana,Segoe,sans-serif;font-size:17px;font-weight:900;letter-spacing:0;line-height:120%;text-align:left;mso-line-height-alt:20.4px"><p style="margin:0"><strong>URGENTE - ALERTA </strong><strong>CONCIERGE 🚨</strong></p></div></td></tr></table></td><td class="column column-2" width="33.333333333333336%" 
                            style="mso-table-lspace:0;mso-table-rspace:0;font-weight:400;text-align:left;padding-bottom:5px;padding-top:5px;vertical-align:top;border-top:0;border-right:0;border-bottom:0;border-left:0"><table class="paragraph_block block-1" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;word-break:break-word"><tr><td class="pad" style="padding-bottom:10px;padding-left:10px;padding-right:10px;padding-top:20px"><div 
                            style="color:#000;direction:ltr;font-family:'Source Sans Pro',Tahoma,Verdana,Segoe,sans-serif;font-size:10px;font-weight:700;letter-spacing:0;line-height:200%;text-align:center;mso-line-height-alt:20px"><p style="margin:0"><span style="color: #6b6b6b;">&lt;Esta mensagem é automatizada&gt;</span></p></div></td></tr></table></td></tr></tbody></table></td></tr></tbody></table><table class="row row-2" align="center" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" 
                            style="mso-table-lspace:0;mso-table-rspace:0"><tbody><tr><td><table class="row-content stack" align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;background-color:#f0f0f0;border-radius:0;color:#000;width:700px;margin:0 auto" width="700"><tbody><tr><td class="column column-1" width="100%" 
                            style="mso-table-lspace:0;mso-table-rspace:0;font-weight:400;text-align:left;padding-bottom:5px;padding-top:5px;vertical-align:top;border-top:0;border-right:0;border-bottom:0;border-left:0"><table class="paragraph_block block-1" width="100%" border="0" cellpadding="10" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;word-break:break-word"><tr><td class="pad"><div 
                            style="color:#000;direction:ltr;font-family:'Source Sans Pro',Tahoma,Verdana,Segoe,sans-serif;font-size:12px;font-weight:400;letter-spacing:0;line-height:120%;text-align:left;mso-line-height-alt:14.399999999999999px"><p style="margin:0">Identificamos&nbsp;um&nbsp;<strong>cliente&nbsp;""") + str(CONDICIONAL) + ("""&nbsp;de URA&nbsp;</strong>que não teve sua solicitação atendida, segue as informações:</p></div></td></tr></table></td></tr></tbody></table></td></tr></tbody></table><table class="row row-3" align="center" 
                            width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0"><tbody><tr><td><table class="row-content stack" align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;background-color:#f0f0f0;border-radius:0;color:#000;width:700px;margin:0 auto" width="700"><tbody><tr><td class="column column-1" width="50%" 
                            style="mso-table-lspace:0;mso-table-rspace:0;font-weight:400;text-align:left;padding-bottom:5px;padding-top:5px;vertical-align:top;border-top:0;border-right:0;border-bottom:0;border-left:0"><table class="paragraph_block block-1" width="100%" border="0" cellpadding="10" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;word-break:break-word"><tr><td class="pad"><div 
                            style="color:#000;direction:ltr;font-family:'Source Sans Pro',Tahoma,Verdana,Segoe,sans-serif;font-size:12px;font-weight:400;letter-spacing:0;line-height:150%;text-align:left;mso-line-height-alt:18px"><p style="margin:0;margin-bottom:16px"><strong>Dados do Especialista</strong></p><p style="margin:0"><strong>&nbsp; &nbsp; &nbsp; Matricula: &nbsp;</strong>""")+ str(TESPECILISTA) +("""<br><strong>&nbsp; &nbsp; &nbsp; Nome: &nbsp;</strong>""")+ str(NOME_y) +("""<br><strong>&nbsp; &nbsp; &nbsp; Operação: </strong>""")+ str(OPERACAO) +("""<br><strong>&nbsp; &nbsp; &nbsp; Líder: &nbsp;</strong>""")+ str(LIDERESPECIALISTA) +("""<br><strong>&nbsp; &nbsp; &nbsp; Sênior: &nbsp;</strong>""")+ str(LIDERSENIOR) +("""<br><strong>&nbsp; &nbsp; &nbsp; Executivo: &nbsp;</strong>""")+ str(LIDEREXECUTIVO) +("""</p></div></td></tr></table></td><td class="column column-2" width="50%" style="mso-table-lspace:0;mso-table-rspace:0;font-weight:400;text-align:left;padding-bottom:5px;padding-top:5px;vertical-align:top;border-top:0;border-right:0;border-bottom:0;border-left:0"><table class="paragraph_block block-1" width="100%" border="0" 
                            cellpadding="10" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;word-break:break-word"><tr><td class="pad"><div style="color:#000;direction:ltr;font-family:'Source Sans Pro',Tahoma,Verdana,Segoe,sans-serif;font-size:12px;font-weight:400;letter-spacing:0;line-height:150%;text-align:left;mso-line-height-alt:18px"><p style="margin:0;margin-bottom:16px"><strong>Dados da Chamada</strong></p><p style="margin:0"><strong>&nbsp; &nbsp; &nbsp; Data: &nbsp;</strong>""")+ str(DATAINICIO) +("""<br><strong>&nbsp; &nbsp; &nbsp; Chaveunica: </strong>""")+ str(CONNID_ORIGINAL) + ("""<br><strong>&nbsp; &nbsp; &nbsp; Nível de Vinculação Cliente: </strong>""") + str(VINCULACAO) + ("""</p></div></td></tr></table></td></tr></tbody></table></td></tr></tbody></table><table class="row row-4" align="center" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0"><tbody><tr><td><table class="row-content stack" align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" 
                            style="mso-table-lspace:0;mso-table-rspace:0;background-color:#f0f0f0;border-radius:0;color:#000;width:700px;margin:0 auto" width="700"><tbody><tr><td class="column column-1" width="100%" style="mso-table-lspace:0;mso-table-rspace:0;font-weight:400;text-align:left;padding-bottom:5px;padding-top:5px;vertical-align:top;border-top:0;border-right:0;border-bottom:0;border-left:0"><table class="paragraph_block block-1" width="100%" border="0" cellpadding="10" cellspacing="0" role="presentation" 
                            style="mso-table-lspace:0;mso-table-rspace:0;word-break:break-word"><tr><td class="pad"><div style="color:#000;direction:ltr;font-family:'Source Sans Pro',Tahoma,Verdana,Segoe,sans-serif;font-size:12px;font-weight:700;letter-spacing:0;line-height:120%;text-align:left;mso-line-height-alt:14.399999999999999px"><p style="margin:0;margin-bottom:16px">Motivo do contato: """) + str(QualArea) + ("""<BR><br>STATUS: """) + str(Status) + ("""<br>FCR: """)+ str(FCR) + ("""<br>WL 2º NIVEL: """) + str(Retorno) + ("""<br><br>Resumo da Chamada:</p>""")+ str(MotivodoContato) + ("""<p style="margin:0;margin-bottom:16px">&nbsp;</p><p style="margin:0;margin-bottom:16px">&nbsp;</p><p style="margin:0">&nbsp;</p>
                            </div></td></tr></table></td></tr></tbody></table></td></tr></tbody></table><table class="row row-5" align="center" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0"><tbody><tr><td><table class="row-content stack" align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;background-color:#f0f0f0;border-radius:0;color:#000;width:700px;margin:0 auto" width="700">
                            <tbody><tr><td class="column column-1" width="100%" style="mso-table-lspace:0;mso-table-rspace:0;font-weight:400;text-align:left;padding-bottom:5px;padding-top:5px;vertical-align:top;border-top:0;border-right:0;border-bottom:0;border-left:0"><table class="paragraph_block block-1" width="100%" border="0" cellpadding="10" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;word-break:break-word"><tr><td class="pad"><div 
                            style="color:#000;direction:ltr;font-family:'Source Sans Pro',Tahoma,Verdana,Segoe,sans-serif;font-size:12px;font-weight:400;letter-spacing:0;line-height:120%;text-align:left;mso-line-height-alt:14.399999999999999px"><p style="margin:0">Favor respoder o email em até 24h com análise da jornada e oprtunidades identificadas.</p></div></td></tr></table></td></tr></tbody></table></td></tr></tbody></table><table class="row row-6" align="center" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" 
                            style="mso-table-lspace:0;mso-table-rspace:0"><tbody><tr><td><table class="row-content stack" align="center" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;background-color:#f0f0f0;border-radius:0 0 10px 10px;color:#000;width:700px;margin:0 auto" width="700"><tbody><tr><td class="column column-1" width="66.66666666666667%" 
                            style="mso-table-lspace:0;mso-table-rspace:0;font-weight:400;text-align:left;padding-bottom:5px;padding-top:5px;vertical-align:top;border-top:0;border-right:0;border-bottom:0;border-left:0"><table class="paragraph_block block-1" width="100%" border="0" cellpadding="10" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0;word-break:break-word"><tr><td class="pad"><div 
                            style="color:#000;direction:ltr;font-family:'Source Sans Pro',Tahoma,Verdana,Segoe,sans-serif;font-size:12px;font-weight:400;letter-spacing:0;line-height:120%;text-align:left;mso-line-height-alt:14.399999999999999px"><p style="margin:0"><strong>Atenciosamente,</strong></p></div></td></tr></table><table class="image_block block-2" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0"><tr><td class="pad" 
                            style="padding-bottom:5px;padding-left:5px;padding-right:5px;width:100%"><div class="alignment" align="left" style="line-height:10px"><img src="https://d15k2d11r6t6rl.cloudfront.net/public/users/Integrators/0db9f180-d222-4b2b-9371-cf9393bf4764/0bd8b69e-4024-4f26-9010-6e2a146401fb/Screenshot_4-removebg-preview.png" style="display:block;height:auto;border:0;max-width:280px;width:100%" width="280"></div></td></tr></table></td><td class="column column-2" width="33.333333333333336%" 
                            style="mso-table-lspace:0;mso-table-rspace:0;font-weight:400;text-align:left;padding-bottom:5px;padding-top:5px;vertical-align:top;border-top:0;border-right:0;border-bottom:0;border-left:0"><table class="empty_block block-1" width="100%" border="0" cellpadding="0" cellspacing="0" role="presentation" style="mso-table-lspace:0;mso-table-rspace:0"><tr><td class="pad"><div></div></td></tr></table></td></tr></tbody></table></td></tr></tbody></table></td></tr></tbody></table><!-- End --><div style="background-color:transparent;">
                            <div style="Margin: 0 auto;min-width: 320px;max-width: 500px;overflow-wrap: break-word;word-wrap: break-word;word-break: break-word;background-color: transparent;" class="block-grid ">
                            <div style="border-collapse: collapse;display: table;width: 100%;background-color:transparent;">
                                <!--[if (mso)|(IE)]><table width="100%" cellpadding="0" cellspacing="0" border="0"><tr><td style="background-color:transparent;" align="center"><table cellpadding="0" cellspacing="0" border="0" style="width: 500px;"><tr class="layout-full-width" style="background-color:transparent;"><![endif]-->
                                <!--[if (mso)|(IE)]><td align="center" width="500" style=" width:500px; padding-right: 0px; padding-left: 0px; padding-top:15px; padding-bottom:15px; border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent;" valign="top"><![endif]-->
                                <div class="col num12" style="min-width: 320px;max-width: 500px;display: table-cell;vertical-align: top;">
                                    <div style="background-color: transparent; width: 100% !important;">
                                        <!--[if (!mso)&(!IE)]><!--><div style="border-top: 0px solid transparent; border-left: 0px solid transparent; border-bottom: 0px solid transparent; border-right: 0px solid transparent; padding-top:15px; padding-bottom:15px; padding-right: 0px; padding-left: 0px;">
                                            <!--<![endif]-->


                                            <!--[if (!mso)&(!IE)]><!-->
                                        </div><!--<![endif]-->
                                    </div>
                                </div>
                                <!--[if (mso)|(IE)]></td></tr></table></td></tr></table><![endif]-->
                            </div>
                            </div>
                            </div></body></html>""")

                            email.SentOnBehalfOfName = "alertas-concierge@sxnegocios.com.br"
                            destinatarios = [f'{TLIDER}',f'{TSENIOR}',f'{TEXEC}',f'{RESP1}',f'{RESP2}',f'{RESP3}']#[f'{TLIDER}@sxnegocios.com.br',f'{TSENIOR}@sxnegocios.com.br',f'{TEXEC}@sxnegocios.com.br']#TLIDER, TSENIOR, TEXEC
                            
                            df = pd.read_excel(r"\\mscluster41fs\ANTIFRAUDELID\BASE CONCIERGE\COPIADOS.xlsx")
                            lista_copiados = df.values.tolist()

                            emails = []
                            for valor in lista_copiados:
                                email1 = str(valor).strip("['']")
                                emails.append(email1)
                                
                            copiados = ";".join(emails)
                            print(copiados)
                            
                            email.Cc = copiados
                            email.Bcc = ""

                            print("verifica destinatarios")
                            def verificar_destinatario(destinatario):
                                print("verificando")
                                outlook = win32.Dispatch('Outlook.Application')
                                resolved = outlook.Session.CreateRecipient(destinatario) #123
                                resolved.Resolve()
                                return resolved
                            # Adicione os destinatários válidos ao email
                            destinatarios_validos = []
                            destinatarios_com_erro = []
                            for destinatario in destinatarios:
                                try:
                                    resolved = verificar_destinatario(destinatario)
                                    if resolved.Resolved:
                                        destinatarios_validos.append(resolved)
                                    else:
                                        destinatarios_com_erro.append(destinatario)
                                except Exception as e:
                                    print(f"Erro ao resolver destinatário {destinatario}: {e}")
                                    destinatarios_com_erro.append(destinatario)

                            # Exiba os destinatários válidos
                            print("Destinatários válidos:")
                            for destinatario_valido in destinatarios_validos:
                                print(destinatario_valido.Name)

                            # Exiba os destinatários com erro
                            print("Destinatários com erro:")
                            for destinatario_erro in destinatarios_com_erro:
                                print(destinatario_erro)

                            # Verifique se há destinatários válidos antes de enviar o email
                            if len(destinatarios_validos) > 0:
                                # Adicione todos os destinatários válidos ao email
                                for destinatario_valido in destinatarios_validos:
                                    email.Recipients.Add(destinatario_valido)
                                
                                # Verifique se há destinatários adicionados ao email
                                if len(email.Recipients) > 0:
                                    email.Send()
                                    print("Email enviado com sucesso!")
                                    
                                    # caminhos
                                    log_dir = r'\\mscluster41fs\ANTIFRAUDELID\BASE CONCIERGE\EMAILS\LOG'
                                    log_file_path = os.path.join(log_dir, 'log.csv')
                                    # verifica se existe
                                    if not os.path.exists(log_file_path):
                                            with open(log_file_path, 'w', newline='') as file:
                                                writer = csv.writer(file)
                                                writer.writerow(["NUMDOCUMENTO","PROTOCOLO","DATA CHAMADA", "TESPECIALISTA", "ESPECIALISTA", "TLIDER", "LIDER", "TSENIOR", "SENIOR", "TEXEC", "EXEC","CONNID_ORIGINAL","CASCATA","OPERAÇÃO","SITE","TIPO_ALERTA"])

                                    #ADICIONAR NOVA ENTRADA AO CSV
                                    with open(log_file_path, 'a', newline='') as file:
                                        writer = csv.writer(file)
                                        data_disparo = datetime.now()
                                        writer.writerow([NUMDOCUMENTO,Protocolo,DATAINICIO,TESPECILISTA,NOME_y,TLIDER,LIDERESPECIALISTA,TSENIOR,LIDERSENIOR,TEXEC,LIDEREXECUTIVO,CONNID_ORIGINAL,QualArea,OPERACAO,SITE,CONDICIONAL])

                                        print("Entrada adicionada ao arquivo de log.")
                                        
                                else:
                                    print("Nenhum destinatário válido adicionado ao email. O email não foi enviado.")
                            else:
                                print("Nenhum destinatário válido encontrado. O email não foi enviado.")

                    dvar=1
            
        meu_script =  MeuScript()

    except:
        print("Deu ruim")
        continue

    while True:
        schedule.run_pending()
        time.sleep(1)
                    



