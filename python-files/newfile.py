import os
import zipfile
from pathlib import Path

def extract_sub_archives(main_archive_path, target_dir):
    
    os.makedirs(target_dir, exist_ok=True)
    
    
    temp_dir = os.path.join(target_dir, "_temp")
    os.makedirs(temp_dir, exist_ok=True)
    
    print(f"Распаковываю главный архив: {main_archive_path}")
    
    try:
       
        with zipfile.ZipFile(main_archive_path, 'r') as zip_ref:
            zip_ref.extractall(temp_dir)
        print("Главный архив успешно распакован")
        
        
        sub_archives = []
        for root, _, files in os.walk(temp_dir):
            for file in files:
                if file.lower().endswith('.zip'):
                    sub_archives.append(os.path.join(root, file))
        
        print(f"Найдено {len(sub_archives)} вложенных архивов")
        
        
        for i, archive_path in enumerate(sub_archives[:300], 1):
           
            folder_name = os.path.splitext(os.path.basename(archive_path))[0]
            extract_path = os.path.join(target_dir, folder_name)
            os.makedirs(extract_path, exist_ok=True)
            
            print(f"{i}. Распаковываю {os.path.basename(archive_path)} в {extract_path}")
            
            try:
                with zipfile.ZipFile(archive_path, 'r') as zip_ref:
                    zip_ref.extractall(extract_path)
            except Exception as e:
                print(f"Ошибка при распаковке {archive_path}: {str(e)}")
        
       
        for root, dirs, files in os.walk(temp_dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(temp_dir)
        
    except Exception as e:
        print(f"Ошибка при обработке главного архива: {str(e)}")

if __name__ == "__main__":
    
    main_archive_path = str(Path("C:/Users/proh/Downloads/300 рп.zip"))
    
    
    target_directory = str(Path("C:/Nursultan/1.16.5/resourcepacks"))
    
    print("Начало обработки...")
    print(f"Главный архив: {main_archive_path}")
    print(f"Целевая папка: {target_directory}")
    
    extract_sub_archives(main_archive_path, target_directory)
    
    print("Все архивы успешно распакованы!")
    print(f"Ресурс-паки находятся в: {target_directory}")