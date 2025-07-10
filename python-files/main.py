import os
import shutil

source_directory = 'C:\\M-2025-1361'  # Zastąp ścieżką do katalogu źródłowego
destination_directory = 'C:\\M-2025-1361_kopia' # Zastąp ścieżką do katalogu docelowego

if os.path.exists(source_directory):
    try:
        shutil.copytree(source_directory, destination_directory)
        print(f"Katalog '{source_directory}' został pomyślnie skopiowany do '{destination_directory}'.")
    except shutil.Error as e:
        print(f"Błąd podczas kopiowania katalogu: {e}")
    except OSError as e:
        print(f"Błąd systemu operacyjnego podczas kopiowania: {e}")
else:
    print(f"Katalog '{source_directory}' nie istnieje.")