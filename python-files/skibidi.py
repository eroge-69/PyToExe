import os
import requests
import subprocess
import tempfile

def download_from_gdrive(url, output_path):
    """Скачивает файл с Google Drive"""
    # Если это обычная ссылка на Google Drive
    if "drive.google.com" in url:
        file_id = url.split('/d/')[1].split('/')[0]
        url = f"https://drive.google.com/uc?export=download&id={file_id}"
    
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(output_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)

def play_audio(file_path):
    """Воспроизводит аудио в отдельном окне"""
    try:
        if os.name == 'nt':  # Windows
            subprocess.Popen(['start', file_path], shell=True)
        else:  # Mac/Linux
            subprocess.Popen(['xdg-open', file_path])
    except Exception as e:
        print(f"Ошибка воспроизведения: {e}")

def main():
    # Укажите свою ссылку на Google Drive здесь
    gdrive_url = "https://drive.google.com/file/d/1ZuQtNag-ejEFVf52B-nh1NYtwmFOEqhH/view?usp=drive_link"
    
    # Создаем временный файл
    temp_dir = tempfile.gettempdir()
    audio_file = os.path.join(temp_dir, "HACKED.mp3")
    
    try:
        print("Делаем несколько вещей...")
        download_from_gdrive(gdrive_url, audio_file)
        
        print("Готово!")
        play_audio(audio_file)
        
        # Программа завершится, но аудио продолжит играть в отдельном окне
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        # Файл не удаляется, чтобы аудио могло играть
        pass

if __name__ == "__main__":
    main()