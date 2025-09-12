import re

ficheiro_entrada = "gba.sql"

ficheiro_saida = "gba_tratado.sql"

with open(ficheiro_entrada, "r",  encoding="latin-1") as f:
    conteudo = f.read()

# 1. Remove blocos { ... }
conteudo = re.sub(r"\{.*?\}\s*", "", conteudo, flags=re.DOTALL)

# 2. Remove linhas grant/revoke
conteudo = re.sub(r"(?mi)^\s*(grant|revoke).*?$", "", conteudo)

# 3. Remove extent/next size/lock mode
conteudo = re.sub(r"extent size \d+ next size \d+ lock mode \w+;?", ";", conteudo, flags=re.IGNORECASE)

# 4. Limpar linhas vazias múltiplas
conteudo = re.sub(r"\n\s*\n+", "\n\n", conteudo)

with open(ficheiro_saida, "w",  encoding="latin-1") as f:
    f.write(conteudo.strip() + "\n")

print(f"Esquema limpo gravado em {ficheiro_saida}")
