#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# ВНИМАНИЕ / IMPORTANT:
# Этот скрипт предназначен ТОЛЬКО для образовательных целей (EDUCATIONAL PURPOSES ONLY).
# Используйте его исключительно с явного согласия владельца ПК и носителя.
# Любое распространение или применение без INFORMED CONSENT нарушает этику и может противоречить закону.
# Автор и распространители не несут ответственности за неправомерное использование.
#
# Поведение:
# - Скачивает обои по заданной ссылке в TEMP и пытается установить их (Windows).
# - Работает и без флешки. Если флешка найдена — дополнительно:
#   * пишет лог на флешку (log.txt);
#   * копирует на флешку скачанные обои.
# - Если скачать не удалось, а флешка есть — пытается найти wallpaper.jpg/.png в корне флешки.
# - Для Linux/macOS — заглушка с пояснениями в лог.
# - Тихий режим: без окон/диалогов, только логирование.

import os
import sys
import ctypes
import shutil
import tempfile
import platform
import datetime
import traceback
from pathlib import Path
from typing import Optional

import urllib.request
import urllib.parse

WALLPAPER_URL = "https://www.meme-arsenal.com/memes/3a65af26fab4288fe2abad0ee9e92563.jpg"

# ------------------------ Вспомогательные функции ------------------------

def now_ts() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def safe_str(p: Path) -> str:
    try:
        return str(p)
    except Exception:
        return repr(p)

def get_script_path() -> Path:
    if getattr(sys, 'frozen', False):
        return Path(sys.executable).resolve()
    return Path(__file__).resolve()

def get_mount_root(path: Path) -> Path:
    # Корень точки монтирования для данного пути
    p = path
    try:
        while True:
            if os.path.ismount(str(p)):
                return p
            parent = p.parent
            if parent == p:
                return p
            p = parent
    except Exception:
        anchor = Path(path.anchor) if path.anchor else path
        return anchor

def list_removable_roots_windows() -> list[Path]:
    roots = []
    try:
        kernel32 = ctypes.windll.kernel32
        GetLogicalDrives = kernel32.GetLogicalDrives
        GetDriveTypeW = kernel32.GetDriveTypeW
        mask = GetLogicalDrives()
        for i in range(26):
            if mask & (1 << i):
                drive = f"{chr(65 + i)}:\\"
                try:
                    dtype = GetDriveTypeW(ctypes.c_wchar_p(drive))
                    if dtype == 2:  # DRIVE_REMOVABLE
                        roots.append(Path(drive))
                except Exception:
                    pass
    except Exception:
        pass
    return roots

def list_removable_roots_posix() -> list[Path]:
    roots = set()
    try:
        # типичные места для USB
        for base in ("/run/media", "/media"):
            bp = Path(base)
            if bp.exists():
                # уровни: /media/<user>/<label> и /media/<label>
                for cand in list(bp.glob("*/*")) + list(bp.glob("*")):
                    try:
                        if os.path.ismount(str(cand)):
                            roots.add(cand.resolve())
                    except Exception:
                        pass
        # macOS
        if platform.system() == "Darwin":
            vp = Path("/Volumes")
            if vp.exists():
                for cand in vp.glob("*"):
                    try:
                        if os.path.ismount(str(cand)):
                            roots.add(cand.resolve())
                    except Exception:
                        pass
        # Дополнительно Linux: /proc/mounts
        if sys.platform.startswith("linux"):
            try:
                with open("/proc/mounts", "r", encoding="utf-8", errors="ignore") as f:
                    for line in f:
                        parts = line.split()
                        if len(parts) >= 3:
                            mp = parts[1]
                            fstype = parts[2].lower()
                            if (mp.startswith("/media/") or mp.startswith("/run/media/")) and fstype in {
                                "vfat", "exfat", "ntfs", "fuseblk", "hfs", "hfsplus", "apfs", "msdos", "fat", "fat32", "udf"
                            }:
                                roots.add(Path(mp).resolve())
            except Exception:
                pass
    except Exception:
        pass
    return sorted(roots, key=lambda p: str(p).lower())

def list_removable_roots() -> list[Path]:
    if os.name == "nt":
        return list_removable_roots_windows()
    return list_removable_roots_posix()

def is_subpath(child: Path, parent: Path) -> bool:
    try:
        child_res = child.resolve()
        parent_res = parent.resolve()
        child_res.relative_to(parent_res)
        return True
    except Exception:
        return False

def find_wallpaper_in_root(root: Path) -> Optional[Path]:
    try:
        for entry in root.iterdir():
            if entry.is_file():
                name = entry.name.lower()
                if name in {"wallpaper.jpg", "wallpaper.png"}:
                    return entry
    except Exception:
        pass
    return None

def ensure_unique_path(dest: Path) -> Path:
    if not dest.exists():
        return dest
    parent = dest.parent
    stem = dest.stem
    ext = dest.suffix
    i = 1
    while True:
        cand = parent / f"{stem}_{i}{ext}"
        if not cand.exists():
            return cand
        i += 1

# ------------------------ Скачивание и копирование ------------------------

def download_to_temp(url: str, log) -> Optional[Path]:
    try:
        tdir = Path(tempfile.gettempdir())
        parsed = urllib.parse.urlparse(url)
        ext = Path(parsed.path).suffix.lower()
        if ext not in (".jpg", ".jpeg", ".png", ".bmp"):
            ext = ".jpg"
        dst = tdir / f"wallpaper_from_url{ext}"

        log.write("INFO", f"Пробую скачать обои: {url}")
        req = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Python-urllib"}
        )
        with urllib.request.urlopen(req, timeout=30) as resp:
            ctype = (resp.headers.get("Content-Type") or "").lower()
            if "jpeg" in ctype and ext not in (".jpg", ".jpeg"):
                ext = ".jpg"
            elif "png" in ctype and ext != ".png":
                ext = ".png"
            elif "bmp" in ctype and ext != ".bmp":
                ext = ".bmp"
            if "image" not in ctype:
                log.write("WARN", f"Content-Type не image/*: {ctype}. Продолжаю сохранение (предполагаю изображение).")
            dst = tdir / f"wallpaper_from_url{ext}"
            with open(dst, "wb") as f:
                shutil.copyfileobj(resp, f)

        log.write("INFO", f"Файл загружен в TEMP: {safe_str(dst)}")
        return dst
    except Exception as e:
        log.write("ERROR", f"Не удалось скачать файл по URL: {e}")
        log.write("DEBUG", traceback.format_exc())
        return None

def copy_to_temp(src: Path) -> Path:
    tdir = Path(tempfile.gettempdir())
    ext = src.suffix.lower() or ".jpg"
    dst = tdir / f"wallpaper_from_source{ext}"
    shutil.copy2(src, dst)
    return dst

def copy_image_to_usb(src: Path, usb_root: Path, log) -> Optional[Path]:
    try:
        ext = src.suffix.lower() or ".jpg"
        dst = usb_root / f"wallpaper_from_url{ext}"
        dst = ensure_unique_path(dst)
        shutil.copy2(src, dst)
        log.write("INFO", f"Скопировал обои на USB: {safe_str(dst)}")
        return dst
    except Exception as e:
        log.write("ERROR", f"Не удалось скопировать обои на USB: {e}")
        log.write("DEBUG", traceback.format_exc())
        return None

# ------------------------ Установка обоев ------------------------

def set_wallpaper_windows(image_path: Path) -> bool:
    try:
        SPI_SETDESKWALLPAPER = 20
        SPIF_UPDATEINIFILE = 0x01
        SPIF_SENDWININICHANGE = 0x02

        user32 = ctypes.windll.user32
        res = user32.SystemParametersInfoW(
            ctypes.c_uint(SPI_SETDESKWALLPAPER),
            ctypes.c_uint(0),
            ctypes.c_wchar_p(str(image_path)),
            ctypes.c_uint(SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE),
        )
        if res != 0:
            return True

        # Fallback: перезапись в реестр + повтор
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Desktop", 0, winreg.KEY_SET_VALUE) as key:
                # 10 — Fill (Windows 10/11), 2 — Stretch
                winreg.SetValueEx(key, "Wallpaper", 0, winreg.REG_SZ, str(image_path))
                winreg.SetValueEx(key, "WallpaperStyle", 0, winreg.REG_SZ, "10")
                winreg.SetValueEx(key, "TileWallpaper", 0, winreg.REG_SZ, "0")
            res2 = user32.SystemParametersInfoW(
                ctypes.c_uint(SPI_SETDESKWALLPAPER),
                ctypes.c_uint(0),
                ctypes.c_wchar_p(str(image_path)),
                ctypes.c_uint(SPIF_UPDATEINIFILE | SPIF_SENDWININICHANGE),
            )
            return res2 != 0
        except Exception:
            return False
    except Exception:
        return False

def set_wallpaper_stub(os_name: str) -> str:
    if os_name == "Darwin":
        return (
            "macOS: Заглушка. Установка обоев не выполнена, чтобы не тянуть зависимости. "
            "Можно вручную установить файл как обои или использовать osascript: "
            'osascript -e \'tell application "Finder" to set desktop picture to POSIX file "<путь_к_файлу>"\''
        )
    else:
        return (
            "Linux: Заглушка. Универсальной установки без внешних утилит нет. Варианты: "
            "GNOME — gsettings; KDE — qdbus; XFCE — xfconf-query (требуют наличия утилит)."
        )

# ------------------------ Логирование ------------------------

class MultiLogger:
    def __init__(self, paths: Optional[list[Path]] = None):
        self.paths = []
        if paths:
            for p in paths:
                self.add_path(p)

    def add_path(self, p: Path):
        try:
            p = Path(p)
            key = str(p.resolve()) if p.exists() else str(p)
            if key not in {str(x) for x in self.paths}:
                self.paths.append(p)
        except Exception:
            # Если resolve() не удался, всё равно добавим как есть
            if str(p) not in {str(x) for x in self.paths}:
                self.paths.append(p)

    def write(self, level: str, message: str):
        for p in self.paths:
            try:
                p.parent.mkdir(parents=True, exist_ok=True)
                with p.open("a", encoding="utf-8") as f:
                    f.write(f"[{now_ts()}] [{level}] {message}\n")
            except Exception:
                # Тихий режим — без вывода исключений
                pass

# ------------------------ Основной поток ------------------------

def main():
    script_path = get_script_path()
    script_mount = get_mount_root(script_path)

    # Лог по умолчанию — в TEMP (всегда доступен без прав)
    temp_log = Path(tempfile.gettempdir()) / "usb_wallpaper_log.txt"
    log = MultiLogger([temp_log])

    # По возможности — лог на флешке
    usb_roots = list_removable_roots()
    usb_root: Optional[Path] = None

    # Если сам скрипт на флешке — приоритет ей
    try:
        for r in usb_roots:
            if r.resolve() == script_mount.resolve():
                usb_root = r
                break
    except Exception:
        pass

    if usb_root is None and usb_roots:
        usb_root = usb_roots[0]

    if usb_root:
        log.add_path(usb_root / "log.txt")

    log.write("INFO", f"Запуск. Скрипт: {safe_str(script_path)}; Монтирование скрипта: {safe_str(script_mount)}; USB: {safe_str(usb_root) if usb_root else 'нет'}")

    # 1) Скачиваем обои
    image_path: Optional[Path] = download_to_temp(WALLPAPER_URL, log)

    # 2) Если не скачалось — пробуем с флешки (если есть)
    if image_path is None and usb_root is not None:
        src = find_wallpaper_in_root(usb_root)
        if src:
            try:
                image_path = copy_to_temp(src)
                log.write("INFO", f"Файл с флешки скопирован в TEMP: {safe_str(image_path)}")
            except Exception as e:
                log.write("ERROR", f"Не удалось скопировать файл с флешки в TEMP: {e}")
                log.write("DEBUG", traceback.format_exc())

    # Доп. запасной вариант (не обязателен): поиск рядом со скриптом
    if image_path is None:
        local_src = find_wallpaper_in_root(script_path.parent)
        if local_src:
            try:
                image_path = copy_to_temp(local_src)
                log.write("INFO", f"Найден локальный файл рядом со скриптом. Скопирован в TEMP: {safe_str(image_path)}")
            except Exception as e:
                log.write("ERROR", f"Не удалось скопировать локальный файл в TEMP: {e}")
                log.write("DEBUG", traceback.format_exc())

    if image_path is None:
        log.write("ERROR", "Не удалось получить файл обоев ни по URL, ни с флешки, ни локально. Завершение.")
        return

    # 3) Устанавливаем обои
    system = platform.system()
    if system == "Windows":
        ok = set_wallpaper_windows(image_path)
        if ok:
            log.write("INFO", "Обои успешно установлены (Windows).")
        else:
            log.write("ERROR", "Не удалось установить обои через WinAPI (Windows).")
    elif system in ("Linux", "Darwin"):
        note = set_wallpaper_stub(system)
        log.write("INFO", f"{note} Файл для ручной установки: {safe_str(image_path)}")
    else:
        log.write("WARN", f"Неизвестная ОС: {system}. Установка обоев не выполнялась.")

    # 4) Если есть флешка — копируем на неё обои (если файл ещё не на флешке)
    if usb_root:
        try:
            if not is_subpath(image_path, usb_root):
                copy_image_to_usb(image_path, usb_root, log)
            else:
                log.write("INFO", "Файл обоев уже находится на флешке — копирование не требуется.")
        except Exception as e:
            log.write("ERROR", f"Ошибка при копировании на USB: {e}")
            log.write("DEBUG", traceback.format_exc())

if __name__ == "__main__":
    main()