import os
import time
from datetime import datetime, timedelta
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import fitz  # PyMuPDF
from PIL import Image
from io import BytesIO
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from email.mime.application import MIMEApplication
import pandas as pd
import matplotlib.pyplot as plt

# Função para obter a data de consulta
def obter_data_consulta(manual=False, ano=2024, mes=8, dia=12):
    if manual:
        return ano, mes, dia
    else:
        hoje = datetime.today()
        return hoje.year, hoje.month, hoje.day

# Obter a data de consulta
ano, mes, dia = obter_data_consulta(manual=False)
mes_str = f"{mes:02d}"
dia_str = f"{dia:02d}"

print(f"Ano: {ano}\nMês: {mes_str}\nDia: {dia_str}")
print("Criando diretório")

# Definir diretório de download
folder_name = 'Base_de_dados'
folder_path = os.path.join(os.getcwd(), folder_name)
if not os.path.exists(folder_path):
    os.makedirs(folder_path)

print("Diretório Criado")

# Configurações do WebDriver
def web_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless")
    options.add_argument("--window-size=1920,1200")
    options.add_experimental_option("prefs", {
        "download.default_directory": folder_path,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": False
    })
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)

# Função para realizar o login no Sintegre
def fazer_login(driver, username, password):
    driver.get("https://sintegre.ons.org.br")
    time.sleep(3)
    username_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "username"))
    )
    username_field.send_keys(username)
    username_field.send_keys(Keys.RETURN)
    time.sleep(1)
    password_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password_field.send_keys(password)
    password_field.send_keys(Keys.RETURN)

# Credenciais de login
username = "joham.albuquerque@bvs2.com.br"
password = "120594jlsA@"

print("Criando wedriver")
# Iniciar o WebDriver e fazer login
driver = web_driver()
print("Iniciando Login")
fazer_login(driver, username, password)
print("Login Feito")

# URL do arquivo PDF
urls = [
    f"https://sintegre.ons.org.br/sites/9/51/_layouts/download.aspx?SourceUrl=/sites/9/51/Produtos/282/REPDOE-{ano}{mes_str}{dia_str}.pdf"
]

# Função para aguardar download completo
def espera_download_completo(downloads_folder, nome_arquivo, timeout=1200):
    tempo_inicial = time.time()
    while True:
        arquivos = os.listdir(downloads_folder)
        if nome_arquivo in arquivos:
            arquivo_path = os.path.join(downloads_folder, nome_arquivo)
            tamanho_inicial = os.path.getsize(arquivo_path)
            time.sleep(1)
            if os.path.getsize(arquivo_path) == tamanho_inicial:
                return True
        if time.time() - tempo_inicial >= timeout:
            return False
        time.sleep(3)

# Download dos arquivos
file_names = [url.split("/")[-1] for url in urls]
for url, nome_arquivo in zip(urls, file_names):
    time.sleep(3) #Adicionado para evitar erro no download
    driver.get(url)
    print(f"{url}")
    if espera_download_completo(folder_path, nome_arquivo):
        print(f"Arquivo {nome_arquivo} baixado")
    else:
        print(f"O tempo limite foi atingido. Download de {nome_arquivo} não concluído.")
driver.quit()

# Extração de parágrafos contendo "Ibiapina" do PDF
def extrair_paragrafos(pdf_path, termo_interesse):
    pdf_document = fitz.open(pdf_path)
    paragrafos_interesse = []
    for page in pdf_document:
        text = page.get_text()
        paragrafos = text.split('\n ')
        for par in paragrafos:
            if termo_interesse in par:
                paragrafos_interesse.append(par)
    return paragrafos_interesse

# Extração da imagem da página que contém o termo "GERAÇÃO EÓLICA E SOLAR PROGRAMADAS (MWMED)"
def extract_chart_from_page_with_fallback(pdf_path, term, rect, zoom=10.0):
    pdf_document = fitz.open(pdf_path)
    for page_num in range(len(pdf_document)):
        page = pdf_document.load_page(page_num)
        text = page.get_text()
        if term in text:
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, clip=rect)
            image_bytes = pix.tobytes("png")
            return Image.open(BytesIO(image_bytes))

    print(f"Termo '{term}' não encontrado. Extraindo imagem da penúltima página.")
    num_pages = len(pdf_document)
    if num_pages < 2:
        print("O PDF não possui páginas suficientes.")
        return None
    page = pdf_document.load_page(num_pages - 2)
    mat = fitz.Matrix(zoom, zoom)
    pix = page.get_pixmap(matrix=mat, clip=rect)
    image_bytes = pix.tobytes("png")
    return Image.open(BytesIO(image_bytes))

# Caminho do PDF e coordenadas para extração
pdf_path = os.path.join(folder_path, file_names[0])
rect = fitz.Rect(37, 440, 550, 605)
termo_busca = "GERAÇÃO EÓLICA E SOLAR PROGRAMADAS (MWMED)"
image = extract_chart_from_page_with_fallback(pdf_path, termo_busca, rect, zoom=10.0)

# Extração dos parágrafos de interesse
termo_interesse = "Ibiapina"
paragrafos_interesse = extrair_paragrafos(pdf_path, termo_interesse)
observacao = f"<p><b>Observação:</b></p><p>{'</p><p>'.join(paragrafos_interesse)}</p>" if paragrafos_interesse else ""

# Define a data de análise
offset_dias = 0
data_analise = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0) - timedelta(days=offset_dias)
diretorio1 = 'https://ons-aws-prod-opendata.s3.amazonaws.com/dataset/programacao_x_previsao/PROGRAMACAO_X_PREVISAO_'
nome_arquivo = data_analise.strftime("%Y_%m_%d") + ".xlsx"
caminho_arquivo = diretorio1 + nome_arquivo

# Tenta ler o arquivo e gerar o gráfico
image_data = None
image_data2 = None
image_data3 = None
try:
    df1 = pd.read_excel(caminho_arquivo)
    df1['Horário'] = (pd.to_timedelta(df1['num_patamar'] * 30, unit='m') % pd.Timedelta(days=1))
    df1['Horário'] = df1['Horário'].apply(lambda x: str(x).split("days")[-1].strip())
    df1['Horário'] = df1['Horário'].str[:5]

    df_cac = df1[df1['nom_usinapdp'].str.startswith('CJE CACIMBAS')].sort_values(by='num_patamar').reset_index(drop=True)
    df_mal = df1[df1['nom_usinapdp'].str.startswith('MALHADINHA1')].sort_values(by='num_patamar').reset_index(drop=True)
    df_sro = df1[df1['nom_usinapdp'].str.startswith('CJSROSALIA')].sort_values(by='num_patamar').reset_index(drop=True)
    
    
    plt.figure(figsize=(12, 6))
    plt.plot(df_cac['Horário'], df_cac['val_previsao'], label='Valor Previsto', marker='o')
    plt.plot(df_cac['Horário'], df_cac['val_programado'], label='Valor Programado', marker='s')
    plt.xlabel('Horário')
    plt.ylabel('Potência (MW)')
    plt.title(f'Programação vs Previsão | Conjunto Cacimbas | {data_analise.strftime("%d/%m/%Y")}')
    plt.ylim(-10, 90)
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    # Salvar Imagem
    image_buffer = BytesIO()
    plt.savefig(image_buffer, format='png')
    plt.close()
    image_data = image_buffer.getvalue()

    plt.figure(figsize=(12, 6))
    plt.plot(df_mal['Horário'], df_mal['val_previsao'], label='Valor Previsto', marker='o')
    plt.plot(df_mal['Horário'], df_mal['val_programado'], label='Valor Programado', marker='s')
    plt.xlabel('Horário')
    plt.ylabel('Potência (MW)')
    plt.title(f'Programação vs Previsão | Conjunto Malhadinha | {data_analise.strftime("%d/%m/%Y")}')
    plt.ylim(-5, 25)
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    # Salvar Imagem
    image_buffer2 = BytesIO()
    plt.savefig(image_buffer2, format='png')
    plt.close()
    image_data2 = image_buffer2.getvalue()

    plt.figure(figsize=(12, 6))
    plt.plot(df_sro['Horário'], df_sro['val_previsao'], label='Valor Previsto', marker='o')
    plt.plot(df_sro['Horário'], df_sro['val_programado'], label='Valor Programado', marker='s')
    plt.xlabel('Horário')
    plt.ylabel('Potência (MW)')
    plt.title(f'Programação vs Previsão | Conjunto Santa Rosália | {data_analise.strftime("%d/%m/%Y")}')
    plt.ylim(-10, 140)
    plt.legend()
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    # Salvar Imagem
    image_buffer3 = BytesIO()
    plt.savefig(image_buffer3, format='png')
    plt.close()
    image_data3 = image_buffer3.getvalue()
    
except Exception as e:
    print(f"Erro ao processar a imagem: {e}")

img_dia = '<p></p><p>O documento programação vs previsão do ONS não está disponível.</p>'
if image_data != None:
    img_dia = '<p></p><p><b>Previsão para o Conj. Cacimbas:</b></p><p></p><img src="cid:image_data" style="width:70%;"><p></p>'
img_dia2 = ''
if image_data2 != None:
    img_dia2 = '<p></p><p><b>Previsão para o Conj. Malhadinha:</b></p><p></p><img src="cid:image_data2" style="width:70%;"><p></p>'
img_dia3 = ''
if image_data3 != None:
    img_dia3 = '<p></p><p><b>Previsão para o Conj. Santa Rosália:</b></p><p></p><img src="cid:image_data3" style="width:70%;"><p></p>'



# Envio de e-mail com a imagem extraída e o PDF anexado
def send_email(image, pdf_path, dia_str, mes_str, ano, observacao, image_data=None, image_data2=None, image_data3=None):
    # Configurações de e-mail
    user = 'notificacoes.bvs2@gmail.com'
    password = 'ruixtyhnyouagbai'
    recipients = ['joham.albuquerque@bvs2.com.br', 'paulo.regis@bvs2.com.br', 'maykel.pinto@bvs2.com.br', 'marcelo.silva@bvs2.com.br']
    cc = ['tfurtado@weg.net', 'operacao.cos@steag.com.br']

    subject = f'Previsão NE - REPDOE - {dia_str}/{mes_str}/{ano}'
    body = f"""
    <html>
    <body>
        <p>Bom dia,</p>
        <p></p>
        <p>Segue a previsão do planejamento diário de operação da região Nordeste para o dia {dia_str}/{mes_str}/{ano}:</p>
        <p></p>
        <p></p>
        <img src="cid:image1" style="width:70%;">
        {img_dia}
        {img_dia2}
        {img_dia3}
        <p></p>
        {observacao}
        <p></p>
        <p>Atenciosamente,</p>
    </body>
    </html>
    """

    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = ', '.join(recipients)
    msg['Cc'] = ', '.join(cc)
    msg['Subject'] = subject

    msg.attach(MIMEText(body, 'html'))  # Alterado para 'html' para suportar a imagem embutida

    # Anexar imagem REPDOE ao corpo do e-mail
    img_buffer = BytesIO()
    image.save(img_buffer, format="PNG")
    img_buffer.seek(0)
    img_part = MIMEImage(img_buffer.read())
    img_part.add_header("Content-ID", "<image1>")
    msg.attach(img_part)

    # Anexar imagem previsão cacimbas ao corpo do e-mail
    if image_data:
        img_cacimbas = MIMEImage(image_data)
        img_cacimbas.add_header("Content-ID", "<image_data>")
        msg.attach(img_cacimbas)

    # Anexar imagem previsão cacimbas ao corpo do e-mail
    if image_data2:
        img_malhadinha = MIMEImage(image_data2)
        img_malhadinha.add_header("Content-ID", "<image_data2>")
        msg.attach(img_malhadinha)

    # Anexar imagem previsão cacimbas ao corpo do e-mail
    if image_data3:
        img_sro = MIMEImage(image_data3)
        img_sro.add_header("Content-ID", "<image_data3>")
        msg.attach(img_sro)

    # Anexar o PDF ao e-mail
    with open(pdf_path, 'rb') as pdf_file:
        attach = MIMEApplication(pdf_file.read(), _subtype="pdf")
        attach.add_header('Content-Disposition', 'attachment', filename=os.path.basename(pdf_path))
        msg.attach(attach)

    # Enviar e-mail
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login(user, password)
        server.sendmail(user, recipients + cc, msg.as_string())

# Exibição da imagem extraída no Jupyter Notebook e envio do e-mail
if image:
    print('Enviando...')
    send_email(image, pdf_path, dia_str, mes_str, ano, observacao, image_data=image_data, image_data2=image_data2, image_data3=image_data3)
    print('Enviado')
else:
    print("Nenhuma área foi extraída como imagem.")

#Parte2
df_cac2 = df_cac.copy()

# Copiar o DataFrame original
df_temp = df_cac2.copy()

# Manter o horário original como string
df_temp['Horário_str'] = df_temp['Horário']

# Converter para datetime (apenas para cálculo)
df_temp['Horário_dt'] = pd.to_datetime(df_temp['Horário_str'], format='%H:%M')

# Verificar divergência
df_temp['diferente'] = df_temp['val_previsao'] != df_temp['val_programado']

# Identificar blocos contínuos
df_temp['grupo'] = (df_temp['diferente'] != df_temp['diferente'].shift()).cumsum()

# Agrupar apenas onde há divergência
grupos = df_temp[df_temp['diferente']].groupby('grupo')

# Gerar os intervalos com strings e datetime
intervalos = grupos.agg(
    horario_inicio_str=('Horário_str', 'first'),
    horario_fim_str=('Horário_str', 'last'),
    horario_inicio_dt=('Horário_dt', 'first'),
    horario_fim_dt=('Horário_dt', 'last'),
    duracao_minutos=('Horário_dt', lambda x: (x.max() - x.min()).seconds // 60)
).reset_index(drop=True)

if len(intervalos)>0:
    # Filtrar intervalos com duração >= 60 minutos
    intervalos_1h = intervalos[intervalos['duracao_minutos'] > 60]
    # Obter o menor horário de início (como string)
    menor_inicio_str = intervalos_1h['horario_inicio_str'].min()
    # Resultado final
    print("Menor horário de início com divergência >= 1 hora:", menor_inicio_str)


if len(intervalos)>0:
    try:
        if len(intervalos_1h)>0:
            def send_email2(dia_str, mes_str, ano, image_data=None):
                # Configurações de e-mail
                user = 'notificacoes.bvs2@gmail.com'
                password = 'ruixtyhnyouagbai'
                recipients = ['tfurtado@weg.net', 'pportela@weg.net', 'joham.albuquerque@bvs2.com.br', 'paulo.regis@bvs2.com.br', 'maykel.pinto@bvs2.com.br', 'marcelo.silva@bvs2.com.br']
                cc = ['']
            
                subject = f'Adiantamento das Manutenções - {dia_str}/{mes_str}/{ano} | Previsão de Curtailment'
                body = f"""
                <html>
                  <body>
                    <p>Thyago,</p>
                    <p>Bom dia.</p>
                    <p></p>
                    <p>Conforme a previsão de limitações de potência para hoje ({dia_str}/{mes_str}/{ano}), as manutenções podem ser adiantadas a partir das <b>{menor_inicio_str} horas</b>:</p>
                    <p></p>
                    <p></p>
                    {img_dia}
                    <p></p>
                    <p>Atenciosamente,</p>
                  </body>
                </html>
                """
            
                msg = MIMEMultipart()
                msg['From'] = user
                msg['To'] = ', '.join(recipients)
                msg['Cc'] = ', '.join(cc)
                msg['Subject'] = subject
            
                msg.attach(MIMEText(body, 'html'))  # Alterado para 'html' para suportar a imagem embutida
                
                # Anexar imagem previsão cacimbas ao corpo do e-mail
                if image_data:
                    img_cacimbas = MIMEImage(image_data)
                    img_cacimbas.add_header("Content-ID", "<image_data>")
                    msg.attach(img_cacimbas)
            
                # Enviar e-mail
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(user, password)
                    server.sendmail(user, recipients + cc, msg.as_string())
            
            print('Enviando...')
            send_email2(dia_str, mes_str, ano, image_data=image_data)
            print('Enviado')
    except:
        if len(intervalos_1h)>0:
            def send_email2(dia_str, mes_str, ano, image_data=None):
                # Configurações de e-mail
                user = 'notificacoes.bvs2@gmail.com'
                password = 'ruixtyhnyouagbai'
                recipients = ['tfurtado@weg.net', 'pportela@weg.net', 'joham.albuquerque@bvs2.com.br', 'paulo.regis@bvs2.com.br', 'maykel.pinto@bvs2.com.br', 'marcelo.silva@bvs2.com.br']
                cc = ['']
            
                subject = f'Adiantamento das Manutenções - {dia_str}/{mes_str}/{ano} | Previsão de Curtailment'
                body = f"""
                <html>
                  <body>
                    <p>Thyago,</p>
                    <p>Bom dia.</p>
                    <p></p>
                    <p>Conforme a previsão de limitações de potência para hoje ({dia_str}/{mes_str}/{ano}), as manutenções <b>não poderão ser adiantadas hoje</b>:</p>
                    <p></p>
                    <p></p>
                    {img_dia}
                    <p></p>
                    <p>Atenciosamente,</p>
                  </body>
                </html>
                """
            
                msg = MIMEMultipart()
                msg['From'] = user
                msg['To'] = ', '.join(recipients)
                msg['Cc'] = ', '.join(cc)
                msg['Subject'] = subject
            
                msg.attach(MIMEText(body, 'html'))  # Alterado para 'html' para suportar a imagem embutida
                
                # Anexar imagem previsão cacimbas ao corpo do e-mail
                if image_data:
                    img_cacimbas = MIMEImage(image_data)
                    img_cacimbas.add_header("Content-ID", "<image_data>")
                    msg.attach(img_cacimbas)
            
                # Enviar e-mail
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(user, password)
                    server.sendmail(user, recipients + cc, msg.as_string())
            
            print('Enviando...')
            send_email2(dia_str, mes_str, ano, image_data=image_data)
            print('Enviado')
if len(intervalos)==0:
            def send_email2(dia_str, mes_str, ano, image_data=None):
                # Configurações de e-mail
                user = 'notificacoes.bvs2@gmail.com'
                password = 'ruixtyhnyouagbai'
                recipients = ['tfurtado@weg.net', 'pportela@weg.net', 'joham.albuquerque@bvs2.com.br', 'paulo.regis@bvs2.com.br', 'maykel.pinto@bvs2.com.br', 'marcelo.silva@bvs2.com.br']
                cc = ['']
            
                subject = f'Adiantamento das Manutenções - {dia_str}/{mes_str}/{ano} | Previsão de Curtailment'
                body = f"""
                <html>
                  <body>
                    <p>Thyago,</p>
                    <p>Bom dia.</p>
                    <p></p>
                    <p>Conforme a previsão de limitações de potência para hoje ({dia_str}/{mes_str}/{ano}), as manutenções <b>não poderão ser adiantadas hoje</b>:</p>
                    <p></p>
                    <p></p>
                    {img_dia}
                    <p></p>
                    <p>Atenciosamente,</p>
                  </body>
                </html>
                """
            
                msg = MIMEMultipart()
                msg['From'] = user
                msg['To'] = ', '.join(recipients)
                msg['Cc'] = ', '.join(cc)
                msg['Subject'] = subject
            
                msg.attach(MIMEText(body, 'html'))  # Alterado para 'html' para suportar a imagem embutida
                
                # Anexar imagem previsão cacimbas ao corpo do e-mail
                if image_data:
                    img_cacimbas = MIMEImage(image_data)
                    img_cacimbas.add_header("Content-ID", "<image_data>")
                    msg.attach(img_cacimbas)
            
                # Enviar e-mail
                with smtplib.SMTP('smtp.gmail.com', 587) as server:
                    server.starttls()
                    server.login(user, password)
                    server.sendmail(user, recipients + cc, msg.as_string())
            
            print('Enviando...')
            send_email2(dia_str, mes_str, ano, image_data=image_data)
            print('Enviado')
