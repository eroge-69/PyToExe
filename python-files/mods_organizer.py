import os
import shutil
import xml.etree.ElementTree as ET

# Mapea categorías a funciones de detección
CATEGORIES = {
    'CAS':       lambda name: 'CAS' in name.upper(),
    'BuildBuy':  lambda name: any(k in name.upper() for k in ('BB','BUILD','BUY')),
    'Overrides': lambda path: 'override' in path.lower(),
    'ScriptMods':lambda name: name.endswith('.ts4script'),
}

# Carpetas destino
DEST_FOLDERS = ['CAS', 'BuildBuy', 'Overrides', 'ScriptMods', 'Genérico', 'Otros']

def crear_carpetas(base):
    """Crea las subcarpetas de destino si no existen."""
    for d in DEST_FOLDERS:
        os.makedirs(os.path.join(base, d), exist_ok=True)

def clasificar_archivo(src_path, base_dest):
    """Devuelve la ruta destino según la categoría del archivo."""
    filename = os.path.basename(src_path)
    dest_cat = None

    # Comprueba cada categoría
    for cat, check in CATEGORIES.items():
        # Algunas funciones usan ruta completa, otras solo el nombre
        arg = src_path if 'path' in check.__code__.co_varnames else filename
        if check(arg):
            dest_cat = cat
            break

    # Si no encaja en ninguna, decide Genérico u Otros
    if not dest_cat:
        ext = os.path.splitext(filename)[1].lower()
        dest_cat = 'Genérico' if ext in ('.package', '.zip') else 'Otros'

    return os.path.join(base_dest, dest_cat, filename)

def detectar_daño(path):
    """Detecta problemas: archivo vacío o XML mal formado."""
    if os.path.getsize(path) == 0:
        return 'Archivo vacío'
    if path.lower().endswith('.xml'):
        try:
            ET.parse(path)
        except ET.ParseError:
            return 'XML mal formado'
    return None

def organizar_mods(src_folder, dest_root):
    """Copia y organiza todos los mods, devolviendo un informe."""
    crear_carpetas(dest_root)
    informe = []

    for root, _, files in os.walk(src_folder):
        for f in files:
            src = os.path.join(root, f)
            issue = detectar_daño(src)
            dest = clasificar_archivo(src, dest_root)
            shutil.copy2(src, dest)
            informe.append({
                'archivo': f,
                'categoría': os.path.basename(os.path.dirname(dest)),
                'issue': issue or 'OK'
            })

    return informe

def guardar_informe(informe, path):
    """Guarda el informe en formato CSV."""
    with open(path, 'w', encoding='utf-8') as log:
        log.write('Archivo,Categoría,Problema\n')
        for i in informe:
            log.write(f"{i['archivo']},{i['categoría']},{i['issue']}\n")

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Organizador de Mods para Los Sims 4')
    parser.add_argument('-m', '--mods', required=True, help='Ruta a la carpeta Mods original')
    parser.add_argument('-o', '--out', required=True, help='Ruta a la carpeta de salida organizada')
    args = parser.parse_args()

    informe = organizar_mods(args.mods, args.out)
    informe_path = os.path.join(args.out, 'informe_mods.csv')
    guardar_informe(informe, informe_path)
    print(f'Organización completada. Informe generado en:\n  {informe_path}')