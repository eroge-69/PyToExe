import os
import shutil
from datetime import datetime

# --- Configurações ---
users_base_path = 'C:\\Users'
organized_downloads_folder_name = os.path.expanduser('~/Documents')

# Mapeamento de extensões de arquivo para nomes de pastas
file_types = {
    'Xml': ['.xml'],
    'DLL': ['.dll'],
    'Relatorio': ['.fr3'],
    'Certificados': ['.pfx'],
    'Imagens': ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', '.webp'],
    'Vídeos': ['.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv'],
    'Músicas': ['.mp3', '.wav', '.flac', '.aac', '.ogg'],
    'Documentos': ['.pdf', '.doc', '.docx', '.txt', '.ppt', '.pptx'],
    'Planilhas': ['.csv', '.xlsx', '.xls'],
    'Apresentações': ['.ppt', '.pptx'],
    'Compactados': ['.zip', '.rar', '.7z', '.tar', '.gz'],
    'Programas': ['.exe', '.msi', '.dmg', '.pkg'],
    'Desconhecido': []
}

# Nomes dos meses em português para as pastas
month_names = {
    1: 'Jan', 2: 'Fev', 3: 'Mar', 4: 'Abr', 5: 'Mai', 6: 'Jun',
    7: 'Jul', 8: 'Ago', 9: 'Set', 10: 'Out', 11: 'Nov', 12: 'Dez'
}

# --- Função Principal de Organização ---
def organize_downloads_for_all_users():
    print(f"Buscando pastas de usuário em '{users_base_path}'...")
    
    for user_folder in os.listdir(users_base_path):
        if user_folder in ['All Users', 'Default', 'Default User', 'Public'] or os.path.islink(os.path.join(users_base_path, user_folder)):
            continue

        user_path = os.path.join(users_base_path, user_folder)
        downloads_folder = os.path.join(user_path, 'Downloads')
        documents_folder = os.path.join(user_path, 'Documents')

        if not os.path.exists(downloads_folder) or not os.path.exists(documents_folder):
            print(f"\nPastas de Downloads ou Documentos não encontradas para o usuário '{user_folder}'. Ignorando.")
            continue

        print(f"\nIniciando a organização para o usuário: '{user_folder}'")
        
        destination_base = os.path.join(documents_folder, organized_downloads_folder_name)
        if not os.path.exists(destination_base):
            os.makedirs(destination_base)
            print(f"Pasta de destino '{destination_base}' criada.")

        for filename in os.listdir(downloads_folder):
            source_path = os.path.join(downloads_folder, filename)

            if os.path.isdir(source_path) or os.path.islink(source_path):
                continue

            file_extension = os.path.splitext(filename)[1].lower()

            # --- Lógica de organização por data ---
            try:
                # Obtém a data de modificação do arquivo
                timestamp = os.path.getmtime(source_path)
                modification_date = datetime.fromtimestamp(timestamp)
                
                # Extrai o ano e o mês
                year = str(modification_date.year)
                month = month_names.get(modification_date.month, str(modification_date.month))
            except Exception as e:
                print(f"Não foi possível obter a data de modificação para '{filename}'. Usando data atual. Erro: {e}")
                now = datetime.now()
                year = str(now.year)
                month = month_names.get(now.month, str(now.month))
            
            # Encontra a pasta de destino por tipo
            destination_folder_by_type = 'Outros'
            for folder, extensions in file_types.items():
                if file_extension in extensions:
                    destination_folder_by_type = folder
                    break

            # Cria a estrutura de pastas: Tipo -> Ano -> Mês
            destination_path = os.path.join(destination_base, destination_folder_by_type, year, month)
            
            # Cria a pasta se ela não existir
            if not os.path.exists(destination_path):
                os.makedirs(destination_path)

            # Move o arquivo
            try:
                shutil.move(source_path, os.path.join(destination_path, filename))
                print(f"Arquivo '{filename}' movido para '{destination_folder_by_type}\\{year}\\{month}'.")
            except shutil.Error as e:
                print(f"Erro ao mover o arquivo '{filename}': {e}")
            except Exception as e:
                print(f"Ocorreu um erro inesperado: {e}")

    print("\nOrganização concluída para todos os usuários!")

# Executa a função
if __name__ == "__main__":
    organize_downloads_for_all_users()