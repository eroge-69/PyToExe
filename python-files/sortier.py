import os
import shutil
from pyfiglet import Figlet
from colorama import Fore, Style, init

init(autoreset=True)

ascii_banner = f'''
{Fore.RED} ░▒▓███████▓▒░░▒▓██████▓▒░░▒▓███████▓▒░▒▓████████▓▒░▒▓█▓▒░▒▓████████▓▒░▒▓███████▓▒░  
{Fore.YELLOW}░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░   ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
{Fore.GREEN}░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░   ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
{Fore.RED} ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓███████▓▒░  ░▒▓█▓▒░   ░▒▓█▓▒░▒▓██████▓▒░ ░▒▓███████▓▒░  
{Fore.YELLOW}       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░   ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
{Fore.GREEN}       ░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░   ░▒▓█▓▒░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░ 
{Fore.RED}░▒▓███████▓▒░ ░▒▓██████▓▒░░▒▓█▓▒░░▒▓█▓▒░ ░▒▓█▓▒░   ░▒▓█▓▒░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░ 
{Style.RESET_ALL}                                                                                   
'''

VIDEO_EXT = {".mp4", ".mov", ".avi", ".mkv", ".webm"}
IMAGE_EXT = {".jpg", ".jpeg", ".png", ".gif", ".bmp"}
PHOTO_FOLDER_NAMES = {"foto", "pic", "pict", "photos"}
VIDEO_FOLDER_NAMES = {"video", "vid", "videos"}

def is_image(filename):
    return os.path.splitext(filename)[1].lower() in IMAGE_EXT

def is_video(filename):
    return os.path.splitext(filename)[1].lower() in VIDEO_EXT

def collect_subfolders(path):
    return [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]

def scan_folder(path):
    files = []
    for root, dirs, filenames in os.walk(path):
        for f in filenames:
            files.append(os.path.join(root, f))
    return files

def rename_and_move(files, new_name, base_folder):
    photo_folder = None
    video_folder = None

    # Cek folder foto dan video yang sudah ada
    for f in os.listdir(base_folder):
        f_path = os.path.join(base_folder, f)
        if os.path.isdir(f_path):
            inner_files = os.listdir(f_path)
            for file in inner_files:
                full_path = os.path.join(f_path, file)
                if is_image(full_path):
                    photo_folder = f_path
                elif is_video(full_path):
                    video_folder = f_path

    has_image = any(is_image(f) for f in files)
    has_video = any(is_video(f) for f in files)

    # Buat folder hanya jika diperlukan
    if has_image and not photo_folder:
        photo_folder = os.path.join(base_folder, "foto")
        os.makedirs(photo_folder, exist_ok=True)
    if has_video and not video_folder:
        video_folder = os.path.join(base_folder, "video")
        os.makedirs(video_folder, exist_ok=True)

    count = 1
    for file in files:
        ext = os.path.splitext(file)[1].lower()
        if not (is_image(file) or is_video(file)):
            continue

        new_filename = f"{new_name} {count}{ext}"
        destination_folder = photo_folder if is_image(file) else video_folder
        destination_path = os.path.join(destination_folder, new_filename)

        while os.path.exists(destination_path):
            count += 1
            new_filename = f"{new_name} {count}{ext}"
            destination_path = os.path.join(destination_folder, new_filename)

        shutil.move(file, destination_path)
        print(f"{Fore.CYAN}✔ Dipindahkan ke: {destination_path}")
        count += 1

def main():
    print(ascii_banner)
    base_path = os.getcwd()
    folders = [f for f in os.listdir(base_path) if os.path.isdir(f)]

    print(f"{Fore.WHITE}Pilih folder untuk diproses:")
    for i, folder in enumerate(folders):
        print(f"{Fore.YELLOW}[{i+1}] {folder}")

    selected = int(input(f"{Fore.GREEN}Masukkan angka folder: ")) - 1
    selected_folder = os.path.join(base_path, folders[selected])

    new_name = input(f"{Fore.GREEN}Masukkan Nama Rename: ")

    all_files = scan_folder(selected_folder)
    rename_and_move(all_files, new_name, selected_folder)
    print(f"\n{Fore.WHITE}{Style.BRIGHT}✅ Proses selesai!")

if __name__ == "__main__":
    main()
