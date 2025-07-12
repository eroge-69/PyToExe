import yt_dlp
import os


def pokaz_postep(d):
    """Funkcja callback do wyświetlania postępu pobierania."""
    if d['status'] == 'downloading':
        info_dict = d.get('info_dict', {})
        tytul_pliku = info_dict.get('title', 'Nieznany plik')
        
        if len(tytul_pliku) > 50:
            tytul_pliku = tytul_pliku[:47] + "..."

        procent_str = d.get('_percent_str', '---').strip()
        szybkosc_str = d.get('_speed_str', '---').strip()
        
        print(f"\rPobieranie: {tytul_pliku} | Postęp: {procent_str} | Prędkość: {szybkosc_str}", end='')
    
    elif d['status'] == 'finished':
        filename = d.get('filename') or d.get('info_dict', {}).get('_filename')
        print(f"\n✅ Pobrane: {os.path.basename(filename)}")
        
    elif d['status'] == 'error':
        print("\n❌ Wystąpił błąd podczas pobierania.")


def pobierz_materialy_yt():
    """Główna funkcja do pobierania filmów lub całych playlist."""
    link = input("Wklej link do filmu lub playlisty z YouTube: ")

    sciezka_pobierania = "Pobrane_yt-dlp"
    if not os.path.exists(sciezka_pobierania):
        os.makedirs(sciezka_pobierania)

    print("\nCo chcesz pobrać?")
    print("1. Wideo (jeden film, z wyborem rozdzielczości)")
    print("2. Tylko audio MP3 (jeden film)")
    print("3. Całą playlistę (jako pliki MP3)")
    print("4. Całą playlistę wideo (MP4 z wyborem rozdzielczości)")
    wybor = input("Twój wybór (1/2/3/4): ")
    
    ydl_opts = {}

    # Opcje 1, 2, 3 pozostają bez zmian
    if wybor == '1':
        try:
            print("\nPobieram listę dostępnych rozdzielczości...")
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                info_dict = ydl.extract_info(link, download=False)
            
            formaty_wideo = []
            for f in info_dict.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                    rozmiar_mb = f.get('filesize') or f.get('filesize_approx')
                    rozmiar_str = f"{rozmiar_mb / (1024*1024):.2f} MB" if rozmiar_mb else "nieznany"
                    rozdzielczosc = f.get('format_note', f"{f.get('height')}p")
                    formaty_wideo.append({
                        'id': f['format_id'], 'res': rozdzielczosc, 
                        'size': rozmiar_str, 'height': f.get('height', 0)
                    })
            
            formaty_wideo = sorted(
                list({f['res']: f for f in formaty_wideo}.values()),
                key=lambda x: x['height'],
                reverse=True
            )

            if not formaty_wideo:
                print("Nie znaleziono dostępnych formatów wideo MP4.")
                return

            print("\nWybierz rozdzielczość do pobrania:")
            for i, f in enumerate(formaty_wideo):
                print(f"{i+1}. {f['res']} ({f['size']})")
            
            wybor_formatu = int(input("Wybierz numer: ")) - 1

            if 0 <= wybor_formatu < len(formaty_wideo):
                wybrany_format_id = formaty_wideo[wybor_formatu]['id']
                print(f"\nWybrano: {formaty_wideo[wybor_formatu]['res']}. Rozpoczynam pobieranie...")
                ydl_opts = {
                    'format': f'{wybrany_format_id}+bestaudio/best[ext=mp4]/best',
                    'outtmpl': os.path.join(sciezka_pobierania, '%(title)s - %(resolution)s.%(ext)s'),
                    'progress_hooks': [pokaz_postep],
                    'merge_output_format': 'mp4',
                }
            else:
                print("Błędny wybór.")
                return
        except Exception as e:
            print(f"Nie udało się pobrać informacji o filmie: {e}")
            return

    elif wybor == '2':
        print("\nRozpoczynam pobieranie i konwersję do MP3...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(sciezka_pobierania, '%(title)s.%(ext)s'),
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}],
            'progress_hooks': [pokaz_postep],
        }
        
    elif wybor == '3':
        print("\nRozpoczynam pobieranie playlisty i konwersję do MP3...")
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(sciezka_pobierania, '%(playlist_title)s', '%(playlist_index)s - %(title)s.%(ext)s'),
            'postprocessors': [{'key': 'FFmpegExtractAudio','preferredcodec': 'mp3','preferredquality': '192',}],
            'progress_hooks': [pokaz_postep],
            'ignoreerrors': True,
        }

    # -- POCZĄTEK FINALNEJ POPRAWKI --
    elif wybor == '4':
        try:
            print("\nPobieram listę dostępnych rozdzielczości z pierwszego filmu na playliście...")
            with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': 'in_playlist'}) as ydl:
                info_dict = ydl.extract_info(link, download=False)
            
            if 'entries' not in info_dict or not info_dict['entries']:
                print("\nBłąd: Podany link nie jest prawidłową playlistą lub playlista jest pusta.")
                return

            first_video_url = info_dict['entries'][0]['url']
            with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
                video_info = ydl.extract_info(first_video_url, download=False)

            formaty_wideo = []
            for f in video_info.get('formats', []):
                if f.get('vcodec') != 'none' and f.get('ext') == 'mp4':
                    rozdzielczosc = f.get('format_note', f"{f.get('height')}p")
                    formaty_wideo.append({
                        'res': rozdzielczosc, 'height': f.get('height', 0)
                    })
            
            unique_formats = sorted(
                list({f['res']: f for f in formaty_wideo}.values()),
                key=lambda x: x['height'],
                reverse=True
            )

            if not unique_formats:
                print("Nie znaleziono dostępnych formatów wideo MP4 dla tej playlisty.")
                return

            print("\nWybierz rozdzielczość dla całej playlisty:")
            for i, f in enumerate(unique_formats):
                print(f"{i+1}. {f['res']}")
            
            wybor_formatu = int(input("Wybierz numer: ")) - 1

            if 0 <= wybor_formatu < len(unique_formats):
                # ZMIANA 1: Zamiast ID, pobieramy wysokość i nazwę rozdzielczości
                wybrana_wysokosc = unique_formats[wybor_formatu]['height']
                wybrana_res_str = unique_formats[wybor_formatu]['res']
                
                print(f"\nWybrano: {wybrana_res_str}. Rozpoczynam pobieranie playlisty...")
                
                ydl_opts = {
                    # ZMIANA 2: Używamy uniwersalnego selektora formatu opartego na wysokości
                    'format': f'bestvideo[height<={wybrana_wysokosc}][ext=mp4]+bestaudio/best[ext=mp4]',
                    # ZMIANA 3 (opcjonalna): Dodajemy rozdzielczość do nazwy pliku
                    'outtmpl': os.path.join(sciezka_pobierania, '%(playlist_title)s', f'%(playlist_index)s - %(title)s - {wybrana_res_str}.%(ext)s'),
                    'progress_hooks': [pokaz_postep],
                    'ignoreerrors': True,
                    'merge_output_format': 'mp4',
                }
            else:
                print("Błędny wybór.")
                return

        except Exception as e:
            print(f"Nie udało się przetworzyć playlisty: {e}")
            return
    # -- KONIEC FINALNEJ POPRAWKI --
    
    else:
        print("Nieprawidłowy wybór.")
        return

    # Sekcja końcowa bez zmian
    if ydl_opts:
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([link])
            print(f"\n\n✅ Pobieranie zakończone pomyślnie!")
            final_path_template = ydl_opts.get('outtmpl', '')
            
            if '%(playlist_title)s' in final_path_template:
                try:
                    with yt_dlp.YoutubeDL({'quiet': True, 'extract_flat': 'in_playlist'}) as ydl:
                        info = ydl.extract_info(link, download=False)
                        playlist_title = info.get('title', 'playlisty')
                        final_dir = os.path.join(sciezka_pobierania, playlist_title)
                        print(f"Pliki zostały zapisane w folderze: '{final_dir}'")
                except Exception:
                     print("Pliki powinny znajdować się w podfolderze o nazwie playlisty wewnątrz folderu 'Pobrane_yt-dlp'")
            else:
                print(f"Plik(i) zapisano w folderze: '{sciezka_pobierania}'")
                
        except yt_dlp.utils.DownloadError as e:
            print(f"\nBłąd: Nie udało się pobrać materiału. Sprawdź link lub błąd poniżej.")
            if "is not a valid URL" in str(e):
                print("Podany link jest nieprawidłowy.")
            else:
                print("Sprawdź swoje połączenie z internetem lub dostępność wideo/playlisty.")
        except Exception as e:
            print(f"\nWystąpił nieoczekiwany błąd: {e}")


if __name__ == "__main__":
    pobierz_materialy_yt()
