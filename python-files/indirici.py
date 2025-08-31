import os
import sys
import subprocess
import shutil

# Yt-dlp ve ffmpeg kontrol
def check_tools():
    for tool in ["yt-dlp", "ffmpeg"]:
        if not shutil.which(tool):
            print(f"[HATA] '{tool}' bulunamadı. Lütfen kurun.")
            sys.exit(1)

# MP3 indir (arama ile)
def mp3_manual():
    os.makedirs("MP3", exist_ok=True)
    track = input("Sanatçı - Şarkı: ").strip()
    if not track:
        print("[HATA] Boş giriş!")
        return
    print("[İNDİRME] Aranıyor ve indiriliyor...")
    subprocess.run([
        "yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "320k",
        "-o", "MP3/%(title)s.%(ext)s", f"ytsearch1:{track}"
    ])

# YouTube URL → MP3
def yt_mp3():
    os.makedirs("MP3", exist_ok=True)
    url = input("YouTube URL: ").strip()
    if not url:
        print("[HATA] Boş giriş!")
        return
    subprocess.run([
        "yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "320k",
        "-o", "MP3/%(title)s.%(ext)s", url
    ])

# SoundCloud URL → MP3
def sc_mp3():
    os.makedirs("MP3", exist_ok=True)
    url = input("SoundCloud URL: ").strip()
    if not url:
        print("[HATA] Boş giriş!")
        return
    subprocess.run([
        "yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "320k",
        "-o", "MP3/%(title)s.%(ext)s", url
    ])

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
    subprocess.run([
        "yt-dlp", f"bestvideo[height<={maxh}]+bestaudio/best[height<={maxh}]",
        "--merge-output-format","mp4",
        "-o", "MP4/%(title)s.%(ext)s", source
    ])

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
        result = subprocess.run([
            "yt-dlp", "-x", "--audio-format", "mp3", "--audio-quality", "320k",
            "-o", "MP3/%(title)s.%(ext)s", f"ytsearch1:{track}"
        ])
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
