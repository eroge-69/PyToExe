import re, sys, time, threading, subprocess
from pathlib import Path
from urllib.parse import quote
import requests
import shutil
from mutagen.id3 import ID3, APIC, TPE1, TIT2, TALB, TRCK, TCON
from mutagen.flac import FLAC, Picture
from mutagen.mp3 import MP3
from PIL import Image
from io import BytesIO


MUSIC_DIR = Path.home() / "Music"
if not MUSIC_DIR.exists():
    MUSIC_DIR = Path.home()
ANIMATION_FRAMES = ["⠋","⠙","⠹","⠸","⠼","⠴","⠦","⠧","⠇","⠏"]
ANIMATION_DELAY = 0.1
DEFAULT_GENRE = "Other"
GENRE_CACHE = {}



def clean_filename(name: str) -> str:
    return re.sub(r'[\\/*?:"<>|]', '', name).strip()

class DownloadAnimation:
    def __init__(self, message: str):
        self.message = message
        self.running = False
        self.thread = None

    def _animate(self):
        idx = 0
        while self.running:
            sys.stdout.write(f"\r{ANIMATION_FRAMES[idx]} {self.message}")
            sys.stdout.flush()
            time.sleep(ANIMATION_DELAY)
            idx = (idx + 1) % len(ANIMATION_FRAMES)
        sys.stdout.write("\r" + " "*(len(self.message)+5) + "\r")

    def start(self):
        self.running = True
        self.thread = threading.Thread(target=self._animate, daemon=True)
        self.thread.start()

    def stop(self):
        self.running = False
        if self.thread:
            self.thread.join()


def search_artist_deezer(name: str):
    try:
        url = f"https://api.deezer.com/search/artist?q={quote(name)}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json().get('data', [])
        if not data:
            return None, None
        art = data[0]
        return art['id'], art['name']
    except Exception as e:
        print(f"Ошибка поиска исполнителя: {e}")
        return None, None


def get_artist_albums_deezer(artist_id: int):
    try:
        url = f"https://api.deezer.com/artist/{artist_id}/albums"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.json().get('data', [])
    except Exception as e:
        print(f"Ошибка получения альбомов: {e}")
        return []


def get_album_tracks_deezer(album_id: int):
    try:
        url = f"https://api.deezer.com/album/{album_id}"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        data = resp.json()
        tracks = [t['title'] for t in data.get('tracks', {}).get('data', [])]
        cover_url = data.get('cover_xl')
        genre_id = data.get('genre_id')
        return tracks, cover_url, genre_id
    except Exception as e:
        print(f"Ошибка получения треков альбома: {e}")
        return [], None, None


def get_genre_name(genre_id):
    if not genre_id:
        return DEFAULT_GENRE
    if genre_id in GENRE_CACHE:
        return GENRE_CACHE[genre_id]
    try:
        url = f"https://api.deezer.com/genre/{genre_id}"
        resp = requests.get(url, timeout=5)
        resp.raise_for_status()
        name = resp.json().get('name', DEFAULT_GENRE)
    except:
        name = DEFAULT_GENRE
    GENRE_CACHE[genre_id] = name
    return name


def fetch_cover_data(url: str):
    if not url:
        return None
    try:
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        return resp.content
    except Exception as e:
        print(f"Ошибка загрузки обложки: {e}")
        return None


def split_albums_and_singles(albums):
    albums_list, singles_list = [], []
    for album in albums:
        kind = album.get('record_type', '').lower()
        if kind == 'album': albums_list.append(album)
        elif kind in ('single', 'ep'): singles_list.append(album)
    return albums_list, singles_list



def add_flac_tags(path: Path, title, artist, album, num, total, genre, cover_data=None):
    try:
        audio = FLAC(path)
        audio['title'] = title
        audio['artist'] = artist
        audio['album'] = album
        audio['tracknumber'] = str(num)
        audio['tracktotal'] = str(total)
        audio['genre'] = genre
        if cover_data:
            img = Image.open(BytesIO(cover_data))
            img.thumbnail((500, 500))
            buf = BytesIO(); img.save(buf, format='JPEG')
            pic = Picture(); pic.data = buf.getvalue()
            pic.type, pic.mime = 3, 'image/jpeg'
            pic.width, pic.height = img.size; pic.depth = 24
            audio.clear_pictures(); audio.add_picture(pic)
        audio.save(); return True
    except Exception as e:
        print(f"Ошибка тэгирования FLAC: {e}"); return False


def add_id3_tags(path: Path, title, artist, album, num, total, genre):
    try:
        audio = MP3(path, ID3=ID3); audio.delete(); audio.add_tags()
        audio.tags.add(TPE1(encoding=3, text=artist)); audio.tags.add(TIT2(encoding=3, text=title))
        audio.tags.add(TALB(encoding=3, text=album)); audio.tags.add(TRCK(encoding=3, text=f"{num}/{total}"))
        audio.tags.add(TCON(encoding=3, text=genre)); audio.save(); return True
    except Exception as e:
        print(f"Ошибка тэгирования MP3: {e}"); return False


def add_mp3_cover(path: Path, cover_data):
    if not cover_data: return False
    try:
        audio = MP3(path, ID3=ID3); audio.tags.delall('APIC')
        img = Image.open(BytesIO(cover_data)); img.thumbnail((500,500))
        buf = BytesIO(); img.save(buf, format='JPEG')
        audio.tags.add(APIC(encoding=3, mime='image/jpeg', type=3, desc='Cover', data=buf.getvalue())); audio.save()
        return True
    except Exception as e:
        print(f"Ошибка добавления обложки MP3: {e}"); return False



def download_yt_flac(artist, track, dest_path: Path):
    dest = dest_path.with_suffix('.flac')
    anim = DownloadAnimation(f"Скачивание FLAC: {track}"); anim.start()
    try:
        res = subprocess.run(['yt-dlp','-x','--audio-format','flac','--audio-quality','0','--default-search','ytsearch','-o',str(dest),f"{artist} - {track}"], capture_output=True)
    finally: anim.stop()
    if res.returncode==0 and dest.exists() and dest.stat().st_size>1024: return dest
    if dest.exists(): dest.unlink()
    print(f"Ошибка скачивания FLAC: {track}"); return None


def download_yt_mp3(artist, track, dest_path: Path):
    dest = dest_path.with_suffix('.mp3'); dest.parent.mkdir(exist_ok=True, parents=True)
    anim = DownloadAnimation(f"Скачивание MP3: {track}"); anim.start()
    try:
        res = subprocess.run(['yt-dlp','-x','--audio-format','mp3','--audio-quality','0','--default-search','ytsearch','-o',str(dest),f"{artist} - {track}"], capture_output=True)
    finally: anim.stop()
    if res.returncode==0 and dest.exists(): return dest
    if dest.exists(): dest.unlink()
    print(f"Ошибка скачивания MP3: {track}"); return None


def ask_download_option():
    print("\nВыберите формат:")
    print("1) FLAC (большой размер, лучшее качество)")
    print("2) MP3 (маленький размер, стандартное качество)")
    while True:
        c=input(": ").strip()
        if c in ('1','2'): return c
        print("Неверный ввод, выберите 1 или 2.")


def manual_track_download(artist: str):
    track_input=input("Введите название трека: ").strip(); fmt=ask_download_option()
    try:
        url=f"https://api.deezer.com/search/track?q={quote(artist+' '+track_input)}"
        resp=requests.get(url,timeout=10); resp.raise_for_status(); data=resp.json().get('data',[])
        if data:
            r=data[0]; track_title=r.get('title',track_input); album_title=r.get('album',{}).get('title',track_input)
            cover_url=r.get('album',{}).get('cover_xl'); genre_id=r.get('artist',{}).get('genre_id'); genre=get_genre_name(genre_id)
            cover_data=fetch_cover_data(cover_url); track_number=r.get('track_position',1); total_tracks=r.get('album',{}).get('nb_tracks',1)
        else:
            track_title=album_title=track_input; genre=DEFAULT_GENRE; cover_data=None; track_number=1; total_tracks=1
    except:
        track_title=album_title=track_input; genre=DEFAULT_GENRE; cover_data=None; track_number=1; total_tracks=1
    dest_dir=MUSIC_DIR/clean_filename(artist)/clean_filename(album_title); dest_dir.mkdir(parents=True,exist_ok=True)
    dest_path=dest_dir/clean_filename(f"{track_number:02d} {track_title}")
    if fmt=='1':
        file=download_yt_flac(artist,track_input,dest_path)
        if file and add_flac_tags(file,track_title,artist,album_title,track_number,total_tracks,genre,cover_data): print(f"✓ [FLAC] {track_title}")
    else:
        file=download_yt_mp3(artist,track_input,dest_path)
        if file and add_id3_tags(file,track_title,artist,album_title,track_number,total_tracks,genre): add_mp3_cover(file,cover_data); print(f"✓ [MP3] {track_title}")
    input("Нажмите Enter для продолжения...")



def main():
    if shutil.which('yt-dlp') is None:
        print("yt-dlp не найден. Установите yt-dlp и повторите.")
        sys.exit(1)
    while True:
        name=input("\nИсполнитель (или 'q' для завершения): ").strip()
        if name.lower()=='q': print("Выход."); break
        aid, artist = search_artist_deezer(name)
        if not aid: print("Исполнитель не найден."); continue
        all_releases=get_artist_albums_deezer(aid)
        if not all_releases: print("Релизы не найдены."); continue
        albums,singles=split_albums_and_singles(all_releases)
        print("\n📀 Альбомы:")
        for i, alb in enumerate(albums,1): year=alb.get('release_date','?')[:4]; print(f"{i}. {alb['title']} ({year})")
        alb_count=len(albums)
        print("\n🎵 Синглы / EP:")
        for i, alb in enumerate(singles,1): year=alb.get('release_date','?')[:4]; print(f"{i+alb_count}. {alb['title']} ({year})")
        print("\nM. Ручной поиск трека")
        choice=input("Выберите альбом/сингл по номеру или 'M': ").strip()
        if choice.lower()=='m': manual_track_download(artist); continue
        if not choice.isdigit(): print("Неверный ввод."); continue
        idx=int(choice)-1
        if idx<0 or idx>=len(albums)+len(singles): print("Неверный номер."); continue
        sel=albums[idx] if idx<len(albums) else singles[idx-len(albums)]
        album_title=sel['title']; print(f"Загружаем альбом «{album_title}»...")
        tracks,cover_url,genre_id=get_album_tracks_deezer(sel['id']); genre=get_genre_name(genre_id); cover_data=fetch_cover_data(cover_url)
        total=len(tracks); base=MUSIC_DIR/clean_filename(artist)/clean_filename(album_title); base.mkdir(parents=True,exist_ok=True)
        fmt=ask_download_option()
        for i, track in enumerate(tracks,1):
            dest=base/clean_filename(f"{i:02d} {track}")
            if fmt=='1': file=download_yt_flac(artist,track,dest);
            else: file=download_yt_mp3(artist,track,dest)
            if file:
                if fmt=='1': add_flac_tags(file,track,artist,album_title,i,total,genre,cover_data); print(f"✓ [FLAC] {track}")
                else: add_id3_tags(file,track,artist,album_title,i,total,genre); add_mp3_cover(file,cover_data); print(f"✓ [MP3] {track}")
            time.sleep(1)
        print(f"Готово: «{album_title}» ({total} треков)."); input("Нажмите Enter для продолжения...")


if __name__=='__main__':
    print("by проституция души\n")
    main()
