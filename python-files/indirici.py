# all_in_one_downloader.py
import os
import sys
import subprocess
import shutil
import re
from pathlib import Path
import tempfile

# Dizinler
MP3_DIR = Path("MP3")
MP4_DIR = Path("MP4")
BIN_DIR = Path("bin")

# Gerekli dosyalar
YT_DLP_PATH = BIN_DIR / "yt-dlp.exe"
FFMPEG_PATH = BIN_DIR / "ffmpeg.exe"

def check_dependencies():
    if not YT_DLP_PATH.exists():
        print("[HATA] yt-dlp.exe 'bin' klasöründe bulunamadı.")
        return False
    if not FFMPEG_PATH.exists():
        print("[HATA] ffmpeg.exe 'bin' klasöründe bulunamadı.")
        return False
    return True

def create_dirs():
    MP3_DIR.mkdir(exist_ok=True)
    MP4_DIR.mkdir(exist_ok=True)

def run_command(cmd, cwd=None):
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding='utf-8',
            errors='replace'
        )
        return result.returncode == 0, result.stdout
    except Exception as e:
        print(f"[HATA] Komut çalıştırılamadı: {e}")
        return False, ""

def download_mp3_manual():
    print("\n" + "="*40)
    print(" [MP3 - Manuel] Şarkı adı ve sanatçıyı girin:")
    print(" Örnek: Artist - Song Name")
    print("="*40)
    track_info = input("Şarkı adı ve sanatçı: ").strip()
    if not track_info:
        print("[HATA] Girdi boş olamaz.")
        return

    print("\n[İNİYOR] Aranıyor ve indiriliyor...")
    cmd = (
        f'"{YT_DLP_PATH}" -x --audio-format mp3 --audio-quality 320k '
        f'--ffmpeg-location "{FFMPEG_PATH}" '
        f'--ignore-errors --no-check-certificates '
        f'--no-warnings --console-title '
        f'-o "{MP3_DIR}/%(title)s.%(ext)s" '
        f'ytsearch1:"{track_info}"'
    )
    success, output = run_command(cmd)
    if success and any(f.endswith(".mp3") for f in os.listdir(MP3_DIR)):
        print(f"\n[BAŞARI] İndirme işlemi tamamlandı!")
        print("[DOSYA] İndirilen dosyalar:")
        for f in MP3_DIR.iterdir():
            if f.suffix.lower() == ".mp3":
                print(f" - {f.name}")
    else:
        print("[HATA] Hiçbir MP3 indirilemedi.")

def bulk_mp3():
    print("\n" + "="*40)
    print(" [Toplu MP3] Birden fazla şarkı indirin")
    print(" Örnek: Artist1 - Song1, Artist2 - Song2")
    print("="*40)
    track_list = input("Sanatçı - Şarkı listesi (virgül ile ayırın): ").strip()
    if not track_list:
        print("[HATA] Girdi boş olamaz.")
        return

    tracks = [t.strip() for t in track_list.split(",") if t.strip()]
    if not tracks:
        print("[HATA] Geçerli şarkı bulunamadı.")
        return

    count = 0
    success_count = 0
    error_count = 0

    for track in tracks:
        count += 1
        print(f"\n===== [{count}] İndiriliyor: {track} =====")
        cmd = (
            f'"{YT_DLP_PATH}" -x --audio-format mp3 --audio-quality 320k '
            f'--ffmpeg-location "{FFMPEG_PATH}" '
            f'--ignore-errors --no-check-certificates '
            f'--no-warnings --console-title '
            f'-o "{MP3_DIR}/%(title)s.%(ext)s" '
            f'ytsearch1:"{track}"'
        )
        success, _ = run_command(cmd)
        if success:
            success_count += 1
        else:
            error_count += 1

    print(f"\n===== TOPLU İNDİRME ÖZETİ =====")
    print(f"Toplam giriş: {count}")
    print(f"Başarılı: {success_count}")
    print(f"Hatalı: {error_count}")
    print("="*40)

def youtube_to_mp3():
    print("\n" + "="*40)
    print(" [YouTube -> MP3] 320 kbps indirici")
    print("="*40)
    url = input("YouTube URL girin: ").strip()
    if not url:
        print("[HATA] Girdi boş olamaz.")
        return

    print("\n[İNİYOR] YouTube'dan MP3 indiriliyor...")
    cmd = (
        f'"{YT_DLP_PATH}" -x --audio-format mp3 --audio-quality 320k '
        f'--ffmpeg-location "{FFMPEG_PATH}" '
        f'--ignore-errors --no-check-certificates '
        f'--no-warnings --console-title '
        f'-o "{MP3_DIR}/%(title)s.%(ext)s" '
        f'"{url}"'
    )
    success, output = run_command(cmd)
    if success and any(f.suffix.lower() == ".mp3" for f in MP3_DIR.iterdir()):
        print(f"\n[BAŞARI] İndirme işlemi tamamlandı!")
        print("[DOSYA] İndirilen dosyalar:")
        for f in MP3_DIR.iterdir():
            if f.suffix.lower() == ".mp3":
                print(f" - {f.name}")
    else:
        print("[HATA] Hiçbir MP3 indirilemedi.")

def soundcloud_to_mp3():
    print("\n" + "="*40)
    print(" [SoundCloud -> MP3] 320 kbps indirici")
    print("="*40)
    url = input("SoundCloud URL girin: ").strip()
    if not url:
        print("[HATA] Girdi boş olamaz.")
        return

    print("\n[İNİYOR] SoundCloud'dan indiriliyor...")
    cmd = (
        f'"{YT_DLP_PATH}" -x --audio-format mp3 --audio-quality 320k '
        f'--ffmpeg-location "{FFMPEG_PATH}" '
        f'--ignore-errors --no-check-certificates '
        f'--no-warnings --console-title '
        f'-o "{MP3_DIR}/%(title)s.%(ext)s" '
        f'"{url}"'
    )
    success, output = run_command(cmd)
    if success and any(f.suffix.lower() == ".mp3" for f in MP3_DIR.iterdir()):
        print(f"\n[BAŞARI] İndirme işlemi tamamlandı!")
        print("[DOSYA] İndirilen dosyalar:")
        for f in MP3_DIR.iterdir():
            if f.suffix.lower() == ".mp3":
                print(f" - {f.name}")
    else:
        print("[HATA] Hiçbir MP3 indirilemedi.")

def youtube_to_video():
    print("\n" + "="*40)
    print(" [YouTube -> Video] Kalite seçmeli indirici")
    print("="*40)
    query = input("YouTube URL veya arama terimi: ").strip()
    if not query:
        print("[HATA] Girdi boş olamaz.")
        return

    print("\nSeçenekler:")
    print(" 1) 360p")
    print(" 2) 480p")
    print(" 3) 720p (HD)")
    print(" 4) 1080p (Full HD)")
    print(" 5) 1440p (2K)")
    print(" 6) 2160p (4K)")
    choice = input("Kalite (1-6): ").strip()

    res_map = {"1": "360", "2": "480", "3": "720", "4": "1080", "5": "1440", "6": "2160"}
    maxh = res_map.get(choice, "720")
    print(f"[BİLGİ] Kalite: {maxh}p seçildi.")

    is_url = query.lower().startswith("http")
    search_prefix = "" if is_url else "ytsearch1:"

    print(f"\n[İNİYOR] Video indiriliyor...")
    cmd = (
        f'"{YT_DLP_PATH}" -f "bestvideo[height<={maxh}]+bestaudio/best[height<={maxh}]" '
        f'--ffmpeg-location "{FFMPEG_PATH}" '
        f'--ignore-errors --no-check-certificates '
        f'--extractor-args "youtube:player-client=android" '
        f'--merge-output-format mp4 '
        f'--no-warnings --console-title '
        f'-o "{MP4_DIR}/%(title)s.%(ext)s" '
        f'"{search_prefix}{query}"'
    )
    success, output = run_command(cmd)
    if success and any(f.suffix.lower() in [".mp4", ".mkv"] for f in MP4_DIR.iterdir()):
        print(f"\n[BAŞARI] İndirme işlemi tamamlandı!")
        print("[DOSYA] İndirilen dosyalar:")
        for f in MP4_DIR.iterdir():
            if f.suffix.lower() in [".mp4", ".mkv"]:
                print(f" - {f.name}")
    else:
        print("[UYARI] MP4 klasöründe dosya bulunamadı.")

def cleanup():
    print("\n[TEMİZLİK] Geçici dosyalar temizleniyor...")
    patterns = ["*.tmp", "*.part", "*.ytdl"]
    for pattern in patterns:
        for file in Path(".").glob(pattern):
            file.unlink(missing_ok=True)
        for file in MP3_DIR.glob(pattern):
            file.unlink(missing_ok=True)
        for file in MP4_DIR.glob(pattern):
            file.unlink(missing_ok=True)
    print("[TEMİZLİK] Temizlik tamamlandı.")

def main():
    create_dirs()
    if not check_dependencies():
        input("\nAna menüye dönmek için Enter'a basın...")
        return

    while True:
        os.system('cls' if os.name == 'nt' else 'clear')
        print("\n" + "="*40)
        print("      ALL-IN-ONE DOWNLOADER")
        print("="*40)
        print("1. MP3 indir (Sanatçı - Şarkı)")
        print("2. YouTube linkten MP3")
        print("3. SoundCloud linkten MP3")
        print("4. YouTube linkten Video (kalite seçenekleriyle)")
        print("5. Toplu MP3 İndir (Sanatçı - Şarkı listesi)")
        print("6. Çıkış")
        print("="*40)
        choice = input("Seçiminiz (1-6): ").strip()

        if choice == "1":
            download_mp3_manual()
        elif choice == "2":
            youtube_to_mp3()
        elif choice == "3":
            soundcloud_to_mp3()
        elif choice == "4":
            youtube_to_video()
        elif choice == "5":
            bulk_mp3()
        elif choice == "6":
            print("Çıkılıyor...")
            break
        else:
            print("Geçersiz seçim, tekrar deneyin.")
            input("Devam etmek için Enter'a basın...")
            continue

        cleanup()
        input("\nAna menüye dönmek için Enter'a basın...")

if __name__ == "__main__":
    main()