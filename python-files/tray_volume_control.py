#!/usr/bin/env python
# -*- coding: utf‑8 -*-

import threading, sys, os, time, configparser, subprocess
from pathlib import Path

import serial      # pyserial
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from ctypes import POINTER, cast
from comtypes import CLSCTX_ALL
import pystray     # sistem tepsisi simgesi
from PIL import Image, ImageDraw

CFG_PATH = Path(__file__).with_suffix('.ini')  # config.ini ile aynı klasörde

class VolumeController:
    """Ana ses düzeyini (master volume) 0‑100 aralığında ayarlayan sarmalayıcı."""
    def __init__(self):
        devices = AudioUtilities.GetSpeakers()
        iface   = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        self.vol = cast(iface, POINTER(IAudioEndpointVolume))

    def set_percent(self, pct: float):
        pct = max(0, min(100, pct))
        # VolumeScalar 0.0‑1.0
        self.vol.SetMasterVolumeLevelScalar(pct / 100.0, None)

class SerialReader(threading.Thread):
    """Arka planda seri portu dinler; pot değeri geldikçe sesi ayarlar."""
    def __init__(self, cfg, vol_ctl):
        super().__init__(daemon=True)
        self.cfg, self.vol_ctl = cfg, vol_ctl
        self._stop = threading.Event()
        self.sp = None

    def connect(self):
        if self.sp and self.sp.is_open:
            self.sp.close()
        self.sp = serial.Serial(
            port     = self.cfg['port'],
            baudrate = int(self.cfg['baudrate']),
            timeout  = 1
        )

    def run(self):
        while not self._stop.is_set():
            try:
                if not (self.sp and self.sp.is_open):
                    self.connect()
                line = self.sp.readline().decode().strip()      # “0‑1023”
                if line.isdigit():
                    raw = int(line)
                    pct = raw * 100 / 1023
                    self.vol_ctl.set_percent(pct)
            except serial.SerialException:
                time.sleep(1)   # bağlantı koptuysa tekrar dene
            except Exception:
                pass  # gürültü bastır

    def stop(self):
        self._stop.set()
        try:
            if self.sp: self.sp.close()
        except Exception:
            pass

def load_config():
    if not CFG_PATH.exists():
        # varsayılan dosyayı üret
        CFG_PATH.write_text('[serial]\nport = COM3\nbaudrate = 115200\n', encoding='utf‑8')
    parser = configparser.ConfigParser()
    parser.read(CFG_PATH, encoding='utf‑8')
    return parser['serial']

def open_config():
    # platform‑agnostik basit editör çağrısı
    if sys.platform == 'win32':
        os.startfile(CFG_PATH)
    else:
        subprocess.Popen(['xdg-open', str(CFG_PATH)])

def restart_app(icon, item):
    """Kendimizi yeniden başlat: mevcut işlemi kapat, yeni bir kopya çağır."""
    python = sys.executable
    os.execl(python, python, *sys.argv)

def create_image(size=64, color1='black', color2='white'):
    # basit daire‑kulakçık ikon
    img = Image.new('RGB', (size, size), color1)
    dc  = ImageDraw.Draw(img)
    dc.ellipse((8, 8, size-8, size-8), fill=color2)
    return img

def main():
    cfg      = load_config()
    vol_ctl  = VolumeController()
    ser_thr  = SerialReader(cfg, vol_ctl)
    ser_thr.start()

    # Sistem tepsisi simgesi
    icon = pystray.Icon(
        'PotVolume',
        create_image(),
        title='ESP Pot Volume',
        menu=pystray.Menu(
            pystray.MenuItem('Config dosyasını aç', lambda icon, item: open_config()),
            pystray.MenuItem('Yeniden yükle (Reload)', restart_app),
            pystray.MenuItem('Çık', lambda icon, item: icon.stop())
        )
    )

    icon.run()          # bloklanır

    # Tepsi menüsünden çıkıldığında:
    ser_thr.stop()

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass
