import os
import shutil
import subprocess
import time

# Caminho do diretório onde está o TLauncher renomeado
caminho = r".\MinecraftPortable"
nome_arquivo_oculto = "om"
nome_temporario = "TLauncher_temp.exe"

# Caminho completo
caminho_oculto = os.path.join(caminho, nome_arquivo_oculto)
caminho_temp = os.path.join(caminho, nome_temporario)

# Verificação simples (substitua por planilha ou URL depois)
autorizado = True

if autorizado:
    print("Permitido. Iniciando o Minecraft...")

    # Copia com o nome temporário
    shutil.copyfile(caminho_oculto, caminho_temp)

    # Executa o arquivo temporário
    processo = subprocess.Popen(caminho_temp)
    print("Minecraft Iniciado")

    # Aguarda alguns segundos antes de tentar remover (ou pode aguardar o processo terminar)
    time.sleep(30)

    # Opcional: esperar o processo terminar para deletar
    processo.wait()

    # Remove o executável temporário para evitar acesso indevido
    try:
        os.remove(caminho_temp)
        # print("TLauncher removido com sucesso após execução.")
    except Exception as e:
        print("Problemas ao executar rm", e)
else:
    print("Minecraft bloqueado no momento.")
