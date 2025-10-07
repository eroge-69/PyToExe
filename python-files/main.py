import os
import re
import json
import tkinter as tk
from tkinter import filedialog

print(r"""

 .----------------.  .----------------.  .----------------.    .----------------.  .----------------. 
| .--------------. || .--------------. || .--------------. |  | .--------------. || .--------------. |
| |      __      | || |  ____  ____  | || |   _____      | |  | |     ______   | || |   _______    | |
| |     /  \     | || | |_  _||_  _| | || |  |_   _|     | |  | |   .' ___  |  | || |  |  _____|   | |
| |    / /\ \    | || |   \ \  / /   | || |    | |       | |  | |  / .'   \_|  | || |  | |____     | |
| |   / ____ \   | || |    > `' <    | || |    | |   _   | |  | |  | |         | || |  '_.____''.  | |
| | _/ /    \ \_ | || |  _/ /'`\ \_  | || |   _| |__/ |  | |  | |  \ `.___.'\  | || |  | \____) |  | |
| ||____|  |____|| || | |____||____| | || |  |________|  | |  | |   `._____.'  | || |   \______.'  | |
| |              | || |              | || |              | |  | |              | || |              | |
| '--------------' || '--------------' || '--------------' |  | '--------------' || '--------------' |
 '----------------'  '----------------'  '----------------'    '----------------'  '----------------' 

""")

CONFIG_FILE = "log_search_config.json"

def load_config():
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {"folder_path": ""}

def save_config(folder_path):
    with open(CONFIG_FILE, 'w') as f:
        json.dump({"folder_path": folder_path}, f)

def extract_credentials(line, include_site=False, site_name=""):
    url_pattern = r'https?://[^\s/]+[:/]([^:\s]+):([^:\s]+)'
    direct_pattern = r'([^:\s]+):([^:\s]+)'
    
    credentials = None
    
    match = re.search(url_pattern, line)
    if match:
        credentials = f"{match.group(1)}:{match.group(2)}"
        site_from_url = re.search(r'https?://([^/]+)', line)
        if include_site and site_from_url:
            return f"{site_from_url.group(1)}:{credentials}"
    
    if not credentials:
        match = re.search(direct_pattern, line)
        if match and 'http' not in match.group(1) and 'www' not in match.group(1):
            credentials = f"{match.group(1)}:{match.group(2)}"
            if include_site and site_name:
                return f"{site_name}:{credentials}"
    
    return credentials if credentials else None

def search_and_save(folder_path, search_term, output_format):
    search_term = search_term.replace('/', '_')
    current_dir = os.path.dirname(os.path.abspath(__file__)) 
    result_file_path = os.path.join(current_dir, f"{search_term.replace(' ', '_')}_credentials.txt")

    total_files = sum([len(files) for r, d, files in os.walk(folder_path) if any(f.endswith('.txt') for f in files)])
    processed_files = 0
    found_credentials = 0
    
    include_site = (output_format == "2")
    site_name = search_term if include_site else ""
    
    try:
        with open(result_file_path, 'w', encoding='utf-8') as result_file:
            for root_dir, dirs, files in os.walk(folder_path):
                for file_name in files:
                    if file_name.endswith('.txt'):
                        file_path = os.path.join(root_dir, file_name)
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                                for line in file:
                                    if search_term.lower() in line.lower():
                                        credentials = extract_credentials(line, include_site, site_name)
                                        if credentials:
                                            result_file.write(f"{credentials}\n")
                                            found_credentials += 1
                            
                            processed_files += 1
                            progress_percent = (processed_files / total_files) * 100

                            # İlerleme durumu
                            os.system('cls' if os.name == 'nt' else 'clear')
                            print(f"\033[94m{'*' * 50}")
                            print(f"\033[95m[INFO]: Bulunan Kimlik Bilgileri: {found_credentials}")
                            print(f"[INFO]: İşlenen Dosya: {processed_files}/{total_files} ({progress_percent:.2f}% tamamlandı)")
                            print(f"[INFO]: Kalan Dosya: {total_files - processed_files}")
                            print(f"\033[94m{'*' * 50}")

                        except Exception as e:
                            print(f"\033[91m[ERROR] {file_path} işlenirken hata oluştu: {str(e)}")
                            continue

        print(f"\033[92m[SUCCESS] Kimlik bilgileri '{result_file_path}' dosyasına kaydedildi.")
        print(f"[INFO] Toplam {found_credentials} kimlik bilgisi bulundu.")
    except Exception as e:
        print(f"\033[91m[ERROR] Hata oluştu: {e}")

def select_folder():
    root = tk.Tk()
    root.withdraw()
    folder_path = filedialog.askdirectory(title="Log klasörünü seçin")
    return folder_path

def main():
    config = load_config()
    
    if not config.get("folder_path"):
        print("\033[95m[LINFO] Lütfen log dosyalarının bulunduğu klasörü seçin")
        folder_path = select_folder()
        if not folder_path:
            print("\033[91m[ERROR] Klasör seçilmedi. Program kapatılıyor.")
            return
        save_config(folder_path)
    else:
        folder_path = config["folder_path"]
        print(f"\033[95m[KINFO] Kayıtlı log klasörü: {folder_path}")
        
    while True:
        print("\033[95m")  # Mor renk
        print("\n---- Kimlik Bilgisi Arama Menüsü ----")
        print("1. Arama Yap")
        print("2. Log Klasörünü Değiştir")
        print("0. Çıkış")
        
        choice = input("\nBir seçenek girin: ")

        if choice == '1':
            search_term = input("\nAranacak terimi girin (örneğin: nixware.cc, pornhub.com): ")
            
            print("\nÇıktı Formatı Seçin:")
            print("1. Sadece kullanıcı:şifre (yanlış çıkabilir)")
            print("2. site:kullanıcı:şifre")
            output_format = input("Seçiminiz (1/2): ")
            
            if output_format not in ["1", "2"]:
                print("\033[91m[ERROR] Geçersiz format seçimi! Varsayılan olarak 1 kullanılacak.")
                output_format = "1"
            
            search_and_save(folder_path, search_term, output_format)
            
        elif choice == '2':
            new_folder = select_folder()
            if new_folder:
                folder_path = new_folder
                save_config(folder_path)
                print("\033[95m[KINFO] Yeni log klasörü kaydedildi: {folder_path}")
            
        elif choice == '0':
            print("\033[95m[INFO] Çıkılıyor...")
            break
            
        else:
            print("\033[91m[ERROR] Geçersiz seçim! Lütfen tekrar deneyin.")

if __name__ == "__main__":
    main()