import os
import shutil
import ctypes

def main():
    current_dir = os.getcwd()
    target_dir = os.path.join(current_dir, "zbedne_RAW")

    # Utworzenie katalogu jeśli nie istnieje
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)

    # Lista znanych rozszerzeń RAW
    raw_exts = {
        ".raw", ".cr2", ".cr3", ".nef", ".arw", ".orf",
        ".raf", ".dng", ".rw2", ".sr2", ".pef", ".erf",
        ".k25", ".kdc", ".mrw", ".3fr", ".mos", ".x3f"
    }

    files = os.listdir(current_dir)

    raws = [f for f in files if os.path.splitext(f)[1].lower() in raw_exts]
    jpgs = {os.path.splitext(f)[0].lower() for f in files if f.lower().endswith((".jpg", ".jpeg"))}

    moved_count = 0

    for raw in raws:
        name, _ = os.path.splitext(raw)
        if name.lower() not in jpgs:
            src = os.path.join(current_dir, raw)
            dst = os.path.join(target_dir, raw)
            shutil.move(src, dst)
            moved_count += 1

    # Wiadomość w MessageBox
    message = f"Łącznie przeniesiono: {moved_count} plików RAW bez odpowiedników JPG/JPEG."
    ctypes.windll.user32.MessageBoxW(0, message, "Operacja zakończona", 0x40)

if __name__ == "__main__":
    main()
