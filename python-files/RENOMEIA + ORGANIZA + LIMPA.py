import os
import shutil
import datetime
import win32com.client as win32

# --- CONFIGURAÇÃO PRINCIPAL ---

# 1. Defina a pasta de origem onde os arquivos são salvos
pasta_origem = 'T:\\'

# 2. Defina a pasta de DESTINO RAIZ final para onde os arquivos serão movidos
pasta_destino_raiz = r'C:\Users\guilherme.omartins\OneDrive - SADACORP\GOM\SEMPRE EDITORA\BANCO DE DADOS\DATASUL - CITRIX'

# 3. Defina os relatórios e suas pastas de destino.
relatorios_e_destinos = {
    "CE0302": "CE0302 - LISTAGEM MOVIMENTO ESTOQUE",
    "CE0919": "CE0919 - LISTAGEM SALDO FISICO ITENS",
    "CE0403": "CE0403 - DIARIO AUXILIAR ESTOQUE"
}

# 4. Defina o nome da pasta para arquivar os arquivos restantes
pasta_outros_nome = "1 - OUTROS ARQUIVOS"
pasta_outros_caminho = os.path.join(pasta_destino_raiz, pasta_outros_nome)

# --- INÍCIO DA EXECUÇÃO ---
print(f"Iniciando organização de relatórios...")
print(f"Origem: '{pasta_origem}'")
print(f"Destino: '{pasta_destino_raiz}'")
print("-" * 60)

excel = None  # Inicializa a variável do Excel

try:
    os.makedirs(pasta_outros_caminho, exist_ok=True)
    lista_de_arquivos = os.listdir(pasta_origem)

    for filename in lista_de_arquivos:
        caminho_completo_origem = os.path.join(pasta_origem, filename)
        
        if not os.path.isfile(caminho_completo_origem):
            continue

        print(f"\nAnalisando arquivo: '{filename}'")
        destino_encontrado = False

        for codigo, nome_pasta_destino in relatorios_e_destinos.items():
            if filename.lower().startswith(codigo.lower()):
                try:
                    caminho_pasta_destino = os.path.join(pasta_destino_raiz, nome_pasta_destino)
                    os.makedirs(caminho_pasta_destino, exist_ok=True)

                    nome_base = os.path.splitext(filename)[0]
                    timestamp_modificacao = os.path.getmtime(caminho_completo_origem)
                    data_formatada = datetime.datetime.fromtimestamp(timestamp_modificacao).strftime("%d-%m-%Y")
                    nome_final_arquivo = f"{nome_base} - {data_formatada}.xlsx"
                    caminho_final_destino = os.path.join(caminho_pasta_destino, nome_final_arquivo)
                    
                    if filename.lower().endswith('.xml'):
                        print(f"  -> Automatizando o Excel para converter '{filename}'...")

                        # Garante que os caminhos são absolutos
                        xml_abs_path = os.path.abspath(caminho_completo_origem)
                        xlsx_abs_path = os.path.abspath(caminho_final_destino)

                        # Inicia o Excel em segundo plano
                        excel = win32.gencache.EnsureDispatch('Excel.Application')
                        excel.Visible = False
                        excel.DisplayAlerts = False # Impede pop-ups de travar o script

                        # Manda o Excel abrir o arquivo XML
                        workbook = excel.Workbooks.Open(xml_abs_path)
                        
                        # Manda o Excel salvar como .xlsx (formato 51)
                        workbook.SaveAs(xlsx_abs_path, FileFormat=51)
                        
                        workbook.Close(SaveChanges=False)
                        
                        os.remove(caminho_completo_origem)
                        print(f"  -> SUCESSO: Convertido via Excel e salvo como '{nome_final_arquivo}'.")

                    elif filename.lower().endswith(('.xlsx', '.xls')):
                        shutil.move(caminho_completo_origem, caminho_final_destino)
                        print(f"  -> SUCESSO: Renomeado e movido.")
                    
                    destino_encontrado = True
                    break

                except Exception as e:
                    print(f"  -> FALHA ao processar '{filename}'. Motivo: {e}")
                    destino_encontrado = True
                    break
        
        if not destino_encontrado:
            shutil.move(caminho_completo_origem, os.path.join(pasta_outros_caminho, filename))
            print(f"  -> AVISO: Movido para '{pasta_outros_nome}'.")

finally:
    # Garante que o processo do Excel seja fechado no final, mesmo que ocorra um erro
    if excel:
        excel.Quit()
    print("-" * 60)
    print("\nProcesso finalizado.")
    input("\nPressione Enter para fechar...")