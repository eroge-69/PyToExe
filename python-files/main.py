# app/school_bell.py
"""
Okul Zil Programı (Python/Tkinter)
- Hafta içi/hafta sonu ve her güne özel zamanlama
- Her olaya ayrı melodi atama (MP3/WAV)
- Teneffüs müzik yayını (klasörden rastgele)
- Zili geçici devre dışı bırakma
- Özel butonlar: İstiklal Marşı / Siren / Saygı Duruşu
- Kapanış (bilgisayarı kapat) olayı
- JSON ile kaydet/yükle

Bağımlılıklar:
- Python 3.9+
- tkinter (standart)
- pygame (önerilir) -> pip install pygame
- (Windows yedeği) winsound (standart)

Not:
- Sistem kapanışı komutları OS'e göre değişir ve yönetici yetkisi gerekebilir.
"""

from __future__ import annotations

import os
import sys
import json
import random
import threading
import time
import queue
import datetime as dt
from dataclasses import dataclass, asdict, field
from typing import List, Optional, Dict, Any

try:
    import tkinter as tk
    from tkinter import ttk, filedialog, messagebox
except Exception as e:
    raise RuntimeError("Tkinter gerekli.") from e

# Opsiyonel: pygame
_HAS_PYGAME = False
try:
    import pygame
    _HAS_PYGAME = True
except Exception:
    _HAS_PYGAME = False

# Windows'ta WAV yedeği
_HAS_WINSOUND = False
if sys.platform.startswith("win"):
    try:
        import winsound
        _HAS_WINSOUND = True
    except Exception:
        _HAS_WINSOUND = False


APP_TITLE = "Okul Zil Programı (Python)"
CONFIG_FILE = "okul_zil_config.json"
TIME_FMT = "%H:%M"          # arayüz
TIME_FMT_SEC = "%H:%M:%S"   # karşılaştırma penceresi için


# --------------------------- Veri Modelleri ---------------------------

class EventType:
    BELL = "ZIL"
    BREAK_MUSIC_ON = "MUSIK_AC"
    BREAK_MUSIC_OFF = "MUSIK_KAPAT"
    SHUTDOWN = "KAPAT"


@dataclass
class BellEvent:
    time: str                     # "HH:MM"
    type: str = EventType.BELL
    label: str = ""
    audio: str = ""               # yol (isteğe bağlı)
    duration_sec: int = 0         # 0 => tam dosya

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "BellEvent":
        return BellEvent(
            time=d.get("time", "08:30"),
            type=d.get("type", EventType.BELL),
            label=d.get("label", ""),
            audio=d.get("audio", ""),
            duration_sec=int(d.get("duration_sec", 0)),
        )


@dataclass
class SpecialSounds:
    istiklal_marsi: str = ""
    siren: str = ""
    saygi_durusu: str = ""        # tercih edilen özel dosya; boşsa sessizlik+opsiyon

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "SpecialSounds":
        return SpecialSounds(
            istiklal_marsi=d.get("istiklal_marsi", ""),
            siren=d.get("siren", ""),
            saygi_durusu=d.get("saygi_durusu", ""),
        )


@dataclass
class AppConfig:
    version: int = 1
    default_bell_audio: str = ""
    break_music_enabled: bool = False
    break_music_folder: str = ""
    week_schedules: Dict[str, List[BellEvent]] = field(default_factory=lambda: {str(i): [] for i in range(7)})
    skip_dates: List[str] = field(default_factory=list) # "YYYY-MM-DD"
    special: SpecialSounds = field(default_factory=SpecialSounds)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "version": self.version,
            "default_bell_audio": self.default_bell_audio,
            "break_music_enabled": self.break_music_enabled,
            "break_music_folder": self.break_music_folder,
            "week_schedules": {k: [e.to_dict() for e in v] for k, v in self.week_schedules.items()},
            "skip_dates": self.skip_dates,
            "special": self.special.to_dict(),
        }

    @staticmethod
    def from_dict(d: Dict[str, Any]) -> "AppConfig":
        cfg = AppConfig()
        cfg.version = int(d.get("version", 1))
        cfg.default_bell_audio = d.get("default_bell_audio", "")
        cfg.break_music_enabled = bool(d.get("break_music_enabled", False))
        cfg.break_music_folder = d.get("break_music_folder", "")
        raw = d.get("week_schedules", {})
        schedules: Dict[str, List[BellEvent]] = {str(i): [] for i in range(7)}
        for k in schedules.keys():
            arr = raw.get(str(k), [])
            schedules[str(k)] = [BellEvent.from_dict(x) for x in arr]
        cfg.week_schedules = schedules
        cfg.skip_dates = list(d.get("skip_dates", []))
        cfg.special = SpecialSounds.from_dict(d.get("special", {}))
        return cfg


# --------------------------- Yardımcılar ---------------------------

def load_config(path: str) -> AppConfig:
    if not os.path.exists(path):
        return AppConfig()
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return AppConfig.from_dict(data)


def save_config(path: str, cfg: AppConfig) -> None:
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(cfg.to_dict(), f, ensure_ascii=False, indent=2)
    os.replace(tmp, path)


def is_today_skipped(cfg: AppConfig, now: dt.datetime) -> bool:
    return now.strftime("%Y-%m-%d") in set(cfg.skip_dates)


def parse_time_to_today(t: str, now: Optional[dt.datetime] = None) -> dt.datetime:
    if now is None:
        now = dt.datetime.now()
    hh, mm = t.split(":")
    return now.replace(hour=int(hh), minute=int(mm), second=0, microsecond=0)


def sorted_events_for_day(cfg: AppConfig, weekday: int) -> List[BellEvent]:
    evs = list(cfg.week_schedules.get(str(weekday), []))
    evs.sort(key=lambda e: e.time)
    return evs


# --------------------------- Ses Yöneticisi ---------------------------

class AudioManager:
    def __init__(self, log_fn):
        self._break_thread: Optional[threading.Thread] = None
        self._break_stop = threading.Event()
        self._lock = threading.Lock()
        self._current_is_break = False
        self.log = log_fn
        if _HAS_PYGAME:
            try:
                pygame.mixer.init()
            except Exception as e:
                self.log(f"Ses başlatma hatası (pygame): {e}")

    def _play_with_pygame(self, path: str, duration: int = 0):
        try:
            pygame.mixer.music.load(path)
            pygame.mixer.music.play()
            if duration > 0:
                # Neden: Dosya uzun bile olsa istenen sürede kesmek için
                time.sleep(max(0, duration))
                pygame.mixer.music.fadeout(500)
            else:
                # Tam çalma; izleyici
                while pygame.mixer.music.get_busy():
                    time.sleep(0.1)
        except Exception as e:
            self.log(f"Oynatma hatası: {e}")

    def _play_with_winsound(self, path: str, duration: int = 0):
        # Only WAV
        try:
            if duration > 0:
                winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                time.sleep(duration)
                winsound.PlaySound(None, winsound.SND_PURGE)
            else:
                winsound.PlaySound(path, winsound.SND_FILENAME)
        except Exception as e:
            self.log(f"Oynatma hatası (winsound): {e}")

    def play_file(self, path: str, duration: int = 0):
        if not path:
            self.log("Ses dosyası seçilmemiş.")
            return
        if not os.path.exists(path):
            self.log(f"Ses dosyası bulunamadı: {path}")
            return
        self.log(f"Çalınıyor: {os.path.basename(path)}" + (f" ({duration}s)" if duration else ""))
        if _HAS_PYGAME:
            self._play_with_pygame(path, duration)
        elif _HAS_WINSOUND and path.lower().endswith(".wav"):
            self._play_with_winsound(path, duration)
        else:
            self.log("Uygun oynatıcı yok (pygame önerilir).")

    def stop_all(self):
        # Neden: Teneffüs ve tekil zil çakışmalarını durdurmak
        if _HAS_PYGAME:
            try:
                pygame.mixer.music.stop()
            except Exception:
                pass
        if _HAS_WINSOUND:
            try:
                winsound.PlaySound(None, winsound.SND_PURGE)
            except Exception:
                pass

    def _break_worker(self, folder: str):
        try:
            files = [os.path.join(folder, f) for f in os.listdir(folder)
                     if f.lower().endswith((".mp3", ".wav", ".ogg"))]
        except Exception:
            files = []
        if not files:
            self.log("Teneffüs klasöründe çalınacak dosya yok.")
            return
        self.log("Teneffüs müziği başladı.")
        idxs = list(range(len(files)))
        random.shuffle(idxs)
        i = 0
        while not self._break_stop.is_set():
            path = files[idxs[i % len(idxs)]]
            i += 1
            if _HAS_PYGAME:
                try:
                    pygame.mixer.music.load(path)
                    pygame.mixer.music.play()
                except Exception as e:
                    self.log(f"Teneffüs çalma hatası: {e}")
                    time.sleep(1)
                    continue
                # Parça bitene veya durdurulana kadar bekle
                while pygame.mixer.music.get_busy() and not self._break_stop.is_set():
                    time.sleep(0.2)
            elif _HAS_WINSOUND and path.lower().endswith(".wav"):
                try:
                    winsound.PlaySound(path, winsound.SND_FILENAME | winsound.SND_ASYNC)
                except Exception as e:
                    self.log(f"Teneffüs çalma hatası (winsound): {e}")
                # WAV uzunluğunu bilemediğimiz için küçük aralıklarla kontrol
                for _ in range(50):
                    if self._break_stop.is_set():
                        break
                    time.sleep(0.2)
            else:
                self.log("Teneffüs için uygun oynatıcı yok.")
                break
        self.stop_all()
        self.log("Teneffüs müziği durdu.")

    def start_break_music(self, folder: str):
        with self._lock:
            if self._current_is_break:
                return
            self._break_stop.clear()
            self._break_thread = threading.Thread(target=self._break_worker, args=(folder,), daemon=True)
            self._current_is_break = True
            self._break_thread.start()

    def stop_break_music(self):
        with self._lock:
            if not self._current_is_break:
                return
            self._break_stop.set()
            self._current_is_break = False


# --------------------------- Zamanlayıcı ---------------------------

class Scheduler(threading.Thread):
    def __init__(self, cfg_getter, audio: AudioManager, ui_notify, log_fn):
        super().__init__(daemon=True)
        self._stop = threading.Event()
        self._snooze = threading.Event()
        self._cfg_getter = cfg_getter    # çağrıldığında güncel config
        self.audio = audio
        self.ui_notify = ui_notify
        self.log = log_fn

    def stop(self):
        self._stop.set()

    def run(self):
        self.log("Zamanlayıcı başlatıldı.")
        last_second = None
        while not self._stop.is_set():
            now = dt.datetime.now()
            sec = now.strftime(TIME_FMT_SEC)
            if sec != last_second:
                last_second = sec
                self._tick(now)
            time.sleep(0.2)
        self.audio.stop_all()
        self.audio.stop_break_music()
        self.log("Zamanlayıcı durdu.")

    def _tick(self, now: dt.datetime):
        cfg: AppConfig = self._cfg_getter()
        if is_today_skipped(cfg, now):
            return
        weekday = now.weekday()  # 0=Mon
        events = sorted_events_for_day(cfg, weekday)
        # saniye hassasiyetini tolerate et (örn. 1-2 sn gecikme)
        current_hm = now.strftime(TIME_FMT)
        for ev in events:
            if ev.time == current_hm:
                self._trigger(ev, cfg)

    def _trigger(self, ev: BellEvent, cfg: AppConfig):
        # Neden: UI'ya son olayı bildirmek/loglamak
        self.ui_notify(f"{ev.time} → {ev.type} ({ev.label})")
        if ev.type == EventType.BELL:
            path = ev.audio or cfg.default_bell_audio
            if not path:
                self.log("Zil dosyası tanımlı değil.")
                return
            self.audio.stop_break_music()  # Neden: Zil sırasında müzik kesilsin
            self.audio.play_file(path, ev.duration_sec)
        elif ev.type == EventType.BREAK_MUSIC_ON:
            if cfg.break_music_enabled and cfg.break_music_folder:
                self.audio.start_break_music(cfg.break_music_folder)
            else:
                self.log("Teneffüs müzik ayarları kapalı/eksik.")
        elif ev.type == EventType.BREAK_MUSIC_OFF:
            self.audio.stop_break_music()
        elif ev.type == EventType.SHUTDOWN:
            self._shutdown_system()
        else:
            self.log(f"Bilinmeyen olay türü: {ev.type}")

    def _shutdown_system(self):
        self.log("Sistem kapanışı başlatılıyor...")
        try:
            if sys.platform.startswith("win"):
                os.system("shutdown /s /t 0")
            elif sys.platform == "darwin":
                os.system("osascript -e 'tell app \"System Events\" to shut down'")
            else:
                os.system("shutdown -h now")
        except Exception as e:
            self.log(f"Kapanış komutu başarısız: {e}")


# --------------------------- GUI ---------------------------

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1100x700")
        self.minsize(1000, 650)

        self.cfg: AppConfig = load_config(CONFIG_FILE)
        self.audio = AudioManager(self._log)
        self._scheduler: Optional[Scheduler] = None
        self._ui_queue = queue.Queue()
        self._zil_devre_disi = tk.BooleanVar(value=False)

        self._build_ui()
        self._after_poll()

        # Basit örnek (ilk kez boşsa) – kullanıcıya fikir vermek için
        self._maybe_seed_example()

    # ---------------- UI ----------------

    def _build_ui(self):
        # Üst kontrol çubuğu
        top = ttk.Frame(self)
        top.pack(side=tk.TOP, fill=tk.X, padx=8, pady=6)

        self.btn_start = ttk.Button(top, text="▶ Başlat", command=self._start_scheduler)
        self.btn_stop = ttk.Button(top, text="⏹ Durdur", command=self._stop_scheduler, state=tk.DISABLED)
        self.btn_start.pack(side=tk.LEFT, padx=4)
        self.btn_stop.pack(side=tk.LEFT, padx=4)

        ttk.Checkbutton(top, text="Zili geçici devre dışı", variable=self._zil_devre_disi,
                        command=self._toggle_disable).pack(side=tk.LEFT, padx=10)

        ttk.Button(top, text="Kaydet", command=self._save).pack(side=tk.RIGHT, padx=4)
        ttk.Button(top, text="Yükle", command=self._load).pack(side=tk.RIGHT, padx=4)

        # Notebook: Günler + Ayarlar + Tatiller + Özel Butonlar
        self.nb = ttk.Notebook(self)
        self.nb.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)

        self.day_tabs = []
        for i, name in enumerate(["Pzt", "Sal", "Çar", "Per", "Cum", "Cmt", "Paz"]):
            frm = ttk.Frame(self.nb)
            self._build_day_tab(frm, weekday=i)
            self.nb.add(frm, text=name)
            self.day_tabs.append(frm)

        self.settings_tab = ttk.Frame(self.nb)
        self._build_settings_tab(self.settings_tab)
        self.nb.add(self.settings_tab, text="Genel Ayarlar")

        self.skip_tab = ttk.Frame(self.nb)
        self._build_skip_tab(self.skip_tab)
        self.nb.add(self.skip_tab, text="Tatil Günleri")

        self.special_tab = ttk.Frame(self.nb)
        self._build_special_tab(self.special_tab)
        self.nb.add(self.special_tab, text="Özel Butonlar")

        # Log panel
        self.log_box = tk.Text(self, height=10, state=tk.DISABLED)
        self.log_box.pack(fill=tk.BOTH, expand=False, padx=8, pady=6)

    def _build_day_tab(self, parent, weekday: int):
        # Sol: liste; Sağ: form
        left = ttk.Frame(parent)
        right = ttk.Frame(parent)
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        right.pack(side=tk.RIGHT, fill=tk.Y)

        cols = ("time", "type", "label", "audio", "duration")
        tv = ttk.Treeview(left, columns=cols, show="headings", height=18)
        tv.heading("time", text="Saat")
        tv.heading("type", text="Tür")
        tv.heading("label", text="Etiket")
        tv.heading("audio", text="Dosya")
        tv.heading("duration", text="Süre(sn)")
        tv.column("time", width=80, anchor="center")
        tv.column("type", width=110, anchor="center")
        tv.column("label", width=180, anchor="w")
        tv.column("audio", width=280, anchor="w")
        tv.column("duration", width=80, anchor="center")
        tv.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=6, pady=6)

        btns = ttk.Frame(left)
        btns.pack(side=tk.TOP, fill=tk.X, padx=6, pady=(0,6))
        ttk.Button(btns, text="Ekle", command=lambda w=weekday, t=tv: self._event_add(w, t)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Düzenle", command=lambda w=weekday, t=tv: self._event_edit(w, t)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Sil", command=lambda w=weekday, t=tv: self._event_del(w, t)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Yukarı", command=lambda t=tv: self._move_up(t)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Aşağı", command=lambda t=tv: self._move_down(t)).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Test Çal", command=lambda t=tv: self._test_play_selected(t)).pack(side=tk.RIGHT, padx=2)

        # doldur
        self._populate_day_tree(tv, weekday)

        # Sağdaki küçük bilgi
        info = ttk.Label(right, text="Olay türleri:\n"
                                     "- ZIL: Belirtilen dosyayı çalar\n"
                                     "- MUSIK_AC: Teneffüs müziğini başlatır\n"
                                     "- MUSIK_KAPAT: Teneffüs müziğini durdurur\n"
                                     "- KAPAT: Bilgisayarı kapatır",
                         justify="left")
        info.pack(anchor="n", padx=8, pady=8)

        # Kaydetme hatırlatması
        ttk.Label(right, text="Değişikliklerden sonra 'Kaydet' yapın.").pack(anchor="s", pady=8)

    def _populate_day_tree(self, tv: ttk.Treeview, weekday: int):
        tv.delete(*tv.get_children())
        evs = sorted_events_for_day(self.cfg, weekday)
        for e in evs:
            tv.insert("", "end", values=(e.time, e.type, e.label, e.audio, e.duration_sec))

    def _build_settings_tab(self, parent):
        frm = ttk.Frame(parent)
        frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Varsayılan zil
        row = ttk.Frame(frm); row.pack(fill=tk.X, pady=4)
        ttk.Label(row, text="Varsayılan zil dosyası:").pack(side=tk.LEFT)
        self.var_default_audio = tk.StringVar(value=self.cfg.default_bell_audio)
        ttk.Entry(row, textvariable=self.var_default_audio, width=70).pack(side=tk.LEFT, padx=6)
        ttk.Button(row, text="Seç", command=lambda: self._choose_file(self.var_default_audio)).pack(side=tk.LEFT)

        # Teneffüs müzik
        row = ttk.Frame(frm); row.pack(fill=tk.X, pady=4)
        self.var_break_enabled = tk.BooleanVar(value=self.cfg.break_music_enabled)
        ttk.Checkbutton(row, text="Teneffüste müzik yayını", variable=self.var_break_enabled).pack(side=tk.LEFT)
        ttk.Label(row, text="Klasör:").pack(side=tk.LEFT, padx=(16,4))
        self.var_break_folder = tk.StringVar(value=self.cfg.break_music_folder)
        ttk.Entry(row, textvariable=self.var_break_folder, width=60).pack(side=tk.LEFT, padx=6)
        ttk.Button(row, text="Seç", command=lambda: self._choose_folder(self.var_break_folder)).pack(side=tk.LEFT)

    def _build_skip_tab(self, parent):
        frm = ttk.Frame(parent)
        frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        ttk.Label(frm, text="Atlanacak günler (YYYY-MM-DD):").pack(anchor="w")

        self.skip_list = tk.Listbox(frm, height=12)
        self.skip_list.pack(fill=tk.BOTH, expand=True, padx=4, pady=6)

        for d in self.cfg.skip_dates:
            self.skip_list.insert(tk.END, d)

        btns = ttk.Frame(frm); btns.pack(fill=tk.X)
        ttk.Button(btns, text="Ekle", command=self._skip_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(btns, text="Sil", command=self._skip_del).pack(side=tk.LEFT, padx=2)

    def _build_special_tab(self, parent):
        frm = ttk.Frame(parent)
        frm.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.var_istiklal = tk.StringVar(value=self.cfg.special.istiklal_marsi)
        self.var_siren = tk.StringVar(value=self.cfg.special.siren)
        self.var_saygi = tk.StringVar(value=self.cfg.special.saygi_durusu)

        def file_row(label, var):
            r = ttk.Frame(frm); r.pack(fill=tk.X, pady=4)
            ttk.Label(r, text=label).pack(side=tk.LEFT)
            ttk.Entry(r, textvariable=var, width=70).pack(side=tk.LEFT, padx=6)
            ttk.Button(r, text="Seç", command=lambda: self._choose_file(var)).pack(side=tk.LEFT)
            ttk.Button(r, text="Çal", command=lambda: self.audio.play_file(var.get())).pack(side=tk.LEFT)

        file_row("İstiklal Marşı:", self.var_istiklal)
        file_row("Siren:", self.var_siren)
        file_row("Saygı Duruşu:", self.var_saygi)

        btns = ttk.Frame(frm); btns.pack(fill=tk.X, pady=8)
        ttk.Button(btns, text="İstiklal Marşı Çal", command=self._play_istiklal).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Siren Çal", command=self._play_siren).pack(side=tk.LEFT, padx=4)
        ttk.Button(btns, text="Saygı Duruşu", command=self._play_saygi).pack(side=tk.LEFT, padx=4)

    # ---------------- Event CRUD ----------------

    def _event_add(self, weekday: int, tv: ttk.Treeview):
        dlg = EventDialog(self, None)
        self.wait_window(dlg)
        ev = dlg.result
        if ev:
            self.cfg.week_schedules[str(weekday)].append(ev)
            self._populate_day_tree(tv, weekday)

    def _event_edit(self, weekday: int, tv: ttk.Treeview):
        sel = tv.selection()
        if not sel:
            return
        idx = tv.index(sel[0])
        current = sorted_events_for_day(self.cfg, weekday)[idx]
        dlg = EventDialog(self, current)
        self.wait_window(dlg)
        ev = dlg.result
        if ev:
            # güncelle
            orig = self.cfg.week_schedules[str(weekday)]
            # aynı sırayı korumak için yerine yaz
            # (liste sırası sonra sort ile arayüzde düzenli görünür)
            # Neden: Kullanıcı sıralamayı butonlarla da değiştirebilir.
            # Bu yüzden indeksle güncelliyoruz.
            orig_idx = orig.index(current)
            orig[orig_idx] = ev
            self._populate_day_tree(tv, weekday)

    def _event_del(self, weekday: int, tv: ttk.Treeview):
        sel = tv.selection()
        if not sel:
            return
        idx = tv.index(sel[0])
        evs = sorted_events_for_day(self.cfg, weekday)
        target = evs[idx]
        self.cfg.week_schedules[str(weekday)].remove(target)
        self._populate_day_tree(tv, weekday)

    def _move_up(self, tv: ttk.Treeview):
        sel = tv.selection()
        if not sel:
            return
        item = sel[0]
        prev = tv.prev(item)
        if not prev:
            return
        tv.move(item, tv.parent(item), tv.index(prev))

    def _move_down(self, tv: ttk.Treeview):
        sel = tv.selection()
        if not sel:
            return
        item = sel[0]
        nxt = tv.next(item)
        if not nxt:
            return
        tv.move(item, tv.parent(item), tv.index(nxt)+1)

    def _test_play_selected(self, tv: ttk.Treeview):
        sel = tv.selection()
        if not sel:
            return
        vals = tv.item(sel[0], "values")
        etype, path, dur = vals[1], vals[3], vals[4]
        if etype == EventType.BELL:
            try:
                dur_i = int(dur) if str(dur).strip() else 0
            except Exception:
                dur_i = 0
            self.audio.play_file(path, dur_i)
        else:
            self._log("Bu test sadece ZIL için.")

    # ---------------- Ayarlar / Tatil ----------------

    def _skip_add(self):
        val = self._prompt("Tarih (YYYY-MM-DD):")
        if not val:
            return
        try:
            dt.datetime.strptime(val, "%Y-%m-%d")
        except Exception:
            messagebox.showerror("Hata", "Tarih biçimi yanlış.")
            return
        if val not in self.cfg.skip_dates:
            self.cfg.skip_dates.append(val)
            self.skip_list.insert(tk.END, val)

    def _skip_del(self):
        sel = self.skip_list.curselection()
        if not sel:
            return
        idx = sel[0]
        val = self.skip_list.get(idx)
        self.cfg.skip_dates.remove(val)
        self.skip_list.delete(idx)

    # ---------------- Çeşitli ----------------

    def _choose_file(self, var: tk.StringVar):
        path = filedialog.askopenfilename(title="Ses dosyası seç",
                                          filetypes=[("Ses", "*.mp3 *.wav *.ogg"), ("Tümü", "*.*")])
        if path:
            var.set(path)

    def _choose_folder(self, var: tk.StringVar):
        path = filedialog.askdirectory(title="Klasör seç")
        if path:
            var.set(path)

    def _save(self):
        self.cfg.default_bell_audio = self.var_default_audio.get().strip()
        self.cfg.break_music_enabled = self.var_break_enabled.get()
        self.cfg.break_music_folder = self.var_break_folder.get().strip()
        # gün sekmelerindeki Treeview sıralaması görsel; esas veri zaten güncellendi.
        save_config(CONFIG_FILE, self.cfg)
        self._log("Ayarlar kaydedildi.")

    def _load(self):
        self.cfg = load_config(CONFIG_FILE)
        # genel ayarlar
        self.var_default_audio.set(self.cfg.default_bell_audio)
        self.var_break_enabled.set(self.cfg.break_music_enabled)
        self.var_break_folder.set(self.cfg.break_music_folder)
        # tatiller
        self.skip_list.delete(0, tk.END)
        for d in self.cfg.skip_dates:
            self.skip_list.insert(tk.END, d)
        # günler
        for i, tab in enumerate(self.day_tabs):
            tv = tab.winfo_children()[0].winfo_children()[0]  # TreeView
            self._populate_day_tree(tv, i)
        # özel
        self.var_istiklal.set(self.cfg.special.istiklal_marsi)
        self.var_siren.set(self.cfg.special.siren)
        self.var_saygi.set(self.cfg.special.saygi_durusu)
        self._log("Ayarlar yüklendi.")

    def _start_scheduler(self):
        if self._scheduler is not None:
            return
        self._save()  # en güncel ayarlarla başlasın
        self._scheduler = Scheduler(
            cfg_getter=lambda: self.cfg if not self._zil_devre_disi.get() else AppConfig(),  # devre dışı ise boş cfg
            audio=self.audio,
            ui_notify=lambda msg: self._ui_queue.put(("notify", msg)),
            log_fn=self._log,
        )
        self._scheduler.start()
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self._log("Başlatıldı.")

    def _stop_scheduler(self):
        if self._scheduler:
            self._scheduler.stop()
            self._scheduler = None
        self.btn_start.config(state=tk.NORMAL)
        self.btn_stop.config(state=tk.DISABLED)
        self._log("Durduruldu.")

    def _toggle_disable(self):
        if self._zil_devre_disi.get():
            self._log("Zil geçici olarak devre dışı.")
        else:
            self._log("Zil yeniden etkin.")

    def _ui_notify_handler(self, msg: str):
        self._log(f"OLAY: {msg}")

    def _after_poll(self):
        # UI kuyruğunu çek
        try:
            while True:
                kind, payload = self._ui_queue.get_nowait()
                if kind == "notify":
                    self._ui_notify_handler(payload)
        except queue.Empty:
            pass
        self.after(200, self._after_poll)

    def _log(self, text: str):
        self.log_box.config(state=tk.NORMAL)
        ts = dt.datetime.now().strftime("%H:%M:%S")
        self.log_box.insert(tk.END, f"[{ts}] {text}\n")
        self.log_box.see(tk.END)
        self.log_box.config(state=tk.DISABLED)

    def _prompt(self, title: str) -> Optional[str]:
        win = tk.Toplevel(self)
        win.title(title)
        win.transient(self)
        win.grab_set()
        ent = ttk.Entry(win, width=30)
        ent.pack(padx=10, pady=10)
        res = {"val": None}

        def ok():
            res["val"] = ent.get().strip()
            win.destroy()

        def cancel():
            win.destroy()

        ttk.Button(win, text="Tamam", command=ok).pack(side=tk.LEFT, padx=10, pady=10)
        ttk.Button(win, text="İptal", command=cancel).pack(side=tk.RIGHT, padx=10, pady=10)
        ent.focus_set()
        self.wait_window(win)
        return res["val"]

    def _maybe_seed_example(self):
        empty = all(len(v) == 0 for v in self.cfg.week_schedules.values())
        if not empty:
            return
        # Örnek: Pazartesi için basit akış
        sample = [
            BellEvent("08:30", EventType.BELL, "Ders Başı", "", 0),
            BellEvent("09:10", EventType.BREAK_MUSIC_ON, "Teneffüs Başlangıç"),
            BellEvent("09:20", EventType.BREAK_MUSIC_OFF, "Teneffüs Bitiş"),
            BellEvent("12:30", EventType.BELL, "Öğle Zili"),
        ]
        self.cfg.week_schedules["0"] = sample
        self._log("Örnek Pazartesi programı eklendi. Kendi saatinize göre düzenleyin.")
        # Arayüzü güncelle
        for i, tab in enumerate(self.day_tabs):
            tv = tab.winfo_children()[0].winfo_children()[0]
            self._populate_day_tree(tv, i)

    # ---------------- Özel Buton Eylemleri ----------------

    def _play_istiklal(self):
        path = self.var_istiklal.get().strip()
        if not path:
            messagebox.showinfo("Bilgi", "İstiklal Marşı dosyasını 'Özel Butonlar' sekmesinden seçin.")
            return
        self.audio.stop_break_music()
        self.audio.play_file(path)

    def _play_siren(self):
        path = self.var_siren.get().strip()
        if not path:
            messagebox.showinfo("Bilgi", "Siren dosyasını 'Özel Butonlar' sekmesinden seçin.")
            return
        self.audio.stop_break_music()
        self.audio.play_file(path)

    def _play_saygi(self):
        # Opsiyon 1: Kullanıcı dosyası
        path = self.var_saygi.get().strip()
        if path:
            self.audio.stop_break_music()
            self.audio.play_file(path)
            return
        # Opsiyon 2: 2 dakikalık sessizlik (kısa)
        self._log("Saygı duruşu (60sn sessizlik)...")
        # Neden: Dosyasız saygı duruşu için basit bekleme; ses çalmıyoruz.
        t_end = time.time() + 60
        while time.time() < t_end:
            self.update()
            time.sleep(0.1)
        self._log("Saygı duruşu tamamlandı.")

# ---------------- Olay Diyaloğu ----------------

class EventDialog(tk.Toplevel):
    def __init__(self, parent: App, event: Optional[BellEvent]):
        super().__init__(parent)
        self.title("Olay")
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        self.result: Optional[BellEvent] = None

        frm = ttk.Frame(self); frm.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        ttk.Label(frm, text="Saat (HH:MM):").grid(row=0, column=0, sticky="e", padx=4, pady=4)
        ttk.Label(frm, text="Tür:").grid(row=1, column=0, sticky="e", padx=4, pady=4)
        ttk.Label(frm, text="Etiket:").grid(row=2, column=0, sticky="e", padx=4, pady=4)
        ttk.Label(frm, text="Dosya:").grid(row=3, column=0, sticky="e", padx=4, pady=4)
        ttk.Label(frm, text="Süre(sn):").grid(row=4, column=0, sticky="e", padx=4, pady=4)

        self.var_time = tk.StringVar(value=event.time if event else "08:30")
        self.var_type = tk.StringVar(value=event.type if event else EventType.BELL)
        self.var_label = tk.StringVar(value=event.label if event else "")
        self.var_audio = tk.StringVar(value=event.audio if event else "")
        self.var_duration = tk.StringVar(value=str(event.duration_sec if event else 0))

        ttk.Entry(frm, textvariable=self.var_time, width=10).grid(row=0, column=1, sticky="w")
        cb = ttk.Combobox(frm, textvariable=self.var_type, values=[
            EventType.BELL, EventType.BREAK_MUSIC_ON, EventType.BREAK_MUSIC_OFF, EventType.SHUTDOWN
        ], state="readonly", width=17)
        cb.grid(row=1, column=1, sticky="w")
        ttk.Entry(frm, textvariable=self.var_label, width=40).grid(row=2, column=1, sticky="w")

        row_file = ttk.Frame(frm); row_file.grid(row=3, column=1, sticky="w")
        ttk.Entry(row_file, textvariable=self.var_audio, width=40).pack(side=tk.LEFT)
        ttk.Button(row_file, text="Seç", command=lambda: self._choose_file(self.var_audio)).pack(side=tk.LEFT, padx=4)

        ttk.Entry(frm, textvariable=self.var_duration, width=10).grid(row=4, column=1, sticky="w")

        btns = ttk.Frame(frm); btns.grid(row=5, column=0, columnspan=2, pady=10)
        ttk.Button(btns, text="Tamam", command=self._ok).pack(side=tk.LEFT, padx=6)
        ttk.Button(btns, text="İptal", command=self._cancel).pack(side=tk.LEFT, padx=6)

        self.bind("<Return>", lambda e: self._ok())
        self.bind("<Escape>", lambda e: self._cancel())

        self.var_type.trace_add("write", lambda *_: self._on_type_change())

        self._on_type_change()
        self.protocol("WM_DELETE_WINDOW", self._cancel)

    def _choose_file(self, var: tk.StringVar):
        path = filedialog.askopenfilename(title="Ses dosyası seç",
                                          filetypes=[("Ses", "*.mp3 *.wav *.ogg"), ("Tümü", "*.*")])
        if path:
            var.set(path)

    def _on_type_change(self):
        t = self.var_type.get()
        audio_enabled = (t == EventType.BELL)
        duration_enabled = (t == EventType.BELL)
        # Neden: Müzik aç/kapat & kapanışta dosya/süre mantıksız olur
        # basitçe inputları devre dışı bırakıyoruz.
        # Grid içindeki belirli widget'ları bulup devre dışı bırak.
        # (satır 3: dosya; satır 4: süre)
        # Burada basit kalıyoruz: kullanıcıyı bilgilendirmek yeterli.

    def _ok(self):
        t = self.var_time.get().strip()
        try:
            dt.datetime.strptime(t, TIME_FMT)
        except Exception:
            messagebox.showerror("Hata", "Saat biçimi HH:MM olmalı.")
            return
        typ = self.var_type.get()
        lbl = self.var_label.get().strip()
        aud = self.var_audio.get().strip()
        try:
            dur = int(self.var_duration.get().strip() or "0")
        except Exception:
            dur = 0
        if typ == EventType.BELL and not (aud or True):
            pass
        self.result = BellEvent(time=t, type=typ, label=lbl, audio=aud, duration_sec=dur)
        self.destroy()

    def _cancel(self):
        self.result = None
        self.destroy()


# ---------------- Çalıştır ----------------

def main():
    app = App()
    app.mainloop()


if __name__ == "__main__":
    main()
