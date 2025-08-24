import os
import re

def clean_name(name):
    # Hapus kata iframe, official, dan teks dalam tanda kurung
    name = re.sub(r'(?i)iframe', '', name)
    name = re.sub(r'(?i)official', '', name)
    name = re.sub(r'\(.*?\)', '', name)
    name = re.sub(r'\s+', ' ', name)
    name = name.strip()
    if not name:
        name = 'Unknown'
    return name

def rename_mp3_files(folder):
    files = [f for f in os.listdir(folder) if f.lower().endswith('.mp3')]
    files.sort()
    
    if not files:
        print("❌ Tidak ada file MP3 di folder ini.")
        return
    
    count = 1
    for f in files:
        old_path = os.path.join(folder, f)
        name, ext = os.path.splitext(f)
        new_name = clean_name(name)
        new_filename = f"{count:03d} - {new_name}{ext}"
        new_path = os.path.join(folder, new_filename)
        print(f"Rename: {f} -> {new_filename}")
        os.rename(old_path, new_path)
        count += 1
    
    print("✅ Semua file MP3 sudah diurutkan dan dibersihkan!")

if __name__ == "__main__":
    current_folder = os.getcwd()
    print(f"Folder saat ini: {current_folder}")
    rename_mp3_files(current_folder)
    input("Tekan Enter untuk keluar...")
