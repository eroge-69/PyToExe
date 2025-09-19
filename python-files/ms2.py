# -*- coding: utf-8 -*-
import os
import sys
import json
import time
import psutil
import shutil
import socket
import threading
import platform
import subprocess
import tkinter as tk
from pathlib import Path
from datetime import datetime
from tkinter import ttk, messagebox

import customtkinter as ctk
import uuid
import traceback

# --- HTTP ---
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# --- System Tray (pystray) & Icon (PIL) ---
try:
    import pystray
    from PIL import Image, ImageDraw, ImageFont
    _TRAY_AVAILABLE = True
except Exception:
    _TRAY_AVAILABLE = False

# =========================================================
#                 UYGULAMA AYARLARI (Windows)
# =========================================================
APP_VERSION = "1.5.2"   # URL-only + expiry lockdown
SUPPORT_HOST = "31.56.87.73"   # Destek sunucusu (ticket)
SUPPORT_PORT = 5055            # Destek portu

# ---- AgentHub bağlanacağı (admin tarafındaki) port/ayarlar ----
AGENT_HOST = SUPPORT_HOST
AGENT_PORT = 6060
HEARTBEAT_INTERVAL = 10  # saniye

# ---- Konfigürasyon YALNIZCA bu URL'den okunur ----
CONFIG_URL = "http://31.56.87.73:8080/AG-msc-pc-16967-ABC3C26E.json"

if os.name != "nt":
    print("❌ Bu uygulama yalnızca Windows üzerinde çalışır.")
    sys.exit(1)

# Tema
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")


# =========================================================
#               Watchdog (ebeveyni ayakta tut)
# =========================================================
def _pick_pythonw():
    exe = sys.executable
    if exe.lower().endswith("python.exe"):
        w = exe[:-10] + "pythonw.exe"
        if os.path.isfile(w):
            return w
    return exe

def run_watchdog(parent_pid: int, main_cmd: list, check_interval=3):
    """
    Ayrı bir süreçte çalışır. parent_pid ölürse main_cmd ile uygulamayı tekrar başlatır.
    """
    try:
        while True:
            alive = psutil.pid_exists(parent_pid)
            if not alive:
                try:
                    # Ana uygulamayı tekrar ayağa kaldır
                    subprocess.Popen(main_cmd, creationflags=subprocess.CREATE_NO_WINDOW)
                except Exception:
                    pass
                # Bir defa yeniden başlatıp kendini de sonlandır
                break
            time.sleep(check_interval)
    except Exception:
        pass
    sys.exit(0)

if len(sys.argv) >= 2 and sys.argv[1] == "--watchdog":
    # ÇAĞRI: --watchdog <parent_pid> <cmd_json>
    try:
        _ppid = int(sys.argv[2])
        _cmd = json.loads(sys.argv[3])
    except Exception:
        sys.exit(0)
    run_watchdog(_ppid, _cmd)


# =========================================================
#               Non-blocking yardımcılar
# =========================================================
class SafeSubprocess:
    @staticmethod
    def run(cmd, timeout=None, shell=False, hide_window=True):
        startupinfo = None
        creationflags = 0
        if os.name == "nt" and hide_window:
            startupinfo = subprocess.STARTUPINFO()
            startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
            creationflags = subprocess.CREATE_NO_WINDOW
        try:
            p = subprocess.Popen(
                cmd,
                shell=shell,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                startupinfo=startupinfo,
                creationflags=creationflags
            )
            try:
                out, err = p.communicate(timeout=timeout)
                return {"code": p.returncode, "out": out, "err": err}
            except subprocess.TimeoutExpired:
                try: p.kill()
                except Exception: pass
                return {"code": None, "out": "", "err": "timeout"}
        except Exception as e:
            return {"code": None, "out": "", "err": str(e)}

def is_admin():
    try:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()
    except Exception:
        return False


# =========================================================
#                   Agent (AgentHub istemcisi)
# =========================================================
class AgentClient:
    """
    Ana sunucudaki AgentHub'a bağlanır (TCP JSONL).
    - hello: ortam + server_info
    - heartbeat: CPU/RAM/Disk/Uptime
    - cmd: get_metrics, run_ps, run_cmd, service, restart, shutdown, open_port, get_logs
    """
    def __init__(self, ui: "ServerManagementUI"):
        self.ui = ui
        self.host = AGENT_HOST
        self.port = AGENT_PORT
        self.sock = None
        self.running = False
        self.send_lock = threading.Lock()
        self.reader_thread = None
        self.heartbeat_thread = None
        self.agent_id = self._ensure_agent_id()
        self.status_var = tk.StringVar(value="Agent: Bağlı değil")

        self._add_status_chip()
        self.start()

    def _deterministic_agent_id(self) -> str:
        host = platform.node().replace(" ", "_")
        # MAC
        mac = uuid.getnode()
        mac_hex = f"{mac:012x}".upper()
        # MachineGuid
        machine_guid = ""
        try:
            import winreg
            with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, r"SOFTWARE\Microsoft\Cryptography") as key:
                machine_guid, _ = winreg.QueryValueEx(key, "MachineGuid")
        except Exception:
            machine_guid = ""
        seed = f"{host}|{machine_guid}|{mac_hex}|{platform.system()}|{platform.release()}"
        u = uuid.uuid5(uuid.NAMESPACE_DNS, seed)
        return f"AG-{host}-{str(u).split('-')[0].upper()}"

    def _ensure_agent_id(self):
        # Öncelik: Uzak config içinde agent.agent_id varsa onu kullan
        try:
            cfg = self.ui.load_config()
            aid = (cfg.get("agent", {}) or {}).get("agent_id", "").strip()
            if aid:
                return aid
        except Exception:
            pass
        # Aksi halde deterministik üret
        return self._deterministic_agent_id()

    def _add_status_chip(self):
        # Bu chip lockdown sonrası silinse bile sorun yok
        bar = ctk.CTkFrame(self.ui.tab_update, corner_radius=12)
        bar.pack(fill="x", padx=20, pady=(0,8))
        ctk.CTkLabel(bar, textvariable=self.status_var, font=self.ui.font_large).pack(side="left", padx=12)

    # ---- lifecycle ----
    def start(self):
        if self.running: return
        self.running = True
        self.reader_thread = threading.Thread(target=self._reader_loop, daemon=True); self.reader_thread.start()
        self.heartbeat_thread = threading.Thread(target=self._heartbeat_loop, daemon=True); self.heartbeat_thread.start()

    def stop(self):
        self.running = False
        try:
            if self.sock:
                try: self.sock.shutdown(socket.SHUT_RDWR)
                except Exception: pass
                self.sock.close()
        except Exception:
            pass
        self.sock = None

    # ---- I/O ----
    def _ensure_connected(self):
        if self.sock: return True
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM); s.settimeout(5)
            s.connect((self.host, self.port))
            s.settimeout(None)
            self.sock = s
            self._send_json({
                "type": "hello",
                "agent_id": self.agent_id,
                "hostname": platform.node(),
                "username": os.getenv("USERNAME", ""),
                "os": f"{platform.system()} {platform.release()}",
                "server_info": self.ui.load_config().get("server_info", {}),
                "ip_addresses": self.ui.load_config().get("server_info", {}).get("ip_addresses", []),
                "app_version": APP_VERSION,
                "ts": datetime.now().isoformat(timespec="seconds"),
            })
            self._set_status(True)
            return True
        except Exception as e:
            self._set_status(False, f"({e})")
            self.sock = None
            return False

    def _set_status(self, ok: bool, extra: str = ""):
        txt = "Agent: Bağlı" if ok else "Agent: Bağlı değil"
        if extra: txt += f" {extra}"
        try: self.status_var.set(txt)
        except Exception: pass

    def _send_json(self, obj: dict):
        data = (json.dumps(obj, ensure_ascii=False) + "\n").encode("utf-8", errors="ignore")
        with self.send_lock:
            if not self.sock:
                raise RuntimeError("socket yok")
            self.sock.sendall(data)

    # ---- loops ----
    def _reader_loop(self):
        buf = b""
        while self.running:
            try:
                if not self._ensure_connected():
                    time.sleep(3); continue
                chunk = self.sock.recv(4096)
                if not chunk:
                    self._set_status(False)
                    try: self.sock.close()
                    except Exception: pass
                    self.sock = None
                    time.sleep(2); continue
                buf += chunk
                while b"\n" in buf:
                    line, buf = buf.split(b"\n", 1)
                    line = line.decode("utf-8", errors="ignore").strip()
                    if not line: continue
                    self._handle_line(line)
            except Exception:
                self._set_status(False)
                try:
                    if self.sock: self.sock.close()
                except Exception: pass
                self.sock = None
                time.sleep(2)

    def _heartbeat_loop(self):
        while self.running:
            try:
                if self._ensure_connected():
                    hb = {
                        "type": "heartbeat",
                        "agent_id": self.agent_id,
                        "ts": datetime.now().isoformat(timespec="seconds"),
                        "metrics": self._collect_metrics(),
                    }
                    self._send_json(hb)
            except Exception:
                pass
            time.sleep(HEARTBEAT_INTERVAL)

    # ---- incoming cmd ----
    def _handle_line(self, line: str):
        try:
            msg = json.loads(line)
        except Exception:
            return
        if msg.get("type") != "cmd":
            return
        cid = msg.get("cmd_id") or f"C{int(time.time())}"
        action = (msg.get("action") or "").lower()
        args = msg.get("args", {}) or {}

        try:
            result = self._execute_action(action, args)
            out = {"type": "cmd_result", "cmd_id": cid, "ok": True, "result": result}
        except Exception as e:
            out = {"type": "cmd_result", "cmd_id": cid, "ok": False, "error": str(e), "trace": traceback.format_exc()[-1200:]}
        try:
            self._send_json(out)
        except Exception:
            pass

    # ---- action impl ----
    def _collect_metrics(self):
        try:
            cpu = psutil.cpu_percent(interval=0.0)
            mem = psutil.virtual_memory()
            dsk = psutil.disk_usage('/')
            boot = datetime.fromtimestamp(psutil.boot_time())
            diff = datetime.now() - boot
            days = diff.days; h, r = divmod(diff.seconds, 3600); m, _ = divmod(r, 60)
            return {
                "cpu": round(cpu, 1),
                "ram": {"percent": round(mem.percent, 1), "used": int(mem.used), "total": int(mem.total)},
                "disk": {"percent": round((dsk.used/dsk.total)*100.0,1), "used": int(dsk.used), "total": int(dsk.total)},
                "uptime": f"{days}g {h:02d}:{m:02d}",
            }
        except Exception as e:
            return {"error": str(e)}

    def _tail_file(self, path, max_lines=200):
        try:
            if not path: return "(!) yol boş"
            chunk = 65536
            with open(path, "rb") as f:
                f.seek(0, os.SEEK_END)
                end = f.tell()
                size = min(chunk, end)
                f.seek(end - size, os.SEEK_SET)
                data = f.read().decode(errors="ignore")
            lines = data.splitlines()
            return "\n".join(lines[-max_lines:])
        except Exception as e:
            return f"(!) okunamadı: {e}"

    def _add_firewall_rule(self, name, port, proto, direction):
        dir_ps = "Inbound" if str(direction).lower().startswith("in") else "Outbound"
        cmd_ps = [
            "powershell", "-NoProfile", "-Command",
            f"New-NetFirewallRule -DisplayName '{name}' -Direction {dir_ps} -Action Allow -Protocol {proto} -LocalPort {port}"
        ]
        res = SafeSubprocess.run(cmd_ps, timeout=20)
        if res["code"] == 0:
            return {"ok": True, "out": (res["out"] or "")[-1000:], "err": (res["err"] or "")[-1000:]}
        dir_netsh = "in" if dir_ps == "Inbound" else "out"
        cmd_ns = ["netsh","advfirewall","firewall","add","rule",
                  f"name={name}", f"dir={dir_netsh}", "action=allow", f"protocol={proto}", f"localport={port}"]
        res = SafeSubprocess.run(cmd_ns, timeout=20)
        return {"ok": res["code"] == 0, "out": (res["out"] or "")[-1000:], "err": (res["err"] or "")[-1000:]}

    def _service_action(self, action, service_name):
        action = action.lower()
        if action == "query":
            res = SafeSubprocess.run(["sc","query",service_name], timeout=20)
        elif action == "start":
            res = SafeSubprocess.run(["sc","start",service_name], timeout=20)
        elif action == "stop":
            res = SafeSubprocess.run(["sc","stop",service_name], timeout=20)
        else:
            raise ValueError("desteklenmeyen service action")
        ok = (res["code"] == 0) or ("STATE" in (res["out"] or ""))
        return {"ok": ok, "code": res["code"], "out": (res["out"] or "")[-2000:], "err": (res["err"] or "")[-1000:]}

    def _execute_action(self, action: str, args: dict):
        if action == "get_metrics":
            return self._collect_metrics()

        if action == "run_ps":
            code = args.get("code", "")
            res = SafeSubprocess.run(["powershell","-NoProfile","-Command", code], timeout=args.get("timeout", 60))
            return {"code": res["code"], "out": (res["out"] or "")[-4000:], "err": (res["err"] or "")[-4000:]}

        if action == "run_cmd":
            cmd = args.get("cmd")
            if isinstance(cmd, str):
                res = SafeSubprocess.run(cmd, timeout=args.get("timeout", 60), shell=True)
            else:
                res = SafeSubprocess.run(cmd, timeout=args.get("timeout", 60), shell=False)
            return {"code": res["code"], "out": (res["out"] or "")[-4000:], "err": (res["err"] or "")[-4000:]}

        if action == "service":
            return self._service_action(args.get("action","query"), args.get("name",""))

        if action == "restart":
            SafeSubprocess.run(["shutdown","/r","/t","5","/f"])
            return {"ok": True, "msg": "restart scheduled"}

        if action == "shutdown":
            SafeSubprocess.run(["shutdown","/s","/t","5","/f"])
            return {"ok": True, "msg": "shutdown scheduled"}

        if action == "open_port":
            port = int(args.get("port", 0))
            proto = args.get("proto","TCP")
            direction = args.get("direction","in")
            name = args.get("name", f"MSClouds-Rule-{port}")
            return self._add_firewall_rule(name, port, proto, direction)

        if action == "get_logs":
            path = args.get("path","")
            tail = int(args.get("tail", 200))
            return {"path": path, "tail": tail, "data": self._tail_file(path, tail)}

        raise ValueError(f"desteklenmeyen action: {action}")


# =========================================================
#                      Ana Uygulama (GUI)
# =========================================================
class BusyDialog:
    def __init__(self, parent, title="⏳ Çalışıyor...", text="Lütfen bekleyin"):
        self.win = ctk.CTkToplevel(parent)
        self.win.title(title)
        self.win.geometry("380x160")
        self.win.resizable(False, False)
        self.win.grab_set()
        self.win.transient(parent)

        frame = ctk.CTkFrame(self.win, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=16, pady=16)

        ctk.CTkLabel(frame, text=text, font=ctk.CTkFont(size=16, weight="bold")).pack(pady=(8,6))
        self.progress = ctk.CTkProgressBar(frame, width=300)
        self.progress.pack(pady=10)

        self._val = 0.0
        self._dir = 1
        self.cancelled = False
        self._animate()

        ctk.CTkButton(frame, text="İptal", command=self._cancel).pack(pady=(6,4))

    def _animate(self):
        if self.cancelled: return
        self._val += 0.03 * self._dir
        if self._val >= 1.0: self._val = 1.0; self._dir = -1
        if self._val <= 0.0: self._val = 0.0; self._dir = 1
        self.progress.set(self._val)
        self.win.after(30, self._animate)

    def _cancel(self): self.cancelled = True; self.close()
    def close(self):
        try:
            if self.win.winfo_exists(): self.win.destroy()
        except Exception: pass


class ServerManagementUI:
    def __init__(self):
        self.root = ctk.CTk()
        self.root.title("🖥️ MSClouds Sunucu Paneli (Windows)")
        self.root.geometry("1300x860")
        self.root.configure(fg_color=("#f8f9fa", "#1a1a1a"))

        # Konfigürasyon (yalnızca URL)
        self._config = None
        self._last_config_raw = None
        self._init_config_or_die()

        # Fontlar
        self.font_title  = ctk.CTkFont("Segoe UI", 24, "bold")
        self.font_header = ctk.CTkFont("Segoe UI", 18, "bold")
        self.font_body   = ctk.CTkFont("Segoe UI", 14)
        self.font_large  = ctk.CTkFont("Segoe UI", 16, "bold")

        # Durum
        self.cpu_usage = tk.StringVar(value="0%")
        self.ram_usage = tk.StringVar(value="0%")
        self.disk_usage= tk.StringVar(value="0%")
        self.uptime    = tk.StringVar(value="00:00:00")
        self.server_status = tk.StringVar(value="Online")
        self.remaining_time= tk.StringVar(value="Hesaplanıyor...")
        self.monitor_warn_label = None

        # Support (çoklu ticket)
        self.sock = None
        self.sock_thread = None
        self.sock_running = False
        self.tickets = {}  # id -> dict
        self.current_ticket_id = None

        # Sekme adları (delete için lazım)
        self.TAB_MONITOR     = "📊 Monitör"
        self.TAB_MANAGEMENT  = "🎛️ Yönetim"
        self.TAB_LOGS        = "📋 Loglar"
        self.TAB_PERF        = "⚡ Performans"
        self.TAB_SUPPORT     = "🆘 Destek"
        self.TAB_NETWORK     = "🌐 Ağ Ayarları"
        self.TAB_UPDATE      = "🔄 Güncelleme"

        # Lockdown bayrağı
        self._locked = False

        # System Tray
        self._tray_icon = None
        self._tray_running = False
        self._withdrawing = False  # Unmap binding döngüsünü engellemek için

        # UI
        self._build_ui()

        # Monitoring thread
        self.running = True
        self._start_monitoring()

        # Update check scheduler (URL’den konfigürasyon diff)
        self._schedule_update_checks()

        # Agent başlat
        self.agent = AgentClient(self)

        # Açılışta süre bitmişse hemen kilitle
        if self._is_expired():
            self._apply_lockdown()

        # Admin uyarısı
        if not is_admin():
            messagebox.showwarning(
                "Yetki",
                "Bazı işlemler (port açma, kural silme, kapatma/yeniden başlatma) için uygulamayı "
                "'Yönetici olarak çalıştırmanız' gerekebilir."
            )

        # Pencere olayları: kapatmayı engelle, tepsiye indir
        self.root.protocol("WM_DELETE_WINDOW", self._minimize_to_tray)
        # Simge durumuna küçültmede tepsiye çek
        self.root.bind("<Unmap>", self._on_unmap_minimize)

    # -------- System Tray Yardımcıları --------
    def _create_tray_image(self):
        # Basit bir 64x64 ikon üret
            img = Image.new("RGBA", (64, 64), (20, 120, 255, 255))
            draw = ImageDraw.Draw(img)
            draw.ellipse((6, 6, 58, 58), fill=(0, 0, 0, 40))
            draw.rounded_rectangle((10, 10, 54, 54), radius=12, fill=(255, 255, 255, 230))
            # "MS" yaz
            try:
                # Font bulunamazsa default’a düşsün
                font = ImageFont.truetype("seguiemj.ttf", 26)
            except Exception:
                font = ImageFont.load_default()

            # Yeni yöntem: metin kutusunun boyutunu almak için textbbox kullanıyoruz
            bbox = draw.textbbox((0, 0), "MS", font=font)  # Sol üst köşe ile sağ alt köşe
            w, h = bbox[2] - bbox[0], bbox[3] - bbox[1]  # Genişlik ve yükseklik hesaplanır

            draw.text(((64 - w) / 2, (64 - h) / 2), "MS", fill=(20, 120, 255), font=font)
            return img

    def _ensure_tray(self):
        if not _TRAY_AVAILABLE:
            return False
        if self._tray_icon is not None:
            return True

        # Menüde "Göster" dışında KAPATMA yok!
        def _menu_show(icon, item):
            # Tk işlemleri ana thread’de yapılmalı
            self.root.after(0, self._restore_from_tray)

        # Bilgi etiketi (pasif)
        status_item = pystray.MenuItem("Çalışıyor", None, enabled=False)
        show_item = pystray.MenuItem("Göster", _menu_show)

        self._tray_icon = pystray.Icon(
            "MSCloudsPanel",
            self._create_tray_image(),
            "MSClouds Panel",
            menu=pystray.Menu(status_item, show_item)
        )
        return True

    def _minimize_to_tray(self):
        """
        Kullanıcı çarpıya bastığında veya Alt+F4 ile kapatmaya çalıştığında pencereleri kapatmak yerine
        sistem tepsisine iner. Kapatma yok.
        """
        if _TRAY_AVAILABLE and self._ensure_tray():
            if not self._tray_running:
                self._tray_running = True
                # Tepsi ikonunu ayrı thread’de çalıştır
                threading.Thread(target=self._tray_icon.run, daemon=True).start()
        # Tk penceresini gizle
        self._withdrawing = True
        try:
            self.root.withdraw()
        finally:
            self._withdrawing = False

    def _restore_from_tray(self):
        # Tepsiden "Göster" denince pencere geri gelsin
        try:
            self.root.deiconify()
            self.root.focus_force()
        except Exception:
            pass
        # Tepsi ikonunu kapat (menüde kapatma yok)
        if self._tray_icon is not None:
            try:
                self._tray_icon.stop()
            except Exception:
                pass
            self._tray_icon = None
            self._tray_running = False

    def _on_unmap_minimize(self, event):
        """
        Kullanıcı görev çubuğuna küçültürse de tepsiye çek (Windows tarzı davranış).
        """
        if self._withdrawing:
            return
        # Eğer iconify olduysa (minimize), tepsiye
        try:
            if self.root.state() == "iconic":
                self._minimize_to_tray()
        except Exception:
            pass

    # -------- Config (URL-only) --------
    def _http_get_text(self, url: str, timeout=8) -> str:
        req = Request(url, headers={"User-Agent": f"MSClouds-Agent/{APP_VERSION}"})
        with urlopen(req, timeout=timeout) as r:
            data = r.read().decode("utf-8", errors="ignore")
        if not data:
            raise RuntimeError("boş yanıt")
        return data

    def _init_config_or_die(self):
        try:
            raw = self._http_get_text(CONFIG_URL, timeout=10)
            self._last_config_raw = raw
            self._config = json.loads(raw)
        except Exception as e:
            try:
                messagebox.showerror("Sunucu Verisi",
                                     f"Sunucu verisine ulaşılamadı.\nURL: {CONFIG_URL}\nHata: {e}")
            except Exception:
                print(f"Sunucu verisine ulaşılamadı: {e}")
            sys.exit(1)

    def _reload_config_if_changed(self):
        """URL’den tekrar çek; ham metin farklıysa uygula."""
        try:
            raw = self._http_get_text(CONFIG_URL, timeout=8)
        except Exception:
            return False
        if self._last_config_raw is None or raw.strip() != (self._last_config_raw or "").strip():
            try:
                cfg = json.loads(raw)
            except Exception:
                return False
            self._last_config_raw = raw
            self._config = cfg
            return True
        return False

    def load_config(self):
        if self._config is None:
            self._init_config_or_die()
        return self._config

    def save_config(self, _data):
        messagebox.showinfo("Bilgi", "Konfigürasyon uzaktan yönetiliyor. Lütfen web panelinden güncelleyin.")

    # -------- Expiry helpers --------
    def _parse_expiry_dt(self):
        s = (self.load_config().get("server_info", {}) or {}).get("expiry_date", "")
        import calendar
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M"):
            try:
                return datetime.strptime(s, fmt)
            except Exception:
                pass
        try:
            date_part = s.split()[0]
            y, m, d = [int(x) for x in date_part.replace("/", "-").split("-")[:3]]
            last = calendar.monthrange(y, m)[1]
            d = min(max(1, d), last)
            return datetime.strptime(f"{y:04d}-{m:02d}-{d:02d} 23:59:59", "%Y-%m-%d %H:%M:%S")
        except Exception:
            return None

    def _is_expired(self) -> bool:
        dt = self._parse_expiry_dt()
        if not dt:
            return False
        return datetime.now() >= dt

    def _remaining_time_text(self):
        dt = self._parse_expiry_dt()
        if not dt:
            return "Hesaplanamadı"
        now = datetime.now()
        if dt <= now:
            # Süre doldu: tam istenen metin
            return "0 Gün 0 Saat 0 Dakika"
        diff = dt - now
        d = diff.days
        h, r = divmod(diff.seconds, 3600)
        m, _ = divmod(r, 60)
        return f"{d} Gün {h} Saat {m} Dakika"

    def _brand_chip(self):
        info = self.load_config()["server_info"]
        return f"{info.get('server_name','Sunucu')} • {info.get('server_type','-')} • {info.get('location','-')}"

    # -------- UI Build --------
    def _build_ui(self):
        container = ctk.CTkFrame(self.root, fg_color="transparent")
        container.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkFrame(container, height=80, corner_radius=16)
        header.pack(fill="x")
        header.pack_propagate(False)

        ctk.CTkLabel(header, text="🖥️  MSClouds Sunucu Paneli",
                     font=self.font_title).pack(side="left", padx=20)
        self.brand_label = ctk.CTkLabel(header, text=self._brand_chip(),
                     font=self.font_body)
        self.brand_label.pack(side="right", padx=20)

        self.tabs = ctk.CTkTabview(container, corner_radius=14, height=700)
        self.tabs.pack(fill="both", expand=True, pady=(20,0))

        self.tab_monitor     = self.tabs.add(self.TAB_MONITOR)
        self.tab_management  = self.tabs.add(self.TAB_MANAGEMENT)
        self.tab_logs        = self.tabs.add(self.TAB_LOGS)
        self.tab_performance = self.tabs.add(self.TAB_PERF)
        self.tab_support     = self.tabs.add(self.TAB_SUPPORT)
        self.tab_network     = self.tabs.add(self.TAB_NETWORK)
        self.tab_update      = self.tabs.add(self.TAB_UPDATE)

        self._build_monitor()
        self._build_management()
        self._build_logs()
        self._build_performance()
        self._build_support()
        self._build_network()
        self._build_update()

    def _card(self, parent, icon, title):
        card = ctk.CTkFrame(parent, corner_radius=12)
        card.pack(fill="x", padx=20, pady=10)
        hdr = ctk.CTkFrame(card, fg_color="transparent")
        hdr.pack(pady=(14,6), fill="x")
        ctk.CTkLabel(hdr, text=icon, font=ctk.CTkFont(size=20)).pack(side="left", padx=6)
        ctk.CTkLabel(hdr, text=title, font=self.font_body).pack(side="left", padx=(8,0))
        return card

    def _build_monitor(self):
        # Bu frame içeriği lockdown'da tamamen silinecek
        scroll = ctk.CTkScrollableFrame(self.tab_monitor, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)
        scroll.grid_columnconfigure((0,1), weight=1)

        left = ctk.CTkFrame(scroll, corner_radius=12); left.grid(row=0, column=0, sticky="nsew", padx=(0,10), pady=10)
        right= ctk.CTkFrame(scroll, corner_radius=12); right.grid(row=0, column=1, sticky="nsew", padx=(10,0), pady=10)

        ctk.CTkLabel(left, text="📊  SİSTEM BİLGİLERİ", font=self.font_header).pack(pady=(20,10))
        cpu = self._card(left, "🔧", "CPU Kullanımı")
        self.l_cpu = ctk.CTkLabel(cpu, textvariable=self.cpu_usage, font=self.font_large); self.l_cpu.pack(pady=6)
        self.p_cpu = ctk.CTkProgressBar(cpu, width=260, height=8); self.p_cpu.pack(pady=(0,12))

        ram = self._card(left, "💾", "RAM Kullanımı")
        self.l_ram = ctk.CTkLabel(ram, textvariable=self.ram_usage, font=self.font_large); self.l_ram.pack(pady=6)
        self.p_ram = ctk.CTkProgressBar(ram, width=260, height=8); self.p_ram.pack(pady=(0,12))

        dsk = self._card(left, "💽", "Disk Kullanımı")
        self.l_dsk = ctk.CTkLabel(dsk, textvariable=self.disk_usage, font=self.font_large); self.l_dsk.pack(pady=6)
        self.p_dsk = ctk.CTkProgressBar(dsk, width=260, height=8); self.p_dsk.pack(pady=(0,12))

        ctk.CTkLabel(right, text="🔍  DURUM BİLGİLERİ", font=self.font_header).pack(pady=(20,10))
        upc = self._card(right, "⏱️", "Çalışma Süresi")
        ctk.CTkLabel(upc, textvariable=self.uptime, font=self.font_large).pack(pady=10)

        stc = self._card(right, "🟢", "Sunucu Durumu")
        ctk.CTkLabel(stc, textvariable=self.server_status, font=self.font_large).pack(pady=10)

        rtc = self._card(right, "⏳", "Kalan Süre")
        self.remaining_label = ctk.CTkLabel(rtc, textvariable=self.remaining_time, font=self.font_large)
        self.remaining_label.pack(pady=10)

        self.monitor_warn_label = ctk.CTkLabel(right, text="", font=ctk.CTkFont(size=13, weight="bold"))
        self.monitor_warn_label.pack(pady=(6,12))

    def _build_management(self):
        scroll = ctk.CTkScrollableFrame(self.tab_management, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        box = ctk.CTkFrame(scroll, corner_radius=12)
        box.pack(fill="x", pady=8)
        ctk.CTkLabel(box, text="🎛️  SİSTEM KONTROLLERİ", font=self.font_header).pack(pady=(18, 12))

        grid = ctk.CTkFrame(box, fg_color="transparent")
        grid.pack(fill="x", padx=30, pady=(0, 20))
        grid.grid_columnconfigure((0,1,2), weight=1)

        ctk.CTkButton(grid, text="🔄 Sunucuyu Yeniden Başlat", height=50, corner_radius=10,
                      command=self._restart_windows).grid(row=0, column=0, sticky="ew", padx=10, pady=6)
        ctk.CTkButton(grid, text="⏹️ Sunucuyu Kapat", height=50, corner_radius=10,
                      command=self._shutdown_windows).grid(row=0, column=1, sticky="ew", padx=10, pady=6)
        ctk.CTkButton(grid, text="🔐 Şifre Değiştir", height=50, corner_radius=10,
                      command=self._change_password_dialog).grid(row=0, column=2, sticky="ew", padx=10, pady=6)

        quick = ctk.CTkFrame(scroll, corner_radius=12); quick.pack(fill="x", pady=8)
        ctk.CTkLabel(quick, text="⚡  HIZLI EYLEMLER", font=self.font_header).pack(pady=(18, 12))
        qgrid = ctk.CTkFrame(quick, fg_color="transparent"); qgrid.pack(fill="x", padx=30, pady=(0, 20))
        qgrid.grid_columnconfigure((0,1,2,3), weight=1)

        actions = [
            ("🧹 Temizlik", self.cleanup_system),
            ("🔒 Güvenlik Taraması", self.security_scan),
            ("📊 Rapor", self.generate_report),
            ("⚙️ Optimizasyon", self.optimize_system)
        ]
        for i, (name, cmd) in enumerate(actions):
            ctk.CTkButton(qgrid, text=name, height=46, corner_radius=10, command=cmd)\
                .grid(row=0, column=i, sticky="ew", padx=8, pady=6)

    # ---- Windows yeniden başlat / kapat ----
    def _restart_windows(self):
        if messagebox.askyesno("Yeniden Başlat", "Sunucuyu yeniden başlatmak istiyor musunuz?\nTüm bağlantılar kesilecektir."):
            SafeSubprocess.run(["shutdown", "/r", "/t", "5", "/f"])

    def _shutdown_windows(self):
        if messagebox.askyesno("Kapat", "Sunucuyu kapatmak istiyor musunuz?\nTüm bağlantılar kesilecektir."):
            SafeSubprocess.run(["shutdown", "/s", "/t", "5", "/f"])

    # ---- Şifre değiştir ----
    def _change_password_dialog(self):
        top = ctk.CTkToplevel(self.root)
        top.title("🔐 Şifre Değiştir")
        top.geometry("430x360")
        top.grab_set(); top.transient(self.root)

        frm = ctk.CTkFrame(top, corner_radius=12); frm.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(frm, text="Mevcut Şifre").pack(anchor="w", padx=8, pady=(6,2))
        e_old = ctk.CTkEntry(frm, show="*"); e_old.pack(fill="x", padx=8, pady=(0,8))
        ctk.CTkLabel(frm, text="Yeni Şifre").pack(anchor="w", padx=8, pady=(6,2))
        e_new = ctk.CTkEntry(frm, show="*"); e_new.pack(fill="x", padx=8, pady=(0,8))
        ctk.CTkLabel(frm, text="Yeni Şifre (Tekrar)").pack(anchor="w", padx=8, pady=(6,2))
        e_new2 = ctk.CTkEntry(frm, show="*"); e_new2.pack(fill="x", padx=8, pady=(0,12))

        def do_change():
            old = e_old.get(); new = e_new.get(); new2= e_new2.get()
            if not old or not new:
                messagebox.showerror("Hata", "Alanlar boş olamaz."); return
            if new != new2:
                messagebox.showerror("Hata", "Yeni şifreler eşleşmiyor."); return
            if len(new) < 6:
                messagebox.showerror("Hata", "Şifre en az 6 karakter olmalı."); return
            ps = (
                "$u=$env:USERNAME; "
                "$o=[ADSI]('WinNT://./'+$u+',user'); "
                "try{ $o.ChangePassword('%OLD%','%NEW%'); exit 0 } "
                "catch{ exit 1 }"
            ).replace("%OLD%", old.replace("'", "''")).replace("%NEW%", new.replace("'", "''"))
            res = SafeSubprocess.run(["powershell","-NoProfile","-Command", ps], timeout=20)
            if res["code"] == 0:
                messagebox.showinfo("Başarılı", "Şifre değiştirildi.")
                top.destroy()
            else:
                messagebox.showerror("Hata", "Şifre değiştirilemedi. Mevcut şifre hatalı olabilir.")

        btnrow = ctk.CTkFrame(frm, fg_color="transparent"); btnrow.pack(fill="x", pady=(6,2))
        ctk.CTkButton(btnrow, text="Değiştir", command=do_change).pack(side="left", padx=6)
        ctk.CTkButton(btnrow, text="Kapat", command=top.destroy).pack(side="right", padx=6)

    # ------------------ Loglar ------------------
    def _build_logs(self):
        frame = ctk.CTkFrame(self.tab_logs, corner_radius=12)
        frame.pack(fill="both", expand=True, padx=20, pady=20)

        top = ctk.CTkFrame(frame, fg_color="transparent"); top.pack(fill="x", padx=20, pady=(16,8))
        ctk.CTkLabel(top, text="📋  SİSTEM LOGLARI (Windows)", font=self.font_header).pack(side="left")
        controls = ctk.CTkFrame(top, fg_color="transparent"); controls.pack(side="right")
        self.log_type = ctk.CTkOptionMenu(controls,
            values=["Sistem Logları","Apache Logları","MySQL Logları","SSH Logları","Güvenlik Logları"],
            command=self.on_log_type_change)
        self.log_type.pack(side="left", padx=6)
        ctk.CTkButton(controls, text="🔄 Yenile", width=100, height=35, command=self.refresh_logs).pack(side="left", padx=6)
        ctk.CTkButton(controls, text="🗑️ Temizle", width=100, height=35, command=self.clear_logs).pack(side="left", padx=6)

        body = ctk.CTkFrame(frame, fg_color="transparent"); body.pack(fill="both", expand=True, padx=20, pady=(8, 16))
        self.log_text = ctk.CTkTextbox(body, font=ctk.CTkFont(family="Consolas", size=11), corner_radius=8)
        self.log_text.pack(fill="both", expand=True, padx=15, pady=15)
        self.refresh_logs(initial=True)

    # ------------------ Performans ------------------
    def _build_performance(self):
        scroll = ctk.CTkScrollableFrame(self.tab_performance, fg_color="transparent")
        scroll.pack(fill="both", expand=True, padx=20, pady=20)

        p = self.load_config().get("performance", {})

        auto = ctk.CTkFrame(scroll, corner_radius=12); auto.pack(fill="x", pady=(0,16))
        ctk.CTkLabel(auto, text="⚡  OTOMATİK OPTİMİZASYON", font=self.font_header).pack(pady=(18,6))
        grid = ctk.CTkFrame(auto, fg_color="transparent"); grid.pack(fill="x", padx=30, pady=(0,16)); grid.grid_columnconfigure((0,1,2), weight=1)

        self.auto_optimize_var = tk.BooleanVar(value=p.get("auto_optimize", True))
        self.auto_cleanup_var  = tk.BooleanVar(value=p.get("auto_cleanup", True))
        self.cleanup_logs_var  = tk.BooleanVar(value=p.get("cleanup_logs", True))

        ctk.CTkSwitch(grid, text="🤖 Otomatik Optimizasyon", variable=self.auto_optimize_var).grid(row=0, column=0, sticky="w", padx=8, pady=8)
        ctk.CTkSwitch(grid, text="🧹 Otomatik Temizlik", variable=self.auto_cleanup_var).grid(row=0, column=1, sticky="w", padx=8, pady=8)
        ctk.CTkSwitch(grid, text="🧾 Log Temizliği", variable=self.cleanup_logs_var).grid(row=0, column=2, sticky="w", padx=8, pady=8)

        limits = ctk.CTkFrame(scroll, corner_radius=12); limits.pack(fill="x", pady=8)
        ctk.CTkLabel(limits, text="🎯  PERFORMANS LİMİTLERİ", font=self.font_header).pack(pady=(18,6))
        lgrid = ctk.CTkFrame(limits, fg_color="transparent"); lgrid.pack(fill="x", padx=30, pady=(0,16))

        ctk.CTkLabel(lgrid, text="🔧 Maksimum CPU (%)").grid(row=0, column=0, sticky="w", padx=6, pady=8)
        self.cpu_limit_slider = ctk.CTkSlider(lgrid, from_=50, to=100, number_of_steps=50)
        self.cpu_limit_slider.grid(row=0, column=1, sticky="ew", padx=12, pady=8)
        self.cpu_limit_slider.set(p.get("max_cpu_usage", 80))

        ctk.CTkLabel(lgrid, text="💾 Maksimum RAM (%)").grid(row=1, column=0, sticky="w", padx=6, pady=8)
        self.ram_limit_slider = ctk.CTkSlider(lgrid, from_=50, to=100, number_of_steps=50)
        self.ram_limit_slider.grid(row=1, column=1, sticky="ew", padx=12, pady=8)
        self.ram_limit_slider.set(p.get("max_ram_usage", 85))

        wbox = ctk.CTkFrame(scroll, corner_radius=12); wbox.pack(fill="x", pady=8)
        ctk.CTkLabel(wbox, text="🪟 Windows Ayarları", font=self.font_header).pack(pady=(18,6))
        wgrid = ctk.CTkFrame(wbox, fg_color="transparent"); wgrid.pack(fill="x", padx=30, pady=(0,16))
        self.win_clear_temp = tk.BooleanVar(value=p.get("windows", {}).get("clear_temp", True))
        self.win_empty_bin  = tk.BooleanVar(value=p.get("windows", {}).get("empty_recycle_bin", True))
        self.win_flush_dns  = tk.BooleanVar(value=p.get("windows", {}).get("flush_dns", True))
        ctk.CTkSwitch(wgrid, text="Temp klasörlerini temizle",  variable=self.win_clear_temp).grid(row=0, column=0, sticky="w", padx=8, pady=6)
        ctk.CTkSwitch(wgrid, text="Geri Dönüşüm Kutusunu boşalt", variable=self.win_empty_bin).grid(row=0, column=1, sticky="w", padx=8, pady=6)
        ctk.CTkSwitch(wgrid, text="DNS önbelleğini temizle",    variable=self.win_flush_dns).grid(row=0, column=2, sticky="w", padx=8, pady=6)

        ctk.CTkButton(scroll, text="💾  Ayarları Kaydet",
                      font=self.font_large, height=50, corner_radius=12,
                      command=self.save_performance_settings).pack(fill="x", pady=16)

    # ------------------ Destek (çoklu ticket + chat) ------------------
    def _build_support(self):
        wrap = ctk.CTkFrame(self.tab_support, corner_radius=12)
        wrap.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(wrap, text="🆘 DESTEK SİSTEMİ (Ticket & Sohbet)", font=self.font_header).pack(pady=(18,10))

        body = ctk.CTkFrame(wrap, corner_radius=12); body.pack(fill="both", expand=True, padx=10, pady=10)
        body.grid_columnconfigure((0,1), weight=1)
        body.grid_rowconfigure(0, weight=1)

        left = ctk.CTkFrame(body, corner_radius=12); left.grid(row=0, column=0, sticky="nsew", padx=(0,8), pady=6)
        ctk.CTkLabel(left, text="🎫 Ticketlar", font=self.font_large).pack(pady=(10,6))
        self.ticket_tree = ttk.Treeview(left, columns=("id","subject","priority","status","created"), show="headings", height=12)
        for col, title, w in [("id","ID",160),("subject","Konu",240),("priority","Öncelik",80),("status","Durum",80),("created","Oluşturma",130)]:
            self.ticket_tree.heading(col, text=title)
            self.ticket_tree.column(col, width=w, anchor="w")
        self.ticket_tree.pack(fill="both", expand=True, padx=8, pady=(0,10))

        btnbar = ctk.CTkFrame(left, fg_color="transparent"); btnbar.pack(fill="x", padx=8, pady=(0,10))
        ctk.CTkButton(btnbar, text="Yeni Ticket", command=self._new_ticket_dialog).pack(side="left", padx=4)
        ctk.CTkButton(btnbar, text="Aç (Sohbet)", command=self._open_selected_ticket).pack(side="left", padx=4)
        ctk.CTkButton(btnbar, text="Kapat", command=self._close_selected_ticket).pack(side="left", padx=4)

        right = ctk.CTkFrame(body, corner_radius=12); right.grid(row=0, column=1, sticky="nsew", padx=(8,0), pady=6)
        self.sup_status = ctk.CTkLabel(right, text="Seçili ticket yok.")
        self.sup_status.pack(padx=10, pady=6, anchor="w")

        self.chat_box = ctk.CTkTextbox(right, font=ctk.CTkFont("Consolas", 12))
        self.chat_box.pack(fill="both", expand=True, padx=10, pady=(0, 8))
        self.chat_box.insert("end", "Ticket listesinden bir ticket açın ya da yeni ticket oluşturun.\n\n")

        inp = ctk.CTkFrame(right, fg_color="transparent"); inp.pack(fill="x", padx=10, pady=(0, 10))
        self.chat_entry = ctk.CTkEntry(inp, placeholder_text="Mesajınızı yazın...", height=40)
        self.chat_entry.pack(side="left", fill="x", expand=True, padx=(0,8))

        # Gönder butonu: Boş mesajı engelle, dinamik enable/disable
        self.btn_send = ctk.CTkButton(inp, text="Gönder", height=40, command=self._support_send)
        self.btn_send.pack(side="right")
        self.btn_disconnect = ctk.CTkButton(inp, text="Bağlantıyı Kes", height=40, command=self._support_disconnect, state="disabled")
        self.btn_disconnect.pack(side="right", padx=8)

        # Mesaj alanı değiştikçe buton durumu güncelle
        self.chat_entry.bind("<KeyRelease>", lambda e: self._update_send_button_state())
        self._update_send_button_state()

    def _update_send_button_state(self):
        txt = (self.chat_entry.get() or "").strip()
        enabled = bool(txt) and self.current_ticket_id is not None and \
                  (self.tickets.get(self.current_ticket_id, {}).get("status") == "Açık")
        self.btn_send.configure(state=("normal" if enabled else "disabled"))

    def _new_ticket_dialog(self):
        top = ctk.CTkToplevel(self.root)
        top.title("Yeni Ticket")
        top.geometry("420x220")
        top.grab_set(); top.transient(self.root)

        frm = ctk.CTkFrame(top, corner_radius=12); frm.pack(fill="both", expand=True, padx=16, pady=16)
        ctk.CTkLabel(frm, text="Konu").pack(anchor="w", padx=8, pady=(0,4))
        e_subject = ctk.CTkEntry(frm, placeholder_text="Örn: Sunucu CPU yüksek…")
        e_subject.pack(fill="x", padx=8, pady=(0,8))
        ctk.CTkLabel(frm, text="Öncelik").pack(anchor="w", padx=8, pady=(0,4))
        p = ctk.CTkOptionMenu(frm, values=["Düşük","Orta","Yüksek","Acil"]); p.set("Orta")
        p.pack(fill="x", padx=8, pady=(0,8))

        def create():
            subject = e_subject.get().strip()
            priority = p.get()
            if not subject:
                messagebox.showerror("❌", "Lütfen ticket konusu girin."); return
            tid = f"MSC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
            self.tickets[tid] = {
                "id": tid, "subject": subject, "priority": priority,
                "status": "Açık", "created": datetime.now().strftime("%d.%m.%Y %H:%M"),
                "history": []
            }
            self.ticket_tree.insert("", "end", values=(tid, subject, priority, "Açık", self.tickets[tid]["created"]))
            top.destroy()
            self._open_ticket(tid)

        ctk.CTkButton(frm, text="Oluştur", command=create).pack(side="left", padx=8, pady=8)
        ctk.CTkButton(frm, text="Kapat", command=top.destroy).pack(side="right", padx=8, pady=8)

    def _get_selected_ticket_id(self):
        sel = self.ticket_tree.selection()
        if not sel: return None
        vals = self.ticket_tree.item(sel[0], "values")
        return vals[0] if vals else None

    def _open_selected_ticket(self):
        tid = self._get_selected_ticket_id()
        if not tid:
            messagebox.showinfo("Bilgi", "Önce listeden bir ticket seçin.")
            return
        self._open_ticket(tid)

    def _close_selected_ticket(self):
        tid = self._get_selected_ticket_id()
        if not tid:
            messagebox.showinfo("Bilgi", "Önce listeden bir ticket seçin.")
            return
        self._close_ticket(tid)

    def _open_ticket(self, tid):
        if self.sock_running and self.current_ticket_id and self.current_ticket_id != tid:
            self._support_disconnect()

        self.current_ticket_id = tid
        t = self.tickets.get(tid)
        if not t:
            messagebox.showerror("Hata", "Ticket bulunamadı."); return

        self.sup_status.configure(text=f"Ticket #{tid} • {t['subject']} • Öncelik: {t['priority']} • {t['status']}")
        self.chat_box.delete("1.0", "end")
        if t["history"]:
            for who, text, ts in t["history"]:
                self.chat_box.insert("end", f"[{who} {ts}] {text}\n")
        else:
            self.chat_box.insert("end", "[Sistem] Sohbet başlatılıyor…\n")

        if t["status"] != "Açık":
            self.chat_box.insert("end", "[Sistem] Bu ticket kapalı. Mesaj gönderemezsiniz.\n")
            self.btn_disconnect.configure(state="disabled")
            self._update_send_button_state()
            return
        self._support_connect()
        self._update_send_button_state()

    def _close_ticket(self, tid):
        t = self.tickets.get(tid)
        if not t: return
        if t["status"] == "Kapalı":
            messagebox.showinfo("Bilgi", "Ticket zaten kapatılmış."); return
        t["status"] = "Kapalı"
        for iid in self.ticket_tree.get_children():
            if self.ticket_tree.item(iid, "values")[0] == tid:
                vals = list(self.ticket_tree.item(iid, "values")); vals[3] = "Kapalı"
                self.ticket_tree.item(iid, values=vals); break
        if self.current_ticket_id == tid and self.sock_running:
            self._support_disconnect()
            self.sup_status.configure(text=f"Ticket #{tid} • {t['subject']} • KAPALI")
            self.chat_box.insert("end", "[Sistem] Ticket kapatıldı. Bağlantı sonlandırıldı.\n")
        self._update_send_button_state()

    def _support_connect(self):
        if self.sock_running: return
        t = self.tickets.get(self.current_ticket_id or "")
        if not t or t.get("status") != "Açık": return

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.settimeout(4)
        try:
            self.sock.connect((SUPPORT_HOST, SUPPORT_PORT))
        except Exception as e:
            self.chat_box.insert("end", f"[Sistem] Bağlanılamadı ({e}). Demo modunda devam ediliyor.\n")
            self.sock = None
            self.sup_status.configure(text=f"Ticket #{self.current_ticket_id or '-'} • Bağlı değil (demo)")
            self._update_send_button_state()
            return

        self.sock_running = True
        self.sup_status.configure(text=f"Ticket #{self.current_ticket_id} • Bağlı")
        self.btn_disconnect.configure(state="normal")
        self.chat_box.insert("end", "[Sistem] Sunucuya bağlandı.\n")
        self._update_send_button_state()

        def listener():
            try:
                self.sock.settimeout(1.0)
                while self.sock_running:
                    try:
                        data = self.sock.recv(4096)
                        if not data:
                            break
                        text = data.decode(errors="ignore").strip()
                        if text:
                            ts = datetime.now().strftime("%H:%M:%S")
                            self.tickets[self.current_ticket_id]["history"].append(("Sunucu", text, ts))
                            self.root.after(0, lambda t=text, ts=ts: self.chat_box.insert("end", f"[Sunucu {ts}] {t}\n"))
                    except socket.timeout:
                        continue
                    except Exception:
                        break
            finally:
                self.sock_running = False
                try:
                    if self.sock: self.sock.close()
                except Exception: pass
                self.sock = None
                self.root.after(0, lambda: (
                    self.sup_status.configure(text=f"Ticket #{self.current_ticket_id or '-'} • Bağlı değil"),
                    self.btn_disconnect.configure(state="disabled"),
                    self.chat_box.insert("end","[Sistem] Bağlantı sonlandı.\n"),
                    self._update_send_button_state()
                ))
        self.sock_thread = threading.Thread(target=listener, daemon=True)
        self.sock_thread.start()

    def _support_disconnect(self):
        self.sock_running = False
        try:
            if self.sock: self.sock.shutdown(socket.SHUT_RDWR)
        except Exception: pass

    def _support_send(self):
        msg_raw = self.chat_entry.get()
        msg = (msg_raw or "").strip()
        if not self.current_ticket_id:
            messagebox.showinfo("Bilgi", "Önce bir ticket açın/seçin."); 
            self._update_send_button_state()
            return
        t = self.tickets.get(self.current_ticket_id)
        if not t or t["status"] != "Açık":
            self.chat_box.insert("end", "[Sistem] Ticket kapalı olduğu için mesaj gönderilemez.\n")
            self._update_send_button_state()
            return
        if not msg:
            # Boş mesaj uyarısı
            self.root.bell()
            messagebox.showwarning("Uyarı", "Lütfen bir mesaj yazın.")
            self._update_send_button_state()
            return

        self.chat_entry.delete(0, "end")
        self._update_send_button_state()
        prefix = f"[#{self.current_ticket_id} {t['priority']}] "
        ts = datetime.now().strftime("%H:%M:%S")
        self.chat_box.insert("end", f"[Ben {ts}] {prefix}{msg}\n")
        t["history"].append(("Ben", prefix+msg, ts))
        if self.sock and self.sock_running:
            try:
                self.sock.sendall((prefix + msg + "\n").encode())
            except Exception as e:
                self.chat_box.insert("end", f"[Sistem] Gönderim hatası: {e}\n")
        else:
            self.chat_box.insert("end", "[Demo] Mesaj alındı (örnek cevap).\n")

    # ------------------ Ağ Ayarları ------------------
    def _build_network(self):
        wrap = ctk.CTkFrame(self.tab_network, corner_radius=12)
        wrap.pack(fill="both", expand=True, padx=20, pady=20)

        header = ctk.CTkFrame(wrap, fg_color="transparent"); header.pack(fill="x", padx=18, pady=(18,8))
        ctk.CTkLabel(header, text="🌐 AĞ AYARLARI", font=self.font_header).pack(side="left")

        righttools = ctk.CTkFrame(header, fg_color="transparent"); righttools.pack(side="right")
        self.only_listen_var = tk.BooleanVar(value=True)
        ctk.CTkSwitch(righttools, text="Sadece LISTEN", variable=self.only_listen_var, command=self._net_refresh).pack(side="left", padx=6)
        ctk.CTkButton(righttools, text="Yenile", width=100, command=self._net_refresh).pack(side="left", padx=6)
        ctk.CTkButton(righttools, text="Yeni Port Aç", width=140, command=self._net_open_port_dialog).pack(side="left", padx=6)

        grid = ctk.CTkFrame(wrap, fg_color="transparent"); grid.pack(fill="both", expand=True, padx=18, pady=(6,18))
        grid.grid_columnconfigure((0,1), weight=1)

        listen_box = ctk.CTkFrame(grid, corner_radius=12); listen_box.grid(row=0, column=0, sticky="nsew", padx=(0,8))
        ctk.CTkLabel(listen_box, text="🔊 Bağlantılar (Dinleyen/Tümü)", font=self.font_large).pack(pady=(10,6))
        self.net_tree = ttk.Treeview(listen_box, columns=("proto","local","remote","status","pid","proc","desc"), show="headings", height=12)
        for col, title in [("proto","Proto"),("local","Yerel Adres:Port"),("remote","Uzak Adres:Port"),("status","Durum"),
                           ("pid","PID"),("proc","Süreç"),("desc","Açıklama")]:
            self.net_tree.heading(col, text=title)
            self.net_tree.column(col, anchor="w")
        self.net_tree.pack(fill="both", expand=True, padx=8, pady=(0,10))

        rule_box = ctk.CTkFrame(grid, corner_radius=12); rule_box.grid(row=0, column=1, sticky="nsew", padx=(8,0))
        ctk.CTkLabel(rule_box, text="🛡️ Firewall Kuralları (MSClouds-*)", font=self.font_large).pack(pady=(10,6))
        self.rule_tree = ttk.Treeview(rule_box, columns=("name","dir","proto","port","enabled"), show="headings", height=12)
        for col, title in [("name","Ad"),("dir","Yön"),("proto","Protokol"),("port","Port"),("enabled","Aktif")]:
            self.rule_tree.heading(col, text=title)
            self.rule_tree.column(col, anchor="w")
        self.rule_tree.pack(fill="both", expand=True, padx=8, pady=(0,6))
        rbtn = ctk.CTkFrame(rule_box, fg_color="transparent"); rbtn.pack(fill="x", padx=8, pady=(0,10))
        ctk.CTkButton(rbtn, text="Seçili Kuralı Sil", command=self._delete_selected_rule).pack(side="left", padx=4)

        self._net_refresh()

    def _port_desc(self, port):
        common = {
            20:"FTP Data", 21:"FTP", 22:"SSH", 23:"Telnet", 25:"SMTP",
            53:"DNS", 80:"HTTP", 110:"POP3", 143:"IMAP", 443:"HTTPS",
            3389:"RDP", 3306:"MySQL", 1433:"MSSQL", 1521:"Oracle",
            27017:"MongoDB", 6379:"Redis", 8080:"HTTP Alt", 8443:"HTTPS Alt"
        }
        return common.get(port, "")

    def _net_refresh(self):
        for row in self.net_tree.get_children():
            self.net_tree.delete(row)
        try:
            conns = psutil.net_connections(kind='inet')
            for c in conns:
                if self.only_listen_var.get():
                    if c.status != psutil.CONN_LISTEN:
                        continue
                proto = "TCP" if c.type == socket.SOCK_STREAM else "UDP"
                laddr = f"{c.laddr.ip}:{c.laddr.port}" if c.laddr else "-"
                raddr = f"{c.raddr.ip}:{getattr(c.raddr,'port', '')}" if c.raddr else "-"
                status = c.status
                pid   = c.pid or "-"
                pname = "-"
                try:
                    if c.pid: pname = psutil.Process(c.pid).name()
                except Exception: pass
                desc = self._port_desc(c.laddr.port) if c.laddr else ""
                self.net_tree.insert("", "end", values=(proto, laddr, raddr, status, pid, pname, desc))
        except Exception as e:
            messagebox.showerror("❌", f"Bağlantılar okunamadı: {e}")

        for row in self.rule_tree.get_children():
            self.rule_tree.delete(row)
        rules = self._list_firewall_rules_msclouds()
        for r in rules:
            self.rule_tree.insert("", "end", values=(r.get("Name",""), r.get("Direction",""), r.get("Protocol",""),
                                                     r.get("LocalPort",""), "Evet" if r.get("Enabled", False) else "Hayır"))

    def _list_firewall_rules_msclouds(self):
        ps = (
            "$rs=Get-NetFirewallRule | Where-Object {$_.DisplayName -like 'MSClouds-*'};"
            "$out=@();"
            "foreach($r in $rs){"
            "$pf=Get-NetFirewallPortFilter -AssociatedNetFirewallRule $r;"
            "foreach($p in $pf){"
            "$out+=[pscustomobject]@{Name=$r.DisplayName;Direction=$r.Direction;Enabled=($r.Enabled -eq 'True');Protocol=$p.Protocol;LocalPort=$p.LocalPort}"
            "}"
            "};"
            "$out | ConvertTo-Json -Compress"
        )
        res = SafeSubprocess.run(["powershell","-NoProfile","-Command", ps], timeout=12)
        if res["code"] == 0 and (res["out"] or "").strip():
            try:
                data = json.loads(res["out"])
                if isinstance(data, dict): data = [data]
                return data
            except Exception:
                pass
        return []

    def _add_firewall_rule(self, name, port, proto, direction):
        dir_ps = "Inbound" if direction.lower().startswith("in") else "Outbound"
        cmd_ps = [
            "powershell", "-NoProfile", "-Command",
            f"New-NetFirewallRule -DisplayName '{name}' -Direction {dir_ps} -Action Allow -Protocol {proto} -LocalPort {port}"
        ]
        res = SafeSubprocess.run(cmd_ps, timeout=20)
        if res["code"] == 0:
            return res
        dir_netsh = "in" if dir_ps == "Inbound" else "out"
        cmd_ns = ["netsh","advfirewall","firewall","add","rule",
                  f"name={name}", f"dir={dir_netsh}", "action=allow", f"protocol={proto}", f"localport={port}"]
        return SafeSubprocess.run(cmd_ns, timeout=20)

    def _delete_selected_rule(self):
        sel = self.rule_tree.selection()
        if not sel:
            messagebox.showinfo("Bilgi", "Silmek için listeden bir kural seçin."); return
        name = self.rule_tree.item(sel[0], "values")[0]
        if not name: return
        if not messagebox.askyesno("Onay", f"'{name}' kuralını silmek istiyor musunuz?"):
            return
        ps = ["powershell","-NoProfile","-Command", f"Remove-NetFirewallRule -DisplayName '{name}' -ErrorAction SilentlyContinue"]
        res = SafeSubprocess.run(ps, timeout=12)
        if res["code"] != 0:
            res = SafeSubprocess.run(["netsh","advfirewall","firewall","delete","rule",f"name={name}"], timeout=12)
        if res["code"] == 0:
            messagebox.showinfo("✅", "Kural silindi."); self._net_refresh()
        else:
            msg = res["err"] or res["out"] or "Bilinmeyen hata"
            messagebox.showerror("❌", f"Kural silinemedi.\n{msg}\n\nLütfen uygulamayı 'Yönetici olarak çalıştırın'.")

    def _net_open_port_dialog(self):
        top = ctk.CTkToplevel(self.root)
        top.title("Yeni Port Aç")
        top.geometry("420x360")
        top.grab_set(); top.transient(self.root)

        frm = ctk.CTkFrame(top, corner_radius=12); frm.pack(fill="both", expand=True, padx=16, pady=16)

        v_name = ctk.CTkEntry(frm, placeholder_text="Kural adı (örn. MSClouds-API)")
        v_name.pack(fill="x", padx=10, pady=8)

        row1 = ctk.CTkFrame(frm, fg_color="transparent"); row1.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(row1, text="Port:").pack(side="left")
        v_port = ctk.CTkEntry(row1, width=100); v_port.pack(side="left", padx=6)
        ctk.CTkLabel(row1, text="Protokol:").pack(side="left", padx=(12,0))
        v_proto = ctk.CTkOptionMenu(row1, values=["TCP","UDP"]); v_proto.pack(side="left", padx=6)

        row2 = ctk.CTkFrame(frm, fg_color="transparent"); row2.pack(fill="x", padx=10, pady=4)
        ctk.CTkLabel(row2, text="Yön:").pack(side="left")
        v_dir = ctk.CTkOptionMenu(row2, values=["in","out"]); v_dir.pack(side="left", padx=6)
        ctk.CTkLabel(frm, text="(MSClouds-* ile başlayan adlar listede görünecek)").pack(padx=10, pady=(4,8))
        v_desc = ctk.CTkEntry(frm, placeholder_text="Açıklama (opsiyonel)")
        v_desc.pack(fill="x", padx=10, pady=8)

        if not is_admin():
            ctk.CTkLabel(frm, text="⚠️ Yönetici yetkisi önerilir (aksi halde ekleme başarısız olabilir).",
                         text_color="orange").pack(pady=(0,6))

        def do_add():
            name = v_name.get().strip() or f"MSClouds-Rule-{int(time.time())}"
            try:
                port = int(v_port.get().strip())
            except Exception:
                messagebox.showerror("❌", "Port sayısal olmalı."); return
            proto = v_proto.get(); direc = v_dir.get()
            res = self._add_firewall_rule(name, port, proto, direc)
            if res["code"] == 0:
                messagebox.showinfo("✅", f"{proto} {port} için kural eklendi.")
                top.destroy(); self._net_refresh()
            else:
                msg = res["err"] or res["out"] or "Bilinmeyen hata"
                messagebox.showerror("❌", f"Kural eklenemedi.\n{msg}\n\nLütfen uygulamayı 'Yönetici olarak çalıştırın'.")

        ctk.CTkButton(frm, text="Ekle", command=do_add).pack(side="left", padx=10, pady=12)
        ctk.CTkButton(frm, text="Kapat", command=top.destroy).pack(side="right", padx=10, pady=12)

    # ------------------ Loglar Yardımcıları ------------------
    def _tail_file(self, path, max_lines=200):
        try:
            if not path: return "(!) Log yolu tanımlı değil."
            chunk = 65536
            with open(path, "rb") as f:
                f.seek(0, os.SEEK_END)
                end = f.tell()
                size = min(chunk, end)
                f.seek(end - size, os.SEEK_SET)
                data = f.read().decode(errors="ignore")
            lines = data.splitlines()
            return "\n".join(lines[-max_lines:])
        except Exception as e:
            return f"(!) '{path}' okunamadı: {e}"

    def refresh_logs(self, initial=False):
        self.log_text.delete("1.0", "end")
        selected = self.log_type.get() if not initial else "Sistem Logları"
        mapping = {"Sistem Logları":"system","Apache Logları":"apache","MySQL Logları":"mysql","SSH Logları":"ssh","Güvenlik Logları":"security"}
        kind = mapping.get(selected, "system")
        tail = self.load_config().get("logs", {}).get("tail_lines", 300)
        path = self.load_config().get("logs", {}).get("windows", {}).get(kind)
        content = self._tail_file(path, tail)
        header = f"📂 {selected} • {path or '-'} • son {tail} satır\n" + ("—"*80) + "\n"
        self.log_text.insert("1.0", header + content)

    def clear_logs(self):
        self.log_text.delete("1.0", "end")
        self.log_text.insert("1.0", "🧹 Log ekranı temizlendi.")

    def on_log_type_change(self, _):
        self.refresh_logs()

    # ------------------ Performans Kaydet ------------------
    def save_performance_settings(self):
        messagebox.showinfo("Bilgi", "Ayarlar web panelinden yönetilir. Yerelde kaydetme devre dışıdır.")

    # ------------------ İzleme ------------------
    def _update_metrics(self):
        try:
            # Kalan süre & kilit kontrolü
            self.remaining_time.set(self._remaining_time_text())
            if self._is_expired() and not self._locked:
                self._apply_lockdown()
                return  # UI kilitlendi, diğer metrikleri güncellemeye gerek yok

            # Normal akış
            cpu = psutil.cpu_percent(interval=0.0)
            mem = psutil.virtual_memory()
            dsk = psutil.disk_usage('/')

            self.cpu_usage.set(f"{cpu:.1f}%")
            self.ram_usage.set(f"{mem.percent:.1f}% ({self._human_bytes(mem.used)}/{self._human_bytes(mem.total)})")
            self.disk_usage.set(f"{(dsk.used/dsk.total)*100:.1f}% ({self._human_bytes(dsk.used)}/{self._human_bytes(dsk.total)})")

            self.p_cpu.set(cpu/100.0); self.p_ram.set(mem.percent/100.0); self.p_dsk.set(dsk.used/dsk.total)

            boot = datetime.fromtimestamp(psutil.boot_time())
            diff = datetime.now() - boot
            days = diff.days; h, r = divmod(diff.seconds, 3600); m, _ = divmod(r, 60)
            self.uptime.set(f"{days} gün {h:02d}:{m:02d}")

            cfg = self.load_config().get("performance", {})
            warn = []
            if cpu >= cfg.get("max_cpu_usage", 80): warn.append(f"CPU {cpu:.0f}%")
            if mem.percent >= cfg.get("max_ram_usage", 85): warn.append(f"RAM {mem.percent:.0f}%")
            if self.monitor_warn_label:
                self.monitor_warn_label.configure(text=("⚠️  " + "  •  ".join(warn)) if warn else "")
        except Exception as e:
            print("İzleme hatası:", e)

    def _start_monitoring(self):
        def loop():
            while self.running:
                self.root.after(0, self._update_metrics)
                time.sleep(3)
        threading.Thread(target=loop, daemon=True).start()

    # -------- Lockdown (süre dolunca) --------
    def _apply_lockdown(self):
        """Süre dolduğunda tüm sekmeleri kaldır, monitör sekmesinde yalnızca uyarı göster."""
        self._locked = True
        try:
            # Sunucu durumu
            self.server_status.set("Askıya alındı")

            # Diğer sekmeleri tamamen kaldır
            for name in [self.TAB_MANAGEMENT, self.TAB_LOGS, self.TAB_PERF, self.TAB_SUPPORT, self.TAB_NETWORK, self.TAB_UPDATE]:
                try:
                    self.tabs.delete(name)
                except Exception:
                    pass

            # Monitör sekmesindeki tüm içerikleri temizle
            for child in list(self.tab_monitor.winfo_children()):
                try:
                    child.destroy()
                except Exception:
                    pass

            # Ortalanmış büyük uyarı mesajı
            wrap = ctk.CTkFrame(self.tab_monitor, corner_radius=12)
            wrap.pack(fill="both", expand=True, padx=40, pady=40)
            inner = ctk.CTkFrame(wrap, corner_radius=16)
            inner.place(relx=0.5, rely=0.5, anchor="center")

            title = ctk.CTkLabel(inner, text="⚠️ Dikkat: Erişiminiz sınırlandırıldı", font=ctk.CTkFont(size=24, weight="bold"))
            subtitle = ctk.CTkLabel(inner, text="Verilerinizi kaybedebilirsiniz.", font=ctk.CTkFont(size=16))
            status = ctk.CTkLabel(inner, text="Durum: Askıya alındı", font=ctk.CTkFont(size=18, weight="bold"))

            # Dikey yerleşim
            title.pack(padx=40, pady=(28, 10))
            subtitle.pack(padx=40, pady=(0, 16))
            status.pack(padx=40, pady=(0, 28))

        except Exception as e:
            print("Lockdown hatası:", e)

    # ------------------ Sistem Eylemleri ------------------
    def _human_bytes(self, n):
        for u in ["B","KB","MB","GB","TB"]:
            if n < 1024: return f"{n:.1f} {u}"
            n /= 1024
        return f"{n:.1f} PB"

    def cleanup_system(self):
        if not messagebox.askyesno("🧹 Temizlik", "Sistem temizliği başlatılsın mı?\n• Temp\n• Geri Dönüşüm Kutusu\n• DNS önbelleği"):
            return
        dlg = BusyDialog(self.root, title="🧹 Temizlik", text="Temizlik işlemleri çalışıyor…")

        def worker():
            freed = 0
            try:
                freed += self._clean_path(Path(os.getenv("TEMP", "C:/Windows/Temp")))
                freed += self._clean_path(Path("C:/Windows/Temp"))
                SafeSubprocess.run(["powershell","-NoProfile","-Command","Clear-RecycleBin -Force -ErrorAction SilentlyContinue"], timeout=30)
                SafeSubprocess.run(["ipconfig","/flushdns"], timeout=10)
                self.root.after(0, lambda: messagebox.showinfo("✅ Başarılı", f"Temizlik tamamlandı (~{freed/1024/1024:.1f} MB)."))
            except Exception as e:
                self.root.after(0, lambda: messagebox.showerror("❌ Hata", f"Temizlik hatası: {e}"))
            finally:
                self.root.after(0, dlg.close)
        threading.Thread(target=worker, daemon=True).start()

    def _dir_size(self, path: Path):
        total = 0
        try:
            for root, dirs, files in os.walk(path, topdown=False):
                for nm in files:
                    fp = os.path.join(root, nm)
                    try: total += os.path.getsize(fp)
                    except Exception: pass
        except Exception: pass
        return total

    def _clean_path(self, path):
        freed = 0
        try:
            p = Path(path)
            if not p.exists(): return 0
            for item in p.iterdir():
                try:
                    if item.is_file():
                        size = item.stat().st_size
                        item.unlink(missing_ok=True); freed += size
                    elif item.is_dir():
                        size = self._dir_size(item)
                        shutil.rmtree(item, ignore_errors=True); freed += size
                except Exception: continue
        except Exception: pass
        return freed

    def security_scan(self):
        exe = self._find_mpcmdrun()
        if not exe:
            messagebox.showwarning("ℹ️ Bilgi", "Windows Defender bulunamadı.")
            return
        dlg = BusyDialog(self.root, title="🔒 Güvenlik Taraması", text="Windows Defender hızlı tarama…")

        def worker():
            try:
                res = SafeSubprocess.run([exe, "-Scan", "-ScanType", "1"], timeout=60)
                if res["err"] == "timeout":
                    self.root.after(0, lambda: messagebox.showwarning("⏱️", "Tarama 60 sn içinde tamamlanmadı."))
                elif res["code"] == 0:
                    out = (res["out"] or "").strip()
                    self.root.after(0, lambda: messagebox.showinfo("✅ Tamamlandı", (out[-1200:] or "Tamamlandı.")))
                else:
                    self.root.after(0, lambda: messagebox.showerror("❌ Hata", res["err"] or "Tarama başarısız."))
            finally:
                self.root.after(0, dlg.close)
        threading.Thread(target=worker, daemon=True).start()

    def _find_mpcmdrun(self):
        paths = [
            r"C:\Program Files\Windows Defender\MpCmdRun.exe",
            r"C:\Program Files\Windows Defender\MpCmdRun\MpCmdRun.exe",
            r"C:\Program Files\Windows Defender"
        ]
        for p in paths:
            if os.path.isfile(p): return p
            if os.path.isdir(p):
                for root, dirs, files in os.walk(p):
                    if "MpCmdRun.exe" in files: return os.path.join(root, "MpCmdRun.exe")
        if shutil.which("MpCmdRun.exe"): return "MpCmdRun.exe"
        return None

    def generate_report(self):
        cfg = self.load_config()
        lines = []
        for key, svc in cfg.get("services", {}).items():
            name = svc.get("windows_service")
            try:
                q = subprocess.run(["sc","query",name], capture_output=True, text=True)
                status = "Çalışıyor ✅" if "RUNNING" in q.stdout.upper() else "Durdurulmuş ⛔"
            except Exception:
                status = "Bilinmiyor"
            lines.append(f"   • {svc.get('name','?')}: {status}")
        data = f"""📊 SUNUCU RAPORU - {datetime.now().strftime('%d.%m.%Y %H:%M')}

🖥️ Sistem:
   • Hostname: {platform.node()}
   • OS: {platform.system()} {platform.release()}
   • CPU: {self.cpu_usage.get()}
   • RAM: {self.ram_usage.get()}
   • Disk: {self.disk_usage.get()}
   • Uptime: {self.uptime.get()}

⚙️ Servisler:
{os.linesep.join(lines)}
"""
        w = ctk.CTkToplevel(self.root); w.title("📊 Sistem Raporu"); w.geometry("720x560")
        f = ctk.CTkFrame(w, corner_radius=15); f.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(f, text="📊 Sistem Raporu", font=ctk.CTkFont(size=20, weight="bold")).pack(pady=(18,12))
        t = ctk.CTkTextbox(f, font=ctk.CTkFont("Consolas", 12)); t.pack(fill="both", expand=True, padx=18, pady=(0,16))
        t.insert("1.0", data)

    def optimize_system(self):
        if not messagebox.askyesno("⚙️ Optimizasyon", "Hızlı optimizasyon başlatılsın mı?\n• DNS Flush\n• Küçük temp temizliği"):
            return
        dlg = BusyDialog(self.root, title="⚙️ Optimizasyon", text="Hızlı optimizasyon çalışıyor…")
        def worker():
            try:
                SafeSubprocess.run(["ipconfig","/flushdns"], timeout=10)
                self._clean_path(Path(os.getenv("TEMP", "C:/Windows/Temp")))
                self.root.after(0, lambda: messagebox.showinfo("✅ Tamamlandı", "Hızlı optimizasyon uygulandı."))
            finally:
                self.root.after(0, dlg.close)
        threading.Thread(target=worker, daemon=True).start()

    # ------------------ Güncelleme sekmesi ------------------
    def _build_update(self):
        wrap = ctk.CTkFrame(self.tab_update, corner_radius=12)
        wrap.pack(fill="both", expand=True, padx=20, pady=20)
        ctk.CTkLabel(wrap, text="🔄 GÜNCELLEME", font=self.font_header).pack(pady=(18, 10))
        info = ctk.CTkFrame(wrap, corner_radius=12, fg_color="transparent"); info.pack(fill="x", padx=20, pady=10)
        row = ctk.CTkFrame(info, fg_color="transparent"); row.pack(fill="x", padx=18, pady=6)
        ctk.CTkLabel(row, text="Mevcut sürüm:", font=self.font_large).pack(side="left")
        ctk.CTkLabel(row, text=APP_VERSION, font=self.font_large).pack(side="left", padx=10)
        ctk.CTkButton(info, text="Konfigürasyonu Yenile (şimdi)", command=self._check_config_change).pack(side="left", padx=18, pady=8)
        self.update_text = ctk.CTkTextbox(wrap, height=380, font=ctk.CTkFont("Consolas", 12))
        self.update_text.pack(fill="both", expand=True, padx=20, pady=(10, 20))
        self.update_text.insert("1.0", "Konfigürasyon URL'den okunur. 5 dakikada bir değişiklik kontrol edilir.\n")

    def _log_update(self, line):
        ts = datetime.now().strftime("%H:%M:%S")
        self.update_text.insert("end", f"[{ts}] {line}\n")
        self.update_text.see("end")

    def _check_config_change(self):
        changed = self._reload_config_if_changed()
        if changed:
            self._log_update("Uzak konfigürasyon değişti; yeniden yüklendi.")
            self.brand_label.configure(text=self._brand_chip())
            # Expiry durumu değişmiş olabilir:
            self.remaining_time.set(self._remaining_time_text())
            if self._is_expired() and not self._locked:
                self._apply_lockdown()
        else:
            self._log_update("Uzak konfigürasyonda değişiklik yok.")

    def _schedule_update_checks(self):
        def loop():
            while self.running:
                try:
                    self.root.after(0, self._check_config_change)
                except Exception:
                    pass
                time.sleep(300)  # 5 dk
        threading.Thread(target=loop, daemon=True).start()

    # ------------------ Lifecycle ------------------
    def run(self):
        # Kapatmayı tamamen engelle (tepsiye indir)
        self.root.protocol("WM_DELETE_WINDOW", self._minimize_to_tray)
        self.root.mainloop()

    def _on_close_force(self):
        """
        Bu fonksiyon normalde kullanılmıyor; gerçekten çıkmak istenirse (örn. uninstall)
        kod içinden çağrılabilir. Tepsi ve thread'leri temizler.
        """
        self.running = False
        self.sock_running = False
        try:
            if self.sock: self.sock.close()
        except Exception: pass
        try:
            if hasattr(self, "agent") and self.agent: self.agent.stop()
        except Exception: pass
        # Tepsiyi kapat
        if self._tray_icon is not None:
            try: self._tray_icon.stop()
            except Exception: pass
            self._tray_icon = None
        self.root.destroy()


# =========================================================
#                         MAIN
# =========================================================
if __name__ == "__main__":
    try:
        import customtkinter, psutil
        if not _TRAY_AVAILABLE:
            # pystray/Pillow eksik ise uyarı verelim ama app çalışır
            print("ℹ️ Sistem tepsisi için pystray + pillow önerilir. Kurulum: pip install pystray pillow")
    except ImportError as e:
        print(f"❌ Eksik kütüphane: {e}\n📦 Kurulum: pip install customtkinter psutil pystray pillow")
        sys.exit(1)

    # ---- Watchdog başlat (kendini koru) ----
    # Ana süreç yeniden başlatılmak üzere bir izleyici süreci (pythonw) başlatır.
    try:
        pythonw = _pick_pythonw()
        main_cmd = [sys.executable, os.path.abspath(sys.argv[0])]
        # Watchdog'a parent pid ve yeniden başlat komutunu json ile veriyoruz
        wd_cmd = [pythonw, os.path.abspath(sys.argv[0]), "--watchdog", str(os.getpid()), json.dumps(main_cmd)]
        # Sessiz başlat
        subprocess.Popen(wd_cmd, creationflags=subprocess.CREATE_NO_WINDOW)
    except Exception:
        pass

    app = ServerManagementUI()
    app.run()
