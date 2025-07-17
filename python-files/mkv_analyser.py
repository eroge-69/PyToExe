import subprocess
import json
import os
import sys

def analisar_mkv(caminho):
    caminho = caminho.strip('{').strip('}')
    if not caminho.lower().endswith('.mkv') or not os.path.exists(caminho):
        resultado_text.set("❌ Arquivo inválido ou não encontrado.")
        return

    # Tenta montar caminho do mkvmerge na mesma pasta do exe
    if getattr(sys, 'frozen', False):
        # Se empacotado com PyInstaller
        base_path = sys._MEIPASS
        exe_dir = os.path.dirname(sys.executable)
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
        exe_dir = base_path

    mkvmerge_path = os.path.join(exe_dir, 'mkvmerge.exe')

    if os.path.isfile(mkvmerge_path):
        cmd = [mkvmerge_path, '-J', caminho]
    else:
        # fallback para mkvmerge no PATH
        cmd = ['mkvmerge', '-J', caminho]

    try:
        resultado = subprocess.run(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        dados = json.loads(resultado.stdout)
        tracks = dados.get("tracks", [])

        output = f"📁 {os.path.basename(caminho)}\n\n"
        tipos = {'video': [], 'audio': [], 'subtitles': []}

        for track in tracks:
            tipo = track["type"]
            id_ = track["id"]
            lang = track["properties"].get("language", "und")
            dur = track["properties"].get("duration", None)
            nome = track["properties"].get("track_name", "")

            dur = round(dur) if dur else "N/A"
            nome = f" ({nome})" if nome else ""

            if tipo in tipos:
                tipos[tipo].append(f"ID {id_} - {lang} - Duração: {dur} ms{nome}")

        for cat, itens in tipos.items():
            output += f"=== {cat.upper()} ===\n" + "\n".join(itens or ["(nenhuma)"]) + "\n\n"

        resultado_text.set(output)

    except Exception as e:
        resultado_text.set(f"❌ Erro: {e}")
