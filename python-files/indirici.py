import os
import sys
import subprocess

# Her zaman bulunduğu dizindeki bin klasörünü kullan
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BIN_DIR = os.path.join(BASE_DIR, "bin")
YTDLP = os.path.join(BIN_DIR, "yt-dlp.exe")
FFMPEG = os.path.join(BIN_DIR, "ffmpeg.exe")

def check_tools():
    if not os.path.exists(YTDLP):
        print("[HATA] yt-dlp.exe 'bin' klasöründe bulunamadı.")
        sys.exit(1)
    if not os.path.exists(FFMPEG):
        print("[HATA] ffmpeg.exe 'bin' klasöründe bulunamadı.")
        sys.exit(1)

def run_cmd(cmd):
    return subprocess.run(cmd, shell=True)

# MP3 indir (arama ile)
def mp3_manual():
    os.makedirs("MP3", exist_ok=True)
    track = input("Sanatçı - Şarkı: ").strip()
    if not track:
        print("[HATA] Boş giriş!")
        return
    print("[İNDİRME] Aranıyor ve indiriliyor...")
    run_cmd(f'"{YTDLP}" -x --audio-format mp3 --audio-quality 320k '
            f'--ffmpeg-location "{FFMPEG}" '
            f'-o "MP3/%(title)s.%(ext)s" "ytsearch1:{track}"')

# YouTube URL → MP3
def yt_mp3():
    os.makedirs("MP3", exist_ok=True)
    url = input("YouTube URL: ").strip()
    if not url:
        print("[HATA] Boş giriş!")
        return
    run_cmd(f'"{YTDLP}" -x --audio-format mp3 --audio-quality 320k '
            f'--ffmpeg-location "{FFMPEG}" '
            f'-o "MP3/%(title)s.%(ext)s" "{url}"')

# SoundCloud URL → MP3
def sc_mp3():
    os.makedirs("MP3", exist_ok=True)
    url = input("SoundCloud URL: ").strip()
    if not url:
        print("[HATA] Boş giriş!")
        return
    run_cmd(f'"{YTDLP}" -x --audio-format mp3 --audio-quality 320k '
            f'--ffmpeg-location "{FFMPEG}" '
            f'-o "MP3/%(title)s.%(ext)s" "{url}"')

# YouTube URL veya arama → MP4
def yt_mp4():
    os.makedirs("MP4", exist_ok=True)
    query = input("YouTube URL veya arama: ").strip()
    if not query:
        print("[HATA] Boş giriş!")
        return

    print("Kalite seçenekleri:")
    print("1) 360p\n2) 480p\n3) 720p\n4) 1080p\n5) 1440p\n6) 2160p")
    choice = input("Seçim (1-6): ").strip()
    res_map = {"1":"360","2":"480","3":"720","4":"1080","5":"1440","6":"2160"}
    maxh = res_map.get(choice,"720")

    source = query if query.startswith("http") else f"ytsearch1:{query}"
    run_cmd(f'"{YTDLP}" -f "bestvideo[height<={maxh}]+bestaudio/best[height<={maxh}]" '
            f'--ffmpeg-location "{FFMPEG}" '
            f'--merge-output-format mp4 '
            f'-o "MP4/%(title)s.%(ext)s" "{source}"')

# Toplu MP3 indirme
def bulk_mp3():
    os.makedirs("MP3", exist_ok=True)
    raw = input("Sanatçı - Şarkı listesi (virgülle ayırın): ").strip()
    if not raw:
        print("[HATA] Boş giriş!")
        return
    tracks = [x.strip() for x in raw.split(",") if x.strip()]
    success, fail = 0, 0
    for i, track in enumerate(tracks,1):
        print(f"\n[{i}/{len(tracks)}] İndiriliyor: {track}")
        result = run_cmd(f'"{YTDLP}" -x --audio-format mp3 --audio-quality 320k '
                         f'--ffmpeg-location "{FFMPEG}" '
                         f'-o "MP3/%(title)s.%(ext)s" "ytsearch1:{track}"')
        if result.returncode==0:
            success+=1
        else:
            fail+=1
    print("\n===== TOPLU İNDİRME ÖZETİ =====")
    print(f"Toplam: {len(tracks)}  Başarılı: {success}  Hatalı: {fail}")

# Ana menü
def main():
    check_tools()
    while True:
        print("\n=========================================")
        print("        ALL-IN-ONE DOWNLOADER")
        print("=========================================")
        print("1. MP3 indir (Sanatçı - Şarkı)")
        print("2. YouTube linkten Mp3")
        print("3. Soundcloud linkten Mp3")
        print("4. YouTube linkten Video (kalite seçimi)")
        print("5. Toplu MP3 İndir")
        print("6. Çıkış")
        choice = input("Seçiminiz (1-6): ").strip()
        if choice=="1": mp3_manual()
        elif choice=="2": yt_mp3()
        elif choice=="3": sc_mp3()
        elif choice=="4": yt_mp4()
        elif choice=="5": bulk_mp3()
        elif choice=="6": sys.exit(0)
        else: print("Geçersiz seçim!")

if __name__=="__main__":
    main()
