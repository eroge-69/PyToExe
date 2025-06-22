import os

def rename_signed_files(directory_path):
    if not os.path.isdir(directory_path):
        print(f"Error: La ruta \'{directory_path}\' no es un directorio válido.")
        return

    for filename in os.listdir(directory_path):
        if "_signed" in filename:
            base_name, extension = os.path.splitext(filename)
            
            if "_signed" in base_name:
                new_base_name = base_name.replace("_signed", "_F")
                new_filename = new_base_name + extension
                
                old_filepath = os.path.join(directory_path, filename)
                new_filepath = os.path.join(directory_path, new_filename)
                
                if old_filepath != new_filepath:
                    try:
                        os.rename(old_filepath, new_filepath)
                        print(f"Renombrado: {filename} -> {new_filename}")
                    except OSError as e:
                        print(f"Error al renombrar {filename}: {e}")

if __name__ == "__main__":
    user_path = input("Por favor, introduce la ruta del directorio a procesar: ")
    rename_signed_files(user_path)
    print("Proceso completado.")


