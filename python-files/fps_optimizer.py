# FPS Optimizer & Monitor — with optional KeyAuth license gate (CustomTkinter)

# --- Dependencies ---
# pip install customtkinter psutil pynvml requests
# Optional: Install PresentMon for FPS capture (Windows)

import os
import time
import threading
import subprocess
import csv
import shutil
import platform
import ctypes
from pathlib import Path
import hashlib
from typing import Optional, Tuple

# GUI
import customtkinter as ctk
from tkinter import messagebox

# System
import psutil

# Optional NVIDIA NVML
try:
    import pynvml
    pynvml.nvmlInit()
    NVML_AVAILABLE = True
except Exception:
    NVML_AVAILABLE = False

# ----------------------------- Optional KeyAuth Integration -----------------------------
# This block is **optional**. If the KeyAuth SDK is installed, a license window is shown first.
# If it's not installed, the app launches without a login gate.

try:
    # Most KeyAuth Python SDKs expose a class named `api` inside `keyauth` or `keyauth.api`.
    # We support both. Only one needs to succeed.
    try:
        from keyauth import api as KeyAuthApi
    except Exception:
        from keyauth.api import api as KeyAuthApi  # type: ignore
except Exception:
    KeyAuthApi = None  # type: ignore

# Fill these with your KeyAuth application values
KEYAUTH_APP_NAME   = "FPS KEY AUTH"
KEYAUTH_OWNER_ID   = "7jIlTki8SA"
KEYAUTH_VERSION    = "1.0"


def getchecksum() -> str:
    """Return SHA256 hash of this script (or the compiled exe)."""
    try:
        filename = __file__
        if not os.path.exists(filename):
            return ""
        with open(filename, "rb") as f:
            data = f.read()
        return hashlib.sha256(data).hexdigest()
    except Exception:
        return ""


keyauthapp = None
if KeyAuthApi is not None:
    try:
        keyauthapp = KeyAuthApi(
            name=KEYAUTH_APP_NAME,
            ownerid=KEYAUTH_OWNER_ID,
            version=KEYAUTH_VERSION,
            hash_to_check=getchecksum(),
        )
    except TypeError:
        # Some SDK variants want `hash_to_check` omitted; try the minimal constructor
        try:
            keyauthapp = KeyAuthApi(
                name=KEYAUTH_APP_NAME,
                ownerid=KEYAUTH_OWNER_ID,
                version=KEYAUTH_VERSION,
            )
        except Exception:
            keyauthapp = None
    except Exception:
        keyauthapp = None

# ----------------------------- Globals -------------------------------------
IS_WINDOWS = (platform.system() == "Windows")
APP_TITLE = "FPS Optimizer & Monitor"

# ----------------------------- Helpers -------------------------------------

def find_presentmon() -> Optional[str]:
    """Return PresentMon.exe path if available, else None."""
    exe = "PresentMon.exe" if IS_WINDOWS else None
    if not exe:
        return None
    # Check PATH
    path = shutil.which(exe)
    if path:
        return path
    # Common locations
    common_dirs = [
        os.path.expandvars(r"%ProgramFiles%\PresentMon"),
        os.path.expandvars(r"%ProgramFiles(x86)%\PresentMon"),
        str(Path.home() / "AppData/Local/Programs/PresentMon"),
    ]
    for d in common_dirs:
        cand = os.path.join(d, exe)
        if os.path.isfile(cand):
            return cand
    return None

PRESENTMON_PATH = find_presentmon()


def list_gamey_processes():
    """Return a list of (pid, name) for user processes that look like games."""
    names_exclude = {
        "explorer.exe","ctfmon.exe","searchapp.exe","shellexperiencehost.exe","runtimebroker.exe",
        "startmenuexperiencehost.exe","svchost.exe","audiodg.exe","system","idle"
    }
    procs = []
    for p in psutil.process_iter(["pid","name","username"]):
        try:
            name = (p.info["name"] or "").lower()
            if not name or name in names_exclude:
                continue
            if p.info.get("username") is None:
                continue
            if IS_WINDOWS:
                try:
                    exe = p.exe().lower()
                    if "windows\\" in exe and "program files" not in exe:
                        continue
                except Exception:
                    pass
            procs.append((p.info["pid"], p.info["name"]))
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

    def mem_of(pid):
        try:
            return psutil.Process(pid).memory_info().rss
        except Exception:
            return 0

    procs.sort(key=lambda x: mem_of(x[0]), reverse=True)
    return procs


def readable_hz(fps: Optional[float]) -> str:
    if fps is None or fps != fps:
        return "—"
    return f"{fps:.1f} FPS"


# ----------------------------- PresentMon Runner ---------------------------
class PresentMonRunner:
    def __init__(self, exe_path: str):
        self.exe_path = exe_path
        self.proc: Optional[subprocess.Popen] = None
        self.thread: Optional[threading.Thread] = None
        self.stop_event = threading.Event()
        self.latest_fps: Optional[float] = None
        self.lock = threading.Lock()

    def start(self, pid: int):
        if not IS_WINDOWS:
            raise RuntimeError("PresentMon only supported on Windows")
        if self.proc is not None:
            self.stop()
        args = [self.exe_path, "-captureall", "-process_id", str(pid), "-q", "-output_stdout"]
        self.proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, bufsize=1)
        self.stop_event.clear()
        self.thread = threading.Thread(target=self._reader_loop, daemon=True)
        self.thread.start()

    def _reader_loop(self):
        assert self.proc and self.proc.stdout
        reader = csv.reader(self.proc.stdout)
        header_parsed = False
        last_times = []
        try:
            for row in reader:
                if self.stop_event.is_set():
                    break
                if not header_parsed:
                    header_parsed = True
                    continue
                ms = None
                for cell in row:
                    try:
                        v = float(cell)
                        if 0.0 < v < 1000.0:
                            ms = v
                            break
                    except Exception:
                        continue
                if ms is None:
                    continue
                last_times.append(ms)
                if len(last_times) > 60:
                    last_times.pop(0)
                if last_times:
                    avg_ms = sum(last_times) / len(last_times)
                    fps = 1000.0 / max(0.01, avg_ms)
                    with self.lock:
                        self.latest_fps = fps
        except Exception:
            pass

    def get_fps(self) -> Optional[float]:
        with self.lock:
            return self.latest_fps

    def stop(self):
        self.stop_event.set()
        if self.proc:
            try:
                self.proc.terminate()
            except Exception:
                pass
            self.proc = None


# ----------------------------- Optimizers ----------------------------------
class Optimizer:
    """Collections of safe-ish toggles. Windows-focused."""
    def __init__(self, log_fn):
        self.log = log_fn
        self.changes = {}

    # --- Existing tweaks ---
    def set_high_priority(self, pid: int):
        try:
            p = psutil.Process(pid)
            if IS_WINDOWS:
                try:
                    import win32process
                    win32process.SetPriorityClass(p.handle, win32process.HIGH_PRIORITY_CLASS)
                    self.log("Set process priority: HIGH")
                    self.changes.setdefault("priority", []).append(pid)
                except Exception:
                    p.nice(psutil.HIGH_PRIORITY_CLASS)
                    self.log("Set process priority (fallback): HIGH")
                    self.changes.setdefault("priority", []).append(pid)
            else:
                p.nice(-5)
                self.log("Set process nice to -5")
        except Exception as e:
            self.log(f"Priority tweak failed: {e}")

    def uncap_power_plan(self):
        if not IS_WINDOWS:
            self.log("Power plan tweak is Windows-only.")
            return
        try:
            subprocess.run(["powercfg","/S","e9a42b02-d5df-448d-aa00-03f14749eb61"], check=False)
            subprocess.run(["powercfg","/S","8c5e7fda-e8bf-4a96-9a85-a6e23a8c635c"], check=False)
            self.log("Set power plan to High/Ultimate Performance (if available)")
            self.changes["power_plan"] = True
        except Exception as e:
            self.log(f"Power plan tweak failed: {e}")

    def disable_xbox_gamebar(self):
        if not IS_WINDOWS:
            return self.log("Xbox Game Bar tweak is Windows-only.")
        try:
            subprocess.run(["reg","add", r"HKCU\SOFTWARE\Microsoft\Windows\CurrentVersion\GameDVR",
                            "/v","AppCaptureEnabled","/t","REG_DWORD","/d","0","/f"], check=False)
            subprocess.run(["reg","add", r"HKCU\System\GameConfigStore",
                            "/v","GameDVR_Enabled","/t","REG_DWORD","/d","0","/f"], check=False)
            self.log("Disabled Xbox Game Bar / Game DVR (current user)")
            self.changes["xbox_gamebar"] = True
        except Exception as e:
            self.log(f"Xbox Game Bar tweak failed: {e}")

    def stop_backgrounds(self):
        candidates = ["OneDrive.exe","Dropbox.exe","SteamWebHelper.exe","Discord.exe",
                      "EpicGamesLauncher.exe","chrome.exe","opera.exe","CefSharp.BrowserSubprocess.exe"]
        stopped = []
        for proc in psutil.process_iter(["pid","name"]):
            try:
                if proc.info["name"] in candidates and proc.pid != os.getpid():
                    proc.terminate()
                    stopped.append(proc.info["name"])
            except Exception:
                continue
        if stopped:
            self.log("Terminated: " + ", ".join(sorted(set(stopped))))
            self.changes.setdefault("stopped", []).extend(stopped)
        else:
            self.log("No heavy background apps found to stop.")

    def apply_gpu_pref(self, pid: int):
        if not IS_WINDOWS:
            return
        try:
            exe = psutil.Process(pid).exe()
            key = r"HKCU\SOFTWARE\Microsoft\DirectX\UserGpuPreferences"
            subprocess.run(["reg","add", key, "/v", exe, "/t","REG_SZ","/d","GpuPreference=2;","/f"], check=False)
            self.log("Hinted High-Performance GPU preference for the game")
            self.changes.setdefault("gpu_pref", []).append(exe)
        except Exception as e:
            self.log(f"GPU preference tweak failed: {e}")

    # --- Stronger tweaks ---
    def disable_visual_effects(self):
        if not IS_WINDOWS:
            return
        try:
            subprocess.run(["reg","add",
                            r"HKCU\Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects",
                            "/v","VisualFXSetting","/t","REG_DWORD","/d","2","/f"], check=False)
            self.log("Disabled Windows visual effects (best performance).")
            self.changes["visual_effects"] = True
        except Exception as e:
            self.log(f"Visual effects tweak failed: {e}")

    def disable_background_apps(self):
        if not IS_WINDOWS:
            return
        try:
            subprocess.run(["reg","add",
                            r"HKCU\Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications",
                            "/v","GlobalUserDisabled","/t","REG_DWORD","/d","1","/f"], check=False)
            self.log("Disabled Windows background apps (current user).")
            self.changes["bg_apps"] = True
        except Exception as e:
            self.log(f"Background apps tweak failed: {e}")

    def clear_temp_files(self):
        if not IS_WINDOWS:
            return
        try:
            temp_dirs = [os.getenv("TEMP"), os.getenv("TMP"), r"C:\\Windows\\Prefetch"]
            cleared = 0
            for d in temp_dirs:
                if d and os.path.exists(d):
                    for f in os.listdir(d):
                        fp = os.path.join(d, f)
                        try:
                            if os.path.isfile(fp):
                                os.remove(fp)
                                cleared += 1
                        except Exception:
                            continue
            self.log(f"Cleared {cleared} temporary/prefetch files.")
        except Exception as e:
            self.log(f"Temp file cleanup failed: {e}")

    def flush_dns_cache(self):
        if not IS_WINDOWS:
            return
        try:
            subprocess.run(["ipconfig","/flushdns"], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            self.log("Flushed DNS cache.")
        except Exception as e:
            self.log(f"DNS flush failed: {e}")

    def disable_fullscreen_optimizations_for(self, pid: int):
        """Disable Fullscreen Optimizations for the attached game's exe (compat layer)."""
        if not IS_WINDOWS:
            return
        try:
            exe = psutil.Process(pid).exe()
            key = r"HKCU\Software\Microsoft\Windows NT\CurrentVersion\AppCompatFlags\Layers"
            val = "DISABLEDXMAXIMIZEDWINDOWEDMODE HIGHDPIAWARE"
            subprocess.run(["reg","add", key, "/v", exe, "/t","REG_SZ",\
                            "/d", val, "/f"], check=False)
            self.log("Disabled Fullscreen Optimizations for the game (compat flags).")
            self.changes.setdefault("fso", []).append(exe)
        except Exception as e:
            self.log(f"Fullscreen Optimizations tweak failed: {e}")

    def revert(self):
        if self.changes.get("power_plan") and IS_WINDOWS:
            try:
                subprocess.run(["powercfg","/S","381b4222-f694-41f0-9685-ff5bb260df2e"], check=False)
            except Exception:
                pass
        self.changes.clear()
        self.log("Reverted power plan to Balanced (if changed). Other changes are non-destructive and can be re-enabled in Windows settings if desired.")


# ----------------------------- Expectation Model ---------------------------

def estimate_expected_fps(current_fps: Optional[float], cpu_util: float, gpu_util: Optional[float]) -> Tuple[Optional[float], str]:
    """Heuristic 'should get' FPS by removing detected bottleneck utilization."""
    if current_fps is None or current_fps <= 0:
        return None, "Waiting for FPS data…"
    note = ""
    if gpu_util is not None and gpu_util > 90:
        expected = current_fps * (100.0 / gpu_util)
        note = "GPU-bound"
    elif cpu_util > 85:
        expected = current_fps * (100.0 / cpu_util)
        note = "CPU-bound"
    else:
        expected = current_fps * 1.10
        note = "No clear bottleneck"
    expected = max(1.0, min(expected, current_fps * 2.5))
    return expected, note


# ----------------------------- Timer Resolution ----------------------------
class HighResTimer:
    """Increase Windows timer resolution to 1ms while running."""
    def __init__(self, log_fn):
        self.log = log_fn
        self._ok = False

    def start(self):
        if not IS_WINDOWS:
            return
        try:
            res = ctypes.windll.winmm.timeBeginPeriod(1)
            if res == 0:
                self._ok = True
                self.log("Set system timer resolution to 1ms (temporary).")
        except Exception:
            pass

    def stop(self):
        if not IS_WINDOWS or not self._ok:
            return
        try:
            ctypes.windll.winmm.timeEndPeriod(1)
            self._ok = False
            self.log("Restored system timer resolution.")
        except Exception:
            pass


# ----------------------------- UI -----------------------------------------
class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title(APP_TITLE)
        self.geometry("1024x700")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")

        self.present = PresentMonRunner(PRESENTMON_PATH) if PRESENTMON_PATH else None
        self.optimizer = Optimizer(self.log)

        self.selected_pid = None
        self.monitor_thread = None
        self.monitor_stop = threading.Event()

        self.timer_res = HighResTimer(self.log)
        self.timer_res.start()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._build()
        self._refresh_processes()

    def _on_close(self):
        try:
            if self.present:
                self.present.stop()
            self.monitor_stop.set()
            self.timer_res.stop()
        finally:
            self.destroy()

    # UI Layout
    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.tabs = ctk.CTkTabview(self)
        self.tabs.grid(row=0, column=0, sticky="nsew", padx=14, pady=14)

        self.tab_monitor = self.tabs.add("Monitor")
        self.tab_opt = self.tabs.add("Optimize")
        self.tab_bench = self.tabs.add("Benchmark")
        self.tab_log = self.tabs.add("Log")

        # Monitor tab
        self.tab_monitor.grid_columnconfigure(0, weight=1)

        self.proc_combo = ctk.CTkComboBox(self.tab_monitor, values=["(loading)"], width=420)
        self.proc_combo.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, 4))

        self.refresh_btn = ctk.CTkButton(self.tab_monitor, text="Refresh Processes", command=self._refresh_processes)
        self.refresh_btn.grid(row=0, column=1, padx=8, pady=(8, 4))

        self.attach_btn = ctk.CTkButton(self.tab_monitor, text="Attach & Start", command=self._attach)
        self.attach_btn.grid(row=0, column=2, padx=8, pady=(8, 4))

        self.detach_btn = ctk.CTkButton(self.tab_monitor, text="Detach", command=self._detach)
        self.detach_btn.grid(row=0, column=3, padx=8, pady=(8, 4))

        self.fps_label = ctk.CTkLabel(self.tab_monitor, text="FPS: —", font=("Segoe UI", 28, "bold"))
        self.fps_label.grid(row=1, column=0, columnspan=2, sticky="w", padx=8, pady=(16, 4))

        self.expected_label = ctk.CTkLabel(self.tab_monitor, text="Expected: — (—)", font=("Segoe UI", 18))
        self.expected_label.grid(row=2, column=0, columnspan=2, sticky="w", padx=8, pady=(4, 12))

        self.util_label = ctk.CTkLabel(self.tab_monitor, text="CPU: —% | GPU: —%", font=("Segoe UI", 16))
        self.util_label.grid(row=3, column=0, columnspan=2, sticky="w", padx=8, pady=(4, 12))

        self.note_label = ctk.CTkLabel(self.tab_monitor, text="", font=("Segoe UI", 14))
        self.note_label.grid(row=4, column=0, columnspan=3, sticky="w", padx=8, pady=(4, 12))

        # Optimize tab
        self.tab_opt.grid_columnconfigure(0, weight=1)

        self.priority_btn = ctk.CTkButton(self.tab_opt, text="Set High Priority (Game)", command=self._tweak_priority)
        self.priority_btn.grid(row=0, column=0, sticky="w", padx=8, pady=8)

        self.power_btn = ctk.CTkButton(self.tab_opt, text="Max Performance Power Plan",
                                       command=self.optimizer.uncap_power_plan)
        self.power_btn.grid(row=0, column=1, sticky="w", padx=8, pady=8)

        self.gpu_pref_btn = ctk.CTkButton(self.tab_opt, text="Prefer High-Perf GPU (Game)",
                                          command=self._tweak_gpu_pref)
        self.gpu_pref_btn.grid(row=0, column=2, sticky="w", padx=8, pady=8)

        self.bg_btn = ctk.CTkButton(self.tab_opt, text="Stop Background Hogs", command=self.optimizer.stop_backgrounds)
        self.bg_btn.grid(row=1, column=0, sticky="w", padx=8, pady=8)

        self.gamebar_btn = ctk.CTkButton(self.tab_opt, text="Disable Xbox Game Bar",
                                         command=self.optimizer.disable_xbox_gamebar)
        self.gamebar_btn.grid(row=1, column=1, sticky="w", padx=8, pady=8)

        self.fso_btn = ctk.CTkButton(self.tab_opt, text="Disable Fullscreen Optimizations (Game)",
                                     command=self._disable_fso)
        self.fso_btn.grid(row=1, column=2, sticky="w", padx=8, pady=8)

        self.visfx_btn = ctk.CTkButton(self.tab_opt, text="Disable Visual Effects",
                                       command=self.optimizer.disable_visual_effects)
        self.visfx_btn.grid(row=2, column=0, sticky="w", padx=8, pady=8)

        self.bgapps_btn = ctk.CTkButton(self.tab_opt, text="Disable Background Apps",
                                        command=self.optimizer.disable_background_apps)
        self.bgapps_btn.grid(row=2, column=1, sticky="w", padx=8, pady=8)

        self.temp_btn = ctk.CTkButton(self.tab_opt, text="Clear Temp & Prefetch",
                                      command=self.optimizer.clear_temp_files)
        self.temp_btn.grid(row=2, column=2, sticky="w", padx=8, pady=8)

        self.dns_btn = ctk.CTkButton(self.tab_opt, text="Flush DNS Cache", command=self.optimizer.flush_dns_cache)
        self.dns_btn.grid(row=3, column=0, sticky="w", padx=8, pady=8)

        self.revert_btn = ctk.CTkButton(self.tab_opt, text="Revert Safe Changes", fg_color="#444444",
                                        command=self.optimizer.revert)
        self.revert_btn.grid(row=3, column=2, sticky="w", padx=8, pady=8)

        tip = ("These toggles make safe, revertible changes. Some actions may require admin rights.\n"
               "For best results: update GPU drivers, close overlays, cap FPS slightly below refresh, and use in-game FSR/DLSS.")
        self.tip_label = ctk.CTkLabel(self.tab_opt, text=tip, wraplength=900, justify="left")
        self.tip_label.grid(row=4, column=0, columnspan=3, sticky="w", padx=8, pady=8)

        # Benchmark tab
        self.bench_btn = ctk.CTkButton(self.tab_bench, text="60s Capture (if PresentMon available)",
                                       command=self._bench_60s)
        self.bench_btn.grid(row=0, column=0, sticky="w", padx=8, pady=8)

        self.bench_result = ctk.CTkLabel(self.tab_bench, text="No benchmark yet.")
        self.bench_result.grid(row=1, column=0, sticky="w", padx=8, pady=8)

        # Log tab
        self.logbox = ctk.CTkTextbox(self.tab_log, width=980, height=520)
        self.logbox.grid(row=0, column=0, sticky="nsew", padx=8, pady=8)
        self.tab_log.grid_rowconfigure(0, weight=1)
        self.tab_log.grid_columnconfigure(0, weight=1)

        # Footer
        present_str = (PRESENTMON_PATH or "not found")
        nvml_str = ("yes" if NVML_AVAILABLE else "no")
        self.footer = ctk.CTkLabel(self, text=(f"PresentMon: {present_str}  |  NVML: {nvml_str}"))
        self.footer.grid(row=1, column=0, sticky="ew", padx=12, pady=(0, 10))

    # Logging helper
    def log(self, msg: str):
        ts = time.strftime("%H:%M:%S")
        try:
            self.logbox.insert("end", f"[{ts}] {msg}\n")
            self.logbox.see("end")
        except Exception:
            print(f"[{ts}] {msg}")

    # Process handling
    def _refresh_processes(self):
        procs = list_gamey_processes()
        items = [f"{name} (pid {pid})" for pid, name in procs]
        self.proc_index = {f"{name} (pid {pid})": pid for pid, name in procs}
        if not items:
            items = ["<no user processes>"]
        self.proc_combo.configure(values=items)
        if items:
            self.proc_combo.set(items[0])

    def _attach(self):
        key = self.proc_combo.get()
        pid = getattr(self, "proc_index", {}).get(key)
        if not pid:
            self.log("Select a valid process first.")
            return
        self.selected_pid = pid
        self.log(f"Attached to PID {pid}")
        if self.present:
            try:
                self.present.start(pid)
                self.log("PresentMon capture started.")
            except Exception as e:
                self.log(f"PresentMon failed: {e}")
        self._start_monitor_loop()

    def _detach(self):
        self.selected_pid = None
        if self.present:
            self.present.stop()
        self.monitor_stop.set()
        self.fps_label.configure(text="FPS: —")
        self.expected_label.configure(text="Expected: — (—)")
        self.util_label.configure(text="CPU: —% | GPU: —%")
        self.note_label.configure(text="")
        self.log("Detached.")

    def _start_monitor_loop(self):
        self.monitor_stop.clear()
        if self.monitor_thread and self.monitor_thread.is_alive():
            return
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()

    def _monitor_loop(self):
        while not self.monitor_stop.is_set():
            cpu_util = psutil.cpu_percent(interval=0.5)
            gpu_util = None
            if NVML_AVAILABLE:
                try:
                    gcount = pynvml.nvmlDeviceGetCount()
                    if gcount > 0:
                        util_sum = 0
                        for i in range(gcount):
                            h = pynvml.nvmlDeviceGetHandleByIndex(i)
                            util = pynvml.nvmlDeviceGetUtilizationRates(h)
                            util_sum += util.gpu
                        gpu_util = util_sum / gcount
                except Exception:
                    gpu_util = None

            fps = self.present.get_fps() if self.present else None
            exp, note = estimate_expected_fps(fps, cpu_util, gpu_util if gpu_util is not None else 0)

            self.fps_label.configure(text=f"FPS: {readable_hz(fps)}")
            gpustr = "—" if gpu_util is None else f"{gpu_util:.0f}"
            self.util_label.configure(text=f"CPU: {cpu_util:.0f}% | GPU: {gpustr}%")
            if exp is None:
                self.expected_label.configure(text="Expected: — (—)")
            else:
                self.expected_label.configure(text=f"Expected: {exp:.1f} ({note})")
            self.note_label.configure(
                text="Tip: If GPU util is high and FPS is low, lower graphics or enable DLSS/FSR. If CPU is high, reduce crowd/AI, view distance, or background apps.")

    # Tweaks bound to selected process
    def _tweak_priority(self):
        if not self.selected_pid:
            self.log("Attach to your game first.")
            return
        self.optimizer.set_high_priority(self.selected_pid)

    def _tweak_gpu_pref(self):
        if not self.selected_pid:
            self.log("Attach to your game first.")
            return
        self.optimizer.apply_gpu_pref(self.selected_pid)

    def _disable_fso(self):
        if not self.selected_pid:
            self.log("Attach to your game first.")
            return
        self.optimizer.disable_fullscreen_optimizations_for(self.selected_pid)

    # Benchmark
    def _bench_60s(self):
        if not self.present or not self.selected_pid:
            self.log("Benchmark needs PresentMon and an attached process.")
            self.bench_result.configure(text="Benchmark unavailable: attach & ensure PresentMon.")
            return
        self.log("Benchmark: capturing 60 seconds…")
        start = time.time()
        samples = []
        while time.time() - start < 60:
            fps = self.present.get_fps()
            if fps:
                samples.append(fps)
            time.sleep(0.25)
        if not samples:
            self.bench_result.configure(text="No FPS samples captured.")
            return
        samples_sorted = sorted(samples)
        avg = sum(samples) / len(samples)
        p1 = samples_sorted[max(0, int(0.01 * len(samples_sorted)) - 1)]
        p99 = samples_sorted[min(len(samples_sorted)-1, int(0.99 * len(samples_sorted)))]
        self.bench_result.configure(text=f"Avg: {avg:.1f} FPS | 1%: {p1:.1f} | 99%: {p99:.1f}")
        self.log("Benchmark complete.")


# ----------------------------- KeyAuth Gate UI -----------------------------
class LicenseGate(ctk.CTk):
    def __init__(self, keyauth_obj):
        super().__init__()
        self.title("KeyAuth Login")
        self.geometry("420x220")
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        self.keyauth = keyauth_obj

        label = ctk.CTkLabel(self, text="Enter License Key", font=("Segoe UI", 18, "bold"))
        label.pack(pady=(24, 8))

        self.entry = ctk.CTkEntry(self, width=280, placeholder_text="XXXXX-XXXXX-XXXXX-XXXXX")
        self.entry.pack(pady=6)

        self.status = ctk.CTkLabel(self, text="", font=("Segoe UI", 12))
        self.status.pack(pady=(6, 2))

        btn = ctk.CTkButton(self, text="Activate", command=self._try_login)
        btn.pack(pady=12)

    def _try_login(self):
        key = (self.entry.get() or "").strip()
        if not key:
            messagebox.showwarning("Input Error", "Please enter a license key.")
            return
        try:
            self.status.configure(text="Checking license…")
            self.update_idletasks()
            # SDK call — most Python SDKs expose `license(key)` on the api instance
            self.keyauth.license(key)  # type: ignore[attr-defined]
            messagebox.showinfo("Success", "License verified! Launching optimizer…")
            self.destroy()
            app = App()
            app.mainloop()
        except Exception as e:
            messagebox.showerror("Auth Failed", f"Invalid license or SDK error.\n\nDetails: {e}")


# ----------------------------- Main ----------------------------------------
if __name__ == "__main__":
    if keyauthapp is not None:
        # Show license window first
        gate = LicenseGate(keyauthapp)
        gate.mainloop()
    else:
        # No KeyAuth installed — launch directly
        main_app = App()
        main_app.mainloop()
