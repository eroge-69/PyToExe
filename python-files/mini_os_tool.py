#!/usr/bin/env python3
"""
Mini OS Tool - Lightweight single-file system information utility (Tkinter)
- Cross-platform (Windows/macOS/Linux)
- Uses only the Python standard library (no external deps)
- Intended to be packaged into a single .exe with PyInstaller:
    pyinstaller --onefile --noconsole mini_os_tool.py
"""

import platform, os, sys, shutil, socket, subprocess, datetime, getpass, tempfile
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog

APP_TITLE = "Mini OS Tool - System Info (Light)"
VERSION = "1.0"

def safe_run(cmd):
    "Run a shell command and return output (utf-8), fallback empty string on error."
    try:
        out = subprocess.check_output(cmd, shell=True, stderr=subprocess.DEVNULL)
        return out.decode('utf-8', errors='replace')
    except Exception:
        return ''

def get_basic_info():
    info = {}
    info['Platform'] = platform.system()
    info['Platform-version'] = platform.version()
    info['Release'] = platform.release()
    info['Architecture'] = platform.machine()
    info['Processor'] = platform.processor() or 'N/A'
    info['Python'] = sys.version.replace('\\n',' ')
    info['User'] = getpass.getuser()
    try:
        info['Hostname'] = socket.gethostname()
    except:
        info['Hostname'] = 'N/A'
    info['Current dir'] = os.getcwd()
    info['Temp dir'] = tempfile.gettempdir()
    try:
        total, used, free = shutil.disk_usage(os.path.abspath(os.sep))
        info['Disk total'] = f"{total//(1024**3)} GB"
        info['Disk free'] = f"{free//(1024**3)} GB"
    except Exception:
        pass
    return info

def get_process_list():
    # Prefer psutil if available for nicer output; else fallback to platform commands
    try:
        import psutil
        procs = []
        for p in psutil.process_iter(['pid','name','cpu_percent','memory_percent']):
            try:
                d = p.info
                procs.append(f"{d.get('pid')}\t{d.get('name')}\tCPU:{d.get('cpu_percent',0)}%\tMEM:{d.get('memory_percent',0):.1f}%")
            except Exception:
                continue
        return "\\n".join(procs[:200]) or "No processes found (psutil)"
    except Exception:
        system = platform.system().lower()
        if 'windows' in system:
            out = safe_run('tasklist /FO LIST')
            return out[:20000] or "Unable to list processes (tasklist failed)"
        else:
            out = safe_run('ps -eo pid,comm,%cpu,%mem --sort=-%cpu | head -n 200')
            return out or "Unable to list processes (ps failed)"

def get_network_info():
    info = []
    try:
        info.append(f"Hostname: {socket.gethostname()}")
        addrs = socket.getaddrinfo(socket.gethostname(), None)
        ips = set()
        for a in addrs:
            ip = a[4][0]
            if ':' not in ip: # skip IPv6 for brevity
                ips.add(ip)
        info.append("Local IPs: " + (', '.join(sorted(ips)) or 'N/A'))
    except Exception:
        info.append("Network: N/A")
    # Try system commands for interface list
    system = platform.system().lower()
    if 'windows' in system:
        info.append("IP Configuration:\\n" + safe_run('ipconfig /all')[:4000])
    else:
        info.append("Ifconfig/Ip addr:\\n" + (safe_run('ifconfig') or safe_run('ip addr') )[:4000])
    return "\\n\\n".join(info)

def get_installed_python_packages():
    # non-critical helper: list pip packages if pip is available
    try:
        out = safe_run(f'"{sys.executable}" -m pip list --format=columns')
        return out or "pip list returned nothing"
    except Exception:
        return "pip not available or failed"

# GUI
class MiniApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{APP_TITLE} v{VERSION}")
        self.geometry("900x620")
        self.minsize(700,500)
        self.create_widgets()

    def create_widgets(self):
        toolbar = ttk.Frame(self)
        toolbar.pack(side=tk.TOP, fill=tk.X, padx=6, pady=6)

        ttk.Button(toolbar, text="Refresh", command=self.refresh_all).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Save Report", command=self.save_report).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Restart App", command=self.restart_app).pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="About", command=self.show_about).pack(side=tk.RIGHT, padx=2)

        paned = ttk.Panedwindow(self, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        left = ttk.Frame(paned, width=480)
        right = ttk.Frame(paned, width=300)
        paned.add(left, weight=3)
        paned.add(right, weight=1)

        # Tabs for left
        tabs = ttk.Notebook(left)
        tabs.pack(fill=tk.BOTH, expand=True)
        self.text_overview = scrolledtext.ScrolledText(tabs, wrap=tk.WORD)
        self.text_processes = scrolledtext.ScrolledText(tabs, wrap=tk.NONE)
        self.text_network = scrolledtext.ScrolledText(tabs, wrap=tk.WORD)
        self.text_packages = scrolledtext.ScrolledText(tabs, wrap=tk.WORD)

        tabs.add(self.text_overview, text="Overview")
        tabs.add(self.text_processes, text="Processes")
        tabs.add(self.text_network, text="Network")
        tabs.add(self.text_packages, text="Python Packages")

        # Right: quick actions and small info
        info_box = ttk.LabelFrame(right, text="Quick Info / Actions")
        info_box.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        self.lbl_basic = tk.Label(info_box, justify=tk.LEFT, anchor="nw", font=("Segoe UI", 10))
        self.lbl_basic.pack(fill=tk.BOTH, expand=True, padx=6, pady=6)

        actions = ttk.Frame(info_box)
        actions.pack(fill=tk.X, padx=6, pady=6)
        ttk.Button(actions, text="Open Temp Folder", command=self.open_temp).pack(fill=tk.X)
        ttk.Button(actions, text="Open Current Folder", command=self.open_cwd).pack(fill=tk.X, pady=4)
        ttk.Button(actions, text="Run Diagnostics", command=self.run_diagnostics).pack(fill=tk.X)

        # Footer
        footer = ttk.Frame(self)
        footer.pack(side=tk.BOTTOM, fill=tk.X, padx=6, pady=6)
        self.status = ttk.Label(footer, text="Ready", anchor="w")
        self.status.pack(fill=tk.X)
        self.refresh_all()

    def refresh_all(self):
        self.status.config(text="Refreshing...")
        self.update_idletasks()
        basic = get_basic_info()
        basic_text = "\\n".join(f"{k}: {v}" for k,v in basic.items())
        self.text_overview.delete("1.0", tk.END)
        self.text_overview.insert(tk.END, basic_text + "\\n\\nDetailed OS info:\\n")
        self.text_overview.insert(tk.END, safe_run('ver') if platform.system().lower().startswith('windows') else safe_run('uname -a'))

        self.text_processes.delete("1.0", tk.END)
        self.text_processes.insert(tk.END, get_process_list())

        self.text_network.delete("1.0", tk.END)
        self.text_network.insert(tk.END, get_network_info())

        self.text_packages.delete("1.0", tk.END)
        self.text_packages.insert(tk.END, get_installed_python_packages())

        self.lbl_basic.config(text="Summary:\\n" + "\\n".join(list(basic.items())[:6]))
        self.status.config(text="Refreshed at " + datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

    def save_report(self):
        content = "\\n--- Overview ---\\n" + self.text_overview.get("1.0", tk.END)
        content += "\\n--- Processes ---\\n" + self.text_processes.get("1.0", tk.END)
        content += "\\n--- Network ---\\n" + self.text_network.get("1.0", tk.END)
        content += "\\n--- Packages ---\\n" + self.text_packages.get("1.0", tk.END)
        fname = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text Files","*.txt")], title="Save report as...")
        if fname:
            try:
                with open(fname, "w", encoding="utf-8") as f:
                    f.write(content)
                messagebox.showinfo("Saved", f"Report saved to {fname}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save report: {e}")

    def open_temp(self):
        path = tempfile.gettempdir()
        self.open_path(path)

    def open_cwd(self):
        self.open_path(os.getcwd())

    def open_path(self, path):
        try:
            if platform.system().lower().startswith('windows'):
                os.startfile(path)
            elif platform.system().lower() == 'darwin':
                subprocess.Popen(['open', path])
            else:
                subprocess.Popen(['xdg-open', path])
        except Exception as e:
            messagebox.showerror("Error", f"Cannot open path: {e}")

    def run_diagnostics(self):
        # lightweight diagnostics: check disk free, temp space, and python writable
        try:
            total, used, free = shutil.disk_usage(os.path.abspath(os.sep))
            tmp = tempfile.gettempdir()
            python_ok = os.access(sys.executable, os.X_OK)
            msg = f"Disk free: {free//(1024**2)} MB\\nTemp dir: {tmp}\\nPython executable OK: {python_ok}"
            messagebox.showinfo("Diagnostics", msg)
        except Exception as e:
            messagebox.showerror("Diagnostics error", str(e))

    def restart_app(self):
        args = sys.argv[:]
        python = sys.executable
        try:
            if getattr(sys, 'frozen', False):
                # If packaged, re-run the exe
                os.execv(sys.executable, [sys.executable] + args)
            else:
                os.execv(python, [python] + args)
        except Exception as e:
            messagebox.showerror("Restart failed", str(e))

    def show_about(self):
        messagebox.showinfo("About", f"{APP_TITLE}\\nVersion {VERSION}\\nLightweight system info utility\\nNo external libraries required.")

if __name__ == "__main__":
    app = MiniApp()
    app.mainloop()
