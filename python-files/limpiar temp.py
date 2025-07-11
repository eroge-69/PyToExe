import os
import shutil
import tempfile
import getpass

def delete_temp_files():
    temp_dir = tempfile.gettempdir()
    print(f"Eliminando archivos temporales en: {temp_dir}")
    try:
        for root, dirs, files in os.walk(temp_dir):
            for name in files:
                try:
                    file_path = os.path.join(root, name)
                    os.remove(file_path)
                except Exception:
                    pass
            for name in dirs:
                try:
                    dir_path = os.path.join(root, name)
                    shutil.rmtree(dir_path, ignore_errors=True)
                except Exception:
                    pass
        print("Archivos temporales eliminados.")
    except Exception as e:
        print(f"Error al eliminar archivos temporales: {e}")

def delete_browser_cache():
    user = getpass.getuser()
    chrome_cache = os.path.join(os.getenv('LOCALAPPDATA'), 'Google', 'Chrome', 'User Data', 'Default', 'Cache')
    edge_cache = os.path.join(os.getenv('LOCALAPPDATA'), 'Microsoft', 'Edge', 'User Data', 'Default', 'Cache')

    for browser, path in [('Chrome', chrome_cache), ('Edge', edge_cache)]:
        if os.path.exists(path):
            print(f"Eliminando caché de {browser} en: {path}")
            try:
                shutil.rmtree(path, ignore_errors=True)
                print(f"Caché de {browser} eliminada.")
            except Exception as e:
                print(f"No se pudo eliminar la caché de {browser}: {e}")
        else:
            print(f"No se encontró la caché de {browser}.")

if __name__ == "__main__":
    print("Iniciando limpieza del sistema...")
    delete_temp_files()
    delete_browser_cache()
    print("Limpieza completada.")


