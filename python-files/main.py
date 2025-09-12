import re
import configparser
import os

# Ler ficheiro de configuração
config = configparser.ConfigParser()
config.read("config.config", encoding="utf-8")  # o config.ini é sempre UTF-8

ficheiro_entrada = config["DEFAULT"]["ficheiro_entrada"]
ficheiro_saida = config["DEFAULT"]["ficheiro_saida"]
encoding_ficheiro = config["DEFAULT"]["encoding_ficheiro"]
folder_base = config["DEFAULT"].get("folder_base", os.getcwd())

os.chdir(folder_base)

# Ler ficheiro de entrada
with open(ficheiro_entrada, "r", encoding=encoding_ficheiro) as f:
    conteudo = f.read()

# 1. Remove blocos { ... }
conteudo = re.sub(r"\{.*?\}\s*", "", conteudo, flags=re.DOTALL)

# 2. Remove linhas grant/revoke
conteudo = re.sub(r"(?mi)^\s*(grant|revoke).*?$", "", conteudo)

# 3. Remove extent/next size/lock mode
conteudo = re.sub(
    r"extent size \d+ next size \d+ lock mode \w+;?", 
    ";", 
    conteudo, 
    flags=re.IGNORECASE
)

# 4. Limpar linhas vazias múltiplas
conteudo = re.sub(r"\n\s*\n+", "\n\n", conteudo)

# Gravar resultado
with open(ficheiro_saida, "w", encoding=encoding_ficheiro) as f:
    f.write(conteudo.strip() + "\n")

print(f"Esquema limpo gravado em {ficheiro_saida}")
