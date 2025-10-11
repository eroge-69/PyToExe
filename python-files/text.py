from pathlib import Path
from kapak.aes import encrypt
import os

def encrypt_directory(folder_path, password="P@ssw0rd", buffer_size=10 * 1024 * 1024):
    folder = Path(folder_path)

    for file in folder.rglob("*"):
        # Skip directories and already encrypted files
        if file.is_file() and not file.suffix.endswith(".kpk"):
            output_file = file.with_suffix(file.suffix + ".kpk")

            print(f"Encrypting: {file.name} → {output_file.name}")

            with file.open("rb") as src, output_file.open("wb") as dst:
                total_len = file.stat().st_size
                progress = 0
                for chunk_len in encrypt(src, dst, password, buffer_size=buffer_size):
                    progress += chunk_len
                    percent = (progress / total_len) * 100
                    print(f"  {percent:.1f}% complete", end="\r")

            print(f"\n✅ Done encrypting: {output_file.name}")

            # Delete the original file safely
            try:
                os.remove(file)
                print(f"🗑️  Deleted original file: {file.name}\n")
            except Exception as e:
                print(f"⚠️ Could not delete {file.name}: {e}\n")

if __name__ == "__main__":
    # Encrypt everything in the folder with 16 KB buffer
    encrypt_directory("D:/Testing-Grounds", password="P@ssw0rd", buffer_size=10 * 1024 * 1024)