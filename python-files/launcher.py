import multiprocessing
import os
import logging
from logging.handlers import RotatingFileHandler
import time
import flet as ft
import minecraft_launcher_lib as mcl
import sys
import subprocess
import threading
import shutil
import requests
import re
import zipfile
import urllib3
import glob
from urllib.parse import urlparse, urlunparse
import tempfile
import colorsys
import urllib.request

try:
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')
except Exception:
    pass

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

ip = "192.168.100.204"
BASE_SCHEME = "https"

def make_base_url():
    return f"{BASE_SCHEME}://{ip}"

def swap_scheme(url: str):
    parts = list(urlparse(url))
    parts[0] = "http" if parts[0] == "https" else "https"
    return urlunparse(parts)

current_version = 4.0
status_version = "Big Fun"

IS_BUSY = False
JAVA_READY = False
LAST_JAVA_VERSION_LOGGED = None
GAME_PROC = None
GAME_RUNNING = False
LAUNCHING = False
CANCEL_REQUESTED = False
SHOWING_LAUNCH_OVERLAY = False


UI = {
    "page": None,
    "username_field": None,
    "slider": None,
    "play_button": None,
    "install_button": None,
    "repair_button": None,
    "busy_overlay": None,
    "overlay_msg": None,
    "overlay_progress_text": None,
    "overlay_progress_bar": None,
    "log_list": None,
    "log_filter": "ALL",
    "status_java": None,
    "status_game": None,
    "ping_text": None,
    "header": None,
    "grad_thread_started": False,
    "actions_column": None,   # <— сюда кладём текущие кнопки действий
}

UI_LOG_BUFFER = []

def get_minecraft_directory():
    appdata_path = os.getenv('APPDATA')
    return os.path.join(appdata_path, '.fuukasGamesMinecraft')

def ensure_dir(p: str):
    os.makedirs(p, exist_ok=True)

def read_settings():
    minecraft_path = get_minecraft_directory()
    os.makedirs(minecraft_path, exist_ok=True)
    settings_file = os.path.join(minecraft_path, 'launcher_settings.txt')
    defaults = {'username': 'Steve','memory': '4','traffic_saver': '0','use_zgc': '0','admin_mode': '0'}
    if not os.path.exists(settings_file):
        write_settings(**defaults)
    settings = defaults.copy()
    try:
        with open(settings_file, 'r', encoding='utf-8') as file:
            for line in file:
                if '=' in line:
                    key, value = line.strip().split('=', 1)
                    settings[key] = value
    except Exception as e:
        logging.error(f"Ошибка при чтении файла настроек: {e}")
    return settings

def write_settings(username=None, memory=None, traffic_saver=None, use_zgc=None, admin_mode=None):
    path = get_minecraft_directory()
    settings_file = os.path.join(path, 'launcher_settings.txt')
    cur = read_settings() if os.path.exists(settings_file) else {}
    if username is not None:      cur['username'] = str(username)
    if memory is not None:        cur['memory'] = str(memory)
    if traffic_saver is not None: cur['traffic_saver'] = '1' if traffic_saver else '0'
    if use_zgc is not None:       cur['use_zgc'] = '1' if use_zgc else '0'
    if admin_mode is not None:    cur['admin_mode'] = '1' if admin_mode else '0'
    try:
        with open(settings_file, 'w', encoding='utf-8') as f:
            for k, v in cur.items():
                f.write(f"{k}={v}\n")
    except IOError:
        logging.error("Не удалось записать файл настроек.")

def _is_true(v: str) -> bool:
    return str(v).strip() in ('1', 'true', 'True', 'yes', 'on')

settings = read_settings()
if settings.get('traffic_saver','0') != '0' or settings.get('use_zgc','0') != '0' or settings.get('admin_mode','0') != '0':
    write_settings(traffic_saver=False, use_zgc=False, admin_mode=False)
    settings = read_settings()

username      = settings.get('username', 'Steve')
set_memory    = int(settings.get('memory', 4))
use_zgc       = _is_true(settings.get('use_zgc', '0'))
admin_mode    = _is_true(settings.get('admin_mode', '0'))
traffic_saver = _is_true(settings.get('traffic_saver', '0'))

DEFAULT_HEADERS = {"User-Agent": f"FuukaLauncher/{current_version} (+requests)"}

def get_with_fallback(url, **kw):
    kw.setdefault("headers", DEFAULT_HEADERS)
    kw.setdefault("verify", False)
    try:
        r = requests.get(url, **kw); r.raise_for_status(); return r
    except Exception:
        alt = swap_scheme(url)
        r = requests.get(alt, **kw); r.raise_for_status(); return r

def get_with_retry(url, attempts=4, **kw):
    delay = 0.25
    for i in range(attempts):
        try:
            return get_with_fallback(url, **kw)
        except Exception:
            if i == attempts-1: raise
            time.sleep(delay * (2**i))

def level_to_color(levelname: str):
    return {"ERROR": ft.colors.RED_400,"WARNING": ft.colors.AMBER_400,"INFO": ft.colors.BLUE_300}.get(levelname, ft.colors.GREY)

def push_log_to_ui(level: str, msg: str):
    UI_LOG_BUFFER.append((level, msg))
    filt = UI.get("log_filter", "ALL")
    if filt != "ALL" and level != filt: return
    if UI.get("log_list") is not None:
        UI["log_list"].controls.append(ft.Text(msg, size=12, color=level_to_color(level)))
        try: UI["log_list"].update()
        except Exception: pass

class FletLogHandler(logging.Handler):
    def emit(self, record):
        try: msg = self.format(record)
        except Exception: msg = str(record.msg)
        push_log_to_ui(record.levelname, msg)

def build_busy_overlay():
    msg_text = ft.Text("Выполняется...", size=16, color=ft.colors.WHITE)
    progress_text = ft.Text("", size=14, color=ft.colors.WHITE)
    progress_bar = ft.ProgressBar(width=420, value=None)
    cancel_btn = ft.OutlinedButton("Отмена", icon=ft.icons.CANCEL, on_click=lambda e: request_cancel(UI.get("page")))
    container = ft.Container(
        expand=True,
        bgcolor=ft.colors.with_opacity(0.55, ft.colors.BLACK),
        alignment=ft.alignment.center,
        content=ft.Column([ft.ProgressRing(width=64, height=64), msg_text, progress_text, progress_bar, cancel_btn],
                          alignment=ft.MainAxisAlignment.CENTER,
                          horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=10),
        visible=False,
    )
    UI["overlay_msg"] = msg_text
    UI["overlay_progress_text"] = progress_text
    UI["overlay_progress_bar"] = progress_bar
    return container

def set_busy(page: ft.Page, busy: bool, msg: str = "Выполняется..."):
    global IS_BUSY, CANCEL_REQUESTED
    IS_BUSY = busy
    for name in ("username_field","slider","play_button","install_button","repair_button"):
        ctrl = UI.get(name)
        if ctrl is not None:
            ctrl.disabled = busy or (not JAVA_READY and name in ("play_button","install_button","repair_button"))
    if UI.get("busy_overlay"):
        UI["busy_overlay"].visible = busy
        if UI.get("overlay_msg"): UI["overlay_msg"].value = msg
        if not busy:
            CANCEL_REQUESTED = False
            if UI.get("overlay_progress_bar"): UI["overlay_progress_bar"].value = None
            if UI.get("overlay_progress_text"): UI["overlay_progress_text"].value = ""
    if page: page.update()

def request_cancel(page: ft.Page):
    global CANCEL_REQUESTED
    CANCEL_REQUESTED = True
    if page:
        sb = ft.SnackBar(ft.Text("Отменяем операцию..."))
        page.overlay.append(sb); sb.open = True; page.update()

def update_progress(page: ft.Page, msg: str = None, fraction: float | None = None):
    if msg is not None and UI.get("overlay_msg"): UI["overlay_msg"].value = msg
    if UI.get("overlay_progress_bar"): UI["overlay_progress_bar"].value = None if fraction is None else max(0.0, min(1.0, fraction))
    if UI.get("overlay_progress_text") is not None: UI["overlay_progress_text"].value = "" if fraction is None else f"{int(fraction*100)}%"
    if page:
        try: page.update()
        except Exception: pass

def open_game_folder(e=None): subprocess.run(["explorer", get_minecraft_directory()])

def copy_logs_to_clipboard(page: ft.Page):
    text = "\n".join([msg for _lvl, msg in UI_LOG_BUFFER][-500:])
    page.set_clipboard(text); sb = ft.SnackBar(ft.Text("Логи скопированы"))
    page.overlay.append(sb); sb.open = True; page.update()

def is_mc_process_alive(minecraft_dir: str) -> bool:
    try:
        cmd = ['wmic', 'process', 'where', 'name="javaw.exe" or name="java.exe"', 'get', 'CommandLine']
        p = subprocess.run(cmd, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        out = (p.stdout or "") + (p.stderr or "")
        out = out.lower()
        if minecraft_dir.lower() in out or "--gamedir" in out or "net.minecraft" in out or "forge" in out:
            return True
    except Exception:
        pass
    try:
        p = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq javaw.exe'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if "javaw.exe" in (p.stdout or ""): return True
        p = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq java.exe'], capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        if "java.exe" in (p.stdout or ""): return True
    except Exception:
        pass
    return False

def java_watchdog(page: ft.Page):
    global JAVA_READY, LAST_JAVA_VERSION_LOGGED
    while True:
        try:
            java_bin_candidates = glob.glob(os.path.join(get_minecraft_directory(), "jre", "jdk-17*", "bin", "java.exe"))
            ready = bool(java_bin_candidates)
            if JAVA_READY != ready:
                JAVA_READY = ready
                if ready:
                    try:
                        jp = java_bin_candidates[0]
                        result = subprocess.run([jp, "-version"], capture_output=True, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
                        msg = (result.stderr or result.stdout).strip()
                        if LAST_JAVA_VERSION_LOGGED != msg:
                            logging.info(f"java -version: {msg}")
                            LAST_JAVA_VERSION_LOGGED = msg
                    except Exception:
                        logging.warning("java -version: не удалось получить версию")
                refresh_status_java(); refresh_buttons_disabled()
        except Exception:
            pass
        time.sleep(3)

def safe_extract(zipf: zipfile.ZipFile, dest_dir: str):
    base = os.path.abspath(dest_dir)
    for m in zipf.infolist():
        target = os.path.abspath(os.path.join(dest_dir, m.filename))
        if not target.startswith(base + os.sep) and target != base:
            raise RuntimeError(f"Zip path traversal: {m.filename}")
    zipf.extractall(dest_dir)

def has_free_space(path: str, need_bytes: int) -> bool:
    try:
        total, used, free = shutil.disk_usage(path)
        return free >= need_bytes
    except Exception:
        return True

def atomic_move(src: str, dst: str):
    ensure_dir(os.path.dirname(dst))
    try:
        os.replace(src, dst)
    except Exception:
        shutil.move(src, dst)

def list_remote_mods():
    base = f"{make_base_url()}/mods/"
    r = get_with_retry(base, timeout=10)
    txt = r.text
    found = []
    for m in re.finditer(r'href=["\']([^"\']+\.jar)["\']', txt, flags=re.I):
        name = os.path.basename(m.group(1))
        url = m.group(1)
        if not url.lower().startswith("http"):
            url = base + url.lstrip("./")
        found.append({"name": name, "url": url})
    if not found:
        for line in txt.splitlines():
            line = line.strip()
            if line.lower().endswith(".jar"):
                name = os.path.basename(line)
                url = base + name
                found.append({"name": name, "url": url})
    seen = set(); uniq = []
    for f in found:
        if f["name"] not in seen:
            uniq.append(f); seen.add(f["name"])
    return uniq

def sync_mods_dir(page: ft.Page) -> bool:
    mods = list_remote_mods()
    mods_dir = os.path.join(get_minecraft_directory(), "mods")
    ensure_dir(mods_dir)
    total = len(mods) or 1
    done = 0
    for m in mods:
        done += 1
        name, url = m["name"], m["url"]
        target = os.path.join(mods_dir, name)
        need = True
        if os.path.exists(target):
            try:
                head = get_with_retry(url, timeout=6)
                remote_len = int(head.headers.get("content-length", "0"))
                if remote_len and os.path.getsize(target) == remote_len:
                    need = False
            except Exception:
                need = True
        update_progress(page, f"Моды: {name}", fraction=done/total)
        if need:
            tmpdir = tempfile.mkdtemp(prefix="mods_dl_")
            tmpfile = os.path.join(tmpdir, name + ".part")
            try:
                with requests.get(url, stream=True, verify=False) as r:
                    r.raise_for_status()
                    with open(tmpfile, "wb") as f:
                        for chunk in r.iter_content(1024*128):
                            if not chunk: continue
                            f.write(chunk)
                atomic_move(tmpfile, target)
                logging.info(f"Мод обновлён: {name}")
            finally:
                try: shutil.rmtree(tmpdir, ignore_errors=True)
                except Exception: pass
    remote_names = {m["name"] for m in mods}
    for x in os.listdir(mods_dir):
        p = os.path.join(mods_dir, x)
        if os.path.isfile(p) and x not in remote_names:
            try:
                os.remove(p); logging.info(f"Удалён лишний мод: {x}")
            except Exception as e:
                logging.warning(f"Не удалось удалить {x}: {e}")
    return True

def sync_mods_and_custom_skin():
    page = UI.get("page")
    if GAME_RUNNING or LAUNCHING:
        if page:
            sb = ft.SnackBar(ft.Text("Игра уже запущена."))
            page.overlay.append(sb); sb.open = True; page.update()
        return
    if not JAVA_READY:
        if page:
            sb = ft.SnackBar(ft.Text("Java ещё устанавливается."))
            page.overlay.append(sb); sb.open = True; page.update()
        return
    if IS_BUSY:
        return
    set_busy(page, True, "Синхронизация модов…")
    try:
        sync_mods_dir(page)
    except Exception as e:
        logging.error(f"Ошибка синхронизации модов: {e}")
    finally:
        set_busy(page, False)
    start_game_launch(page)

def refresh_status_java():
    if UI.get("status_java"):
        UI["status_java"].value = f"Java готова: {'да' if JAVA_READY else 'нет'}"
        try: UI["status_java"].update()
        except Exception: pass

def set_game_running(page: ft.Page, running: bool):
    global GAME_RUNNING
    GAME_RUNNING = running
    if UI.get("status_game"):
        UI["status_game"].value = f"Игра: {'запущена' if running else 'не запущена'}"
        try: UI["status_game"].update()
        except Exception: pass
    pb = UI.get("play_button")
    if pb:
        try:
            if running:
                pb.text = "Запущено"
                pb.icon = ft.icons.ROCKET_LAUNCH
                pb.disabled = True
                pb.on_click = None
            else:
                try: globals()["LAUNCHING"] = False
                except: pass
                pb.text = "Играть"
                pb.icon = ft.icons.PLAY_ARROW
                pb.disabled = (IS_BUSY or (not JAVA_READY))
                pb.on_click = (lambda e: sync_mods_and_custom_skin())
            pb.update()
        except Exception:
            pass

def refresh_buttons_disabled():
    page = UI.get("page")
    if not page: return
    for k in ("play_button","install_button","repair_button"):
        ctrl = UI.get(k)
        if ctrl: ctrl.disabled = IS_BUSY or (not JAVA_READY)
    page.update()

def set_username(new_username):
    global username
    username = new_username
    write_settings(username=username, memory=read_settings().get('memory', 4))
    logging.info(f"Имя пользователя: {username}")

def slider_changed(e, page):
    global set_memory
    mem = int(e.control.value); set_memory = mem
    write_settings(username=read_settings().get('username','Steve'), memory=mem)
    logging.info(f"Память: {mem} ГБ"); page.update()

# ---------- Подтверждение починки: показываем, что сохраняется ----------
def confirm_repair(page, do_repair):
    items_to_keep = ['config','mods','options.txt','.sl_password','launcher_logs','launcher_settings','schematics', 'jre', 'launcher_settings.txt']
    keep_list = "\n".join(f"• {x}" for x in items_to_keep)
    dlg = ft.AlertDialog(
        modal=True,
        title=ft.Text("Подтверждение"),
        content=ft.Column([
            ft.Text("Будут удалены ВСЕ файлы игры, кроме следующих:"),
            ft.Text(keep_list),
            ft.Text("Продолжить?"),
        ], tight=True, spacing=8),
        actions=[
            ft.TextButton("Отмена", on_click=lambda e: (setattr(dlg, "open", False), page.update())),
            ft.FilledButton("Починить", on_click=lambda e: (setattr(dlg, "open", False), page.update(), do_repair())),
        ],
        actions_alignment=ft.MainAxisAlignment.END,
    )
    page.overlay.append(dlg); dlg.open = True; page.update()

def repair_minecraft(page):
    if not JAVA_READY:
        page.overlay.append(ft.SnackBar(ft.Text("Java ещё устанавливается."))); page.overlay[-1].open=True; page.update(); return
    if IS_BUSY: 
        logging.info("Операция уже выполняется."); 
        return

    def do_repair():
        set_busy(page, True, "Починка...")
        minecraft_directory = get_minecraft_directory()
        try:
            items_to_keep = ['config','mods','options.txt','.sl_password','launcher_logs','launcher_settings','schematics', 'jre', 'launcher_settings.txt']
            for item in os.listdir(minecraft_directory):
                if item not in items_to_keep:
                    pth = os.path.join(minecraft_directory, item)
                    try:
                        if os.path.isfile(pth) or os.path.islink(pth): 
                            os.remove(pth)
                        elif os.path.isdir(pth): 
                            shutil.rmtree(pth)
                    except Exception as e:
                        logging.warning(f"Не удалось удалить {pth}: {e}")
            # На этом этапе игры нет — переключим кнопки на «Установить»
            set_actions_for_installed(False, page)
        except Exception as e:
            logging.error(f"Ошибка при починке Minecraft: {e}")
            page.overlay.append(ft.SnackBar(ft.Text(f"Починка не удалась: {e}"))); page.overlay[-1].open=True; page.update()
        finally:
            set_busy(page, False)

        # После удаления — сразу переустановим сборку
        install_minecraft(page)

    confirm_repair(page, do_repair)

# ---------- Проверка наличия игры и переключение кнопок ----------
def is_game_installed() -> bool:
    mcdir = get_minecraft_directory()
    ver_dir = os.path.join(mcdir, "versions", "1.20.1-forge-47.4.9")
    # если есть конкретная версия — считаем что игра установлена
    if os.path.isdir(ver_dir):
        return True
    # fallback: есть папка versions с чем-то внутри
    versions = os.path.join(mcdir, "versions")
    return os.path.isdir(versions) and any(os.scandir(versions))

def set_actions_for_installed(installed: bool, page: ft.Page):
    col: ft.Column = UI.get("actions_column")
    if col is None:
        return
    col.controls.clear()
    if installed:
        # показываем Играть + Починить
        row = ft.Row([UI["play_button"], UI["repair_button"]], spacing=10)
        col.controls.append(row)
    else:
        # показываем Установить
        col.controls.append(ft.Row([UI["install_button"]], spacing=10))
    try:
        col.update()
    except Exception:
        pass
    refresh_buttons_disabled()

# ---------------- Установка Minecraft (clear.zip) ----------------
def install_minecraft(page: ft.Page):
    if not JAVA_READY:
        sb = ft.SnackBar(ft.Text("Java ещё устанавливается. Подождите."))
        page.overlay.append(sb); sb.open = True; page.update(); return
    if IS_BUSY:
        logging.info("Операция уже выполняется."); return

    set_busy(page, True, "Загрузка Minecraft…")
    zip_file_path = os.path.join(get_minecraft_directory(), 'clear.zip')
    local_extract_path = get_minecraft_directory()

    try:
        clear_zip_url = f"{make_base_url()}/minecraft/clear.zip"

        # HEAD для размера
        try:
            head = get_with_retry(clear_zip_url, timeout=10)
            total_size = int(head.headers.get("content-length", 0))
        except Exception:
            total_size = 0

        if total_size and not has_free_space(local_extract_path, int(total_size*1.2)):
            raise RuntimeError("Недостаточно свободного места для установки")

        # скачиваем с прогрессом
        downloaded = 0
        update_progress(page, "Скачивание Minecraft…", 0.0)
        with requests.get(clear_zip_url, stream=True, verify=False) as r:
            r.raise_for_status()
            with open(zip_file_path, 'wb') as f:
                for chunk in r.iter_content(1024*256):
                    if not chunk: 
                        continue
                    f.write(chunk)
                    if total_size:
                        downloaded += len(chunk)
                        update_progress(page, "Скачивание Minecraft…", downloaded/total_size)

        # распаковка
        set_busy(page, True, "Распаковка…")
        update_progress(page, None, None)
        with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
            safe_extract(zip_ref, local_extract_path)
        try:
            os.remove(zip_file_path)
        except Exception:
            pass

        logging.info("Установка Minecraft завершена.")
        page.overlay.append(ft.SnackBar(ft.Text("Установка Minecraft завершена"))); page.overlay[-1].open=True

        # Переключаем действия на «Играть/Починить»
        set_actions_for_installed(True, page)

    except Exception as e:
        logging.error(f"Ошибка при установке Minecraft: {e}")
        page.overlay.append(ft.SnackBar(ft.Text(f"Установка не удалась: {e}"))); page.overlay[-1].open=True
    finally:
        set_busy(page, False)
        if page: page.update()

# ===== Java download (urlretrieve) with progress hook =====
def _progress_hook_java(page, total_holder):
    def _hook(blocknum, blocksize, totalsize):
        try:
            if totalsize > 0:
                total_holder["total"] = totalsize
            downloaded = blocknum * blocksize
            total = total_holder.get("total", 0) or totalsize or 1
            frac = min(1.0, downloaded / float(total))
            update_progress(page, "Скачивание Java…", frac)
        except Exception:
            pass
    return _hook

def download_and_install_java_async(page, post_action=None):
    th = threading.Thread(target=download_and_install_java, args=(page, post_action))
    th.daemon = False
    th.start()

def download_and_install_java(page, post_action=None):
    global JAVA_READY, LAST_JAVA_VERSION_LOGGED
    try:
        set_busy(page, True, "Устанавливается Java 17…")
        update_progress(page, "Подготовка…", None)

        mc_dir = get_minecraft_directory()
        ensure_dir(mc_dir)
        java_zip_path = os.path.join(mc_dir, "microsoft-jdk.zip")
        java_extract_path = os.path.join(mc_dir, "jre")
        ensure_dir(java_extract_path)

        java_zip_url = "https://aka.ms/download-jdk/microsoft-jdk-17.0.14-windows-x64.zip"

        total_holder = {"total": 0}
        update_progress(page, "Скачивание Java…", 0.0)
        urllib.request.urlretrieve(java_zip_url, java_zip_path, _progress_hook_java(page, total_holder))

        logging.info("Распаковка Java...")
        update_progress(page, "Распаковка Java…", None)
        with zipfile.ZipFile(java_zip_path, 'r') as zip_ref:
            safe_extract(zip_ref, java_extract_path)

        try:
            os.remove(java_zip_path)
        except Exception:
            pass

        java_bin_candidates = glob.glob(os.path.join(java_extract_path, "jdk-17*", "bin", "java.exe"))
        if not java_bin_candidates:
            raise RuntimeError("Не удалось найти java.exe после распаковки")
        JAVA_READY = True

        try:
            jp = java_bin_candidates[0]
            result = subprocess.run([jp, "-version"], capture_output=True, text=True, shell=True, creationflags=subprocess.CREATE_NO_WINDOW)
            msg = (result.stderr or result.stdout).strip()
            if LAST_JAVA_VERSION_LOGGED != msg:
                logging.info(f"java -version: {msg}")
                LAST_JAVA_VERSION_LOGGED = msg
        except Exception:
            pass

        logging.info("Java 17 установлена.")
        if page:
            sb = ft.SnackBar(ft.Text("Java 17 установлена"))
            page.overlay.append(sb); sb.open = True
    except Exception as e:
        logging.error(f"Ошибка при установке Java: {e}")
        if page:
            sb = ft.SnackBar(ft.Text(f"Ошибка установки Java: {e}"))
            page.overlay.append(sb); sb.open = True
    finally:
        refresh_status_java(); refresh_buttons_disabled()
        # подстраховка: если до этого игры не было — оставить «Установить»; если есть — «Играть»
        try:
            set_actions_for_installed(is_game_installed(), UI.get("page"))
        except:
            pass
        set_busy(page, False)
        if page: page.update()
        if post_action: post_action()

def launch_minecraft_daemon():
    global GAME_PROC
    if not JAVA_READY:
        logging.info("Java ещё не готова.")
        return
    try:
        minecraft_directory = get_minecraft_directory()
        os.chdir(minecraft_directory)
        max_memory = f'-Xmx{int(set_memory)}G'
        java_bin_candidates = glob.glob(os.path.join(minecraft_directory, "jre", "jdk-17*", "bin", "java.exe"))
        if not java_bin_candidates:
            logging.error("Портативная Java не найдена.")
            return
        java_path = java_bin_candidates[0]
        jvm_args = ['-Xms4G', max_memory]
        if use_zgc:
            jvm_args.append("-XX:+UseZGC")
        target_version = '1.20.1-forge-47.4.9'
        options = {"username": username,"uuid": username,"token": "offline","jvmArguments": jvm_args,"gameDirectory": minecraft_directory,"javaExecutable": java_path}
        cmd = mcl.command.get_minecraft_command(target_version, minecraft_directory, options)
        cmd[0] = java_path
        env = os.environ.copy(); env.pop('JAVA_HOME', None)
        if "PATH" in env:
            seg = env["PATH"].split(os.pathsep); seg = [s for s in seg if "Java" not in s and "javapath" not in s]; env["PATH"] = os.pathsep.join(seg)
        GAME_PROC = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.STDOUT, text=False, env=env, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except Exception as e:
        logging.error(f"Ошибка при запуске игры: {e}")

def start_game_launch(page: ft.Page):
    global LAUNCHING, SHOWING_LAUNCH_OVERLAY
    if IS_BUSY: return
    if GAME_RUNNING or LAUNCHING or is_mc_process_alive(get_minecraft_directory()):
        sb = ft.SnackBar(ft.Text("Игра уже запущена."))
        page.overlay.append(sb); sb.open = True; page.update(); return
    LAUNCHING = True
    SHOWING_LAUNCH_OVERLAY = True
    set_busy(page, True, "Запуск игры…")
    threading.Thread(target=launch_minecraft_daemon, daemon=True).start()


def game_state_watchdog():
    last = None
    mcdir = get_minecraft_directory()
    while True:
        try:
            page = UI.get("page")
            proc = GAME_PROC
            running = False
            if proc is not None:
                alive = proc.poll() is None
                running = alive
                if not alive:
                    try:
                        proc.stdout and proc.stdout.close()
                        proc.stderr and proc.stderr.close()
                    except Exception:
                        pass
                    try:
                        globals()["GAME_PROC"] = None
                    except Exception:
                        pass
            if not running:
                running = is_mc_process_alive(mcdir)

            if running != last:
                set_game_running(page, running)

            # если показывали оверлей запуска — убираем его,
            # когда игра реально стартовала ИЛИ когда попытка запуска завершилась.
            if 'SHOWING_LAUNCH_OVERLAY' in globals():
                if SHOWING_LAUNCH_OVERLAY and (running or not LAUNCHING):
                    try:
                        set_busy(page, False)
                    finally:
                        globals()["SHOWING_LAUNCH_OVERLAY"] = False

            if not running and LAUNCHING:
                globals()["LAUNCHING"] = False

            last = running
        except Exception:
            pass
        time.sleep(1.0)


def _hsv_to_hex(h, s, v):
    r, g, b = colorsys.hsv_to_rgb(h % 1.0, max(0.0, min(1.0, s)), max(0.0, min(1.0, v)))
    return f"#{int(r*255):02x}{int(g*255):02x}{int(b*255):02x}"

def start_header_gradient_anim():
    if UI.get("grad_thread_started"):
        return
    UI["grad_thread_started"] = True
    def _run():
        base_s, base_v = 0.65, 0.9
        while True:
            try:
                t = time.time()
                h1 = (t * 0.03) % 1.0
                h2 = (t * 0.03 + 0.33) % 1.0
                c1 = _hsv_to_hex(h1, base_s, base_v)
                c2 = _hsv_to_hex(h2, base_s, base_v)
                header = UI.get("header")
                if header is not None:
                    header.gradient = ft.LinearGradient(colors=[c1, c2], begin=ft.alignment.center_left, end=ft.alignment.center_right)
                    try: header.update()
                    except Exception: pass
            except Exception:
                pass
            time.sleep(0.06)
    threading.Thread(target=_run, daemon=True).start()

def build_settings_tab(page: ft.Page):
    s = read_settings()
    def on_toggle_traffic(e):
        global traffic_saver; traffic_saver = e.control.value; write_settings(traffic_saver=traffic_saver); logging.info(f"Экономия трафика: {traffic_saver}")
    def on_toggle_zgc(e):
        global use_zgc; use_zgc = e.control.value; write_settings(use_zgc=use_zgc); logging.info(f"UseZGC: {use_zgc}")
    def on_toggle_admin(e):
        global admin_mode; admin_mode = e.control.value; write_settings(admin_mode=admin_mode); logging.info(f"Admin mode: {admin_mode}")
    return ft.Container(content=ft.Column([
        ft.Text("Настройки", size=20, weight=ft.FontWeight.BOLD),
        ft.Switch(label="Режим экономии трафика", value=_is_true(s.get('traffic_saver','0')), on_change=on_toggle_traffic),
        ft.Switch(label="Запуск с -XX:+UseZGC", value=_is_true(s.get('use_zgc','0')), on_change=on_toggle_zgc),
        ft.Switch(label="Запуск от имени администратора", value=_is_true(s.get('admin_mode','0')), on_change=on_toggle_admin),
        ft.Text("Изменения сохраняются автоматически.", size=12, color=ft.colors.GREY)
    ], scroll=ft.ScrollMode.ALWAYS), padding=10)

def build_logs_tab(page: ft.Page):
    def set_filter(value):
        UI["log_filter"] = value; lst = UI["log_list"]; lst.controls.clear()
        for lvl, msg in UI_LOG_BUFFER:
            if value == "ALL" or lvl == value: lst.controls.append(ft.Text(msg, size=12, color=level_to_color(lvl)))
        lst.update()
    filter_dd = ft.Dropdown(label="Фильтр логов", value=UI["log_filter"],
                            options=[ft.dropdown.Option(x) for x in ("ALL","INFO","WARNING","ERROR")],
                            on_change=lambda e: set_filter(e.control.value), width=220)
    UI["log_list"] = ft.ListView(expand=1, spacing=2, auto_scroll=True)
    for lvl, msg in UI_LOG_BUFFER[-200:]: UI["log_list"].controls.append(ft.Text(msg, size=12, color=level_to_color(lvl)))
    return ft.Column([filter_dd, UI["log_list"]], expand=True)

def tile(title: str, body: ft.Control, icon=None, accent=None):
    hdr = ft.Row([
        ft.Icon(icon or ft.icons.DASHBOARD, size=18, color=accent or ft.colors.PRIMARY),
        ft.Text(title, size=14, weight=ft.FontWeight.BOLD)
    ], spacing=8, vertical_alignment=ft.CrossAxisAlignment.CENTER)
    card = ft.Container(
        content=ft.Column([hdr, body], spacing=8),
        padding=14,
        bgcolor=ft.colors.with_opacity(0.06, ft.colors.ON_SURFACE),
        border_radius=16,
        border=ft.border.all(1, ft.colors.with_opacity(0.05, ft.colors.ON_SURFACE)),
    )
    return card

def main_build(page: ft.Page):
    try:
        page.window.width = 1160
        page.window.height = 720
    except Exception:
        pass
    page.theme_mode = ft.ThemeMode.DARK
    page.padding = 0

    def open_settings_dialog(pg: ft.Page):
        dlg = ft.AlertDialog(
            title=ft.Text("Настройки"),
            content=build_settings_tab(pg),
            actions=[ft.TextButton("Закрыть", on_click=lambda e: (setattr(dlg, "open", False), pg.update()))],
        )
        pg.overlay.append(dlg)
        dlg.open = True
        pg.update()

    UI["header"] = ft.Container(
        gradient=ft.LinearGradient(colors=[ft.colors.BLUE_GREY_900, ft.colors.DEEP_PURPLE_900],
                                   begin=ft.alignment.center_left, end=ft.alignment.center_right),
        padding=16,
        content=ft.Row([
            ft.Row([ft.Icon(ft.icons.SPORTS_ESPORTS, color=ft.colors.WHITE, size=28),
                    ft.Text("Fuuka Launcher", color=ft.colors.WHITE, size=20, weight=ft.FontWeight.BOLD),
                    ft.Text(f"v{current_version} • {status_version}", color=ft.colors.WHITE70, size=12)], spacing=10),
            ft.Container(expand=True),
            ft.IconButton(ft.icons.TUNE, tooltip="Настройки", icon_color=ft.colors.WHITE, on_click=lambda e: open_settings_dialog(page)),
            ft.IconButton(ft.icons.HEALTH_AND_SAFETY, tooltip="Диагностика", icon_color=ft.colors.WHITE, on_click=lambda e: run_diagnostics(page)),
            ft.IconButton(ft.icons.FOLDER_OPEN, tooltip="Папка игры", icon_color=ft.colors.WHITE, on_click=open_game_folder),
            ft.IconButton(ft.icons.CONTENT_COPY, tooltip="Копировать логи", icon_color=ft.colors.WHITE, on_click=lambda e: copy_logs_to_clipboard(page)),
        ], vertical_alignment=ft.CrossAxisAlignment.CENTER)
    )

    logs = build_logs_tab(page)

    s = read_settings()
    uname = s.get('username', 'Steve')
    mem = int(s.get('memory', 4))
    username_field = ft.TextField(value=uname, label="Имя пользователя", on_change=lambda e: set_username(e.control.value), disabled=IS_BUSY)
    mem_slider = ft.Slider(min=4, max=20, divisions=16, label="{value}Gb", value=mem, on_change=lambda e: slider_changed(e, page), disabled=IS_BUSY)

    # Кнопки (создаём все сразу, а показываем нужные)
    play_btn = ft.FilledButton(icon=ft.icons.PLAY_ARROW, text="Играть",
                               on_click=lambda e: sync_mods_and_custom_skin(),
                               style=ft.ButtonStyle(bgcolor=ft.colors.GREEN_ACCENT_700, shape=ft.RoundedRectangleBorder(radius=16), padding=18),
                               disabled=(IS_BUSY or not JAVA_READY))
    repair_btn = ft.OutlinedButton(icon=ft.icons.BUILD_CIRCLE_OUTLINED, text="Починить",
                                   on_click=lambda e: repair_minecraft(page),
                                   style=ft.ButtonStyle(shape=ft.RoundedRectangleBorder(radius=16), padding=14),
                                   disabled=(IS_BUSY or not JAVA_READY))
    install_btn = ft.FilledButton(icon=ft.icons.DOWNLOAD, text="Установить",
                                  on_click=lambda e: install_minecraft(page),
                                  style=ft.ButtonStyle(bgcolor=ft.colors.ORANGE_600, shape=ft.RoundedRectangleBorder(radius=16), padding=18),
                                  disabled=(IS_BUSY or not JAVA_READY))

    UI["play_button"] = play_btn
    UI["repair_button"] = repair_btn
    UI["install_button"] = install_btn
    UI["username_field"] = username_field
    UI["slider"] = mem_slider

    UI["status_java"] = ft.Text(f"Java готова: {'да' if JAVA_READY else 'нет'}")
    UI["status_game"] = ft.Text("Игра: не запущена")

    try:
        t0 = time.time(); get_with_retry(f"{make_base_url()}/", timeout=5); dt = (time.time()-t0)*1000
        ping_text = ft.Text(f"Пинг: {int(dt)} мс", color=ft.colors.GREEN_300)
        srv = ft.Row([ft.Icon(ft.icons.CHECK, color=ft.colors.GREEN_300, size=18), ft.Text("Сервер: OK")], spacing=6)
    except Exception:
        ping_text = ft.Text("Пинг: —", color=ft.colors.RED_300)
        srv = ft.Row([ft.Icon(ft.icons.CLOUD_OFF, color=ft.colors.RED_300, size=18), ft.Text("Сервер: нет связи")], spacing=6)
    UI["ping_text"] = ping_text

    # Контейнер с действиями, контент переключаем динамически
    actions_column = ft.Column(spacing=12)
    UI["actions_column"] = actions_column
    # первичная расстановка кнопок по факту наличия игры
    set_actions_for_installed(is_game_installed(), page)

    actions_tile = ft.Container(
        tile("Действия", actions_column, icon=ft.icons.GAMEPAD, accent=ft.colors.GREEN_300),
        col={"xs":12, "md":4}
    )
    profile_tile = ft.Container(
        tile("Профиль", ft.Column([username_field, ft.Text("Память"), mem_slider], spacing=6),
             icon=ft.icons.PERSON, accent=ft.colors.AMBER_300),
        col={"xs":12, "md":4}
    )
    status_tile = ft.Container(
        tile("Статус", ft.Column([srv, UI["status_java"], ping_text, UI["status_game"]], spacing=4),
             icon=ft.icons.INSIGHTS, accent=ft.colors.BLUE_300),
        col={"xs":12, "md":4}
    )
    grid = ft.ResponsiveRow([actions_tile, profile_tile, status_tile], spacing=10)

    logs_card = ft.Container(
        content=ft.Column([
            ft.Row([ft.Icon(ft.icons.LIST), ft.Text("Логи", size=14, weight=ft.FontWeight.BOLD)], spacing=8),
            ft.Container(logs, expand=True)
        ], expand=True),
        padding=12, border_radius=16, bgcolor=ft.colors.with_opacity(0.06, ft.colors.ON_SURFACE), expand=True
    )

    if UI.get("busy_overlay") is None:
        UI["busy_overlay"] = build_busy_overlay()
        page.overlay.append(UI["busy_overlay"])
    elif UI["busy_overlay"] not in page.overlay:
        page.overlay.append(UI["busy_overlay"])

    page.controls.clear()
    page.add(ft.Column([
        UI["header"],
        ft.Container(grid, padding=16),
        ft.Container(logs_card, padding=16, expand=True),
        ft.Container(ft.Text(f"Fuuka Launcher v{current_version} • {status_version}", size=11, color=ft.colors.GREY), alignment=ft.alignment.center, padding=8)
    ], expand=True))

    start_header_gradient_anim()
    page.update()

def run_diagnostics(page: ft.Page):
    try:
        t0 = time.time(); get_with_retry(f"{make_base_url()}/", timeout=5); dt = (time.time()-t0)*1000
        logging.info(f"Диагностика: сервер доступен, задержка ~{int(dt)} мс")
        if UI.get("ping_text"):
            UI["ping_text"].value = f"Пинг: {int(dt)} мс"; UI["ping_text"].color = ft.colors.GREEN_300; UI["ping_text"].update()
    except Exception as e:
        logging.error(f"Диагностика: сервер недоступен: {e}")
        if UI.get("ping_text"):
            UI["ping_text"].value = "Пинг: —"; UI["ping_text"].color = ft.colors.RED_300; UI["ping_text"].update()

def main(page: ft.Page):
    UI["page"] = page
    threading.Thread(target=java_watchdog, args=(page,), daemon=True).start()
    threading.Thread(target=game_state_watchdog, daemon=True).start()
    log_formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    flet_log_handler = FletLogHandler(); flet_log_handler.setFormatter(log_formatter)
    logger = logging.getLogger(); logger.setLevel(logging.INFO); logger.addHandler(flet_log_handler)
    logging.info("Лаунчер запускается…")
    logging.info(f"Версия: {current_version} {status_version}")
    main_build(page)

    java_candidates = glob.glob(os.path.join(get_minecraft_directory(), 'jre', 'jdk-17*', 'bin', 'java.exe'))
    if not java_candidates:
        set_busy(page, True, 'Устанавливается Java 17…')
        download_and_install_java_async(page)

    def on_close(event):
        try:
            logging.info("Приложение закрывается.")
            logging.shutdown()
        finally:
            os._exit(0)
    page.on_close = on_close

if __name__ == "__main__":
    # ВАЖНО: фикс для PyInstaller на Windows, чтобы не улетать в рекурсию процессов
    try:
        import multiprocessing, sys
        if sys.platform == "win32":
            multiprocessing.set_start_method("spawn", force=True)
        # freeze_support обязателен в frozen-режиме
        multiprocessing.freeze_support()
    except Exception:
        pass

    # дальше — как у тебя:
    multiprocessing.freeze_support()
    logs_dir = os.path.join(get_minecraft_directory(), "launcher_logs"); os.makedirs(logs_dir, exist_ok=True)
    log_file_path = os.path.join(logs_dir, "launcher.log")
    log_file_handler = RotatingFileHandler(log_file_path, maxBytes=10*1024*1024, backupCount=5, encoding='utf-8')
    log_file_handler.setFormatter(logging.Formatter("%(asctime)s - %(levelname)s - %(message)s"))
    logger = logging.getLogger(); logger.setLevel(logging.INFO); logger.addHandler(log_file_handler)
    print("Booting Flet app…")
    ft.app(target=main, assets_dir="assets")

