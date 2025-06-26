import re
import os
from collections import defaultdict

def get_files_in_directory(directory):
    """Encuentra los archivos .txt necesarios en el directorio del script."""
    try:
        files = [f for f in os.listdir(directory) if f.endswith('.txt')]
        database_file = "both.txt"
        
        if database_file not in files:
            return None, None, f"Error: No se encontró el archivo de base de datos '{database_file}'."

        files.remove(database_file)
        
        if len(files) == 0:
            return None, None, "Error: No se encontró ningún otro archivo .txt para analizar."
        if len(files) > 1:
            return None, None, f"Error: Se encontró más de un archivo .txt para analizar. Solo debe haber uno además de '{database_file}'."

        source_file = files[0]
        return os.path.join(directory, database_file), os.path.join(directory, source_file), None

    except Exception as e:
        return None, None, f"Error al buscar los archivos: {e}"

def extract_data_from_log(file_path):
    """Extrae IPs y AUTHs de un archivo de log."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except FileNotFoundError:
        return None, None
    except Exception as e:
        print(f"Error al leer el archivo {file_path}: {e}")
        return None, None

    ip_pattern = re.compile(r"IP: (\S+)")
    auth_pattern = re.compile(r"AUTH: (\S+)")

    ips = set(ip_pattern.findall(content))
    auths = set(auth_pattern.findall(content))

    return ips, auths

def find_matches_in_file(file_to_search, database_ips, database_auths):
    """Encuentra IPs y AUTHs del archivo a verificar en la base de datos."""
    try:
        with open(file_to_search, 'r', encoding='utf-8') as f:
            content_to_search = f.read()
    except Exception as e:
        print(f"Error al leer el archivo a verificar {file_to_search}: {e}")
        return None, None

    found_ips = set()
    found_auths = set()

    for ip in database_ips:
        if ip in content_to_search:
            found_ips.add(ip)

    for auth in database_auths:
        if auth in content_to_search:
            found_auths.add(auth)

    return found_ips, found_auths

def main():
    """Función principal del programa."""
    print("="*50)
    print("      Analizador de Coincidencias de Jugadores")
    print("="*50)

    script_directory = os.path.dirname(os.path.abspath(__file__))

    # --- Detectar archivos automáticamente ---
    database_path, source_path, error = get_files_in_directory(script_directory)

    if error:
        print(f"\n[!] {error}")
        input("\nPresiona Enter para salir.")
        return

    print(f"\n[*] Base de datos detectada: {os.path.basename(database_path)}")
    print(f"[*] Archivo de ingresos a analizar: {os.path.basename(source_path)}")

    # --- Extraer datos de la base de datos ---
    print(f"\n[*] Analizando la base de datos...")
    db_ips, db_auths = extract_data_from_log(database_path)

    if db_ips is None:
        print("[!] No se pudo procesar el archivo de base de datos. Saliendo.")
        return

    print(f"[*] Se han extraído {len(db_ips)} IPs y {len(db_auths)} AUTHs únicos de la base de datos.")

    # --- Encontrar coincidencias en el archivo de ingresos ---
    print(f"\n[*] Buscando coincidencias en {os.path.basename(source_path)}...")
    found_ips, found_auths = find_matches_in_file(source_path, db_ips, db_auths)

    # --- Mostrar resultados ---
    print("\n" + "="*20 + " RESULTADOS " + "="*20)

    if not found_ips and not found_auths:
        print("\n[✅] No se encontraron coincidencias de IP o AUTH.")
    else:
        if found_ips:
            print(f"\n[!] Se encontraron {len(found_ips)} IPs coincidentes:")
            for ip in sorted(list(found_ips)):
                print(f"  - IP: {ip}")
        
        if found_auths:
            print(f"\n[!] Se encontraron {len(found_auths)} AUTHs coincidentes:")
            for auth in sorted(list(found_auths)):
                print(f"  - AUTH: {auth}")

    print("\n" + "="*52)
    input("[*] Análisis completado. Presiona Enter para salir.")


if __name__ == "__main__":
    main()