import os
import shutil
from tqdm import tqdm
from pathlib import Path

# Dinamik yollar
user_profile = Path.home()
windows_dir = Path(os.environ.get("WINDIR", "C:\\Windows"))

folders_to_clean = {
    "Windows Temp": windows_dir / "Temp",
    "Local Temp": user_profile / "AppData" / "Local" / "Temp",
    "Prefetch": windows_dir / "Prefetch",
    "Recents": user_profile / "AppData" / "Roaming" / "Microsoft" / "Windows" / "Recent"
}

def clean_folder(folder_path: Path, folder_name: str):
    if not folder_path.exists():
        print(f"{folder_name} klasörü bulunamadı: {folder_path}")
        return

    confirm = input(f"{folder_name} klasörünü temizlemek istiyor musunuz?: ").strip().lower()
    if confirm != "E":
        print(f"{folder_name} atlandı.\n")
        return

    files = list(folder_path.iterdir())
    print(f"{folder_name} klasöründe {len(files)} dosya bulundu. Temizleniyor...")

    for file in tqdm(files, desc=f"{folder_name} temizleniyor", unit="dosya"):
        try:
            if file.is_dir():
                shutil.rmtree(file, ignore_errors=True)
            else:
                file.unlink()
        except PermissionError:
            pass
        except Exception as e:
            print(f"Hata: {e}")

    print(f"{folder_name} klasörü başarıyla temizlendi.\n")

def main():
    print("Temizleme işlemi başlatılıyor\n\n-------KONTROLLER-------\n- Sorulara 'Evet' demek için E tuşuna 1 kere basıp, ardından 'Enter' tuşuna basmanız yeterlidir.\n- Sorulara 'Hayır' cevabı vermek için bir şey yazmadan 'Enter' tuşuna bir kere basmanız yeterlidir.\n------------------------\n\n")
    for name, path in folders_to_clean.items():
        clean_folder(path, name)

    input("Tüm işlemler tamamlandı. Çıkmak için Enter'a basın.")

if __name__ == "__main__":
    main()