
import os
import shutil
from pathlib import Path
from datetime import datetime

# 📂 Caminho da pasta com as fotos originais
pasta_origem = Path("/Users/teu_utilizador/Imagens/FotosOriginais")  # <- Muda aqui
# 📂 Pasta onde as fotos organizadas vão ser guardadas
pasta_destino = Path("/Users/teu_utilizador/Imagens/FotosOrganizadas")  # <- Muda aqui

# Criar pasta de destino se não existir
pasta_destino.mkdir(parents=True, exist_ok=True)

# Verifica todos os ficheiros na pasta origem
for ficheiro in pasta_origem.glob("*"):
    if ficheiro.is_file():
        # Usa a data de modificação como fallback
        timestamp = ficheiro.stat().st_mtime
        data = datetime.fromtimestamp(timestamp)

        ano = str(data.year)
        mes = f"{data.month:02d}"

        # Criar subpastas por ano/mês
        destino = pasta_destino / ano / mes
        destino.mkdir(parents=True, exist_ok=True)

        # Copiar ou mover o ficheiro (mudar para `shutil.move` se preferires)
        shutil.copy2(ficheiro, destino / ficheiro.name)

print("✅ Organização concluída!")
