import socket
import concurrent.futures
import threading
import queue
import time
from datetime import datetime
import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

APP_NAME = "Bardia Port Scanner"
APP_VERSION = "1.0.0"

# ----------------------- Core Scanner -----------------------
def scan_port(host: str, port: int, timeout: float = 0.5) -> bool:
    """Return True if TCP port is open, else False."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            sock.settimeout(timeout)
            return sock.connect_ex((host, port)) == 0
    except Exception:
        return False

# ----------------------- Theming ----------------------------
def apply_dark_theme(root: tk.Tk):
    """Apply a modern dark theme to ttk widgets."""
    style = ttk.Style(root)
    try:
        style.theme_use("clam")  # good base for custom colors
    except Exception:
        pass

    # Palette
    bg = "#0f1115"       # window background
    card = "#161a20"     # frames/cards
    fg = "#e6e6e6"       # primary text
    subfg = "#b8c1cc"    # secondary text
    accent = "#00d1ff"   # cyan accent
    accent2 = "#8a5bff"  # purple accent for progress
    border = "#2a2f3a"
    selbg = "#233242"

    root.configure(bg=bg)

    # General
    style.configure("TLabel", background=card, foreground=fg)
    style.configure("TFrame", background=card)
    style.configure("Card.TFrame", background=card, relief="flat")

    # Entries
    style.configure("TEntry", fieldbackground="#0d0f14", background="#0d0f14", foreground=fg)
    style.map("TEntry", fieldbackground=[("disabled", "#0d0f14"), ("focus", "#0d0f14")])

    # Buttons
    style.configure("TButton", background=card, foreground=fg, borderwidth=0, padding=8)
    style.map(
        "TButton",
        background=[("active", "#1e2430"), ("pressed", "#1c2230")],
        foreground=[("disabled", "#6c7683")]
    )

    # Progressbar
    style.configure("TProgressbar", troughcolor="#0d0f14", background=accent2, bordercolor=border, lightcolor=accent2, darkcolor=accent2)

    # Treeview
    style.configure(
        "Treeview",
        background="#0d0f14",
        fieldbackground="#0d0f14",
        foreground=fg,
        bordercolor=border,
        rowheight=24,
    )
    style.configure("Treeview.Heading", background=card, foreground=subfg)
    style.map("Treeview", background=[("selected", selbg)])

    # Notebook (tabs) if ever used
    style.configure("TNotebook", background=card, borderwidth=0)
    style.configure("TNotebook.Tab", background=card, foreground=subfg)
    style.map("TNotebook.Tab", background=[("selected", "#1a1f28")])

    # Separators
    style.configure("TSeparator", background=border)

    # Create a top bar (custom title look)
    return {
        "bg": bg,
        "card": card,
        "fg": fg,
        "subfg": subfg,
        "accent": accent,
        "accent2": accent2,
        "border": border,
    }

# ----------------------- GUI App ----------------------------
class PortScannerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(APP_NAME)
        self.geometry("860x600")
        self.minsize(780, 520)
        self.resizable(True, True)

        # State
        self.cancel_event = threading.Event()
        self.progress_q: "queue.Queue[tuple]" = queue.Queue()  # (kind, payload)
        self.total_ports = 0
        self.scanned_ports = 0
        self.open_ports = []  # list of (port, service)
        self.executor = None

        # Theme
        self.palette = apply_dark_theme(self)

        self._build_ui()
        self._schedule_drain()

    # -------------------- UI Layout --------------------
    def _build_ui(self):
        pad = {"padx": 12, "pady": 10}

        # App header
        header = ttk.Frame(self, style="Card.TFrame")
        header.pack(fill=tk.X)
        title = ttk.Label(header, text=f"{APP_NAME}", font=("Segoe UI", 16, "bold"))
        title.pack(side=tk.LEFT, padx=12, pady=12)
        subtitle = ttk.Label(header, text=f"Fast TCP port scanner • v{APP_VERSION}", foreground=self.palette["subfg"]) 
        subtitle.pack(side=tk.LEFT, padx=6)

        # Main card
        frm = ttk.Frame(self, style="Card.TFrame")
        frm.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        # Row 1: Target + Resolve
        row1 = ttk.Frame(frm, style="Card.TFrame")
        row1.pack(fill=tk.X)
        ttk.Label(row1, text="Target (IP or domain):").pack(side=tk.LEFT)
        self.ent_target = ttk.Entry(row1)
        self.ent_target.insert(0, "scanme.nmap.org")
        self.ent_target.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=10)

        # Row 2: Range, Timeout, Threads
        row2 = ttk.Frame(frm, style="Card.TFrame")
        row2.pack(fill=tk.X, pady=(6, 0))
        ttk.Label(row2, text="From port:").pack(side=tk.LEFT)
        self.ent_start = ttk.Entry(row2, width=8)
        self.ent_start.insert(0, "1")
        self.ent_start.pack(side=tk.LEFT, padx=8)

        ttk.Label(row2, text="To port:").pack(side=tk.LEFT)
        self.ent_end = ttk.Entry(row2, width=8)
        self.ent_end.insert(0, "65535")
        self.ent_end.pack(side=tk.LEFT, padx=8)

        ttk.Label(row2, text="Timeout (s):").pack(side=tk.LEFT)
        self.ent_timeout = ttk.Entry(row2, width=8)
        self.ent_timeout.insert(0, "0.5")
        self.ent_timeout.pack(side=tk.LEFT, padx=8)

        ttk.Label(row2, text="Threads:").pack(side=tk.LEFT)
        self.ent_threads = ttk.Entry(row2, width=8)
        self.ent_threads.insert(0, "350")
        self.ent_threads.pack(side=tk.LEFT, padx=8)

        # Row 3: Buttons
        row3 = ttk.Frame(frm, style="Card.TFrame")
        row3.pack(fill=tk.X, pady=(8, 0))
        self.btn_start = ttk.Button(row3, text="▶ Start Scan", command=self.start_scan)
        self.btn_start.pack(side=tk.LEFT)
        self.btn_stop = ttk.Button(row3, text="■ Stop", command=self.stop_scan, state=tk.DISABLED)
        self.btn_stop.pack(side=tk.LEFT, padx=8)
        self.btn_save = ttk.Button(row3, text="💾 Save Results", command=self.save_results, state=tk.DISABLED)
        self.btn_save.pack(side=tk.LEFT)
        self.btn_clear = ttk.Button(row3, text="🧹 Clear", command=self.clear_results)
        self.btn_clear.pack(side=tk.LEFT, padx=8)

        # Row 4: Progress
        row4 = ttk.Frame(frm, style="Card.TFrame")
        row4.pack(fill=tk.X, pady=(8, 0))
        self.prog = ttk.Progressbar(row4, orient=tk.HORIZONTAL, mode="determinate")
        self.prog.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.lbl_status = ttk.Label(row4, text="Idle.", foreground=self.palette["subfg"]) 
        self.lbl_status.pack(side=tk.LEFT, padx=10)

        # Row 5: Results (Treeview)
        row5 = ttk.Frame(frm, style="Card.TFrame")
        row5.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        columns = ("port", "service")
        self.tree = ttk.Treeview(row5, columns=columns, show="headings", height=16)
        self.tree.heading("port", text="Port")
        self.tree.heading("service", text="Service (best guess)")
        self.tree.column("port", width=90, anchor=tk.CENTER)
        self.tree.column("service", width=300)
        vsb = ttk.Scrollbar(row5, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Footer
        sep = ttk.Separator(self)
        sep.pack(fill=tk.X, padx=12)
        footer = ttk.Frame(self, style="Card.TFrame")
        footer.pack(fill=tk.X)
        self.lbl_footer = ttk.Label(
            footer,
            text="Use responsibly. Scan only hosts you own or have permission to test.")
        self.lbl_footer.pack(fill=tk.X, padx=12, pady=8)

    # -------------------- Actions --------------------
    def start_scan(self):
        target = self.ent_target.get().strip()
        try:
            start_port = int(self.ent_start.get())
            end_port = int(self.ent_end.get())
            timeout = float(self.ent_timeout.get())
            threads = int(self.ent_threads.get())
        except ValueError:
            messagebox.showerror("Invalid input", "Please enter valid numbers for ports/timeout/threads.")
            return

        if not target:
            messagebox.showerror("Missing target", "Please enter a target IP or domain.")
            return
        if not (1 <= start_port <= 65535 and 1 <= end_port <= 65535 and start_port <= end_port):
            messagebox.showerror("Invalid range", "Port range must be within 1..65535 and start <= end.")
            return
        if threads < 1:
            messagebox.showerror("Invalid threads", "Threads must be >= 1.")
            return
        if timeout <= 0:
            messagebox.showerror("Invalid timeout", "Timeout must be > 0.")
            return

        # Resolve host to IP first (for speed & clarity)
        try:
            resolved_ip = socket.gethostbyname(target)
        except socket.gaierror:
            messagebox.showerror("Resolution failed", f"Could not resolve host: {target}")
            return

        # Reset state
        self.clear_results()
        self.cancel_event.clear()
        self.total_ports = end_port - start_port + 1
        self.scanned_ports = 0
        self.prog.configure(maximum=self.total_ports, value=0)
        self.lbl_status.config(text=f"Scanning {target} ({resolved_ip}) {start_port}-{end_port}...")
        self.btn_start.config(state=tk.DISABLED)
        self.btn_stop.config(state=tk.NORMAL)
        self.btn_save.config(state=tk.DISABLED)

        # Launch scanning in background thread so UI stays responsive
        t = threading.Thread(
            target=self._scan_manager,
            args=(resolved_ip, start_port, end_port, timeout, threads),
            daemon=True,
        )
        t.start()

    def stop_scan(self):
        self.cancel_event.set()
        self.lbl_status.config(text="Stopping... (letting in-flight checks finish)")

    def clear_results(self):
        for row in self.tree.get_children():
            self.tree.delete(row)
        self.open_ports.clear()
        self.prog.configure(value=0)
        self.lbl_status.config(text="Idle.")

    def save_results(self):
        if not self.open_ports:
            messagebox.showinfo("No results", "There are no open ports to save.")
            return
        ts = datetime.now().strftime("%Y%m%d_%H%M%S")
        default_name = f"{APP_NAME.lower().replace(' ', '_')}_{ts}.csv"
        path = filedialog.asksaveasfilename(
            defaultextension=".csv", initialfile=default_name, filetypes=[("CSV files", ".csv")]
        )
        if not path:
            return
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write("port,service\n")
                for p, s in sorted(self.open_ports, key=lambda x: x[0]):
                    f.write(f"{p},{s}\n")
            messagebox.showinfo("Saved", f"Results saved to:\n{path}")
        except Exception as e:
            messagebox.showerror("Save failed", str(e))

    # -------------------- Scan Engine --------------------
    def _scan_manager(self, ip: str, start_port: int, end_port: int, timeout: float, threads: int):
        start_time = time.time()
        ports = list(range(start_port, end_port + 1))

        # Limit threads to a reasonable upper bound to avoid exhausting file descriptors
        threads = max(1, min(threads, 1000))

        try:
            with concurrent.futures.ThreadPoolExecutor(max_workers=threads) as ex:
                futures = {ex.submit(self._scan_one_and_report, ip, p, timeout): p for p in ports}
                for _ in concurrent.futures.as_completed(futures):
                    if self.cancel_event.is_set():
                        break
        finally:
            # Signal completion
            elapsed = time.time() - start_time
            self.progress_q.put(("done", elapsed))

    def _scan_one_and_report(self, ip: str, port: int, timeout: float):
        if self.cancel_event.is_set():
            return
        is_open = scan_port(ip, port, timeout)
        # Update progress regardless of open/closed
        self.progress_q.put(("progress", 1))
        if is_open:
            try:
                service = socket.getservbyport(port)
            except OSError:
                service = "unknown"
            self.progress_q.put(("open", (port, service)))

    # -------------------- UI Update Loop --------------------
    def _schedule_drain(self):
        self.after(40, self._drain_queue)

    def _drain_queue(self):
        while True:
            try:
                kind, payload = self.progress_q.get_nowait()
            except queue.Empty:
                break

            if kind == "progress":
                self.scanned_ports += int(payload)
                self.prog.configure(value=self.scanned_ports)
                self.lbl_status.config(text=f"Scanned {self.scanned_ports}/{self.total_ports} ports...")
            elif kind == "open":
                port, service = payload
                self.open_ports.append((port, service))
                self.tree.insert("", tk.END, values=(port, service))
            elif kind == "done":
                elapsed = payload
                self.btn_start.config(state=tk.NORMAL)
                self.btn_stop.config(state=tk.DISABLED)
                self.btn_save.config(state=tk.NORMAL if self.open_ports else tk.DISABLED)
                if self.cancel_event.is_set():
                    self.lbl_status.config(text=f"Stopped. Scanned {self.scanned_ports}/{self.total_ports} ports in {elapsed:.1f}s")
                else:
                    self.lbl_status.config(text=f"Done in {elapsed:.1f}s. Open ports: {len(self.open_ports)}")

        # Keep looping
        self._schedule_drain()


# ----------------------- Entry Point ------------------------
def resource_path(relative_path: str) -> str:
    """Get absolute path to resource, works for dev and for PyInstaller."""
    if getattr(sys, 'frozen', False) and hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)


if __name__ == "__main__":
    app = PortScannerApp()
    app.iconbitmap(resource_path("app.ico")) if os.path.exists(resource_path("app.ico")) and sys.platform.startswith("win") else None
    app.mainloop()
