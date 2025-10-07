import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from tkinter.scrolledtext import ScrolledText
import threading, subprocess, shlex, os, sys, json, shutil, re
from pathlib import Path

# ----------- Optional diagnostics (helpful when switching IDEs) -----------
print("Python exe:", sys.executable)
try:
    import serial  # noqa
    import serial.tools.list_ports  # noqa
    print("pyserial import: OK")
except Exception as e:
    print("pyserial import failed:", e)

# ---------- Robust COM port discovery (pyserial + Windows registry) ----------
def _list_ports_pyserial_detailed():
    try:
        from serial.tools import list_ports
        return [(p.device, getattr(p, "description", "") or "") for p in list_ports.comports()]
    except Exception:
        return []

def _list_ports_winreg():
    """Return [(COMx, '(registry) ...')] using the Windows registry as fallback."""
    pairs = []
    try:
        import winreg
        key = r"HARDWARE\DEVICEMAP\SERIALCOMM"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key) as k:
            i = 0
            while True:
                try:
                    name, value, _ = winreg.EnumValue(k, i)
                    pairs.append((str(value), f"(registry) {name}"))
                    i += 1
                except OSError:
                    break
    except Exception:
        pass
    return pairs

def list_com_ports_detailed():
    """Merge pyserial + registry, remove dups, keep descriptions."""
    seen = set()
    result = []
    for dev, desc in _list_ports_pyserial_detailed() + _list_ports_winreg():
        if dev not in seen:
            seen.add(dev)
            result.append((dev, desc))
    return result

# ----------------- Config / constants -----------------
APP_NAME    = "PymcuprogGUI"
CFG_FILE    = Path(os.getenv("APPDATA") or Path.home()) / f"{APP_NAME}.json"

PORT_DEFAULT = "COM7"
BAUD_DEFAULT = "115200"
BAUD_PRESETS = ["57600", "115200", "230400", "460800"]
THEME_BG     = "pink"

# Preset pretty labels -> pymcuprog ids (you can add more common ones)
MCU_MAP = {
    "ATtiny214":   "attiny214",
    "ATtiny414":   "attiny414",
    "ATtiny416":   "attiny416",
    "ATtiny3216":  "attiny3216",
    "AVR128DA32":  "avr128da32",
}

# Known signatures you actually use (add more as you confirm them)
SIG_TO_DEV = {
    "1E9709": "attiny414",
    "1E9714": "attiny416",
    # "1E9723": "avr128da32",  # example placeholder
}

# ----------------- Config helpers (MUST be above App class) -----------------
def load_cfg():
    if CFG_FILE.exists():
        try:
            return json.loads(CFG_FILE.read_text(encoding="utf-8"))
        except Exception:
            pass
    return {
        "pymcu_path": "",
        "hex_path": "",
        "mcu_pretty": "ATtiny414",
        "interface": "uart",
        "port": PORT_DEFAULT,
        "baud": BAUD_DEFAULT,
        "geometry": "1000x700",
    }

def save_cfg(cfg: dict):
    try:
        CFG_FILE.write_text(json.dumps(cfg, indent=2), encoding="utf-8")
    except Exception as e:
        print("Config save error:", e, file=sys.stderr)

# ----------------- Resource helper for dev + PyInstaller -----------------
def resource_path(relative_path: str) -> str:
    """
    Get absolute path to resource, works in dev and PyInstaller .exe.
    Place files (e.g., mccu.ico) next to this script, and add them with:
      --add-data "mccu.ico;."
    """
    try:
        base_path = Path(sys._MEIPASS)  # type: ignore[attr-defined]
    except Exception:
        base_path = Path(__file__).parent
    return str((base_path / relative_path).resolve())

# ----------------- App -----------------
class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.cfg = load_cfg()

        self.title("Pymcuprog GUI Wrapper")
        self._set_icon()  # safe icon loader for dev + PyInstaller
        self.configure(background=THEME_BG)
        self.geometry(self.cfg.get("geometry", "1000x700"))
        self.minsize(800, 520)
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(4, weight=1)

        self._build_paths()
        self._build_controls()
        self._build_actions_bar()
        self._build_preview()
        self._build_log()
        self._wire_events()
        self._load_initial_values()
        self._refresh_ports(initial=True)
        self._update_preview()

        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # -------- Icon handling (robust for .exe) --------
    def _set_icon(self):
        """
        Try to set a window icon that works in both the IDE and frozen .exe.
        Looks for 'mccu.ico' first (Windows .ico), then optional 'mccu.png'.
        """
        try:
            ico = Path(resource_path("mccu.ico"))
            if ico.exists():
                self.iconbitmap(str(ico))
                return
        except Exception as e:
            print("ICO icon load failed:", e)
        # Fallback to PNG (Tk uses iconphoto); keep a ref to avoid GC
        try:
            png = Path(resource_path("mccu.png"))
            if png.exists():
                self._icon_img = tk.PhotoImage(file=str(png))
                self.iconphoto(True, self._icon_img)
        except Exception as e:
            print("PNG icon load failed:", e)

    # -------- UI builders --------
    def _build_paths(self):
        fr = tk.Frame(self, bg="skyblue")
        fr.grid(row=0, column=0, padx=16, pady=(12,6), sticky="ew")
        fr.grid_columnconfigure(1, weight=1)

        tk.Label(fr, text="PATH TO PYMCUPROG", bg="skyblue").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        tk.Label(fr, text="PATH TO AVR HEX",   bg="skyblue").grid(row=1, column=0, padx=6, pady=6, sticky="e")

        self.var_pymcu = tk.StringVar()
        self.var_hex   = tk.StringVar()

        tk.Entry(fr, textvariable=self.var_pymcu).grid(row=0, column=1, padx=6, pady=6, sticky="ew")
        tk.Entry(fr, textvariable=self.var_hex).grid(  row=1, column=1, padx=6, pady=6, sticky="ew")

        tk.Button(fr, text="Browse", command=self._pick_pymcu).grid(row=0, column=2, padx=6, pady=6)
        tk.Button(fr, text="Browse", command=self._pick_hex).grid(  row=1, column=2, padx=6, pady=6)

    def _build_controls(self):
        fr = tk.Frame(self, bg="skyblue")
        fr.grid(row=1, column=0, padx=16, pady=6, sticky="ew")
        for c in range(10):
            fr.grid_columnconfigure(c, weight=1 if c in (1,3,5,7,9) else 0)

        # MCU (editable)
        tk.Label(fr, text="MCU", bg="skyblue").grid(row=0, column=0, padx=6, pady=6, sticky="e")
        self.mculist = list(MCU_MAP.keys())
        self.cbo_mcu = ttk.Combobox(fr, values=self.mculist, state="normal", width=22)  # EDITABLE
        self.cbo_mcu.grid(row=0, column=1, padx=6, pady=6, sticky="ew")

        # Interface
        tk.Label(fr, text="Interface", bg="skyblue").grid(row=0, column=2, padx=6, pady=6, sticky="e")
        self.cbo_iface = ttk.Combobox(fr, values=["uart (SerialUPDI)", "hid (Atmel-ICE)"], state="readonly", width=22)
        self.cbo_iface.grid(row=0, column=3, padx=6, pady=6, sticky="ew")

        # Port (Combobox) + Refresh
        tk.Label(fr, text="Port", bg="skyblue").grid(row=0, column=4, padx=6, pady=6, sticky="e")
        self.var_port = tk.StringVar()
        self.cbo_port = ttk.Combobox(fr, values=[], textvariable=self.var_port, width=18)  # editable + dropdown
        self.cbo_port.grid(row=0, column=5, padx=6, pady=6, sticky="ew")
        tk.Button(fr, text="Refresh", command=self._refresh_ports).grid(row=0, column=6, padx=6, pady=6)

        # Baud (Combobox with presets, also editable)
        tk.Label(fr, text="Baud", bg="skyblue").grid(row=0, column=7, padx=6, pady=6, sticky="e")
        self.var_baud = tk.StringVar()
        self.cbo_baud = ttk.Combobox(fr, values=BAUD_PRESETS, textvariable=self.var_baud, width=12)
        self.cbo_baud.grid(row=0, column=8, padx=6, pady=6, sticky="ew")

    def _build_actions_bar(self):
        bar = tk.Frame(self, bg="skyblue")
        bar.grid(row=2, column=0, padx=16, pady=(0,6), sticky="ew")
        for i in range(6):
            bar.grid_columnconfigure(i, weight=1)

        self.btn_program = tk.Button(bar, text="Program (Erase + Flash + Verify)", command=self._on_program, width=24)
        self.btn_verify  = tk.Button(bar, text="Verify Only",                       command=self._on_verify, width=18)
        self.btn_erase   = tk.Button(bar, text="Erase Only",                        command=self._on_erase, width=18)
        self.btn_ping    = tk.Button(bar, text="Ping / Read Signature",             command=self._on_ping, width=18)
        self.btn_copy    = tk.Button(bar, text="Copy Cmd",                          command=self._copy_preview, width=12)
        self.btn_savelog = tk.Button(bar, text="Save Log",                          command=self._save_log, width=12)

        self.btn_program.grid(row=0, column=0, padx=6, pady=6, sticky="ew")
        self.btn_verify.grid( row=0, column=1, padx=6, pady=6, sticky="ew")
        self.btn_erase.grid(  row=0, column=2, padx=6, pady=6, sticky="ew")
        self.btn_ping.grid(   row=0, column=3, padx=6, pady=6, sticky="ew")
        self.btn_copy.grid(   row=0, column=4, padx=6, pady=6, sticky="ew")
        self.btn_savelog.grid(row=0, column=5, padx=6, pady=6, sticky="ew")

    def _build_preview(self):
        fr = tk.Frame(self, bg="skyblue")
        fr.grid(row=3, column=0, padx=16, pady=(0,6), sticky="ew")
        fr.grid_columnconfigure(0, weight=1)
        self.var_preview = tk.StringVar(value="")
        tk.Entry(fr, textvariable=self.var_preview, state="readonly", readonlybackground="white")\
            .grid(row=0, column=0, padx=6, pady=6, sticky="ew")

    def _build_log(self):
        fr = tk.Frame(self)
        fr.grid(row=4, column=0, padx=16, pady=10, sticky="nsew")
        self.grid_rowconfigure(4, weight=1)
        fr.grid_rowconfigure(0, weight=1)
        fr.grid_columnconfigure(0, weight=1)
        self.log = ScrolledText(fr, height=18, wrap="word")
        self.log.grid(row=0, column=0, sticky="nsew")

    # -------- Utilities --------
    def _log_write(self, text: str):
        self.log.insert("end", text)
        self.log.see("end")

    def _pick_pymcu(self):
        p = filedialog.askopenfilename(
            title="Select pymcuprog (exe/script)",
            filetypes=[("Executable/Scripts","*.exe *.cmd *.bat *.py *.pyw"), ("All","*.*")]
        )
        if p:
            self.var_pymcu.set(p)

    def _pick_hex(self):
        p = filedialog.askopenfilename(
            title="Select HEX file",
            filetypes=[("Intel HEX","*.hex"), ("All","*.*")]
        )
        if p:
            self.var_hex.set(p)

    def _copy_preview(self):
        try:
            cmd = self.var_preview.get()
            self.clipboard_clear()
            self.clipboard_append(cmd)
            messagebox.showinfo("Copy", "Command copied to clipboard.")
        except Exception:
            pass

    def _save_log(self):
        p = filedialog.asksaveasfilename(
            title="Save Log As",
            defaultextension=".txt",
            filetypes=[("Text files","*.txt"), ("All","*.*")]
        )
        if not p: return
        try:
            Path(p).write_text(self.log.get("1.0", "end"), encoding="utf-8")
            messagebox.showinfo("Save Log", "Saved.")
        except Exception as e:
            messagebox.showerror("Save Log", f"Failed: {e}")

    def _wire_events(self):
        # reflect changes into preview
        self.var_pymcu.trace_add("write", lambda *_: self._update_preview())
        self.var_hex.trace_add("write",   lambda *_: self._update_preview())
        self.cbo_mcu.bind("<<ComboboxSelected>>", lambda e: self._update_preview())
        self.cbo_mcu.bind("<KeyRelease>", lambda e: self._update_preview())  # typing custom MCU updates preview

        # Interface change: toggle UART controls + refresh ports + update preview
        self.cbo_iface.bind("<<ComboboxSelected>>",
                            lambda e: (self._toggle_uart_controls(), self._refresh_ports(), self._update_preview()))

        # Port/baud updates
        self.cbo_port.bind("<<ComboboxSelected>>", lambda e: self._update_preview())
        self.cbo_baud.bind("<<ComboboxSelected>>", lambda e: self._update_preview())
        self.cbo_port.bind("<KeyRelease>", lambda e: self._update_preview())  # allow typing COM
        self.cbo_baud.bind("<KeyRelease>", lambda e: self._update_preview())

        # Live refresh moments
        self.bind("<FocusIn>", lambda e: self._refresh_ports())
        self.cbo_port.bind("<Button-1>", lambda e: self._refresh_ports())  # refresh when user opens dropdown

    def _load_initial_values(self):
        self.var_pymcu.set(self.cfg.get("pymcu_path", ""))
        self.var_hex.set(self.cfg.get("hex_path", ""))

        # Keep previously-typed custom MCU text
        pretty = self.cfg.get("mcu_pretty", "ATtiny414")
        self.cbo_mcu.set(pretty if pretty else "ATtiny414")

        iface = self.cfg.get("interface", "uart")
        self.cbo_iface.set("uart (SerialUPDI)" if iface == "uart" else "hid (Atmel-ICE)")

        self.var_port.set(self.cfg.get("port", PORT_DEFAULT))
        self.var_baud.set(self.cfg.get("baud", BAUD_DEFAULT))
        # keep user's baud inside presets list for combo
        self.cbo_baud.configure(values=sorted(set(BAUD_PRESETS + [self.var_baud.get()])))

        self._toggle_uart_controls()

    def _toggle_uart_controls(self):
        is_uart = "uart" in self.cbo_iface.get()
        state = "normal" if is_uart else "disabled"
        for w in (self.cbo_port, self.cbo_baud):
            w.configure(state=state)

    def _refresh_ports(self, initial=False):
        pairs = list_com_ports_detailed()  # [(dev, desc), ...]
        # DEBUG: show what we saw
        self._log_write(f"\n[detect] ports: {pairs}\n")

        # Score ports so likely programmer ports come first
        def score(pair):
            dev, desc = pair
            text = (dev + " " + desc).lower()
            s = 0
            for kw in ("usb", "ftdi", "cp210", "ch340", "atmel", "microchip", "updi", "ice", "usb-serial"):
                if kw in text:
                    s += 10
            m = re.search(r'com(\d+)', dev.lower())
            if m:
                try: s += int(m.group(1)) / 100.0
                except: pass
            return s

        pairs.sort(key=score, reverse=True)
        devices = [d for d,_ in pairs]

        # Update dropdown values
        self.cbo_port.configure(values=devices)

        cur = self.var_port.get().strip()
        if cur and cur in devices:
            pass  # keep current if still valid
        elif devices:
            self.var_port.set(devices[0])  # auto-pick best device
        else:
            if initial and self.cfg.get("port"):
                self.var_port.set(self.cfg["port"])  # keep previous when nothing detected

        self._update_preview()

    def _save_runtime_cfg(self):
        self.cfg["pymcu_path"] = self.var_pymcu.get().strip()
        self.cfg["hex_path"]   = self.var_hex.get().strip()
        self.cfg["mcu_pretty"] = self.cbo_mcu.get().strip()
        self.cfg["interface"]  = "uart" if "uart" in self.cbo_iface.get() else "hid"
        self.cfg["port"]       = self.var_port.get().strip()
        self.cfg["baud"]       = self.var_baud.get().strip()
        save_cfg(self.cfg)

    def _on_close(self):
        try:
            self.cfg["geometry"] = self.geometry()
            self._save_runtime_cfg()
        finally:
            self.destroy()

    # -------- pymcuprog command building --------
    def _resolve_pymcuprog(self):
        path = self.var_pymcu.get().strip()
        if path:
            return [path]
        found = shutil.which("pymcuprog")
        if found:
            return [found]
        return [sys.executable, "-m", "pymcuprog"]

    def _current_dev(self):
        """Return pymcuprog device id from dropdown or typed text."""
        sel = self.cbo_mcu.get().strip()
        return MCU_MAP.get(sel, sel.lower() if sel else "")

    def _current_iface(self):
        return "uart" if "uart" in self.cbo_iface.get() else "hid"

    def _build_base(self):
        exe   = self._resolve_pymcuprog()
        dev   = self._current_dev()
        iface = self._current_iface()
        if not dev:
            raise RuntimeError("Select (or type) an MCU.")
        base = exe + ["-t", iface, "-d", dev]
        if iface == "uart":
            port = (self.var_port.get().strip() or PORT_DEFAULT)
            baud = (self.var_baud.get().strip() or BAUD_DEFAULT)
            base += ["-u", port, "-c", baud]
        return base

    def _build_program(self):
        hexf = self.var_hex.get().strip()
        if not hexf:
            raise RuntimeError("Select a HEX file first.")
        return self._build_base() + ["write", "-f", hexf, "--erase", "--verify"]

    def _build_verify(self):
        hexf = self.var_hex.get().strip()
        if not hexf:
            raise RuntimeError("Select a HEX file first.")
        return self._build_base() + ["verify", "-f", hexf]

    def _build_erase(self):
        return self._build_base() + ["erase"]

    def _build_ping(self):
        return self._build_base() + ["ping"]

    def _update_preview(self):
        try:
            cmd = self._build_program()
            self.var_preview.set(" ".join(shlex.quote(x) for x in cmd))
        except Exception as e:
            self.var_preview.set(f"[!] {e}")
        self._save_runtime_cfg()

    # -------- subprocess runner --------
    def _run_cmd_async(self, cmd:list[str], after_done=None):
        for b in (self.btn_program, self.btn_verify, self.btn_erase, self.btn_ping, self.btn_copy, self.btn_savelog):
            b.config(state="disabled")
        self._log_write("\n> " + " ".join(shlex.quote(x) for x in cmd) + "\n")
        def worker():
            try:
                with subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True) as p:
                    for line in p.stdout:
                        self.after(0, lambda s=line: self._log_write(s))
            except FileNotFoundError:
                self.after(0, lambda: messagebox.showerror("Error", "pymcuprog not found. Set path or add to PATH."))
            except Exception as e:
                self.after(0, lambda: self._log_write(f"\n[ERROR] {e}\n"))
            finally:
                self.after(0, lambda: [b.config(state="normal") for b in
                                       (self.btn_program, self.btn_verify, self.btn_erase, self.btn_ping, self.btn_copy, self.btn_savelog)])
                if after_done:
                    self.after(0, after_done)
        threading.Thread(target=worker, daemon=True).start()

    # -------- Extras: ping/signature & guard --------
    def _ping_and_signature(self):
        cmd = self._build_ping()
        self._log_write("\n> " + " ".join(shlex.quote(x) for x in cmd) + "\n")
        try:
            out = subprocess.check_output(cmd, stderr=subprocess.STDOUT, text=True)
        except subprocess.CalledProcessError as e:
            out = e.output
        except Exception as e:
            messagebox.showerror("Ping", f"Ping failed: {e}")
            return None
        self._log_write(out)
        m = re.search(r"Ping response:\s*([0-9A-Fa-f]{6})", out)
        return m.group(1).upper() if m else None

    def _guard_mcu_mismatch(self):
        selected_pretty = self.cbo_mcu.get().strip()
        selected = self._current_dev()

        # Skip mismatch dialog for AVR128DA32 as requested
        if selected == "avr128da32":
            return True

        # Skip mismatch dialog for custom-typed MCUs (not in preset keys)
        if selected_pretty not in MCU_MAP:
            return True

        sig = self._ping_and_signature()
        if not sig:
            return True  # cannot parse; allow to proceed
        detected = SIG_TO_DEV.get(sig)
        if detected and detected != selected:
            pretty_detected = next((k for k,v in MCU_MAP.items() if v == detected), detected)
            return messagebox.askyesno(
                "MCU Mismatch",
                f"Detected chip: {pretty_detected} (sig {sig})\n"
                f"Selected in GUI: {selected}\n\n"
                f"Proceed anyway?"
            )
        return True

    # -------- Actions --------
    def _on_program(self):
        if not self._guard_mcu_mismatch():
            return
        try:
            cmd = self._build_program()
        except Exception as e:
            messagebox.showerror("Program", str(e)); return
        self._run_cmd_async(cmd)

    def _on_verify(self):
        try:
            cmd = self._build_verify()
        except Exception as e:
            messagebox.showerror("Verify", str(e)); return
        self._run_cmd_async(cmd)

    def _on_erase(self):
        if not messagebox.askyesno("Erase", "This will erase the device. Continue?"):
            return
        try:
            cmd = self._build_erase()
        except Exception as e:
            messagebox.showerror("Erase", str(e)); return
        self._run_cmd_async(cmd)

    def _on_ping(self):
        try:
            cmd = self._build_ping()
        except Exception as e:
            messagebox.showerror("Ping", str(e)); return
        self._run_cmd_async(cmd)

# ----------------- run -----------------
if __name__ == "__main__":
    App().mainloop()
