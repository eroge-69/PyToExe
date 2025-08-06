import os
import shutil
import re
from PyPDF2 import PdfReader

def extrair_protocolo(caminho_pdf):
    reader = PdfReader(caminho_pdf)
    for page in reader.pages:
        texto = page.extract_text()
        match = re.search(r'Protocolo\s+(\d{11}-\d{2})', texto)
        if match:
            return match.group(1)
    return None

USUARIO_DIR = os.path.expanduser('~')
source_folder = os.path.join(USUARIO_DIR, 'Downloads')
destination_folder = os.path.join(USUARIO_DIR, 'Documents', 'atendimento_pdf_logfly')

nome_arquivo = 'Conversa.pdf.pdf'
caminho_origem = os.path.join(source_folder, nome_arquivo)

if os.path.exists(caminho_origem):
    protocolo = extrair_protocolo(caminho_origem)

    if protocolo:
        protocolo_sem_hifen = protocolo.replace('-', '')

        os.makedirs(destination_folder, exist_ok=True)

        novo_nome = f'{protocolo_sem_hifen}.pdf'
        caminho_destino = os.path.join(destination_folder, novo_nome)
        shutil.move(caminho_origem, caminho_destino)
        print(f'Arquivo movido e renomeado para: {caminho_destino}')
    else:
        print('Protocolo não encontrado no PDF.')
else:
    print(f'Arquivo {nome_arquivo} não encontrado em {source_folder}.')
