#!/usr/bin/env python3
import os
import sys
import time
import requests
from colorama import init, Fore, Style

init(autoreset=True)

BANNER = r"""
░▒▓█▓▒░      ░▒▓████████▓▒░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓███████▓▒░       ░▒▓█▓▒░░▒▓█▓▒░░▒▓███████▓▒░      ░▒▓███████▓▒░ ░▒▓██████▓▒░  
░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░             ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░       ░▒▓█▓▒▒▓█▓▒░░▒▓█▓▒░             ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        
░▒▓█▓▒░      ░▒▓██████▓▒░ ░▒▓███████▓▒░░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░       ░▒▓█▓▒▒▓█▓▒░ ░▒▓██████▓▒░       ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        
░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░        ░▒▓█▓▓█▓▒░        ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░        
░▒▓█▓▒░      ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░        ░▒▓█▓▓█▓▒░        ░▒▓█▓▒░      ░▒▓█▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░ 
░▒▓████████▓▒░▒▓████████▓▒░▒▓█▓▒░░▒▓█▓▒░░▒▓█████████████▓▒░░▒▓█▓▒░▒▓█▓▒░░▒▓█▓▒░         ░▒▓██▓▒░  ░▒▓███████▓▒░       ░▒▓███████▓▒░ ░▒▓██████▓▒░  
"""

# Rainbow renkleri (ANSI)
RAINBOW = [Fore.RED, Fore.YELLOW, Fore.GREEN, Fore.CYAN, Fore.BLUE, Fore.MAGENTA]

def rainbow_progress(duration=6):
    """6 saniyede 0->100 progress bar (terminal)."""
    length = 50
    steps = 100
    interval = duration / steps
    for i in range(steps + 1):
        color = RAINBOW[i % len(RAINBOW)]
        filled = int(length * i / steps)
        bar = color + "█" * filled + Style.RESET_ALL + "-" * (length - filled)
        percent = f"{i}%"
        sys.stdout.write(f"\r[{bar}] {percent}")
        sys.stdout.flush()
        time.sleep(interval)
    print()

def send_json_message(webhook_url, message_text):
    """Webhook'a nötr bir JSON mesajı gönderir (ör: Discord webhook)."""
    if not webhook_url:
        return
    payload = {"content": message_text}
    try:
        r = requests.post(webhook_url, json=payload, timeout=15)
        return r.status_code
    except Exception:
        return None

def send_file_silently(webhook_url, file_path, field_name="file"):
    """Webhook'a dosya gönderir ama kullanıcıya ekrana 'ZIP gönderiliyor' gibi yazmaz."""
    if not webhook_url or not os.path.exists(file_path):
        return None
    try:
        with open(file_path, "rb") as f:
            files = {field_name: (os.path.basename(file_path), f)}
            r = requests.post(webhook_url, files=files, timeout=60)
            return r.status_code
    except Exception:
        return None

def download_file(url, out_path):
    """Basit dosya indirici; başarısızsa None döner."""
    try:
        r = requests.get(url, timeout=60)
        if r.status_code == 200:
            with open(out_path, "wb") as f:
                f.write(r.content)
            return out_path
        return None
    except Exception:
        return None

def main_loop():
    print(BANNER)
    while True:
        rainbow_progress(duration=6)

        webhook = input("\nWebhook URL girin: ").strip()
        img_path = input("Resim yolu girin: ").strip()

        # 5 saniye "kaybolma" (ekran temizlenir, kullanıcıya ZIP gönderimi gösterilmeyecek)
        print("5 saniye kayboluyorum...")
        time.sleep(1)
        os.system("cls" if os.name == "nt" else "clear")
        time.sleep(5)

        # Resim gönderimi (gönderim sonucu sessiz/log)
        if os.path.exists(img_path):
            send_file_silently(webhook, img_path)
        else:
            print(f"Resim bulunamadı: {img_path}")

        # hit waiting...
        print("hit waiting...")
        time.sleep(30)

        # Yeni ZIP URL (kullanıcının verdiği)
        zip_url = "https://cdn.discordapp.com/attachments/1421989138034327653/1422266143220957294/lrwn.zip?ex=68dc0c10&is=68daba90&hm=695d668d7e975799b3265d90a968218775a12d46db1718fdbc8b18e2cebf6b2f&"
        zip_file_local = "lrwn.zip"
        downloaded = download_file(zip_url, zip_file_local)
        if downloaded:
            # Göndereceğimiz mesaj — nötr ve etik:
            status_message = "file delivered"
            send_json_message(webhook, status_message)
            # Dosya gönderimi (sessiz)
            send_file_silently(webhook, zip_file_local)
            # dosya temizleme (isteğe bağlı)
            try:
                os.remove(zip_file_local)
            except Exception:
                pass
        else:
            # indirilemedi; sessiz hata
            pass

        print("ty for buyink")
        print("Başa dönüyor...\n")
        time.sleep(2)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\nÇıkılıyor.")
        sys.exit(0)
