import subprocess
import sys
import threading
import pystray
from PIL import Image, ImageDraw

def display_switch(mode):
    # mode: "/internal" veya "/extend"
    subprocess.Popen(['DisplaySwitch.exe', mode])

def create_image():
    # Basit 16x16 ikon yapıyoruz
    image = Image.new('RGB', (16, 16), color='white')
    dc = ImageDraw.Draw(image)
    dc.rectangle([4, 4, 12, 12], fill='black')
    return image

def on_quit(icon, item):
    icon.stop()

def main():
    icon = pystray.Icon('display_switcher', create_image(), 'Ekran Seçici',
                        menu=pystray.Menu(
                            pystray.MenuItem('Tek Ekran (Yalnızca 1)', lambda _: display_switch('/internal')),
                            pystray.MenuItem('Genişlet (Extend)', lambda _: display_switch('/extend')),
                            pystray.MenuItem('Çıkış', on_quit)
                        ))

    # icon.run() bloklayıcı, arka planda thread ile çalıştırıyoruz
    threading.Thread(target=icon.run, daemon=True).start()

    # Ana thread kapanmasın diye sonsuz döngü
    try:
        while True:
            pass
    except KeyboardInterrupt:
        icon.stop()
        sys.exit()

if __name__ == '__main__':
    main()
